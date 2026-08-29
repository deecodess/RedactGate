from __future__ import annotations

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
