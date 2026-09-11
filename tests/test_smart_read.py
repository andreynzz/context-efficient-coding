from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "smart_read.py"


class SmartReadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)

    def run_script(self, file: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(file), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def write_lines(self, name: str, count: int) -> Path:
        path = self.root / name
        path.write_text(
            "\n".join(f"line {number}" for number in range(1, count + 1)),
            encoding="utf-8",
        )
        return path

    def test_lines_respects_max_lines_and_reports_truncation(self) -> None:
        result = self.run_script(
            self.write_lines("large.txt", 30),
            "--lines",
            "5:15",
            "--max-lines",
            "3",
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("5 | line 5", result.stdout)
        self.assertIn("7 | line 7", result.stdout)
        self.assertNotIn("8 | line 8", result.stdout)
        self.assertIn("truncated; showed 3 of 11 requested lines", result.stdout)

    def test_regex_with_one_match(self) -> None:
        path = self.root / "one.txt"
        path.write_text("before\ncreateUser\nafter", encoding="utf-8")

        result = self.run_script(path, "--match", "createUser", "--context", "0")

        self.assertEqual(result.returncode, 0)
        self.assertIn("matches: 1", result.stdout)
        self.assertIn("2 | createUser", result.stdout)

    def test_multiple_matches_merge_overlapping_ranges(self) -> None:
        path = self.write_lines("overlap.txt", 8)
        path.write_text(
            path.read_text(encoding="utf-8")
            .replace("line 3", "line 3 hit")
            .replace("line 5", "line 5 hit"),
            encoding="utf-8",
        )

        result = self.run_script(path, "--match", "hit", "--context", "2")

        self.assertEqual(result.returncode, 0)
        self.assertIn("matches: 2", result.stdout)
        self.assertEqual(result.stdout.count("4 | line 4"), 1)

    def test_ignore_case(self) -> None:
        path = self.root / "case.txt"
        path.write_text("CreateUser\ncreateuser", encoding="utf-8")

        result = self.run_script(path, "--match", "CREATEUSER", "--ignore-case")

        self.assertEqual(result.returncode, 0)
        self.assertIn("matches: 2", result.stdout)

    def test_no_match_returns_one(self) -> None:
        result = self.run_script(
            self.write_lines("none.txt", 3), "--match", "missing"
        )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.strip(), "no matches")

    def test_invalid_regex_returns_two(self) -> None:
        result = self.run_script(self.write_lines("invalid.txt", 3), "--match", "[")

        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid regex", result.stderr)

    def test_empty_file_has_explicit_results(self) -> None:
        path = self.root / "empty.txt"
        path.touch()

        match_result = self.run_script(path, "--match", "anything")
        range_result = self.run_script(path, "--lines", "1:1")

        self.assertEqual(match_result.returncode, 1)
        self.assertEqual(match_result.stdout.strip(), "no matches")
        self.assertEqual(range_result.returncode, 2)
        self.assertIn("file is empty", range_result.stderr)


if __name__ == "__main__":
    unittest.main()
