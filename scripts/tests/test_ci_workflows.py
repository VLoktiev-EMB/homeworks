"""Prove the LFS-pointer guard's behaviour and the two workflow contracts.

The guard is behaviour, not text: `check_lfs_pointers.sh` is executed against a
temporary directory so a clean tree, an empty file, a real pointer, a missing
directory and a symlink each have an observed exit status. Grepping `docs.yml`
for the command would only prove that the string exists, so the workflow
assertions here are deliberately limited to the names and commands the YAML must
carry; whether the guard works is proven above by running it.

The suite is stdlib-only (04/D-14): it imports neither PyYAML nor jsonschema and
reads the workflows as plain text.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "scripts" / "ci" / "check_lfs_pointers.sh"
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
GENERATED_VIEWS = WORKFLOWS / "generated-views.yml"
DOCS = WORKFLOWS / "docs.yml"

POINTER = "version https://git-lfs.github.com/spec/v1\noid sha256:" + "0" * 64 + "\nsize 42\n"
TIMEOUT = 30


class LfsPointerGuardTests(unittest.TestCase):
    """The guard's exit status, not the workflow's spelling of it."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def run_guard(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(GUARD), *args],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )

    def test_a_clean_tree_exits_zero(self) -> None:
        (self.root / "index.html").write_text("<html></html>\n", encoding="utf-8")
        result = self.run_guard(str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_an_empty_file_exits_zero(self) -> None:
        (self.root / "empty.png").write_bytes(b"")
        result = self.run_guard(str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_pointer_exits_one_and_names_the_file(self) -> None:
        pointer = self.root / "images" / "board.png"
        pointer.parent.mkdir()
        pointer.write_text(POINTER, encoding="utf-8")
        result = self.run_guard(str(self.root))
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(str(pointer), result.stderr)

    def test_a_missing_directory_exits_two(self) -> None:
        result = self.run_guard(str(self.root / "missing"))
        self.assertEqual(result.returncode, 2, result.stderr)

    def test_a_symlink_is_not_followed(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "pointer.png").write_text(POINTER, encoding="utf-8")
        site = self.root / "site"
        site.mkdir()
        (site / "link.png").symlink_to(outside / "pointer.png")
        result = self.run_guard(str(site))
        self.assertEqual(result.returncode, 0, result.stderr)


class WorkflowTextTests(unittest.TestCase):
    """The names and commands the YAML must carry; behaviour lives above."""

    def test_generated_views_names_the_check_command(self) -> None:
        text = GENERATED_VIEWS.read_text(encoding="utf-8")
        self.assertIn("python scripts/gen_views.py --all --check", text)

    def test_docs_builds_strictly_in_a_named_step(self) -> None:
        text = DOCS.read_text(encoding="utf-8")
        self.assertIn("Build the site with warnings as errors", text)
        self.assertIn("mkdocs build --strict", text)

    def test_docs_runs_the_lfs_guard_on_the_site_directory(self) -> None:
        text = DOCS.read_text(encoding="utf-8")
        self.assertIn("bash scripts/ci/check_lfs_pointers.sh site", text)


if __name__ == "__main__":
    unittest.main()
