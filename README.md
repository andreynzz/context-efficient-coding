# Context Efficient Coding

A Codex skill that reduces unnecessary context, tool output, rereads, and response tokens without compromising correctness, completeness, or verification.

It is designed for implementation, debugging, refactoring, code review, testing, and repository exploration during long coding sessions.

## Why

The skill prioritizes work quality over efficiency:

1. Correctness
2. Completeness
3. Verification
4. Context efficiency
5. Output efficiency

It saves context by narrowing investigation and retaining useful evidence—not by guessing, lowering reasoning effort, or skipping required tests.

## Install

Requirements:

- Codex
- Python 3.10 or later for the optional helper scripts

### macOS and Linux

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/andreynzz/context-efficient-coding.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/context-efficient-coding"
```

### Windows PowerShell

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
New-Item -ItemType Directory -Force -Path (Join-Path $codexHome "skills")
git clone https://github.com/andreynzz/context-efficient-coding.git `
  (Join-Path $codexHome "skills\context-efficient-coding")
```

Start a new Codex task after installing so the skill can be discovered. It permits implicit invocation; invoke it explicitly with `$context-efficient-coding` when you want to make the intent clear.

## How it works

The central inspection protocol is:

```text
Search -> Slice -> Read -> Expand only if necessary
```

Before opening a large file, the skill searches for the relevant symbol, error, route, call site, or reference; reads the likely region; and expands only when the evidence requires it. It favors `rg -n`, narrow diffs, and focused tests.

For difficult debugging, migrations, cross-module refactors, and long tasks, it loads the dedicated heavy-work protocol. Benchmark guidance is loaded only when evaluating or tuning the skill.

## Helper scripts

The scripts are optional, use only the Python standard library, make no network requests, and do not modify the target project. Resolve their path from the installed skill directory, then run them from the repository you are investigating.

| Helper | Purpose | Example |
| --- | --- | --- |
| `repo_snapshot.py` | Summarizes the repository, working tree, project markers, and active `AGENTS.md` chain without dumping file contents. | `python3 <skill-dir>/scripts/repo_snapshot.py` |
| `smart_read.py` | Prints numbered file regions or regex-match context with explicit truncation. | `python3 <skill-dir>/scripts/smart_read.py src/app.py --match 'createUser' --context 30` |
| `compact_run.py` | Retains a noisy command's full log; previews the tail on success and the head plus tail on failure. | `python3 <skill-dir>/scripts/compact_run.py -- npm test` |

On Windows, use an available Python 3 command such as `py -3` instead of `python3` when appropriate.

## Guidance included

- [Heavy-work protocol](references/heavy-work.md) for difficult debugging, migrations, architecture work, and cross-module refactors.
- [Benchmark protocol](references/benchmark.md) for LIGHT, NORMAL, and HEAVY A/B evaluations. Optimizations are rejected if they reduce quality, verification, or total time to a correct outcome.

## Test

Python 3.10 remains the minimum because the helpers use modern type-union syntax without compatibility shims. Run the same compile check and standard-library test suite used by CI:

```bash
python3 -m py_compile scripts/repo_snapshot.py scripts/smart_read.py scripts/compact_run.py
python3 -m unittest discover -s tests -v
```

GitHub Actions runs these checks on pushes and pull requests targeting `main`. Use the script help output to see all options:

```bash
python3 scripts/smart_read.py --help
python3 scripts/compact_run.py --help
```

## Contributing

Keep the entrypoint focused: universal rules belong in `SKILL.md`; conditional workflows belong in `references/`; deterministic, reusable behavior belongs in `scripts/`. Test every change to a helper script and avoid adding dependencies unless they provide a concrete benefit.

## License

Distributed under the [MIT License](LICENSE).
