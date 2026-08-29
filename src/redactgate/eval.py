from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

from .classifier import ClassificationResult, classify_candidates
from .context import extract_candidates
from .detectors import scan
from .parsers import validate_format
from .redactor import combine_detections, redact_with_verification_retries
from .report import write_json
from .verifier import verify_gold_release


CASE_FILE = Path("eval/cases/cases.json")
RESULT_DIR = Path("eval/results")
PRESERVATION_THRESHOLD = 0.95


@dataclass(frozen=True)
class EvalCase:
    id: str
    format: str
    description: str
    content: str
    sensitive: list[dict[str, str]]
    must_preserve: list[str]


def load_cases(path: Path = CASE_FILE) -> list[EvalCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [EvalCase(**item) for item in raw]


def evaluate_cases(cases: list[EvalCase], workflow_name: str) -> dict[str, object]:
    started = time.perf_counter()
    case_results = []
    total_sensitive = 0
    redacted_sensitive = 0
    total_preserve = 0
    preserved = 0
    false_redactions = 0
    candidate_windows = 0
    candidate_window_chars = 0
    model_calls = 0
    input_tokens = 0
    output_tokens = 0
    estimated_model_cost = 0.0
    classifier_provider = "none"
    prompt_version = "none"
    failure_category_counts: dict[str, int] = {}
    verification_retries = 0

    for case in cases:
        deterministic = scan(case.content)
        candidates = []
        classification = ClassificationResult(decisions=[])
        detections = deterministic
        if workflow_name == "final":
            candidates = extract_candidates(case.content, deterministic)
            classification = classify_candidates(candidates)
            classifier_provider = classification.provider
            prompt_version = classification.prompt_version
            detections = combine_detections(deterministic + classification.sensitive_detections)
            candidate_windows += len(candidates)
            candidate_window_chars += sum(len(item.window) for item in candidates)
            model_calls += classification.model_calls
            input_tokens += classification.input_tokens
            output_tokens += classification.output_tokens
            estimated_model_cost += classification.estimated_model_cost
        result, _, retries = redact_with_verification_retries(case.content, detections)
        verification_retries += retries
        verification = verify_gold_release(
            result.text,
            case.sensitive,
            case.must_preserve,
            PRESERVATION_THRESHOLD,
        )
        format_validation = validate_format(case.format, result.text)
        verification["format_check_passed"] = format_validation["passed"]
        verification["format_validation"] = format_validation
        if not format_validation["passed"]:
            verification["passed"] = False
            verification["failure_categories"].append("MALFORMED_OUTPUT")

        total_sensitive += len(case.sensitive)
        redacted_sensitive += len(case.sensitive) - int(verification["leaked_sensitive_count"])
        total_preserve += len(case.must_preserve)
        preserved += len(case.must_preserve) - int(verification["false_redactions"])
        false_redactions += int(verification["false_redactions"])
        for category in verification["failure_categories"]:
            failure_category_counts[category] = failure_category_counts.get(category, 0) + 1

        case_results.append(
            {
                "id": case.id,
                "description": case.description,
                "passed": verification["passed"],
                "leaked_sensitive_count": verification["leaked_sensitive_count"],
                "leaked_sensitive_types": verification["leaked_sensitive_types"],
                "benign_preservation": verification["benign_preservation"],
                "false_redactions": verification["false_redactions"],
                "failure_categories": verification["failure_categories"],
                "obvious_secret_scan_passed": verification["obvious_secret_scan_passed"],
                "preservation_check_passed": verification["preservation_check_passed"],
                "redactions": len(result.detections),
                "candidate_windows": len(candidates),
                "classified_sensitive": len(classification.sensitive_detections),
                "verification_retries": retries,
            }
        )

    passing = sum(1 for item in case_results if item["passed"])
    runtime_ms = round((time.perf_counter() - started) * 1000, 3)
    return {
        "workflow": workflow_name,
        "case_count": len(cases),
        "safe_release_rate": passing / len(cases) if cases else 0.0,
        "sensitive_recall": redacted_sensitive / total_sensitive if total_sensitive else 1.0,
        "benign_preservation": preserved / total_preserve if total_preserve else 1.0,
        "false_redactions": false_redactions,
        "runtime_ms": runtime_ms,
        "candidate_windows": candidate_windows,
        "candidate_window_chars": candidate_window_chars,
        "model_calls": model_calls,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_model_cost": estimated_model_cost,
        "classifier_provider": classifier_provider,
        "prompt_version": prompt_version,
        "failure_category_counts": failure_category_counts,
        "verification_retries": verification_retries,
        "cases": case_results,
    }


def write_comparison(baseline: dict[str, object], final: dict[str, object]) -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    rows = [
        ("Safe Release Rate", baseline["safe_release_rate"], final["safe_release_rate"]),
        ("Sensitive recall", baseline["sensitive_recall"], final["sensitive_recall"]),
        ("Benign preservation", baseline["benign_preservation"], final["benign_preservation"]),
        ("False redactions", baseline["false_redactions"], final["false_redactions"]),
        ("Candidate windows", baseline["candidate_windows"], final["candidate_windows"]),
        ("Candidate window chars", baseline["candidate_window_chars"], final["candidate_window_chars"]),
        ("Verification retries", baseline["verification_retries"], final["verification_retries"]),
        ("Model calls", baseline["model_calls"], final["model_calls"]),
        ("Input tokens", baseline["input_tokens"], final["input_tokens"]),
    ]
    lines = [
        "# RedactGate Evaluation Comparison",
        "",
        "| Metric | Baseline | Final | Change |",
        "|---|---:|---:|---:|",
    ]
    for label, base, fin in rows:
        change = fin - base if isinstance(base, (int, float)) and isinstance(fin, (int, float)) else "n/a"
        lines.append(f"| {label} | {base} | {fin} | {change} |")
    lines.append("")
    lines.append(f"Baseline failure categories: `{baseline['failure_category_counts']}`")
    lines.append(f"Final failure categories: `{final['failure_category_counts']}`")
    lines.append(f"Final classifier provider: `{final['classifier_provider']}`")
    lines.append(f"Final prompt version: `{final['prompt_version']}`")
    lines.append("")
    lines.append("Note: final currently uses a local deterministic contextual classifier, not a model provider.")
    (RESULT_DIR / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    cases = load_cases()
    baseline = evaluate_cases(cases, "baseline")
    final = evaluate_cases(cases, "final")
    write_json(RESULT_DIR / "baseline.json", baseline)
    write_json(RESULT_DIR / "final.json", final)
    write_comparison(baseline, final)
    print(f"baseline safe_release_rate={baseline['safe_release_rate']:.3f}")
    print(f"final safe_release_rate={final['safe_release_rate']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
