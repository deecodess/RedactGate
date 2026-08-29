import unittest

from redactgate.redactor import redact_text
from redactgate.verifier import verify_text


class RedactorTests(unittest.TestCase):
    def test_redacts_and_preserves_context(self) -> None:
        result = redact_text("User alice@example.com saw HTTP 500 request_id=req_public_123")
        self.assertNotIn("alice@example.com", result.text)
        self.assertIn("[REDACTED_EMAIL]", result.text)
        self.assertIn("HTTP 500", result.text)
        self.assertIn("req_public_123", result.text)

    def test_verifier_catches_remaining_obvious_secret(self) -> None:
        verification = verify_text("Still has bob@example.com")
        self.assertFalse(verification["obvious_secret_scan_passed"])


if __name__ == "__main__":
    unittest.main()

