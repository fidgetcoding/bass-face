"""Ableton-facing outputs: virtual MIDI source + OSC sender.

MIDI is the automation-recording path (Live records mapped CC moves with
Automation Arm). OSC feeds the M4L mapper device (modulation path).
"""

from __future__ import annotations

from tracker.core import CHANNEL_ORDER

MIDI_PORT_NAME = "Bass Face"
MIDI_CHANNEL = 0  # MIDI channel 1
CC_BASE = 20      # ott=20, drive=21, squint=22, filth=23

OSC_HOST, OSC_PORT = "127.0.0.1", 7400
OSC_PREFIX = "/bassface"


class MidiOut:
    """Virtual CoreMIDI source. Sends a CC only when its 7-bit value changes."""

    def __init__(self, port_name: str = MIDI_PORT_NAME):
        import rtmidi
        self._out = rtmidi.MidiOut()
        self._out.open_virtual_port(port_name)
        self._last: dict[str, int] = {}

    def send(self, channels: dict[str, float]) -> None:
        for i, name in enumerate(CHANNEL_ORDER):
            if name not in channels:  # channel soloed out (mapping isolation)
                continue
            value = min(max(int(round(channels[name] * 127)), 0), 127)
            if self._last.get(name) != value:
                self._last[name] = value
                self._out.send_message([0xB0 | MIDI_CHANNEL, CC_BASE + i, value])

    def close(self) -> None:
        self._out.close_port()


class OscOut:
    """UDP OSC sender for the M4L device."""

    def __init__(self, host: str = OSC_HOST, port: int = OSC_PORT):
        from pythonosc.udp_client import SimpleUDPClient
        self._client = SimpleUDPClient(host, port)

    def send(self, channels: dict[str, float]) -> None:
        for name in CHANNEL_ORDER:
            if name in channels:
                self._client.send_message(f"{OSC_PREFIX}/{name}",
                                          float(channels[name]))

    def close(self) -> None:
        pass


def open_outputs(midi: bool = True, osc: bool = True) -> list:
    outs = []
    if midi:
        outs.append(MidiOut())
    if osc:
        outs.append(OscOut())
    return outs
