import unittest

from fleetdiag.rules import DropClearedRule, RuleContext
from tests.factories import finding


class DropClearedRuleTest(unittest.TestCase):
    def setUp(self):
        self.rule = DropClearedRule()

    def test_drops_status_zero(self):
        result = self.rule.apply(
            [finding(status=0x00), finding(code="P0420", status=0x28)], RuleContext()
        )
        self.assertEqual([f.code for f in result], ["P0420"])

    @unittest.skip("TODO FD-118 : statut 0x50 (tests non terminés uniquement) — test à écrire")
    def test_drops_status_with_only_test_not_completed_bits(self):
        pass


if __name__ == "__main__":
    unittest.main()
