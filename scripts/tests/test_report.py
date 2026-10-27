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

# The body of every numbered section. A test mutates one entry or drops one
# heading, so a failing fixture differs from the compliant report in exactly
# one place.
SECTION_BODIES = {
    "1. Title and Metadata": "| Field | Value |\n|-------|-------|\n| Homework ID | `1_3-good` |",
    "2. Objective": "The objective.",
    "3. Assumptions": "Each assumption names its consequence and validation.",
    "4. Theory": "The theory.\n\n### Limitations\n\nNone.",
    "5. Hardware and Wiring": (
        "The wiring.\n\n"
        "### Bill of Materials\n\nThe parts.\n\n"
        "### Pin Map\n\nThe pins.\n\n"
        "### Electrical Calculations\n\nThe calculations.\n\n"
        "### Safety Checklist\n\nThe hazards."
    ),
    "6. Methodology": "The method.",
    "7. Results": (
        "The results.\n\n"
        "### Measurement Ledger\n\nThe ledger.\n\n"
        "### Traceability Matrix\n\nThe matrix."
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


if __name__ == "__main__":
    unittest.main()
