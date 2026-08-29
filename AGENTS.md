# RedactGate — Agent Instructions

## Mission

Build **RedactGate**, a small, reliable privacy-sanitization tool that removes sensitive information from developer/support artifacts while preserving as much useful context as possible.

The product should accept supported files, identify sensitive spans, redact them, independently verify the sanitized output, and produce both:

1. a safe sanitized artifact; and
2. a concise redaction report.

The implementation should be intentionally small. Prefer deterministic code for obvious cases and use an LLM only where context is genuinely needed.

---

## Product Principle

> Let deterministic code handle certainty. Spend model tokens only on ambiguity.

Do not create a large multi-agent system. Do not add infrastructure unless a measured failure requires it.

---

## MVP Scope

Support these input types first:

- `.txt`
- `.log`
- `.json`
- `.csv`

Do not add PDF, image OCR, browser automation, databases, authentication, or a large frontend until the core workflow is complete and evaluated.

The first complete version may be CLI-only.

---

## Core Workflow

Implement this pipeline:

```text
Input file
   ↓
Parser / normalizer
   ↓
Deterministic sensitive-data scanner
   ↓
Context-window builder for ambiguous candidates
   ↓
Context classifier / redaction agent
   ↓
Redaction engine
   ↓
Independent verification scan
   ↓
Preservation check
   ↓
Sanitized file + report + trajectory
```

### Deterministic scanner

Handle obvious patterns in code where practical, such as:

- email addresses;
- authorization headers;
- bearer tokens;
- JWT-like strings;
- API-key-like values;
- database URLs containing credentials;
- common secret assignments;
- phone numbers when confidence is high;
- explicit sensitive labels such as `password`, `secret`, `token`, `api_key`.

Do not rely on the LLM for obvious regex-detectable secrets.

### Contextual classifier

Use the model only for candidate text windows that may contain context-dependent sensitive data, for example:

- names after labels such as `Customer:`, `User:`, `Account holder:`;
- street/postal addresses;
- organization-specific identifiers that may or may not be safe;
- ambiguous numeric strings;
- other spans that deterministic rules cannot safely classify.

Keep context windows small.

The model should return structured output, not prose.

Suggested decision schema:

```json
{
  "items": [
    {
      "span": "Marcus Williams",
      "type": "PERSON_NAME",
      "sensitive": true,
      "confidence": 0.96,
      "reason": "Appears after an explicit customer label."
    }
  ]
}
```

### Redaction engine

Use stable typed placeholders such as:

```text
[REDACTED_EMAIL]
[REDACTED_TOKEN]
[REDACTED_PERSON]
[REDACTED_ADDRESS]
[REDACTED_PHONE]
[REDACTED_SECRET]
```

The same sensitive value appearing multiple times in the same artifact should be handled consistently.

Do not silently mutate unrelated text.

### Independent verifier

After redaction, scan the sanitized output again.

A file is not considered safe merely because the first pass completed.

The verifier must check for:

- remaining obvious secrets;
- remaining gold-sensitive spans during evaluation;
- malformed output;
- accidental loss of too much benign content.

Use bounded retries. No infinite loops.

---

## Baseline

Maintain a separate baseline that uses deterministic detection only.

The baseline and final system must run on exactly the same evaluation cases.

Suggested commands:

```bash
python -m redactgate.baseline <input>
python -m redactgate.cli <input>
python -m redactgate.eval
```

Adapt names to the actual repository, but keep baseline and final solution independently runnable.

---

## Evaluation

The primary metric is:

# Safe Release Rate

A case passes only when:

1. no known sensitive span is leaked; and
2. benign information preservation meets the configured threshold.

Also report:

- sensitive-span recall;
- benign-span preservation;
- false-redaction count;
- runtime;
- model calls;
- input/output tokens when available;
- estimated model cost when available.

Use synthetic cases with explicit ground truth.

Never invent results.

---

## Project Structure

Prefer a compact structure similar to:

```text
.
├── AGENTS.md
├── README.md
├── pyproject.toml
├── .env.example
├── src/
│   └── redactgate/
│       ├── cli.py
│       ├── parsers.py
│       ├── detectors.py
│       ├── context.py
│       ├── classifier.py
│       ├── redactor.py
│       ├── verifier.py
│       ├── report.py
│       ├── baseline.py
│       └── eval.py
├── tests/
├── eval/
│   ├── cases/
│   └── results/
├── trajectories/
└── docs/
    ├── PROJECT_SPEC.md
    ├── BUILD_PLAN.md
    ├── EVALUATION.md
    ├── CHANGELOG.md
    └── REPRODUCTION.md
```

Reuse existing conventions if the repository already has them.

---

## Engineering Rules

- Keep modules small and explicit.
- Prefer standard-library solutions where reasonable.
- Use typed models / schemas for model responses.
- Keep prompts versioned in the repository.
- Do not hardcode benchmark results.
- Do not commit credentials.
- Provide `.env.example`.
- Keep sensitive sample data synthetic.
- Make errors visible and understandable.
- Add unit tests for detection, redaction, preservation, and verification.
- Add at least one end-to-end test.
- Avoid unnecessary frameworks.
- Avoid unnecessary agent orchestration.
- Do not build a large UI before evaluation works.

---

## Token-Efficiency Rules

Model usage must be measurable.

Before sending content to the model:

1. run deterministic rules;
2. isolate only ambiguous candidate regions;
3. remove unrelated surrounding text;
4. avoid sending an entire file when a short context window is enough;
5. batch small compatible candidates when useful.

Record model-call counts and token usage when the provider exposes it.

A design that increases token use without improving safety or preservation should be rejected or reverted.

---

## Git and Commit Discipline

Commit after every important, working step.

An important step includes:

- initial project scaffold;
- baseline implementation;
- evaluation dataset/harness;
- deterministic detector;
- contextual classifier;
- redaction engine;
- verification layer;
- end-to-end workflow;
- meaningful evaluation improvement;
- documentation/reproduction cleanup.

Before each commit:

1. run relevant tests;
2. remove debug output and temporary files;
3. inspect `git diff`;
4. make sure no secrets or generated junk are included;
5. update `docs/CHANGELOG.md` when the step changes behavior, architecture, evaluation, or a meaningful project decision.

Prefer focused commits such as:

```text
chore: scaffold redactgate project
feat: add deterministic sensitive-data detector
test: add synthetic redaction benchmark
feat: classify ambiguous sensitive spans
feat: verify sanitized artifacts before release
eval: compare baseline and hybrid workflow
docs: finalize reproduction instructions
```

Do not combine several unrelated milestones into one giant commit.

Do not commit a broken intermediate state unless there is a strong reason and it is clearly marked.

---

## Changelog Rules

Maintain `docs/CHANGELOG.md` as an engineering narrative, not a generated dump.

Each meaningful entry should state:

- what changed;
- why;
- evidence or observation;
- decision / learning.

When a meaningful product or engineering choice was explicitly made by the user, occasionally record that naturally in the changelog.

Approved wording includes:

> Deepanshi made this decision to keep the first version intentionally small and verifiable.

or:

> The user, Deepanshi, chose this tradeoff after reviewing the earlier result.

Do **not** put Deepanshi's name in every entry. Use it only when it truthfully represents a user-directed decision and reads naturally.

Never fabricate a decision and attribute it to Deepanshi.

---

## Cleanliness Rules

Keep the repository neat.

Do not leave:

- scratch scripts;
- duplicate implementations;
- unused dependencies;
- abandoned prompts;
- stale benchmark outputs;
- large generated files;
- secrets;
- unexplained TODO piles.

If an experiment is removed, delete dead code but preserve the learning in the changelog.

Generated evaluation outputs should live under a clearly named results directory.

---

## Decision Rule for New Features

Before adding a feature, answer:

1. What failure does this solve?
2. Can deterministic code solve it?
3. Does it improve Safe Release Rate or preservation?
4. Does it materially improve reliability or reproducibility?
5. Is the added complexity worth it?

If the answer is unclear, do not add the feature.

---

## Definition of Done

The first complete version is done when:

- [ ] CLI accepts all four MVP file types;
- [ ] deterministic-only baseline runs;
- [ ] hybrid workflow runs;
- [ ] contextual model receives only ambiguous windows;
- [ ] sanitized artifact is produced;
- [ ] redaction report is produced;
- [ ] independent verification runs before success is reported;
- [ ] at least 10 synthetic evaluation cases exist;
- [ ] at least one difficult case exists;
- [ ] baseline and final workflow use the same cases;
- [ ] Safe Release Rate is computed from real evaluation output;
- [ ] token/model-call usage is recorded when available;
- [ ] tests pass;
- [ ] representative trajectories are saved without secrets;
- [ ] changelog is current;
- [ ] reproduction instructions work from a clean environment;
- [ ] repository has been cleaned of temporary or dead artifacts.

---

## Final Reporting

When finishing a milestone, report:

### Completed

What was implemented.

### Evidence

Tests/evaluation that ran and their real results.

### Files changed

Important files only.

### Commit

The commit hash and message if a commit was created.

### Next step

Exactly one recommended next milestone.

Never claim an evaluation result that was not actually generated.
