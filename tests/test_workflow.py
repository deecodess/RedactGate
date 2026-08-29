import json
import tempfile
import unittest
from pathlib import Path

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
            self.assertTrue(report_path.exists())
            persisted = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertNotIn("Marcus Williams", json.dumps(persisted))


if __name__ == "__main__":
    unittest.main()
