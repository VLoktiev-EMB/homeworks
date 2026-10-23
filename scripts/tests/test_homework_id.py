"""Prove the homework-ID convention documented in `AGENTS.md`.

FOUND-02 fixes the identifier shape: `module_lesson-name`, for example
`1_3-police-flasher`, and the identifier is stable after publication. The
canonical regular expression lives in `AGENTS.md` as a backticked, anchored
pattern; this module extracts that expression from the prose and applies it.
Documentation and behavior therefore cannot drift — editing either the pattern
or its examples fails here.

The probe set is deliberately two-sided: the canonical forms must match, and an
empty string, a separator-less name, a mixed-case name, a dotted name, and a
non-ASCII name must not. The last case is the ASCII rule: byte length and
codepoint length never diverge in a path or an identifier.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS = REPO_ROOT / "AGENTS.md"

BACKTICKED = re.compile(r"`([^`\n]+)`")
EXPECTED_PATTERN = r"^[0-9]+_[0-9]+-[a-z0-9-]+$"

MATCHING_IDS = ("1_3-police-flasher", "2_1-blink", "11_4-ring-buffer")
REJECTED_IDS = ("", "police-flasher", "1_3_Police-Flasher", "x.y", "1_3-policía")


class HomeworkIdPatternTest(unittest.TestCase):
    """Extract the documented identifier pattern and apply it."""

    @classmethod
    def setUpClass(cls):
        cls.text = AGENTS.read_text(encoding="utf-8") if AGENTS.is_file() else ""
        cls.patterns = [
            span
            for span in BACKTICKED.findall(cls.text)
            if span.startswith("^") and span.endswith("$")
        ]

    def _regex(self) -> re.Pattern[str]:
        self.assertEqual(
            len(self.patterns),
            1,
            f"expected exactly one anchored pattern in AGENTS.md, found {self.patterns}",
        )
        return re.compile(self.patterns[0])

    def test_rulebook_exists(self):
        self.assertTrue(AGENTS.is_file(), f"missing {AGENTS}")

    def test_documents_exactly_one_anchored_pattern(self):
        self.assertEqual(
            len(self.patterns),
            1,
            f"expected exactly one anchored pattern in AGENTS.md, found {self.patterns}",
        )

    def test_documented_pattern_is_the_canonical_expression(self):
        self.assertEqual(self._regex().pattern, EXPECTED_PATTERN)

    def test_documents_the_module_lesson_form(self):
        self.assertIn("module_lesson-name", self.text)

    def test_canonical_ids_match(self):
        pattern = self._regex()
        for value in MATCHING_IDS:
            with self.subTest(value=value):
                self.assertIsNotNone(
                    pattern.match(value),
                    f"{value!r} must satisfy the documented homework-ID pattern",
                )

    def test_rejected_ids_do_not_match(self):
        pattern = self._regex()
        for value in REJECTED_IDS:
            with self.subTest(value=value):
                self.assertIsNone(
                    pattern.match(value),
                    f"{value!r} must not satisfy the documented homework-ID pattern",
                )


if __name__ == "__main__":
    unittest.main()
