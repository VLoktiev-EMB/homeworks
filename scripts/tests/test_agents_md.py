"""Contract tests for the canonical rulebook and its Claude Code adapter.

`AGENTS.md` is the single place where repository rules live; `.claude/CLAUDE.md`
imports it so Claude Code loads the same rules instead of a copy. Two failure
modes are silent and expensive: the rulebook growing past the point an agent
actually reads it, and the adapter forking into an independently edited rule
set. Both are asserted here.

The generator-owned blocks (`skills`, `workflow`, `profile`) are excluded from
the "no restated rules" check, because GSD owns their inner text and a future
generator run must stay compatible with this test.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS = REPO_ROOT / "AGENTS.md"
ADAPTER = REPO_ROOT / ".claude" / "CLAUDE.md"

# D-02: REQUIREMENTS wins over the sub-200-line guidance for this file.
LINE_CEILING = 300

# D-03: literal, machine-matchable vocabulary. No [MAY], no [INFO].
ENFORCEMENT_TOKENS = (
    "[MUST]",
    "[SHOULD]",
    "[ENFORCED: pre-commit]",
    "[ENFORCED: CI]",
    "[ENFORCED: review]",
)

# The commands an agent needs before its first commit.
CANONICAL_COMMANDS = (
    "scripts/tag_homework.sh",
    "scripts/check_policy.py --check",
    "scripts/check_pr_templates.py",
    "unittest discover -s scripts/tests",
    "pre-commit run --all-files",
)

# The agents.md convention's precedence sentence, quoted verbatim.
PRECEDENCE = (
    "The closest AGENTS.md to the edited file wins; "
    "explicit user chat prompts override everything."
)

GSD_BLOCK = re.compile(
    r"<!-- GSD:(?P<name>[a-z]+)-start\b.*?<!-- GSD:(?P=name)-end -->",
    re.DOTALL,
)

GENERATOR_BLOCKS = ("skills", "workflow", "profile")


class RulebookTest(unittest.TestCase):
    """Guard the rulebook's ceiling, vocabulary, commands, and routing table."""

    @classmethod
    def setUpClass(cls):
        cls.text = AGENTS.read_text(encoding="utf-8") if AGENTS.is_file() else ""

    def test_rulebook_exists(self):
        self.assertTrue(AGENTS.is_file(), f"missing {AGENTS}")

    def test_stays_under_the_line_ceiling(self):
        lines = self.text.splitlines()
        self.assertLessEqual(
            len(lines),
            LINE_CEILING,
            f"AGENTS.md is {len(lines)} lines; the ceiling is {LINE_CEILING}",
        )

    def test_carries_the_full_enforcement_vocabulary(self):
        for token in ENFORCEMENT_TOKENS:
            with self.subTest(token=token):
                self.assertIn(token, self.text)

    def test_canonical_commands_are_listed(self):
        for command in CANONICAL_COMMANDS:
            with self.subTest(command=command):
                self.assertIn(command, self.text)

    def test_routing_table_names_the_decisions_index(self):
        self.assertIn("docs/decisions/README.md", self.text)

    def test_planned_paths_are_marked_planned(self):
        # Any path that does not exist yet must say so on its own line.
        for number, line in enumerate(self.text.splitlines(), start=1):
            if "docs/standards/" in line:
                with self.subTest(line=number):
                    self.assertIn(
                        "planned",
                        line.lower(),
                        f"line {number} links docs/standards/ without a planned marker",
                    )

    def test_records_the_nearest_file_precedence(self):
        self.assertIn(PRECEDENCE, self.text)


class AdapterTest(unittest.TestCase):
    """Guard the single-source rule: the adapter imports, it does not fork."""

    @classmethod
    def setUpClass(cls):
        cls.text = ADAPTER.read_text(encoding="utf-8") if ADAPTER.is_file() else ""

    def test_adapter_exists(self):
        self.assertTrue(ADAPTER.is_file(), f"missing {ADAPTER}")

    def test_imports_the_rulebook(self):
        self.assertIn("@AGENTS.md", self.text)

    def test_import_is_the_first_substantive_line(self):
        substantive = [line for line in self.text.splitlines() if line.strip()]
        self.assertTrue(substantive, "adapter is empty")
        self.assertEqual(substantive[0].strip(), "@AGENTS.md")

    def test_restates_no_enforcement_rules(self):
        # Generator-owned blocks are not the adapter's own prose.
        hand_written = GSD_BLOCK.sub("", self.text)
        for token in ENFORCEMENT_TOKENS:
            with self.subTest(token=token):
                self.assertNotIn(token, hand_written)

    def test_preserves_every_generator_block(self):
        for name in GENERATOR_BLOCKS:
            with self.subTest(block=name):
                self.assertIn(f"<!-- GSD:{name}-start", self.text)
                self.assertIn(f"<!-- GSD:{name}-end -->", self.text)


if __name__ == "__main__":
    unittest.main()
