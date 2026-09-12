# Security Notes

## Current Scope

RedactGate is a local CLI for `.txt`, `.log`, `.json`, and `.csv` artifacts. It does not upload content or call a model provider in the current default workflow.

## Sensitive-Data Handling

- Sanitized artifacts are written to `output/`.
- Redaction reports omit original detected values.
- Runtime trajectories omit original detected values, contextual spans, and candidate-window text.
- Evaluation cases use synthetic sensitive values only.
- Generated outputs are ignored by Git.

## Current Checks

- Unit tests assert that reports and trajectories do not persist representative raw sensitive values.
- Evaluation records failure categories for leaks, over-redaction, malformed output, and verifier findings.
- `rg` leak checks were run against generated outputs during milestone verification.

## Known Limits

- Unlabeled PII is only partially covered.
- The local contextual classifier is deterministic and label/pattern driven.
- No external security audit has been performed.
- This is not yet hardened for hostile inputs, concurrent writes, or large-scale batch processing.

## Before Production Use

- Test with real representative internal artifacts.
- Run a security review focused on report/trajectory leakage.
- Add CI secret scanning for commits and release artifacts.
- Decide whether a model-backed classifier is required, and document its data-handling policy before enabling it.

