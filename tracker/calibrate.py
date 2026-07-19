"""Guided webcam calibration -> calibration/nate-webcam.json.

Hold each of the 5 phases when prompted (2s countdown, 3s capture). Floors come
from the neutral phase median, peaks from the p90 of each channel's peak phase.
Output format matches nate-v1.json, and core.py auto-prefers the webcam profile.

Run: .venv/bin/python tracker/calibrate.py
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent

CHANNEL_MEMBERS = {
    "ott_brow": ["browInnerUp", "browOuterUpLeft", "browOuterUpRight"],
    "drive_mouth": ["jawOpen"],
    "phase_squint": ["eyeSquintLeft", "eyeSquintRight", "eyeBlinkLeft", "eyeBlinkRight"],
    "filth_disgust": ["browDownLeft", "browDownRight"],
}

PHASES = [
    ("neutral", "Relax. Dead face. Think about rent."),
    ("eyebrows-raised", "Eyebrows UP. Surprised. Hold it."),
    ("mouth-open", "Mouth OPEN in an O. Brows stay up."),
    ("eyes-closed", "Eyes SCRUNCHED shut. Feel the drop coming."),
    ("bass-face", "FULL BASS FACE. Disgust. The filthiest sound you've ever heard."),
]

PEAK_PHASE = {
    "ott_brow": "eyebrows-raised",
    "drive_mouth": "mouth-open",
    "phase_squint": "eyes-closed",
    "filth_disgust": "bass-face",
}

COUNTDOWN_S = 2
CAPTURE_S = 3


def main() -> None:
    import cv2
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

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
    samples: dict[str, dict[str, list[float]]] = {}

    for phase, prompt in PHASES:
        print(f"\n>>> {phase.upper()}: {prompt}")
        for n in range(COUNTDOWN_S, 0, -1):
            print(f"    {n}...")
            time.sleep(1)
        print("    HOLD")
        phase_samples: dict[str, list[float]] = {ch: [] for ch in CHANNEL_MEMBERS}
        dropped = 0
        t_end = time.monotonic() + CAPTURE_S
        while time.monotonic() < t_end:
            ok, frame = cap.read()
            if not ok:
                continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            ts = int((time.monotonic() - t0) * 1000)
            result = landmarker.detect_for_video(mp_img, ts)
            if not result.face_blendshapes:
                dropped += 1
                continue
            shapes = {c.category_name: c.score for c in result.face_blendshapes[0]}
            for ch, members in CHANNEL_MEMBERS.items():
                phase_samples[ch].append(
                    float(np.mean([shapes.get(m, 0.0) for m in members])))
        n_frames = len(phase_samples["ott_brow"])
        if n_frames < 10:
            sys.exit(f"only {n_frames} usable frames for {phase} - lighting? re-run")
        print(f"    captured {n_frames} frames ({dropped} dropped)")
        samples[phase] = phase_samples

    cap.release()

    calib = {"subject": "nate", "version": 2, "source": "webcam-guided", "channels": {}}
    print("\nchannel        floor   peak")
    for ch, members in CHANNEL_MEMBERS.items():
        floor = float(np.median(samples["neutral"][ch]))
        peak = float(np.percentile(samples[PEAK_PHASE[ch]][ch], 90))
        if peak - floor < 0.05:
            print(f"⚠️  {ch}: span {peak - floor:.3f} too small - phase not read, re-run")
        calib["channels"][ch] = {
            "members": members,
            "floor": round(floor, 4),
            "peak": round(peak, 4),
            "peak_phase": PEAK_PHASE[ch],
        }
        print(f"{ch:<14} {floor:.3f}   {peak:.3f}")

    out = ROOT / "calibration" / "nate-webcam.json"
    out.write_text(json.dumps(calib, indent=2))
    print(f"\nwrote {out}\ncore.py will now use this profile automatically")


if __name__ == "__main__":
    main()
