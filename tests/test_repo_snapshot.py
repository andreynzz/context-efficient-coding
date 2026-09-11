from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "repo_snapshot.py"


class RepoSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        if not shutil.which("git"):
            self.skipTest("git is required")
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.repo = Path(self.temp_dir.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "test")
        (self.repo / "AGENTS.md").write_text("root rules", encoding="utf-8")
        (self.repo / "tracked.txt").write_text("clean", encoding="utf-8")
        self.git("add", ".")
        self.git(
            "-c",
            "user.name=Test User",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "fixture",
        )

    def git(self, *args: str) -> None:
        subprocess.run(
            ["git", *args],
            cwd=self.repo,
            check=True,
            capture_output=True,
            text=True,
        )

    def snapshot(self, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=cwd or self.repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_clean_git_repo_root_agent_and_no_markers(self) -> None:
        result = self.snapshot()

        self.assertEqual(result.returncode, 0)
        self.assertIn("branch: test", result.stdout)
        self.assertIn("changes: 0", result.stdout)
        self.assertIn("AGENTS.md (10 B)", result.stdout)
        self.assertIn("markers: none detected", result.stdout)

    def test_modified_worktree(self) -> None:
        (self.repo / "tracked.txt").write_text("modified", encoding="utf-8")

        result = self.snapshot()

        self.assertEqual(result.returncode, 0)
        self.assertIn("changes: 1", result.stdout)
        self.assertIn("M tracked.txt", result.stdout)

    def test_nested_chain_accumulates_and_override_wins(self) -> None:
        nested = self.repo / "src" / "module"
        nested.mkdir(parents=True)
        (nested / "AGENTS.md").write_text("ignored", encoding="utf-8")
        (nested / "AGENTS.override.md").write_text("override rules", encoding="utf-8")

        result = self.snapshot(nested)
        override_path = str(Path("src") / "module" / "AGENTS.override.md")
        regular_path = str(Path("src") / "module" / "AGENTS.md")

        self.assertEqual(result.returncode, 0)
        self.assertIn("project AGENTS chain: 24 B", result.stdout)
        self.assertIn(override_path, result.stdout)
        self.assertNotIn(regular_path, result.stdout)

    def test_git_status_items_are_limited(self) -> None:
        for number in range(30):
            (self.repo / f"untracked-{number:02}.txt").write_text("x", encoding="utf-8")

        result = self.snapshot()
        shown = [line for line in result.stdout.splitlines() if line.startswith("  ??")]

        self.assertEqual(result.returncode, 0)
        self.assertIn("changes: 30", result.stdout)
        self.assertEqual(len(shown), 24)
        self.assertIn("... +6 more", result.stdout)


if __name__ == "__main__":
    unittest.main()
