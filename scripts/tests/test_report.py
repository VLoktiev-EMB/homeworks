"""Prove the report and evidence contract end to end.

The checker is invoked as a subprocess (`uv run scripts/check_report.py`)
because it reads `homework.yaml` with PyYAML, and this suite stays
dependency-free: no test module may import PyYAML or jsonschema. Every fixture
is a temporary root that contains one `homeworks/<id>/` directory, so the real
tree is never touched and a negative case can fail only because of its single
mutation. `RealTreeTests` additionally reads the shipped tree and proves the
repository itself satisfies the contract.

Coverage: one rule id per fixture for the lifecycle family (`RPT-001` ... `RPT-004`)
and the structure family (`RPT-101` ... `RPT-108`), a compliant report, a fenced
heading, the section-5 not-applicable waiver, the section-7 extra subsection,
determinism, the `--json` shape, the stdlib-only import boundary, and the
real-tree pass that locks the retrofitted worked example.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.report import contract, markdown, tables
from scripts.report.vocabulary import REPORT_HEADINGS, REPORT_MAX_BYTES, RULES

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_report.py"
PACKAGE = REPO_ROOT / "scripts" / "report"

# The seven contracted tables as literals a test can mutate in one place.
SECTION_ONE_TABLE = (
    "| Field | Value |\n|-------|-------|\n"
    "| Homework ID | `1_3-good` |\n"
    "| Title | Good homework |\n"
    "| Board | ESP32-S3-DevKitC-1 (N16R8: 16 MB flash, 8 MB octal PSRAM) |\n"
    "| Framework | Arduino |\n"
    "| Language | C++ composition root; pure C pattern library |\n"
    "| PlatformIO Core | 6.2.0 |\n"
    "| Platform | `platformio/espressif32` 8.0.0 |\n"
    "| Homework status | `in-progress` |\n"
    "| Report status | `draft` |\n"
    "| Implementation commit | `9e1238d` |"
)

ASSUMPTIONS_TABLE = (
    "| ID | Assumption | Impact if wrong | Validation |\n"
    "|----|------------|-----------------|------------|\n"
    "| A-01 | The rail is 3.3 V. | The LED current shifts. | Measure the rail. |"
)

BOM_TABLE = (
    "| Ref | Part or value | Quantity | Package | Source or link | Notes |\n"
    "|-----|---------------|----------|---------|----------------|-------|\n"
    "| esp | ESP32-S3-DevKitC-1 | 1 | module | n/a | The board. |\n"
    "| r1 | 150 ohm resistor | 1 | axial | n/a | Series resistor. |"
)

PIN_MAP_TABLE = (
    "| Signal | Pin | Connects to | Notes |\n"
    "|--------|-----|-------------|-------|\n"
    "| LED A | GPIO4 | `r1:1` | Half-bridge drive. |"
)

CALCULATIONS_TABLE = (
    "| ID | Quantity | Formula | Units | Input provenance | Result | Uncertainty | "
    "Assumption effect |\n"
    "|----|----------|---------|-------|------------------|--------|-------------|"
    "-------------------|\n"
    "| C-01 | LED current | `I = (Vs - Vf) / R` | mA | `Vs = 3.3 V` datasheet | "
    "`I = 9.33 mA` | plus or minus 1.4 mA | A lower Vf raises the current. |"
)

SAFETY_LIST = "- **3V3-to-ground short.** Check continuity before applying power."

# D-37: the two section-7 claim paragraphs the metadata promises.
NATIVE_PARAGRAPH = "**Native suite.** 38 of 38 cases pass in 1.429 s."
SIMULATION_PARAGRAPH = "**Simulation.** The scenario was executed: all three runs exited 0."

# CR-01: ~2 KB of valid YAML syntax that exhausts a recursive composer with
# 1,000 nested flow sequences. It sits inside every declared size gate, so only
# a nesting bound can turn it into a content record (T-10-28).
DEEP_YAML = "title: " + "[" * 1000 + "]" * 1000 + "\n"

# CR-02: 200,000 bytes of `[` — inside the 1 MiB report bound, but deep enough
# to exhaust `json.loads` before it can report malformed JSON (T-10-29).
DEEP_DIAGRAM = "[" * 100_000

LEDGER_TABLE = (
    "| ID | Quantity | Value | Label | Instrument | Method | Uncertainty | "
    "Implementation commit |\n"
    "|----|----------|-------|-------|------------|--------|-------------|"
    "-----------------------|\n"
    "| L-01 | Supply voltage | not measured: bench offline | not measured | multimeter | "
    "DC volts across the rail | not applicable: no reading | `9e1238d` |"
)

TRACEABILITY_TABLE = (
    "| ID | Claim or requirement | Design artifact | Verification method | Evidence | Status |\n"
    "|----|----------------------|-----------------|---------------------|----------|--------|\n"
    "| T-01 | Target build | `platformio.ini` | `pio run` | `SUCCESS` | verified |\n"
    "| T-02 | Report contract REPORT-01, REPORT-02, REPORT-03, REPORT-04, REPORT-05, "
    "REPORT-06, REPORT-07, REPORT-08 | `report.md` | manual review | this report | manual |"
)

# The body of every numbered section. A test mutates one entry or drops one
# heading, so a failing fixture differs from the compliant report in exactly
# one place.
SECTION_BODIES = {
    "1. Title and Metadata": SECTION_ONE_TABLE,
    "2. Objective": "The objective.",
    "3. Assumptions": (
        "Each assumption names its consequence and validation.\n\n" + ASSUMPTIONS_TABLE
    ),
    "4. Theory": "The theory [1].\n\n### Limitations\n\nNone.",
    "5. Hardware and Wiring": (
        "The wiring.\n\n"
        "### Bill of Materials\n\n" + BOM_TABLE + "\n\n"
        "### Pin Map\n\n" + PIN_MAP_TABLE + "\n\n"
        "### Electrical Calculations\n\n" + CALCULATIONS_TABLE + "\n\n"
        "### Safety Checklist\n\n" + SAFETY_LIST
    ),
    "6. Methodology": "The method.",
    "7. Results": (
        "The results.\n\n"
        "**Target build.** The target build passes.\n\n"
        + NATIVE_PARAGRAPH
        + "\n\n"
        + SIMULATION_PARAGRAPH
        + "\n\n"
        "### Measurement Ledger\n\n" + LEDGER_TABLE + "\n\n"
        "### Traceability Matrix\n\n" + TRACEABILITY_TABLE
    ),
    "8. Analysis": "Industry note: a non-blocking loop keeps the beacon responsive.",
    "9. Conclusions": "Status: the homework is in progress.\n\n### Next Steps\n\n- Tag the pilot.",
    "10. References": "[1] A reference.",
}


def compliant_report(sections=None, order=None):
    """Assemble a report that satisfies every rule this plan owns."""
    content = dict(SECTION_BODIES)
    if sections:
        content.update(sections)
    titles = order if order is not None else REPORT_HEADINGS
    parts = ["# Good homework"]
    for title in titles:
        parts.append(f"## {title}\n\n{content[title]}\n")
    return "\n".join(parts)


def homework_yaml(
    *,
    homework_id="1_3-good",
    status="in-progress",
    report_status="draft",
    with_report=True,
    native=True,
    simulation_status=None,
):
    """Assemble one `homework.yaml` payload, never with a `yaml` import."""
    lines = [
        "schema_version: 1",
        f'id: "{homework_id}"',
        'title: "Good homework"',
        "board: esp32-s3-devkitc-1",
        "framework: arduino",
        "language: cpp",
        f"status: {status}",
        "source:",
        "  reference: https://example.com/homeworks",
        "toolchain:",
        '  platformio: "6.2.0"',
        '  platform: "espressif32@8.0.0"',
    ]
    if simulation_status is not None:
        lines.extend(
            [
                "simulation:",
                "  tool: wokwi",
                "  diagram: assets/diagram.json",
                f"  status: {simulation_status}",
            ]
        )
    lines.extend(
        [
            "tests:",
            "  framework: unity",
            f"  native: {'true' if native else 'false'}",
            "  coverage: false",
        ]
    )
    if with_report:
        lines.extend(["report:", "  path: report.md", f"  status: {report_status}"])
    return "\n".join(lines) + "\n"


def default_diagram(parts=("esp", "r1")):
    """Return a diagram payload whose part ids cover the fixture BOM refs."""
    return json.dumps(
        {
            "version": 1,
            "parts": [{"id": part} for part in parts],
            "connections": [],
        }
    )


def run_report_checker(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
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


def setUpModule():
    """Warm uv's script environment before the first asserted run.

    Environment creation can print an install line on stderr once; a warm run
    keeps the determinism assertion about the checker, not about uv.
    """
    result = run_report_checker("--help")
    if result.returncode != 0:
        raise RuntimeError(f"uv could not run the checker: {combined(result)}")


class FixtureBase(unittest.TestCase):
    """A temporary root with one homework directory."""

    homework_id = "1_3-good"

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="report-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def write_homework(self, text=None, homework_id=None):
        homework_id = homework_id or self.homework_id
        path = self.root / "homeworks" / homework_id / "homework.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        if text is None:
            text = homework_yaml(homework_id=homework_id)
        path.write_text(text, encoding="utf-8")
        return path

    def write_diagram(self, text=None, homework_id=None):
        homework_id = homework_id or self.homework_id
        path = self.root / "homeworks" / homework_id / "assets" / "diagram.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if text is None:
            text = default_diagram()
        path.write_text(text, encoding="utf-8")
        return path

    def write_artifact(self, relative, text="placeholder\n", homework_id=None):
        homework_id = homework_id or self.homework_id
        path = self.root / "homeworks" / homework_id / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_report(self, text=None, homework_id=None, with_diagram=True):
        homework_id = homework_id or self.homework_id
        path = self.root / "homeworks" / homework_id / "report.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        if text is None:
            text = compliant_report()
        path.write_text(text, encoding="utf-8")
        # The fixture's traceability row names `platformio.ini`, so the file
        # exists for RPT-307. This is the second artifact the fixture carries
        # after the diagram, for the same reason: a rule now consumes it.
        self.write_artifact("platformio.ini", homework_id=homework_id)
        if with_diagram:
            self.write_diagram(homework_id=homework_id)
        return path

    def run_fixture(self, *args):
        return run_report_checker("--dir", str(self.root), *args)

    def assert_accepted(self, result):
        self.assertEqual(0, result.returncode, combined(result))
        self.assertIn(": OK — ", result.stdout)

    def assert_rejected(self, result, fragment=None):
        self.assertEqual(1, result.returncode, combined(result))
        self.assertIn(": ERROR ", result.stdout)
        if fragment:
            self.assertIn(fragment, result.stdout)

    def assert_environment_error(self, result, fragment=None):
        self.assertEqual(2, result.returncode, combined(result))
        self.assertIn("ERROR:", result.stderr)
        if fragment:
            self.assertIn(fragment, result.stderr)


class TracerTests(FixtureBase):
    """The tracer slice: one rule family through the real CLI and exit codes."""

    def test_tracer_compliant_fixture_passes_with_one_ok_record(self):
        self.write_homework()
        self.write_report()
        result = self.run_fixture()
        self.assert_accepted(result)
        self.assertIn("PASS: report contract satisfied", result.stdout)
        self.assertEqual(1, result.stdout.count(": OK — "), combined(result))

    def test_tracer_missing_heading_reports_rpt_101_with_a_line(self):
        self.write_homework()
        order = [title for title in REPORT_HEADINGS if title != "4. Theory"]
        self.write_report(compliant_report(order=order))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-101]")
        self.assertIn(":0: ERROR [RPT-101]", result.stdout)
        self.assertIn("4. Theory", result.stdout)
        self.assertIn("FAIL: 1 report violation(s)", result.stdout)

    def test_tracer_json_carries_rule_and_line(self):
        self.write_homework()
        order = [title for title in REPORT_HEADINGS if title != "4. Theory"]
        self.write_report(compliant_report(order=order))
        result = self.run_fixture("--json")
        self.assertEqual(1, result.returncode, combined(result))
        payload = json.loads(result.stdout)
        self.assertTrue(all({"rule", "line"} <= set(item) for item in payload))
        self.assertIn("RPT-101", {item["rule"] for item in payload})

    def test_tracer_help_exits_zero_and_names_dir(self):
        result = run_report_checker("--help")
        self.assertEqual(0, result.returncode, combined(result))
        self.assertIn("--dir", result.stdout)

    def test_tracer_non_directory_positional_is_exit_two(self):
        self.write_homework()
        self.write_report()
        result = self.run_fixture("missing-directory")
        self.assert_environment_error(result, "no homework directory")

    def test_tracer_package_imports_no_third_party_module(self):
        forbidden = {"yaml", "jsonschema"}
        for path in sorted(PACKAGE.glob("*.py")):
            with self.subTest(module=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                roots = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        roots.update(alias.name.split(".")[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        roots.add(node.module.split(".")[0])
                self.assertEqual(set(), roots & forbidden, f"{path.name} imports a third party")


class HeadingsTests(FixtureBase):
    """One failing fixture and one passing counterpart per structure rule."""

    def swapped_order(self):
        order = list(REPORT_HEADINGS)
        order[2], order[3] = order[3], order[2]
        return order

    def test_headings_fenced_heading_is_invisible_and_true_line_survives(self):
        sections = {
            "2. Objective": "```text\n## 9. Conclusions\n```\n\nAfter the fence.",
        }
        report = compliant_report(sections=sections, order=self.swapped_order())
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-102]")
        self.assertNotIn("[RPT-103]", result.stdout)
        expected = report.splitlines().index("## 3. Assumptions") + 1
        self.assertIn(f":{expected}: ERROR [RPT-102]", result.stdout)

    def test_headings_out_of_order_reports_rpt_102(self):
        self.write_homework()
        self.write_report(compliant_report(order=self.swapped_order()))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-102]")
        self.assertIn("out of ascending order", result.stdout)

    def test_headings_duplicate_reports_rpt_103(self):
        order = list(REPORT_HEADINGS)
        order.insert(2, "2. Objective")
        self.write_homework()
        self.write_report(compliant_report(order=order))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-103]")
        self.assertIn('duplicate heading "2. Objective"', result.stdout)
        self.assertNotIn("[RPT-102]", result.stdout)

    def test_headings_missing_subsection_reports_rpt_104(self):
        self.write_homework()
        self.write_report(compliant_report(sections={"4. Theory": "The theory."}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-104]")
        self.assertIn('required subsection "Limitations"', result.stdout)

    def test_headings_not_applicable_without_reason_reports_rpt_105(self):
        self.write_homework()
        self.write_report(compliant_report(sections={"3. Assumptions": "_Not applicable._"}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-105]")

    def test_headings_not_applicable_in_forbidden_section_reports_rpt_106(self):
        sections = {"2. Objective": "_Not applicable — no objective._"}
        self.write_homework()
        self.write_report(compliant_report(sections=sections))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-106]")
        self.assertIn('section "2. Objective"', result.stdout)

    def test_headings_section_five_not_applicable_waives_subsections(self):
        sections = {
            "5. Hardware and Wiring": "_Not applicable — software-only assignment._",
        }
        self.write_homework()
        self.write_report(compliant_report(sections=sections))
        self.assert_accepted(self.run_fixture())

    def test_headings_section_seven_extra_subsection_passes(self):
        sections = {
            "7. Results": (
                "The results.\n\n" + NATIVE_PARAGRAPH + "\n\n"
                "### Measurement Ledger\n\n" + LEDGER_TABLE + "\n\n"
                "### Interpreting the Forward-Voltage Row\n\nThe interpretation.\n\n"
                "### Traceability Matrix\n\n" + TRACEABILITY_TABLE
            ),
        }
        self.write_homework()
        self.write_report(compliant_report(sections=sections))
        self.assert_accepted(self.run_fixture())

    def test_headings_missing_industry_note_reports_rpt_107(self):
        sections = {"8. Analysis": "The analysis without the required note."}
        self.write_homework()
        self.write_report(compliant_report(sections=sections))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-107]")
        self.assertIn('beginning "Industry note:"', result.stdout)

    def test_headings_missing_status_paragraph_reports_rpt_108(self):
        sections = {"9. Conclusions": "### Next Steps\n\n- Tag the pilot."}
        self.write_homework()
        self.write_report(compliant_report(sections=sections))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-108]")
        self.assertIn('beginning "Status:"', result.stdout)


class LifecycleTests(FixtureBase):
    """Status gating, the placeholder exemption, the bound and determinism."""

    def test_lifecycle_planned_without_report_block_is_ok(self):
        self.write_homework(homework_yaml(status="planned", with_report=False))
        result = self.run_fixture()
        self.assert_accepted(result)
        self.assertIn("no report declared", result.stdout)

    def test_lifecycle_in_progress_without_report_block_is_rpt_001(self):
        self.write_homework(homework_yaml(status="in-progress", with_report=False))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-001]")

    def test_lifecycle_in_progress_with_placeholder_is_rpt_003(self):
        self.write_homework(homework_yaml(status="in-progress", report_status="placeholder"))
        self.write_report("TODO: skeleton.\n")
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-003]")

    def test_lifecycle_placeholder_report_without_headings_is_exempt(self):
        self.write_homework(homework_yaml(status="planned", report_status="placeholder"))
        self.write_report("TODO: skeleton.\n")
        result = self.run_fixture()
        self.assert_accepted(result)
        self.assertIn("placeholder", result.stdout)

    def test_lifecycle_empty_report_is_rpt_002(self):
        self.write_homework()
        self.write_report("")
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-002]")
        self.assertIn("empty", result.stdout)

    def test_lifecycle_absent_report_is_rpt_002(self):
        self.write_homework()
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-002]")
        self.assertIn("absent", result.stdout)

    def test_lifecycle_symlink_report_is_rpt_002(self):
        self.write_homework()
        target = self.root / "outside-report.md"
        target.write_text("outside\n", encoding="utf-8")
        path = self.root / "homeworks" / self.homework_id / "report.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-002]")
        self.assertIn("symlink", result.stdout)

    def test_lifecycle_oversized_report_is_rpt_004(self):
        self.write_homework()
        self.write_report("x" * (1024 * 1024 + 1))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-004]")
        self.assertIn(str(1024 * 1024 + 1), result.stdout)

    def test_lifecycle_two_runs_are_byte_identical(self):
        self.write_homework()
        self.write_report()
        first = self.run_fixture()
        second = self.run_fixture()
        self.assertEqual(0, first.returncode, combined(first))
        self.assertEqual(first.stdout, second.stdout)

    def test_lifecycle_json_and_text_agree_on_record_count(self):
        self.write_homework()
        order = [title for title in REPORT_HEADINGS if title != "4. Theory"]
        self.write_report(compliant_report(order=order))
        text_result = self.run_fixture()
        json_result = self.run_fixture("--json")
        text_records = [
            line
            for line in text_result.stdout.splitlines()
            if ": ERROR " in line or ": OK — " in line
        ]
        self.assertEqual(len(text_records), len(json.loads(json_result.stdout)))


class HostileMetadataTests(FixtureBase):
    """CR-01/T-10-28: a hostile `homework.yaml` is a record, not a traceback."""

    def test_deeply_nested_metadata_is_rpt_001_not_a_traceback(self):
        self.write_homework(DEEP_YAML)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-001]")
        self.assertNotIn("Traceback", combined(result))

    def test_deeply_nested_metadata_keeps_the_json_contract(self):
        self.write_homework(DEEP_YAML)
        result = self.run_fixture("--json")
        self.assertEqual(1, result.returncode, combined(result))
        records = json.loads(result.stdout)
        self.assertTrue(records, result.stdout)
        self.assertIn("RPT-001", {item["rule"] for item in records})
        for item in records:
            with self.subTest(record=item):
                self.assertEqual(
                    {"path", "status", "rule", "line", "reason"}, set(item)
                )


class IdentityTests(FixtureBase):
    """`RPT-401`/`RPT-402`/`RPT-403`: identity against normalized metadata."""

    def section_one(self, old, new):
        return compliant_report(
            sections={"1. Title and Metadata": SECTION_ONE_TABLE.replace(old, new)}
        )

    def test_identity_live_report_identity_matches(self):
        result = run_report_checker("--json")
        self.assertEqual(0, result.returncode, combined(result))
        rules = {item["rule"] for item in json.loads(result.stdout)}
        self.assertEqual(set(), rules & {"RPT-401", "RPT-402", "RPT-403"})

    def test_identity_compliant_fixture_passes(self):
        self.write_homework()
        self.write_report()
        self.assert_accepted(self.run_fixture())

    def test_identity_h1_mismatch_reports_rpt_401(self):
        report = compliant_report().replace("# Good homework", "# Another title", 1)
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-401]")
        self.assertIn("does not match homework.yaml title", result.stdout)

    def test_identity_missing_h1_reports_rpt_401(self):
        report = compliant_report().replace("# Good homework\n", "", 1)
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-401]")
        self.assertIn("expected exactly one", result.stdout)

    def test_identity_duplicate_h1_reports_rpt_401(self):
        report = compliant_report().replace(
            "# Good homework\n", "# Good homework\n\n# Second title\n", 1
        )
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-401]")
        self.assertIn("expected exactly one", result.stdout)

    def test_identity_homework_id_mismatch_reports_rpt_402_naming_field(self):
        report = self.section_one("`1_3-good`", "`1_3-other`")
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-402]")
        self.assertIn('"Homework ID"', result.stdout)
        self.assertIn("expected '1_3-good'", result.stdout)

    def test_identity_title_cell_mismatch_reports_rpt_402_naming_field(self):
        report = self.section_one("| Title | Good homework |", "| Title | Another title |")
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-402]")
        self.assertIn('"Title"', result.stdout)

    def test_identity_homework_status_mismatch_reports_rpt_402(self):
        report = self.section_one("`in-progress`", "`complete`")
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-402]")
        self.assertIn('"Homework status"', result.stdout)

    def test_identity_report_status_mismatch_reports_rpt_402(self):
        report = self.section_one("| Report status | `draft` |", "| Report status | `complete` |")
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-402]")
        self.assertIn('"Report status"', result.stdout)

    def test_identity_backticked_report_status_passes(self):
        # Both the backticked cell the worked example uses and a plain cell
        # compare equal after `normalize_cell`.
        self.write_homework()
        for cell in ("`draft`", "draft"):
            with self.subTest(cell=cell):
                report = self.section_one(
                    "| Report status | `draft` |", f"| Report status | {cell} |"
                )
                self.write_report(report)
                self.assert_accepted(self.run_fixture())

    def test_identity_framework_case_insensitive_passes(self):
        report = self.section_one("| Framework | Arduino |", "| Framework | arduino |")
        self.write_homework()
        self.write_report(report)
        self.assert_accepted(self.run_fixture())

    def test_identity_framework_mismatch_reports_rpt_403_naming_field(self):
        report = self.section_one("| Framework | Arduino |", "| Framework | ESP-IDF |")
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-403]")
        self.assertIn('"Framework"', result.stdout)

    def test_identity_platformio_core_mismatch_reports_rpt_403(self):
        report = self.section_one("| PlatformIO Core | 6.2.0 |", "| PlatformIO Core | 6.1.0 |")
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-403]")
        self.assertIn('"PlatformIO Core"', result.stdout)

    def test_identity_platform_spellings_compare_equal(self):
        report = self.section_one(
            "`platformio/espressif32` 8.0.0",
            "espressif32@8.0.0",
        )
        self.write_homework()
        self.write_report(report)
        self.assert_accepted(self.run_fixture())

    def test_identity_platform_mismatch_reports_rpt_403(self):
        report = self.section_one(
            "`platformio/espressif32` 8.0.0",
            "`platformio/espressif32` 7.0.0",
        )
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-403]")
        self.assertIn('"Platform"', result.stdout)

    def test_identity_board_and_language_display_prose_passes(self):
        # The default fixture writes a prose board description and a prose
        # language cell against a slug and a `cpp`; neither is compared.
        self.write_homework()
        self.write_report()
        self.assert_accepted(self.run_fixture())


class LanguageTests(FixtureBase):
    """`RPT-405`/`RPT-406`: English-only text and no authoring sentinel."""

    def test_language_compliant_fixture_passes(self):
        self.write_homework()
        self.write_report()
        self.assert_accepted(self.run_fixture())

    def test_language_live_report_is_english_and_sentinel_free(self):
        result = run_report_checker("--json")
        self.assertEqual(0, result.returncode, combined(result))
        rules = {item["rule"] for item in json.loads(result.stdout)}
        self.assertEqual(set(), rules & {"RPT-405", "RPT-406"})

    def test_language_cyrillic_word_reports_rpt_405_with_line(self):
        body = "The objective contains тест."
        report = compliant_report(sections={"2. Objective": body})
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-405]")
        expected = report.splitlines().index(body) + 1
        self.assertIn(f":{expected}: ERROR [RPT-405]", result.stdout)
        self.assertIn("Cyrillic character", result.stdout)

    def test_language_cyrillic_supplement_reports_rpt_405(self):
        body = "A supplement codepoint Ԁ is Cyrillic."
        report = compliant_report(sections={"2. Objective": body})
        self.write_homework()
        self.write_report(report)
        self.assert_rejected(self.run_fixture(), "[RPT-405]")

    def test_language_todo_in_draft_reports_rpt_406_with_line(self):
        body = "TODO: finish the objective."
        report = compliant_report(sections={"2. Objective": body})
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-406]")
        expected = report.splitlines().index(body) + 1
        self.assertIn(f":{expected}: ERROR [RPT-406]", result.stdout)
        self.assertIn('sentinel "TODO"', result.stdout)

    def test_language_tbd_in_complete_reports_rpt_406(self):
        self.write_homework(homework_yaml(report_status="complete"))
        self.write_report(compliant_report(sections={"2. Objective": "TBD objective."}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-406]")
        self.assertIn('sentinel "TBD"', result.stdout)

    def test_language_todo_in_placeholder_passes(self):
        self.write_homework(homework_yaml(status="planned", report_status="placeholder"))
        self.write_report("TODO: skeleton.\n")
        result = self.run_fixture()
        self.assert_accepted(result)
        self.assertIn("placeholder", result.stdout)


class LinkTests(FixtureBase):
    """`RPT-404`: relative Markdown links and images resolve without I/O."""

    def test_link_live_report_links_resolve(self):
        result = run_report_checker("--json")
        self.assertEqual(0, result.returncode, combined(result))
        rules = {item["rule"] for item in json.loads(result.stdout)}
        self.assertEqual(set(), rules & {"RPT-404"})

    def test_link_live_report_has_two_relative_links(self):
        text = (REPO_ROOT / "homeworks" / "1_3-police-flasher" / "report.md").read_text(
            encoding="utf-8"
        )
        targets = [target for _, target in contract.link_targets(text.splitlines())]
        self.assertEqual(["assets/diagram.json", "assets/diagram.json"], targets)

    def test_link_compliant_fixture_passes(self):
        self.write_homework()
        self.write_report()
        self.assert_accepted(self.run_fixture())

    def test_link_missing_target_reports_rpt_404_with_line(self):
        body = "See [the diagram](assets/missing.json)."
        report = compliant_report(sections={"2. Objective": body})
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-404]")
        expected = report.splitlines().index(body) + 1
        self.assertIn(f":{expected}: ERROR [RPT-404]", result.stdout)
        self.assertIn("assets/missing.json", result.stdout)

    def test_link_escaping_target_reports_rpt_404(self):
        body = "See [passwd](../../../etc/passwd)."
        self.write_homework()
        self.write_report(compliant_report(sections={"2. Objective": body}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-404]")
        self.assertIn("../../../etc/passwd", result.stdout)

    def test_link_external_url_is_skipped_without_resolution(self):
        targets = [
            target
            for _, target in contract.link_targets(["[x](https://example.invalid)"])
        ]
        self.assertEqual([], targets)

    def test_link_external_url_fixture_passes(self):
        self.write_homework()
        self.write_report(
            compliant_report(sections={"2. Objective": "See [the site](https://example.invalid)."})
        )
        self.assert_accepted(self.run_fixture())

    def test_link_title_and_fragment_are_stripped(self):
        lines = [
            '[x](assets/diagram.json "a title")',
            "[x](assets/diagram.json#section)",
            "[x](assets/diagram.json?rev=1)",
        ]
        targets = [target for _, target in contract.link_targets(lines)]
        self.assertEqual(["assets/diagram.json"] * 3, targets)

    def test_link_image_target_is_checked(self):
        self.write_homework()
        self.write_report(
            compliant_report(sections={"2. Objective": "![d](assets/missing.png)"})
        )
        self.assert_rejected(self.run_fixture(), "[RPT-404]")

    def test_link_inside_a_fence_is_invisible(self):
        fence = "```text\n[x](assets/missing.json)\n```"
        self.write_homework()
        self.write_report(compliant_report(sections={"2. Objective": fence}))
        self.assert_accepted(self.run_fixture())


class StatusClaimsTests(FixtureBase):
    """`RPT-407`/`RPT-408`: section-7 claims agree with homework.yaml (D-37)."""

    def results(self, old, new):
        body = SECTION_BODIES["7. Results"].replace(old, new)
        return compliant_report(sections={"7. Results": body})

    def test_status_claims_live_report_passes(self):
        result = run_report_checker("--json")
        self.assertEqual(0, result.returncode, combined(result))
        rules = {item["rule"] for item in json.loads(result.stdout)}
        self.assertEqual(set(), rules & {"RPT-407", "RPT-408"})

    def test_status_claims_compliant_fixture_passes(self):
        self.write_homework()
        self.write_report()
        self.assert_accepted(self.run_fixture())

    def test_status_claims_native_false_waives_rpt_407(self):
        self.write_homework(homework_yaml(native=False))
        self.write_report(self.results(NATIVE_PARAGRAPH + "\n\n", ""))
        self.assert_accepted(self.run_fixture())

    def test_status_claims_native_true_missing_paragraph_reports_rpt_407(self):
        self.write_homework(homework_yaml(native=True))
        self.write_report(self.results(NATIVE_PARAGRAPH + "\n\n", ""))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-407]")
        self.assertIn("tests.native is true", result.stdout)

    def test_status_claims_missing_simulation_paragraph_reports_rpt_408(self):
        self.write_homework(homework_yaml(simulation_status="verified"))
        self.write_report(self.results(SIMULATION_PARAGRAPH + "\n\n", ""))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-408]")
        self.assertIn('beginning "**Simulation.**"', result.stdout)

    def test_status_claims_verified_without_run_claim_reports_rpt_408(self):
        self.write_homework(homework_yaml(simulation_status="verified"))
        self.write_report(
            self.results(
                SIMULATION_PARAGRAPH,
                "**Simulation.** The scenario is described in the methodology.",
            )
        )
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-408]")
        self.assertIn("simulation.status is verified", result.stdout)

    def test_status_claims_pending_with_run_claim_reports_rpt_408(self):
        self.write_homework(homework_yaml(simulation_status="pending"))
        self.write_report()
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-408]")
        self.assertIn("simulation.status is pending", result.stdout)

    def test_status_claims_pending_paragraph_naming_phase_passes(self):
        self.write_homework(homework_yaml(simulation_status="pending"))
        self.write_report(
            self.results(
                SIMULATION_PARAGRAPH,
                "**Simulation.** Simulation execution is pending; Phase 11 owns the runs.",
            )
        )
        self.assert_accepted(self.run_fixture())

    def test_status_claims_no_simulation_and_native_false_is_silent(self):
        self.write_homework(homework_yaml(native=False, simulation_status=None))
        self.write_report(self.results(NATIVE_PARAGRAPH + "\n\n", ""))
        result = self.run_fixture()
        self.assert_accepted(result)
        self.assertNotIn("[RPT-407]", result.stdout)
        self.assertNotIn("[RPT-408]", result.stdout)


class PinMapTests(FixtureBase):
    """`RPT-201`: every required table is matched by its exact header literal."""

    def test_pin_map_compliant_report_passes(self):
        self.write_homework()
        self.write_report()
        self.assert_accepted(self.run_fixture())

    def test_pin_map_renamed_column_reports_rpt_201_naming_table_and_line(self):
        body = SECTION_BODIES["5. Hardware and Wiring"].replace(
            "| Signal | Pin | Connects to | Notes |",
            "| Signal | ESP32-S3 pin | Connects to | Notes |",
        )
        report = compliant_report(sections={"5. Hardware and Wiring": body})
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-201]")
        self.assertIn('table "pin map"', result.stdout)
        self.assertIn("ESP32-S3 pin", result.stdout)
        expected = report.splitlines().index("| Signal | ESP32-S3 pin | Connects to | Notes |") + 1
        self.assertIn(f":{expected}: ERROR [RPT-201]", result.stdout)

    def test_pin_map_every_required_header_is_matched_verbatim(self):
        cases = (
            (
                "section 1 metadata",
                "1. Title and Metadata",
                "| Field | Value |",
                "| Field | Amount |",
            ),
            (
                "assumptions",
                "3. Assumptions",
                "| ID | Assumption | Impact if wrong | Validation |",
                "| ID | Assumption | Impact | Validation |",
            ),
            (
                "bill of materials",
                "5. Hardware and Wiring",
                "| Ref | Part or value | Quantity | Package | Source or link | Notes |",
                "| Ref | Part or value | Quantity | Package | Source or link | Remark |",
            ),
            (
                "pin map",
                "5. Hardware and Wiring",
                "| Signal | Pin | Connects to | Notes |",
                "| Signal | ESP32-S3 pin | Connects to | Notes |",
            ),
            (
                "electrical calculations",
                "5. Hardware and Wiring",
                CALCULATIONS_TABLE.splitlines()[0],
                "| ID | Quantity | Formula | Units | Provenance | Result | Uncertainty | "
                "Assumption effect |",
            ),
            (
                "measurement ledger",
                "7. Results",
                LEDGER_TABLE.splitlines()[0],
                "| ID | Quantity | Value | Label | Instrument | Method | Uncertainty | Commit |",
            ),
            (
                "traceability matrix",
                "7. Results",
                TRACEABILITY_TABLE.splitlines()[0],
                "| ID | Claim or requirement | Design artifact | Verification method | "
                "Evidence | State |",
            ),
        )
        self.write_homework()
        for label, section, original, renamed in cases:
            with self.subTest(table=label):
                body = SECTION_BODIES[section].replace(original, renamed)
                self.write_report(compliant_report(sections={section: body}))
                result = self.run_fixture()
                self.assert_rejected(result, "[RPT-201]")
                self.assertIn(f'table "{label}"', result.stdout)

    def test_pin_map_absent_table_is_rpt_201(self):
        body = SECTION_BODIES["5. Hardware and Wiring"].replace(PIN_MAP_TABLE, "The pins.")
        self.write_homework()
        self.write_report(compliant_report(sections={"5. Hardware and Wiring": body}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-201]")
        self.assertIn('table "pin map" is absent', result.stdout)


class CalculationsTests(FixtureBase):
    """`RPT-202`/`RPT-203`/`RPT-204` on the calculations table and escaped pipes."""

    def calculations_body(self, old, new):
        return SECTION_BODIES["5. Hardware and Wiring"].replace(old, new)

    def test_calculations_complete_row_passes(self):
        self.write_homework()
        self.write_report()
        self.assert_accepted(self.run_fixture())

    def test_calculations_empty_uncertainty_reports_rpt_203_naming_column(self):
        body = self.calculations_body("| plus or minus 1.4 mA |", "|  |")
        self.write_homework()
        self.write_report(compliant_report(sections={"5. Hardware and Wiring": body}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-203]")
        self.assertIn('empty "Uncertainty" cell', result.stdout)

    def test_calculations_empty_assumption_effect_reports_rpt_203(self):
        body = self.calculations_body("| A lower Vf raises the current. |", "|  |")
        self.write_homework()
        self.write_report(compliant_report(sections={"5. Hardware and Wiring": body}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-203]")
        self.assertIn('empty "Assumption effect" cell', result.stdout)

    def test_calculations_zero_data_rows_reports_rpt_204(self):
        header_only = "\n".join(CALCULATIONS_TABLE.splitlines()[:2])
        body = self.calculations_body(CALCULATIONS_TABLE, header_only)
        self.write_homework()
        self.write_report(compliant_report(sections={"5. Hardware and Wiring": body}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-204]")
        self.assertIn('table "electrical calculations" has no data rows', result.stdout)

    def test_calculations_extra_cell_reports_rpt_202(self):
        body = self.calculations_body(
            "| A lower Vf raises the current. |",
            "| A lower Vf raises the current. | extra |",
        )
        self.write_homework()
        self.write_report(compliant_report(sections={"5. Hardware and Wiring": body}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-202]")
        self.assertIn("cells but its header has 8", result.stdout)

    def test_calculations_escaped_pipe_keeps_the_cell_count(self):
        body = self.calculations_body("`I = 9.33 mA`", "`I = 9.33 \\| 9.4 mA`")
        self.write_homework()
        self.write_report(compliant_report(sections={"5. Hardware and Wiring": body}))
        self.assert_accepted(self.run_fixture())


class SafetyTests(FixtureBase):
    """`RPT-205`: the safety checklist carries bold hazard bullets."""

    def test_safety_bold_hazard_bullet_passes(self):
        self.write_homework()
        self.write_report()
        self.assert_accepted(self.run_fixture())

    def test_safety_plain_bullet_reports_rpt_205_with_its_line(self):
        body = SECTION_BODIES["5. Hardware and Wiring"].replace(
            SAFETY_LIST, "- Check continuity before applying power."
        )
        report = compliant_report(sections={"5. Hardware and Wiring": body})
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-205]")
        expected = report.splitlines().index("- Check continuity before applying power.") + 1
        self.assertIn(f":{expected}: ERROR [RPT-205]", result.stdout)

    def test_safety_empty_checklist_reports_rpt_205(self):
        body = SECTION_BODIES["5. Hardware and Wiring"].replace(SAFETY_LIST, "No hazards.")
        self.write_homework()
        self.write_report(compliant_report(sections={"5. Hardware and Wiring": body}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-205]")
        self.assertIn("at least one hazard bullet", result.stdout)

    def test_safety_section_level_marker_waives_the_checklist(self):
        sections = {
            "5. Hardware and Wiring": "_Not applicable — software-only assignment._",
        }
        self.write_homework()
        self.write_report(compliant_report(sections=sections))
        self.assert_accepted(self.run_fixture())


class BomTests(FixtureBase):
    """`RPT-201`/`RPT-202`/`RPT-204` on the bill of materials, then `RPT-206`."""

    def test_bom_compliant_table_passes(self):
        self.write_homework()
        self.write_report()
        self.assert_accepted(self.run_fixture())

    def test_bom_missing_column_reports_rpt_201(self):
        body = SECTION_BODIES["5. Hardware and Wiring"].replace(
            "| Ref | Part or value | Quantity | Package | Source or link | Notes |",
            "| Ref | Part or value | Quantity | Package | Source or link |",
        )
        self.write_homework()
        self.write_report(compliant_report(sections={"5. Hardware and Wiring": body}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-201]")
        self.assertIn('table "bill of materials"', result.stdout)

    def test_bom_extra_cell_reports_rpt_202(self):
        body = SECTION_BODIES["5. Hardware and Wiring"].replace(
            "| r1 | 150 ohm resistor | 1 | axial | n/a | Series resistor. |",
            "| r1 | 150 ohm resistor | 1 | axial | n/a | Series resistor. | extra |",
        )
        self.write_homework()
        self.write_report(compliant_report(sections={"5. Hardware and Wiring": body}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-202]")
        self.assertIn("cells but its header has 6", result.stdout)

    def test_bom_zero_rows_reports_rpt_204(self):
        header_only = "\n".join(BOM_TABLE.splitlines()[:2])
        body = SECTION_BODIES["5. Hardware and Wiring"].replace(BOM_TABLE, header_only)
        self.write_homework()
        self.write_report(compliant_report(sections={"5. Hardware and Wiring": body}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-204]")
        self.assertIn('table "bill of materials" has no data rows', result.stdout)

    def test_bom_ref_absent_from_diagram_reports_rpt_206(self):
        body = SECTION_BODIES["5. Hardware and Wiring"].replace(
            "| r1 | 150 ohm resistor | 1 | axial | n/a | Series resistor. |",
            "| r99 | 150 ohm resistor | 1 | axial | n/a | Series resistor. |",
        )
        self.write_homework()
        self.write_report(compliant_report(sections={"5. Hardware and Wiring": body}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-206]")
        self.assertIn('BOM Ref "r99"', result.stdout)

    def test_bom_extra_diagram_part_is_allowed(self):
        self.write_homework()
        self.write_report()
        self.write_diagram(default_diagram(parts=("esp", "r1", "virtual")))
        self.assert_accepted(self.run_fixture())

    def test_bom_malformed_json_reports_rpt_207_at_exit_one(self):
        self.write_homework()
        self.write_report()
        self.write_diagram('{"parts": [')
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-207]")
        self.assertIn("not valid JSON", result.stdout)
        self.assertNotIn("Traceback", combined(result))

    def test_bom_missing_diagram_reports_rpt_207_at_exit_one(self):
        self.write_homework()
        self.write_report(with_diagram=False)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-207]")
        self.assertIn("assets/diagram.json", result.stdout)
        self.assertIn("file is absent", result.stdout)
        self.assertNotIn("Traceback", combined(result))

    def test_bom_not_applicable_marker_waives_the_diagram(self):
        sections = {
            "5. Hardware and Wiring": "_Not applicable — software-only assignment._",
        }
        self.write_homework()
        self.write_report(compliant_report(sections=sections), with_diagram=False)
        self.assert_accepted(self.run_fixture())

    def test_bom_subsection_marker_waives_the_diagram(self):
        body = SECTION_BODIES["5. Hardware and Wiring"].replace(
            BOM_TABLE,
            "_Not applicable — the parts are integrated on the board._",
        )
        self.write_homework()
        self.write_report(
            compliant_report(sections={"5. Hardware and Wiring": body}),
            with_diagram=False,
        )
        self.assert_accepted(self.run_fixture())


class LedgerTests(FixtureBase):
    """`RPT-301`/`RPT-303`/`RPT-304`/`RPT-305`: the measurement ledger columns."""

    def ledger_report(self, replacements):
        body = SECTION_BODIES["7. Results"]
        for old, new in replacements:
            body = body.replace(old, new)
        return compliant_report(sections={"7. Results": body})

    def test_ledger_compliant_report_passes(self):
        self.write_homework()
        self.write_report()
        self.assert_accepted(self.run_fixture())

    def test_ledger_bare_observed_label_reports_rpt_301_naming_row_and_label(self):
        report = self.ledger_report(
            [("| not measured | multimeter |", "| observed | multimeter |")]
        )
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-301]")
        self.assertIn('ledger row "L-01" has label "observed"', result.stdout)

    def test_ledger_empty_label_reports_rpt_301(self):
        report = self.ledger_report(
            [("| not measured | multimeter |", "|  | multimeter |")]
        )
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-301]")
        self.assertIn('ledger row "L-01" has label ""', result.stdout)

    def test_ledger_not_measured_value_without_reason_reports_rpt_303(self):
        report = self.ledger_report(
            [("not measured: bench offline", "bench offline")]
        )
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-303]")
        self.assertIn('begin "not measured:" with a reason', result.stdout)

    def test_ledger_measured_value_without_prefix_reports_rpt_303(self):
        report = self.ledger_report(
            [
                ("| not measured | multimeter |", "| measured | multimeter |"),
                ("not measured: bench offline", "3.3 V"),
            ]
        )
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-303]")
        self.assertIn('"user-reported:" or "serial-log:"', result.stdout)

    def test_ledger_measured_observed_value_without_serial_log_reports_rpt_303(self):
        report = self.ledger_report(
            [
                ("| not measured | multimeter |", "| measured (observed) | multimeter |"),
                ("not measured: bench offline", "3.3 V"),
            ]
        )
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-303]")
        self.assertIn('measured (observed) value must begin "serial-log:"', result.stdout)

    def test_ledger_differing_commit_reports_rpt_304_naming_the_row(self):
        report = self.ledger_report(
            [
                (
                    "| not applicable: no reading | `9e1238d` |",
                    "| not applicable: no reading | `abcdef0` |",
                )
            ]
        )
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-304]")
        self.assertIn('ledger row "L-01" "Implementation commit"', result.stdout)
        self.assertIn("does not match the section-1 commit", result.stdout)

    def test_ledger_non_hex_section_commit_reports_rpt_304(self):
        report = compliant_report(
            sections={
                "1. Title and Metadata": SECTION_ONE_TABLE.replace(
                    "| Implementation commit | `9e1238d` |",
                    "| Implementation commit | `zzzzzzz` |",
                )
            }
        )
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-304]")
        self.assertIn("lowercase hex string", result.stdout)

    def test_ledger_calculated_without_calculation_reports_rpt_305(self):
        report = self.ledger_report(
            [
                ("| not measured | multimeter |", "| calculated | multimeter |"),
                ("| DC volts across the rail |", "| computed from the formula |"),
            ]
        )
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-305]")
        self.assertIn("calculated row must name a C-NN calculation", result.stdout)

    def test_ledger_datasheet_without_citation_reports_rpt_305(self):
        report = self.ledger_report(
            [
                ("| not measured | multimeter |", "| datasheet | none |"),
                ("| DC volts across the rail |", "| manufacturer ratings |"),
            ]
        )
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-305]")
        self.assertIn("datasheet row must cite an [N] source", result.stdout)

    def test_ledger_simulated_without_path_reports_rpt_305(self):
        report = self.ledger_report(
            [
                ("| not measured | multimeter |", "| simulated | Wokwi |"),
                ("| DC volts across the rail |", "| the scenario expectation |"),
            ]
        )
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-305]")
        self.assertIn("simulated row must name a scenario or run-artifact path", result.stdout)

    def test_ledger_measured_without_instrument_reports_rpt_305(self):
        report = self.ledger_report(
            [
                ("| not measured | multimeter |", "| measured | none |"),
                ("not measured: bench offline", "user-reported: 3.3 V"),
            ]
        )
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-305]")
        self.assertIn('measured row must name an instrument other than "none"', result.stdout)


class TraceabilityTests(FixtureBase):
    """`RPT-306`/`RPT-307`/`RPT-308`/`RPT-310`: the traceability matrix."""

    def matrix_report(self, replacements):
        table = TRACEABILITY_TABLE
        for old, new in replacements:
            table = table.replace(old, new)
        body = SECTION_BODIES["7. Results"].replace(TRACEABILITY_TABLE, table)
        return compliant_report(sections={"7. Results": body})

    def test_traceability_compliant_report_passes(self):
        self.write_homework()
        self.write_report()
        self.assert_accepted(self.run_fixture())

    def test_traceability_live_report_resolves_artifacts(self):
        result = run_report_checker("--json")
        self.assertEqual(0, result.returncode, combined(result))
        rules = {item["rule"] for item in json.loads(result.stdout)}
        self.assertEqual(set(), rules & {"RPT-306", "RPT-307", "RPT-308"})

    def test_traceability_invalid_status_reports_rpt_306(self):
        report = self.matrix_report([("| verified |", "| done |")])
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-306]")
        self.assertIn('traceability row "T-01" has status "done"', result.stdout)

    def test_traceability_missing_artifact_reports_rpt_307(self):
        report = self.matrix_report([("`platformio.ini`", "`lib/missing.c`")])
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-307]")
        self.assertIn('Design artifact token "lib/missing.c" does not resolve', result.stdout)

    def test_traceability_pending_row_is_exempt(self):
        report = self.matrix_report(
            [
                (
                    "| T-01 | Target build | `platformio.ini` | `pio run` | `SUCCESS` | verified |",
                    "| T-01 | Target build | `lib/missing.c` | `pio run` | `SUCCESS` | pending |",
                )
            ]
        )
        self.write_homework()
        self.write_report(report)
        self.assert_accepted(self.run_fixture())

    def test_traceability_escaping_token_reports_rpt_307(self):
        report = self.matrix_report([("`platformio.ini`", "`../../../etc/passwd`")])
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-307]")
        self.assertIn("../../../etc/passwd", result.stdout)

    def test_traceability_command_token_splits_and_resolves(self):
        report = self.matrix_report(
            [("`platformio.ini`", "`pio run -d homeworks/1_3-good`")]
        )
        self.write_homework()
        self.write_report(report)
        self.assert_accepted(self.run_fixture())

    def test_traceability_duplicate_id_reports_rpt_308(self):
        report = self.matrix_report([("| T-02 |", "| T-01 |")])
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-308]")
        self.assertIn('row id "T-01" is duplicated', result.stdout)

    def test_traceability_missing_requirement_reports_rpt_310(self):
        report = self.matrix_report([("REPORT-05, ", "")])
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-310]")
        self.assertIn("does not cite REPORT-05", result.stdout)

    def test_traceability_single_row_yields_seven_missing_requirements(self):
        single = (
            "| ID | Claim or requirement | Design artifact | Verification method | "
            "Evidence | Status |\n"
            "|----|----------------------|-----------------|---------------------|"
            "----------|--------|\n"
            "| T-01 | Report contract REPORT-01 | `report.md` | manual review | "
            "this report | manual |"
        )
        body = SECTION_BODIES["7. Results"].replace(TRACEABILITY_TABLE, single)
        self.write_homework()
        self.write_report(compliant_report(sections={"7. Results": body}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-310]")
        reasons = [line for line in result.stdout.splitlines() if "[RPT-310]" in line]
        self.assertEqual(7, len(reasons))
        ids = re.findall(r"REPORT-\d{2}", "\n".join(reasons))
        self.assertEqual([f"REPORT-0{index}" for index in range(2, 9)], ids)

    def test_traceability_zero_rows_reports_every_requirement(self):
        header_only = "\n".join(TRACEABILITY_TABLE.splitlines()[:2])
        body = SECTION_BODIES["7. Results"].replace(TRACEABILITY_TABLE, header_only)
        self.write_homework()
        self.write_report(compliant_report(sections={"7. Results": body}))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-310]")
        reasons = [line for line in result.stdout.splitlines() if "[RPT-310]" in line]
        self.assertEqual(8, len(reasons))


class CrossReferenceTests(FixtureBase):
    """`RPT-309`/`RPT-311`/`RPT-312`: intra-report ids and IEEE citations."""

    def test_cross_reference_live_report_has_six_references(self):
        text = (REPO_ROOT / "homeworks" / "1_3-police-flasher" / "report.md").read_text(
            encoding="utf-8"
        )
        lines = text.splitlines()
        sections = markdown.sections(lines)
        entries = markdown.reference_entries(lines, sections, "10. References")
        self.assertEqual([1, 2, 3, 4, 5, 6], [number for number, _ in entries])
        references = next(item for item in sections if item.heading.text == "10. References")
        self.assertTrue(
            all(
                references.body_start <= line <= references.body_end
                for _, line in entries
            ),
            "a reference entry was collected outside section 10",
        )

    def test_cross_reference_live_report_has_no_id_or_citation_records(self):
        result = run_report_checker("--json")
        self.assertEqual(0, result.returncode, combined(result))
        rules = {item["rule"] for item in json.loads(result.stdout)}
        self.assertEqual(set(), rules & {"RPT-309", "RPT-311", "RPT-312"})

    def test_cross_reference_unresolved_id_reports_rpt_309(self):
        report = compliant_report(sections={"2. Objective": "The objective refers to C-99."})
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-309]")
        self.assertIn('"C-99" does not resolve to a row in the C table', result.stdout)

    def test_cross_reference_missing_entry_reports_rpt_311(self):
        report = compliant_report(sections={"2. Objective": "The objective cites [7]."})
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-311]")
        self.assertIn('citation [7] has no entry in "10. References"', result.stdout)

    def test_cross_reference_uncited_entry_reports_rpt_312(self):
        report = compliant_report(
            sections={"10. References": "[1] A reference.\n\n[6] An uncited reference."}
        )
        self.write_homework()
        self.write_report(report)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-312]")
        self.assertIn("reference entry [6] is never cited", result.stdout)


class RealTreeTests(unittest.TestCase):
    """The shipped repository is the worked example the contract must accept.

    Each fixture class above proves one rule on a temporary root; this class
    proves the contract is satisfiable on the real tree, so a green fixture can
    never stand in for a repository that violates its own contract.
    """

    def real_reports(self):
        """Every report the tree ships, discovered the same way a reader would."""
        return sorted((REPO_ROOT / "homeworks").glob("*/report.md"))

    def test_real_tree_checker_exits_zero_with_the_pass_summary(self):
        result = run_report_checker()
        self.assertEqual(0, result.returncode, combined(result))
        self.assertEqual("", result.stderr)
        self.assertEqual("PASS: report contract satisfied", result.stdout.splitlines()[-1])

    def test_real_tree_json_has_one_ok_record_per_report(self):
        reports = self.real_reports()
        # Guard the count assertion against vacuity: a tree with no report would
        # otherwise satisfy "one record per report" with zero records.
        self.assertGreaterEqual(len(reports), 1, "no real report was discovered")
        result = run_report_checker("--json")
        self.assertEqual(0, result.returncode, combined(result))
        payload = json.loads(result.stdout)
        self.assertEqual(len(reports), len(payload), combined(result))
        for record in payload:
            with self.subTest(path=record.get("path")):
                self.assertEqual("OK", record["status"], record)
                self.assertTrue({"rule", "line"} <= set(record), record)
                self.assertTrue((REPO_ROOT / record["path"]).is_file(), record["path"])
        order = [(record["path"], record["line"], record["rule"]) for record in payload]
        self.assertEqual(sorted(order), order, "records are not sorted by (path, line, rule)")

    def test_real_tree_two_runs_are_byte_identical(self):
        first = run_report_checker()
        second = run_report_checker()
        self.assertEqual(0, first.returncode, combined(first))
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stderr, second.stderr)


# ---------------------------------------------------------------------------
# Plan 10-07: one violating fixture factory per registered rule. `RULE_FIXTURES`
# is exhaustive by construction, so a rule added to `RULES` without a factory
# fails `test_rule_registry_every_id_has_a_violating_fixture`, and a rule added
# without a remediation row fails the standard-table set equality. Neither test
# reads the standard's prose: the id set and row uniqueness are the only
# documentation-text assertions, because prose/doc-sync checks were pruned in
# `261026-ky7` (Open Question 3).

_MISSING_DIAGRAM = object()


def _write_rule_fixture(
    root,
    *,
    homework=None,
    report=None,
    with_report=True,
    diagram=_MISSING_DIAGRAM,
):
    """Write one homework directory; every rule fixture overrides one input.

    The default is the compliant fixture: a draft report, a readable diagram and
    the `platformio.ini` artifact its traceability row names. A rule fixture
    therefore differs from a passing document in exactly one place.
    """
    directory = root / "homeworks" / "1_3-good"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "homework.yaml").write_text(
        homework if homework is not None else homework_yaml(), encoding="utf-8"
    )
    if with_report:
        (directory / "report.md").write_text(
            report if report is not None else compliant_report(), encoding="utf-8"
        )
    (directory / "platformio.ini").write_text("placeholder\n", encoding="utf-8")
    payload = default_diagram() if diagram is _MISSING_DIAGRAM else diagram
    if payload is not None:
        target = directory / "assets" / "diagram.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload, encoding="utf-8")
    return directory


def _mutated_section(name, old, new):
    """Return a compliant report with one literal replaced in one section."""
    return compliant_report(sections={name: SECTION_BODIES[name].replace(old, new)})


def _mutated_results(*replacements):
    """Return a compliant report with replacements applied to section 7."""
    body = SECTION_BODIES["7. Results"]
    for old, new in replacements:
        body = body.replace(old, new)
    return compliant_report(sections={"7. Results": body})


def _header_only(table):
    """Return a table's header and separator rows, so it has no data rows."""
    return "\n".join(table.splitlines()[:2])


def _swapped_order():
    """Swap `3. Assumptions` and `4. Theory` to violate ascending order."""
    order = list(REPORT_HEADINGS)
    order[2], order[3] = order[3], order[2]
    return order


def _duplicated_order():
    """Repeat `2. Objective` so the heading appears twice."""
    order = list(REPORT_HEADINGS)
    order.insert(2, "2. Objective")
    return order


RULE_FIXTURES = {
    # Lifecycle family: `check_report.py` owns these before the document rules.
    "RPT-001": lambda root: _write_rule_fixture(
        root, homework=homework_yaml(with_report=False), with_report=False
    ),
    "RPT-002": lambda root: _write_rule_fixture(root, with_report=False),
    "RPT-003": lambda root: _write_rule_fixture(
        root, homework=homework_yaml(status="in-progress", report_status="placeholder")
    ),
    "RPT-004": lambda root: _write_rule_fixture(root, report="x" * (REPORT_MAX_BYTES + 1)),
    # Structure family.
    "RPT-101": lambda root: _write_rule_fixture(
        root,
        report=compliant_report(
            order=[title for title in REPORT_HEADINGS if title != "4. Theory"]
        ),
    ),
    "RPT-102": lambda root: _write_rule_fixture(
        root, report=compliant_report(order=_swapped_order())
    ),
    "RPT-103": lambda root: _write_rule_fixture(
        root, report=compliant_report(order=_duplicated_order())
    ),
    "RPT-104": lambda root: _write_rule_fixture(
        root, report=compliant_report(sections={"4. Theory": "The theory [1]."})
    ),
    "RPT-105": lambda root: _write_rule_fixture(
        root, report=compliant_report(sections={"3. Assumptions": "_Not applicable._"})
    ),
    "RPT-106": lambda root: _write_rule_fixture(
        root,
        report=compliant_report(
            sections={"2. Objective": "_Not applicable — no objective._"}
        ),
    ),
    "RPT-107": lambda root: _write_rule_fixture(
        root,
        report=compliant_report(
            sections={"8. Analysis": "The analysis without the required note."}
        ),
    ),
    "RPT-108": lambda root: _write_rule_fixture(
        root,
        report=compliant_report(
            sections={"9. Conclusions": "### Next Steps\n\n- Tag the pilot."}
        ),
    ),
    # Table family.
    "RPT-201": lambda root: _write_rule_fixture(
        root,
        report=_mutated_section(
            "5. Hardware and Wiring",
            "| Signal | Pin | Connects to | Notes |",
            "| Signal | ESP32-S3 pin | Connects to | Notes |",
        ),
    ),
    "RPT-202": lambda root: _write_rule_fixture(
        root,
        report=_mutated_section(
            "5. Hardware and Wiring",
            "| A lower Vf raises the current. |",
            "| A lower Vf raises the current. | extra |",
        ),
    ),
    "RPT-203": lambda root: _write_rule_fixture(
        root,
        report=_mutated_section(
            "5. Hardware and Wiring", "| plus or minus 1.4 mA |", "|  |"
        ),
    ),
    "RPT-204": lambda root: _write_rule_fixture(
        root,
        report=_mutated_section(
            "5. Hardware and Wiring",
            CALCULATIONS_TABLE,
            _header_only(CALCULATIONS_TABLE),
        ),
    ),
    "RPT-205": lambda root: _write_rule_fixture(
        root,
        report=_mutated_section(
            "5. Hardware and Wiring",
            SAFETY_LIST,
            "- Check continuity before applying power.",
        ),
    ),
    "RPT-206": lambda root: _write_rule_fixture(
        root,
        report=_mutated_section(
            "5. Hardware and Wiring",
            "| r1 | 150 ohm resistor | 1 | axial | n/a | Series resistor. |",
            "| r99 | 150 ohm resistor | 1 | axial | n/a | Series resistor. |",
        ),
    ),
    "RPT-207": lambda root: _write_rule_fixture(root, diagram=None),
    # Evidence family.
    "RPT-301": lambda root: _write_rule_fixture(
        root,
        report=_mutated_results(
            ("| not measured | multimeter |", "| observed | multimeter |")
        ),
    ),
    "RPT-303": lambda root: _write_rule_fixture(
        root,
        report=_mutated_results(("not measured: bench offline", "bench offline")),
    ),
    "RPT-304": lambda root: _write_rule_fixture(
        root,
        report=_mutated_results(
            (
                "| not applicable: no reading | `9e1238d` |",
                "| not applicable: no reading | `abcdef0` |",
            )
        ),
    ),
    "RPT-305": lambda root: _write_rule_fixture(
        root,
        report=_mutated_results(
            ("| not measured | multimeter |", "| calculated | multimeter |"),
            ("| DC volts across the rail |", "| computed from the formula |"),
        ),
    ),
    "RPT-306": lambda root: _write_rule_fixture(
        root, report=_mutated_results(("| verified |", "| done |"))
    ),
    "RPT-307": lambda root: _write_rule_fixture(
        root,
        report=_mutated_results(("`platformio.ini`", "`lib/missing.c`")),
    ),
    "RPT-308": lambda root: _write_rule_fixture(
        root, report=_mutated_results(("| T-02 |", "| T-01 |"))
    ),
    "RPT-309": lambda root: _write_rule_fixture(
        root,
        report=compliant_report(
            sections={"2. Objective": "The objective refers to C-99."}
        ),
    ),
    "RPT-310": lambda root: _write_rule_fixture(
        root, report=_mutated_results(("REPORT-05, ", ""))
    ),
    "RPT-311": lambda root: _write_rule_fixture(
        root,
        report=compliant_report(sections={"2. Objective": "The objective cites [7]."}),
    ),
    "RPT-312": lambda root: _write_rule_fixture(
        root,
        report=compliant_report(
            sections={"10. References": "[1] A reference.\n\n[6] An uncited reference."}
        ),
    ),
    # Document-integrity family.
    "RPT-401": lambda root: _write_rule_fixture(
        root,
        report=compliant_report().replace("# Good homework", "# Another title", 1),
    ),
    "RPT-402": lambda root: _write_rule_fixture(
        root,
        report=_mutated_section(
            "1. Title and Metadata", "`1_3-good`", "`1_3-other`"
        ),
    ),
    "RPT-403": lambda root: _write_rule_fixture(
        root,
        report=_mutated_section(
            "1. Title and Metadata",
            "| Framework | Arduino |",
            "| Framework | ESP-IDF |",
        ),
    ),
    "RPT-404": lambda root: _write_rule_fixture(
        root,
        report=compliant_report(
            sections={"2. Objective": "See [the diagram](assets/missing.json)."}
        ),
    ),
    "RPT-405": lambda root: _write_rule_fixture(
        root,
        report=compliant_report(
            sections={"2. Objective": "The objective contains тест."}
        ),
    ),
    "RPT-406": lambda root: _write_rule_fixture(
        root,
        report=compliant_report(
            sections={"2. Objective": "TODO: finish the objective."}
        ),
    ),
    "RPT-407": lambda root: _write_rule_fixture(
        root,
        report=_mutated_results((NATIVE_PARAGRAPH + "\n\n", "")),
    ),
    "RPT-408": lambda root: _write_rule_fixture(
        root, homework=homework_yaml(simulation_status="pending")
    ),
}


class RuleRegistryTests(unittest.TestCase):
    """The rule registry, its remediation table, and its non-vacuity fixtures.

    The only documentation-text assertion in the repository is the id set of the
    `## Rule reference` table; prose is never compared (`261026-ky7`, Open
    Question 3). A rule added without a remediation row fails here.
    """

    def test_rule_registry_ids_match_the_rule_shape(self):
        pattern = re.compile(r"^RPT-[0-9]{3}$")
        for rule_id in RULES:
            with self.subTest(rule=rule_id):
                self.assertRegex(rule_id, pattern)

    def test_rule_registry_ids_are_unique(self):
        self.assertEqual(len(RULES), len(set(RULES)))

    def test_rule_registry_every_id_has_a_summary_and_a_remediation(self):
        for rule_id, (summary, remediation) in RULES.items():
            with self.subTest(rule=rule_id):
                self.assertTrue(summary.strip(), rule_id)
                self.assertTrue(remediation.strip(), rule_id)

    def assert_rule_reference(self, ids, rules=None):
        """The one assertion: no duplicate row and the exact registered set."""
        rules = RULES if rules is None else rules
        self.assertEqual(len(ids), len(set(ids)), "the rule reference has a duplicate row")
        self.assertEqual(set(rules), set(ids))

    def rule_reference_ids(self):
        text = (REPO_ROOT / "docs" / "standards" / "report.md").read_text(encoding="utf-8")
        found = [
            table
            for table in tables.extract_tables(text)
            if table.header == ("Rule", "Meaning", "Fix")
        ]
        self.assertEqual(1, len(found), "expected exactly one Rule | Meaning | Fix table")
        return [tables.normalize_cell(row.cells[0]) for row in found[0].rows]

    def test_rule_registry_standard_rule_table_matches_the_registry(self):
        self.assert_rule_reference(self.rule_reference_ids())

    def test_rule_registry_zero_rule_rows_fail_set_equality(self):
        with self.assertRaises(AssertionError):
            self.assert_rule_reference([])

    def test_rule_registry_duplicate_rule_row_fails_uniqueness(self):
        ids = self.rule_reference_ids()
        with self.assertRaises(AssertionError):
            self.assert_rule_reference(ids + [ids[0]])

    def test_rule_registry_single_row_for_a_single_rule_passes(self):
        self.assert_rule_reference(["RPT-001"], rules={"RPT-001": RULES["RPT-001"]})

    def test_rule_registry_every_id_has_a_violating_fixture(self):
        self.assertEqual(set(RULES), set(RULE_FIXTURES))
        for rule_id, factory in RULE_FIXTURES.items():
            with self.subTest(rule=rule_id):
                with tempfile.TemporaryDirectory(prefix="report-rule-") as tmp:
                    factory(Path(tmp))
                    result = run_report_checker("--dir", tmp, "--json")
                    self.assertEqual(1, result.returncode, combined(result))
                    fired = {item["rule"] for item in json.loads(result.stdout)}
                    self.assertIn(rule_id, fired, f"{rule_id} did not fire")


if __name__ == "__main__":
    unittest.main()
