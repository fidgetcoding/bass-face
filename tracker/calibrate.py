"""Guided webcam calibration -> calibration/nate-webcam.json.

One neutral hold (floors), then 4 sweeps - neutral to YOUR max, one per
channel (peak = p95 of the sweep). core.py runs this automatically on first
launch (no profile) or with --recalibrate.

Standalone run: .venv/bin/python tracker/calibrate.py
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "calibration" / "profile.json"

CHANNEL_MEMBERS = {
    "ott_brow": ["browInnerUp", "browOuterUpLeft", "browOuterUpRight"],
    "drive_mouth": ["jawOpen"],
    "phase_squint": ["eyeSquintLeft", "eyeSquintRight", "eyeBlinkLeft", "eyeBlinkRight"],
    "filth_disgust": ["browDownLeft", "browDownRight"],
}

SWEEPS = [
    ("ott_brow", "Neutral, then raise EYEBROWS to your max"),
    ("drive_mouth", "Neutral, then open MOUTH to the widest O"),
    ("phase_squint", "Neutral, then SQUINT as hard as you can"),
    ("filth_disgust", "Neutral, then FULL DISGUST bass face"),
]

COUNTDOWN_S = 2
NEUTRAL_S = 2
SWEEP_S = 4


def _channel_value(shapes: dict, members: list[str]) -> float:
    return float(np.mean([shapes.get(m, 0.0) for m in members]))


def run_calibration(cap, landmarker, t0: float) -> Path:
    """Guided flow on an already-open capture + landmarker. Returns profile path."""
    import cv2
    import mediapipe as mp

    def show(frame, line1, line2, capturing):
        disp = cv2.flip(frame, 1)
        color = (0, 0, 255) if capturing else (0, 200, 255)
        cv2.putText(disp, line1, (20, 44), cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 3)
        cv2.putText(disp, line2, (20, 84), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 255), 1)
        cv2.imshow("Bass Face Calibration", disp)
        cv2.waitKey(1)

    def capture(seconds, title, prompt):
        """Collect per-channel raw values for `seconds`, with live preview."""
        vals = {ch: [] for ch in CHANNEL_MEMBERS}
        dropped = 0
        t_end = time.monotonic() + seconds
        while time.monotonic() < t_end:
            ok, frame = cap.read()
            if not ok:
                continue
            show(frame, title, prompt, capturing=True)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            ts = int((time.monotonic() - t0) * 1000)
            result = landmarker.detect_for_video(mp_img, ts)
            if not result.face_blendshapes:
                dropped += 1
                continue
            shapes = {c.category_name: c.score for c in result.face_blendshapes[0]}
            for ch, members in CHANNEL_MEMBERS.items():
                vals[ch].append(_channel_value(shapes, members))
        n = len(vals["ott_brow"])
        if n < 10:
            sys.exit(f"only {n} usable frames ({dropped} dropped) - lighting? re-run")
        return vals

    def countdown(title, prompt):
        for n in range(COUNTDOWN_S, 0, -1):
            t_end = time.monotonic() + 1
            while time.monotonic() < t_end:
                ok, frame = cap.read()
                if ok:
                    show(frame, f"{title} in {n}", prompt, capturing=False)

    print("\n=== BASS FACE CALIBRATION ===")
    countdown("NEUTRAL", "Relax. Dead face.")
    neutral = capture(NEUTRAL_S, "HOLD NEUTRAL", "Relax. Dead face.")
    floors = {ch: float(np.median(v)) for ch, v in neutral.items()}

    calib = {"version": 3, "source": "webcam-sweeps", "channels": {}}
    print("\nchannel        floor   peak")
    for ch, prompt in SWEEPS:
        countdown(ch.upper(), prompt)
        sweep = capture(SWEEP_S, f"SWEEP: {ch.upper()}", prompt)
        peak = float(np.percentile(sweep[ch], 95))
        floor = floors[ch]
        if peak - floor < 0.05:
            print(f"⚠️  {ch}: span {peak - floor:.3f} too small - expression not "
                  f"read; rerun with --recalibrate")
        calib["channels"][ch] = {
            "members": CHANNEL_MEMBERS[ch],
            "floor": round(floor, 4),
            "peak": round(peak, 4),
            "peak_phase": f"sweep:{ch}",
        }
        print(f"{ch:<14} {floor:.3f}   {peak:.3f}")

    PROFILE.write_text(json.dumps(calib, indent=2))
    print(f"\nwrote {PROFILE}")
    try:
        import cv2 as _cv2
        _cv2.destroyWindow("Bass Face Calibration")
    except Exception:
        pass
    return PROFILE


def main() -> None:
    import cv2
    import mediapipe as mp  # noqa: F401
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    sys.path.insert(0, str(ROOT))
    from tracker.core import builtin_camera_index

    opts = vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(
            model_asset_path=str(ROOT / "models" / "face_landmarker.task")),
        running_mode=vision.RunningMode.VIDEO,
        output_face_blendshapes=True,
        num_faces=1,
    )
    landmarker = vision.FaceLandmarker.create_from_options(opts)
    cap = cv2.VideoCapture(builtin_camera_index())  # standalone: no preflight
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        sys.exit("camera unavailable - check System Settings > Privacy > Camera")
    try:
        run_calibration(cap, landmarker, time.monotonic())
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
