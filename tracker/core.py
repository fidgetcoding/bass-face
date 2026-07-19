"""Bass Face live tracker core.

Webcam -> MediaPipe blendshapes -> calibrated channels -> escalation ratchet
-> terminal meters. The Engine is I/O-free so MIDI (T3) and OSC (T4) senders
plug into the same loop.

Run: .venv/bin/python tracker/core.py  (macOS will prompt for camera access)
"""

from __future__ import annotations

import json
import math
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Escalation ladder order matters: index = stage (0-based).
CHANNEL_ORDER = ["ott_brow", "drive_mouth", "phase_squint", "filth_disgust"]

CONFIG = {
    "engage": 0.35,       # normalized value that counts as "stage engaged"
    "release": 0.12,      # all channels below this -> candidate neutral
    "release_ms": 350,    # sustained neutral before latches clear
    "peak_headroom": 0.90,  # full scale at 90% of calibrated max - the true
                            # max is hard to reproduce mid-performance
    "cascade_ms": 400,      # reaching a stage ramps all lower stages to 1.0
                            # (jump straight to bass face = everything fills)
    "gamma": {            # per-channel response curve (1.0 = linear)
        "ott_brow": 1.0,
        "drive_mouth": 1.0,
        "phase_squint": 1.0,
        "filth_disgust": 1.0,
    },
    # One-euro filter: min_cutoff down = smoother at rest; beta up = faster catch-up.
    "filter": {"min_cutoff": 1.2, "beta": 0.06, "d_cutoff": 1.0},
}


class OneEuro:
    """One-euro filter (Casiez et al.) - jitter-free at rest, low lag in motion."""

    def __init__(self, min_cutoff: float, beta: float, d_cutoff: float):
        self.min_cutoff, self.beta, self.d_cutoff = min_cutoff, beta, d_cutoff
        self.x_prev: float | None = None
        self.dx_prev = 0.0
        self.t_prev: float | None = None

    @staticmethod
    def _alpha(cutoff: float, dt: float) -> float:
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def __call__(self, x: float, t: float) -> float:
        if self.x_prev is None:
            self.x_prev, self.t_prev = x, t
            return x
        dt = max(t - self.t_prev, 1e-4)
        self.t_prev = t
        dx = (x - self.x_prev) / dt
        a_d = self._alpha(self.d_cutoff, dt)
        self.dx_prev = a_d * dx + (1 - a_d) * self.dx_prev
        cutoff = self.min_cutoff + self.beta * abs(self.dx_prev)
        a = self._alpha(cutoff, dt)
        self.x_prev = a * x + (1 - a) * self.x_prev
        return self.x_prev


@dataclass
class Channel:
    name: str
    members: list[str]
    floor: float
    peak: float
    gamma: float
    filt: OneEuro
    live: float = 0.0      # smoothed normalized value this frame
    phrase_peak: float = 0.0  # running max since last neutral release


@dataclass
class Engine:
    """Calibrated channels + escalation ratchet. Feed blendshape dicts, get 0-1 outs.

    Ratchet: once a higher stage engages, every lower stage's OUTPUT holds its
    phrase peak (brows dropping during squint no longer close the OTT). Neutral
    face sustained for release_ms clears the phrase.
    """

    channels: list[Channel]
    engage: float
    release: float
    release_ms: float
    cascade_ms: float = 150.0
    max_engaged_stage: int = 0  # highest stage engaged this phrase (1-based)
    neutral_since: float | None = None
    releasing: bool = False
    t_prev: float | None = None

    @classmethod
    def from_calibration(cls, calib_path: Path, config: dict = CONFIG) -> "Engine":
        calib = json.loads(calib_path.read_text())
        f = config["filter"]
        headroom = config.get("peak_headroom", 1.0)
        chans = []
        for name in CHANNEL_ORDER:
            c = calib["channels"][name]
            eff_peak = c["floor"] + (c["peak"] - c["floor"]) * headroom
            chans.append(Channel(
                name=name, members=c["members"], floor=c["floor"], peak=eff_peak,
                gamma=config["gamma"][name],
                filt=OneEuro(f["min_cutoff"], f["beta"], f["d_cutoff"]),
            ))
        return cls(channels=chans, engage=config["engage"],
                   release=config["release"], release_ms=config["release_ms"],
                   cascade_ms=config.get("cascade_ms", 150.0))

    def update(self, shapes: dict[str, float], t: float) -> dict[str, float]:
        dt = (t - self.t_prev) if self.t_prev is not None else 0.0
        self.t_prev = t
        for ch in self.channels:
            raw = sum(shapes.get(m, 0.0) for m in ch.members) / len(ch.members)
            span = max(ch.peak - ch.floor, 1e-6)
            norm = min(max((raw - ch.floor) / span, 0.0), 1.0) ** ch.gamma
            ch.live = ch.filt(norm, t)
            ch.phrase_peak = max(ch.phrase_peak, ch.live)

        for stage, ch in enumerate(self.channels, start=1):
            if ch.live >= self.engage and stage > self.max_engaged_stage:
                self.max_engaged_stage = stage

        # Cascade-fill: reaching a stage implies every lower stage completes.
        # Jump straight to bass face -> OTT/drive/squint ramp to 1.0 in
        # cascade_ms instead of being skipped.
        if self.max_engaged_stage > 1 and dt > 0 and not self.releasing:
            step = dt / (self.cascade_ms / 1000.0)
            for stage, ch in enumerate(self.channels, start=1):
                if stage < self.max_engaged_stage and ch.phrase_peak < 1.0:
                    ch.phrase_peak = min(1.0, ch.phrase_peak + step)

        if all(ch.live < self.release for ch in self.channels):
            if self.neutral_since is None:
                self.neutral_since = t
            elif (t - self.neutral_since) * 1000 >= self.release_ms:
                self.releasing = True
        else:
            self.neutral_since = None
            self.releasing = False  # face re-engaged - catch the fall

        # Release ramp: latched channels drain to 0 at the cascade rate, so
        # the way down mirrors the way up instead of snapping.
        if self.releasing and dt > 0:
            step = dt / (self.cascade_ms / 1000.0)
            for ch in self.channels:
                ch.phrase_peak = max(0.0, ch.phrase_peak - step)
            if all(ch.phrase_peak == 0.0 for ch in self.channels):
                self.releasing = False
                self.max_engaged_stage = 0

        out = {}
        for stage, ch in enumerate(self.channels, start=1):
            latched = stage < self.max_engaged_stage
            out[ch.name] = ch.phrase_peak if latched else ch.live
        return out

    def latched_channels(self) -> set[str]:
        return {ch.name for stage, ch in enumerate(self.channels, start=1)
                if stage < self.max_engaged_stage}

    def release_all(self) -> None:
        """Manual unlock (head-shake gesture) - same effect as neutral hold."""
        for ch in self.channels:
            ch.phrase_peak = 0.0
        self.max_engaged_stage = 0


class ShakeDetector:
    """Head-shake-to-unlock: >=3 alternating fast yaw swings within a window."""

    def __init__(self, vel_thresh: float = 1.2, window: float = 0.7,
                 cooldown: float = 1.0):
        self.vel_thresh, self.window, self.cooldown = vel_thresh, window, cooldown
        self.events: list[tuple[float, int]] = []
        self.last_yaw: float | None = None
        self.last_t = 0.0
        self.last_fire = -10.0

    def update(self, yaw: float, t: float) -> bool:
        fired = False
        if self.last_yaw is not None:
            vel = (yaw - self.last_yaw) / max(t - self.last_t, 1e-3)
            if abs(vel) > self.vel_thresh:
                direction = 1 if vel > 0 else -1
                if not self.events or self.events[-1][1] != direction:
                    self.events.append((t, direction))
        self.events = [(et, d) for et, d in self.events if t - et < self.window]
        if len(self.events) >= 3 and t - self.last_fire > self.cooldown:
            fired = True
            self.last_fire = t
            self.events.clear()
        self.last_yaw, self.last_t = yaw, t
        return fired




def camera_devices() -> list[tuple[str, str]]:
    """(name, deviceType) in OpenCV's exact index order.

    Mirrors cap_avfoundation_mac.mm: video + muxed devices, sorted by
    uniqueID string compare. Computed at call time because Continuity
    Camera (iPhone) joins/leaves the list and reshuffles every index.
    """
    try:
        import AVFoundation as AVF
        devs = list(AVF.AVCaptureDevice.devicesWithMediaType_(AVF.AVMediaTypeVideo))
        devs += list(AVF.AVCaptureDevice.devicesWithMediaType_(AVF.AVMediaTypeMuxed))
        devs.sort(key=lambda d: str(d.uniqueID()))
        return [(str(d.localizedName()), str(d.deviceType())) for d in devs]
    except Exception:
        return []


def builtin_camera_index() -> int:
    """Machine camera's OpenCV index, computed fresh. deviceType match, never
    name guessing. No saved index - indices aren't stable across launches
    (Continuity Camera reshuffles them), so remembering one is a footgun."""
    devs = camera_devices()
    for i, (name, dtype) in enumerate(devs):
        if "BuiltIn" in dtype:
            return i
    for i, (name, dtype) in enumerate(devs):
        if "FaceTime" in name or "Built-in" in name:
            return i
    return 0




def newest_calibration() -> Path:
    """Prefer the onboarded webcam profile over the photo bootstrap."""
    cal_dir = ROOT / "calibration"
    for name in ("profile.json", "nate-webcam.json"):
        if (cal_dir / name).exists():
            return cal_dir / name
    return cal_dir / "nate-v1.json"


LABELS = {
    "ott_brow": "OTT   brow",
    "drive_mouth": "DRIVE mouth",
    "phase_squint": "PHASE squint",
    "filth_disgust": "FILTH disgust",
}


def render(out: dict[str, float], latched: set[str], fps: float, infer_ms: float) -> str:
    lines = ["BASS FACE  --  ctrl-c to quit", ""]
    for name in CHANNEL_ORDER:
        v = out[name]
        bar = "█" * round(v * 24)
        tag = " [LOCK]" if name in latched else ""
        lines.append(f"{LABELS[name]:<14} {bar:<24} {v:5.2f}{tag}")
    lines.append("")
    lines.append(f"{fps:5.1f} fps   inference {infer_ms:5.1f} ms")
    return "\x1b[H\x1b[J" + "\n".join(lines)


def main() -> None:
    import argparse

    import cv2
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    sys.path.insert(0, str(ROOT))
    from tracker.outputs import open_outputs

    ap = argparse.ArgumentParser()
    ap.add_argument("--no-midi", action="store_true", help="skip virtual MIDI port")
    ap.add_argument("--no-osc", action="store_true", help="skip OSC sender")
    ap.add_argument("--camera", type=int, default=None,
                    help="camera index override (default: built-in FaceTime cam)")
    ap.add_argument("--no-preview", action="store_true", help="terminal meters only")
    ap.add_argument("--recalibrate", action="store_true",
                    help="redo the guided calibration before tracking")
    args = ap.parse_args()
    outputs = open_outputs(midi=not args.no_midi, osc=not args.no_osc)

    opts = vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(
            model_asset_path=str(ROOT / "models" / "face_landmarker.task")),
        running_mode=vision.RunningMode.VIDEO,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=1,
    )
    landmarker = vision.FaceLandmarker.create_from_options(opts)

    devs = camera_devices()
    n_cams = max(len(devs), 1)
    cam_idx = args.camera if args.camera is not None else builtin_camera_index()
    for i, (name, dtype) in enumerate(devs):
        marker = " <- using" if i == cam_idx else ""
        print(f"  cam {i}: {name}{marker}", file=sys.stderr)

    def open_camera(idx: int):
        c = cv2.VideoCapture(idx)
        c.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        c.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return c

    cap = open_camera(cam_idx)
    if not cap.isOpened():
        sys.exit("camera unavailable - check System Settings > Privacy > Camera")

    def cycle_camera(idx):
        idx = (idx + 1) % max(n_cams, idx + 2)
        new = open_camera(idx)
        if not new.isOpened():
            idx = 0
            new = open_camera(idx)
        print(f"switched to camera {idx}", file=sys.stderr)
        return idx, new

    # Preflight: user confirms the face camera BEFORE calibration/tracking.
    if not args.no_preview:
        while True:
            ok, frame = cap.read()
            if not ok:
                continue
            disp = cv2.flip(frame, 1)
            cv2.putText(disp, "THIS CAMERA?", (20, 44),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 200, 255), 3)
            cv2.putText(disp, "c = switch camera   ENTER = start",
                        (20, 84), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (255, 255, 255), 1)
            cv2.imshow("Bass Face", disp)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("c"):
                cap.release()
                cam_idx, cap = cycle_camera(cam_idx)
            elif key in (13, ord("s")):
                break
            elif key == ord("q"):
                cap.release()
                cv2.destroyAllWindows()
                return

    t0 = time.monotonic()

    from tracker.calibrate import PROFILE, run_calibration
    if args.recalibrate or not PROFILE.exists():
        print("no calibration profile - running guided onboarding first",
              file=sys.stderr)
        run_calibration(cap, landmarker, t0)

    engine = Engine.from_calibration(newest_calibration())
    print(f"calibration: {newest_calibration().name}", file=sys.stderr)
    shake = ShakeDetector()
    unlocked_flash_until = 0.0

    frames = 0
    fps = 0.0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                continue
            t = time.monotonic()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            t_inf = time.monotonic()
            result = landmarker.detect_for_video(mp_img, int((t - t0) * 1000))
            infer_ms = (time.monotonic() - t_inf) * 1000

            if result.face_blendshapes:
                shapes = {c.category_name: c.score
                          for c in result.face_blendshapes[0]}
                out = engine.update(shapes, t)
            else:
                out = {name: 0.0 for name in CHANNEL_ORDER}

            if result.facial_transformation_matrixes:
                m = result.facial_transformation_matrixes[0]
                yaw = math.atan2(m[0][2], m[2][2])
                if shake.update(yaw, t):
                    engine.release_all()
                    unlocked_flash_until = t + 0.6
                    print("unlocked (head shake)", file=sys.stderr)

            for o in outputs:
                o.send(out)

            if not args.no_preview:
                disp = cv2.flip(frame, 1)
                h, w = disp.shape[:2]
                if result.face_landmarks:
                    for lm in result.face_landmarks[0][::2]:
                        cv2.circle(disp, (w - int(lm.x * w), int(lm.y * h)),
                                   1, (0, 255, 0), -1)
                for i, name in enumerate(CHANNEL_ORDER):
                    v, y = out[name], 20 + i * 28
                    cv2.rectangle(disp, (10, y), (10 + int(v * 200), y + 18),
                                  (0, 140, 255), -1)
                    cv2.rectangle(disp, (10, y), (210, y + 18), (255, 255, 255), 1)
                    label = LABELS[name].split()[0]
                    if name in engine.latched_channels():
                        label += " LOCK"
                    cv2.putText(disp, label, (218, y + 14),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
                cv2.putText(disp, f"cam {cam_idx}  (c = switch, q = quit, "
                            f"shake head = unlock)",
                            (10, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                            (200, 200, 200), 1)
                if t < unlocked_flash_until:
                    cv2.putText(disp, "UNLOCKED", (w // 2 - 90, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                cv2.imshow("Bass Face", disp)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                if key == ord("c"):
                    cap.release()
                    cam_idx, cap = cycle_camera(cam_idx)

            frames += 1
            if frames % 10 == 0:
                fps = 10 / max(t - getattr(main, "_t_fps", t0), 1e-6)
                main._t_fps = t
            sys.stdout.write(render(out, engine.latched_channels(), fps, infer_ms))
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        for o in outputs:
            o.close()


if __name__ == "__main__":
    main()
