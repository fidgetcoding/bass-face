"""Headless output tests. Run: .venv/bin/python tests/test_outputs.py"""

import socket
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tracker.core import CHANNEL_ORDER
from tracker.outputs import CC_BASE, MidiOut, OscOut


def test_virtual_midi_port_appears():
    import rtmidi
    out = MidiOut("Bass Face Test")
    time.sleep(0.2)  # CoreMIDI registration
    ports = rtmidi.MidiIn().get_ports()
    assert any("Bass Face Test" in p for p in ports), ports
    out.close()
    print("✓ virtual MIDI port appears in CoreMIDI")


def test_midi_sends_only_on_change():
    class Recorder:
        def __init__(self):
            self.msgs = []
        def send_message(self, m):
            self.msgs.append(m)
        def open_virtual_port(self, n):
            pass
        def close_port(self):
            pass

    out = MidiOut.__new__(MidiOut)
    out._out = Recorder()
    out._last = {}
    vals = dict.fromkeys(CHANNEL_ORDER, 0.5)
    out.send(vals)
    out.send(vals)  # identical frame -> no new messages
    assert len(out._out.msgs) == 4, out._out.msgs
    vals["ott_brow"] = 0.9
    out.send(vals)
    assert len(out._out.msgs) == 5
    assert out._out.msgs[-1][1] == CC_BASE  # ott CC number
    print("✓ MIDI throttles to value changes")


def test_osc_roundtrip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 7400))
    sock.settimeout(2)
    out = OscOut()
    out.send(dict.fromkeys(CHANNEL_ORDER, 0.42))
    seen = set()
    for _ in range(len(CHANNEL_ORDER)):
        data, _ = sock.recvfrom(1024)
        for name in CHANNEL_ORDER:
            if f"/bassface/{name}".encode() in data:
                seen.add(name)
    sock.close()
    assert seen == set(CHANNEL_ORDER), seen
    print("✓ OSC roundtrip delivers all 4 channels")


if __name__ == "__main__":
    test_virtual_midi_port_appears()
    test_midi_sends_only_on_change()
    test_osc_roundtrip()
    print("all passed")
