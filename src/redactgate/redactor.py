from __future__ import annotations

from .detectors import scan
from .models import Detection, RedactionResult
from .verifier import verify_text


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


def combine_detections(detections: list[Detection]) -> list[Detection]:
    ordered = sorted(detections, key=lambda item: (item.start, -(item.end - item.start)))
    selected: list[Detection] = []
    occupied_until = -1
    for item in ordered:
        if item.start < occupied_until:
            continue
        selected.append(item)
        occupied_until = item.end
    return selected


def redact_with_verification_retries(
    text: str,
    detections: list[Detection],
    *,
    max_retries: int = 1,
) -> tuple[RedactionResult, dict[str, object], int]:
    result = redact_text(text, detections)
    verification = verify_text(result.text)
    retries = 0
    all_detections = list(result.detections)
    replacements = result.replacements

    while not verification["obvious_secret_scan_passed"] and retries < max_retries:
        retry_detections = scan(result.text)
        if not retry_detections:
            break
        retry_result = redact_text(result.text, retry_detections)
        retries += 1
        all_detections.extend(retry_result.detections)
        replacements += retry_result.replacements
        result = RedactionResult(
            text=retry_result.text,
            detections=all_detections,
            replacements=replacements,
        )
        verification = verify_text(result.text)

    return result, verification, retries
