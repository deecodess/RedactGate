from __future__ import annotations

from .detectors import scan
from .models import Detection, RedactionResult


def redact_text(text: str, detections: list[Detection] | None = None) -> RedactionResult:
    found = detections if detections is not None else scan(text)
    pieces: list[str] = []
    cursor = 0
    replacements = 0

    for item in sorted(found, key=lambda detection: detection.start):
        pieces.append(text[cursor:item.start])
        pieces.append(item.replacement)
        cursor = item.end
        replacements += 1

    pieces.append(text[cursor:])
    return RedactionResult(text="".join(pieces), detections=found, replacements=replacements)

