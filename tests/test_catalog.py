import unittest

from fleetdiag.core import Catalog, Severity
from fleetdiag.core.catalog import UNKNOWN_SEVERITY


class CatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = Catalog.load()

    def test_known_code(self):
        entry = self.catalog.lookup("c0035")
        self.assertEqual(entry.severity, Severity.CRITICAL)

    def test_unknown_code_falls_back(self):
        self.assertEqual(self.catalog.lookup("P0999").severity, UNKNOWN_SEVERITY)

    def test_catalog_is_not_empty(self):
        self.assertGreater(len(self.catalog), 10)


if __name__ == "__main__":
    unittest.main()
