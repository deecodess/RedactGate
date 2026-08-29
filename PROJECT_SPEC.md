# RedactGate — Project Specification

## One-line product definition

RedactGate sanitizes developer and support artifacts before they are shared by removing sensitive information while preserving the technical context needed to debug or collaborate.

---

## Target user

Primary users:

- software developers;
- support engineers;
- operations engineers;
- technical founders.

Typical situation:

A user needs to share a log, JSON payload, CSV export, or debug text with an external model, vendor, contractor, teammate, or support service, but the artifact may contain secrets or personal data.

---

## Core problem

Manual inspection is unreliable.

Simple regex-only scrubbing catches many obvious values but can miss context-dependent information such as names and addresses. Aggressive scrubbing can also destroy useful technical information.

The product must balance two goals:

1. **Safety:** sensitive content should not leak.
2. **Utility:** benign debugging context should remain intact.

---

## Product promise

Given a supported artifact, RedactGate should return:

1. a sanitized copy;
2. a redaction manifest/report;
3. a clear verification status.

A successful result should answer:

- What was redacted?
- Why was it redacted?
- Did verification pass?
- Was useful benign content preserved?

---

## MVP inputs

Supported file formats:

- TXT
- LOG
- JSON
- CSV

Maximum file size for the first version should be conservative and configurable.

---

## MVP outputs

For an input such as:

```text
samples/server.log
```

produce something equivalent to:

```text
output/server.redacted.log
output/server.redaction-report.json
```

The report should contain at minimum:

```json
{
  "input_file": "server.log",
  "status": "PASS",
  "redactions": [
    {
      "type": "EMAIL",
      "replacement": "[REDACTED_EMAIL]",
      "source": "deterministic",
      "confidence": 1.0
    }
  ],
  "verification": {
    "obvious_secret_scan_passed": true,
    "preservation_check_passed": true
  }
}
```

Do not store the original sensitive value in a persisted report unless explicitly required for a local-only debug mode. Default behavior should avoid reproducing secrets in logs or reports.

---

## Sensitive categories for the first version

### High-confidence deterministic categories

- email;
- bearer token;
- JWT-like credential;
- password/secret/token assignments;
- database URL credentials;
- common API-key-like values;
- high-confidence phone numbers.

### Context-dependent categories

- person names;
- street/postal addresses;
- customer/account-holder names;
- internal identifiers when context indicates sensitivity;
- ambiguous numeric sequences;
- organization-specific PII.

Do not attempt to solve every possible privacy classification problem in v1.

---

## Non-sensitive data that should usually survive

Examples:

- HTTP status codes;
- timestamps;
- stack traces;
- filenames;
- line numbers;
- request IDs that are not credentials;
- public package names;
- error messages;
- route names;
- non-secret configuration keys;
- benign numeric metrics.

This preservation requirement matters because deleting everything is safe but useless.

---

## Core pipeline

```text
parse
  ↓
deterministic detection
  ↓
candidate extraction
  ↓
contextual classification
  ↓
redaction
  ↓
verification
  ↓
report
```

The contextual model must not receive the full artifact unless a measured limitation demonstrates that broader context is necessary.

---

## Baseline definition

The baseline uses only deterministic detection and redaction.

It does not use the contextual model.

The final system is compared against this baseline on the exact same synthetic cases.

---

## Primary metric

# Safe Release Rate

A case passes when:

```text
no gold sensitive span remains
AND
benign preservation >= configured threshold
```

Recommended initial benign-preservation threshold:

```text
95%
```

The threshold may be changed if evaluation shows it is unrealistic, but the reason must be documented.

---

## Secondary metrics

- sensitive-span recall;
- false-redaction rate;
- benign-span preservation;
- runtime;
- model calls per artifact;
- model input/output tokens;
- estimated model cost when available.

---

## Initial evaluation set

Create at least 10 synthetic cases.

Suggested cases:

1. obvious email + bearer token;
2. JSON with API key and benign request ID;
3. DB URL with embedded password;
4. customer name after explicit label;
5. postal address in support note;
6. phone number mixed with benign timestamps;
7. repeated sensitive value appearing in multiple places;
8. CSV with PII columns and benign technical columns;
9. tricky case containing UUIDs that should not be redacted;
10. mixed artifact with both deterministic and contextual sensitive spans;
11. one intentionally difficult ambiguous numeric identifier;
12. one case designed to expose over-redaction.

Every case must include explicit gold labels.

---

## Key risks

### Leakage

A sensitive span survives.

Mitigation:

- second-pass verification;
- gold-span checks in evaluation;
- high-confidence deterministic rules.

### Over-redaction

Benign debugging context is removed.

Mitigation:

- preservation metric;
- typed redactions;
- context-aware classification;
- evaluation cases containing benign lookalikes.

### Token waste

Too much file content is sent to the model.

Mitigation:

- deterministic prefilter;
- small context windows;
- token telemetry.

### False confidence

The tool reports success even when verification is weak.

Mitigation:

- explicit PASS / FAIL / REVIEW status;
- bounded retry;
- never hide verification failures.

---

## Out of scope for the first complete version

- OCR;
- image redaction;
- PDFs;
- browser extensions;
- cloud storage integrations;
- authentication;
- team accounts;
- real-time streaming;
- enterprise policy engines;
- giant web dashboard;
- autonomous external sharing.

Finish and evaluate the core workflow before considering these.
