import json
import tempfile
import unittest
from pathlib import Path

from redactgate.workflow import sanitize_file


class TrajectoryTests(unittest.TestCase):
    def test_final_workflow_writes_sanitized_trajectory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "sample.txt"
            output = base / "out"
            trajectories = base / "trajectories"
            source.write_text(
                "Customer: Marcus Williams email marcus@example.com reported HTTP 500",
                encoding="utf-8",
            )

            _, _, report = sanitize_file(
                source,
                output,
                use_contextual=True,
                trajectory_dir=trajectories,
            )

            trajectory_path = Path(report["trajectory_path"])
            self.assertTrue(trajectory_path.exists())
            payload = json.loads(trajectory_path.read_text(encoding="utf-8"))
            serialized = json.dumps(payload)
            self.assertNotIn("Marcus Williams", serialized)
            self.assertNotIn("marcus@example.com", serialized)
            self.assertEqual(payload["workflow"], "final")
            self.assertEqual(payload["steps"][1]["detections"], 1)
            self.assertEqual(payload["steps"][2]["candidate_windows"], 1)
            self.assertEqual(payload["metrics"]["model_calls"], 0)


if __name__ == "__main__":
    unittest.main()

