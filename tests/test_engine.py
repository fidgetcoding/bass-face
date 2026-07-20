"""Engine unit tests with synthetic blendshape sequences. Run directly:
.venv/bin/python tests/test_engine.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tracker.core import CHANNEL_ORDER, Engine

BOOTSTRAP = Path(__file__).resolve().parent.parent / "calibration" / "nate-v1.json"


def make_engine(warmup=0.0) -> Engine:
    from tracker.core import CONFIG
    return Engine.from_calibration(BOOTSTRAP, {**CONFIG, "warmup_s": warmup})


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
    _, t = feed(e, shapes_for(squint=0.7, browdown=0.5), t, 1.0)
    vals = []
    for i in range(45):  # 1.5s of release at 30fps
        out = e.update(shapes_for(), t + i / 30)
        vals.append(out["ott_brow"])
    mids = [v for v in vals if 0.1 < v < 0.9]
    assert len(mids) >= 3, f"snapped instead of gliding: {vals[:12]}"
    assert vals[-1] < 0.05, vals[-1]
    print("✓ release glides down instead of snapping")


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

def test_far_drift_static_escape():
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(brow=0.72), t, 1.0)
    _, t = feed(e, shapes_for(squint=0.7, browdown=0.5), t, 1.0)
    # rest with filth floor badly drifted: norm ~0.5, beyond stuck (engage)
    # escape and beyond the 0.3-span learn band
    out, t = feed(e, shapes_for(browdown=0.31), t, 6.0)
    assert e.max_engaged_stage == 0, f"far drift never released: {e.max_engaged_stage}"
    assert out["ott_brow"] < 0.1, out
    print("✓ far-drift static escape releases")

def test_post_hold_residual_tension_releases():
    """debug.log 2026-07-19: after a 20s bass face, residual tension keeps
    channels fluttering 0.1-0.45 - old escapes never fired."""
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(squint=0.7, browdown=0.5), t, 8.0)  # long hold
    # residual tension: flutter between values whose lives cross release/engage
    out = None
    for i in range(150):  # 5s of flutter at 30fps
        bd = 0.24 if (i // 8) % 2 == 0 else 0.31
        sq = 0.30 if (i // 6) % 2 == 0 else 0.34
        out = e.update(shapes_for(squint=sq, browdown=bd), t + i / 30)
    t += 5.0
    assert e.max_engaged_stage == 0, f"post-hold flutter stuck: {e.max_engaged_stage}"
    assert out["phase_squint"] < 0.3, out
    print("✓ post-hold residual tension releases")

def test_apex_collapse_releases_fast():
    """Releasing the bass face must drain ALL channels in under ~1.2s -
    no stall waiting for neutral confirmation."""
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(squint=0.7, browdown=0.5), t, 3.0)  # bass face
    out, t = feed(e, shapes_for(), t, 1.2)  # release the scrunch
    assert out["ott_brow"] < 0.15, f"stall: {out}"
    assert out["phase_squint"] < 0.15, f"stall: {out}"
    assert e.max_engaged_stage == 0 or e.releasing, "should be draining/done"
    print("✓ apex collapse releases fast (no stall)")


def test_blink_dip_does_not_apex_release():
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(squint=0.7), t, 2.0)   # stage-3 frontier hold
    _, t = feed(e, shapes_for(squint=0.05), t, 0.1)  # 100ms blink-like dip
    out, t = feed(e, shapes_for(squint=0.7), t, 1.0)
    assert not e.releasing and e.max_engaged_stage >= 3
    assert out["phase_squint"] > 0.8, out
    print("✓ blink dip does not apex-release")

def test_warmup_blocks_phantom_startup_phrase():
    """Stale floor + residual rest face read 0.35+ at launch and cascade-
    filled a phantom phrase. Warmup blocks engagement while floors settle."""
    e = make_engine(warmup=2.5)
    t = 0.0
    out, t = feed(e, shapes_for(browdown=0.31), t, 2.4)  # drifted rest face
    assert e.max_engaged_stage == 0, f"phantom phrase: {e.max_engaged_stage}"
    assert out["ott_brow"] < 0.05, out
    print("✓ warmup blocks phantom startup phrase")

def test_release_synchronized_no_stagger():
    """All channels must move down TOGETHER the moment the face releases -
    no filth-first-then-the-others stagger."""
    e = make_engine()
    t = 0.0
    _, t = feed(e, shapes_for(squint=0.7, browdown=0.5), t, 3.0)  # bass face
    started_moving_gap = None
    filth_fall_frame = None
    for i in range(45):
        out = e.update(shapes_for(), t + i / 30)
        assert abs(out["ott_brow"] - out["drive_mouth"]) < 0.02  # in lockstep
        if filth_fall_frame is None and out["filth_disgust"] < 0.5:
            filth_fall_frame = i
        if started_moving_gap is None and filth_fall_frame is not None \
                and out["ott_brow"] < 0.97:
            started_moving_gap = i - filth_fall_frame
    assert started_moving_gap is not None and started_moving_gap <= 3, \
        f"latched channels lagged {started_moving_gap} frames behind filth"
    print("✓ release is synchronized (no stagger)")

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

def test_solo_brow_riding_not_eaten_by_floor():
    """Sub-engage expressive brow moves must keep full response - the floor
    must not chase a moving channel (only static drift learns)."""
    e = make_engine()
    t = 0.0
    outs = []
    for i in range(240):  # 8s of slow brow riding below engage
        b = 0.10 if (i // 15) % 2 == 0 else 0.24
        out = e.update(shapes_for(brow=b), t + i / 30)
        outs.append(out["ott_brow"])
    ch = e.channels[0]
    assert ch.floor_track < ch.floor + 0.05, f"floor chased brow: {ch.floor_track}"
    swing = max(outs[-60:]) - min(outs[-60:])
    assert swing > 0.12, f"brow response collapsed: swing {swing:.3f}"
    print("✓ solo brow riding keeps full response")


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
    test_far_drift_static_escape()
    test_post_hold_residual_tension_releases()
    test_apex_collapse_releases_fast()
    test_blink_dip_does_not_apex_release()
    test_warmup_blocks_phantom_startup_phrase()
    test_release_synchronized_no_stagger()
    test_solo_brow_riding_not_eaten_by_floor()
    print("all passed")
