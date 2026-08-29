from __future__ import annotations

import argparse
from pathlib import Path

from .workflow import sanitize_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the hybrid RedactGate workflow.")
    parser.add_argument("input", type=Path, help="Path to a .txt, .log, .json, or .csv file.")
    parser.add_argument("-o", "--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args(argv)

    redacted_path, report_path, report = sanitize_file(args.input, args.output_dir, use_contextual=True)
    print(f"{report['status']} redacted={redacted_path} report={report_path}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
