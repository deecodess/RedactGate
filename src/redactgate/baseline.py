from __future__ import annotations

import argparse
from pathlib import Path

from .parsers import DEFAULT_MAX_BYTES
from .workflow import sanitize_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic RedactGate baseline.")
    parser.add_argument("input", type=Path, help="Path to a .txt, .log, .json, or .csv file.")
    parser.add_argument("-o", "--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    args = parser.parse_args(argv)

    try:
        redacted_path, report_path, report = sanitize_file(args.input, args.output_dir, max_bytes=args.max_bytes)
    except (OSError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")
    print(f"{report['status']} redacted={redacted_path} report={report_path}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
