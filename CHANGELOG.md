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
