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
    "cascade_ms": 400,      # ramp time for cascade-fill and release drain
    "cascade_from_stage": 4,  # ONLY the full bass face fills lower stages to
                              # 1.0; middle stages ratchet real peaks (mouth
                              # open must not drag OTT up on its own)
    "cancel_ms": 150,       # re-engagement must sustain this long to cancel a
                            # release - blinks (~100ms) spike the squint channel
                            # and must not reset the neutral clock
    "stuck_ms": 1200,       # latched + everything below stuck_ceiling this
                            # long = resting with residual tension / drifted
                            # floor; re-zero floors so the phrase can release
    "stuck_ceiling": 0.6,   # post-long-hold residual tension flutters up to
                            # ~0.45 (debug.log 2026-07-19); deliberate holds
                            # run ~0.95+, so 0.6 separates them cleanly
    "static_ms": 1500,      # latched + every channel motionless + nothing held
                            # high this long = at rest with badly drifted floor
                            # (beyond the learn band); rebaseline and release
    "static_band": 0.08,    # max live movement that still counts as motionless
    "apex_release": 0.25,   # frontier stage falling below this...
    "apex_min_peak": 0.6,   # ...after peaking above this = the come-down
                            # gesture; drain everything immediately (no
                            # neutral wait - kills the release stall)
    "apex_ms": 150,         # sustained collapse (blinks are ~100ms)
    "warmup_s": 2.5,        # no engagement right after launch - floors need a
                            # beat to settle onto the actual resting face
                            # (stale floor read 0.35 at rest -> phantom phrase)
    "still_learn_s": 2.0,   # upward floor learning needs this much continuous
                            # stillness - riding plateaus must not count as drift
    "release_follow": 0.5,  # once the frontier falls below this fraction of
                            # its peak, latched channels follow it down
                            # proportionally - all four reach zero the same
                            # instant the face does (synchronized release)
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
    floor_track: float | None = None  # drift-adaptive floor (starts at floor)
    last_raw: float = 0.0
    raw_lo: float = 0.0    # leaky min of raw - honest rebaseline target
    win_lo: float = 0.0    # leaky min/max of live - recent-motion window
    win_hi: float = 0.0
    still_since: float | None = None


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
    cascade_from_stage: int = 4
    cancel_ms: float = 150.0
    stuck_ms: float = 1200.0
    stuck_ceiling: float = 0.6
    static_ms: float = 1500.0
    static_band: float = 0.08
    static_since: float | None = None
    apex_release: float = 0.25
    apex_min_peak: float = 0.6
    apex_ms: float = 150.0
    apex_since: float | None = None
    warmup_s: float = 2.5
    started_at: float | None = None
    release_follow: float = 0.5
    still_learn_s: float = 2.0
    max_engaged_stage: int = 0  # highest stage engaged this phrase (1-based)
    neutral_since: float | None = None
    above_since: float | None = None
    stuck_since: float | None = None
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
                   cascade_ms=config.get("cascade_ms", 150.0),
                   cascade_from_stage=config.get("cascade_from_stage", 4),
                   cancel_ms=config.get("cancel_ms", 150.0),
                   stuck_ms=config.get("stuck_ms", 1200.0),
                   stuck_ceiling=config.get("stuck_ceiling", 0.6),
                   static_ms=config.get("static_ms", 1500.0),
                   static_band=config.get("static_band", 0.08),
                   apex_release=config.get("apex_release", 0.25),
                   apex_min_peak=config.get("apex_min_peak", 0.6),
                   apex_ms=config.get("apex_ms", 150.0),
                   warmup_s=config.get("warmup_s", 2.5),
                   release_follow=config.get("release_follow", 0.5),
                   still_learn_s=config.get("still_learn_s", 2.0))

    def update(self, shapes: dict[str, float], t: float) -> dict[str, float]:
        dt = (t - self.t_prev) if self.t_prev is not None else 0.0
        self.t_prev = t
        if self.started_at is None:
            self.started_at = t
        in_warmup = (t - self.started_at) < self.warmup_s
        for ch in self.channels:
            raw = sum(shapes.get(m, 0.0) for m in ch.members) / len(ch.members)
            span = max(ch.peak - ch.floor, 1e-6)
            if ch.floor_track is None:
                ch.floor_track = ch.floor
            # Floor learning. Warmup: whatever the face is at launch IS
            # rest - learn it fast. After: downward correction is immediate
            # (in band); upward learning ONLY when the channel reads truly
            # quiet (below release) so expressive riding is never eaten.
            # Drift that idles above release is handled by the escapes.
            if in_warmup and dt > 0:
                rate = 0.5 * span * dt
                ch.floor_track += max(-rate, min(rate, raw - ch.floor_track))
            elif (self.max_engaged_stage == 0 and dt > 0
                    and abs(raw - ch.floor_track) < 0.45 * span
                    and (raw < ch.floor_track or ch.live < self.release)):
                rate = 0.1 * span * dt
                ch.floor_track += max(-rate, min(rate, raw - ch.floor_track))
            ch.floor_track = min(max(ch.floor_track, 0.0),
                                 ch.floor + 0.8 * span)
            ch.last_raw = raw
            ch.raw_lo = min(raw, ch.raw_lo + 0.25 * span * dt)
            norm = min(max((raw - ch.floor_track) / span, 0.0), 1.0) ** ch.gamma
            ch.live = ch.filt(norm, t)
            if not self.releasing:  # a draining phrase is over - don't refill
                ch.phrase_peak = max(ch.phrase_peak, ch.live)
            decay = 0.6 * dt
            ch.win_lo = min(ch.live, ch.win_lo + decay)
            ch.win_hi = max(ch.live, ch.win_hi - decay)

        for stage, ch in enumerate(self.channels, start=1):
            if (not in_warmup and ch.live >= self.engage
                    and stage > self.max_engaged_stage):
                self.max_engaged_stage = stage

        # Apex collapse: the frontier stage falling hard IS the release
        # gesture - drain immediately instead of waiting for full neutral.
        if self.max_engaged_stage > 0 and not self.releasing:
            fch = self.channels[self.max_engaged_stage - 1]
            if fch.phrase_peak > self.apex_min_peak and fch.live < self.apex_release:
                if self.apex_since is None:
                    self.apex_since = t
                elif (t - self.apex_since) * 1000 >= self.apex_ms:
                    self.releasing = True
                    self.apex_since = None
            else:
                self.apex_since = None

        # Cascade-fill: ONLY the full bass face implies everything below it.
        # Jump straight to bass face -> OTT/drive/squint ramp to 1.0. Middle
        # stages never fill lower ones (mouth open must not drag OTT up).
        if (self.max_engaged_stage >= self.cascade_from_stage and dt > 0
                and not self.releasing):
            step = dt / (self.cascade_ms / 1000.0)
            for stage, ch in enumerate(self.channels, start=1):
                if stage < self.max_engaged_stage and ch.phrase_peak < 1.0:
                    ch.phrase_peak = min(1.0, ch.phrase_peak + step)

        # Stuck escape: latched but everything sits below engage - the resting
        # floor drifted (hood, head pitch, lighting) and parked a channel in
        # the release/engage dead zone. Re-zero floors; release then fires.
        if (self.max_engaged_stage > 0 and not self.releasing
                and all(ch.live < self.stuck_ceiling for ch in self.channels)):
            if self.stuck_since is None:
                self.stuck_since = t
            elif (t - self.stuck_since) * 1000 >= self.stuck_ms:
                self._rebaseline()
                self.stuck_since = None
        else:
            self.stuck_since = None

        # Second escape for drift beyond the learn band: latched + every
        # channel motionless + nothing held high = at rest, floors are lying.
        if (self.max_engaged_stage > 0 and not self.releasing
                and all(ch.win_hi - ch.win_lo < self.static_band
                        for ch in self.channels)
                and all(ch.live < 0.85 for ch in self.channels)):
            if self.static_since is None:
                self.static_since = t
            elif (t - self.static_since) * 1000 >= self.static_ms:
                self._rebaseline()
                self.static_since = None
        else:
            self.static_since = None

        if all(ch.live < self.release for ch in self.channels):
            self.above_since = None
            if self.neutral_since is None:
                self.neutral_since = t
            elif (t - self.neutral_since) * 1000 >= self.release_ms:
                self.releasing = True
        else:
            self.neutral_since = None
            # Catch-the-fall requires REAL re-engagement (above engage,
            # sustained past blink length). Residual tension between the
            # neutral floor and engage must NOT cancel a running drain -
            # that was the release stall.
            if any(ch.live >= self.engage for ch in self.channels):
                if self.above_since is None:
                    self.above_since = t
                elif (t - self.above_since) * 1000 >= self.cancel_ms:
                    self.releasing = False
            else:
                self.above_since = None

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
        frontier = self.max_engaged_stage
        ratio = 1.0
        if frontier > 0:
            fch = self.channels[frontier - 1]
            denom = max(fch.phrase_peak * self.release_follow, 1e-6)
            ratio = min(fch.live / denom, 1.0)
        for stage, ch in enumerate(self.channels, start=1):
            if stage < frontier:
                out[ch.name] = ch.phrase_peak * ratio
            else:
                out[ch.name] = ch.live
        return out

    def latched_channels(self) -> set[str]:
        return {ch.name for stage, ch in enumerate(self.channels, start=1)
                if stage < self.max_engaged_stage}

    def release_all(self) -> None:
        """Manual unlock (head-shake gesture) - same effect as neutral hold."""
        for ch in self.channels:
            ch.phrase_peak = 0.0
        self.max_engaged_stage = 0

    def _rebaseline(self) -> None:
        """Adopt current raws as floors (clamped) so a drifted rest releases."""
        for ch in self.channels:
            span = max(ch.peak - ch.floor, 1e-6)
            ch.floor_track = min(max(ch.floor_track, ch.raw_lo),
                                 ch.floor + 0.8 * span)


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


def render(out: dict[str, float], latched: set[str], fps: float,
           infer_ms: float, status: str = "") -> str:
    lines = [f"BASS FACE  --  ctrl-c to quit   {status}", ""]
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
    ap.add_argument("--debug", action="store_true",
                    help="log per-frame engine state to debug.log")
    ap.add_argument("--autostart", action="store_true",
                    help="launched by the M4L device: skip the camera-confirm "
                         "gate, trust the built-in pick")
    args = ap.parse_args()
    debug_f = open(ROOT / "debug.log", "w") if args.debug else None
    if debug_f:
        cols = ["t", "eng", "rel", "neu", "stuck", "static"]
        for n in CHANNEL_ORDER:
            cols += [f"{n}.raw", f"{n}.floor", f"{n}.live", f"{n}.peak"]
        debug_f.write(",".join(cols) + "\n")
        print(f"debug log: {ROOT / 'debug.log'}", file=sys.stderr)
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
    if not args.no_preview and not args.autostart:
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
    solo: int | None = None  # 0-3 = only that channel broadcasts (mapping aid)

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

            sendable = out if solo is None else {
                name: v for i, (name, v) in enumerate(out.items()) if i == solo}
            for o in outputs:
                o.send(sendable)

            if debug_f:
                row = [f"{t - t0:.2f}", str(engine.max_engaged_stage),
                       "1" if engine.releasing else "0",
                       "1" if engine.neutral_since is not None else "0",
                       "1" if engine.stuck_since is not None else "0",
                       "1" if engine.static_since is not None else "0"]
                for ch in engine.channels:
                    row += [f"{ch.last_raw:.3f}",
                            f"{ch.floor_track if ch.floor_track is not None else -1:.3f}",
                            f"{ch.live:.3f}", f"{ch.phrase_peak:.3f}"]
                debug_f.write(",".join(row) + "\n")

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
                hint = (f"cam {cam_idx}  (c = switch, q = quit, shake = unlock, "
                        f"1-4 = solo CC for mapping, 0 = all)")
                if solo is not None:
                    cv2.putText(disp, f"SOLO: {LABELS[CHANNEL_ORDER[solo]]} "
                                f"(CC {20 + solo}) - press 0 to restore",
                                (10, h - 36), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                                (0, 200, 255), 2)
                cv2.putText(disp, hint, (10, h - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
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
                elif key in (ord("1"), ord("2"), ord("3"), ord("4")):
                    solo = key - ord("1")
                    print(f"solo: {CHANNEL_ORDER[solo]} (CC {20 + solo})",
                          file=sys.stderr)
                elif key == ord("0"):
                    solo = None
                    print("solo off - all channels broadcasting", file=sys.stderr)

            frames += 1
            if frames % 10 == 0:
                fps = 10 / max(t - getattr(main, "_t_fps", t0), 1e-6)
                main._t_fps = t
            status = ""
            if solo is not None:
                status = (f"⚠️  SOLO {CHANNEL_ORDER[solo]} ONLY - other knobs "
                          f"in Live are FROZEN - press 0 in video window")
            sys.stdout.write(render(out, engine.latched_channels(), fps,
                                    infer_ms, status))
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        for o in outputs:
            o.close()
        if debug_f:
            debug_f.close()


if __name__ == "__main__":
    main()
