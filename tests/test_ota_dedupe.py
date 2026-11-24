import unittest
from types import SimpleNamespace

from cmf_watch_utils import cmf_watch as cw
from cmf_watch_utils.ota_client import DEDUPE_WINDOW, Ota


class Clock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


def make(window=None):
    args = SimpleNamespace(ota_write=None)
    if window is not None:
        args.dedupe_window = window
    ota = Ota(args, image=b"\0" * 16)
    ota.clock = Clock()
    return ota


def a042_frame(offset):
    # A plaintext watch -> phone data request like the ones seen twice in #35.
    return cw.build_frame(0xFFFF, 0xA042, offset.to_bytes(4, "big") + (2403).to_bytes(4, "big"),
                          plaintext_no_crc=True)


class DedupeTests(unittest.TestCase):
    def test_default_window(self):
        self.assertEqual(make().dedupe_window, DEDUPE_WINDOW)

    def test_immediate_copy_is_dropped(self):
        ota = make()
        frame = a042_frame(0x400)
        ota.on_notify(None, frame)
        ota.clock.now += 0.003
        ota.on_notify(None, bytearray(frame))
        self.assertEqual(ota.rx.qsize(), 1)
        self.assertEqual((ota.notify_received, ota.notify_dropped), (2, 1))

    def test_watch_rerequest_after_window_is_kept(self):
        ota = make()
        frame = a042_frame(0x400)
        ota.on_notify(None, frame)
        ota.clock.now += 1.5  # the watch re-requests a range about 1.5 s later
        ota.on_notify(None, frame)
        self.assertEqual(ota.rx.qsize(), 2)
        self.assertEqual(ota.notify_dropped, 0)

    def test_different_frames_are_kept(self):
        ota = make()
        ota.on_notify(None, a042_frame(0x400))
        ota.on_notify(None, a042_frame(0xC00))
        self.assertEqual(ota.rx.qsize(), 2)

    def test_every_frame_doubled_yields_each_once(self):
        ota = make()
        for offset in range(0, 0x400 * 8, 0x400):
            frame = a042_frame(offset)
            ota.on_notify(None, frame)
            ota.clock.now += 0.002
            ota.on_notify(None, frame)
            ota.clock.now += 0.05
        self.assertEqual(ota.rx.qsize(), 8)
        self.assertEqual(ota.notify_dropped, 8)

    def test_zero_window_disables(self):
        ota = make(window=0)
        frame = a042_frame(0x400)
        ota.on_notify(None, frame)
        ota.on_notify(None, frame)
        self.assertEqual(ota.rx.qsize(), 2)


if __name__ == "__main__":
    unittest.main()
