from __future__ import annotations

import json
from pathlib import Path

from .models import RedactionResult


def build_report(input_file: Path, result: RedactionResult, verification: dict[str, object]) -> dict[str, object]:
    status = "PASS" if verification["obvious_secret_scan_passed"] else "FAIL"
    return {
        "input_file": str(input_file),
        "status": status,
        "redactions": [item.to_report() for item in result.detections],
        "verification": verification,
        "metrics": {
            "redaction_count": result.replacements,
            "model_calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_model_cost": 0.0,
        },
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

