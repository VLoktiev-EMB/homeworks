"""Tests for scripts/gen_schematic.py.

Verifies Mermaid flowchart generation, clean Wokwi layout reformatting,
Manhattan routing waypoints, and CLI flags (--mermaid, --format, --check).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.gen_schematic import (
    generate_mermaid_from_diagram,
    generate_schematic_svg,
    reformat_police_flasher_diagram,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = str(REPO_ROOT / "scripts" / "gen_schematic.py")


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


class ReformatDiagramTests(unittest.TestCase):
    """Unit tests for reformat_police_flasher_diagram."""

    def setUp(self) -> None:
        self.raw_diagram = {
            "version": 1,
            "parts": [
                {"type": "board-esp32-s3-devkitc-1", "id": "esp", "top": 0, "left": 0},
                {"type": "wokwi-resistor", "id": "r1", "top": -60, "left": 300},
                {"type": "wokwi-led", "id": "led1", "top": -100, "left": 220},
                {"type": "wokwi-led", "id": "led2", "top": -140, "left": 220},
                {"type": "wokwi-resistor", "id": "r2", "top": -200, "left": 300},
                {"type": "wokwi-led", "id": "led3", "top": -240, "left": 220},
                {"type": "wokwi-pushbutton", "id": "btn1", "top": -300, "left": 220},
            ],
            "connections": [
                ["esp:4", "r1:1", "green", []],
            ],
        }

    def test_reformat_places_components_in_clean_zones(self) -> None:
        formatted = reformat_police_flasher_diagram(self.raw_diagram)
        parts_by_id = {p["id"]: p for p in formatted["parts"]}

        # Microcontroller board
        self.assertEqual(parts_by_id["esp"]["top"], 0)
        self.assertEqual(parts_by_id["esp"]["left"], 0)

        # Half breadboard adjacent to microcontroller
        self.assertIn("bb1", parts_by_id)
        self.assertEqual(parts_by_id["bb1"]["type"], "wokwi-breadboard-half")
        self.assertEqual(parts_by_id["bb1"]["top"], -30)
        self.assertEqual(parts_by_id["bb1"]["left"], 180)

        # Input button to the left
        self.assertEqual(parts_by_id["btn1"]["top"], 120)
        self.assertEqual(parts_by_id["btn1"]["left"], -140)

        # Output LEDs and resistors on breadboard
        self.assertEqual(parts_by_id["r1"]["left"], 230)
        self.assertEqual(parts_by_id["r2"]["left"], 230)
        self.assertEqual(parts_by_id["led1"]["left"], 360)
        self.assertEqual(parts_by_id["led2"]["left"], 360)
        self.assertEqual(parts_by_id["led3"]["left"], 360)

    def test_reformat_adds_manhattan_routing(self) -> None:
        formatted = reformat_police_flasher_diagram(self.raw_diagram)
        connections = formatted["connections"]

        # Ensure all hardware connections have Manhattan waypoints
        hw_conns = [
            c for c in connections if "$serialMonitor" not in c[0] and "$serialMonitor" not in c[1]
        ]
        for conn in hw_conns:
            src, dst, color, bends = conn
            self.assertIsInstance(bends, list)
            self.assertGreater(len(bends), 0, f"Connection {src}->{dst} must have bends")
            for bend in bends:
                self.assertTrue(
                    bend.startswith("h") or bend.startswith("v"),
                    f"Bend {bend} in {src}->{dst} must be Manhattan horizontal or vertical",
                )


class SchematicSvgTests(unittest.TestCase):
    """Unit tests for vector SVG generation."""

    def test_generate_schematic_svg_via_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            hw_dir = Path(tmpdir)
            assets_dir = hw_dir / "assets"
            assets_dir.mkdir(parents=True)
            diagram_file = assets_dir / "diagram.json"
            diagram_file.write_text(
                '{"version": 1, "parts": [], "connections": []}', encoding="utf-8"
            )

            res = run_schematic(str(hw_dir), "--svg")
            self.assertEqual(res.returncode, 0)
            self.assertIn("Generated schematic SVG", res.stdout)

            svg_file = assets_dir / "schematic.svg"
            self.assertTrue(svg_file.is_file())
            content = svg_file.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("<svg"))
            self.assertTrue(content.strip().endswith("</svg>"))
            self.assertIn("ESP32-S3", content)
            self.assertIn("GPIO4", content)
            self.assertIn("GPIO6", content)
            self.assertIn("GPIO7", content)
            self.assertIn("MODE", content)
            self.assertIn("150Ω", content)

    def test_generate_schematic_svg_direct_if_available(self) -> None:
        try:
            import schemdraw  # noqa: F401
        except ImportError:
            self.skipTest("schemdraw not installed in test runner environment; verified via uv run")

        with tempfile.TemporaryDirectory() as tmpdir:
            svg_path = Path(tmpdir) / "schematic.svg"
            result_path = generate_schematic_svg(svg_path)
            self.assertEqual(result_path, svg_path)
            self.assertTrue(svg_path.is_file())
            content = svg_path.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("<svg"))
            self.assertTrue(content.strip().endswith("</svg>"))


class SchematicCliTests(unittest.TestCase):
    """End-to-end tests for the CLI execution."""

    def test_missing_directory_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            res = run_schematic(tmpdir)
            self.assertEqual(res.returncode, 1)
            self.assertIn("ERROR: No diagram.json found", res.stderr)

    def test_format_and_check_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            hw_dir = Path(tmpdir)
            assets_dir = hw_dir / "assets"
            assets_dir.mkdir(parents=True)
            diagram_file = assets_dir / "diagram.json"

            raw_diagram = {
                "version": 1,
                "parts": [
                    {"type": "board-esp32-s3-devkitc-1", "id": "esp", "top": 0, "left": 0},
                    {"type": "wokwi-pushbutton", "id": "btn1", "top": 0, "left": 0},
                ],
                "connections": [],
            }
            diagram_file.write_text(json.dumps(raw_diagram), encoding="utf-8")

            # Check fails before formatting
            res_check1 = run_schematic(str(hw_dir), "--check")
            self.assertEqual(res_check1.returncode, 1)

            # Format in place
            res_format = run_schematic(str(hw_dir), "--format")
            self.assertEqual(res_format.returncode, 0)
            self.assertIn("Formatted", res_format.stdout)

            # Check passes after formatting
            res_check2 = run_schematic(str(hw_dir), "--check")
            self.assertEqual(res_check2.returncode, 0)

            # Mermaid output
            res_mermaid = run_schematic(str(hw_dir), "--mermaid")
            self.assertEqual(res_mermaid.returncode, 0)
            self.assertIn("flowchart LR", res_mermaid.stdout)

            # Schemdraw SVG generation
            res_svg = run_schematic(str(hw_dir), "--svg")
            self.assertEqual(res_svg.returncode, 0)
            self.assertIn("Generated schematic SVG", res_svg.stdout)
            self.assertTrue((hw_dir / "assets" / "schematic.svg").is_file())

            # Combined --all execution
            res_all = run_schematic(str(hw_dir), "--all")
            self.assertEqual(res_all.returncode, 0)
            self.assertIn("Formatted", res_all.stdout)
            self.assertIn("Generated schematic SVG", res_all.stdout)
            self.assertIn("flowchart LR", res_all.stdout)


if __name__ == "__main__":
    unittest.main()
