#!/usr/bin/env python3
"""Run a noisy command once, save full output, and print a bounded preview."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_SUCCESS_LINES = 35
DEFAULT_FAILURE_LINES = 140


def log_path() -> Path:
    root = Path(tempfile.gettempdir()) / "codex-context-efficient"
    root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    return root / f"command-{stamp}-{os.getpid()}.log"


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--success-lines", type=int, default=DEFAULT_SUCCESS_LINES)
    parser.add_argument("--failure-lines", type=int, default=DEFAULT_FAILURE_LINES)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("provide a command after --")
    if args.success_lines < 0 or args.failure_lines < 1:
        parser.error("invalid preview line limits")

    started = time.monotonic()
    path = log_path()
    try:
        with path.open("w", encoding="utf-8", errors="replace", newline="") as log:
            proc = subprocess.Popen(
                command,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=os.environ.copy(),
            )
            returncode = proc.wait()
    except FileNotFoundError:
        path.unlink(missing_ok=True)
        print(f"command not found: {command[0]}", file=sys.stderr)
        return 127
    except OSError as exc:
        path.unlink(missing_ok=True)
        print(f"failed to run command: {exc}", file=sys.stderr)
        return 126

    elapsed = time.monotonic() - started
    preview_count = args.success_lines if returncode == 0 else args.failure_lines
    tail: deque[str] = deque(maxlen=preview_count)
    line_count = 0
    with path.open(encoding="utf-8", errors="replace") as log:
        for line in log:
            line_count += 1
            if preview_count:
                tail.append(line.rstrip("\r\n"))

    print(f"exit: {returncode}; duration: {elapsed:.1f}s; output-lines: {line_count}")
    print(f"full-log: {path}")

    if tail:
        if line_count > len(tail):
            print(f"... showing last {len(tail)} of {line_count} lines ...")
        print("\n".join(tail))

    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
