{
 "patcher": {
  "fileversion": 1,
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
     "text": "BASS FACE v1.3 - auto-wires to macros named BROW OTT / MOUTH DRIVE / SQUINT PHASE / FACE FILTH on this track. Run tracker/core.py."
    }
   },
   {
    "box": {
     "id": "obj-2",
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
     "id": "obj-3",
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
     "id": "obj-4",
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
     "id": "obj-5",
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
     "id": "obj-6",
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
     ]
    }
   },
   {
    "box": {
     "id": "obj-7",
     "maxclass": "comment",
     "numinlets": 0,
     "numoutlets": 0,
     "patching_rect": [
      866.0,
      43.0,
      50.0,
      20.0
     ],
     "text": "rescan"
    }
   },
   {
    "box": {
     "id": "obj-8",
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
     "id": "obj-9",
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
     "id": "obj-10",
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
     "id": "obj-11",
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
     "id": "obj-12",
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
     "id": "obj-13",
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
     "id": "obj-14",
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
     "id": "obj-15",
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
     "id": "obj-16",
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
     "id": "obj-17",
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
     "id": "obj-18",
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
     "id": "obj-19",
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
     "id": "obj-20",
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
     "id": "obj-21",
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
     "id": "obj-22",
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
     "id": "obj-23",
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
     "id": "obj-24",
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
     "id": "obj-25",
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
     "id": "obj-26",
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
     "id": "obj-27",
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
     "id": "obj-28",
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
     "id": "obj-29",
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
     "id": "obj-30",
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
     "id": "obj-31",
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
     "id": "obj-32",
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
     "id": "obj-33",
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
     "id": "obj-34",
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
      "obj-2",
      0
     ],
     "destination": [
      "obj-3",
      0
     ]
    }
   },
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
      "obj-5",
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
      "obj-8",
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
      "obj-10",
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
      "obj-11",
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
      "obj-12",
      3
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
      "obj-12",
      4
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
      "obj-13",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-3",
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
      "obj-3",
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
      "obj-12",
      0
     ],
     "destination": [
      "obj-13",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-8",
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
      "obj-16",
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
      "obj-16",
      1
     ],
     "destination": [
      "obj-18",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-16",
      2
     ],
     "destination": [
      "obj-18",
      4
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
      "obj-19",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-3",
      1
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
      "obj-3",
      1
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
      "obj-19",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-8",
      2
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
      "obj-22",
      1
     ],
     "destination": [
      "obj-24",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-22",
      2
     ],
     "destination": [
      "obj-24",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-23",
      0
     ],
     "destination": [
      "obj-25",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-3",
      2
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
      "obj-3",
      2
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
      "obj-24",
      0
     ],
     "destination": [
      "obj-25",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-8",
      3
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
      "obj-28",
      1
     ],
     "destination": [
      "obj-30",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-28",
      2
     ],
     "destination": [
      "obj-30",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-29",
      0
     ],
     "destination": [
      "obj-31",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-3",
      3
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
      "obj-3",
      3
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
      "obj-30",
      0
     ],
     "destination": [
      "obj-31",
      0
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
      "obj-34",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-33",
      1
     ],
     "destination": [
      "obj-34",
      1
     ]
    }
   }
  ]
 }
}