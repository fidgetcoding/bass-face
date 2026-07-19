# Implementation Plan: Bass Face v1 (Mac / Ableton Live 12)

## Overview

Face-tracking controller for Ableton. A Python sidecar watches the built-in webcam,
converts Nate's face into 4 escalation channels (calibrated from his 5 phase photos),
and streams them into Live 12 two ways: a virtual MIDI source (works in any Live
edition, day one) and OSC into a Max for Live mapper device (the shippable product).
Free product, Patreon funnel, name locked: **Bass Face**.

## Architecture Decisions

- **Controller, not distortion.** Bass Face maps face → any Live parameter
  (Expression-Control style). Users keep their own OTT/distortion chains.
- **Sidecar + device split.** MediaPipe can't live inside Max reliably; tracker runs
  as its own process, talks OSC (127.0.0.1:7400) + virtual CoreMIDI source
  ("Bass Face", CC 20–23). Two transports = M4L path AND edition-agnostic path.
- **Escalation ratchet.** Squinting anatomically drags brows down (photos confirm).
  Once the mouth-open stage engages, earlier channels latch at peak; global release
  when the face returns to neutral for N ms. Ladder only adds, never subtracts.
- **Calibration = guided webcam session.** The 5 phase photos are bootstrap/smoke-test
  only (`nate-v1.json`). Real profile comes from `calibrate.py`: guided on-camera
  session, hold each phase ~3s, robust stats (median floor / p90 peak) per channel →
  `nate-webcam.json`. Full multi-face calibration engine = v2.
- **Occlusion resilience (glasses/sunglasses).** Per-channel signal-health monitor +
  eye-patch luminance heuristic (dark patch over eye landmarks = sunglasses). Dead
  brow channel → remap OTT to head pitch (facial transform matrix — pose survives
  sunglasses); dead squint → fall back to cheekSquint (cheeks visible below frames);
  else disable channel with UI flag. Clear glasses mostly track; sunglasses are the
  real degradation case.
- **One-euro smoothing** on every channel — kills frame jitter without lag spikes.
- **Ableton Live 12 Suite confirmed on disk** → bundled Max editor available;
  device ships as `.amxd` saved into the M4L User Library.

## The 4 channels

| Channel | Blendshapes (mean) | Stage |
|---|---|---|
| ott_brow | browInnerUp, browOuterUp L/R | 1. eyebrows raised |
| drive_mouth | jawOpen (+mouthFunnel weight) | 2. mouth "O" |
| phase_squint | eyeSquint L/R, eyeBlink L/R | 3. eyes scrunch |
| filth_disgust | noseSneer L/R, cheekSquint L/R | 4. bass face |

## Task List

### Phase 1: Calibration ground truth
- [ ] T1: Run `analyze_photos.py` → blendshape table + `calibration/nate-v1.json`.
      Sanity: jawOpen peaks on mouth-open, browUp peaks on eyebrows-raised,
      squint peaks on eyes-closed, sneer/cheek peaks on bass-face.

### Phase 2: Live tracker core
- [ ] T2: `tracker/core.py` — webcam → FaceLandmarker (LIVE_STREAM mode) →
      normalize against nate-v1 floors/peaks → one-euro filter → ratchet state
      machine → 4 channels at 0–1. Terminal meter display + FPS/latency readout.
      Verify: on-camera run; each face phase moves only its channel; ratchet holds
      brow channel through squint; neutral releases all.

- [ ] T2.5: `tracker/calibrate.py` — guided webcam calibration session (prompts per
      phase, 3s holds, median/p90 stats) → `calibration/nate-webcam.json`,
      supersedes photo profile. Verify: channels normalized 0–1 across full sweep;
      repeat run produces stable ranges (±10%).

### Checkpoint A — the instrument works on camera (no Ableton yet)

### Phase 3: Ableton I/O
- [ ] T3: Virtual MIDI source "Bass Face" (rtmidi), channels → CC 20–23,
      throttled ~60 Hz. Verify: Live 12 MIDI prefs sees "Bass Face"; MIDI-map a
      macro; move face, knob moves.
- [ ] T4: OSC sender `/bassface/<channel>` → 127.0.0.1:7400.
      Verify: `oscdump`-style monitor or the M4L device in T5.

### Checkpoint B — face moves a knob in Live 12 (MIDI path). "Works in Ableton
immediately" achieved before the device exists.

### Phase 4: M4L mapper device
- [ ] T5: `m4l/BassFace.maxpat` — udpreceive 7400 → route → 4 channel strips
      (live.dial + Map button → live.remote~ binding, Expression Control pattern).
      Delivery: Max "New From Clipboard" → save as .amxd into User Library.
      Verify: map ott_brow → OTT depth on a real chain; all 4 map/unmap clean;
      device survives Live restart + set reload.

### Checkpoint C — full product path works end-to-end. Latency feel test on camera:
face → sound audibly < ~50ms or tune.

### Phase 5: Feel pass
- [ ] T6: Curve shaping (per-channel gamma), ratchet release timing, smoothing
      cutoffs — all in a config block, tuned live on camera with Nate.

- [ ] T7: Occlusion resilience — eye-patch luminance heuristic, per-channel health
      monitor (flatlined channel while others move = dead), fallback map
      (ott_brow → head pitch, phase_squint → cheekSquint, else disable + flag).
      Verify: on-camera test wearing sunglasses — OTT still controllable via head
      pitch, no channel emits garbage.

### Phase 6: Ship (separate session)
- [ ] PyInstaller .app bundle, first-run camera-permission UX, Patreon packaging,
      demo video capture. Windows/FL (MIDI-only) = v2.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| MediaPipe live latency too high | High | Checkpoint B measures early; fallback = smaller model, lower res, Apple Vision v2 |
| .amxd authoring friction | Med | Deliver maxpat via New From Clipboard; hand-save once in bundled Max |
| Terminal camera permission | Low | macOS prompts once for Ghostty; documented in run instructions |
| Ratchet feels wrong live | Med | T6 feel pass; release timing configurable |

## Open Questions

- None blocking. (Live 12 Suite + M4L presence verified on disk.)
