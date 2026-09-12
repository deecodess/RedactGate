from __future__ import annotations

import re
from pathlib import Path
from collections.abc import Iterable

from .models import Detection


SENSITIVE_LABELS = (
    "password",
    "passwd",
    "pwd",
    "secret",
    "token",
    "api_key",
    "api-key",
    "apikey",
    "apiKey",
    "access_key",
    "access-key",
    "accessKey",
    "access_token",
    "access-token",
    "accessToken",
    "client_secret",
    "client-secret",
    "clientSecret",
    "private_key",
    "private-key",
    "privateKey",
)
SENSITIVE_LABEL_RE = "|".join(re.escape(label) for label in SENSITIVE_LABELS)
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
GOOGLE_API_KEY_RE = re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")
SLACK_TOKEN_RE = re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")
STRIPE_KEY_RE = re.compile(r"\b(?:sk|rk)_(?:live|test|demo)_[A-Za-z0-9]{16,}\b")
PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
    re.DOTALL,
)
DB_URL_RE = re.compile(
    r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^:\s/@]+:[^@\s/]+@[^\s'\"\)]+",
    re.IGNORECASE,
)
SECRET_ASSIGN_RE = re.compile(
    rf"\b({SENSITIVE_LABEL_RE}|api[_-]?key|access[_-]?key|client[_-]?secret)"
    r"\b\s*[:=]\s*(\"[^\"\r\n]{4,}\"|'[^'\r\n]{4,}'|[A-Za-z0-9_./+=:-]{8,})",
    re.IGNORECASE,
)
JSON_SECRET_FIELD_RE = re.compile(
    rf'"(?P<label>{SENSITIVE_LABEL_RE}|api[_-]?key|access[_-]?key|client[_-]?secret)"'
    r'\s*:\s*"(?P<value>(?:\\.|[^"\\]){4,})"',
    re.IGNORECASE,
)
PHONE_RE = re.compile(r"(?<!\d)(?:\+1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)")


def scan(text: str, path_or_format: Path | str | None = None) -> list[Detection]:
    candidates: list[Detection] = []
    candidates.extend(_simple_matches(text, EMAIL_RE, "EMAIL", "Email address pattern."))
    candidates.extend(_simple_matches(text, AUTH_HEADER_RE, "TOKEN", "Authorization header credential."))
    candidates.extend(_simple_matches(text, BEARER_RE, "TOKEN", "Bearer token pattern."))
    candidates.extend(_simple_matches(text, JWT_RE, "JWT", "JWT-like credential."))
    candidates.extend(_secret_assignments(text))
    candidates.extend(_simple_matches(text, API_KEY_RE, "TOKEN", "Common API key pattern."))
    candidates.extend(_simple_matches(text, GOOGLE_API_KEY_RE, "TOKEN", "Google API key pattern."))
    candidates.extend(_simple_matches(text, SLACK_TOKEN_RE, "TOKEN", "Slack token pattern."))
    candidates.extend(_simple_matches(text, STRIPE_KEY_RE, "TOKEN", "Stripe secret key pattern."))
    candidates.extend(_simple_matches(text, PRIVATE_KEY_RE, "SECRET", "PEM private key block."))
    candidates.extend(_simple_matches(text, DB_URL_RE, "DATABASE_URL", "Database URL with embedded credentials."))
    candidates.extend(_simple_matches(text, PHONE_RE, "PHONE", "High-confidence US phone number."))
    candidates.extend(_structured_matches(text, path_or_format))
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


def _structured_matches(text: str, path_or_format: Path | str | None) -> Iterable[Detection]:
    suffix = _suffix(path_or_format)
    if suffix == ".json":
        yield from _json_secret_fields(text)
    elif suffix == ".csv":
        yield from _csv_secret_columns(text)


def _json_secret_fields(text: str) -> Iterable[Detection]:
    for match in JSON_SECRET_FIELD_RE.finditer(text):
        yield Detection(
            start=match.start("value"),
            end=match.end("value"),
            type="SECRET",
            source="structured_json",
            confidence=1.0,
            reason=f"Sensitive JSON key '{match.group('label')}'.",
            value=match.group("value"),
        )


def _csv_secret_columns(text: str) -> Iterable[Detection]:
    lines = text.splitlines(keepends=True)
    if not lines:
        return
    headers = [header.strip().lower() for header in lines[0].rstrip("\r\n").split(",")]
    sensitive_indexes = {
        index
        for index, header in enumerate(headers)
        if header in {label.lower() for label in SENSITIVE_LABELS}
        or header.replace("-", "_") in {"api_key", "access_key", "access_token", "client_secret", "private_key"}
    }
    if not sensitive_indexes:
        return

    offset = len(lines[0])
    for line in lines[1:]:
        row_text = line.rstrip("\r\n")
        spans = _simple_csv_cell_spans(row_text)
        for index in sensitive_indexes:
            if index >= len(spans):
                continue
            start, end = spans[index]
            if end <= start:
                continue
            yield Detection(
                start=offset + start,
                end=offset + end,
                type="SECRET",
                source="structured_csv",
                confidence=1.0,
                reason=f"Sensitive CSV column '{headers[index]}'.",
                value=row_text[start:end],
            )
        offset += len(line)


def _simple_csv_cell_spans(line: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    start = 0
    in_quotes = False
    index = 0
    while index < len(line):
        char = line[index]
        if char == '"':
            if in_quotes and index + 1 < len(line) and line[index + 1] == '"':
                index += 2
                continue
            in_quotes = not in_quotes
        elif char == "," and not in_quotes:
            spans.append(_trim_cell_span(line, start, index))
            start = index + 1
        index += 1
    spans.append(_trim_cell_span(line, start, len(line)))
    return spans


def _trim_cell_span(line: str, start: int, end: int) -> tuple[int, int]:
    while start < end and line[start].isspace():
        start += 1
    while end > start and line[end - 1].isspace():
        end -= 1
    if end - start >= 2 and line[start] == '"' and line[end - 1] == '"':
        return start + 1, end - 1
    return start, end


def _suffix(path_or_format: Path | str | None) -> str:
    if path_or_format is None:
        return ""
    if isinstance(path_or_format, Path):
        return path_or_format.suffix.lower()
    value = path_or_format.lower()
    return value if value.startswith(".") else f".{value}"


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
