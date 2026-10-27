"""Prove the homework metadata contract end to end.

The checker is invoked as a subprocess (`uv run scripts/check_metadata.py`)
because the validator imports PyYAML and jsonschema, and D-14 keeps this suite
dependency-free: no test module may import either library. Every fixture is a
temporary root that contains a copy of `schema/` and `platformio.shared.ini`,
so the real tree is never touched and a negative case can fail only because of
its single mutation.

Coverage: the minimal and full documents, an unknown key at the root and in
every nested block, every required root key and every required `$defs` member,
the optional `simulation.diagram`, the research probe matrix, the identity
invariant `id == homeworks/<dir>`, malformed YAML / non-mapping / duplicated
keys / the 64 KiB cap, toolchain drift and a broken shared configuration, the
`--json` record shape, determinism and read-only behaviour, and the one
canonical homework-ID literal shared by the schema, `contract.py`, and
`AGENTS.md`.

Provenance semantics for `task.md` are owned by plan 04-03: every fixture now
writes both `homework.yaml` and `task.md`, and this module asserts the D-39
status branch, the four provenance fields and the shape rules.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

EXPECTED_PATTERN = r"^[0-9]+_[0-9]+-[a-z0-9-]+$"

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_metadata.py"
# The canonical id literal now lives in the stdlib-only `paths.py`; `contract.py`
# re-exports it (D-19 extraction, 05-01) rather than keeping a second copy.
CONTRACT = REPO_ROOT / "scripts" / "metadata" / "paths.py"
SCHEMA = REPO_ROOT / "schema" / "homework.schema.json"
AGENTS = REPO_ROOT / "AGENTS.md"

# D-04/D-27: the board-profile contract and its one real document. The template
# text is the known-good payload every board fixture is derived from; reading it
# with `Path` keeps this module free of a PyYAML import (04/D-14).
BOARD_SCHEMA = REPO_ROOT / "schema" / "board-profile.schema.json"
BOARD_TEMPLATE = (
    REPO_ROOT / "templates" / "board-profile" / "profile.yaml"
).read_text(encoding="utf-8")

ROOT_ORDER = (
    "schema_version",
    "id",
    "title",
    "board",
    "framework",
    "language",
    "status",
    "source",
    "toolchain",
)

SCALAR_CHUNKS = {
    "schema_version": "schema_version: 1\n",
    "id": "id: {homework_id}\n",
    "title": "title: Good homework\n",
    "board": "board: esp32-s3-devkitc-1\n",
    "framework": "framework: arduino\n",
    "language": "language: cpp\n",
    "status": "status: planned\n",
}

DEFS_CHUNKS = {
    "source": {"reference": "  reference: TODO\n"},
    "toolchain": {
        "platformio": "  platformio: 6.2.0\n",
        "platform": "  platform: espressif32@8.0.0\n",
    },
    "simulation": {"tool": "  tool: none\n", "status": "  status: none\n"},
    "tests": {
        "framework": "  framework: unity\n",
        "native": "  native: true\n",
        "coverage": "  coverage: false\n",
    },
    "report": {
        "path": "  path: report/report.md\n",
        "status": "  status: placeholder\n",
    },
}

DEFS_REQUIRED = {
    "source": ("reference",),
    "toolchain": ("platformio", "platform"),
    "simulation": ("tool", "status"),
    "tests": ("framework", "native", "coverage"),
    "report": ("path", "status"),
}

OPTIONAL_BLOCKS = ("simulation", "tests", "report")
ASSETS_CHUNK = "assets:\n  - assets/wiring.png\n"

# CR-01: ~2 KB of valid YAML syntax with 1,000 nested flow sequences. It sits
# inside the 64 KiB input bound, so only a nesting bound turns it into a record.
DEEP_YAML = "title: " + "[" * 1000 + "]" * 1000 + "\n"
DEEP_FRONTMATTER = "---\nkey: " + "[" * 1000 + "]" * 1000 + "\n---\n# Task\n"

# The scaffolded skeleton (D-39). `TODO` is literal and legal only while the
# homework is `status: planned`; no timestamp is ever rendered (Pitfall P10).
TASK_TEMPLATE = (
    "---\n"
    "source_url: TODO\n"
    "retrieved: TODO\n"
    "attribution: TODO\n"
    "license: TODO\n"
    "---\n"
    "\n"
    "# Good homework\n"
    "\n"
    "## Task\n"
    "\n"
    "TODO: English paraphrase.\n"
)


def run_checker(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", str(SCRIPT), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=120,
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


def setUpModule():
    """Warm uv's script environment before the first asserted run.

    Environment creation can print an install line on stderr once; a warm run
    keeps the determinism assertion about the checker, not about uv.
    """
    result = run_checker("--help")
    if result.returncode != 0:
        raise RuntimeError(f"uv could not run the checker: {combined(result)}")


def block_text(name, omit=()):
    body = "".join(
        chunk for key, chunk in DEFS_CHUNKS[name].items() if key not in omit
    )
    return f"{name}:\n{body}"


def document(
    *,
    homework_id="1_3-good",
    omit_root=(),
    omit_defs=(),
    optional=True,
    with_diagram=False,
    assets=None,
):
    """Render a `homework.yaml` payload by string assembly, never with `yaml`."""
    omitted = set(omit_defs)
    chunks = []
    for key in ROOT_ORDER:
        if key in omit_root:
            continue
        if key in SCALAR_CHUNKS:
            chunks.append(SCALAR_CHUNKS[key])
        else:
            chunks.append(block_text(key, {m for b, m in omitted if b == key}))
    if optional:
        for name in OPTIONAL_BLOCKS:
            if name == "simulation" and with_diagram:
                chunks.append(
                    "simulation:\n"
                    "  tool: none\n"
                    "  diagram: assets/diagram.svg\n"
                    "  status: none\n"
                )
                continue
            chunks.append(block_text(name, {m for b, m in omitted if b == name}))
        chunks.append(ASSETS_CHUNK if assets is None else assets)
    return "".join(chunks).format(homework_id=homework_id)


class FixtureBase(unittest.TestCase):
    """A temporary root with the schema and the shared configuration copied in."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="metadata-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        shutil.copytree(REPO_ROOT / "schema", self.root / "schema")
        shutil.copy2(
            REPO_ROOT / "platformio.shared.ini",
            self.root / "platformio.shared.ini",
        )

    def write_homework(
        self,
        text=None,
        homework_id="1_3-good",
        directory=None,
        with_task=True,
        task_text=None,
    ):
        directory = directory or homework_id
        path = self.root / "homeworks" / directory / "homework.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        if text is None:
            text = document(homework_id=homework_id)
        path.write_text(text, encoding="utf-8")
        if with_task:
            self.write_task(task_text, directory=directory)
        return path

    def write_task(self, text=None, directory="1_3-good"):
        path = self.root / "homeworks" / directory / "task.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(TASK_TEMPLATE if text is None else text, encoding="utf-8")
        return path

    def run_fixture(self, *args):
        return run_checker("--dir", str(self.root), *args)

    def assert_accepted(self, result):
        self.assertEqual(0, result.returncode, combined(result))
        self.assertIn(": OK — ", result.stdout)

    def assert_rejected(self, result, fragment=None):
        self.assertEqual(1, result.returncode, combined(result))
        self.assertIn(": ERROR — ", result.stdout)
        if fragment:
            self.assertIn(fragment, result.stdout)

    def assert_environment_error(self, result, fragment=None):
        self.assertEqual(2, result.returncode, combined(result))
        self.assertIn("ERROR:", result.stderr)
        if fragment:
            self.assertIn(fragment, result.stderr)


class SchemaShapeTest(unittest.TestCase):
    """The committed schema stays strict and never relies on `format`."""

    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_schema_declares_additional_properties_everywhere(self):
        self.assertIs(False, self.schema.get("additionalProperties"))
        self.assertEqual(
            {"source", "toolchain", "simulation", "tests", "report"},
            set(self.schema.get("$defs", {})),
        )
        for name, block in self.schema["$defs"].items():
            with self.subTest(block=name):
                self.assertIs(False, block.get("additionalProperties"))

    def test_schema_contains_no_format_keyword(self):
        # Pitfall P1: `format: uri` accepts "not a url" without a checker, so
        # every shape must be an anchored pattern instead.
        self.assertNotIn('"format"', json.dumps(self.schema))

    def test_board_schema_is_strict_and_describes_frameworks(self):
        # The board profile keeps the homework envelope's strictness: no unknown
        # key anywhere, no `format` keyword, and an enum whose rationale is
        # written down rather than implied.
        board = json.loads(BOARD_SCHEMA.read_text(encoding="utf-8"))
        self.assertIs(False, board.get("additionalProperties"))
        self.assertNotIn('"format"', json.dumps(board))
        frameworks = board["properties"]["frameworks"]
        self.assertEqual("array", frameworks["type"])
        self.assertIs(True, frameworks.get("uniqueItems"))
        self.assertEqual({"arduino", "espidf"}, set(frameworks["items"]["enum"]))
        self.assertTrue(frameworks.get("description"))


class BoardProfileTests(FixtureBase):
    """D-27: `boards/<id>.yaml` has the same machine-enforced contract."""

    STEM = "esp32-s3-devkitc-1"

    def write_board(self, text=None, stem=None, directory="boards"):
        """Write a board document by string assembly, never with PyYAML."""
        path = self.root / directory / f"{stem or self.STEM}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            BOARD_TEMPLATE if text is None else text, encoding="utf-8"
        )
        return path

    def board_path(self, stem=None):
        return f"boards/{stem or self.STEM}.yaml"

    def test_accepted_profile_is_ok(self):
        self.write_board()
        result = self.run_fixture()
        self.assert_accepted(result)
        self.assertIn(f"{self.board_path()}: OK — ", result.stdout)

    def test_id_must_match_the_file_stem(self):
        self.write_board(stem="other-board")
        self.assert_rejected(self.run_fixture(), "does not match the file stem")

    def test_unknown_key_is_error(self):
        self.write_board(BOARD_TEMPLATE + "unexpected: true\n")
        self.assert_rejected(self.run_fixture(), "unexpected")

    def test_missing_required_key_is_error(self):
        self.write_board(BOARD_TEMPLATE.replace("flash_mb: 16\n", ""))
        self.assert_rejected(self.run_fixture(), "flash_mb")

    def test_psram_outside_the_enum_is_error(self):
        self.write_board(BOARD_TEMPLATE.replace("psram: octal", "psram: hex"))
        self.assert_rejected(self.run_fixture(), "psram")

    def test_non_https_pinout_url_is_error(self):
        self.write_board(
            BOARD_TEMPLATE.replace(
                "https://docs.espressif.com", "http://docs.espressif.com"
            )
        )
        self.assert_rejected(self.run_fixture(), "pinout_url")

    def test_duplicate_frameworks_entry_is_error(self):
        duplicated = BOARD_TEMPLATE.replace(
            "frameworks:\n  - arduino\n  - espidf\n",
            "frameworks:\n  - arduino\n  - arduino\n",
        )
        self.assertNotEqual(BOARD_TEMPLATE, duplicated)
        self.write_board(duplicated)
        self.assert_rejected(self.run_fixture(), "frameworks")

    def test_duplicate_psram_key_is_error(self):
        # `yaml.safe_load` would keep the last value silently; StrictSafeLoader
        # turns the merge accident into a content problem.
        duplicated = BOARD_TEMPLATE.replace(
            "psram: octal\n", "psram: octal\npsram: octal\n"
        )
        self.assertNotEqual(BOARD_TEMPLATE, duplicated)
        self.write_board(duplicated)
        self.assert_rejected(self.run_fixture(), "duplicate key 'psram'")

    def test_duplicate_pinout_url_key_is_error(self):
        last_line = BOARD_TEMPLATE.splitlines(keepends=True)[-1]
        self.write_board(BOARD_TEMPLATE + last_line)
        self.assert_rejected(self.run_fixture(), "duplicate key 'pinout_url'")

    def test_symlinked_boards_directory_is_refused(self):
        outside = Path(tempfile.mkdtemp(prefix="boards-outside-"))
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        (outside / f"{self.STEM}.yaml").write_text(
            BOARD_TEMPLATE, encoding="utf-8"
        )
        (self.root / "boards").symlink_to(outside, target_is_directory=True)
        self.assert_environment_error(self.run_fixture(), "boards")

    def test_symlinked_board_document_is_refused_not_followed(self):
        outside = Path(tempfile.mkdtemp(prefix="boards-outside-"))
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        target = outside / "profile.yaml"
        target.write_text(BOARD_TEMPLATE, encoding="utf-8")
        boards = self.root / "boards"
        boards.mkdir()
        (boards / f"{self.STEM}.yaml").symlink_to(target)
        result = self.run_fixture()
        self.assert_rejected(result, "symlink")
        self.assertIn(f"{self.board_path()}: ERROR — ", result.stdout)

    def test_missing_boards_directory_is_not_an_error(self):
        result = self.run_fixture()
        self.assertEqual(0, result.returncode, combined(result))
        self.assertNotIn("boards/", result.stdout)

    def test_board_only_positional_scans_no_homework(self):
        self.write_homework()
        self.write_board()
        result = self.run_fixture("--json", self.board_path())
        self.assertEqual(0, result.returncode, combined(result))
        paths = [record["path"] for record in json.loads(result.stdout)]
        self.assertEqual([self.board_path()], paths)

    def test_homework_only_positional_scans_no_board(self):
        self.write_homework()
        self.write_board()
        result = self.run_fixture("--json", "homeworks/1_3-good")
        self.assertEqual(0, result.returncode, combined(result))
        paths = [record["path"] for record in json.loads(result.stdout)]
        self.assertTrue(paths)
        self.assertTrue(
            all(path.startswith("homeworks/") for path in paths), paths
        )

    def test_mixed_positionals_scan_exactly_the_named_families(self):
        # A homework positional expands to that directory's two contract
        # documents; what must not happen is a board or homework family being
        # widened to "all" because the other family was named.
        self.write_homework()
        self.write_board()
        result = self.run_fixture(
            "--json", self.board_path(), "homeworks/1_3-good"
        )
        self.assertEqual(0, result.returncode, combined(result))
        paths = [record["path"] for record in json.loads(result.stdout)]
        self.assertEqual(
            sorted(
                [
                    self.board_path(),
                    "homeworks/1_3-good/homework.yaml",
                    "homeworks/1_3-good/task.md",
                ]
            ),
            paths,
        )

    def test_missing_board_schema_is_exit_two(self):
        self.write_board()
        (self.root / "schema" / "board-profile.schema.json").unlink()
        result = self.run_fixture()
        self.assertEqual(2, result.returncode, combined(result))
        self.assertEqual("", result.stdout)
        self.assertIn("ERROR:", result.stderr)


class BaselineTests(FixtureBase):
    """The fixture harness starts from a document the contract accepts."""

    def test_minimal_document_is_accepted(self):
        self.write_homework(document(optional=False))
        self.assert_accepted(self.run_fixture())

    def test_full_document_with_every_optional_block_is_accepted(self):
        self.write_homework(document())
        self.assert_accepted(self.run_fixture())


class TaskProvenanceTests(FixtureBase):
    """D-15 / D-39: provenance is text, and the sentinel follows the status."""

    def test_planned_task_sentinels_are_accepted(self):
        self.write_homework()
        self.assert_accepted(self.run_fixture())

    def test_sentinel_is_rejected_once_status_leaves_planned(self):
        self.write_homework(
            document().replace("status: planned", "status: in-progress")
        )
        result = self.run_fixture()
        self.assert_rejected(result, "homeworks/1_3-good/task.md: ERROR — ")
        self.assertIn("source_url", result.stdout)
        self.assertIn("'planned'", result.stdout)

    def test_missing_task_md_is_error(self):
        self.write_homework(with_task=False)
        self.assert_rejected(self.run_fixture(), "task.md is missing")

    def test_extra_task_frontmatter_key_is_error(self):
        text = TASK_TEMPLATE.replace(
            "license: TODO\n", "license: TODO\nunexpected: TODO\n"
        )
        self.write_homework(task_text=text)
        self.assert_rejected(
            self.run_fixture(), "unexpected: unknown frontmatter key"
        )


class ProvenanceShapeTests(FixtureBase):
    """D-15/D-16: every field shape is proven accepted and rejected."""

    def test_unquoted_iso_timestamp_stays_a_string(self):
        # The base loader is what makes this pass: SafeLoader would turn the
        # scalar into a datetime before the string checks run.
        text = TASK_TEMPLATE.replace(
            "retrieved: TODO", "retrieved: 2026-10-24T20:01:00Z"
        )
        self.write_homework(task_text=text)
        self.assert_accepted(self.run_fixture())

    def test_valid_url_timestamp_and_license_are_accepted(self):
        for retrieved in ("2026-10-24T20:01:00Z", "2026-10-24T20:01:00+02:00"):
            for license_value in ("MIT", "CC-BY-4.0"):
                with self.subTest(retrieved=retrieved, license=license_value):
                    text = (
                        TASK_TEMPLATE.replace(
                            "source_url: TODO",
                            "source_url: https://example.com/assignment",
                        )
                        .replace("retrieved: TODO", f"retrieved: {retrieved}")
                        .replace("license: TODO", f"license: {license_value}")
                    )
                    self.write_homework(task_text=text)
                    self.assert_accepted(self.run_fixture())

    def test_invalid_shapes_are_rejected(self):
        cases = {
            "bare date": TASK_TEMPLATE.replace(
                "retrieved: TODO", "retrieved: 2026-10-24"
            ),
            "non-url source_url": TASK_TEMPLATE.replace(
                "source_url: TODO", "source_url: example.com/x"
            ),
            "empty attribution": TASK_TEMPLATE.replace(
                "attribution: TODO", "attribution: ''"
            ),
            "license with space": TASK_TEMPLATE.replace(
                "license: TODO", "license: 'cc by'"
            ),
            "license with underscore": TASK_TEMPLATE.replace(
                "license: TODO", "license: CC_BY"
            ),
        }
        for name, text in cases.items():
            with self.subTest(case=name):
                self.write_homework(task_text=text)
                self.assert_rejected(
                    self.run_fixture(), "homeworks/1_3-good/task.md: ERROR — "
                )


class CyrillicGateTests(FixtureBase):
    """T-04-05: the name-based scan covers every Cyrillic block."""

    WORD = "поліцейський"

    def _cyrillic_task(self):
        return TASK_TEMPLATE + self.WORD + "\n"

    def test_cyrillic_word_is_rejected_with_line_number(self):
        self.write_homework(task_text=self._cyrillic_task())
        result = self.run_fixture()
        self.assert_rejected(result, "homeworks/1_3-good/task.md: ERROR — ")
        expected_line = TASK_TEMPLATE.count("\n") + 1
        self.assertIn(f"line {expected_line}:", result.stdout)
        self.assertIn("Cyrillic character", result.stdout)

    def test_extended_b_character_is_rejected(self):
        # U+A647 CYRILLIC SMALL LETTER IOTA: outside the basic block.
        self.write_homework(task_text=TASK_TEMPLATE + "ꙇ\n")
        self.assert_rejected(self.run_fixture(), "Cyrillic character")

    def test_latin_homoglyph_is_not_rejected(self):
        # U+0065 LATIN SMALL LETTER E looks like U+0435 CYRILLIC SMALL LETTER IE.
        self.write_homework(task_text=TASK_TEMPLATE + "e\n")
        self.assert_accepted(self.run_fixture())

    def test_json_failure_carries_task_path_and_error(self):
        self.write_homework(task_text=self._cyrillic_task())
        result = self.run_fixture("--json")
        self.assertEqual(1, result.returncode, combined(result))
        payload = json.loads(result.stdout)
        task_records = [
            item
            for item in payload
            if item["path"] == "homeworks/1_3-good/task.md"
        ]
        self.assertTrue(task_records)
        self.assertTrue(
            all(item["status"] == "ERROR" for item in task_records)
        )


class CrossValidationTests(FixtureBase):
    """D-17: the two documents must agree on the source URL."""

    URL = "https://example.com/a"

    def _homework_with(self, reference):
        return document().replace(
            "  reference: TODO\n", f"  reference: {reference}\n"
        )

    def test_identical_reference_and_source_url_is_accepted(self):
        self.write_homework(
            self._homework_with(self.URL),
            task_text=TASK_TEMPLATE.replace(
                "source_url: TODO", f"source_url: {self.URL}"
            ),
        )
        self.assert_accepted(self.run_fixture())

    def test_mismatched_reference_and_source_url_is_error(self):
        self.write_homework(
            self._homework_with(self.URL),
            task_text=TASK_TEMPLATE.replace(
                "source_url: TODO", "source_url: https://example.com/b"
            ),
        )
        self.assert_rejected(
            self.run_fixture(), "disagrees with homework.yaml source.reference"
        )


class TaskInputHardeningTests(FixtureBase):
    """T-04-15/T-04-21: malformed, duplicated and oversized input is exit 1."""

    def test_malformed_frontmatter_is_error(self):
        text = TASK_TEMPLATE.replace(
            "source_url: TODO", 'source_url: "unclosed'
        )
        self.write_homework(task_text=text)
        self.assert_rejected(self.run_fixture(), "invalid YAML frontmatter")

    def test_non_mapping_frontmatter_is_error(self):
        text = "---\njust a scalar\n---\n\n# Body\n"
        self.write_homework(task_text=text)
        self.assert_rejected(self.run_fixture(), "not a YAML mapping")

    def test_duplicate_frontmatter_key_is_error(self):
        text = TASK_TEMPLATE.replace(
            "license: TODO\n", "license: TODO\nlicense: MIT\n"
        )
        self.write_homework(task_text=text)
        self.assert_rejected(self.run_fixture(), "duplicate key 'license'")

    def test_oversized_task_is_error(self):
        text = TASK_TEMPLATE + "# " + ("x" * (64 * 1024)) + "\n"
        self.write_homework(task_text=text)
        self.assert_rejected(self.run_fixture(), "larger than 65536 bytes")

    def test_orphan_directory_is_error(self):
        (self.root / "homeworks" / "1_9-orphan").mkdir(parents=True)
        self.assert_rejected(
            self.run_fixture(), "homeworks/1_9-orphan: ERROR — "
        )

    def test_directory_with_only_task_is_error(self):
        self.write_task()
        self.assert_rejected(self.run_fixture(), "homework.yaml is missing")


class UnknownKeyTests(FixtureBase):
    """`additionalProperties: false` holds at the root and in every block."""

    NESTED_ANCHORS = {
        "source": ("source:\n  reference: TODO\n", "  unexpected: true\n"),
        "toolchain": (
            "toolchain:\n  platformio: 6.2.0\n",
            "  unexpected: true\n",
        ),
        "simulation": ("simulation:\n  tool: none\n", "  unexpected: true\n"),
        "tests": ("tests:\n  framework: unity\n", "  unexpected: true\n"),
        "report": ("report:\n  path: report/report.md\n", "  unexpected: true\n"),
    }

    def test_unknown_top_level_key_is_error(self):
        text = document(optional=False).replace(
            "status: planned\n", "status: planned\nunexpected: true\n", 1
        )
        self.write_homework(text)
        self.assert_rejected(self.run_fixture(), "unexpected")

    def test_unknown_nested_key_is_error(self):
        for name, (anchor, injection) in self.NESTED_ANCHORS.items():
            with self.subTest(block=name):
                text = document().replace(anchor, anchor + injection, 1)
                self.assertNotEqual(document(), text, f"anchor missing for {name}")
                self.write_homework(text)
                self.assert_rejected(self.run_fixture(), "unexpected")


class RequiredKeyTests(FixtureBase):
    """Every required key is proven separately, not just the first one."""

    def test_every_required_root_key_is_required(self):
        for key in ROOT_ORDER:
            with self.subTest(key=key):
                self.write_homework(
                    document(omit_root=(key,), optional=False)
                )
                self.assert_rejected(self.run_fixture())

    def test_every_required_defs_member_is_required(self):
        for block, members in DEFS_REQUIRED.items():
            for member in members:
                with self.subTest(block=block, member=member):
                    self.write_homework(
                        document(omit_defs=((block, member),))
                    )
                    self.assert_rejected(self.run_fixture())

    def test_optional_simulation_diagram_is_accepted(self):
        self.write_homework(document(with_diagram=True))
        self.assert_accepted(self.run_fixture())


class ResearchProbeTests(FixtureBase):
    """Every probe from the research matrix is rejected."""

    def test_research_probes_are_rejected(self):
        minimal = document(optional=False)
        cases = {
            "id police-flasher": document(homework_id="police-flasher", optional=False),
            "status draft": minimal.replace("status: planned", "status: draft"),
            "framework stm32": minimal.replace(
                "framework: arduino", "framework: stm32"
            ),
            "platformio 6.2": minimal.replace(
                "platformio: 6.2.0", "platformio: 6.2"
            ),
            "duplicate assets": minimal + "assets:\n  - a.png\n  - a.png\n",
            "absolute asset path": minimal + "assets:\n  - /etc/passwd\n",
            "dotdot asset path": minimal + "assets:\n  - ../escape.png\n",
            "backslash asset path": minimal + "assets:\n  - 'dir\\x.png'\n",
            "trailing slash asset path": minimal + "assets:\n  - assets/\n",
        }
        for name, text in cases.items():
            with self.subTest(probe=name):
                self.write_homework(text)
                self.assert_rejected(self.run_fixture())


class IdentityTests(FixtureBase):
    """`id` is the single source of identity and must name its directory."""

    def test_matching_id_is_accepted(self):
        self.write_homework(document(homework_id="1_3-good", optional=False))
        self.assert_accepted(self.run_fixture())

    def test_id_must_match_containing_directory(self):
        self.write_homework(
            document(homework_id="1_3-other", optional=False),
            homework_id="1_3-good",
        )
        self.assert_rejected(self.run_fixture(), "containing directory")

    def test_id_mismatch_survives_a_symlinked_homeworks_base(self):
        # D-14: stdlib only. The candidate lives outside the root and is
        # reached through a symlinked `homeworks/`; the identity invariant must
        # still fire instead of being erased by path resolution (T-04-27).
        outside = Path(tempfile.mkdtemp(prefix="metadata-outside-"))
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        directory = outside / "1_3-good"
        directory.mkdir()
        (directory / "homework.yaml").write_text(
            document(homework_id="1_3-other", optional=False), encoding="utf-8"
        )
        (directory / "task.md").write_text(TASK_TEMPLATE, encoding="utf-8")
        (self.root / "homeworks").symlink_to(outside)

        self.assert_rejected(self.run_fixture(), "containing directory")

    def test_id_mismatch_holds_when_the_root_is_spelled_differently(self):
        # A symlink alias names the same tree with a different absolute
        # spelling, so the identity check must not depend on how the caller
        # spells the root (T-04-29). `run_fixture` cannot express this: it
        # hardcodes `--dir str(self.root)` and passes no positional path.
        alias_parent = Path(tempfile.mkdtemp(prefix="metadata-alias-"))
        self.addCleanup(shutil.rmtree, alias_parent, ignore_errors=True)
        alias = alias_parent / "spelled-root"
        alias.symlink_to(self.root.resolve(), target_is_directory=True)
        self.write_homework(
            document(homework_id="1_3-other", optional=False),
            homework_id="1_3-good",
        )

        for name, root_spelling in (
            ("alias", alias),
            ("canonical", self.root.resolve()),
        ):
            with self.subTest(spelling=name):
                positional = (
                    root_spelling / "homeworks" / "1_3-good" / "homework.yaml"
                )
                result = run_checker(
                    "--dir", str(root_spelling), str(positional)
                )
                self.assert_rejected(result, "containing directory")

    def test_matching_id_is_accepted_when_the_root_is_spelled_differently(self):
        # The spelling repair must not pass by rejecting every spelling.
        alias_parent = Path(tempfile.mkdtemp(prefix="metadata-alias-"))
        self.addCleanup(shutil.rmtree, alias_parent, ignore_errors=True)
        alias = alias_parent / "spelled-root"
        alias.symlink_to(self.root.resolve(), target_is_directory=True)
        self.write_homework(document(homework_id="1_3-good", optional=False))

        result = run_checker(
            "--dir", str(alias), str(alias / "homeworks" / "1_3-good")
        )
        self.assert_accepted(result)

    def test_id_mismatch_survives_a_symlinked_base_under_a_differently_spelled_root(
        self,
    ):
        # T-04-30: reconciling the ancestor prefix must not resolve the
        # `homeworks` component, or the symlinked-base protection is erased.
        alias_parent = Path(tempfile.mkdtemp(prefix="metadata-alias-"))
        self.addCleanup(shutil.rmtree, alias_parent, ignore_errors=True)
        alias = alias_parent / "spelled-root"
        alias.symlink_to(self.root.resolve(), target_is_directory=True)
        outside = Path(tempfile.mkdtemp(prefix="metadata-outside-"))
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        directory = outside / "1_3-good"
        directory.mkdir()
        (directory / "homework.yaml").write_text(
            document(homework_id="1_3-other", optional=False), encoding="utf-8"
        )
        (directory / "task.md").write_text(TASK_TEMPLATE, encoding="utf-8")
        (self.root / "homeworks").symlink_to(outside)

        result = run_checker(
            "--dir", str(alias), str(alias / "homeworks" / "1_3-good")
        )
        self.assert_rejected(result, "containing directory")


class PayloadTests(FixtureBase):
    """Content problems are ERROR records at exit 1, never environment errors."""

    def test_malformed_yaml_is_error(self):
        self.write_homework('title: "unclosed\n')
        self.assert_rejected(self.run_fixture(), "invalid YAML")

    def test_non_mapping_payload_is_error(self):
        self.write_homework("just a scalar\n")
        self.assert_rejected(self.run_fixture(), "not a YAML mapping")

    def test_duplicate_mapping_key_is_error(self):
        text = document(optional=False) + "source:\n  reference: again\n"
        self.write_homework(text)
        self.assert_rejected(self.run_fixture(), "duplicate key 'source'")

    def test_nested_duplicate_mapping_key_is_error(self):
        text = document(optional=False).replace(
            "source:\n  reference: TODO\n",
            "source:\n  reference: TODO\n  reference: again\n",
            1,
        )
        self.write_homework(text)
        self.assert_rejected(self.run_fixture(), "duplicate key 'reference'")

    def test_composed_mapping_key_is_error(self):
        # A constructed key that is not hashable must become a YAML error
        # record, never a TypeError traceback with empty --json output
        # (CR-02, T-04-24).
        text = document(optional=False) + "? [a, b]\n: c\n"
        self.write_homework(text)
        result = self.run_fixture("--json")
        self.assertEqual(1, result.returncode, combined(result))
        payload = json.loads(result.stdout)
        self.assertIsInstance(payload, list)
        self.assertTrue(payload)
        records = [
            item
            for item in payload
            if item["path"] == "homeworks/1_3-good/homework.yaml"
        ]
        self.assertTrue(records, payload)
        self.assertEqual("ERROR", records[0]["status"])
        self.assertIn("found unhashable key", records[0]["reason"])
        self.assertNotIn("Traceback", result.stderr)

    def test_composed_key_in_task_frontmatter_is_error(self):
        text = "---\n? [a, b]\n: c\n---\n\n# T\n\nbody\n"
        self.write_homework(task_text=text)
        result = self.run_fixture("--json")
        self.assertEqual(1, result.returncode, combined(result))
        payload = json.loads(result.stdout)
        self.assertIsInstance(payload, list)
        self.assertTrue(payload)
        records = [
            item
            for item in payload
            if item["path"] == "homeworks/1_3-good/task.md"
        ]
        self.assertTrue(records, payload)
        self.assertEqual("ERROR", records[0]["status"])
        self.assertIn("found unhashable key", records[0]["reason"])
        self.assertNotIn("Traceback", result.stderr)

    def test_oversized_document_is_error(self):
        text = document(optional=False) + "# " + ("x" * (64 * 1024)) + "\n"
        self.write_homework(text)
        self.assert_rejected(self.run_fixture(), "larger than 65536 bytes")


class HostileNestingTests(FixtureBase):
    """CR-01/T-10-28: the shared loader bounds nesting for every caller."""

    def test_deeply_nested_metadata_is_an_error_record_not_a_traceback(self):
        self.write_homework(text=DEEP_YAML)
        result = self.run_fixture()
        self.assertIn(": ERROR — ", result.stdout, combined(result))
        self.assertIn("nesting depth", result.stdout, combined(result))
        self.assertNotIn("Traceback", combined(result))

    def test_deeply_nested_task_frontmatter_is_an_error_record_not_a_traceback(self):
        self.write_homework(task_text=DEEP_FRONTMATTER)
        result = self.run_fixture()
        self.assertEqual(1, result.returncode, combined(result))
        self.assertIn(": ERROR — ", result.stdout, combined(result))
        self.assertIn("nesting depth", result.stdout, combined(result))
        self.assertNotIn("Traceback", combined(result))

    def test_deeply_nested_task_frontmatter_json_contract(self):
        self.write_homework(task_text=DEEP_FRONTMATTER)
        result = self.run_fixture("--json")
        self.assertEqual(1, result.returncode, combined(result))
        records = json.loads(result.stdout)
        self.assertIsInstance(records, list)
        self.assertTrue(records, result.stdout)
        matching = [
            item
            for item in records
            if item.get("path") == "homeworks/1_3-good/task.md"
            and item.get("status") == "ERROR"
            and "nesting depth" in item.get("reason", "")
        ]
        self.assertTrue(matching, records)
        for item in records:
            with self.subTest(record=item):
                self.assertEqual({"path", "status", "reason"}, set(item))


class ToolchainTests(FixtureBase):
    """The toolchain pins are cross-checked against the shared configuration."""

    def test_platform_mismatch_is_error(self):
        text = document(optional=False).replace(
            "platform: espressif32@8.0.0", "platform: espressif32@9.9.9"
        )
        self.write_homework(text)
        self.assert_rejected(self.run_fixture(), "toolchain.platform")

    def test_inconsistent_shared_sections_exit_2(self):
        (self.root / "platformio.shared.ini").write_text(
            "[esp32s3_arduino]\n"
            "platform = espressif32@8.0.0\n"
            "[esp32s3_espidf]\n"
            "platform = espressif32@7.0.0\n",
            encoding="utf-8",
        )
        self.write_homework(document(optional=False))
        self.assert_environment_error(self.run_fixture(), "disagree")

    def test_missing_shared_section_exit_2(self):
        (self.root / "platformio.shared.ini").write_text(
            "[esp32s3_arduino]\nplatform = espressif32@8.0.0\n",
            encoding="utf-8",
        )
        self.write_homework(document(optional=False))
        self.assert_environment_error(self.run_fixture(), "esp32s3_espidf")

    def test_missing_shared_ini_exit_2(self):
        (self.root / "platformio.shared.ini").unlink()
        self.write_homework(document(optional=False))
        self.assert_environment_error(self.run_fixture(), "platformio.shared.ini")


class JsonOutputTests(FixtureBase):
    """`--json` is the stable CI surface: records only, no prose."""

    def _mixed_fixture(self):
        self.write_homework(document(optional=False))
        self.write_homework(
            document(homework_id="2_4-bad", optional=False).replace(
                "title: Good homework", "title: Bad\nunexpected: true", 1
            ),
            homework_id="2_4-bad",
        )

    def test_json_records_have_exactly_three_keys(self):
        self._mixed_fixture()
        result = self.run_fixture("--json")
        self.assertEqual(1, result.returncode, combined(result))
        payload = json.loads(result.stdout)
        self.assertEqual(4, len(payload))
        for record in payload:
            with self.subTest(path=record.get("path")):
                self.assertEqual({"path", "status", "reason"}, set(record))

    def test_json_statuses_and_sorting(self):
        self._mixed_fixture()
        result = self.run_fixture("--json")
        payload = json.loads(result.stdout)
        statuses = {record["path"]: record["status"] for record in payload}
        self.assertEqual("OK", statuses["homeworks/1_3-good/homework.yaml"])
        self.assertEqual("OK", statuses["homeworks/1_3-good/task.md"])
        self.assertEqual("ERROR", statuses["homeworks/2_4-bad/homework.yaml"])
        self.assertEqual("OK", statuses["homeworks/2_4-bad/task.md"])
        self.assertEqual(
            sorted(statuses), [record["path"] for record in payload]
        )

    def test_json_real_tree_records_are_all_ok(self):
        # The real tree gained its first homework in Phase 4.2, so the JSON
        # surface is no longer an empty array. What must hold for any shipped
        # tree is that every record is an OK metadata document for a path that
        # exists, that the order is by path, and that no prose reaches stderr.
        result = run_checker("--json")
        self.assertEqual(0, result.returncode, combined(result))
        self.assertEqual("", result.stderr)
        payload = json.loads(result.stdout)
        for record in payload:
            with self.subTest(path=record.get("path")):
                self.assertEqual({"path", "status", "reason"}, set(record))
                self.assertEqual("OK", record["status"], record)
                self.assertTrue(
                    (REPO_ROOT / record["path"]).is_file(), record["path"]
                )
        self.assertEqual(
            sorted(record["path"] for record in payload),
            [record["path"] for record in payload],
        )


class RealTreeTests(unittest.TestCase):
    """The shipped tree passes, and the checker is read-only."""

    def test_real_tree_passes(self):
        result = run_checker()
        self.assertEqual(0, result.returncode, combined(result))
        self.assertIn("PASS: metadata contract satisfied", result.stdout)

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


class SymlinkedDocumentTests(FixtureBase):
    """CR-06: metadata checker must refuse symlinked homework.yaml and task.md."""

    def test_symlinked_homework_yaml_is_refused_without_reading(self):
        outside = self.root.parent / f"{self.root.name}-outside.yaml"
        outside.write_text("id: 1_3-good\ntitle: LEAKME-SECRET\n", encoding="utf-8")
        self.addCleanup(outside.unlink)
        hw_dir = self.root / "homeworks" / "1_3-good"
        hw_dir.mkdir(parents=True, exist_ok=True)
        hw_link = hw_dir / "homework.yaml"
        hw_link.symlink_to(outside)
        self.addCleanup(hw_link.unlink)
        self.write_task(directory="1_3-good")
        result = self.run_fixture()
        self.assertEqual(1, result.returncode, combined(result))
        self.assertIn(": ERROR — ", result.stdout)
        self.assertIn("symlink", result.stdout)
        self.assertNotIn("LEAKME-SECRET", result.stdout)
        self.assertNotIn("LEAKME-SECRET", result.stderr)

    def test_symlinked_task_md_is_refused_without_reading(self):
        outside = self.root.parent / f"{self.root.name}-outside-task.md"
        outside.write_text("# LEAKME-SECRET\n", encoding="utf-8")
        self.addCleanup(outside.unlink)
        self.write_homework(with_task=False)
        hw_dir = self.root / "homeworks" / "1_3-good"
        task_link = hw_dir / "task.md"
        task_link.symlink_to(outside)
        self.addCleanup(task_link.unlink)
        result = self.run_fixture()
        self.assertEqual(1, result.returncode, combined(result))
        self.assertIn(": ERROR — ", result.stdout)
        self.assertIn("symlink", result.stdout)
        self.assertNotIn("LEAKME-SECRET", result.stdout)
        self.assertNotIn("LEAKME-SECRET", result.stderr)

    def test_broken_symlinks_are_refused_as_symlinks(self):
        hw_dir = self.root / "homeworks" / "1_3-good"
        hw_dir.mkdir(parents=True, exist_ok=True)
        hw_link = hw_dir / "homework.yaml"
        hw_link.symlink_to(self.root / "non-existent-target.yaml")
        self.addCleanup(hw_link.unlink)
        self.write_task(directory="1_3-good")
        result = self.run_fixture()
        self.assertEqual(1, result.returncode, combined(result))
        self.assertIn(": ERROR — ", result.stdout)
        self.assertIn("symlink", result.stdout)
        self.assertNotIn("missing", result.stdout)


class CanonicalIdTest(unittest.TestCase):
    """One literal, checked in three places at once."""

    def test_canonical_id_literal_is_identical_in_three_places(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        schema_pattern = schema["properties"]["id"]["pattern"]

        contract_source = CONTRACT.read_text(encoding="utf-8")
        match = re.search(
            r'HOMEWORK_ID = re\.compile\(r"([^"]+)"\)', contract_source
        )
        self.assertIsNotNone(match, "HOMEWORK_ID literal not found in paths.py")

        agents_text = AGENTS.read_text(encoding="utf-8")
        spans = [
            span
            for span in re.findall(r"`([^`\n]+)`", agents_text)
            if span.startswith("^") and span.endswith("$")
        ]
        self.assertEqual(
            1,
            len(spans),
            f"expected exactly one anchored pattern in AGENTS.md, found {spans}",
        )

        self.assertEqual(
            {schema_pattern, match.group(1), spans[0]},
            {EXPECTED_PATTERN},
            "the canonical homework-ID literal drifted between its three homes",
        )


class CliContractTests(unittest.TestCase):
    """The command-line surface is stable for Phase 8 CI."""

    def test_help_exits_zero(self):
        result = run_checker("--help")
        self.assertEqual(0, result.returncode, combined(result))
        self.assertIn("homework metadata contract", result.stdout)

    def test_unknown_argument_exits_two(self):
        # argparse owns this failure path and prints its own usage; the exit
        # code, not our ERROR prefix, is the contract.
        result = run_checker("--no-such-option")
        self.assertEqual(2, result.returncode, combined(result))
        self.assertIn("unrecognized arguments", result.stderr)


if __name__ == "__main__":
    unittest.main()
