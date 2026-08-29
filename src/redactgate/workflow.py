from __future__ import annotations

from pathlib import Path

from .classifier import classify_candidates
from .context import extract_candidates
from .detectors import scan
from .parsers import load_text, validate_format
from .redactor import combine_detections, redact_with_verification_retries
from .report import build_report, write_json
from .trajectory import build_trajectory, write_trajectory
from .verifier import estimate_preservation


def sanitize_file(
    input_path: Path,
    output_dir: Path,
    *,
    use_contextual: bool = False,
    classifier_provider: str = "local",
    trajectory_dir: Path | None = None,
    max_verification_retries: int = 1,
) -> tuple[Path, Path, dict[str, object]]:
    text = load_text(input_path)
    deterministic = scan(text)
    candidates = []
    classification = None
    detections = deterministic

    if use_contextual:
        candidates = extract_candidates(text, deterministic)
        classification = classify_candidates(candidates, provider=classifier_provider)
        detections = combine_detections(deterministic + classification.sensitive_detections)

    result, verification, verification_retries = redact_with_verification_retries(
        text,
        detections,
        max_retries=max_verification_retries,
    )
    preservation = estimate_preservation(text, result.detections)
    verification["preservation_check_passed"] = preservation["passed"]
    verification["estimated_preservation"] = preservation
    format_validation = validate_format(input_path, result.text)
    verification["format_check_passed"] = format_validation["passed"]
    verification["format_validation"] = format_validation
    report = build_report(input_path, result, verification)
    report["metrics"]["verification_retries"] = verification_retries
    report["context"] = {
        "candidate_windows": len(candidates),
        "candidate_window_chars": sum(len(item.window) for item in candidates),
        "decisions": [item.to_report() for item in classification.decisions] if classification else [],
    }
    if classification:
        report["metrics"].update(
            {
                "classifier_provider": classification.provider,
                "prompt_version": classification.prompt_version,
                "model_calls": classification.model_calls,
                "input_tokens": classification.input_tokens,
                "output_tokens": classification.output_tokens,
                "estimated_model_cost": classification.estimated_model_cost,
            }
        )
    if trajectory_dir is not None:
        workflow_name = "final" if use_contextual else "baseline"
        trajectory = build_trajectory(
            input_path=input_path,
            workflow=workflow_name,
            deterministic_count=len(deterministic),
            candidates=candidates,
            result=result,
            verification=verification,
            metrics=report["metrics"],
        )
        trajectory_path = write_trajectory(trajectory_dir, input_path, workflow_name, trajectory)
        report["trajectory_path"] = str(trajectory_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    redacted_path = output_dir / f"{input_path.stem}.redacted{input_path.suffix}"
    report_path = output_dir / f"{input_path.stem}.redaction-report.json"

    redacted_path.write_text(result.text, encoding="utf-8")
    write_json(report_path, report)
    return redacted_path, report_path, report
