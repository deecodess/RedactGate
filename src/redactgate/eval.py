from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

from .redactor import redact_text
from .report import write_json


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

    for case in cases:
        result = redact_text(case.content)
        leaked = [item for item in case.sensitive if item["value"] in result.text]
        kept = [item for item in case.must_preserve if item in result.text]
        missing_benign = len(case.must_preserve) - len(kept)
        preservation = 1.0 if not case.must_preserve else len(kept) / len(case.must_preserve)
        passed = not leaked and preservation >= PRESERVATION_THRESHOLD

        total_sensitive += len(case.sensitive)
        redacted_sensitive += len(case.sensitive) - len(leaked)
        total_preserve += len(case.must_preserve)
        preserved += len(kept)
        false_redactions += missing_benign

        case_results.append(
            {
                "id": case.id,
                "description": case.description,
                "passed": passed,
                "leaked_sensitive_count": len(leaked),
                "benign_preservation": preservation,
                "false_redactions": missing_benign,
                "redactions": len(result.detections),
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
        "model_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "estimated_model_cost": 0.0,
        "cases": case_results,
    }


def write_comparison(baseline: dict[str, object], final: dict[str, object]) -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    rows = [
        ("Safe Release Rate", baseline["safe_release_rate"], final["safe_release_rate"]),
        ("Sensitive recall", baseline["sensitive_recall"], final["sensitive_recall"]),
        ("Benign preservation", baseline["benign_preservation"], final["benign_preservation"]),
        ("False redactions", baseline["false_redactions"], final["false_redactions"]),
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
    lines.append("Note: final currently uses the deterministic workflow until contextual classification is added.")
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

