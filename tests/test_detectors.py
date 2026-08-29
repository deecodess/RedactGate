import unittest

from redactgate.detectors import scan


class DetectorTests(unittest.TestCase):
    def test_detects_obvious_sensitive_values(self) -> None:
        text = (
            "email a@example.com Authorization: Bearer abcdefghijklmnop "
            "url postgres://user:pass1234@localhost/db phone 415-555-0199"
        )
        found = scan(text)
        types = [item.type for item in found]
        self.assertIn("EMAIL", types)
        self.assertIn("TOKEN", types)
        self.assertIn("DATABASE_URL", types)
        self.assertIn("PHONE", types)

    def test_secret_assignment_redacts_value_only(self) -> None:
        text = "api_key=sk-abcdefghijklmnopqrstuvwxyz123456 request_id=req_public"
        found = scan(text)
        secret = next(item for item in found if item.type == "SECRET")
        self.assertEqual(text[secret.start:secret.end], "sk-abcdefghijklmnopqrstuvwxyz123456")

    def test_benign_uuid_is_not_detected(self) -> None:
        found = scan("request_id=550e8400-e29b-41d4-a716-446655440000 HTTP 500")
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()

