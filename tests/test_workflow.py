import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from redactgate.workflow import sanitize_file


class WorkflowTests(unittest.TestCase):
    def test_sanitize_file_writes_artifact_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "sample.log"
            output = base / "out"
            source.write_text("Email alice@example.com failed with HTTP 500", encoding="utf-8")

            redacted_path, report_path, report = sanitize_file(source, output)

            self.assertTrue(redacted_path.exists())
            self.assertTrue(report_path.exists())
            self.assertEqual(report["status"], "PASS")
            self.assertTrue(report["verification"]["format_check_passed"])
            self.assertNotIn("alice@example.com", redacted_path.read_text(encoding="utf-8"))
            persisted = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertNotIn("alice@example.com", json.dumps(persisted))

    def test_hybrid_workflow_redacts_contextual_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "sample.txt"
            output = base / "out"
            source.write_text("Customer: Marcus Williams reported HTTP 500", encoding="utf-8")

            redacted_path, report_path, report = sanitize_file(source, output, use_contextual=True)

            self.assertEqual(report["status"], "PASS")
            self.assertIn("[REDACTED_PERSON]", redacted_path.read_text(encoding="utf-8"))
            self.assertNotIn("Marcus Williams", redacted_path.read_text(encoding="utf-8"))
            self.assertEqual(report["context"]["candidate_windows"], 1)
            self.assertEqual(report["metrics"]["model_calls"], 0)
            self.assertEqual(report["metrics"]["classifier_provider"], "local")
            self.assertTrue(report_path.exists())
            persisted = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertNotIn("Marcus Williams", json.dumps(persisted))

    def test_workflow_omits_trajectory_when_not_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "sample.txt"
            output = base / "out"
            source.write_text("Customer: Marcus Williams reported HTTP 500", encoding="utf-8")

            _, _, report = sanitize_file(source, output, use_contextual=True)

            self.assertNotIn("trajectory_path", report)

    def test_workflow_retries_when_verifier_finds_missed_obvious_secret(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "sample.log"
            output = base / "out"
            source.write_text("Email alice@example.com failed with HTTP 500", encoding="utf-8")

            with patch("redactgate.workflow.scan", return_value=[]):
                redacted_path, _, report = sanitize_file(source, output, max_verification_retries=1)

            self.assertEqual(report["metrics"]["verification_retries"], 1)
            self.assertEqual(report["status"], "PASS")
            self.assertNotIn("alice@example.com", redacted_path.read_text(encoding="utf-8"))

    def test_report_flags_excessive_redaction_density(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "sample.txt"
            output = base / "out"
            source.write_text("api_key=" + "x" * 600, encoding="utf-8")

            _, _, report = sanitize_file(source, output)

            self.assertEqual(report["status"], "FAIL")
            self.assertFalse(report["verification"]["preservation_check_passed"])
            self.assertGreater(report["verification"]["estimated_preservation"]["redaction_density"], 0.4)


if __name__ == "__main__":
    unittest.main()
