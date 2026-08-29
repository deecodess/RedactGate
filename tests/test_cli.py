import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from redactgate.baseline import main as baseline_main
from redactgate.cli import main as final_main


class CliTests(unittest.TestCase):
    def test_baseline_cli_returns_clean_error_for_unsupported_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "sample.md"
            source.write_text("email alice@example.com", encoding="utf-8")
            stderr = io.StringIO()

            with self.assertRaises(SystemExit) as raised, redirect_stderr(stderr):
                baseline_main([str(source)])

            self.assertEqual(raised.exception.code, 2)
            self.assertIn("Unsupported file type", stderr.getvalue())

    def test_final_cli_honors_max_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "sample.txt"
            source.write_text("email alice@example.com", encoding="utf-8")
            stderr = io.StringIO()

            with self.assertRaises(SystemExit) as raised, redirect_stderr(stderr):
                final_main([str(source), "--max-bytes", "4"])

            self.assertEqual(raised.exception.code, 2)
            self.assertIn("above the 4 byte limit", stderr.getvalue())

    def test_final_cli_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "sample.txt"
            output = Path(tmp) / "out"
            trajectories = Path(tmp) / "trajectories"
            source.write_text("Customer: Marcus Williams reported HTTP 500", encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                code = final_main([str(source), "-o", str(output), "--trajectory-dir", str(trajectories)])

            self.assertEqual(code, 0)
            self.assertIn("PASS", stdout.getvalue())
            self.assertTrue((trajectories / "sample.final.trajectory.json").exists())


if __name__ == "__main__":
    unittest.main()

