"""CRITIQUE — l'interface publique doit rester identique au contrat v1."""

import json
import sys
import unittest

from tests import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import public_api  # noqa: E402


class PublicApiContractTest(unittest.TestCase):
    def test_public_api_matches_contract_v1(self):
        expected = json.loads(public_api.CONTRACT.read_text(encoding="utf-8"))["symbols"]
        problems = public_api.diff(expected, public_api.fingerprint())
        self.assertEqual(problems, [], "Rupture du contrat public v1 :\n" + "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
