import unittest

from fleetdiag.rules import MergeDuplicatesRule, RuleContext
from tests.factories import finding


class MergeDuplicatesRuleTest(unittest.TestCase):
    def setUp(self):
        self.rule = MergeDuplicatesRule()
        self.ctx = RuleContext()

    def test_merges_same_code_and_ecu(self):
        result = self.rule.apply(
            [
                finding(status=0x28, occurrences=1, last_seen="2026-10-01T00:00:00Z"),
                finding(status=0x09, occurrences=2, last_seen="2026-10-14T00:00:00Z"),
            ],
            self.ctx,
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].status, 0x29)
        self.assertEqual(result[0].occurrences, 3)
        self.assertEqual(result[0].last_seen, "2026-10-14T00:00:00Z")

    def test_does_not_mutate_input(self):
        items = [finding(), finding()]
        self.rule.apply(items, self.ctx)
        self.assertEqual(len(items), 2)

    # TODO(FD-118) : couvrir le cas « même code, ECU différents » (ne doit PAS fusionner)
    # TODO(FD-118) : couvrir last_seen absent sur les deux lectures


if __name__ == "__main__":
    unittest.main()
