# RedactGate

RedactGate sanitizes text-first developer/support artifacts before sharing. The current milestone includes a deterministic baseline, a local contextual classifier, and a synthetic evaluation harness.

Main failure mode: unlabeled or implicit PII that does not match deterministic rules or the current contextual labels may survive.

Hot take: the useful privacy agent is mostly not an agent. The safer first move is a small verified pipeline that spends model tokens only when deterministic code cannot decide.

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
The classifier provider is explicit and defaults to `local`; the versioned prompt/schema lives at `prompts/context_classifier_v1.md`.
It writes a sanitized trajectory to `trajectories/` unless `--no-trajectory` is passed.

Outputs are written to `output/` by default:

- `<name>.redacted<suffix>`
- `<name>.redaction-report.json`

Final workflow trajectories are written as:

- `trajectories/<name>.final.trajectory.json`

A committed sanitized example is available at `trajectories/sample.final.trajectory.example.json`.

Reports include an estimated preservation section with original size, redacted span density, retained character ratio, and the configured density threshold.
JSON and CSV outputs are structurally validated before the report status is marked `PASS`.

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
format_check_passed=true
classifier_provider=local
prompt_version=context_classifier_v1
estimated_candidate_input_tokens=628
model_calls=0
```
