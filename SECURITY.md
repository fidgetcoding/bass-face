# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest (`main`) | Yes |

## Reporting a Vulnerability

If you find a security problem, please report it privately:

1. **Don't open a public GitHub issue.**
2. Use GitHub's private reporting: the repo's **Security** tab → **Report a vulnerability**. Only the maintainer sees it.
3. Include what you found, how to reproduce it, and what it could affect.
4. You'll hear back within 48 hours.

## What Bass Face touches

**Your camera.** The tracker reads webcam frames at 640×480 and hands each one to MediaPipe's face model, which runs on your Mac from `models/face_landmarker.task`. Frames are shown in the preview window and then dropped. Bass Face never saves a frame and never sends one anywhere. macOS asks for camera permission for your terminal app, or for Ableton Live when the device starts the tracker.

**The network.** Bass Face's own code sends exactly one thing: OSC over UDP to `127.0.0.1:7400`, which is your own Mac. Nothing goes to the internet.

**MIDI.** It opens a virtual MIDI source named "Bass Face" that sends CC 20 to 23. Any app on your Mac can listen to it.

**Files it writes,** both gitignored:

- `calibration/profile.json`: your resting and max values for the four channels. Numbers only, no images.
- `debug.log`: only with `--debug`. One row of engine numbers per frame, no images.

**What it runs.** Calibration plays macOS system sounds with `afplay`. In Live, the device's launcher (Node for Max) reads `~/.bassface` for the repo path (default `~/code/bass-face`), checks for a running tracker with `pgrep`, starts `.venv/bin/python tracker/core.py --autostart` from that folder, and stops it with a signal or `pkill -f tracker/core.py` when you switch CAM off. Whatever Python sits at that path runs with Live's permissions, camera included, so keep `~/.bassface` pointing at your real clone.

**The Live device** reads parameter names on its own track (and one level into rack chains) through the Live API, and drives the four it matches by name. It doesn't touch other tracks.

**The photos** in `calibration/photos/` are my own face, published on purpose.

## Scope

- `tracker/`, `m4l/` and `tests/`
- The install commands in `README.md`
