import unittest

from redactgate.context import extract_candidates
from redactgate.detectors import scan


class ContextTests(unittest.TestCase):
    def test_extracts_name_window_from_explicit_label(self) -> None:
        text = "prefix " * 20 + "Customer: Marcus Williams reported error E_CONN_RESET on route /checkout."
        candidates = extract_candidates(text)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].span, "Marcus Williams")
        self.assertEqual(candidates[0].type_hint, "PERSON_NAME")
        self.assertIn("Customer:", candidates[0].window)
        self.assertIn("E_CONN_RESET", candidates[0].window)
        self.assertNotIn("prefix prefix prefix prefix prefix prefix", candidates[0].window)

    def test_extracts_address_without_following_unrelated_sentence(self) -> None:
        text = "Ship-to address: 742 Evergreen Terrace, Springfield, IL 62704. Error code remains HTTP 409."
        candidates = extract_candidates(text)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].span, "742 Evergreen Terrace, Springfield, IL 62704")
        self.assertEqual(candidates[0].type_hint, "ADDRESS")

    def test_extracts_ambiguous_numeric_identifier_by_label(self) -> None:
        text = "Patient ID 782913445 should not be shared. Queue depth 42 and HTTP 202 should survive."
        candidates = extract_candidates(text)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].span, "782913445")
        self.assertEqual(candidates[0].type_hint, "IDENTIFIER")

    def test_skips_already_deterministic_spans(self) -> None:
        text = "User: Alice Smith email alice@example.com"
        candidates = extract_candidates(text, scan(text))
        self.assertEqual([item.span for item in candidates], ["Alice Smith"])


if __name__ == "__main__":
    unittest.main()

