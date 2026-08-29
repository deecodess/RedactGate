# RedactGate — Reproduction Guide

Keep this file updated while the project is built.

The final version should allow another developer to reproduce the main workflow from a clean checkout without guessing.

---

## 1. Requirements

```text
Python: 3.13.5
OS tested: Windows
Package manager: pip 25.1.1
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

No environment variables are required for the deterministic baseline.

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
Ran 7 tests
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
final safe_release_rate=0.667

Model calls: 0
Input tokens: 0
Output tokens: 0
Estimated model cost: 0.0
```

Do not estimate these if the tool/provider exposes actual values.

---

## 9. Expected limitations

- Only `.txt`, `.log`, `.json`, and `.csv` inputs are supported.
- The final CLI currently uses the deterministic workflow.
- Context-dependent spans such as customer names, addresses, and ambiguous identifiers are present in the benchmark but are not yet handled.

---

## 10. Clean-environment verification

Before considering reproduction complete:

- [ ] clone into a fresh directory;
- [ ] create a fresh environment;
- [ ] install from documented commands;
- [ ] run tests;
- [ ] run baseline example;
- [ ] run final example;
- [ ] run evaluation;
- [ ] confirm documented output paths;
- [ ] confirm no secret is required beyond documented environment variables;
- [ ] commit final documentation cleanup.

Record the tested commit hash here:

```text
Run `git rev-parse HEAD` in the checked-out repository.
```
