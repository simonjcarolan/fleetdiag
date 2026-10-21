import json
import subprocess
import sys
import unittest

from tests import ROOT
from tests.factories import SAMPLE

CLI = ROOT / "consumers" / "workshop_cli" / "report_cli.py"


class WorkshopCliTest(unittest.TestCase):
    def test_json_output_is_parseable(self):
        out = subprocess.run(
            [sys.executable, str(CLI), str(SAMPLE), "--json"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertEqual(json.loads(out)["vehicle_id"], "VF1-TLS-0042")


if __name__ == "__main__":
    unittest.main()
