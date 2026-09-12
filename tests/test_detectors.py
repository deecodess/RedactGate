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

    def test_detects_json_secret_value_by_key(self) -> None:
        text = '{"password":"hunter2-secret","request_id":"req_public"}'
        found = scan(text, "json")
        self.assertEqual(found[0].source, "structured_json")
        self.assertEqual(text[found[0].start:found[0].end], "hunter2-secret")

    def test_detects_csv_secret_column_by_header(self) -> None:
        text = "ticket,api_key,status\nT-1,syntheticsecretvalue,open\n"
        found = scan(text, "csv")
        self.assertEqual(found[0].source, "structured_csv")
        self.assertEqual(text[found[0].start:found[0].end], "syntheticsecretvalue")

    def test_detects_common_provider_tokens(self) -> None:
        text = (
            "google AIzaabcdefghijklmnopqrstuvwxyzABCDE1234 "
            "slack xoxb-123456789012-abcdefABCDEF "
            "stripe sk_demo_abcdefghijklmnopqrstuvwxyz"
        )
        found = scan(text)
        self.assertEqual([item.type for item in found], ["TOKEN", "TOKEN", "TOKEN"])

    def test_detects_private_key_block(self) -> None:
        text = (
            "before\n-----BEGIN PRIVATE KEY-----\n"
            "syntheticprivatekeymaterial\n"
            "-----END PRIVATE KEY-----\nafter"
        )
        found = scan(text)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].type, "SECRET")
        self.assertIn("PRIVATE KEY", found[0].value)


if __name__ == "__main__":
    unittest.main()
