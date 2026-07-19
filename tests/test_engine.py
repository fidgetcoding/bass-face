"""Engine unit tests with synthetic blendshape sequences. Run directly:
.venv/bin/python tests/test_engine.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tracker.core import CHANNEL_ORDER, Engine, newest_calibration


def make_engine() -> Engine:
    return Engine.from_calibration(Path(newest_calibration()))


def shapes_for(brow=0.0, jaw=0.0, squint=0.0, browdown=0.0) -> dict:
    return {
        "browInnerUp": brow, "browOuterUpLeft": brow, "browOuterUpRight": brow,
        "jawOpen": jaw,
        "eyeSquintLeft": squint, "eyeSquintRight": squint,
        "eyeBlinkLeft": squint, "eyeBlinkRight": squint,
        "browDownLeft": browdown, "browDownRight": browdown,
    }


def feed(engine, shapes, t_start, seconds, hz=30):
    out = None
    for i in range(int(seconds * hz)):
        out = engine.update(shapes, t_start + i / hz)
    return out, t_start + seconds


def test_normalization_and_directionality():
    e = make_engine()
    out, _ = feed(e, shapes_for(), 0.0, 1.0)
    assert out["ott_brow"] < 0.1, out
    e2 = make_engine()
    out, _ = feed(e2, shapes_for(brow=0.72), 0.0, 1.0)
    assert out["ott_brow"] > 0.9, out
    assert out["drive_mouth"] < 0.1, out
    print("✓ normalization + directionality")


def test_ratchet_locks_brow_through_squint():
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(brow=0.72), t, 1.0)            # stage 1: brows up
    _, t = feed(e, shapes_for(brow=0.70, jaw=0.45), t, 1.0)  # stage 2: mouth opens
    # stage 3: squint - brows anatomically collapse
    out, t = feed(e, shapes_for(brow=0.02, jaw=0.05, squint=0.65), t, 1.0)
    assert out["ott_brow"] > 0.9, f"ratchet failed: {out}"
    assert "ott_brow" in e.latched_channels()
    assert out["phase_squint"] > 0.8, out
    print("✓ ratchet locks brow through squint")


def test_neutral_release_clears_latches():
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(brow=0.72), t, 1.0)
    _, t = feed(e, shapes_for(jaw=0.45), t, 1.0)
    out, t = feed(e, shapes_for(), t, 2.0)  # neutral hold >> release_ms
    assert e.max_engaged_stage == 0, e.max_engaged_stage
    assert out["ott_brow"] < 0.1, out
    assert not e.latched_channels()
    print("✓ neutral release clears latches")


def test_pre_engagement_brow_moves_freely():
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(brow=0.72), t, 1.0)
    out, t = feed(e, shapes_for(brow=0.10), t, 1.0)  # no higher stage engaged yet
    assert out["ott_brow"] < 0.35, f"brow should fall freely pre-engagement: {out}"
    print("✓ pre-engagement brow moves freely")


if __name__ == "__main__":
    test_normalization_and_directionality()
    test_ratchet_locks_brow_through_squint()
    test_neutral_release_clears_latches()
    test_pre_engagement_brow_moves_freely()
    test_release_all_unlocks()
    print("all passed")


def test_release_all_unlocks():
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(brow=0.72), t, 1.0)
    _, t = feed(e, shapes_for(jaw=0.45), t, 1.0)
    assert e.max_engaged_stage >= 2
    e.release_all()
    assert e.max_engaged_stage == 0 and not e.latched_channels()
    print("✓ release_all unlocks")
