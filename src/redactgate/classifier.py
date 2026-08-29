from __future__ import annotations

from dataclasses import dataclass

from .context import CandidateWindow
from .models import Detection


@dataclass(frozen=True)
class ClassificationDecision:
    span: str
    type: str
    sensitive: bool
    confidence: float
    reason: str
    start: int
    end: int

    def to_detection(self) -> Detection:
        return Detection(
            start=self.start,
            end=self.end,
            type=self.type,
            source="contextual_local",
            confidence=self.confidence,
            reason=self.reason,
            value=self.span,
        )

    def to_report(self) -> dict[str, object]:
        return {
            "type": self.type,
            "sensitive": self.sensitive,
            "confidence": self.confidence,
            "reason": self.reason,
            "start": self.start,
            "end": self.end,
        }


@dataclass(frozen=True)
class ClassificationResult:
    decisions: list[ClassificationDecision]
    model_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_model_cost: float = 0.0

    @property
    def sensitive_detections(self) -> list[Detection]:
        return [item.to_detection() for item in self.decisions if item.sensitive]


def classify_candidates(candidates: list[CandidateWindow]) -> ClassificationResult:
    decisions = [_classify_candidate(candidate) for candidate in candidates]
    return ClassificationResult(decisions=decisions)


def _classify_candidate(candidate: CandidateWindow) -> ClassificationDecision:
    return ClassificationDecision(
        span=candidate.span,
        type=candidate.type_hint,
        sensitive=True,
        confidence=_confidence(candidate.type_hint),
        reason=f"Appears after explicit {candidate.trigger!r} label.",
        start=candidate.start,
        end=candidate.end,
    )


def _confidence(type_hint: str) -> float:
    if type_hint == "PERSON_NAME":
        return 0.94
    if type_hint == "ADDRESS":
        return 0.96
    if type_hint == "IDENTIFIER":
        return 0.9
    return 0.85
