---
name: context-efficient-coding
description: Minimize unnecessary Codex context, tool output, rereads, and response tokens while preserving correctness, completeness, and verification. Use for software implementation, debugging, refactoring, code review, testing, and repository exploration, especially during long coding sessions.
---

# Context-Efficient Coding

Optimize the work, not the intelligence used to do it.

## Priority order

1. Correctness.
2. Completeness.
3. Verification.
4. Context efficiency.
5. Output efficiency.

Never save tokens by guessing, skipping required investigation, weakening tests, omitting error handling, or leaving requested work incomplete.

## Working protocol

Resolve helper script paths relative to this skill directory, not the target repository. Invoke the resolved script path with an available Python 3 interpreter.

### 1. Establish only the context you need

- Reuse facts already established in the current task. Do not rediscover them.
- Do not explore the repository broadly unless the task requires broad understanding.
- When repository state is unknown and materially useful, run `<python3> <skill-dir>/scripts/repo_snapshot.py` once from the target working directory. Rerun only if branch, working tree, or working directory materially changes.
- Search for symbols, paths, references, and call sites before opening files. Prefer `rg -n`, targeted `git diff`, and narrow directory searches over directory dumps.
- Prefer `git diff -- <path>` after edits instead of rereading the whole file.

### 2. Search -> Slice -> Read -> Expand

- Locate relevant regions first.
- Read the smallest contiguous region that can answer the question.
- Expand only when evidence shows more context is necessary.
- Prefer `<python3> <skill-dir>/scripts/smart_read.py <file> --match <regex>` or `--lines START:END` for large files.
- Reading a whole file is fine when it is small or when relationships across the file are necessary.
- Do not reread an unchanged region already inspected unless a new question, changed file, or failed verification makes rereading useful.

### 3. Keep command output bounded without hiding evidence

- Use the narrowest relevant command while iterating: focused test, package, module, file, symbol, or lint target.
- Avoid repeatedly running a full suite when a focused check answers the current iteration.
- Run the broader checks required by project instructions and task risk before completion.
- For commands expected to be noisy, prefer `<python3> <skill-dir>/scripts/compact_run.py -- <command> ...`. It preserves the complete output in a temporary log, prints a bounded preview, and returns the original exit code.
- If the bounded preview is insufficient, inspect the saved log with search or `smart_read.py`; do not rerun the expensive command merely to recover output.
- Do not truncate output when doing so could conceal the only evidence needed to diagnose a failure.

### 4. Communicate adaptively

For normal work, avoid operational narration such as announcing every read, search, edit, or test. Work quietly and report the result concisely.

Use a brief checkpoint only when it materially helps the user steer the task, especially before or after discovering:

- a destructive or difficult-to-reverse action;
- a schema/data migration;
- a breaking API or public-contract change;
- a security/authentication-sensitive change;
- a major architectural choice with meaningful alternatives;
- scope expansion across many modules;
- an ambiguity that changes product behavior.

A checkpoint should state the decision/risk and the intended path, not recap routine work.

### 5. Verify proportionally

- During iteration, prefer the smallest check that can falsify the current change.
- Before completion, run all checks required by repository instructions plus enough broader validation to cover the changed behavior.
- Never claim a test passed unless it was actually run successfully.
- If verification cannot be run, say exactly what remains unverified and why.

### 6. Finish compactly

Default final response should contain only what is useful to the user:

- what changed or what was found;
- verification performed and its result;
- important risk/blocker only if one remains.

Do not paste code, diffs, command logs, or a chronological work diary unless the user asks for them.

## Task modes

Use the protocol above for ordinary tasks.

For long, cross-module, architecture-heavy, migration-heavy, or unusually difficult debugging work, read `references/heavy-work.md` before broad exploration.

When the user asks to measure or tune this skill's efficiency, read `references/benchmark.md` and follow the A/B protocol there.
