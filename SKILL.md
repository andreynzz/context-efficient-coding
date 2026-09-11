---
name: context-efficient-coding
description: Minimize unnecessary Codex context, tool output, rereads, and response tokens while preserving correctness, completeness, and verification. Use for software implementation, debugging, refactoring, code review, testing, and repository exploration, especially during long coding sessions.
---

# Context-Efficient Coding

Reduce wasted context without weakening the work.

## Priorities

1. Correctness.
2. Completeness.
3. Verification.
4. Context efficiency.
5. Output efficiency.

Never save tokens by guessing, skipping necessary investigation or tests, weakening error handling, or leaving work incomplete.

## Protocol

Resolve helper paths relative to this skill directory and run them with Python 3.

### Search -> Slice -> Read -> Expand

- Search for the relevant symbol, path, reference, call site, or error before opening large files. Prefer `rg -n`, targeted diffs, and narrow searches over repository dumps.
- Read the smallest region that can answer the question; expand only when evidence requires more context. Whole-file reads are fine when the file is small or its relationships matter.
- Reuse established facts. Do not reread unchanged regions unless a new question, edit, or failed verification makes it useful.
- After edits, prefer `git diff -- <path>` over rereading the file.
- When a compact state summary is useful, run `<python3> <skill-dir>/scripts/repo_snapshot.py` once and rerun only after a material state change.

### Commands and verification

- Use `<python3> <skill-dir>/scripts/smart_read.py` for bounded regions or regex context when useful.
- During iteration, run the smallest focused check that can falsify the change.
- Before completion, run project-required checks and validation broad enough to cover the changed behavior. Never claim an unexecuted test passed.
- For noisy commands, use `<python3> <skill-dir>/scripts/compact_run.py -- <command> ...`. It preserves the full log, prints a bounded preview, and returns the command's exit code.
- If a preview lacks evidence, search or slice the saved log instead of rerunning an expensive command merely to recover output. Do not truncate the only useful diagnostic evidence.

### Communication

- Avoid narrating routine searches, reads, edits, and commands.
- Use a brief checkpoint when user steering matters, such as for destructive work, migrations, public-contract or security changes, major architecture choices, large scope expansion, or consequential ambiguity.
- Keep the final response to what changed or was found, verification performed, and any important remaining risk. Do not paste full files, diffs, logs, or a work diary unless asked.

## Conditional guidance

Use the protocol above for ordinary tasks.

For long, cross-module, architectural, migration, or difficult debugging work, read `references/heavy-work.md` before broad exploration.

For efficiency measurement or tuning, read `references/benchmark.md` and follow its A/B protocol.
