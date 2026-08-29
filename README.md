# RedactGate

RedactGate sanitizes text-first developer/support artifacts before sharing. The current milestone is a deterministic baseline plus a synthetic evaluation harness.

Supported inputs:

- `.txt`
- `.log`
- `.json`
- `.csv`

## Setup

```bash
python -m pip install -e .
```

## Run Tests

```bash
python -m unittest discover -s tests
```

## Run The Baseline

```bash
python -m redactgate.baseline path/to/input.log
```

Outputs are written to `output/` by default:

- `<name>.redacted<suffix>`
- `<name>.redaction-report.json`

## Run Evaluation

```bash
python -m redactgate.eval
```

Evaluation outputs are written to `eval/results/`.

