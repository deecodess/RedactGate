# RedactGate Demo Video Outline

## Goal

Show that RedactGate turns a risky developer/support artifact into a safer shareable artifact with a report, verification status, and sanitized trajectory.

## Flow

1. Open `examples/sample.log` and point out the synthetic email and authorization header.
2. Run the deterministic baseline:

```bash
python -m redactgate.baseline examples/sample.log
```

3. Open `output/sample.redacted.log` and show typed placeholders.
4. Run the final workflow:

```bash
python -m redactgate.cli examples/sample.log
```

5. Open `output/sample.redaction-report.json` and show:

- `status`
- `redactions`
- `verification`
- `metrics`

6. Open `trajectories/sample.final.trajectory.json` and show that it contains counts and metadata, not raw secrets.
7. Run evaluation:

```bash
python -m redactgate.eval
```

8. Show `eval/results/comparison.md` with baseline versus final metrics.

## Talking Points

- Deterministic rules handle obvious secrets first.
- Candidate extraction keeps model context small.
- The current classifier is local, so model calls and cost are zero.
- The main known limitation is unlabeled or implicit PII outside the current candidate triggers.

