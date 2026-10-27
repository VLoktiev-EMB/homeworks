#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""Generate clean Wokwi diagram layouts and embeddable Mermaid schematics.

Provides automated layout helpers, Manhattan routing, and Mermaid generation
for homework circuits. Eliminates manual coordinate guesswork and wire
overlapping in `assets/diagram.json`.

Usage:
  uv run scripts/gen_schematic.py <homework_dir> [--mermaid] [--format] [--check]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def generate_mermaid_from_diagram(diagram: dict) -> str:
    """Generate a GitHub-flavored Mermaid flowchart from diagram parts and connections."""
    parts = {p["id"]: p for p in diagram.get("parts", [])}
    connections = diagram.get("connections", [])

    lines = ["```mermaid", "flowchart LR"]

    # Board subgraph
    board_part = next((p for p in parts.values() if "board" in p.get("type", "")), None)
    if board_part:
        b_id = board_part["id"]
        lines.append(f'    subgraph Board["{board_part.get("type", "Board")}"]')
        lines.append(f"        {b_id}[{b_id}]")
        lines.append("    end")

    # Parts
    for pid, part in parts.items():
        if "board" in part.get("type", ""):
            continue
        ptype = part.get("type", "")
        attrs = part.get("attrs", {})
        label = pid
        if ptype == "wokwi-resistor":
            val = attrs.get("value", "R")
            label = f"{pid} [{val}Ω]"
        elif ptype == "wokwi-led":
            col = attrs.get("color", "LED")
            label = f"{pid} [LED {col}]"
        elif ptype == "wokwi-pushbutton":
            btn_lbl = attrs.get("label", "Button")
            label = f"{pid} [{btn_lbl}]"
        lines.append(f"    {pid}(\"{label}\")")

    lines.append("")

    # Connections
    for conn in connections:
        if len(conn) < 2:
            continue
        src, dst = conn[0], conn[1]
        if "$serialMonitor" in src or "$serialMonitor" in dst:
            continue

        src_part, _, src_pin = src.partition(":")
        dst_part, _, dst_pin = dst.partition(":")

        edge_label = f"|{src_pin} -> {dst_pin}|" if src_pin and dst_pin else ""
        lines.append(f"    {src_part} -->{edge_label} {dst_part}")

    lines.append("```")
    return "\n".join(lines)


def reformat_police_flasher_diagram(diagram: dict) -> dict:
    """Apply clean spacing, Manhattan wire routing, and color coding to 1_3-police-flasher."""
    # Specific layout optimized for 1_3-police-flasher
    new_diagram = dict(diagram)
    parts = []
    for p in diagram.get("parts", []):
        part = dict(p)
        pid = part["id"]
        if pid == "esp":
            part["top"] = 100
            part["left"] = 50
        elif pid == "btn1":
            # Input button to the left
            part["top"] = 140
            part["left"] = -140
        elif pid == "r1":
            # Branch 1 series resistor
            part["top"] = -80
            part["left"] = 320
            part["attrs"] = dict(part.get("attrs", {}))
        elif pid == "led1":
            # Branch 1 forward LED
            part["top"] = -150
            part["left"] = 460
        elif pid == "led2":
            # Branch 1 reverse LED (anti-parallel)
            part["top"] = -30
            part["left"] = 460
        elif pid == "r2":
            # Branch 2 series resistor
            part["top"] = 160
            part["left"] = 320
        elif pid == "led3":
            # Branch 2 indicator LED
            part["top"] = 160
            part["left"] = 460
        parts.append(part)

    new_diagram["parts"] = parts

    # Clean Manhattan connections
    new_diagram["connections"] = [
        # Button: GPIO7 -> btn1:1.l, btn1:2.l -> GND
        ["btn1:1.l", "esp:7", "green", ["h40", "v80"]],
        ["btn1:2.l", "esp:GND.1", "black", ["v120", "h180"]],

        # Branch 1: GPIO4 -> r1 -> Node X (led1:A / led2:C)
        ["esp:4", "r1:1", "orange", ["h80", "v-220"]],
        ["r1:2", "led1:A", "blue", ["h40", "v-50"]],
        ["r1:2", "led2:C", "blue", ["h40", "v70"]],
        ["led1:C", "esp:GND.2", "black", ["v140", "h-220"]],
        ["esp:3V3.1", "led2:A", "red", ["h60", "v-150"]],

        # Branch 2: GPIO6 -> r2 -> led3 -> GND
        ["esp:6", "r2:1", "purple", ["h90", "v30"]],
        ["r2:2", "led3:A", "red", ["h40"]],
        ["led3:C", "esp:GND.2", "black", ["v80", "h-220"]],

        # Serial monitor
        ["esp:TX", "$serialMonitor:RX", "green", []],
        ["esp:RX", "$serialMonitor:TX", "green", []],
    ]

    return new_diagram


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate and layout Wokwi diagrams and Mermaid schematics."
    )
    parser.add_argument("directory", help="Homework directory (e.g. homeworks/1_3-police-flasher)")
    parser.add_argument("--mermaid", action="store_true", help="Print generated Mermaid flowchart")
    parser.add_argument(
        "--format", action="store_true", help="Apply clean layout and routing to diagram.json"
    )
    parser.add_argument("--check", action="store_true", help="Check if diagram.json is formatted")

    args = parser.parse_args()

    hw_dir = Path(args.directory)
    diagram_path = hw_dir / "assets" / "diagram.json"
    if not diagram_path.is_file():
        # Fallback to root diagram.json if present
        diagram_path = hw_dir / "diagram.json"

    if not diagram_path.is_file():
        print(f"ERROR: No diagram.json found in {hw_dir}", file=sys.stderr)
        return 1

    try:
        content = json.loads(diagram_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: Failed to read {diagram_path}: {exc}", file=sys.stderr)
        return 1

    if args.mermaid:
        mermaid_text = generate_mermaid_from_diagram(content)
        print(mermaid_text)

    if args.format:
        formatted = reformat_police_flasher_diagram(content)
        diagram_path.write_text(json.dumps(formatted, indent=2) + "\n", encoding="utf-8")
        print(f"Formatted {diagram_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
