### 2026-08-29 - Deterministic baseline scaffold

**What changed**

Added the initial Python package, deterministic scanner/redactor, file workflow, baseline CLI, final CLI placeholder, 12 synthetic evaluation cases, and standard-library tests.

**Why**

The first useful milestone should remove obvious secrets without spending model tokens. Evaluation now exists before contextual classification, so later improvements can be measured against the same cases.

**Evidence**

`python -m unittest discover -s tests` ran 7 tests successfully.

`python -m redactgate.eval` generated:

```text
baseline safe_release_rate=0.667
final safe_release_rate=0.667
```

**Decision / learning**

The contextual classifier remains unimplemented in this milestone. This avoids adding model calls before candidate extraction and baseline behavior are measurable.

---

### 2026-08-29 - Ambiguous candidate extraction

**What changed**

Added deterministic candidate extraction for context-dependent spans after explicit labels, including customer/user/account-holder names, ship-to/address fields, and labeled numeric identifiers.

**Why**

The future classifier needs small, relevant windows instead of entire artifacts. This step measures candidate-window volume without adding model calls or changing release behavior.

**Evidence**

`python -m unittest discover -s tests` ran 12 tests successfully.

`python -m redactgate.eval` generated:

```text
baseline safe_release_rate=0.667
final safe_release_rate=0.667
final candidate_windows=4
final candidate_window_chars=306
```

**Decision / learning**

Candidate extraction is intentionally separate from redaction. A span becoming a candidate does not make it sensitive until a later classifier or rule confirms it.

---

### 2026-08-29 - Local contextual classifier

**What changed**

Added a structured local classifier interface that converts explicit contextual candidates into redaction detections without calling a model provider. The final CLI now uses this hybrid path while the baseline CLI remains deterministic-only.

**Why**

This creates the full baseline-versus-final comparison loop before spending model tokens. It also gives the later model-backed classifier a stable interface to replace.

**Evidence**

`python -m unittest discover -s tests` ran 14 tests successfully.

`python -m redactgate.eval` generated:

```text
baseline safe_release_rate=0.667
final safe_release_rate=1.000
final candidate_windows=4
final candidate_window_chars=306
model_calls=0
```

**Decision / learning**

Explicit contextual labels were enough to close the current synthetic benchmark without model calls. Reports intentionally avoid persisting contextual span text, so the report does not reproduce the sensitive values it helped redact.

---

### 2026-08-29 - Evaluation verification hardening

**What changed**

Centralized verification for evaluation in `verifier.py`, including gold-sensitive leak checks, benign-preservation checks, independent obvious-secret scanning, and explicit failure categories.

**Why**

Safe Release Rate should be backed by a verifier that explains why a case failed. This keeps future improvements honest and makes regression analysis cheaper.

**Evidence**

`python -m unittest discover -s tests` ran 18 tests successfully.

`python -m redactgate.eval` generated:

```text
baseline safe_release_rate=0.667
final safe_release_rate=1.000
baseline failure_categories={'LEAK_CONTEXTUAL': 4}
final failure_categories={}
```

**Decision / learning**

The current baseline misses four context-dependent cases, all categorized as `LEAK_CONTEXTUAL`. The final local contextual workflow passes those cases without adding model calls.

---

### 2026-08-29 - Sanitized trajectory logging

**What changed**

Added trajectory logging for the final workflow. Trajectories record the workflow steps, detection counts, candidate-window counts, verifier outcome, redaction metadata, and model/token usage.

**Why**

The project needs representative execution traces without storing source secrets. This makes the workflow auditable while keeping generated trajectories safe to inspect locally.

**Evidence**

`python -m unittest discover -s tests` ran 20 tests successfully.

`python -m redactgate.eval` generated:

```text
baseline safe_release_rate=0.667
final safe_release_rate=1.000
```

`python -m redactgate.cli examples/sample.log` wrote `trajectories/sample.final.trajectory.json`; a search for the sample email/token in generated outputs returned no matches.

**Decision / learning**

Trajectory records intentionally omit raw detected values, contextual spans, and candidate-window text. Generated trajectory files are ignored by Git, while the directory is kept with `.gitkeep`.

---

### 2026-08-29 - Bounded verification retries

**What changed**

Added a bounded retry loop after independent verification. If the verifier finds an obvious remaining secret, the workflow performs one more deterministic redaction pass over the sanitized text and records the retry count.

**Why**

The verifier should be able to block or repair obvious misses instead of merely reporting that the first pass completed.

**Evidence**

`python -m unittest discover -s tests` ran 22 tests successfully.

`python -m redactgate.eval` generated:

```text
baseline safe_release_rate=0.667
final safe_release_rate=1.000
baseline verification_retries=0
final verification_retries=0
```

The retry path is covered by a workflow regression test that simulates an initial obvious-secret miss and verifies that one bounded retry redacts it.

**Decision / learning**

Retries are capped by default at one pass. This satisfies the bounded-retry requirement without hiding persistent verifier failures behind an infinite loop.

---

### 2026-08-29 - CLI preservation scoring

**What changed**

Added estimated preservation scoring to normal CLI reports. Reports now include original character count, redacted original characters, retained character ratio, redaction density, and density thresholds.

**Why**

Non-evaluation runs need a visible signal for accidental over-redaction, even when there are no gold `must_preserve` spans.

**Evidence**

`python -m unittest discover -s tests` ran 24 tests successfully.

`python -m redactgate.eval` generated:

```text
baseline safe_release_rate=0.667
final safe_release_rate=1.000
```

`python -m redactgate.baseline examples/sample.log` and `python -m redactgate.cli examples/sample.log` both returned `PASS`.

The sample report recorded redaction density `0.476` and passed because the artifact has 145 characters, below the 200-character density-failure floor.

**Decision / learning**

Redaction density is useful as a warning signal, but it is too noisy to fail very small files. The CLI therefore reports density for every file and only fails density checks once the artifact is large enough for the ratio to be meaningful.

---

### 2026-08-29 - Format validation checks

**What changed**

Added structural validation for JSON and CSV sanitized outputs. Reports now include `format_check_passed` and format-validation details, and evaluation can categorize malformed output as `MALFORMED_OUTPUT`.

**Why**

A sanitized file should not be considered releasable if redaction leaves it malformed. This is especially important for JSON and CSV artifacts that users may feed into other tooling.

**Evidence**

`python -m unittest discover -s tests` ran 29 tests successfully.

`python -m redactgate.eval` generated:

```text
baseline safe_release_rate=0.667
final safe_release_rate=1.000
```

Both sample CLIs returned `PASS`, and the sample report recorded `format_check_passed=true`.

**Decision / learning**

JSON uses strict standard-library parsing. CSV validation checks parse errors and inconsistent row widths as a small, deterministic malformed-output signal.

---

### 2026-08-29 - Versioned classifier provider boundary

**What changed**

Added an explicit classifier provider boundary and checked in `prompts/context_classifier_v1.md` as the versioned structured-output prompt/schema for future model-backed classification.

**Why**

The project needs prompt versioning and measurable provider metadata before any model provider is enabled. Keeping the default provider as `local` preserves the zero-token workflow.

**Evidence**

`python -m unittest discover -s tests` ran 31 tests successfully.

`python -m redactgate.eval` generated:

```text
baseline safe_release_rate=0.667
final safe_release_rate=1.000
classifier_provider=local
prompt_version=context_classifier_v1
model_calls=0
```

**Decision / learning**

The provider interface rejects unsupported providers for now. A network model can be added later behind the same structured result type without changing the baseline path.

---

### 2026-08-29 - Deliverable documentation artifacts

**What changed**

Added a demo video outline, committed a sanitized representative trajectory example, updated the README with the main failure mode and project insight, and recorded the latest generated evaluation summary in `EVALUATION.md`.

**Why**

The project deliverables require a demo path, representative trajectories without secrets, and clear reproduction/evaluation context.

**Evidence**

The committed trajectory example contains redaction metadata, counts, verifier status, and model/token metrics without raw sensitive values.

**Decision / learning**

Generated runtime trajectories remain ignored. Only the stable `.example.json` trajectory is committed as a reviewable artifact.

---

### 2026-08-29 - Clean reproduction verification

**What changed**

Updated reproduction notes with a clean local clone and fresh virtual-environment verification run.

**Why**

The project should be runnable from a fresh checkout without hidden setup steps.

**Evidence**

The clean clone ran:

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

Expected output paths existed, and generated outputs did not contain the sample sensitive values.

**Decision / learning**

The package has no runtime dependencies. Editable installation still needs the standard build backend, so a sandboxed environment may require network permission for build dependencies.

---

### 2026-08-29 - MVP file-type workflow coverage

**What changed**

Added an end-to-end workflow test that sanitizes `.txt`, `.log`, `.json`, and `.csv` files and verifies redacted artifacts, reports, and format checks.

**Why**

The MVP explicitly supports four file types, so the workflow should prove all four routes work instead of relying on parser constants alone.

**Evidence**

`python -m unittest discover -s tests` ran 32 tests successfully.

`python -m redactgate.eval` generated:

```text
baseline safe_release_rate=0.667
final safe_release_rate=1.000
```

**Decision / learning**

The current implementation keeps parsing lightweight and validates JSON/CSV structure after redaction.

---

### 2026-08-29 - Model payload boundary

**What changed**

Added a classifier payload builder that packages only candidate spans and their small windows, along with prompt version metadata and estimated input-token count.

**Why**

Before any network model provider is enabled, the code should prove that model input is bounded to ambiguous windows rather than whole artifacts.

**Evidence**

`python -m unittest discover -s tests` ran 33 tests successfully.

`python -m redactgate.eval` generated:

```text
baseline safe_release_rate=0.667
final safe_release_rate=1.000
estimated_candidate_input_tokens=628
model_calls=0
input_tokens=0
```

**Decision / learning**

The model boundary is explicit but inactive by default. This keeps token use at zero while preserving the integration point for future ambiguity that deterministic rules cannot handle.

---

### 2026-08-29 - CLI size limit and errors

**What changed**

Added `--max-bytes` to both baseline and final CLIs, passed the configurable size limit through the workflow, and converted parser/workflow failures into concise CLI errors.

**Why**

The MVP requires a conservative configurable file-size limit, and users should see understandable errors instead of stack traces for unsupported inputs or oversized files.

**Evidence**

`python -m unittest discover -s tests` ran 36 tests successfully.

`python -m redactgate.eval` generated:

```text
baseline safe_release_rate=0.667
final safe_release_rate=1.000
```

`python -m redactgate.cli examples/sample.log --max-bytes 1000000` returned `PASS`.

**Decision / learning**

The default input limit remains 1,000,000 bytes. This is intentionally conservative for the first CLI version.

---

### 2026-08-29 - Final clean reproduction refresh

**What changed**

Refreshed the clean-clone reproduction transcript after adding CLI input-limit tests.

**Why**

The reproduction guide should reflect the latest test suite and current HEAD behavior.

**Evidence**

A fresh local clone with a fresh virtual environment ran:

```text
.venv\Scripts\python.exe -m unittest discover -s tests
Ran 36 tests
OK

.venv\Scripts\python.exe -m redactgate.baseline examples/sample.log
PASS redacted=output\sample.redacted.log report=output\sample.redaction-report.json

.venv\Scripts\python.exe -m redactgate.cli examples/sample.log
PASS redacted=output\sample.redacted.log report=output\sample.redaction-report.json

.venv\Scripts\python.exe -m redactgate.eval
baseline safe_release_rate=0.667
final safe_release_rate=1.000
```

Expected output paths existed, and generated outputs did not contain the sample sensitive values.

**Decision / learning**

The final reproduction flow remains dependency-light. The only network need observed in the sandbox was build-backend installation for editable package setup.
