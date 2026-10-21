import hashlib
import unittest

from fleetdiag.auth import SCOPE_WORKSHOP, AuthenticationError, authenticate, load_keyring_from_env


def _digest(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


class AuthenticateTest(unittest.TestCase):
    def setUp(self):
        self.keyring = {"garage": (_digest("cle-de-test"), frozenset({SCOPE_WORKSHOP}))}

    def test_known_key(self):
        principal = authenticate("cle-de-test", keyring=self.keyring)
        self.assertEqual(principal.client_id, "garage")
        self.assertTrue(principal.has_scope(SCOPE_WORKSHOP))

    def test_unknown_key(self):
        with self.assertRaises(AuthenticationError):
            authenticate("mauvaise-cle", keyring=self.keyring)

    def test_unknown_scope_is_rejected(self):
        keyring = {"x": (_digest("k"), frozenset({"report:admin"}))}
        with self.assertRaises(AuthenticationError):
            authenticate("k", keyring=keyring)

    def test_keyring_from_env(self):
        env = {"FLEETDIAG_KEY_GARAGE": f"{_digest('k')};report:workshop", "PATH": "/bin"}
        self.assertEqual(load_keyring_from_env(env)["garage"][1], frozenset({SCOPE_WORKSHOP}))


if __name__ == "__main__":
    unittest.main()
