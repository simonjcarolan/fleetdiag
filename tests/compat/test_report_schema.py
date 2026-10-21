"""CRITIQUE — FleetPortal doit accepter le rapport, quel que soit le profil appelant."""

import unittest

from consumers.fleetportal_stub.validator import validate_report
from tests.factories import ENGINEERING, FLEET, WORKSHOP, sample_records, service


class ReportSchemaCompatTest(unittest.TestCase):
    def test_fleetportal_accepts_report_for_every_profile(self):
        for name, principal in [
            ("internal", None),
            ("engineering", ENGINEERING),
            ("workshop", WORKSHOP),
            ("fleet", FLEET),
        ]:
            with self.subTest(profile=name):
                report = service().build_report(
                    sample_records(), principal=principal, vehicle_id="VF1-TLS-0042"
                )
                self.assertEqual(validate_report(report.to_dict()), [])

    def test_empty_report_is_accepted(self):
        self.assertEqual(validate_report(service().build_report([]).to_dict()), [])

    def test_validator_rejects_undeclared_field(self):
        payload = service().build_report([]).to_dict()
        payload["summary"]["hidden"] = 0
        self.assertTrue(validate_report(payload))


if __name__ == "__main__":
    unittest.main()
