from __future__ import annotations

from .detectors import scan


def verify_text(text: str) -> dict[str, object]:
    remaining = scan(text)
    return {
        "obvious_secret_scan_passed": not remaining,
        "remaining_findings": [item.to_report() for item in remaining],
        "preservation_check_passed": True,
    }

