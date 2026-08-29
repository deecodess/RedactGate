from __future__ import annotations

import re
from collections.abc import Iterable

from .models import Detection


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
AUTH_HEADER_RE = re.compile(
    r"\bAuthorization\s*:\s*(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{8,}",
    re.IGNORECASE,
)
BEARER_RE = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}\b", re.IGNORECASE)
JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")
API_KEY_RE = re.compile(
    r"\b(?:sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})\b"
)
DB_URL_RE = re.compile(
    r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^:\s/@]+:[^@\s/]+@[^\s'\"\)]+",
    re.IGNORECASE,
)
SECRET_ASSIGN_RE = re.compile(
    r"\b(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|client[_-]?secret)"
    r"\b\s*[:=]\s*(\"[^\"\r\n]{4,}\"|'[^'\r\n]{4,}'|[A-Za-z0-9_./+=:-]{8,})",
    re.IGNORECASE,
)
PHONE_RE = re.compile(r"(?<!\d)(?:\+1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)")


def scan(text: str) -> list[Detection]:
    candidates: list[Detection] = []
    candidates.extend(_simple_matches(text, EMAIL_RE, "EMAIL", "Email address pattern."))
    candidates.extend(_simple_matches(text, AUTH_HEADER_RE, "TOKEN", "Authorization header credential."))
    candidates.extend(_simple_matches(text, BEARER_RE, "TOKEN", "Bearer token pattern."))
    candidates.extend(_simple_matches(text, JWT_RE, "JWT", "JWT-like credential."))
    candidates.extend(_secret_assignments(text))
    candidates.extend(_simple_matches(text, API_KEY_RE, "TOKEN", "Common API key pattern."))
    candidates.extend(_simple_matches(text, DB_URL_RE, "DATABASE_URL", "Database URL with embedded credentials."))
    candidates.extend(_simple_matches(text, PHONE_RE, "PHONE", "High-confidence US phone number."))
    return _without_overlaps(candidates)


def _simple_matches(text: str, pattern: re.Pattern[str], type_: str, reason: str) -> Iterable[Detection]:
    for match in pattern.finditer(text):
        yield Detection(
            start=match.start(),
            end=match.end(),
            type=type_,
            source="deterministic",
            confidence=1.0,
            reason=reason,
            value=match.group(0),
        )


def _secret_assignments(text: str) -> Iterable[Detection]:
    for match in SECRET_ASSIGN_RE.finditer(text):
        yield Detection(
            start=match.start(2),
            end=match.end(2),
            type="SECRET",
            source="deterministic",
            confidence=1.0,
            reason=f"Sensitive assignment label '{match.group(1)}'.",
            value=match.group(2),
        )


def _without_overlaps(candidates: list[Detection]) -> list[Detection]:
    ordered = sorted(candidates, key=lambda item: (item.start, -(item.end - item.start)))
    selected: list[Detection] = []
    occupied_until = -1
    for item in ordered:
        if item.start < occupied_until:
            continue
        selected.append(item)
        occupied_until = item.end
    return selected
