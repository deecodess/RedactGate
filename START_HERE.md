# RedactGate Workflow Pack

Use these files at the root of the RedactGate repository.

## Start here

1. Put `AGENTS.md` in the repository root.
2. Put the `docs/` files under `docs/`.
3. Give Codex this instruction:

```text
Read AGENTS.md and all files in docs/ before making changes.
Start with Phase 0 in docs/BUILD_PLAN.md.
Work one phase at a time.
Run tests before each important commit.
Update docs/CHANGELOG.md when behavior, architecture, evaluation, or a meaningful project decision changes.
Commit after every important working step.
Do not skip ahead.
```

4. Let the implementation evolve only when evaluation or a clear product requirement justifies it.

## Files

- `AGENTS.md` — main coding-agent instructions.
- `docs/PROJECT_SPEC.md` — product scope and architecture.
- `docs/BUILD_PLAN.md` — ordered implementation phases and commit gates.
- `docs/EVALUATION.md` — benchmark and scoring rules.
- `docs/CHANGELOG.md` — decision/experiment narrative.
- `docs/REPRODUCTION.md` — clean-environment run instructions.

The goal is to keep the build small, evidence-driven, easy to review, and easy to reproduce.
