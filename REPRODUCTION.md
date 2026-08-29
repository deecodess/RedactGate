# RedactGate — Reproduction Guide

Keep this file updated while the project is built.

The final version should allow another developer to reproduce the main workflow from a clean checkout without guessing.

---

## 1. Requirements

```text
Python: 3.13.5
OS tested: Windows
Package manager: pip 25.1.1
Default max input size: 1,000,000 bytes
```

---

## 2. Setup

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
Copy-Item .env.example .env
```

The editable install was tested on Windows.

---

## 3. Environment variables

No environment variables are required for the deterministic baseline or the current local contextual classifier.

```text
MODEL_API_KEY=
MODEL_NAME=
```

Never place real credentials in this file.

---

## 4. Run tests

```bash
python -m unittest discover -s tests
```

Expected outcome:

```text
Ran 36 tests
OK
```

---

## 5. Run the deterministic baseline

```bash
python -m redactgate.baseline examples/sample.log
```

Expected output files:

```text
output/sample.redacted.log
output/sample.redaction-report.json
```

---

## 6. Run RedactGate

```bash
python -m redactgate.cli examples/sample.log
```

Expected output files:

```text
output/sample.redacted.log
output/sample.redaction-report.json
trajectories/sample.final.trajectory.json
```

---

## 7. Run evaluation

```bash
python -m redactgate.eval
```

Expected result files:

```text
eval/results/baseline.json
eval/results/final.json
eval/results/comparison.md
```

Only keep names that match the real implementation.

---

## 8. Runtime and cost

```text
Observed command output:
baseline safe_release_rate=0.667
final safe_release_rate=1.000
baseline failure categories: {'LEAK_CONTEXTUAL': 4}
final failure categories: {}
baseline verification retries: 0
final verification retries: 0
sample format check: PASS
classifier provider: local
prompt version: context_classifier_v1
estimated candidate input tokens: 628
sample preservation density: 0.476
sample preservation status: PASS because original_chars=145 is below the 200-character density-failure floor

Model calls: 0
Input tokens: 0
Output tokens: 0
Estimated model cost: 0.0
```

Representative sanitized trajectory:

```text
trajectories/sample.final.trajectory.example.json
```

Do not estimate these if the tool/provider exposes actual values.

---

## 9. Expected limitations

- Only `.txt`, `.log`, `.json`, and `.csv` inputs are supported.
- The final CLI currently uses deterministic rules plus a local contextual classifier.
- Context-dependent spans are handled only for explicit labels covered by candidate extraction.
- No external model provider is wired yet.

---

## 10. Clean-environment verification

Verified locally on Windows using a fresh local clone at `.repro-clone/` and a fresh virtual environment.

- [x] clone into a fresh directory;
- [x] create a fresh environment;
- [x] install from documented commands;
- [x] run tests;
- [x] run baseline example;
- [x] run final example;
- [x] run evaluation;
- [x] confirm documented output paths;
- [x] confirm no secret is required beyond documented environment variables;
- [x] confirm generated outputs do not contain sample sensitive values.

Observed clean-clone commands:

```text
.venv\Scripts\python.exe -m unittest discover -s tests
Ran 31 tests
OK

.venv\Scripts\python.exe -m redactgate.baseline examples/sample.log
PASS redacted=output\sample.redacted.log report=output\sample.redaction-report.json

.venv\Scripts\python.exe -m redactgate.cli examples/sample.log
PASS redacted=output\sample.redacted.log report=output\sample.redaction-report.json

.venv\Scripts\python.exe -m redactgate.eval
baseline safe_release_rate=0.667
final safe_release_rate=1.000
```

Record the tested commit hash here:

```text
Run `git rev-parse HEAD` in the checked-out repository.
```
