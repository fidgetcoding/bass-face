"""Engine unit tests with synthetic blendshape sequences. Run directly:
.venv/bin/python tests/test_engine.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tracker.core import CHANNEL_ORDER, Engine

BOOTSTRAP = Path(__file__).resolve().parent.parent / "calibration" / "nate-v1.json"


def make_engine() -> Engine:
    return Engine.from_calibration(BOOTSTRAP)


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

def test_release_all_unlocks():
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(brow=0.72), t, 1.0)
    _, t = feed(e, shapes_for(jaw=0.45), t, 1.0)
    assert e.max_engaged_stage >= 2
    e.release_all()
    assert e.max_engaged_stage == 0 and not e.latched_channels()
    print("✓ release_all unlocks")

def test_direct_to_filth_cascades_lower_stages():
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(), t, 0.2)  # brief neutral
    # jump straight to full bass face (browdown + squint, no brow/jaw)
    out, t = feed(e, shapes_for(squint=0.7, browdown=0.5), t, 1.0)
    assert out["filth_disgust"] > 0.8, out
    assert out["ott_brow"] > 0.95, f"cascade failed: {out}"
    assert out["drive_mouth"] > 0.95, f"cascade failed: {out}"
    print("✓ direct-to-filth cascades lower stages to full")

def test_release_ramps_down_not_snap():
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(brow=0.72), t, 1.0)
    _, t = feed(e, shapes_for(squint=0.7, browdown=0.5), t, 1.0)  # latch ott at 1.0
    # smoothing needs ~330ms to reach neutral threshold, then 350ms confirm,
    # then the 400ms drain starts: probe mid-drain at 0.9s
    out, t = feed(e, shapes_for(), t, 0.9)
    assert 0.15 < out["ott_brow"] < 0.85, f"should be mid-drain: {out}"
    out, t = feed(e, shapes_for(), t, 1.0)  # ramp completes
    assert out["ott_brow"] < 0.05 and e.max_engaged_stage == 0, out
    print("✓ release ramps down instead of snapping")

def test_blink_does_not_block_release():
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(brow=0.72), t, 1.0)
    _, t = feed(e, shapes_for(squint=0.7, browdown=0.5), t, 1.0)
    _, t = feed(e, shapes_for(), t, 0.5)                 # relaxing...
    _, t = feed(e, shapes_for(squint=0.9), t, 0.1)       # blink spike (100ms)
    out, t = feed(e, shapes_for(), t, 1.5)               # keep relaxing
    assert e.max_engaged_stage == 0, f"blink blocked release: {e.max_engaged_stage}"
    assert out["ott_brow"] < 0.05, out
    print("✓ blink does not block release")


def test_sustained_reengage_cancels_release():
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(brow=0.72), t, 1.0)
    _, t = feed(e, shapes_for(squint=0.7, browdown=0.5), t, 1.0)
    _, t = feed(e, shapes_for(), t, 0.8)                 # drain likely started
    _, t = feed(e, shapes_for(squint=0.7), t, 0.5)       # real re-engage
    assert e.max_engaged_stage > 0, "sustained re-engage should keep latches"
    print("✓ sustained re-engage cancels release")

def test_dead_zone_drift_unsticks():
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(brow=0.72), t, 1.0)
    _, t = feed(e, shapes_for(squint=0.7, browdown=0.5), t, 1.0)
    # drift: filth raw parks between release and engage thresholds
    out, t = feed(e, shapes_for(browdown=0.23), t, 4.0)
    assert e.max_engaged_stage == 0, f"stuck in dead zone: {e.max_engaged_stage}"
    assert out["ott_brow"] < 0.05, out
    print("✓ dead-zone drift unsticks via floor rebaseline")


def test_held_frontier_not_rebaselined():
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(brow=0.72), t, 1.0)
    out, t = feed(e, shapes_for(squint=0.7), t, 3.0)  # deliberate long hold
    assert e.max_engaged_stage >= 3, "hold above engage must keep the phrase"
    assert out["phase_squint"] > 0.8, out
    print("✓ held frontier is not rebaselined")

def test_mouth_alone_does_not_fill_brow():
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(jaw=0.45), t, 1.5)  # mouth only, brows never up
    out, _ = feed(e, shapes_for(jaw=0.45), t, 0.1)
    assert out["ott_brow"] < 0.1, f"mouth must not drag OTT up: {out}"
    # brows still controllable upward mid-phrase
    out, t = feed(e, shapes_for(brow=0.72, jaw=0.45), t + 0.1, 1.0)
    assert out["ott_brow"] > 0.9, out
    print("✓ mouth alone does not fill brow; brow still rises mid-phrase")


if __name__ == "__main__":
    test_normalization_and_directionality()
    test_ratchet_locks_brow_through_squint()
    test_neutral_release_clears_latches()
    test_pre_engagement_brow_moves_freely()
    test_release_all_unlocks()
    test_direct_to_filth_cascades_lower_stages()
    test_release_ramps_down_not_snap()
    test_blink_does_not_block_release()
    test_sustained_reengage_cancels_release()
    test_dead_zone_drift_unsticks()
    test_held_frontier_not_rebaselined()
    test_mouth_alone_does_not_fill_brow()
    print("all passed")
