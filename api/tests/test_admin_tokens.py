import unittest

from src.core.admin_tokens import create_admin_token, decode_admin_token


class AdminTokenTest(unittest.TestCase):
    def test_token_round_trip(self):
        token = create_admin_token("admin")
        self.assertEqual(decode_admin_token(token), "admin")

    def test_invalid_token_is_rejected(self):
        self.assertIsNone(decode_admin_token("not.a.valid.token"))


if __name__ == "__main__":
    unittest.main()