import unittest

from tests.factories import ENGINEERING, WORKSHOP, sample_records, service


class BuildReportTest(unittest.TestCase):
    def test_sample_report_internal_call(self):
        report = service().build_report(sample_records(), vehicle_id="VF1-TLS-0042")
        codes = [e.code for e in report.entries]
        self.assertNotIn("B1000", codes)  # effacé : supprimé
        self.assertEqual(codes.count("P0562"), 1)  # doublon fusionné
        self.assertEqual(report.summary["total"], 9)
        self.assertEqual(report.summary["active"], 3)
        self.assertEqual(report.summary["critical"], 1)

    def test_entries_sorted_by_severity(self):
        report = service().build_report(sample_records())
        severities = [int(e.severity) for e in report.entries]
        self.assertEqual(severities, sorted(severities, reverse=True))

    def test_engineering_sees_everything(self):
        internal = service().build_report(sample_records())
        eng = service().build_report(sample_records(), principal=ENGINEERING)
        self.assertEqual(internal.to_dict()["entries"], eng.to_dict()["entries"])

    def test_workshop_sees_all_codes(self):
        # FD-101 (2025) : régression corrigée — les ateliers ne voyaient pas
        # certains codes. Depuis, un atelier doit voir exactement les mêmes
        # défauts qu'un appel interne.
        internal = service().build_report(sample_records())
        workshop = service().build_report(sample_records(), principal=WORKSHOP)
        self.assertEqual(len(workshop.entries), len(internal.entries))

    # TODO : aucun test sur le profil « fleet »
    # TODO : aucun test sur un catalogue personnalisé


if __name__ == "__main__":
    unittest.main()
