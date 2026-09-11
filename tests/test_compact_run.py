from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "compact_run.py"


class CompactRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)

    def command(self, name: str, lines: int, exit_code: int = 0) -> Path:
        path = self.root / name
        path.write_text(
            "import sys\n"
            f"for number in range({lines}):\n"
            "    print(f'line-{number}')\n"
            f"sys.exit({exit_code})\n",
            encoding="utf-8",
        )
        return path

    def run_script(self, command: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--", sys.executable, str(command)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def log_from(self, result: subprocess.CompletedProcess[str]) -> Path:
        match = re.search(r"^full-log: (.+)$", result.stdout, re.MULTILINE)
        self.assertIsNotNone(match)
        path = Path(match.group(1).strip())
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def test_success_small_output_and_integral_log(self) -> None:
        result = self.run_script(self.command("success.py", 3), "--success-lines", "5")
        log = self.log_from(result)

        self.assertEqual(result.returncode, 0)
        self.assertNotIn("omitted", result.stdout)
        self.assertEqual(log.read_text(encoding="utf-8").splitlines(), [
            "line-0",
            "line-1",
            "line-2",
        ])

    def test_success_large_output_is_tail_bounded(self) -> None:
        result = self.run_script(self.command("large.py", 20), "--success-lines", "3")

        self.assertEqual(result.returncode, 0)
        self.assertIn("omitted 17 lines; showing tail", result.stdout)
        self.assertIn("line-17", result.stdout)
        self.assertIn("line-19", result.stdout)
        self.assertNotIn("line-0\n", result.stdout)
        log_lines = self.log_from(result).read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(log_lines), 20)

    def test_failure_preserves_exit_code_head_tail_and_log(self) -> None:
        result = self.run_script(
            self.command("failure.py", 12, 7),
            "--failure-head-lines",
            "2",
            "--failure-tail-lines",
            "3",
        )
        log = self.log_from(result)

        self.assertEqual(result.returncode, 7)
        self.assertIn("exit: 7", result.stdout)
        self.assertIn("line-0", result.stdout)
        self.assertIn("line-1", result.stdout)
        self.assertIn("omitted 7 lines", result.stdout)
        self.assertNotIn("line-5", result.stdout)
        self.assertIn("line-9", result.stdout)
        self.assertIn("line-11", result.stdout)
        self.assertEqual(len(log.read_text(encoding="utf-8").splitlines()), 12)

    def test_failure_small_output_is_not_duplicated(self) -> None:
        result = self.run_script(
            self.command("small_failure.py", 4, 2),
            "--failure-head-lines",
            "3",
            "--failure-tail-lines",
            "3",
        )

        self.assertEqual(result.returncode, 2)
        self.assertNotIn("omitted", result.stdout)
        for number in range(4):
            self.assertEqual(result.stdout.count(f"line-{number}"), 1)
        self.log_from(result)

    def test_failure_lines_remains_a_compatibility_alias(self) -> None:
        result = self.run_script(
            self.command("alias.py", 8, 1),
            "--failure-head-lines",
            "1",
            "--failure-lines",
            "2",
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("omitted 5 lines", result.stdout)
        self.assertIn("line-0", result.stdout)
        self.assertIn("line-7", result.stdout)
        self.log_from(result)


if __name__ == "__main__":
    unittest.main()
