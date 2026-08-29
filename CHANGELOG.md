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
