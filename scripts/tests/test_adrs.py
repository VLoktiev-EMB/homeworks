"""Structural tests for the architecture decision records in ``docs/decisions/``.

The suite is deliberately dependency-free: frontmatter is parsed as plain text and
headings are matched by exact line, so it runs under the stdlib ``unittest`` runner
without a YAML parser — the same convention as ``scripts/tests/test_check_policy.py``.

What it protects (TOOL-07, D-27):

* numbers are sequential from 0001 and never duplicated or reused;
* every record carries the five MADR frontmatter keys with ``status: accepted``;
* the status index in ``docs/decisions/README.md`` agrees with the records on disk;
* every record follows the eight-section MADR 4.0 order and opens its Decision
  Outcome with the chosen-option sentence;
* the content notes that make the Git, licensing, and asset decisions auditable are
  actually present.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

DECISIONS_DIR = Path(__file__).resolve().parents[2] / "docs" / "decisions"
INDEX_FILE = DECISIONS_DIR / "README.md"
TEMPLATE_FILE = DECISIONS_DIR / "template.md"

FRONTMATTER_KEYS = (
    "status",
    "date",
    "decision-makers",
    "consulted",
    "informed",
)

MADR_SECTIONS = (
    "## Context and Problem Statement",
    "## Decision Drivers",
    "## Considered Options",
    "## Decision Outcome",
    "### Consequences",
    "### Confirmation",
    "## Pros and Cons of the Options",
    "## More Information",
)

LFS_EXTENSIONS = (".pdf", ".step", ".stl", ".fzz", ".zip", ".bin", ".elf", ".vcd")

ADR_FILENAME = re.compile(r"^(\d{4})-[a-z0-9-]+\.md$")
EMAIL_ADDRESS = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def adr_files() -> list[Path]:
    """Return ADR files in numeric order (template and index are excluded)."""
    if not DECISIONS_DIR.is_dir():
        return []
    return sorted(
        (path for path in DECISIONS_DIR.iterdir() if ADR_FILENAME.match(path.name)),
        key=lambda path: path.name,
    )


def adr_for(number: int) -> Path:
    matches = [path for path in adr_files() if path.name.startswith(f"{number:04d}-")]
    if len(matches) != 1:
        raise AssertionError(f"expected exactly one ADR {number:04d}, got {matches}")
    return matches[0]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> dict[str, str] | None:
    """Parse the leading ``---`` block as ``key: raw value`` text (no YAML)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    values: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return values
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip()
    return None


def index_rows() -> list[list[str]]:
    """Return the status-index table rows as ``[number, title, status, date]``."""
    rows: list[list[str]] = []
    for line in read(INDEX_FILE).splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 4 or not re.fullmatch(r"\d{4}", cells[0]):
            continue
        rows.append(cells)
    return rows


def title_of(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise AssertionError("record has no top-level title")


def section_order(text: str) -> list[int]:
    """Return the indices at which each MADR heading appears, in file order."""
    lines = text.splitlines()
    return [lines.index(heading) for heading in MADR_SECTIONS if heading in lines]


def pros_and_cons_subsections(text: str) -> dict[str, list[str]]:
    """Map each option subsection under Pros and Cons to its body lines."""
    body = text.split("## Pros and Cons of the Options", 1)[1]
    body = body.split("## More Information", 1)[0]
    subsections: dict[str, list[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        if line.startswith("### "):
            current = line[4:].strip()
            subsections[current] = []
        elif current is not None:
            subsections[current].append(line)
    return subsections


class AdrSetTests(unittest.TestCase):
    def test_decisions_directory_has_template_and_index(self) -> None:
        self.assertTrue(TEMPLATE_FILE.is_file(), "docs/decisions/template.md missing")
        self.assertTrue(INDEX_FILE.is_file(), "docs/decisions/README.md missing")

    def test_numbers_are_contiguous_from_one(self) -> None:
        numbers = [int(path.name[:4]) for path in adr_files()]
        self.assertEqual(numbers, list(range(1, len(numbers) + 1)))

    def test_phase_one_numbers_0001_to_0005_exist(self) -> None:
        numbers = {int(path.name[:4]) for path in adr_files()}
        missing = sorted(set(range(1, 6)) - numbers)
        self.assertEqual(missing, [], f"missing phase-1 ADR numbers: {missing}")

    def test_numbers_are_not_duplicated(self) -> None:
        numbers = [path.name[:4] for path in adr_files()]
        self.assertEqual(len(numbers), len(set(numbers)))


class AdrFrontmatterTests(unittest.TestCase):
    def test_every_record_has_all_frontmatter_keys(self) -> None:
        self.assertTrue(adr_files(), "no ADR files found")
        for path in adr_files():
            with self.subTest(adr=path.name):
                values = frontmatter(read(path))
                self.assertIsNotNone(values, f"{path.name} has no frontmatter block")
                for key in FRONTMATTER_KEYS:
                    self.assertIn(key, values, f"{path.name} lacks '{key}'")

    def test_every_record_is_accepted_and_dated(self) -> None:
        for path in adr_files():
            with self.subTest(adr=path.name):
                values = frontmatter(read(path)) or {}
                self.assertEqual(values.get("status"), "accepted")
                self.assertRegex(values.get("date", ""), r"^\d{4}-\d{2}-\d{2}$")

    def test_no_email_address_in_record_prose(self) -> None:
        for path in adr_files():
            with self.subTest(adr=path.name):
                matches = EMAIL_ADDRESS.findall(read(path))
                self.assertEqual(matches, [], f"{path.name} contains an email address")


class IndexAgreementTests(unittest.TestCase):
    def test_index_has_a_row_for_every_record(self) -> None:
        rows = {row[0]: row for row in index_rows()}
        for path in adr_files():
            number = path.name[:4]
            with self.subTest(adr=path.name):
                self.assertIn(number, rows, f"{number} is absent from the index")
                values = frontmatter(read(path)) or {}
                self.assertEqual(
                    rows[number][2],
                    values.get("status"),
                    f"index status for {number} disagrees with frontmatter",
                )
                self.assertEqual(
                    rows[number][3],
                    values.get("date"),
                    f"index date for {number} disagrees with frontmatter",
                )

    def test_index_has_no_row_without_a_record(self) -> None:
        on_disk = {path.name[:4] for path in adr_files()}
        for row in index_rows():
            with self.subTest(number=row[0]):
                self.assertIn(row[0], on_disk, f"index row {row[0]} has no file")

    def test_index_titles_match_record_titles(self) -> None:
        rows = {row[0]: row for row in index_rows()}
        for path in adr_files():
            number = path.name[:4]
            with self.subTest(adr=path.name):
                self.assertIn(number, rows, f"{number} is absent from the index")
                self.assertEqual(rows[number][1], title_of(read(path)))

    def test_index_states_the_numbering_rules(self) -> None:
        text = read(INDEX_FILE).lower()
        self.assertIn("sequential", text)
        self.assertIn("never reused", text)


class MadrStructureTests(unittest.TestCase):
    def test_every_record_has_all_sections_in_madr_order(self) -> None:
        for path in adr_files():
            with self.subTest(adr=path.name):
                indices = section_order(read(path))
                self.assertEqual(
                    len(indices),
                    len(MADR_SECTIONS),
                    f"{path.name} is missing a MADR section",
                )
                self.assertEqual(indices, sorted(indices), f"{path.name}: wrong order")

    def test_decision_outcome_opens_with_the_chosen_option(self) -> None:
        for path in adr_files():
            with self.subTest(adr=path.name):
                body = read(path).split("## Decision Outcome", 1)[1]
                first_line = next(
                    line for line in body.splitlines() if line.strip()
                )
                self.assertTrue(
                    first_line.startswith('Chosen option: "'),
                    f"{path.name} does not open with 'Chosen option: \"...\"'",
                )

    def test_at_least_two_options_are_considered(self) -> None:
        for path in adr_files():
            with self.subTest(adr=path.name):
                body = read(path).split("## Considered Options", 1)[1]
                body = body.split("## Decision Outcome", 1)[0]
                bullets = [
                    line for line in body.splitlines() if line.startswith("* ")
                ]
                self.assertGreaterEqual(len(bullets), 2)

    def test_every_option_has_a_pros_and_cons_entry(self) -> None:
        for path in adr_files():
            with self.subTest(adr=path.name):
                subsections = pros_and_cons_subsections(read(path))
                self.assertGreaterEqual(len(subsections), 2)
                for option, lines in subsections.items():
                    with self.subTest(adr=path.name, option=option):
                        judgements = [
                            line
                            for line in lines
                            if line.startswith(("* Good,", "* Neutral,", "* Bad,"))
                        ]
                        self.assertTrue(
                            judgements, f"{path.name}: '{option}' has no judgement"
                        )


class RequiredContentTests(unittest.TestCase):
    def test_adr_0003_records_the_git_policy_audit_gaps(self) -> None:
        text = read(adr_for(3)).lower()
        for phrase in (
            "squash",
            "default branch",
            "approvals",
            "second maintainer",
            ".planning",
            "mutable",
            "tag",
            "revisit",
            "require_extra_approval_for_unattributed_changes",
            "200",
            "re-read",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_adr_0004_records_the_license_substitutions(self) -> None:
        text = read(adr_for(4))
        lowered = text.lower()
        for phrase in (
            "reuse.toml",
            "dep5",
            "sim-02",
            "stale",
            ".github/pull_request_template",
            "mit",
            "cc-by-4.0",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, lowered)

    def test_adr_0005_records_the_asset_policy(self) -> None:
        text = read(adr_for(5))
        lowered = text.lower()
        for phrase in ("lfs", "github pages", "linked", "1024"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, lowered)
        for extension in LFS_EXTENSIONS:
            with self.subTest(extension=extension):
                self.assertIn(extension, lowered)


if __name__ == "__main__":
    unittest.main()
