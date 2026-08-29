from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from .context import CandidateWindow
from .models import RedactionResult
from .report import write_json


def build_trajectory(
    *,
    input_path: Path,
    workflow: str,
    deterministic_count: int,
    candidates: list[CandidateWindow],
    result: RedactionResult,
    verification: dict[str, object],
    metrics: dict[str, object],
) -> dict[str, object]:
    return {
        "version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "input_file": input_path.name,
        "workflow": workflow,
        "steps": [
            {"name": "parse", "status": "completed"},
            {"name": "deterministic_scan", "status": "completed", "detections": deterministic_count},
            {
                "name": "candidate_extraction",
                "status": "completed",
                "candidate_windows": len(candidates),
                "candidate_window_chars": sum(len(item.window) for item in candidates),
            },
            {
                "name": "classification",
                "status": "completed",
                "model_calls": metrics["model_calls"],
                "input_tokens": metrics["input_tokens"],
                "output_tokens": metrics["output_tokens"],
            },
            {"name": "redaction", "status": "completed", "redactions": result.replacements},
            {
                "name": "verification",
                "status": "completed",
                "passed": verification["obvious_secret_scan_passed"]
                and verification["preservation_check_passed"],
                "retries": metrics["verification_retries"],
            },
        ],
        "redactions": [item.to_report() for item in result.detections],
        "candidates": [item.to_report() for item in candidates],
        "verification": verification,
        "preservation": verification.get("estimated_preservation", {}),
        "metrics": metrics,
    }


def write_trajectory(trajectory_dir: Path, input_path: Path, workflow: str, payload: dict[str, object]) -> Path:
    trajectory_dir.mkdir(parents=True, exist_ok=True)
    path = trajectory_dir / f"{input_path.stem}.{workflow}.trajectory.json"
    write_json(path, payload)
    return path
