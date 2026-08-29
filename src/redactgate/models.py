from __future__ import annotations

from dataclasses import dataclass


PLACEHOLDERS: dict[str, str] = {
    "EMAIL": "[REDACTED_EMAIL]",
    "TOKEN": "[REDACTED_TOKEN]",
    "JWT": "[REDACTED_TOKEN]",
    "SECRET": "[REDACTED_SECRET]",
    "DATABASE_URL": "[REDACTED_SECRET]",
    "PHONE": "[REDACTED_PHONE]",
}


@dataclass(frozen=True)
class Detection:
    start: int
    end: int
    type: str
    source: str
    confidence: float
    reason: str
    value: str

    @property
    def replacement(self) -> str:
        return PLACEHOLDERS.get(self.type, "[REDACTED_SECRET]")

    def to_report(self) -> dict[str, object]:
        return {
            "type": self.type,
            "replacement": self.replacement,
            "source": self.source,
            "confidence": self.confidence,
            "start": self.start,
            "end": self.end,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class RedactionResult:
    text: str
    detections: list[Detection]
    replacements: int

