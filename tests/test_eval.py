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


if __name__ == "__main__":
    unittest.main()

