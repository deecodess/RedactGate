import unittest

from redactgate.redactor import redact_text
from redactgate.verifier import verify_gold_release, verify_text


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

    def test_gold_verifier_reports_contextual_leak(self) -> None:
        verification = verify_gold_release(
            "Customer: Marcus Williams reported HTTP 500",
            sensitive=[{"value": "Marcus Williams", "type": "PERSON_NAME"}],
            must_preserve=["HTTP 500"],
        )
        self.assertFalse(verification["passed"])
        self.assertEqual(verification["failure_categories"], ["LEAK_CONTEXTUAL"])

    def test_gold_verifier_reports_unlabeled_obvious_secret(self) -> None:
        verification = verify_gold_release(
            "Unexpected leak bob@example.com",
            sensitive=[],
            must_preserve=[],
        )
        self.assertFalse(verification["passed"])
        self.assertEqual(verification["failure_categories"], ["LEAK_DETERMINISTIC"])

    def test_gold_verifier_reports_over_redaction(self) -> None:
        verification = verify_gold_release(
            "Customer: [REDACTED_PERSON]",
            sensitive=[{"value": "Marcus Williams", "type": "PERSON_NAME"}],
            must_preserve=["HTTP 500"],
        )
        self.assertFalse(verification["passed"])
        self.assertEqual(verification["failure_categories"], ["OVER_REDACTION"])


if __name__ == "__main__":
    unittest.main()
