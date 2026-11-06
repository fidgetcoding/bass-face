# bass-face: how it got here

Commit hashes are from this repo. "Private note" means a dated record I keep offline: the idea note from May and my notes from the build session. Times are US Eastern (UTC-4), straight from the git log; that's where I was when I built it. My own words are quoted only where my notes kept them.

## 1. The short version

I wrote the idea down on May 4, 2026 and built the whole thing on July 19, 2026, from 2:50 pm to 11:40 pm, with a World Cup break in the middle. 46 commits.

It started as five phone photos of my face and a plan. By late afternoon a Python tracker read my face and sent MIDI and OSC. The evening went to making it feel right: locks on the way up, a drain on the way down, and a camera picker that stopped grabbing my phone. Then the Live device, which went through three ways of finding its knobs before it settled on names. The worst bug of the night was the sound hanging on after a long bass face. It took six or more tries and only died once I logged real numbers. The last commit made the device start its own camera.

## 2. Origin

The idea came in as content idea #23. My dictation spelled it "base face emulator."

The note from May 4 (private note) pitched a plugin that watches the producer's webcam and maps eyebrow raise, mouth open and the bass face scrunch onto a distortion or OTT style processor. The point of it: producers already make this face without meaning to, so the plugin just closes the loop. It also set the bar that mattered most: webcam to knob had to stay under 50 ms, or the joke dies.

## 3. Timeline

All on 2026-07-19.

| Time | What happened | Evidence |
|---|---|---|
| 14:50 | Photos, photo analysis, plan | `88cec34` |
| 14:52 | Starting calibration from the photos | `2d74691` |
| 14:59 | Engine with the ladder, guided calibration | `368f3ab` |
| 15:58 | Virtual MIDI source and OSC sender | `41640ef` |
| 15:59 | First Max for Live patch | `4c36224` |
| 18:46 to 19:17 | Camera picking, preview window, one shared window | `194437e` to `d093864` |
| 18:59 | Calibration becomes a first-run gate with sweeps; head-shake unlock | `2f26dad` |
| 19:26 to 19:27 | 90% headroom, calibration sounds | `6c8dd96`, `69be280` |
| 19:31 | Checkpoint A: works on camera | `ed2f4d1` |
| 19:40 to 19:59 | Feel: cascade, slower ramp, drain, blink debounce, stuck fix | `435fdda` to `24be410` |
| 20:03 | Solo keys for MIDI mapping | `9dcd470` |
| 20:08 | Checkpoint B: my face moves an OTT knob in Live | `d078792` |
| 20:41 | Cascade only from the full bass face | `9729791` |
| 20:56 to 21:03 | Patch shipped as a file; Checkpoint C | `c0fe883`, `2261327` |
| 21:08 to 21:37 | v1.1: Map buttons, verified | `19579c7`, `6dbbb2c` |
| 21:46 to 21:56 | v1.2: saved paths, never captured | `cb554f0`, `954b775` |
| 22:04 to 22:21 | v1.3: wire by name, verified, survives a fresh set | `70d2341` to `ffe06e9` |
| 22:26 to 22:54 | The release stall: debug log, three fixes, verified | `4180d12` to `99f944b` |
| 23:01 to 23:20 | v1.4: clean device face, direct device writes | `56c59ec`, `6e6c451` |
| 23:40 | v1.5: the device starts its own camera | `ec872c8` |

## 4. Round by round

**Round 1: photos and a plan (14:50 to 14:59).**
Built: five phone photos of my face, one per phase (neutral, eyebrows raised, eyes closed, mouth open, bass face), run through MediaPipe to get a starting calibration, then the engine and a guided calibration.
Decided before any code: it's a controller. Bass Face moves knobs, and you keep your own OTT and distortion.
Found: the obvious blendshapes for a disgust face, the nose sneer and cheek squint, read 0.000 on my face in every photo. My own note on the bass face photo was that my "eyebrows compress in," and the numbers agreed: brows pulled down read 0.50 on the bass face and 0.02 with my eyes just closed. FACE FILTH has watched the brows ever since.

**Round 2: into Live (15:58 to 15:59).**
Built: a virtual MIDI source called "Bass Face" on CC 20 to 23, an OSC sender to 127.0.0.1:7400, and a first Max for Live patch with four automatable face lanes, delivered by pasting into Max.
Then a World Cup break.

**Round 3: the camera (18:46 to 19:17).**
Broke: the tracker kept opening the wrong camera, usually my iPhone through Continuity Camera.
Tried: three ways of guessing the right one, plus remembering the pick between launches (`6656e96`). All wrong.
Fixed: I read OpenCV's own source. It sorts cameras by an internal ID string, an order no other API shows you, and the iPhone joining or leaving reshuffles every index. So the tracker now copies that sort exactly and picks the Mac's built-in camera by type, shows a "THIS CAMERA?" screen first, and lets `c` cycle. It never saves a camera index anymore.
Also built: one window for the camera check, calibration and tracking, with my face mesh and four bars drawn on it.

**Round 4: calibration as a gate (18:59 to 19:31).**
The plan said hold each face for 3 seconds. What shipped is a sweep per face, from neutral to your max, with the max taken from the top of the sweep. It runs before anything else on first launch. Full scale moved to 90% of the calibrated max, since the true max is hard to hit again mid-song (`6c8dd96`). Then sounds, so I could calibrate without reading the terminal: Tink counts down, Pop captures, Glass got it, Hero done (`69be280`).
Tested: Checkpoint A, on camera (`ed2f4d1`).

**Round 5: feel (19:40 to 20:08).**
Built: reaching a stage ramps every stage below it to full (`435fdda`). The ramp felt too fast at 150 ms, so it went to 400 ms (`ce7dc92`). Releases got the same slope on the way down instead of snapping (`d8711af`).
Broke: the cascade kept refilling the drain while it was draining (`37f4db6`). Blinks spiked the squint channel and blocked releases, so changes now have to last 150 ms to count (`91d3155`). The face sometimes got stuck reading not-quite-neutral, fixed by only learning the resting floor while the face is at rest (`24be410`).
Broke in Live: with all four faces streaming at once, MIDI Map Mode grabbed whichever CC moved first. Fixed with solo keys 1 to 4 (`9dcd470`).
Tested: Checkpoint B. My eyebrows moved an OTT knob in Live 12 over CC 20 (`d078792`).

**Round 6: only the bass face cascades (20:41 to 20:45).**
Broke: opening my mouth dragged the OTT up with it, because every stage was filling the ones below.
Fixed: only the full bass face fills the lower stages. The middle ones lock whatever peak they really hit (`9729791`). Plus a second escape for a resting face that drifts far, and a loud terminal warning when a solo key is on (`be5bee8`).

**Round 7: the device (20:56 to 21:03).**
Broke: pasting patches into Max from the clipboard was unreliable.
Fixed: the patch ships as a `.maxpat` file you open with File → Open (`c0fe883`).
Tested: Checkpoint C. `BassFace.amxd` loaded in Live, its dials followed my face over OSC, and its lanes recorded automation (`2261327`).

**Round 8: knobs that stay wired (21:08 to 22:21).**
v1.1: a Map button per face. Click Map, click a knob, done. All four drove my rack's macros (`6dbbb2c`), until I reloaded the set. The buttons stored Live's internal IDs, and Live renumbers everything on every load.
v1.2: save each parameter's path and look it up again on load. It never captured a single path. The observer that should have reported the clicked knob stayed silent, and Max's `trigger` was stripping the `id` off every message (`954b775`).
v1.3: forget clicking. The device walks every device on its track and one level into rack chains, and wires any parameter named exactly BROW OTT, MOUTH DRIVE, SQUINT PHASE or FACE FILTH (`70d2341`). One more Max trap on the way: a `\$1` in a message box is literal text, and only `$1` gets replaced (`9ad8093`).
Tested: wired live (`fb787f4`), then the real test: a brand new set from my template. The macros followed my face with zero setup (`ffe06e9`).

**Round 9: the release stall (22:26 to 22:54).**
Broke: after a long bass face, the sound hung on for 1 to 4 seconds after my face went neutral.
Tried: six or more fixes on theory, blaming the solo keys, then the floors. Every blind fix missed.
Measured: `--debug`, which logs every frame's engine state to a CSV (`4180d12`). It showed a short bass face released fine. A 20-second hold left leftover muscle tension that fluttered the channels between 0.1 and 0.45: above the release line, below the escape gates, forever. Worse, the design itself staggered. FACE FILTH followed my face live while the locked channels waited on timers.
Fixed: a design change more than a tune. When the top face falls hard (from above 0.6 to under 0.25), that fall is the release, and everything drains right away (`158c571`). The locked channels follow the top one down, so all four hit zero together, with no timers in anything you can hear (`a7bb892`). A 2.5-second warmup at launch stops a stale floor from firing a phantom phrase. And the resting floor only learns upward while a channel is quiet, because riding my eyebrows on their own was getting eaten (`11d5f9d`).
Tested: "fairly smooth," live (`99f944b`).

**Round 10: a clean face, and no more pasting (23:01 to 23:20).**
Built: presentation mode. The device shows a BASS FACE title, four dials and a rescan button (`56c59ec`).
Broke, nearly for good: in Max's presentation view, ⌘A only selects what's on the device face. I copied that and pasted a gutted shell over the working device, partly. It came back because the `.amxd` on disk still had everything.
Fixed, for good: I worked out the `.amxd` file format (a small `ampf` header, then a `ptch` chunk with its size, then the patch itself). From then on device updates got written straight to disk and I just dragged the device in again. The copy-paste dance was over (`6e6c451`).

**Round 11: the device starts its own camera (23:40).**
Built: a Node for Max script inside the device starts `tracker/core.py --autostart` when the device loads and stops it when the device goes away or Live quits. It checks for a tracker that's already running before it starts another. A CAM toggle on the device face stops and starts it and shows the real state. The new `--autostart` flag skips the camera check screen (`ec872c8`).
Learned: the first auto-launch makes macOS ask whether Ableton Live can use the camera, since the tracker runs as Live's child.
Broke: the same `\$1` trap from Round 8, a second time. The generator got fixed.
Tested: my notes from that night say the camera came on when the device loaded and my face played the rack. This one has no separate "verified" commit like the earlier versions got.

## 5. Feature family tree

```
"base face emulator" (May idea): webcam bolted to a distortion plugin
└─ a controller instead: face → any knob in Live
   ├─ photos → starting calibration → FACE FILTH reads the brows
   ├─ tracker: MediaPipe → 4 channels → MIDI CC 20-23 + OSC 7400
   │  ├─ camera picker → copy OpenCV's sort → "THIS CAMERA?" screen
   │  ├─ calibration gate → sweeps → 90% headroom → sounds
   │  └─ the ladder
   │     ├─ locks on the way up → cascade only from the full bass face
   │     ├─ drain on the way down → blink debounce → stuck escapes
   │     └─ release stall → --debug CSV → fall = release, all four follow
   └─ the device
      ├─ pasted patch → .maxpat file → automation lanes
      ├─ Map buttons (lost on reload) → saved paths (never captured)
      │  └─ wire by name → survives a fresh set
      ├─ clean device face → direct .amxd writes
      └─ starts its own camera
```

## 6. Test log

| When | What | Result | Where |
|---|---|---|---|
| Jul 19 14:52 | My 5 photos through MediaPipe | Sneer and cheek 0.000; brows down 0.50 vs 0.02 | `2d74691`, `calibration/nate-v1.json` |
| Jul 19 19:31 | Checkpoint A: tracker and calibration on camera | Passed | `ed2f4d1` |
| Jul 19 20:08 | Checkpoint B: eyebrows on an OTT knob in Live 12, CC 20 | Passed | `d078792` |
| Jul 19 21:03 | Checkpoint C: device dials follow over OSC, lanes record | Passed | `2261327` |
| Jul 19 21:37 | v1.1 Map buttons drive all four macros | Passed, lost on reload | `6dbbb2c` |
| Jul 19 22:18 | v1.3 wire by name | Passed | `fb787f4` |
| Jul 19 22:21 | Fresh set from my template | Macros follow my face, zero setup | `ffe06e9` |
| Jul 19 22:54 | Release after long holds | "fairly smooth," no stall | `99f944b` |
| Jul 19 23:20 | v1.4 clean device face | Verified | `6e6c451` |
| Nov 6 | 19 engine tests, 3 output tests (macOS 26, Python 3.12.13) | All 22 pass | `tests/` |

Trap to remember: every blind fix for the release stall missed, and both real fixes came minutes after reading `debug.log`. If it feels wrong, log it before guessing.

## 7. Roads not taken

- **A distortion plugin.** That was the May idea. A controller lets people keep the OTT and distortion they already love.
- **Apple's Vision framework.** The May note listed it next to MediaPipe. MediaPipe did the job, so Vision stayed a backup plan.
- **TouchDesigner.** People do build face-to-music rigs with it. I cut it from the plan: good for a prototype, wrong for something other people install.
- **Nose sneer for the bass face.** It read zero on my face. Brows pulled down took its place.
- **Holding each face for 3 seconds** to calibrate. Sweeps from neutral to max replaced it.
- **Remembering the camera.** Indices change whenever a phone joins, so a saved one picks the wrong camera.
- **Map buttons and saved paths.** One forgot everything on reload; the other never saved anything. Names won.
- **Release timers.** Waiting for a confirmed neutral face is what made the sound hang on. The fall of the top face is the release now.
- **Pasting into Max.** Replaced by a `.maxpat` file, then by writing the `.amxd` directly.

## 8. What's next

- A feel pass on the curves and smoothing.
- The sunglasses fallback: move the OTT with head tilt when the brows can't be read.
- An app you can download, so there's no Python setup, plus the device and rack in this repo.
- Secret hand gestures: hand to nose for random LFO chaos on everything, hands on head for a reverb freeze. Both need MediaPipe's hand tracker added.
- Windows and FL Studio through the MIDI route.
- Calibration that's been tried on faces other than mine.

## 9. Sources

- Commits: `git log` of `fidgetcoding/bass-face`.
- [README.md](README.md), [SECURITY.md](SECURITY.md), `tasks/plan.md` and `tasks/todo.md` in this repo.
- Private, kept by me: the idea note dated May 4, 2026, and the build session notes dated July 19, 2026.

## 2026-11-06: getting ready to go public

Added the public docs: this file, the README, ESSENCE, SECURITY, AGENTS and the license. The five photos of my face stay in the repo on purpose; they're how it started, and the bass face one is in the README. `requirements.txt` pins the versions I run, since a fresh unpinned install now pulls a newer MediaPipe I haven't tested. The device's launcher used to point at my own folder; now it looks in `~/code/bass-face`, or wherever `~/.bassface` points.

Then I put the device itself in the repo: `device/BassFace.amxd` and `device/BASS FACE RACK.adg` are copies of the exact files in my User Library, so nobody has to rebuild the device by hand.

Checked: all 22 tests pass on macOS 26 with Python 3.12.13.
