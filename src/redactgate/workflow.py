from __future__ import annotations

from pathlib import Path

from .parsers import load_text
from .redactor import redact_text
from .report import build_report, write_json
from .verifier import verify_text


def sanitize_file(input_path: Path, output_dir: Path) -> tuple[Path, Path, dict[str, object]]:
    text = load_text(input_path)
    result = redact_text(text)
    verification = verify_text(result.text)
    report = build_report(input_path, result, verification)

    output_dir.mkdir(parents=True, exist_ok=True)
    redacted_path = output_dir / f"{input_path.stem}.redacted{input_path.suffix}"
    report_path = output_dir / f"{input_path.stem}.redaction-report.json"

    redacted_path.write_text(result.text, encoding="utf-8")
    write_json(report_path, report)
    return redacted_path, report_path, report

