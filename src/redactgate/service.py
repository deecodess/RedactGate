from __future__ import annotations

from pathlib import Path
import tempfile

from .parsers import DEFAULT_MAX_BYTES
from .workflow import sanitize_file

SUPPORTED_SUFFIXES = {".txt", ".log", ".json", ".csv"}


def sanitize_upload(filename: str, data: bytes) -> dict[str, object]:
    safe_name = Path(filename).name
    suffix = Path(safe_name).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError("Supported files are .txt, .log, .json, and .csv.")
    if len(data) > DEFAULT_MAX_BYTES:
        raise ValueError(f"Input is above the {DEFAULT_MAX_BYTES} byte limit.")

    with tempfile.TemporaryDirectory(prefix="redactgate-") as temporary:
        root = Path(temporary)
        input_path = root / safe_name
        input_path.write_bytes(data)
        redacted_path, _, report = sanitize_file(
            input_path,
            root / "output",
            use_contextual=True,
            trajectory_dir=None,
            max_bytes=DEFAULT_MAX_BYTES,
        )
        # Never expose a server filesystem path in a browser response.
        report["input_file"] = safe_name
        return {
            "filename": safe_name,
            "status": report["status"],
            "sanitized": redacted_path.read_text(encoding="utf-8"),
            "report": report,
        }
