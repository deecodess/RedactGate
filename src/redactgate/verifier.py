from __future__ import annotations

from .models import Detection
from .detectors import scan


def verify_text(text: str, must_preserve: list[str] | None = None, preservation_threshold: float = 0.95) -> dict[str, object]:
    remaining = scan(text)
    preservation = verify_preservation(text, must_preserve or [], preservation_threshold)
    return {
        "obvious_secret_scan_passed": not remaining,
        "remaining_findings": [item.to_report() for item in remaining],
        "preservation_check_passed": preservation["passed"],
        "benign_preservation": preservation["score"],
        "missing_benign_count": preservation["missing_count"],
        "format_check_passed": True,
    }


def estimate_preservation(
    original_text: str,
    detections: list[Detection],
    *,
    max_redaction_density: float = 0.4,
    min_chars_for_density_failure: int = 200,
) -> dict[str, object]:
    original_chars = len(original_text)
    redacted_chars = _covered_chars(detections)
    redaction_density = 0.0 if original_chars == 0 else redacted_chars / original_chars
    retained_char_ratio = 1.0 - redaction_density
    passed = original_chars < min_chars_for_density_failure or redaction_density <= max_redaction_density
    return {
        "passed": passed,
        "original_chars": original_chars,
        "redacted_original_chars": redacted_chars,
        "retained_char_ratio": retained_char_ratio,
        "redaction_density": redaction_density,
        "max_redaction_density": max_redaction_density,
        "min_chars_for_density_failure": min_chars_for_density_failure,
    }


def verify_preservation(text: str, must_preserve: list[str], threshold: float = 0.95) -> dict[str, object]:
    kept = [item for item in must_preserve if item in text]
    missing_count = len(must_preserve) - len(kept)
    score = 1.0 if not must_preserve else len(kept) / len(must_preserve)
    return {
        "passed": score >= threshold,
        "score": score,
        "missing_count": missing_count,
    }


def _covered_chars(detections: list[Detection]) -> int:
    ranges = sorted((item.start, item.end) for item in detections if item.end > item.start)
    if not ranges:
        return 0

    total = 0
    current_start, current_end = ranges[0]
    for start, end in ranges[1:]:
        if start <= current_end:
            current_end = max(current_end, end)
            continue
        total += current_end - current_start
        current_start, current_end = start, end
    total += current_end - current_start
    return total


def verify_gold_release(
    text: str,
    sensitive: list[dict[str, str]],
    must_preserve: list[str],
    preservation_threshold: float = 0.95,
) -> dict[str, object]:
    leaked = [item for item in sensitive if item["value"] in text]
    preservation = verify_preservation(text, must_preserve, preservation_threshold)
    obvious = verify_text(text, must_preserve, preservation_threshold)
    failure_categories = _failure_categories(leaked, preservation["passed"], obvious["obvious_secret_scan_passed"])
    return {
        "passed": not leaked and preservation["passed"] and obvious["obvious_secret_scan_passed"],
        "leaked_sensitive_count": len(leaked),
        "leaked_sensitive_types": sorted({item["type"] for item in leaked}),
        "benign_preservation": preservation["score"],
        "false_redactions": preservation["missing_count"],
        "obvious_secret_scan_passed": obvious["obvious_secret_scan_passed"],
        "preservation_check_passed": preservation["passed"],
        "failure_categories": failure_categories,
    }


def _failure_categories(
    leaked: list[dict[str, str]],
    preservation_passed: bool,
    obvious_secret_scan_passed: bool,
) -> list[str]:
    categories: list[str] = []
    if (
        any(item["type"] in {"EMAIL", "TOKEN", "JWT", "SECRET", "DATABASE_URL", "PHONE"} for item in leaked)
        or not obvious_secret_scan_passed
    ):
        categories.append("LEAK_DETERMINISTIC")
    if any(item["type"] not in {"EMAIL", "TOKEN", "JWT", "SECRET", "DATABASE_URL", "PHONE"} for item in leaked):
        categories.append("LEAK_CONTEXTUAL")
    if not preservation_passed:
        categories.append("OVER_REDACTION")
    return categories
