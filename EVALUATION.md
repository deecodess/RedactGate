# RedactGate — Evaluation Plan

## Purpose

Evaluation should answer one practical question:

> Can this artifact be released after redaction without leaking known sensitive content or destroying too much useful context?

The benchmark must compare the deterministic baseline and the hybrid workflow on the exact same cases.

---

## Primary metric

# Safe Release Rate

For each case:

```text
PASS =
    zero gold sensitive spans leaked
    AND
    benign preservation >= threshold
```

Recommended initial preservation threshold:

```text
95%
```

Overall:

```text
Safe Release Rate =
    passing cases / total cases
```

---

## Secondary metrics

### Sensitive-span recall

```text
correctly redacted gold sensitive spans
/
all gold sensitive spans
```

### Benign preservation

```text
benign protected items left intact
/
all benign protected items
```

### False-redaction count

Number of protected benign items that were altered/redacted.

### Efficiency

Record where available:

- wall-clock runtime;
- model calls;
- input tokens;
- output tokens;
- estimated model cost.

---

## Case format

Each evaluation case should have a stable ID.

Suggested metadata:

```json
{
  "id": "case_007",
  "format": "log",
  "description": "Bearer token plus benign UUID",
  "sensitive": [
    {
      "value": "Bearer abc.def.ghi",
      "type": "TOKEN"
    }
  ],
  "must_preserve": [
    "550e8400-e29b-41d4-a716-446655440000",
    "HTTP 500"
  ]
}
```

Do not persist real secrets. All benchmark values must be synthetic.

---

## Minimum benchmark

Use at least these categories:

| Case | Main challenge |
|---|---|
| 01 | Email + bearer token |
| 02 | JSON API key + benign request ID |
| 03 | Database URL credentials |
| 04 | Person name after customer label |
| 05 | Postal address in support text |
| 06 | Phone number near timestamps |
| 07 | Repeated sensitive value |
| 08 | CSV with sensitive + benign columns |
| 09 | UUID that must remain untouched |
| 10 | Mixed deterministic + contextual content |
| 11 | Ambiguous numeric identifier |
| 12 | Deliberate over-redaction trap |

At least one case must be meaningfully difficult.

---

## Baseline

The baseline must use deterministic rules only.

Do not intentionally cripple it.

It should represent a competent small rules-based redactor.

---

## Final workflow

The final workflow may use:

- deterministic rules;
- candidate extraction;
- contextual classification;
- verification.

It must not receive extra evaluation information unavailable to the baseline other than the capabilities inherent to the final workflow.

Gold labels must never be exposed to the classifier.

---

## Required result artifacts

Store generated results under:

```text
eval/results/
```

Suggested files:

```text
baseline.json
final.json
comparison.md
```

A comparison should include:

| Metric | Baseline | Final | Change |
|---|---:|---:|---:|
| Safe Release Rate | generated | generated | generated |
| Sensitive recall | generated | generated | generated |
| Benign preservation | generated | generated | generated |
| False redactions | generated | generated | generated |
| Model calls | 0 | generated | generated |
| Input tokens | 0 | generated | generated |

Never hand-enter fabricated metrics.

---

## Failure analysis

Every failed case should record a failure category.

Suggested categories:

- `LEAK_DETERMINISTIC`
- `LEAK_CONTEXTUAL`
- `OVER_REDACTION`
- `PARSER_FAILURE`
- `CLASSIFIER_FAILURE`
- `VERIFICATION_FAILURE`
- `FORMAT_DAMAGE`
- `UNKNOWN`

Use failure analysis to decide what to improve next.

Do not add architecture based on intuition alone.

---

## Evaluation discipline

When improving the system:

1. keep the same benchmark;
2. make one meaningful change;
3. rerun evaluation;
4. record result;
5. keep or revert based on evidence;
6. update `docs/CHANGELOG.md`.

If a benchmark case itself is invalid, fix it explicitly and document why.
