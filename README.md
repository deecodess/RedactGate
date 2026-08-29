# RedactGate

RedactGate sanitizes text-first developer/support artifacts before sharing. The current milestone includes a deterministic baseline, a local contextual classifier, and a synthetic evaluation harness.

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

The baseline uses deterministic rules only.

## Run RedactGate

```bash
python -m redactgate.cli path/to/input.log
```

The final workflow currently adds local contextual classification for explicit candidate windows. It does not call a model provider yet.
It writes a sanitized trajectory to `trajectories/` unless `--no-trajectory` is passed.

Outputs are written to `output/` by default:

- `<name>.redacted<suffix>`
- `<name>.redaction-report.json`

Final workflow trajectories are written as:

- `trajectories/<name>.final.trajectory.json`

## Run Evaluation

```bash
python -m redactgate.eval
```

Evaluation outputs are written to `eval/results/`.

Latest local evaluation:

```text
baseline safe_release_rate=0.667
final safe_release_rate=1.000
baseline failure categories={'LEAK_CONTEXTUAL': 4}
final failure categories={}
baseline verification_retries=0
final verification_retries=0
model_calls=0
```
