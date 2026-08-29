import unittest

from redactgate.classifier import classify_candidates
from redactgate.context import extract_candidates


class ClassifierTests(unittest.TestCase):
    def test_local_classifier_returns_structured_sensitive_decision(self) -> None:
        candidates = extract_candidates("Customer: Marcus Williams reported HTTP 500")
        result = classify_candidates(candidates)

        self.assertEqual(result.model_calls, 0)
        self.assertEqual(len(result.decisions), 1)
        self.assertTrue(result.decisions[0].sensitive)
        self.assertEqual(result.decisions[0].type, "PERSON_NAME")
        self.assertEqual(result.sensitive_detections[0].source, "contextual_local")


if __name__ == "__main__":
    unittest.main()

