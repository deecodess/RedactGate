import unittest

from redactgate.eval import EvalCase, evaluate_cases


class EvalTests(unittest.TestCase):
    def test_evaluate_cases_computes_real_metrics(self) -> None:
        cases = [
            EvalCase(
                id="tiny",
                format="txt",
                description="tiny",
                content="Email a@example.com HTTP 500",
                sensitive=[{"value": "a@example.com", "type": "EMAIL"}],
                must_preserve=["HTTP 500"],
            )
        ]
        result = evaluate_cases(cases, "baseline")
        self.assertEqual(result["safe_release_rate"], 1.0)
        self.assertEqual(result["sensitive_recall"], 1.0)
        self.assertEqual(result["benign_preservation"], 1.0)
        self.assertEqual(result["verification_retries"], 0)

    def test_baseline_eval_records_failure_categories(self) -> None:
        cases = [
            EvalCase(
                id="contextual",
                format="txt",
                description="contextual",
                content="Customer: Marcus Williams reported HTTP 500",
                sensitive=[{"value": "Marcus Williams", "type": "PERSON_NAME"}],
                must_preserve=["HTTP 500"],
            )
        ]
        result = evaluate_cases(cases, "baseline")
        self.assertEqual(result["safe_release_rate"], 0.0)
        self.assertEqual(result["cases"][0]["failure_categories"], ["LEAK_CONTEXTUAL"])
        self.assertEqual(result["failure_category_counts"], {"LEAK_CONTEXTUAL": 1})

    def test_final_eval_counts_candidate_windows(self) -> None:
        cases = [
            EvalCase(
                id="contextual",
                format="txt",
                description="contextual",
                content="Customer: Marcus Williams reported HTTP 500",
                sensitive=[{"value": "Marcus Williams", "type": "PERSON_NAME"}],
                must_preserve=["HTTP 500"],
            )
        ]
        result = evaluate_cases(cases, "final")
        self.assertEqual(result["candidate_windows"], 1)
        self.assertGreater(result["candidate_window_chars"], 0)
        self.assertEqual(result["safe_release_rate"], 1.0)
        self.assertEqual(result["model_calls"], 0)


if __name__ == "__main__":
    unittest.main()
