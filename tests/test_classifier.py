import unittest

from redactgate.classifier import PROMPT_VERSION, build_model_payload, classify_candidates, load_prompt
from redactgate.context import extract_candidates


class ClassifierTests(unittest.TestCase):
    def test_local_classifier_returns_structured_sensitive_decision(self) -> None:
        candidates = extract_candidates("Customer: Marcus Williams reported HTTP 500")
        result = classify_candidates(candidates)

        self.assertEqual(result.model_calls, 0)
        self.assertEqual(result.provider, "local")
        self.assertEqual(result.prompt_version, PROMPT_VERSION)
        self.assertEqual(len(result.decisions), 1)
        self.assertTrue(result.decisions[0].sensitive)
        self.assertEqual(result.decisions[0].type, "PERSON_NAME")
        self.assertEqual(result.sensitive_detections[0].source, "contextual_local")

    def test_prompt_is_versioned_in_repo(self) -> None:
        prompt = load_prompt()
        self.assertIn("structured JSON", prompt)
        self.assertIn("PERSON_NAME", prompt)

    def test_rejects_unknown_provider(self) -> None:
        with self.assertRaises(ValueError):
            classify_candidates([], provider="network")

    def test_model_payload_contains_only_candidate_windows(self) -> None:
        text = "unrelated-start " * 20 + "Customer: Marcus Williams reported HTTP 500"
        candidates = extract_candidates(text)
        payload = build_model_payload(candidates)
        serialized = str(payload)

        self.assertEqual(payload["prompt_version"], PROMPT_VERSION)
        self.assertIn("Marcus Williams", serialized)
        self.assertIn("HTTP 500", serialized)
        self.assertNotIn("unrelated-start unrelated-start unrelated-start", serialized)
        self.assertGreater(payload["estimated_input_tokens"], 0)


if __name__ == "__main__":
    unittest.main()
