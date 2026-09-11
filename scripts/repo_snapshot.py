#!/usr/bin/env python3
"""Print a compact repository/context snapshot for Codex without dumping files."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

DEFAULT_PROJECT_DOC_LIMIT = 32 * 1024
MAX_STATUS_LINES = 24
PROJECT_MARKERS = (
    "package.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "package-lock.json",
    "pyproject.toml",
    "requirements.txt",
    "uv.lock",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "go.mod",
    "Cargo.toml",
    "composer.json",
)
AGENT_NAMES = ("AGENTS.override.md", "AGENTS.md")


def run_git(*args: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, proc.stdout.strip()


def project_root(cwd: Path) -> Path:
    code, out = run_git("rev-parse", "--show-toplevel")
    return Path(out).resolve() if code == 0 and out else cwd.resolve()


def first_nonempty_agent(directory: Path) -> Path | None:
    for name in AGENT_NAMES:
        candidate = directory / name
        if candidate.is_file() and candidate.stat().st_size > 0:
            return candidate
    return None


def agent_chain(root: Path, cwd: Path) -> list[Path]:
    try:
        rel = cwd.resolve().relative_to(root.resolve())
    except ValueError:
        return [p for p in [first_nonempty_agent(cwd)] if p]

    dirs = [root]
    current = root
    for part in rel.parts:
        current = current / part
        dirs.append(current)

    chain: list[Path] = []
    for directory in dirs:
        found = first_nonempty_agent(directory)
        if found:
            chain.append(found)
    return chain


def fmt_bytes(value: int) -> str:
    if value < 1024:
        return f"{value} B"
    return f"{value / 1024:.1f} KiB"


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    cwd = Path.cwd().resolve()
    root = project_root(cwd)
    code, branch = run_git("branch", "--show-current")
    if code != 0 or not branch:
        _, branch = run_git("rev-parse", "--short", "HEAD")
        branch = branch or "n/a"

    print(f"repo-root: {root}")
    print(f"cwd: {cwd}")
    print(f"branch: {branch}")

    _, status = run_git("status", "--short", "--untracked-files=normal")
    status_lines = status.splitlines() if status else []
    print(f"changes: {len(status_lines)}")
    for line in status_lines[:MAX_STATUS_LINES]:
        print(f"  {line}")
    if len(status_lines) > MAX_STATUS_LINES:
        print(f"  ... +{len(status_lines) - MAX_STATUS_LINES} more")

    markers = [name for name in PROJECT_MARKERS if (root / name).exists()]
    print("markers: " + (", ".join(markers) if markers else "none detected"))

    chain = agent_chain(root, cwd)
    total = sum(path.stat().st_size for path in chain)
    print(f"project AGENTS chain: {fmt_bytes(total)} / {fmt_bytes(DEFAULT_PROJECT_DOC_LIMIT)}")
    for path in chain:
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        print(f"  {rel} ({fmt_bytes(path.stat().st_size)})")
    if not chain:
        print("  none")

    ratio = total / DEFAULT_PROJECT_DOC_LIMIT
    if ratio >= 0.875:
        print("AGENTS status: HIGH RISK")
    elif ratio >= 0.75:
        print("AGENTS status: WARNING")
    elif ratio >= 0.5:
        print("AGENTS status: REVIEW")
    else:
        print("AGENTS status: OK")

    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    global_agent = first_nonempty_agent(codex_home)
    if global_agent:
        print(f"global AGENTS: {global_agent.name} ({fmt_bytes(global_agent.stat().st_size)})")
    else:
        print("global AGENTS: none")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
