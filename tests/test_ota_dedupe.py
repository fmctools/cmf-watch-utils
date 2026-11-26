import asyncio
import unittest
from unittest import mock
from types import SimpleNamespace

from cmf_watch_utils import cmf_watch as cw
from cmf_watch_utils import ota_client
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

    def test_interleaved_copies_are_dropped(self):
        # two different notifications inside the same duplication gap arrive as A B A B
        ota = make()
        a, b = a042_frame(0x400), a042_frame(0x800)
        for frame in (a, b, a, b):
            ota.on_notify(None, frame)
            ota.clock.now += 0.001
        self.assertEqual(ota.rx.qsize(), 2)
        self.assertEqual(ota.notify_dropped, 2)

    def test_frame_split_over_two_notifications_and_doubled(self):
        # at MTU 23 a frame arrives in pieces; each piece doubled (N1 N1 N2 N2) still parses once
        ota = make()
        frame = cw.build_frame(0xFFFF, 0xA042, bytes(range(19)), plaintext_no_crc=True)
        self.assertGreater(len(frame), 20)
        n1, n2 = frame[:20], frame[20:]
        for piece in (n1, n1, n2, n2):
            ota.on_notify(None, piece)
            ota.clock.now += 0.002
        self.assertEqual(ota.rx.qsize(), 1)
        self.assertEqual(ota.notify_dropped, 2)

    def test_copy_at_window_edge_is_kept(self):
        ota = make()
        frame = a042_frame(0x400)
        ota.on_notify(None, frame)
        ota.clock.now += DEDUPE_WINDOW
        ota.on_notify(None, frame)
        self.assertEqual(ota.rx.qsize(), 2)


class FindTests(unittest.TestCase):
    def scan(self, *devices, address=None):
        args = SimpleNamespace(ota_write=None, address=address)
        ota = Ota(args, image=b"\0" * 16)
        ota.log = lambda msg: None

        async def discover(timeout):
            return list(devices)

        with mock.patch.object(ota_client.BleakScanner, "discover", discover):
            return asyncio.run(ota.find())

    def test_single_watch_of_either_model(self):
        for name in ("CMF Watch Pro 2-AAAA", "CMF Watch 3 Pro-AAAA"):
            dev = SimpleNamespace(name=name, address="AA:BB:CC:DD:EE:FF")
            self.assertIs(self.scan(dev, SimpleNamespace(name="Phone", address="11:22:33:44:55:66")), dev)

    def test_two_watches_need_an_address(self):
        w2 = SimpleNamespace(name="CMF Watch Pro 2-AAAA", address="AA:BB:CC:DD:EE:01")
        w3 = SimpleNamespace(name="CMF Watch 3 Pro-BBBB", address="AA:BB:CC:DD:EE:02")
        with self.assertRaises(SystemExit) as e:
            self.scan(w2, w3)
        self.assertIn("pass --address", str(e.exception))
        self.assertIs(self.scan(w2, w3, address="aa:bb:cc:dd:ee:02"), w3)


if __name__ == "__main__":
    unittest.main()
