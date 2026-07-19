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
    max_engaged_stage: int = 0  # highest stage engaged this phrase (1-based)
    neutral_since: float | None = None

    @classmethod
    def from_calibration(cls, calib_path: Path, config: dict = CONFIG) -> "Engine":
        calib = json.loads(calib_path.read_text())
        f = config["filter"]
        chans = []
        for name in CHANNEL_ORDER:
            c = calib["channels"][name]
            chans.append(Channel(
                name=name, members=c["members"], floor=c["floor"], peak=c["peak"],
                gamma=config["gamma"][name],
                filt=OneEuro(f["min_cutoff"], f["beta"], f["d_cutoff"]),
            ))
        return cls(channels=chans, engage=config["engage"],
                   release=config["release"], release_ms=config["release_ms"])

    def update(self, shapes: dict[str, float], t: float) -> dict[str, float]:
        for ch in self.channels:
            raw = sum(shapes.get(m, 0.0) for m in ch.members) / len(ch.members)
            span = max(ch.peak - ch.floor, 1e-6)
            norm = min(max((raw - ch.floor) / span, 0.0), 1.0) ** ch.gamma
            ch.live = ch.filt(norm, t)
            ch.phrase_peak = max(ch.phrase_peak, ch.live)

        for stage, ch in enumerate(self.channels, start=1):
            if ch.live >= self.engage and stage > self.max_engaged_stage:
                self.max_engaged_stage = stage

        if all(ch.live < self.release for ch in self.channels):
            if self.neutral_since is None:
                self.neutral_since = t
            elif (t - self.neutral_since) * 1000 >= self.release_ms:
                for ch in self.channels:
                    ch.phrase_peak = 0.0
                self.max_engaged_stage = 0
        else:
            self.neutral_since = None

        out = {}
        for stage, ch in enumerate(self.channels, start=1):
            latched = stage < self.max_engaged_stage
            out[ch.name] = ch.phrase_peak if latched else ch.live
        return out

    def latched_channels(self) -> set[str]:
        return {ch.name for stage, ch in enumerate(self.channels, start=1)
                if stage < self.max_engaged_stage}


def newest_calibration() -> Path:
    """Prefer the guided webcam profile over the photo bootstrap."""
    cal_dir = ROOT / "calibration"
    webcam = cal_dir / "nate-webcam.json"
    return webcam if webcam.exists() else cal_dir / "nate-v1.json"


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
    args = ap.parse_args()
    outputs = open_outputs(midi=not args.no_midi, osc=not args.no_osc)

    engine = Engine.from_calibration(newest_calibration())
    print(f"calibration: {newest_calibration().name}", file=sys.stderr)

    opts = vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(
            model_asset_path=str(ROOT / "models" / "face_landmarker.task")),
        running_mode=vision.RunningMode.VIDEO,
        output_face_blendshapes=True,
        num_faces=1,
    )
    landmarker = vision.FaceLandmarker.create_from_options(opts)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        sys.exit("camera unavailable - check System Settings > Privacy > Camera")

    t0 = time.monotonic()
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

            for o in outputs:
                o.send(out)

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
        for o in outputs:
            o.close()


if __name__ == "__main__":
    main()
