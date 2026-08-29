from __future__ import annotations

from pathlib import Path

from .classifier import classify_candidates
from .context import extract_candidates
from .detectors import scan
from .parsers import load_text
from .redactor import combine_detections, redact_text
from .report import build_report, write_json
from .verifier import verify_text


def sanitize_file(
    input_path: Path,
    output_dir: Path,
    *,
    use_contextual: bool = False,
) -> tuple[Path, Path, dict[str, object]]:
    text = load_text(input_path)
    deterministic = scan(text)
    candidates = []
    classification = None
    detections = deterministic

    if use_contextual:
        candidates = extract_candidates(text, deterministic)
        classification = classify_candidates(candidates)
        detections = combine_detections(deterministic + classification.sensitive_detections)

    result = redact_text(text, detections)
    verification = verify_text(result.text)
    report = build_report(input_path, result, verification)
    report["context"] = {
        "candidate_windows": len(candidates),
        "candidate_window_chars": sum(len(item.window) for item in candidates),
        "decisions": [item.to_report() for item in classification.decisions] if classification else [],
    }
    if classification:
        report["metrics"].update(
            {
                "model_calls": classification.model_calls,
                "input_tokens": classification.input_tokens,
                "output_tokens": classification.output_tokens,
                "estimated_model_cost": classification.estimated_model_cost,
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    redacted_path = output_dir / f"{input_path.stem}.redacted{input_path.suffix}"
    report_path = output_dir / f"{input_path.stem}.redaction-report.json"

    redacted_path.write_text(result.text, encoding="utf-8")
    write_json(report_path, report)
    return redacted_path, report_path, report
