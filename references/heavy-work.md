# Heavy-work protocol

Load this only for long, cross-module, migration-heavy, architecture-heavy, or difficult debugging tasks.

## Scope map before deep reads

Build a compact evidence map instead of opening many files immediately:

1. Identify the entry point or failing behavior.
2. Search for the primary symbol/API and its direct callers/callees.
3. Inspect relevant tests before expanding into implementation details when tests encode expected behavior.
4. Use `git diff --stat`, targeted history, or blame only when history is likely to resolve the current question.
5. Keep a small working set of files. Add a file only when it answers a concrete unresolved question.

If the current hypothesis is falsified, update the scope map instead of restarting repository exploration from scratch.

## Difficult debugging

Use an evidence ladder:

1. reproduce or inspect the concrete failure;
2. isolate the smallest failing path;
3. form one or a few explicit hypotheses;
4. gather evidence that can distinguish them;
5. patch only after the cause is sufficiently supported;
6. run focused regression coverage, then required broader validation.

Prefer inspecting an existing complete command log over rerunning the command. Search logs first for exception names, failed assertions, error codes, stack frames, and the first causal error rather than reading them linearly.

## Large changes

Partition the work into dependency-ordered slices that can be verified independently. Do not narrate every slice to the user.

Before a high-risk irreversible step, checkpoint only if user steering is materially useful. Otherwise keep executing.

After each slice, validate the narrow contract it changes. Run broader integration checks after the slices compose.

## Context hygiene

- Prefer summaries you derived from evidence over keeping many raw file regions active.
- Do not reopen unchanged files merely to regain confidence; search your current evidence first.
- If context becomes polluted by unrelated objectives, finish or checkpoint the current coherent objective rather than expanding the thread indefinitely.
- Do not force early compaction or lower reasoning effort merely to save usage unless the user explicitly chooses that trade-off.
