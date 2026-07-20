{
 "patcher": {
  "fileversion": 1,
  "openinpresentation": 1,
  "appversion": {
   "major": 9,
   "minor": 0,
   "revision": 0,
   "architecture": "x64",
   "modernui": 1
  },
  "classnamespace": "box",
  "rect": [
   80.0,
   80.0,
   1010.0,
   420.0
  ],
  "boxes": [
   {
    "box": {
     "id": "obj-1",
     "maxclass": "comment",
     "numinlets": 0,
     "numoutlets": 0,
     "patching_rect": [
      30.0,
      10.0,
      700.0,
      20.0
     ],
     "text": "BASS FACE v1.5 - auto-wires to macros + auto-launches the camera tracker (Node for Max). CAM toggle stops/starts it."
    }
   },
   {
    "box": {
     "id": "obj-2",
     "maxclass": "comment",
     "numinlets": 0,
     "numoutlets": 0,
     "patching_rect": [
      0.0,
      0.0,
      90.0,
      18.0
     ],
     "text": "BASS FACE",
     "presentation": 1,
     "presentation_rect": [
      8.0,
      4.0,
      90.0,
      18.0
     ],
     "fontface": 1
    }
   },
   {
    "box": {
     "id": "obj-3",
     "maxclass": "comment",
     "numinlets": 0,
     "numoutlets": 0,
     "patching_rect": [
      0.0,
      0.0,
      150.0,
      15.0
     ],
     "text": "face -> your rack",
     "presentation": 1,
     "presentation_rect": [
      8.0,
      24.0,
      150.0,
      15.0
     ],
     "fontsize": 9.0
    }
   },
   {
    "box": {
     "id": "obj-4",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "patching_rect": [
      30.0,
      40.0,
      110.0,
      22.0
     ],
     "text": "udpreceive 7400",
     "outlettype": [
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-5",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 5,
     "patching_rect": [
      30.0,
      72.0,
      620.0,
      22.0
     ],
     "text": "route /bassface/ott_brow /bassface/drive_mouth /bassface/phase_squint /bassface/filth_disgust",
     "outlettype": [
      "",
      "",
      "",
      "",
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-6",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 3,
     "patching_rect": [
      700.0,
      40.0,
      100.0,
      22.0
     ],
     "text": "live.thisdevice",
     "outlettype": [
      "bang",
      "",
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-7",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "patching_rect": [
      700.0,
      72.0,
      130.0,
      22.0
     ],
     "text": "js bassface_map.js",
     "outlettype": [
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-8",
     "maxclass": "button",
     "numinlets": 1,
     "numoutlets": 1,
     "patching_rect": [
      840.0,
      40.0,
      24.0,
      24.0
     ],
     "outlettype": [
      "bang"
     ],
     "presentation": 1,
     "presentation_rect": [
      258.0,
      96.0,
      20.0,
      20.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-9",
     "maxclass": "comment",
     "numinlets": 0,
     "numoutlets": 0,
     "patching_rect": [
      866.0,
      43.0,
      50.0,
      20.0
     ],
     "text": "rescan",
     "presentation": 1,
     "presentation_rect": [
      240.0,
      118.0,
      56.0,
      15.0
     ],
     "fontsize": 9.0
    }
   },
   {
    "box": {
     "id": "obj-10",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 5,
     "patching_rect": [
      700.0,
      104.0,
      90.0,
      22.0
     ],
     "text": "route 0 1 2 3",
     "outlettype": [
      "",
      "",
      "",
      "",
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-11",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 2,
     "patching_rect": [
      700.0,
      140.0,
      200.0,
      22.0
     ],
     "text": "node.script bassface_launcher.js @autostart 1 @watch 0",
     "outlettype": [
      "",
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-12",
     "maxclass": "toggle",
     "numinlets": 1,
     "numoutlets": 1,
     "patching_rect": [
      910.0,
      140.0,
      24.0,
      24.0
     ],
     "outlettype": [
      "int"
     ],
     "presentation": 1,
     "presentation_rect": [
      258.0,
      44.0,
      20.0,
      20.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-13",
     "maxclass": "comment",
     "numinlets": 0,
     "numoutlets": 0,
     "patching_rect": [
      910.0,
      168.0,
      40.0,
      20.0
     ],
     "text": "CAM",
     "presentation": 1,
     "presentation_rect": [
      244.0,
      66.0,
      48.0,
      15.0
     ],
     "fontsize": 9.0
    }
   },
   {
    "box": {
     "id": "obj-14",
     "maxclass": "newobj",
     "numinlets": 3,
     "numoutlets": 3,
     "patching_rect": [
      910.0,
      196.0,
      50.0,
      22.0
     ],
     "text": "sel 1 0",
     "outlettype": [
      "bang",
      "bang",
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-15",
     "maxclass": "message",
     "numinlets": 2,
     "numoutlets": 1,
     "patching_rect": [
      880.0,
      226.0,
      55.0,
      22.0
     ],
     "text": "launch",
     "outlettype": [
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-16",
     "maxclass": "message",
     "numinlets": 2,
     "numoutlets": 1,
     "patching_rect": [
      945.0,
      226.0,
      40.0,
      22.0
     ],
     "text": "halt",
     "outlettype": [
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-17",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 2,
     "patching_rect": [
      700.0,
      172.0,
      90.0,
      22.0
     ],
     "text": "route running",
     "outlettype": [
      "",
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-18",
     "maxclass": "message",
     "numinlets": 2,
     "numoutlets": 1,
     "patching_rect": [
      700.0,
      202.0,
      45.0,
      22.0
     ],
     "text": "set $1",
     "outlettype": [
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-19",
     "maxclass": "comment",
     "numinlets": 0,
     "numoutlets": 0,
     "patching_rect": [
      30.0,
      120.0,
      100.0,
      20.0
     ],
     "text": "OTT"
    }
   },
   {
    "box": {
     "id": "obj-20",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 3,
     "patching_rect": [
      30.0,
      150.0,
      90.0,
      22.0
     ],
     "text": "unpack 0 0. 0.",
     "outlettype": [
      "int",
      "float",
      "float"
     ]
    }
   },
   {
    "box": {
     "id": "obj-21",
     "maxclass": "message",
     "numinlets": 2,
     "numoutlets": 1,
     "patching_rect": [
      30.0,
      185.0,
      50.0,
      22.0
     ],
     "text": "id $1",
     "outlettype": [
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-22",
     "maxclass": "newobj",
     "numinlets": 5,
     "numoutlets": 1,
     "patching_rect": [
      30.0,
      220.0,
      110.0,
      22.0
     ],
     "text": "scale 0. 1. 0. 1.",
     "outlettype": [
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-23",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 0,
     "patching_rect": [
      30.0,
      255.0,
      90.0,
      22.0
     ],
     "text": "live.remote~"
    }
   },
   {
    "box": {
     "id": "obj-24",
     "maxclass": "live.dial",
     "numinlets": 1,
     "numoutlets": 2,
     "patching_rect": [
      30.0,
      300.0,
      48.0,
      48.0
     ],
     "outlettype": [
      "",
      "float"
     ],
     "presentation": 1,
     "presentation_rect": [
      10.0,
      48.0,
      48.0,
      60.0
     ],
     "varname": "ott_brow",
     "parameter_enable": 1,
     "saved_attribute_attributes": {
      "valueof": {
       "parameter_longname": "OTT",
       "parameter_shortname": "OTT",
       "parameter_type": 0,
       "parameter_mmin": 0.0,
       "parameter_mmax": 1.0,
       "parameter_unitstyle": 1
      }
     }
    }
   },
   {
    "box": {
     "id": "obj-25",
     "maxclass": "comment",
     "numinlets": 0,
     "numoutlets": 0,
     "patching_rect": [
      265.0,
      120.0,
      100.0,
      20.0
     ],
     "text": "Drive"
    }
   },
   {
    "box": {
     "id": "obj-26",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 3,
     "patching_rect": [
      265.0,
      150.0,
      90.0,
      22.0
     ],
     "text": "unpack 0 0. 0.",
     "outlettype": [
      "int",
      "float",
      "float"
     ]
    }
   },
   {
    "box": {
     "id": "obj-27",
     "maxclass": "message",
     "numinlets": 2,
     "numoutlets": 1,
     "patching_rect": [
      265.0,
      185.0,
      50.0,
      22.0
     ],
     "text": "id $1",
     "outlettype": [
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-28",
     "maxclass": "newobj",
     "numinlets": 5,
     "numoutlets": 1,
     "patching_rect": [
      265.0,
      220.0,
      110.0,
      22.0
     ],
     "text": "scale 0. 1. 0. 1.",
     "outlettype": [
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-29",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 0,
     "patching_rect": [
      265.0,
      255.0,
      90.0,
      22.0
     ],
     "text": "live.remote~"
    }
   },
   {
    "box": {
     "id": "obj-30",
     "maxclass": "live.dial",
     "numinlets": 1,
     "numoutlets": 2,
     "patching_rect": [
      265.0,
      300.0,
      48.0,
      48.0
     ],
     "outlettype": [
      "",
      "float"
     ],
     "presentation": 1,
     "presentation_rect": [
      68.0,
      48.0,
      48.0,
      60.0
     ],
     "varname": "drive_mouth",
     "parameter_enable": 1,
     "saved_attribute_attributes": {
      "valueof": {
       "parameter_longname": "Drive",
       "parameter_shortname": "Drive",
       "parameter_type": 0,
       "parameter_mmin": 0.0,
       "parameter_mmax": 1.0,
       "parameter_unitstyle": 1
      }
     }
    }
   },
   {
    "box": {
     "id": "obj-31",
     "maxclass": "comment",
     "numinlets": 0,
     "numoutlets": 0,
     "patching_rect": [
      500.0,
      120.0,
      100.0,
      20.0
     ],
     "text": "Phase"
    }
   },
   {
    "box": {
     "id": "obj-32",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 3,
     "patching_rect": [
      500.0,
      150.0,
      90.0,
      22.0
     ],
     "text": "unpack 0 0. 0.",
     "outlettype": [
      "int",
      "float",
      "float"
     ]
    }
   },
   {
    "box": {
     "id": "obj-33",
     "maxclass": "message",
     "numinlets": 2,
     "numoutlets": 1,
     "patching_rect": [
      500.0,
      185.0,
      50.0,
      22.0
     ],
     "text": "id $1",
     "outlettype": [
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-34",
     "maxclass": "newobj",
     "numinlets": 5,
     "numoutlets": 1,
     "patching_rect": [
      500.0,
      220.0,
      110.0,
      22.0
     ],
     "text": "scale 0. 1. 0. 1.",
     "outlettype": [
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-35",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 0,
     "patching_rect": [
      500.0,
      255.0,
      90.0,
      22.0
     ],
     "text": "live.remote~"
    }
   },
   {
    "box": {
     "id": "obj-36",
     "maxclass": "live.dial",
     "numinlets": 1,
     "numoutlets": 2,
     "patching_rect": [
      500.0,
      300.0,
      48.0,
      48.0
     ],
     "outlettype": [
      "",
      "float"
     ],
     "presentation": 1,
     "presentation_rect": [
      126.0,
      48.0,
      48.0,
      60.0
     ],
     "varname": "phase_squint",
     "parameter_enable": 1,
     "saved_attribute_attributes": {
      "valueof": {
       "parameter_longname": "Phase",
       "parameter_shortname": "Phase",
       "parameter_type": 0,
       "parameter_mmin": 0.0,
       "parameter_mmax": 1.0,
       "parameter_unitstyle": 1
      }
     }
    }
   },
   {
    "box": {
     "id": "obj-37",
     "maxclass": "comment",
     "numinlets": 0,
     "numoutlets": 0,
     "patching_rect": [
      735.0,
      120.0,
      100.0,
      20.0
     ],
     "text": "Filth"
    }
   },
   {
    "box": {
     "id": "obj-38",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 3,
     "patching_rect": [
      735.0,
      150.0,
      90.0,
      22.0
     ],
     "text": "unpack 0 0. 0.",
     "outlettype": [
      "int",
      "float",
      "float"
     ]
    }
   },
   {
    "box": {
     "id": "obj-39",
     "maxclass": "message",
     "numinlets": 2,
     "numoutlets": 1,
     "patching_rect": [
      735.0,
      185.0,
      50.0,
      22.0
     ],
     "text": "id $1",
     "outlettype": [
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-40",
     "maxclass": "newobj",
     "numinlets": 5,
     "numoutlets": 1,
     "patching_rect": [
      735.0,
      220.0,
      110.0,
      22.0
     ],
     "text": "scale 0. 1. 0. 1.",
     "outlettype": [
      ""
     ]
    }
   },
   {
    "box": {
     "id": "obj-41",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 0,
     "patching_rect": [
      735.0,
      255.0,
      90.0,
      22.0
     ],
     "text": "live.remote~"
    }
   },
   {
    "box": {
     "id": "obj-42",
     "maxclass": "live.dial",
     "numinlets": 1,
     "numoutlets": 2,
     "patching_rect": [
      735.0,
      300.0,
      48.0,
      48.0
     ],
     "outlettype": [
      "",
      "float"
     ],
     "presentation": 1,
     "presentation_rect": [
      184.0,
      48.0,
      48.0,
      60.0
     ],
     "varname": "filth_disgust",
     "parameter_enable": 1,
     "saved_attribute_attributes": {
      "valueof": {
       "parameter_longname": "Filth",
       "parameter_shortname": "Filth",
       "parameter_type": 0,
       "parameter_mmin": 0.0,
       "parameter_mmax": 1.0,
       "parameter_unitstyle": 1
      }
     }
    }
   },
   {
    "box": {
     "id": "obj-43",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 2,
     "patching_rect": [
      700.0,
      255.0,
      70.0,
      22.0
     ],
     "text": "plugin~",
     "outlettype": [
      "signal",
      "signal"
     ]
    }
   },
   {
    "box": {
     "id": "obj-44",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 2,
     "patching_rect": [
      700.0,
      295.0,
      70.0,
      22.0
     ],
     "text": "plugout~",
     "outlettype": [
      "signal",
      "signal"
     ]
    }
   }
  ],
  "lines": [
   {
    "patchline": {
     "source": [
      "obj-4",
      0
     ],
     "destination": [
      "obj-5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-6",
      0
     ],
     "destination": [
      "obj-7",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-8",
      0
     ],
     "destination": [
      "obj-7",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-7",
      0
     ],
     "destination": [
      "obj-10",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-12",
      0
     ],
     "destination": [
      "obj-14",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-14",
      0
     ],
     "destination": [
      "obj-15",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-14",
      1
     ],
     "destination": [
      "obj-16",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-15",
      0
     ],
     "destination": [
      "obj-11",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-16",
      0
     ],
     "destination": [
      "obj-11",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-11",
      0
     ],
     "destination": [
      "obj-17",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-17",
      0
     ],
     "destination": [
      "obj-18",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-18",
      0
     ],
     "destination": [
      "obj-12",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-10",
      0
     ],
     "destination": [
      "obj-20",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-20",
      0
     ],
     "destination": [
      "obj-21",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-20",
      1
     ],
     "destination": [
      "obj-22",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-20",
      2
     ],
     "destination": [
      "obj-22",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-21",
      0
     ],
     "destination": [
      "obj-23",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-5",
      0
     ],
     "destination": [
      "obj-24",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-5",
      0
     ],
     "destination": [
      "obj-22",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-22",
      0
     ],
     "destination": [
      "obj-23",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-10",
      1
     ],
     "destination": [
      "obj-26",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-26",
      0
     ],
     "destination": [
      "obj-27",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-26",
      1
     ],
     "destination": [
      "obj-28",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-26",
      2
     ],
     "destination": [
      "obj-28",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-27",
      0
     ],
     "destination": [
      "obj-29",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-5",
      1
     ],
     "destination": [
      "obj-30",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-5",
      1
     ],
     "destination": [
      "obj-28",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-28",
      0
     ],
     "destination": [
      "obj-29",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-10",
      2
     ],
     "destination": [
      "obj-32",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-32",
      0
     ],
     "destination": [
      "obj-33",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-32",
      1
     ],
     "destination": [
      "obj-34",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-32",
      2
     ],
     "destination": [
      "obj-34",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-33",
      0
     ],
     "destination": [
      "obj-35",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-5",
      2
     ],
     "destination": [
      "obj-36",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-5",
      2
     ],
     "destination": [
      "obj-34",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-34",
      0
     ],
     "destination": [
      "obj-35",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-10",
      3
     ],
     "destination": [
      "obj-38",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-38",
      0
     ],
     "destination": [
      "obj-39",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-38",
      1
     ],
     "destination": [
      "obj-40",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-38",
      2
     ],
     "destination": [
      "obj-40",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-39",
      0
     ],
     "destination": [
      "obj-41",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-5",
      3
     ],
     "destination": [
      "obj-42",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-5",
      3
     ],
     "destination": [
      "obj-40",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-40",
      0
     ],
     "destination": [
      "obj-41",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-43",
      0
     ],
     "destination": [
      "obj-44",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-43",
      1
     ],
     "destination": [
      "obj-44",
      1
     ]
    }
   }
  ]
 }
}