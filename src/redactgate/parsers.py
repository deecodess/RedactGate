from __future__ import annotations

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

