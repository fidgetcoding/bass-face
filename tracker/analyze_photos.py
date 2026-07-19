"""Run the 5 phase photos through MediaPipe and derive Nate's v1 calibration.

Output: prints a per-phase blendshape table and writes calibration/nate-v1.json
with neutral->peak ranges for the 4 mapped channels.
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "calibration" / "photos"
MODEL = ROOT / "models" / "face_landmarker.task"

# Phase order matches the escalation ladder.
PHASES = ["neutral", "eyebrows-raised", "mouth-open", "eyes-closed", "bass-face"]

# Blendshapes worth watching for this instrument.
WATCH = [
    "browInnerUp", "browOuterUpLeft", "browOuterUpRight",
    "browDownLeft", "browDownRight",
    "jawOpen", "mouthFunnel", "mouthPucker",
    "eyeSquintLeft", "eyeSquintRight", "eyeBlinkLeft", "eyeBlinkRight",
    "eyeWideLeft", "eyeWideRight",
    "noseSneerLeft", "noseSneerRight",
    "mouthShrugUpper", "mouthUpperUpLeft", "mouthUpperUpRight",
    "cheekSquintLeft", "cheekSquintRight",
]

# Channel definitions: mean of the listed blendshapes.
CHANNELS = {
    "ott_brow": ["browInnerUp", "browOuterUpLeft", "browOuterUpRight"],
    "drive_mouth": ["jawOpen"],
    "phase_squint": ["eyeSquintLeft", "eyeSquintRight", "eyeBlinkLeft", "eyeBlinkRight"],
    # noseSneer/cheekSquint read 0.000 on Nate's face (weak MediaPipe blendshapes);
    # browDown separates bass-face (0.50) from eyes-closed (0.02) cleanly.
    "filth_disgust": ["browDownLeft", "browDownRight"],
}


FOREHEAD, CHIN = 10, 152  # face-mesh landmark indices


def detect(landmarker, img: Image.Image):
    """Return (blendshape dict, rotation) for the upright-face rotation.

    A face detected sideways/upside-down still yields blendshapes — garbage ones.
    Correct rotation is the one where the forehead->chin vector points straight
    down in image space.
    """
    best = None
    for rot in (0, 90, 180, 270):
        rotated = img.rotate(rot, expand=True) if rot else img
        arr = np.asarray(rotated.convert("RGB"))
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=arr)
        result = landmarker.detect(mp_img)
        if result.face_blendshapes and result.face_landmarks:
            lms = result.face_landmarks[0]
            dx = lms[CHIN].x - lms[FOREHEAD].x
            dy = lms[CHIN].y - lms[FOREHEAD].y
            uprightness = dy / (np.hypot(dx, dy) + 1e-9)  # 1.0 = perfectly upright
            if best is None or uprightness > best[2]:
                shapes = {c.category_name: c.score for c in result.face_blendshapes[0]}
                best = (shapes, rot, uprightness)
    if best is None or best[2] < 0.8:
        return None, None
    return best[0], best[1]


def main():
    opts = vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(MODEL)),
        output_face_blendshapes=True,
        num_faces=1,
    )
    landmarker = vision.FaceLandmarker.create_from_options(opts)

    all_shapes: dict[str, dict[str, float]] = {}
    for phase in PHASES:
        path = PHOTOS / f"{phase}.jpg"
        img = ImageOps.exif_transpose(Image.open(path))
        shapes, rot = detect(landmarker, img)
        if shapes is None:
            print(f"✗ {phase}: NO FACE DETECTED", file=sys.stderr)
            sys.exit(1)
        all_shapes[phase] = shapes
        print(f"✓ {phase} (rotation {rot}°)")

    # Table
    col = max(len(n) for n in WATCH) + 1
    header = "blendshape".ljust(col) + "".join(p[:12].rjust(13) for p in PHASES)
    print("\n" + header)
    print("-" * len(header))
    for name in WATCH:
        row = name.ljust(col)
        for p in PHASES:
            row += f"{all_shapes[p].get(name, 0.0):13.3f}"
        print(row)

    # Channel values per phase
    print("\nchannels (mean of member blendshapes)")
    for ch, members in CHANNELS.items():
        row = ch.ljust(col)
        for p in PHASES:
            v = float(np.mean([all_shapes[p].get(m, 0.0) for m in members]))
            row += f"{v:13.3f}"
        print(row)

    # Derived calibration: neutral floor -> per-channel peak across its phase
    peak_phase = {
        "ott_brow": "eyebrows-raised",
        "drive_mouth": "mouth-open",
        "phase_squint": "eyes-closed",
        "filth_disgust": "bass-face",
    }
    calib = {"subject": "nate", "version": 1, "channels": {}}
    for ch, members in CHANNELS.items():
        floor = float(np.mean([all_shapes["neutral"].get(m, 0.0) for m in members]))
        peak = float(np.mean([all_shapes[peak_phase[ch]].get(m, 0.0) for m in members]))
        calib["channels"][ch] = {
            "members": members,
            "floor": round(floor, 4),
            "peak": round(peak, 4),
            "peak_phase": peak_phase[ch],
        }
    calib["raw"] = {p: {k: round(v, 4) for k, v in s.items()} for p, s in all_shapes.items()}

    out = ROOT / "calibration" / "nate-v1.json"
    out.write_text(json.dumps(calib, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
