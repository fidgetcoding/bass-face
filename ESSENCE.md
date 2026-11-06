# bass-face: the essence

**What it is.** A face-tracking controller for Ableton Live 12. A small Python program watches your webcam with MediaPipe and turns four faces (eyebrows up, mouth open, squint, full bass face) into four channels. It streams them as a virtual MIDI source called "Bass Face" (CC 20 to 23) and as OSC to a Max for Live device, which finds four macros named BROW OTT, MOUTH DRIVE, SQUINT PHASE and FACE FILTH on its track and drives them. It makes no sound itself. Your rack does.

**Who it's for.** People who make bass music in Ableton on a Mac and pull the face anyway. You need a webcam, Live 12 (Suite for the device, any edition for the MIDI route) and a willingness to set up Python 3.12.

**Why it exists.** I make this face every time a bass line lands right. In May I wrote down the idea that the face should do something, and on July 19, 2026 I built it in one sitting with Claude Code.

**What's different.**

- The four faces are a ladder. Each step locks the ones below it at their peak, so squinting can't drag your eyebrows' OTT back down mid-build. Only the full bass face slams everything below it to 100%.
- The way down is one gesture. When the top face falls, all four channels drain together and hit zero the moment your face does. A head shake unlocks everything on the spot.
- It wires itself by name. Name four macros and the device finds them on every load, so it survives set reloads with no mapping.
- The device starts and stops its own camera tracker.
- Calibration is a 30-second guided session on camera, with sounds, and the profile stays on your Mac.
- Everything runs locally. The only thing it sends is OSC to your own machine.

**How to try it.** Clone the repo, make a Python 3.12 venv, `pip install -r requirements.txt`, and run `tracker/core.py`. Then either MIDI-map CC 20 to 23 in Live, or build the device from `m4l/BassFace-map.maxpat` and name four macros. The [README](README.md) has every step, plus a block to paste to your own agent. [SECURITY.md](SECURITY.md) lists what it touches.

**What works today.** All of this is from my own Mac, and [EVOLUTION.md](EVOLUTION.md) says where each piece came from.

- It went from first commit to auto-launching device in 46 commits on July 19, 2026, between 2:50 pm and 11:40 pm Eastern.
- Every checkpoint that night passed live: tracker and calibration on camera, my eyebrows moving an OTT knob in Live 12 over MIDI, the device's dials recording automation, auto-wire by name, and a brand new set from my template following my face with zero setup.
- The release stall (sound hanging on for 1 to 4 seconds after a long hold) is fixed and played smooth live.
- 19 engine tests and 3 output tests pass, checked again on November 6, 2026, on macOS 26 with Python 3.12.13.
- I've only calibrated my own face. There's no app yet: the Python side is set up by hand, and the device and my rack are files you copy into Live.
