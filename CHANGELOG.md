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
