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
    "BASS FACE v1.2 - Map: arm, click any Live knob (mapping survives "
    "reload). X: unmap. Run tracker/core.py.")
udp = box("newobj", 30, 40, 110, 22, "udpreceive 7400", numin=0, numout=1,
          outlettype=[""])
route = box("newobj", 30, 72, 620, 22,
            "route /bassface/ott_brow /bassface/drive_mouth "
            "/bassface/phase_squint /bassface/filth_disgust",
            numin=1, numout=5, outlettype=["", "", "", "", ""])
wire(udp, 0, route, 0)

lb = box("newobj", 700, 40, 60, 22, "loadbang", numin=0, numout=1,
         outlettype=["bang"])
tsh = box("newobj", 700, 70, 50, 22, "t b b", numin=1, numout=2,
          outlettype=["bang", "bang"])
mpath = box("message", 760, 100, 120, 22, "path live_set view",
            numin=2, numout=1, outlettype=[""])
mprop = box("message", 700, 130, 170, 22, "property selected_parameter",
            numin=2, numout=1, outlettype=[""])
lpath = box("newobj", 760, 160, 70, 22, "live.path", numin=1, numout=3,
            outlettype=["", "", ""])
lobs = box("newobj", 700, 190, 90, 22, "live.observer", numin=2, numout=2,
           outlettype=["", ""])
ssel = box("newobj", 700, 220, 80, 22, "s ---selp", numin=1, numout=0)
robsb = box("newobj", 800, 190, 90, 22, "r ---obsbang", numin=0, numout=1,
            outlettype=[""])
wire(lb, 0, tsh, 0)
wire(tsh, 1, mpath, 0)
wire(tsh, 0, mprop, 0)
wire(mpath, 0, lpath, 0)
wire(lpath, 0, lobs, 1)
wire(mprop, 0, lobs, 0)
wire(lobs, 0, ssel, 0)
wire(robsb, 0, lobs, 0)

# ---- per-slot mapping subsystem ----
for i, (chan, short) in enumerate(zip(CHANNELS, SHORT)):
    x = 30 + i * 235
    box("comment", x, 120, 100, 20, short)
    tog = box("toggle", x, 145, 24, 24, numin=1, numout=1, outlettype=["int"])
    box("comment", x + 28, 148, 36, 20, "Map")
    selarm = box("newobj", x + 66, 145, 40, 22, "sel 1", numin=2, numout=2,
                 outlettype=["bang", ""])
    sobsb = box("newobj", x + 66, 175, 90, 22, "s ---obsbang",
                numin=1, numout=0)
    btn = box("button", x + 160, 145, 24, 24, numin=1, numout=1,
              outlettype=["bang"])
    box("comment", x + 186, 148, 46, 20, "unmap")
    tclr = box("newobj", x + 160, 175, 50, 22, "t b b", numin=1, numout=2,
               outlettype=["bang", "bang"])
    mid0 = box("message", x + 120, 205, 36, 22, "id 0", numin=2, numout=1,
               outlettype=[""])
    mnone = box("message", x + 165, 205, 40, 22, "none", numin=2, numout=1,
                outlettype=[""])
    rsel = box("newobj", x, 205, 70, 22, "r ---selp", numin=0, numout=1,
               outlettype=[""])
    gat = box("newobj", x, 235, 50, 22, "gate", numin=2, numout=1,
              outlettype=[""])
    dfl = box("newobj", x, 265, 60, 22, "deferlow", numin=1, numout=1,
              outlettype=[""])
    rid = box("newobj", x, 295, 60, 22, "route id", numin=1, numout=2,
              outlettype=["", ""])
    snz = box("newobj", x, 325, 40, 22, "sel 0", numin=2, numout=2,
              outlettype=["bang", ""])
    pre = box("newobj", x, 355, 70, 22, "prepend id", numin=1, numout=1,
              outlettype=[""])
    trgC = box("newobj", x, 385, 60, 22, "t b b a", numin=1, numout=3,
               outlettype=["bang", "bang", ""])
    mgp = box("message", x + 70, 415, 55, 22, "getpath", numin=2, numout=1,
              outlettype=[""])
    mdis = box("message", x + 135, 415, 24, 22, "0", numin=2, numout=1,
               outlettype=[""])
    lobj = box("newobj", x, 445, 80, 22, "live.object", numin=2, numout=1,
               outlettype=[""])
    rpm = box("newobj", x, 475, 130, 22, "route path min max", numin=1,
              numout=4, outlettype=["", "", "", ""])
    prep2 = box("newobj", x, 505, 90, 22, "prepend path", numin=1, numout=1,
                outlettype=[""])
    pat = box("newobj", x, 535, 170, 22,
              f"pattr map_{chan} @autorestore 1", numin=1, numout=3,
              outlettype=["", "", ""])
    rnone = box("newobj", x, 565, 75, 22, "route none", numin=1, numout=2,
                outlettype=["", ""])
    lpth = box("newobj", x, 595, 70, 22, "live.path", numin=1, numout=3,
               outlettype=["", "", ""])
    rid2 = box("newobj", x, 625, 60, 22, "route id", numin=1, numout=2,
               outlettype=["", ""])
    pre2 = box("newobj", x, 655, 70, 22, "prepend id", numin=1, numout=1,
               outlettype=[""])
    trgR = box("newobj", x, 685, 60, 22, "t b a a", numin=1, numout=3,
               outlettype=["bang", "", ""])
    mgmm = box("message", x + 70, 715, 100, 22, "get min, get max",
               numin=2, numout=1, outlettype=[""])
    scl = box("newobj", x, 745, 110, 22, "scale 0. 1. 0. 1.", numin=5,
              numout=1, outlettype=[""])
    lrm = box("newobj", x, 775, 90, 22, "live.remote~", numin=2, numout=0)
    dial = box("live.dial", x, 810, 48, 48, extra={
        "varname": chan, "parameter_enable": 1,
        "saved_attribute_attributes": {"valueof": {
            "parameter_longname": short, "parameter_shortname": short,
            "parameter_type": 0, "parameter_mmin": 0.0,
            "parameter_mmax": 1.0, "parameter_unitstyle": 1}}},
        numin=1, numout=2, outlettype=["", "float"])

    # arm / capture -> store PATH
    wire(tog, 0, gat, 0)
    wire(tog, 0, selarm, 0)
    wire(selarm, 0, sobsb, 0)
    wire(rsel, 0, gat, 1)
    wire(gat, 0, dfl, 0)
    wire(dfl, 0, rid, 0)
    wire(rid, 0, snz, 0)
    wire(snz, 1, pre, 0)
    wire(pre, 0, trgC, 0)
    wire(trgC, 2, lobj, 1)   # bind captured id
    wire(trgC, 1, mgp, 0)    # ask for its canonical path
    wire(trgC, 0, mdis, 0)   # disarm toggle (closes gate)
    wire(mgp, 0, lobj, 0)
    wire(mdis, 0, tog, 0)
    wire(lobj, 0, rpm, 0)
    wire(rpm, 0, prep2, 0)   # "path ..." -> persist
    wire(prep2, 0, pat, 0)
    wire(rpm, 1, scl, 3)     # min -> out-lo
    wire(rpm, 2, scl, 4)     # max -> out-hi
    # resolve (fires on capture AND on set load via autorestore)
    wire(pat, 0, rnone, 0)
    wire(rnone, 1, lpth, 0)  # stored "path ..." -> fresh id this session
    wire(lpth, 0, rid2, 0)
    wire(rid2, 0, pre2, 0)
    wire(pre2, 0, trgR, 0)
    wire(trgR, 2, lobj, 1)   # re-bind
    wire(trgR, 1, lrm, 1)    # take control
    wire(trgR, 0, mgmm, 0)   # query range (fires last)
    wire(mgmm, 0, lobj, 0)
    # face value -> dial (lane) + scaled remote
    wire(route, i, dial, 0)
    wire(route, i, scl, 0)
    wire(scl, 0, lrm, 0)
    # unmap: release now + persist "none"
    wire(btn, 0, tclr, 0)
    wire(tclr, 1, mid0, 0)
    wire(tclr, 0, mnone, 0)
    wire(mid0, 0, lrm, 1)
    wire(mnone, 0, pat, 0)

# ---- audio passthrough ----
plug = box("newobj", 700, 775, 70, 22, "plugin~", numin=1, numout=2,
           outlettype=["signal", "signal"])
plout = box("newobj", 700, 815, 70, 22, "plugout~", numin=2, numout=2,
            outlettype=["signal", "signal"])
wire(plug, 0, plout, 0)
wire(plug, 1, plout, 1)

doc = {"patcher": {
    "fileversion": 1,
    "appversion": {"major": 9, "minor": 0, "revision": 0,
                   "architecture": "x64", "modernui": 1},
    "classnamespace": "box",
    "rect": [80.0, 80.0, 1010.0, 920.0],
    "boxes": boxes,
    "lines": lines,
}}

out = Path(__file__).parent / "BassFace-map.maxpat"
out.write_text(json.dumps(doc, indent=1))
print(f"wrote {out} ({len(boxes)} boxes, {len(lines)} lines)")
