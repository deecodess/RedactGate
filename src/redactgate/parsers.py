from __future__ import annotations

import csv
import io
import json
from pathlib import Path


SUPPORTED_SUFFIXES = {".txt", ".log", ".json", ".csv"}
DEFAULT_MAX_BYTES = 1_000_000


def load_text(path: Path, max_bytes: int = DEFAULT_MAX_BYTES) -> str:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_SUFFIXES))
        raise ValueError(f"Unsupported file type '{suffix}'. Supported: {supported}")
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(f"Input is {size} bytes, above the {max_bytes} byte limit.")
    return path.read_text(encoding="utf-8")


def validate_format(path_or_format: Path | str, text: str) -> dict[str, object]:
    suffix = _suffix(path_or_format)
    if suffix == ".json":
        return _validate_json(text)
    if suffix == ".csv":
        return _validate_csv(text)
    return {"passed": True, "format": suffix.lstrip("."), "reason": "No structural validation required."}


def _suffix(path_or_format: Path | str) -> str:
    if isinstance(path_or_format, Path):
        return path_or_format.suffix.lower()
    value = path_or_format.lower()
    return value if value.startswith(".") else f".{value}"


def _validate_json(text: str) -> dict[str, object]:
    try:
        json.loads(text)
    except json.JSONDecodeError as error:
        return {"passed": False, "format": "json", "reason": error.msg}
    return {"passed": True, "format": "json", "reason": "JSON parsed successfully."}


def _validate_csv(text: str) -> dict[str, object]:
    try:
        rows = list(csv.reader(io.StringIO(text), strict=True))
    except csv.Error as error:
        return {"passed": False, "format": "csv", "reason": str(error)}
    widths = {len(row) for row in rows}
    if len(widths) > 1:
        return {"passed": False, "format": "csv", "reason": "CSV rows have inconsistent column counts."}
    return {"passed": True, "format": "csv", "reason": "CSV parsed successfully."}
