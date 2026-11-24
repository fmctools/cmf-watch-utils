import unittest

from cmf_watch_utils.cmf_watch import DEFAULT_NAME_PREFIX, matches_name, parse_a055


class NameMatchTests(unittest.TestCase):
    def test_default_prefixes_cover_both_models(self):
        self.assertTrue(matches_name("CMF Watch Pro 2-1A2B", DEFAULT_NAME_PREFIX))
        self.assertTrue(matches_name("CMF Watch 3 Pro-1A2B", DEFAULT_NAME_PREFIX))
        self.assertFalse(matches_name("Some Door Lock", DEFAULT_NAME_PREFIX))
        self.assertFalse(matches_name(None, DEFAULT_NAME_PREFIX))


class A055Tests(unittest.TestCase):
    def test_watch_pro_2_documented_sample(self):
        # From devices/cmf-watch-pro-2/protocol/ble.md: 3 ids, capacity byte 7.
        payload = bytes.fromhex("01020307" "45010000" "d03f5171" "dc9c4d3a")
        dials = parse_a055(payload)
        self.assertEqual(dials["count"], 3)
        self.assertEqual(dials["capacity"], 7)
        self.assertEqual(dials["ids"], [325, 1901150160, 978164956])

    def test_watch_3_pro_after_append(self):
        # Watch 3 Pro 1.0.1.77 after appending one face to seven listed dials.
        payload = bytes.fromhex(
            "0107080e" "14010000" "93010000" "9c010000" "35030000"
            "36030000" "37030000" "38030000" "23a25948")
        dials = parse_a055(payload)
        self.assertEqual((dials["byte1"], dials["count"], dials["capacity"]), (7, 8, 14))
        self.assertEqual(dials["ids"][-1], 0x4859A223)
        self.assertEqual(len(dials["ids"]), dials["count"])

    def test_sentinel_is_skipped(self):
        dials = parse_a055(bytes.fromhex("01000107" "ffffffff" "14010000"))
        self.assertEqual(dials["ids"], [276])

    def test_short_payload(self):
        with self.assertRaises(ValueError):
            parse_a055(b"\x01\x02")


if __name__ == "__main__":
    unittest.main()
