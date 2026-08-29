from __future__ import annotations

import argparse
from pathlib import Path

from .parsers import DEFAULT_MAX_BYTES
from .workflow import sanitize_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the hybrid RedactGate workflow.")
    parser.add_argument("input", type=Path, help="Path to a .txt, .log, .json, or .csv file.")
    parser.add_argument("-o", "--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--classifier-provider", default="local", choices=["local"])
    parser.add_argument("--trajectory-dir", type=Path, default=Path("trajectories"))
    parser.add_argument("--no-trajectory", action="store_true", help="Do not write a sanitized trajectory file.")
    args = parser.parse_args(argv)

    trajectory_dir = None if args.no_trajectory else args.trajectory_dir
    try:
        redacted_path, report_path, report = sanitize_file(
            args.input,
            args.output_dir,
            use_contextual=True,
            classifier_provider=args.classifier_provider,
            trajectory_dir=trajectory_dir,
            max_bytes=args.max_bytes,
        )
    except (OSError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")
    print(f"{report['status']} redacted={redacted_path} report={report_path}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
