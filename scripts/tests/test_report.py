"""Prove the report and evidence contract end to end.

The checker is invoked as a subprocess (`uv run scripts/check_report.py`)
because it reads `homework.yaml` with PyYAML, and this suite stays
dependency-free: no test module may import PyYAML or jsonschema. Every fixture
is a temporary root that contains one `homeworks/<id>/` directory, so the real
tree is never touched and a negative case can fail only because of its single
mutation.

Coverage: one rule id per fixture for the lifecycle family (`RPT-001` ... `RPT-004`)
and the structure family (`RPT-101` ... `RPT-108`), a compliant report, a fenced
heading, the section-5 not-applicable waiver, the section-7 extra subsection,
determinism, the `--json` shape, and the stdlib-only import boundary.
"""

from __future__ import annotations

import ast
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.report.vocabulary import REPORT_HEADINGS

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_report.py"
PACKAGE = REPO_ROOT / "scripts" / "report"

# The seven contracted tables as literals a test can mutate in one place.
SECTION_ONE_TABLE = (
    "| Field | Value |\n|-------|-------|\n| Homework ID | `1_3-good` |\n| Title | Good homework |"
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
    "| T-01 | Target build | `platformio.ini` | `pio run` | `SUCCESS` | verified |"
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
    "4. Theory": "The theory.\n\n### Limitations\n\nNone.",
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
    if with_report:
        lines.extend(["report:", "  path: report.md", f"  status: {report_status}"])
    return "\n".join(lines) + "\n"


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

    def write_report(self, text=None, homework_id=None):
        homework_id = homework_id or self.homework_id
        path = self.root / "homeworks" / homework_id / "report.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        if text is None:
            text = compliant_report()
        path.write_text(text, encoding="utf-8")
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
                "The results.\n\n"
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


if __name__ == "__main__":
    unittest.main()
