"""Generate BassFace-map.maxpat - v1.2 device with PERSISTENT Map buttons.

v1.1 stored raw Live ids, which are session-only (Live re-numbers every
object on set load), so mappings died with the session. v1.2 persists the
parameter's canonical PATH (queried via live.object getpath at capture) and
re-resolves it through live.path on every load - the way commercial M4L
mappers survive reloads.

Per slot: Map toggle arms capture -> selected_parameter id -> bind
live.object -> getpath -> pattr stores "path ..." -> live.path resolves to
a fresh id -> live.remote~ takes control with live.object min/max range
scaling. X unmaps (releases remote, stores "none").

Run: python3 m4l/generate_device.py   -> writes m4l/BassFace-map.maxpat
"""

import json
from pathlib import Path

CHANNELS = ["ott_brow", "drive_mouth", "phase_squint", "filth_disgust"]
SHORT = ["OTT", "Drive", "Phase", "Filth"]

boxes = []
lines = []
_id = 0


def box(maxclass, x, y, w, h, text=None, extra=None, numin=0, numout=0,
        outlettype=None):
    global _id
    _id += 1
    oid = f"obj-{_id}"
    b = {"id": oid, "maxclass": maxclass, "numinlets": numin,
         "numoutlets": numout, "patching_rect": [float(x), float(y),
                                                 float(w), float(h)]}
    if text is not None:
        b["text"] = text
    if numout and outlettype is not None:
        b["outlettype"] = outlettype
    if extra:
        b.update(extra)
    boxes.append({"box": b})
    return oid


def wire(src, out, dst, inl):
    lines.append({"patchline": {"source": [src, out],
                                "destination": [dst, inl]}})


# ---- shared: OSC in + selected-parameter observer ----
box("comment", 30, 10, 700, 20,
    "BASS FACE v1.4 - auto-wires to macros named BROW OTT / MOUTH DRIVE / "
    "SQUINT PHASE / FACE FILTH on this track. Run tracker/core.py.")
box("comment", 0, 0, 90, 18, "BASS FACE",
    extra={"presentation": 1, "presentation_rect": [8.0, 4.0, 90.0, 18.0],
           "fontface": 1})
box("comment", 0, 0, 150, 15, "face -> your rack",
    extra={"presentation": 1, "presentation_rect": [8.0, 24.0, 150.0, 15.0],
           "fontsize": 9.0})
udp = box("newobj", 30, 40, 110, 22, "udpreceive 7400", numin=0, numout=1,
          outlettype=[""])
route = box("newobj", 30, 72, 620, 22,
            "route /bassface/ott_brow /bassface/drive_mouth "
            "/bassface/phase_squint /bassface/filth_disgust",
            numin=1, numout=5, outlettype=["", "", "", "", ""])
wire(udp, 0, route, 0)

ltd = box("newobj", 700, 40, 100, 22, "live.thisdevice", numin=1, numout=3,
          outlettype=["bang", "", ""])
mjs = box("newobj", 700, 72, 130, 22, "js bassface_map.js", numin=1, numout=1,
          outlettype=[""])
rescan = box("button", 840, 40, 24, 24, numin=1, numout=1,
             outlettype=["bang"],
             extra={"presentation": 1,
                    "presentation_rect": [258.0, 96.0, 20.0, 20.0]})
box("comment", 866, 43, 50, 20, "rescan",
    extra={"presentation": 1,
           "presentation_rect": [240.0, 118.0, 56.0, 15.0], "fontsize": 9.0})
rt4 = box("newobj", 700, 104, 90, 22, "route 0 1 2 3", numin=1, numout=5,
          outlettype=["", "", "", "", ""])
wire(ltd, 0, mjs, 0)
wire(rescan, 0, mjs, 0)
wire(mjs, 0, rt4, 0)

# ---- per-slot: unpack id/min/max -> remote, face -> scale -> remote ----
for i, (chan, short) in enumerate(zip(CHANNELS, SHORT)):
    x = 30 + i * 235
    box("comment", x, 120, 100, 20, short)
    unp = box("newobj", x, 150, 90, 22, "unpack 0 0. 0.", numin=1, numout=3,
              outlettype=["int", "float", "float"])
    mid = box("message", x, 185, 50, 22, "id $1", numin=2, numout=1,
              outlettype=[""])
    scl = box("newobj", x, 220, 110, 22, "scale 0. 1. 0. 1.", numin=5,
              numout=1, outlettype=[""])
    lrm = box("newobj", x, 255, 90, 22, "live.remote~", numin=2, numout=0)
    dial = box("live.dial", x, 300, 48, 48, extra={
        "presentation": 1,
        "presentation_rect": [10.0 + i * 58, 48.0 + 0 * 1, 48.0, 60.0],
        "varname": chan, "parameter_enable": 1,
        "saved_attribute_attributes": {"valueof": {
            "parameter_longname": short, "parameter_shortname": short,
            "parameter_type": 0, "parameter_mmin": 0.0,
            "parameter_mmax": 1.0, "parameter_unitstyle": 1}}},
        numin=1, numout=2, outlettype=["", "float"])

    wire(rt4, i, unp, 0)
    wire(unp, 0, mid, 0)
    wire(unp, 1, scl, 3)
    wire(unp, 2, scl, 4)
    wire(mid, 0, lrm, 1)
    wire(route, i, dial, 0)
    wire(route, i, scl, 0)
    wire(scl, 0, lrm, 0)

# ---- audio passthrough ----
plug = box("newobj", 700, 255, 70, 22, "plugin~", numin=1, numout=2,
           outlettype=["signal", "signal"])
plout = box("newobj", 700, 295, 70, 22, "plugout~", numin=2, numout=2,
            outlettype=["signal", "signal"])
wire(plug, 0, plout, 0)
wire(plug, 1, plout, 1)

doc = {"patcher": {
    "fileversion": 1,
    "openinpresentation": 1,
    "appversion": {"major": 9, "minor": 0, "revision": 0,
                   "architecture": "x64", "modernui": 1},
    "classnamespace": "box",
    "rect": [80.0, 80.0, 1010.0, 420.0],
    "boxes": boxes,
    "lines": lines,
}}

out = Path(__file__).parent / "BassFace-map.maxpat"
out.write_text(json.dumps(doc, indent=1))
print(f"wrote {out} ({len(boxes)} boxes, {len(lines)} lines)")
