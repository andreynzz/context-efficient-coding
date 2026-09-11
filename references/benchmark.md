# Efficiency benchmark

Use this only when evaluating or tuning the skill.

## Goal

Measure usage reduction without accepting lower engineering quality.

## Profiles

Test comparable real tasks in three groups:

- LIGHT: small bug fixes, narrow reviews, small features.
- NORMAL: complete features, moderate debugging, moderate refactors.
- HEAVY: broad refactors, difficult failures, migrations, cross-module work.

Prefer at least 3 tasks per group; 5 or more per group is better.

## A/B method

For each task, record the Codex usage/status immediately before and after the task when that information is available. Run one version without this skill and one with it on equivalent starting states. Alternate A/B order when practical so task familiarity does not always favor the skill.

Do not compare two runs on a working tree where the first run's solution remains present.

Record:

- profile and task identifier;
- elapsed active work time;
- usage/status delta available from Codex;
- number of tool/command invocations if visible;
- repeated file reads noticed;
- broad vs focused test executions;
- correctness result;
- tests/checks passed;
- reviewer/user acceptance;
- regressions or rework required.

## Quality gate

Reject an optimization if it reduces usage but causes any systematic increase in:

- incorrect implementations;
- missed requirements;
- unverified claims;
- regressions;
- user intervention needed to recover context;
- time spent rerunning commands because useful evidence was truncated.

## Tuning order

Tune one variable at a time in this order:

1. final-response verbosity;
2. redundant narration;
3. broad repository reads;
4. rereads;
5. noisy tool output;
6. test breadth during iteration;
7. skill catalog / MCP exposure;
8. global Codex token limits only after evidence justifies them.

Keep model reasoning effort unchanged while benchmarking this skill unless the experiment is explicitly about reasoning effort.
