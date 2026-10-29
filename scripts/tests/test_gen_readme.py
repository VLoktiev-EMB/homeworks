"""Behavioural tests for scripts/gen_readme.py.

Every test drives the real script through `uv run` against a disposable
repository root built by `scripts.tests.temp_root`, never against the
repository itself. The discovery interpreter has no PyYAML, so this module
imports neither the generator nor any module that pulls it in: the process
boundary is the subject, not an internal function.

The coverage is deliberately the behaviour that is otherwise unverified: row
order and links, the report cell and its `none` fallback, separator escaping,
the empty message, every exit-2 marker and environment case, check-mode drift
without a write, idempotency, prose preservation outside the region, and an
invalid document leaving the README unchanged.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.tests import temp_root

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = "scripts/gen_readme.py"

BEGIN = "<!-- BEGIN GENERATED: homeworks -->"
END = "<!-- END GENERATED -->"
EMPTY_MESSAGE = "No homework assignments published yet."
TABLE_HEADER = "| ID | Project | Board | Framework | Status | Report |"

PROSE_BEFORE = "# Fixture README\n\nAuthored intro.\n\n## Homeworks\n\n"
PROSE_AFTER = "\n\n## Repository rules\n\nAuthored outro.\n"


def run_gen_readme(*args, timeout=180):
    """Run the generator from the repository root and return the result."""
    if shutil.which("uv") is None:
        raise AssertionError("uv is not available; the generator cannot be driven")
    return subprocess.run(
        ["uv", "run", SCRIPT, *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


class GenReadmeTestCase(unittest.TestCase):
    """Shared fixture: a synthetic root plus a README carrying both markers."""

    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp_dir.cleanup)
        self.root = Path(self._temp_dir.name)
        temp_root.write_synthetic_root(self.root, homeworks=True)
        self.readme_path = self.root / "README.md"
        self.write_readme(PROSE_BEFORE + BEGIN + "\n\n" + END + PROSE_AFTER)

    def write_readme(self, text: str) -> None:
        self.readme_path.write_text(text, encoding="utf-8")

    def read_text(self) -> str:
        return self.readme_path.read_text(encoding="utf-8")

    def read_bytes(self) -> bytes:
        return self.readme_path.read_bytes()

    def region(self) -> str:
        text = self.read_text()
        start = text.index(BEGIN) + len(BEGIN)
        return text[start : text.index(END)]

    def run_generator(self, *args, timeout=180):
        return run_gen_readme("--dir", str(self.root), *args, timeout=timeout)

    def rewrite_homework(self, homework_id: str, transform) -> None:
        path = self.root / "homeworks" / homework_id / "homework.yaml"
        path.write_text(transform(path.read_text(encoding="utf-8")), encoding="utf-8")


class TableContentTests(GenReadmeTestCase):
    def test_lists_fixtures_in_sorted_order_with_links_and_metadata(self) -> None:
        completed = self.run_generator()
        self.assertEqual(completed.returncode, 0, completed.stderr)

        region = self.region()
        alpha = region.index("[Alpha](homeworks/1_3-alpha/)")
        beta = region.index("[Beta](homeworks/1_4-beta/)")
        self.assertLess(alpha, beta)
        self.assertIn("esp32-s3-devkitc-1", region)
        self.assertIn("arduino", region)
        self.assertIn("espidf", region)
        self.assertIn("in-progress", region)

    def test_report_cell_links_the_declared_path(self) -> None:
        completed = self.run_generator()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("[report](homeworks/1_3-alpha/report.md)", self.region())

    def test_missing_report_block_renders_none(self) -> None:
        def drop_report(text: str) -> str:
            lines = text.splitlines(keepends=True)
            kept = []
            dropping = False
            for line in lines:
                if line.startswith("report:"):
                    dropping = True
                    continue
                if dropping and line.startswith("  "):
                    continue
                dropping = False
                kept.append(line)
            return "".join(kept)

        self.rewrite_homework("1_3-alpha", drop_report)
        completed = self.run_generator()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        row = next(
            line for line in self.region().splitlines() if "1_3-alpha" in line
        )
        self.assertTrue(row.endswith("| none |"), row)

    def test_pipe_in_title_is_escaped(self) -> None:
        self.rewrite_homework(
            "1_3-alpha",
            lambda text: text.replace('title: "Alpha"', 'title: "Alpha | Beta"'),
        )
        completed = self.run_generator()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("[Alpha \\| Beta](homeworks/1_3-alpha/)", self.region())
        row = next(
            line for line in self.region().splitlines() if "1_3-alpha" in line
        )
        self.assertEqual(row.count(" | "), TABLE_HEADER.count(" | "))

    def test_empty_homeworks_renders_the_empty_message(self) -> None:
        with tempfile.TemporaryDirectory() as other:
            root = Path(other)
            temp_root.write_synthetic_root(root, homeworks=False)
            readme = root / "README.md"
            readme.write_text(
                PROSE_BEFORE + BEGIN + "\n\n" + END + PROSE_AFTER, encoding="utf-8"
            )

            completed = run_gen_readme("--dir", str(root))
            self.assertEqual(completed.returncode, 0, completed.stderr)
            text = readme.read_text(encoding="utf-8")
            self.assertIn(EMPTY_MESSAGE, text)
            self.assertNotIn(TABLE_HEADER, text)


class RegionBoundaryTests(GenReadmeTestCase):
    def test_absent_readme_exits_2_and_is_not_created(self) -> None:
        self.readme_path.unlink()
        completed = self.run_generator()
        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertFalse(self.readme_path.exists())

    def test_missing_begin_marker_exits_2_without_a_write(self) -> None:
        original = PROSE_BEFORE + "\n\n" + END + PROSE_AFTER
        self.write_readme(original)
        completed = self.run_generator()
        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertEqual(self.read_text(), original)

    def test_duplicate_begin_marker_exits_2_without_a_write(self) -> None:
        original = PROSE_BEFORE + BEGIN + "\n" + BEGIN + "\n" + END + PROSE_AFTER
        self.write_readme(original)
        completed = self.run_generator()
        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertEqual(self.read_text(), original)

    def test_end_marker_before_begin_exits_2_without_a_write(self) -> None:
        original = PROSE_BEFORE + END + "\n" + BEGIN + PROSE_AFTER
        self.write_readme(original)
        completed = self.run_generator()
        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertEqual(self.read_text(), original)


class WriteModeTests(GenReadmeTestCase):
    def test_write_replaces_the_region_and_preserves_prose(self) -> None:
        completed = self.run_generator()
        self.assertEqual(completed.returncode, 0, completed.stderr)

        text = self.read_text()
        self.assertTrue(text.startswith(PROSE_BEFORE))
        self.assertTrue(text.endswith(PROSE_AFTER))
        self.assertIn(TABLE_HEADER, self.region())

    def test_second_write_is_byte_identical(self) -> None:
        self.assertEqual(self.run_generator().returncode, 0)
        first = self.read_bytes()
        self.assertEqual(self.run_generator().returncode, 0)
        self.assertEqual(self.read_bytes(), first)

    def test_invalid_document_exits_1_and_leaves_readme_unchanged(self) -> None:
        original = self.read_bytes()
        self.rewrite_homework(
            "1_3-alpha",
            lambda text: text.replace("status: in-progress", "status: bogus"),
        )
        completed = self.run_generator()
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertEqual(self.read_bytes(), original)


class CheckModeTests(GenReadmeTestCase):
    def test_check_reports_drift_without_writing(self) -> None:
        original = self.read_bytes()
        completed = self.run_generator("--check")
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn("README.md: stale — run: uv run scripts/gen_readme.py", completed.stderr)
        self.assertEqual(self.read_bytes(), original)

    def test_check_is_clean_after_a_write(self) -> None:
        self.assertEqual(self.run_generator().returncode, 0)
        completed = self.run_generator("--check")
        self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
