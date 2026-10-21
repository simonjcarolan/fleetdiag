import unittest

from fleetdiag.core import DtcRecord, normalize_code, system_of


class NormalizeCodeTest(unittest.TestCase):
    def test_uppercases_and_strips(self):
        self.assertEqual(normalize_code(" p0301 "), "P0301")

    def test_rejects_invalid_codes(self):
        for bad in ("", "P03", "X0301", "P4301", "P03G1"):
            with self.subTest(code=bad), self.assertRaises(ValueError):
                normalize_code(bad)

    def test_system_mapping(self):
        self.assertEqual(system_of("C0035"), "chassis")
        self.assertEqual(system_of("U0100"), "network")


class DtcRecordTest(unittest.TestCase):
    def test_from_dict_accepts_hex_status(self):
        record = DtcRecord.from_dict({"code": "p0420", "ecu": "ECM", "status": "0x28"})
        self.assertEqual(record.code, "P0420")
        self.assertEqual(record.status, 0x28)
        self.assertEqual(record.occurrences, 1)

    def test_rejects_status_out_of_range(self):
        with self.assertRaises(ValueError):
            DtcRecord(code="P0420", status=0x100, ecu="ECM")


if __name__ == "__main__":
    unittest.main()
