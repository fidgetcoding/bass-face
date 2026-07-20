"""Generate BassFace-map.maxpat - v1.1 device with per-slot Map buttons.

Per slot: Map toggle arms capture; clicking any Live parameter routes its id
(via shared live.observer on selected_parameter) into live.remote~, with
min/max queried through live.object feeding a scale. pattr @autorestore
persists the mapping inside the device. X button unmaps (id 0).

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
title = box("comment", 30, 10, 640, 20,
            "BASS FACE v1.1 - Map: arm, click any Live knob. X: unmap. "
            "Run tracker/core.py.")
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
mprop = box("message", 700, 100, 170, 22, "property selected_parameter",
            numin=2, numout=1, outlettype=[""])
lpath = box("newobj", 760, 132, 70, 22, "live.path", numin=1, numout=3,
            outlettype=["", "", ""])
lobs = box("newobj", 700, 164, 90, 22, "live.observer", numin=2, numout=2,
           outlettype=["", ""])
ssel = box("newobj", 700, 196, 80, 22, "s ---selp", numin=1, numout=0)
robsb = box("newobj", 800, 164, 90, 22, "r ---obsbang", numin=0, numout=1,
            outlettype=[""])
wire(lb, 0, tsh, 0)
wire(tsh, 1, mpath, 0)      # right first: set path
wire(tsh, 0, mprop, 0)      # then property
wire(mpath, 0, lpath, 0)
wire(lpath, 0, lobs, 1)     # id of live_set view -> observer right inlet
wire(mprop, 0, lobs, 0)
wire(lobs, 0, ssel, 0)
wire(robsb, 0, lobs, 0)     # bang re-emits current selection on arm

# ---- per-slot mapping subsystem ----
for i, (chan, short) in enumerate(zip(CHANNELS, SHORT)):
    x = 30 + i * 235
    lbl = box("comment", x, 120, 100, 20, short)
    tog = box("toggle", x, 145, 24, 24, numin=1, numout=1, outlettype=["int"])
    lblm = box("comment", x + 28, 148, 40, 20, "Map")
    selarm = box("newobj", x + 70, 145, 40, 22, "sel 1", numin=2, numout=2,
                 outlettype=["bang", ""])
    sobsb = box("newobj", x + 70, 175, 90, 22, "s ---obsbang",
                numin=1, numout=0)
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
    pat = box("newobj", x, 385, 160, 22,
              f"pattr map_{chan} @autorestore 1", numin=1, numout=3,
              outlettype=["", "", ""])
    trg = box("newobj", x, 415, 80, 22, "t b b l l", numin=1, numout=4,
              outlettype=["bang", "bang", "", ""])
    mgmm = box("message", x + 95, 445, 100, 22, "get min, get max",
               numin=2, numout=1, outlettype=[""])
    lobj = box("newobj", x, 475, 80, 22, "live.object", numin=2, numout=1,
               outlettype=[""])
    rmm = box("newobj", x, 505, 90, 22, "route min max", numin=1, numout=3,
              outlettype=["", "", ""])
    scl = box("newobj", x, 535, 110, 22, "scale 0. 1. 0. 1.", numin=5,
              numout=1, outlettype=[""])
    lrm = box("newobj", x, 565, 90, 22, "live.remote~", numin=2, numout=0)
    mdis = box("message", x + 100, 415, 30, 22, "0", numin=2, numout=1,
               outlettype=[""])
    btn = box("button", x + 140, 145, 24, 24, numin=1, numout=1,
              outlettype=["bang"])
    lblx = box("comment", x + 168, 148, 50, 20, "unmap")
    mclr = box("message", x + 140, 175, 40, 22, "id 0", numin=2, numout=1,
               outlettype=[""])
    dial = box("live.dial", x, 605, 48, 48, extra={
        "varname": chan, "parameter_enable": 1,
        "saved_attribute_attributes": {"valueof": {
            "parameter_longname": short, "parameter_shortname": short,
            "parameter_type": 0, "parameter_mmin": 0.0,
            "parameter_mmax": 1.0, "parameter_unitstyle": 1}}},
        numin=1, numout=2, outlettype=["", "float"])

    # arm / capture
    wire(tog, 0, gat, 0)
    wire(tog, 0, selarm, 0)
    wire(selarm, 0, sobsb, 0)
    wire(rsel, 0, gat, 1)
    wire(gat, 0, dfl, 0)
    wire(dfl, 0, rid, 0)
    wire(rid, 0, snz, 0)
    wire(snz, 1, pre, 0)
    wire(pre, 0, pat, 0)
    # pattr re-emits (capture AND autorestore) -> bind chain
    wire(pat, 0, trg, 0)
    wire(trg, 3, lobj, 1)    # bind live.object
    wire(trg, 2, lrm, 1)     # take control
    wire(trg, 1, mgmm, 0)    # query range
    wire(trg, 0, mdis, 0)    # disarm toggle
    wire(mdis, 0, tog, 0)
    wire(mgmm, 0, lobj, 0)
    wire(lobj, 0, rmm, 0)
    wire(rmm, 0, scl, 3)     # min -> out-lo
    wire(rmm, 1, scl, 4)     # max -> out-hi
    # face value -> dial (lane) + scaled remote
    wire(route, i, dial, 0)
    wire(route, i, scl, 0)
    wire(scl, 0, lrm, 0)
    # unmap
    wire(btn, 0, mclr, 0)
    wire(mclr, 0, pat, 0)

# ---- audio passthrough ----
plug = box("newobj", 700, 605, 70, 22, "plugin~", numin=1, numout=2,
           outlettype=["signal", "signal"])
plout = box("newobj", 700, 645, 70, 22, "plugout~", numin=2, numout=2,
            outlettype=["signal", "signal"])
wire(plug, 0, plout, 0)
wire(plug, 1, plout, 1)

doc = {"patcher": {
    "fileversion": 1,
    "appversion": {"major": 9, "minor": 0, "revision": 0,
                   "architecture": "x64", "modernui": 1},
    "classnamespace": "box",
    "rect": [80.0, 80.0, 980.0, 720.0],
    "boxes": boxes,
    "lines": lines,
}}

out = Path(__file__).parent / "BassFace-map.maxpat"
out.write_text(json.dumps(doc, indent=1))
print(f"wrote {out} ({len(boxes)} boxes, {len(lines)} lines)")
