"""Tests for scripts/check_pr_templates.py.

The real-tree tests exercise the shipped contract end to end. Every negative
fixture copies the three templates into a temporary tree, mutates exactly one
property, and points the checker at the copy with ``--dir`` — the script's only
test seam.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import check_pr_templates

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_pr_templates.py"
TEMPLATES = REPO_ROOT / ".github" / "PULL_REQUEST_TEMPLATE"
NAMES = ("homework.md", "infra.md", "docs.md")

START = "<!-- pr-header:start -->"
END = "<!-- pr-header:end -->"
CHECKLIST = re.compile(r"^\s*-\s*\[[ xX]\]")
DOD_HEADING = re.compile(r"^##\s+Definition of Done\s*$", re.IGNORECASE)


def run_checker(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def combined(result: subprocess.CompletedProcess) -> str:
    return result.stdout + result.stderr


def git_status() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    ).stdout


class RealTreeTests(unittest.TestCase):
    """The shipped tree satisfies the contract the script enforces."""

    def test_real_tree_passes(self):
        result = run_checker()
        self.assertEqual(0, result.returncode, combined(result))
        self.assertIn("PASS: PR template contract satisfied", result.stdout)

    def test_each_template_carries_exactly_one_marker_pair(self):
        for name in NAMES:
            with self.subTest(template=name):
                data = (TEMPLATES / name).read_text(encoding="utf-8")
                self.assertEqual(1, data.count(START), name)
                self.assertEqual(1, data.count(END), name)

    def test_required_dod_items_present_per_type(self):
        keywords = {
            "homework.md": ["pio run", "native", "report", "provenance", "index", "simulation"],
            "infra.md": ["adr", "check_policy.py", "secret", "documentation"],
            "docs.md": ["link", "markdownlint", "duplicat"],
        }
        for name, words in keywords.items():
            text = (TEMPLATES / name).read_text(encoding="utf-8").lower()
            for word in words:
                with self.subTest(template=name, keyword=word):
                    self.assertIn(word, text, f"{name} is missing DoD item {word!r}")

    def test_no_required_row_demands_ai_disclosure(self):
        ai = re.compile(r"\bai\b|artificial intelligence", re.IGNORECASE)
        for name in NAMES:
            for line in (TEMPLATES / name).read_text(encoding="utf-8").splitlines():
                if not CHECKLIST.match(line):
                    continue
                lowered = line.lower()
                asks_for_disclosure = "disclos" in lowered or "assistance" in lowered
                with self.subTest(template=name, row=line):
                    self.assertFalse(
                        ai.search(line) and asks_for_disclosure,
                        f"{name} requires AI-assistance disclosure: {line!r}",
                    )

    def test_real_tree_has_no_default_template_at_any_supported_path(self):
        # Every folder GitHub reads a default template from, in the file shape
        # and in the ``PULL_REQUEST_TEMPLATE/default.md`` shape.
        self.assertEqual([], check_pr_templates.default_template_paths(REPO_ROOT))

    def test_second_run_is_identical_and_read_only(self):
        before = git_status()
        first = run_checker()
        second = run_checker()
        after = git_status()

        self.assertEqual(0, first.returncode, combined(first))
        self.assertEqual(0, second.returncode, combined(second))
        self.assertEqual(
            (first.returncode, first.stdout, first.stderr),
            (second.returncode, second.stdout, second.stderr),
        )
        self.assertEqual(before, after, "the checker modified the working tree")


class FixtureTests(unittest.TestCase):
    """Each contract violation fails closed in a synthetic tree."""

    def make_tree(self) -> tuple[Path, Path]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        dest = root / ".github" / "PULL_REQUEST_TEMPLATE"
        shutil.copytree(TEMPLATES, dest)
        return root, dest

    def test_header_mismatch_exits_1_and_names_file(self):
        root, dest = self.make_tree()
        target = dest / "infra.md"
        text = target.read_text(encoding="utf-8")
        self.assertIn("- **Type:**", text)
        target.write_text(text.replace("- **Type:**", "- **TYPE:**", 1), encoding="utf-8")

        result = run_checker("--dir", str(root))

        self.assertEqual(1, result.returncode, combined(result))
        self.assertIn("FAIL header", result.stdout)
        self.assertIn("infra.md", result.stdout)

    def test_empty_dod_section_exits_1(self):
        root, dest = self.make_tree()
        target = dest / "homework.md"
        kept = []
        in_dod = False
        for line in target.read_text(encoding="utf-8").splitlines():
            if DOD_HEADING.match(line):
                in_dod = True
            elif in_dod and CHECKLIST.match(line):
                continue
            kept.append(line)
        target.write_text("\n".join(kept) + "\n", encoding="utf-8")

        result = run_checker("--dir", str(root))

        self.assertEqual(1, result.returncode, combined(result))
        self.assertIn("FAIL definition-of-done", result.stdout)
        self.assertIn("homework.md", result.stdout)

    def test_missing_end_marker_exits_1(self):
        root, dest = self.make_tree()
        target = dest / "docs.md"
        target.write_text(
            target.read_text(encoding="utf-8").replace(END, ""), encoding="utf-8"
        )

        result = run_checker("--dir", str(root))

        self.assertEqual(1, result.returncode, combined(result))
        self.assertIn("docs.md", combined(result))
        self.assertIn("marker", combined(result).lower())

    def test_stray_default_template_exits_1(self):
        # The full GitHub lookup order: a ``pull_request_template.md`` and a
        # ``PULL_REQUEST_TEMPLATE/default.md`` in the repository root, ``docs/``
        # and ``.github/``, in any casing. A checker that misses one of these
        # exits 0 while GitHub stops showing the template chooser.
        fallback_paths = (
            "pull_request_template.md",
            "PULL_REQUEST_TEMPLATE.md",
            "PULL_REQUEST_TEMPLATE/default.md",
            "PULL_REQUEST_TEMPLATE/DEFAULT.md",
            "docs/pull_request_template.md",
            "docs/PULL_REQUEST_TEMPLATE.md",
            "docs/PULL_REQUEST_TEMPLATE/default.md",
            ".github/pull_request_template.md",
            ".github/PULL_REQUEST_TEMPLATE/default.md",
            ".github/PULL_REQUEST_TEMPLATE/DEFAULT.md",
        )
        for relative in fallback_paths:
            with self.subTest(path=relative):
                root, _ = self.make_tree()
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("default\n", encoding="utf-8")

                result = run_checker("--dir", str(root))

                self.assertEqual(1, result.returncode, combined(result))
                self.assertIn("FAIL default-template", result.stdout)
                self.assertIn(relative, result.stdout)

    def test_missing_template_file_exits_2(self):
        root, dest = self.make_tree()
        (dest / "docs.md").unlink()

        result = run_checker("--dir", str(root))

        self.assertEqual(2, result.returncode, combined(result))
        self.assertIn("docs.md", result.stderr)


if __name__ == "__main__":
    unittest.main()
