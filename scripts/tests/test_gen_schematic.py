"""Tests for scripts/gen_schematic.py and scripts/schematic_svg.py.

Verifies Mermaid generation, diagram validation, the universal SVG renderer
(branch layout and net-label fallback), determinism, and the CLI flags.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.gen_schematic import generate_mermaid_from_diagram, validate_diagram
from scripts.schematic_svg import render_schematic_svg

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = str(REPO_ROOT / "scripts" / "gen_schematic.py")

SIMPLE_DIAGRAM = {
    "version": 1,
    "parts": [
        {"type": "board-esp32-s3-devkitc-1", "id": "esp", "top": 0, "left": 0},
        {"type": "wokwi-resistor", "id": "r1", "top": 0, "left": 300, "attrs": {"value": "220"}},
        {"type": "wokwi-led", "id": "led1", "top": 0, "left": 400, "attrs": {"color": "red"}},
        {
            "type": "wokwi-pushbutton",
            "id": "btn1",
            "top": 0,
            "left": -150,
            "attrs": {"label": "MODE"},
        },
    ],
    "connections": [
        ["esp:15", "r1:2", "orange", []],
        ["r1:1", "led1:A", "blue", []],
        ["led1:C", "esp:GND.1", "black", []],
        ["btn1:1.l", "esp:21", "green", []],
        ["btn1:2.l", "esp:GND.1", "black", []],
    ],
}

MULTI_PIN_DIAGRAM = {
    "version": 1,
    "parts": [
        {"type": "board-esp32-s3-devkitc-1", "id": "esp", "top": 0, "left": 0},
        {"type": "wokwi-74hc595", "id": "ic1", "top": 0, "left": 400},
    ],
    "connections": [
        ["esp:15", "ic1:DS", "green", []],
        ["esp:16", "ic1:SHCP", "blue", []],
        ["esp:17", "ic1:STCP", "orange", []],
        ["ic1:VCC", "esp:3V3.1", "red", []],
        ["ic1:GND", "esp:GND.1", "black", []],
    ],
}


def run_schematic(*args: str, timeout: int = 180) -> subprocess.CompletedProcess:
    """Invoke `uv run scripts/gen_schematic.py` from the repository root."""
    if shutil.which("uv") is None:
        raise AssertionError(
            "uv is a required repository tool; install it before running this suite"
        )
    return subprocess.run(
        ["uv", "run", SCRIPT, *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def setUpModule() -> None:
    """Warm `uv` so its first-run install line cannot pollute an stderr check."""
    if shutil.which("uv") is None:
        return
    subprocess.run(
        ["uv", "run", SCRIPT, "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )


def _schemdraw_available() -> bool:
    try:
        import schemdraw  # noqa: F401
    except ImportError:
        return False
    return True


class MermaidGenerationTests(unittest.TestCase):
    """Unit tests for generate_mermaid_from_diagram."""

    def setUp(self) -> None:
        self.sample_diagram = {
            "version": 1,
            "parts": [
                {"type": "board-esp32-s3-devkitc-1", "id": "esp", "top": 100, "left": 50},
                {
                    "type": "wokwi-resistor",
                    "id": "r1",
                    "top": -80,
                    "left": 320,
                    "attrs": {"value": "220"},
                },
                {
                    "type": "wokwi-led",
                    "id": "led1",
                    "top": -150,
                    "left": 460,
                    "attrs": {"color": "red"},
                },
                {
                    "type": "wokwi-pushbutton",
                    "id": "btn1",
                    "top": 140,
                    "left": -140,
                    "attrs": {"label": "RESET"},
                },
            ],
            "connections": [
                ["btn1:1.l", "esp:7", "green", ["h40", "v80"]],
                ["esp:4", "r1:1", "orange", []],
                ["r1:2", "led1:A", "blue", []],
                ["esp:TX", "$serialMonitor:RX", "green", []],
            ],
        }

    def test_mermaid_structure_and_enclosure(self) -> None:
        text = generate_mermaid_from_diagram(self.sample_diagram)
        self.assertTrue(text.startswith("```mermaid\nflowchart LR"))
        self.assertTrue(text.endswith("```"))

    def test_board_subgraph_is_generated(self) -> None:
        text = generate_mermaid_from_diagram(self.sample_diagram)
        self.assertIn('subgraph Board["board-esp32-s3-devkitc-1"]', text)
        self.assertIn("esp[esp]", text)

    def test_component_labels(self) -> None:
        text = generate_mermaid_from_diagram(self.sample_diagram)
        self.assertIn('r1("r1 [220Ω]")', text)
        self.assertIn('led1("led1 [LED red]")', text)
        self.assertIn('btn1("btn1 [RESET]")', text)

    def test_serial_monitor_is_excluded(self) -> None:
        text = generate_mermaid_from_diagram(self.sample_diagram)
        self.assertNotIn("$serialMonitor", text)

    def test_connection_pin_labels(self) -> None:
        text = generate_mermaid_from_diagram(self.sample_diagram)
        self.assertIn("btn1 -->|1.l -> 7| esp", text)
        self.assertIn("esp -->|4 -> 1| r1", text)
        self.assertIn("r1 -->|2 -> A| led1", text)


class DiagramValidationTests(unittest.TestCase):
    """Unit tests for validate_diagram."""

    def test_a_well_formed_diagram_passes(self) -> None:
        validate_diagram(SIMPLE_DIAGRAM)

    def test_an_unknown_part_in_a_connection_fails(self) -> None:
        diagram = {"parts": [{"id": "esp"}], "connections": [["esp:1", "r9:1"]]}
        with self.assertRaises(ValueError):
            validate_diagram(diagram)

    def test_duplicate_part_ids_fail(self) -> None:
        diagram = {"parts": [{"id": "esp"}, {"id": "esp"}], "connections": []}
        with self.assertRaises(ValueError):
            validate_diagram(diagram)

    def test_a_malformed_terminal_fails(self) -> None:
        diagram = {"parts": [{"id": "esp"}], "connections": [["esp:1", "oops"]]}
        with self.assertRaises(ValueError):
            validate_diagram(diagram)


class SchematicSvgTests(unittest.TestCase):
    """Unit tests for the universal vector renderer."""

    def setUp(self) -> None:
        if not _schemdraw_available():
            self.skipTest("schemdraw is only installed inside `uv run`")

    def test_a_two_terminal_chain_renders_labelled_wires(self) -> None:
        svg = render_schematic_svg(SIMPLE_DIAGRAM)
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.strip().endswith("</svg>"))
        self.assertIn("GPIO15", svg)
        self.assertIn("GPIO21", svg)
        self.assertIn("r1 220Ω", svg)
        self.assertIn("led1 red LED", svg)
        self.assertIn('fill="#ffffff"', svg)

    def test_a_multi_pin_part_falls_back_to_net_labels(self) -> None:
        svg = render_schematic_svg(MULTI_PIN_DIAGRAM)
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("GPIO15", svg)
        self.assertIn("GPIO16", svg)
        self.assertIn("GPIO17", svg)
        self.assertIn("ic1", svg)

    def test_rendering_is_deterministic(self) -> None:
        self.assertEqual(render_schematic_svg(SIMPLE_DIAGRAM), render_schematic_svg(SIMPLE_DIAGRAM))


class SchematicCliTests(unittest.TestCase):
    """End-to-end tests for the CLI execution."""

    def test_missing_directory_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            res = run_schematic(tmpdir)
            self.assertEqual(res.returncode, 1)
            self.assertIn("ERROR: No diagram.json found", res.stderr)

    def test_multi_pin_diagram_renders_via_cli(self) -> None:
        """The net-label fallback must be exercised through `uv run` in CI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hw_dir = Path(tmpdir)
            assets_dir = hw_dir / "assets"
            assets_dir.mkdir(parents=True)
            (assets_dir / "diagram.json").write_text(
                json.dumps(MULTI_PIN_DIAGRAM), encoding="utf-8"
            )

            res = run_schematic(str(hw_dir), "--svg")
            self.assertEqual(res.returncode, 0)
            content = (assets_dir / "schematic.svg").read_text(encoding="utf-8")
            self.assertIn("GPIO15", content)
            self.assertIn("GPIO16", content)
            self.assertIn("GPIO17", content)
            self.assertIn("ic1", content)

    def test_rendering_is_deterministic_via_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            hw_dir = Path(tmpdir)
            assets_dir = hw_dir / "assets"
            assets_dir.mkdir(parents=True)
            (assets_dir / "diagram.json").write_text(
                json.dumps(SIMPLE_DIAGRAM), encoding="utf-8"
            )

            self.assertEqual(run_schematic(str(hw_dir), "--svg").returncode, 0)
            first = (assets_dir / "schematic.svg").read_bytes()
            self.assertEqual(run_schematic(str(hw_dir), "--svg").returncode, 0)
            self.assertEqual(first, (assets_dir / "schematic.svg").read_bytes())

    def test_svg_and_check_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            hw_dir = Path(tmpdir)
            assets_dir = hw_dir / "assets"
            assets_dir.mkdir(parents=True)
            diagram_file = assets_dir / "diagram.json"
            diagram_file.write_text(json.dumps(SIMPLE_DIAGRAM), encoding="utf-8")

            # A missing SVG is a drift failure.
            res_check1 = run_schematic(str(hw_dir), "--check")
            self.assertEqual(res_check1.returncode, 1)
            self.assertIn("is missing", res_check1.stderr)

            res_svg = run_schematic(str(hw_dir), "--svg")
            self.assertEqual(res_svg.returncode, 0)
            self.assertIn("Generated schematic SVG", res_svg.stdout)
            svg_file = assets_dir / "schematic.svg"
            self.assertTrue(svg_file.is_file())

            res_check2 = run_schematic(str(hw_dir), "--check")
            self.assertEqual(res_check2.returncode, 0)

            res_mermaid = run_schematic(str(hw_dir), "--mermaid")
            self.assertEqual(res_mermaid.returncode, 0)
            self.assertIn("flowchart LR", res_mermaid.stdout)

            res_all = run_schematic(str(hw_dir), "--all")
            self.assertEqual(res_all.returncode, 0)
            self.assertIn("Generated schematic SVG", res_all.stdout)
            self.assertIn("flowchart LR", res_all.stdout)

            # A changed diagram makes the committed SVG stale.
            changed = dict(SIMPLE_DIAGRAM)
            changed["parts"] = SIMPLE_DIAGRAM["parts"] + [
                {"type": "wokwi-led", "id": "led2", "attrs": {"color": "green"}}
            ]
            changed["connections"] = SIMPLE_DIAGRAM["connections"] + [
                ["r1:1", "led2:A", "purple", []],
                ["led2:C", "esp:GND.1", "black", []],
            ]
            diagram_file.write_text(json.dumps(changed), encoding="utf-8")
            res_check3 = run_schematic(str(hw_dir), "--check")
            self.assertEqual(res_check3.returncode, 1)
            self.assertIn("is stale", res_check3.stderr)


if __name__ == "__main__":
    unittest.main()
