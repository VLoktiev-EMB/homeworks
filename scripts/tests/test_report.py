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
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.metadata.paths import relative_path
from scripts.report import tables
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
    report_path="report.md",
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
        lines.extend(["report:", f"  path: {report_path}", f"  status: {report_status}"])
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

    def _outside_sentinel(self, suffix):
        """Write a malformed report outside the checked root, and return it.

        The body opens with `# OUTSIDE-SENTINEL` so a test can prove the file
        was never opened, and it is malformed enough that opening it would emit
        `RPT-101` records instead of the expected refusal.
        """
        path = self.root.parent / f"{self.root.name}-{suffix}"
        path.write_text("# OUTSIDE-SENTINEL\n\n# Broken\n", encoding="utf-8")
        self.addCleanup(path.unlink)
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

    def test_headings_missing_heading_reports_rpt_101(self):
        order = [title for title in REPORT_HEADINGS if title != "4. Theory"]
        self.write_homework()
        self.write_report(compliant_report(order=order))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-101]")
        self.assertIn('missing heading "4. Theory"', result.stdout)


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


class ReportPathContainmentTests(FixtureBase):
    """CR-03/T-10-30/T-10-31: `report.path` never leaves its homework directory.

    `homework.yaml` is untrusted repository content and the checker deliberately
    does not apply the JSON Schema (D-02), so an absolute or escaping
    `report.path` must be refused before any `stat`, `is_file` or read. The
    final component keeps its shipped classification, so a symlinked or absent
    document is still `RPT-002`.
    """

    def test_absolute_report_path_is_rpt_001_and_never_read(self):
        sentinel = self._outside_sentinel("absolute")
        self.write_homework(homework_yaml(report_path=str(sentinel)))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-001]")
        self.assertNotIn("OUTSIDE-SENTINEL", result.stdout)
        self.assertNotIn("[RPT-101]", result.stdout)
        self.assertNotIn("Traceback", combined(result))

    def test_parent_directory_escape_is_rpt_001_and_never_read(self):
        sentinel = self._outside_sentinel("parent")
        self.write_homework(homework_yaml(report_path=f"../../../{sentinel.name}"))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-001]")
        self.assertNotIn("OUTSIDE-SENTINEL", result.stdout)
        self.assertNotIn("[RPT-101]", result.stdout)
        self.assertNotIn("Traceback", combined(result))

    def test_intermediate_symlink_is_rpt_001_and_never_read(self):
        outside_dir = self.root.parent / f"{self.root.name}-linked"
        outside_dir.mkdir()
        (outside_dir / "report.md").write_text("# OUTSIDE-SENTINEL\n", encoding="utf-8")
        self.addCleanup(shutil.rmtree, outside_dir, True)
        linked = self.root / "homeworks" / self.homework_id / "linked"
        linked.parent.mkdir(parents=True, exist_ok=True)
        linked.symlink_to(outside_dir)
        self.addCleanup(linked.unlink)
        self.write_homework(homework_yaml(report_path="linked/report.md"))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-001]")
        self.assertIn("symlink", result.stdout)
        self.assertNotIn("OUTSIDE-SENTINEL", result.stdout)
        self.assertNotIn("Traceback", combined(result))

    def test_nested_relative_report_path_inside_the_homework_is_accepted(self):
        # The traceability row names the report as a design artifact, so the
        # fixture's token must follow the declared nested path.
        traceability = TRACEABILITY_TABLE.replace("`report.md`", "`docs/report.md`")
        report = compliant_report(
            sections={
                "7. Results": SECTION_BODIES["7. Results"].replace(
                    TRACEABILITY_TABLE, traceability
                )
            }
        )
        self.write_homework(homework_yaml(report_path="docs/report.md"))
        self.write_artifact("docs/report.md", report)
        self.write_artifact("platformio.ini")
        self.write_diagram()
        result = self.run_fixture()
        self.assert_accepted(result)

    def test_final_component_symlink_is_still_rpt_002(self):
        self.write_homework()
        target = self.root / "outside-report.md"
        target.write_text("outside\n", encoding="utf-8")
        path = self.root / "homeworks" / self.homework_id / "report.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target)
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-002]")
        self.assertIn("symlink", result.stdout)
        self.assertNotIn("[RPT-001]", result.stdout)

    def test_absent_document_is_still_rpt_002(self):
        self.write_homework()
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-002]")
        self.assertIn("absent", result.stdout)
        self.assertNotIn("[RPT-001]", result.stdout)

    def test_null_byte_in_final_component_is_rpt_001_not_a_traceback(self):
        self.write_homework(homework_yaml(report_path=r'"report\0.md"'))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-001]")
        self.assertNotIn("Traceback", combined(result))
        json_result = self.run_fixture("--json")
        self.assertEqual(1, json_result.returncode, combined(json_result))
        records = json.loads(json_result.stdout)
        self.assertTrue(records, json_result.stdout)
        self.assertIn("RPT-001", {item["rule"] for item in records})
        for item in records:
            with self.subTest(record=item):
                self.assertEqual(
                    {"path", "status", "rule", "line", "reason"}, set(item)
                )

    def test_null_byte_in_parent_component_is_rpt_001_not_a_traceback(self):
        self.write_homework(homework_yaml(report_path=r'"dir\0/report.md"'))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-001]")
        self.assertNotIn("Traceback", combined(result))
        json_result = self.run_fixture("--json")
        self.assertEqual(1, json_result.returncode, combined(json_result))
        records = json.loads(json_result.stdout)
        self.assertTrue(records, json_result.stdout)
        self.assertIn("RPT-001", {item["rule"] for item in records})
        for item in records:
            with self.subTest(record=item):
                self.assertEqual(
                    {"path", "status", "rule", "line", "reason"}, set(item)
                )

    def test_lone_surrogate_is_rpt_001_not_a_traceback(self):
        self.write_homework(homework_yaml(report_path=r'"report\ud800.md"'))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-001]")
        self.assertNotIn("Traceback", combined(result))
        json_result = self.run_fixture("--json")
        self.assertEqual(1, json_result.returncode, combined(json_result))
        records = json.loads(json_result.stdout)
        self.assertTrue(records, json_result.stdout)
        self.assertIn("RPT-001", {item["rule"] for item in records})
        for item in records:
            with self.subTest(record=item):
                self.assertEqual(
                    {"path", "status", "rule", "line", "reason"}, set(item)
                )

    def test_overlong_component_is_rpt_001_not_exit_2(self):
        self.write_homework(homework_yaml(report_path=("a" * 300) + "/report.md"))
        result = self.run_fixture()
        self.assert_rejected(result, "[RPT-001]")
        self.assertEqual(1, result.returncode, combined(result))
        self.assertNotIn("Traceback", combined(result))
        self.assertNotIn(str(self.root), result.stderr)
        self.assertNotIn("File name too long", result.stderr)
        json_result = self.run_fixture("--json")
        self.assertEqual(1, json_result.returncode, combined(json_result))
        records = json.loads(json_result.stdout)
        self.assertTrue(records, json_result.stdout)
        self.assertIn("RPT-001", {item["rule"] for item in records})
        for item in records:
            with self.subTest(record=item):
                self.assertEqual(
                    {"path", "status", "rule", "line", "reason"}, set(item)
                )

    def test_relative_path_handles_unrepresentable_path(self):
        self.assertEqual("report\x00.md", relative_path(self.root, "report\x00.md"))
        self.assertEqual("report\ud800.md", relative_path(self.root, "report\ud800.md"))


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


class HostileDocumentContractTests(FixtureBase):
    """G-10-1: every hostile document is valid JSON at exit 1, never a crash.

    The three inputs are the two CR-01/CR-02 payloads and the CR-03 escaping
    path. Each must exit 1 with a parseable, non-empty `--json` array whose
    records carry the five contract keys, with no traceback, and repeated runs
    over each fixture must be byte-identical (T-10-28 through T-10-31).
    """

    def write_deep_metadata(self, homework_id=None):
        self.write_homework(DEEP_YAML, homework_id=homework_id)

    def write_deep_diagram(self, homework_id=None):
        self.write_homework(homework_id=homework_id)
        self.write_report(homework_id=homework_id)
        self.write_diagram(DEEP_DIAGRAM, homework_id=homework_id)

    def write_escaping_path(self, homework_id=None):
        homework_id = homework_id or self.homework_id
        sentinel = self._outside_sentinel("contract")
        self.write_homework(
            homework_yaml(homework_id=homework_id, report_path=str(sentinel)),
            homework_id=homework_id,
        )
        return sentinel

    def assert_content_error(self, *args):
        return self.assert_content_error_result(self.run_fixture("--json", *args))

    def assert_content_error_result(self, result):
        self.assertEqual(1, result.returncode, combined(result))
        self.assertNotIn("Traceback", combined(result))
        records = json.loads(result.stdout)
        self.assertTrue(records, result.stdout)
        self.assertIn("ERROR", {item["status"] for item in records})
        for item in records:
            with self.subTest(record=item):
                self.assertEqual({"path", "status", "rule", "line", "reason"}, set(item))
        return records

    def test_deep_metadata_keeps_the_contract(self):
        self.write_deep_metadata()
        records = self.assert_content_error()
        self.assertIn("RPT-001", {item["rule"] for item in records})

    def test_escaping_report_path_keeps_the_contract(self):
        self.write_escaping_path()
        result = self.run_fixture("--json")
        records = self.assert_content_error_result(result)
        self.assertIn("RPT-001", {item["rule"] for item in records})
        self.assertNotIn("OUTSIDE-SENTINEL", result.stdout)

    def test_hostile_inputs_are_deterministic(self):
        cases = (
            ("1_3-deep", self.write_deep_metadata),
            ("1_3-escape", self.write_escaping_path),
        )
        for homework_id, writer in cases:
            with self.subTest(fixture=homework_id):
                writer(homework_id=homework_id)
                positional = f"homeworks/{homework_id}"
                first = self.run_fixture(positional)
                second = self.run_fixture(positional)
                self.assertEqual(1, first.returncode, combined(first))
                self.assertEqual(first.stdout, second.stdout)
                self.assertNotIn("Traceback", combined(first))

                json_first = self.run_fixture(positional, "--json")
                json_second = self.run_fixture(positional, "--json")
                self.assertEqual(1, json_first.returncode, combined(json_first))
                self.assertEqual(json_first.stdout, json_second.stdout)
                self.assert_content_error_result(json_first)


class SymlinkSecurityTests(FixtureBase):
    """CR-06/WR-12: checkers must never follow symlinks to outside files."""

    def test_symlinked_homework_yaml_is_rpt_001_and_never_read(self):
        outside = self.root.parent / f"{self.root.name}-outside.yaml"
        outside.write_text(
            "status: LEAKME-SECRET\nreport:\n  path: report.md\n  status: complete\n",
            encoding="utf-8",
        )
        self.addCleanup(outside.unlink)
        hw_dir = self.root / "homeworks" / self.homework_id
        hw_dir.mkdir(parents=True, exist_ok=True)
        hw_link = hw_dir / "homework.yaml"
        hw_link.symlink_to(outside)
        self.addCleanup(hw_link.unlink)
        result = self.run_fixture()
        self.assertEqual(1, result.returncode, combined(result))
        self.assert_rejected(result, "[RPT-001]")
        self.assertIn("symlink", result.stdout)
        self.assertNotIn("LEAKME-SECRET", result.stdout)
        self.assertNotIn("LEAKME-SECRET", result.stderr)
        self.assertNotIn("[RPT-003]", result.stdout)

    def test_broken_symlinked_homework_yaml_is_rpt_001(self):
        hw_dir = self.root / "homeworks" / self.homework_id
        hw_dir.mkdir(parents=True, exist_ok=True)
        hw_link = hw_dir / "homework.yaml"
        hw_link.symlink_to(self.root / "non-existent-target.yaml")
        self.addCleanup(hw_link.unlink)
        result = self.run_fixture()
        self.assertEqual(1, result.returncode, combined(result))
        self.assert_rejected(result, "[RPT-001]")
        self.assertIn("symlink", result.stdout)
        self.assertNotIn("missing", result.stdout)


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
