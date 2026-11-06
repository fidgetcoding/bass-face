# AGENTS.md

There's no hosted copy. Bass Face is a Python tracker (`tracker/`) plus a Max for Live device built from `m4l/`, and it runs on its owner's Mac next to Ableton Live 12.

To explain or evaluate this project, read ESSENCE.md, then EVOLUTION.md, then the code: `tracker/core.py` (the engine and the main loop; every tuning value sits in `CONFIG` at the top), `tracker/calibrate.py`, `tracker/outputs.py` and `m4l/generate_device.py`.

To set it up, follow README.md, which has a paste block written for agents. What the tracker and device touch is in SECURITY.md.

Setting it up on someone's Mac:

- Python 3.12, a venv at `.venv` in the repo, `pip install -r requirements.txt`. The device runs the tracker with `<repo>/.venv/bin/python`, from `~/code/bass-face` or the path written in `~/.bassface`.
- Don't run `tracker/core.py` yourself. It turns on their camera, and with no `calibration/profile.json` it starts a calibration that needs their face in front of it. Give them the command.
- Building the device and naming the four macros happen in Live and Max, by hand. Walk them through the README; don't script it.

Working on it:

- Tests: `.venv/bin/python tests/test_engine.py` (19 tests, no camera, synthetic blendshapes against `calibration/nate-v1.json`) and `.venv/bin/python tests/test_outputs.py` (3 tests; it opens a virtual MIDI port and binds UDP 7400, so it fails while Live has the device loaded). Run both after any change.
- Engine changes never touch the device. Restart the tracker to pick them up.
- The device patch is generated. Edit `m4l/generate_device.py` and run `python3 m4l/generate_device.py` to rewrite `m4l/BassFace-map.maxpat`. Don't hand-edit the `.maxpat`. Two Max traps that bit during the build: in a message box `$1` is replaced and `\$1` is literal text, and `trigger` with `l` strips the message selector (use `a`).
- Feel changes go in `CONFIG`, each with an engine test that feeds made-up face data through `Engine.update`.
- For timing bugs, run with `--debug` and read `debug.log` (per-frame CSV) before theorising. Every blind fix of the release stall missed.
- `calibration/profile.json` and `debug.log` are personal and gitignored. Never commit them. The photos in `calibration/photos/` are public on purpose.
- Don't stop the tracker with `pkill` while someone is playing. The device's CAM toggle is how they stop it.
