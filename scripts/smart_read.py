#!/usr/bin/env python3
"""Read a bounded file slice or regex match context with line numbers."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_MAX_LINES = 220
DEFAULT_CONTEXT = 30


def parse_range(value: str, total: int) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)?:(\d+)?", value)
    if not match:
        raise ValueError("range must be START:END, e.g. 120:220")
    start = int(match.group(1) or 1)
    end = int(match.group(2) or total)
    if start < 1 or end < start:
        raise ValueError("invalid line range")
    if start > total:
        raise ValueError(f"range starts after end of file ({total} lines)")
    return start, min(end, total)


def emit(lines: list[str], ranges: list[tuple[int, int]], max_lines: int) -> None:
    merged: list[tuple[int, int]] = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    requested_lines = sum(end - start + 1 for start, end in merged)
    remaining = max_lines
    emitted = 0
    for idx, (start, end) in enumerate(merged):
        if remaining <= 0:
            break
        allowed_end = min(end, start + remaining - 1)
        if idx:
            print("...")
        for line_no in range(start, allowed_end + 1):
            print(f"{line_no:>6} | {lines[line_no - 1]}")
        count = allowed_end - start + 1
        remaining -= count
        emitted += count
        if allowed_end < end:
            break
    if emitted < requested_lines:
        print(f"... truncated; showed {emitted} of {requested_lines} requested lines")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--lines", help="1-based START:END")
    mode.add_argument("--match", help="Python regex; prints bounded context around matches")
    parser.add_argument("--context", type=int, default=DEFAULT_CONTEXT)
    parser.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    parser.add_argument("--ignore-case", action="store_true")
    args = parser.parse_args()

    if args.max_lines < 1 or args.context < 0:
        parser.error("--max-lines must be positive and --context non-negative")

    try:
        text = args.file.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.lines:
        lines = text.splitlines()
        if not lines:
            print("error: file is empty", file=sys.stderr)
            return 2
        try:
            start, end = parse_range(args.lines, len(lines))
        except ValueError as exc:
            parser.error(str(exc))
        emit(lines, [(start, end)], args.max_lines)
        return 0

    flags = re.IGNORECASE if args.ignore_case else 0
    try:
        pattern = re.compile(args.match, flags)
    except re.error as exc:
        parser.error(f"invalid regex: {exc}")

    lines = text.splitlines()
    if not lines:
        print("no matches")
        return 1

    matches = [i + 1 for i, line in enumerate(lines) if pattern.search(line)]
    if not matches:
        print("no matches")
        return 1

    ranges = [
        (max(1, line_no - args.context), min(len(lines), line_no + args.context))
        for line_no in matches
    ]
    print(f"matches: {len(matches)}; file lines: {len(lines)}")
    emit(lines, ranges, args.max_lines)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
