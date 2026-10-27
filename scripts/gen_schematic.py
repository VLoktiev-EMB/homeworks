#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3", "schemdraw==0.23"]
# ///
"""Generate clean Wokwi diagram layouts, Schemdraw vector SVGs, and Mermaid schematics.

Provides automated layout helpers, breadboard integration, Manhattan routing,
IEEE vector schematic generation via Schemdraw, and Mermaid diagrams for homework
circuits.

Usage:
  uv run scripts/gen_schematic.py <homework_dir> [--mermaid] [--svg] [--format] [--check] [--all]
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
        ptype = part.get("type", "")
        if "board" in ptype or "breadboard" in ptype:
            continue
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
        lines.append(f'    {pid}("{label}")')

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

        # Ignore direct breadboard internal jumper lines for clean top-level Mermaid
        if "bb" in src_part and "bb" in dst_part:
            continue

        edge_label = f"|{src_pin} -> {dst_pin}|" if src_pin and dst_pin else ""
        lines.append(f"    {src_part} -->{edge_label} {dst_part}")

    lines.append("```")
    return "\n".join(lines)


def generate_schematic_svg(output_path: Path) -> Path:
    """Generate an IEEE standard vector schematic SVG using Schemdraw."""
    try:
        import schemdraw
        import schemdraw.elements as elm
    except ImportError as exc:
        raise RuntimeError(
            "schemdraw is required to generate vector SVGs. Run via uv run."
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with schemdraw.Drawing(file=str(output_path), show=False) as d:
        d.config(unit=2.0, fontsize=11)

        # Microcontroller Block in Center
        ic = d.add(
            elm.Ic(
                pins=[
                    # Left side: inputs
                    elm.IcPin(name="GPIO7", side="left", slot="2/2"),
                    elm.IcPin(name="GND_L", pin="GND", side="left", slot="1/2"),
                    # Right side: outputs
                    elm.IcPin(name="GPIO4", side="right", slot="4/4"),
                    elm.IcPin(name="GPIO6", side="right", slot="3/4"),
                    elm.IcPin(name="3V3", pin="3.3V", side="right", slot="2/4"),
                    elm.IcPin(name="GND_R", pin="GND", side="right", slot="1/4"),
                ],
                w=3.5,
                h=4.5,
            ).label("ESP32-S3\nDevKitC-1", loc="center")
        )

        # Button Branch on the Left
        d.add(elm.Line().left(1.5).at(ic.GPIO7))
        btn = d.add(elm.Button(up=True).left(1.5).label("MODE\n(SW1)", loc="top"))
        d.add(elm.Line().down(1.0).at(btn.start))
        d.add(elm.Ground())

        # Branch 1 (Anti-parallel pair) on the Right
        d.add(elm.Line().right(1.5).at(ic.GPIO4))
        d.add(elm.Resistor().right(1.5).label("R1\n150Ω", loc="top"))
        node_x = d.add(elm.Dot())

        # Path 1A: LED1 (Forward) -> GND
        d.add(elm.Line().down(1.0).at(node_x.center))
        d.add(elm.LED().down(1.5).label("LED1 (RED)\n[GPIO4=HIGH]", loc="right"))
        d.add(elm.Ground())

        # Path 1B: LED2 (Reverse to 3.3V)
        d.add(elm.Line().up(1.0).at(node_x.center))
        d.add(elm.LED().up(1.5).reverse().label("LED2 (RED)\n[GPIO4=LOW]", loc="right"))
        d.add(elm.Vdd().label("3.3V"))

        # Branch 2 (Indicator LED3) on the Right
        d.add(elm.Line().right(2.5).at(ic.GPIO6))
        d.add(elm.Resistor().right(1.5).label("R2\n150Ω", loc="top"))
        d.add(elm.LED().down(1.5).label("LED3 (RED)\n[GPIO6=HIGH]", loc="right"))
        d.add(elm.Ground())

        # Power rails reference
        d.add(elm.Line().right(1.0).at(ic["3V3"]))
        d.add(elm.Vdd().label("3.3V"))

        d.add(elm.Line().right(1.0).at(ic.GND_R))
        d.add(elm.Ground())

    return output_path


def reformat_police_flasher_diagram(diagram: dict) -> dict:
    """Apply clean breadboard layout and Manhattan wire routing to anti-parallel LED circuit."""
    new_diagram = dict(diagram)
    parts = []

    # Map existing parts and ensure breadboard is present
    has_breadboard = any(p.get("type") == "wokwi-breadboard-half" for p in diagram.get("parts", []))

    for p in diagram.get("parts", []):
        part = dict(p)
        pid = part["id"]
        if pid == "esp":
            part["top"] = 0
            part["left"] = 0
        elif pid == "bb1":
            part["top"] = -30
            part["left"] = 180
        elif pid == "btn1":
            # Input button to the left
            part["top"] = 120
            part["left"] = -140
        elif pid == "r1":
            # Branch 1 series resistor on breadboard
            part["top"] = 30
            part["left"] = 230
            part["attrs"] = dict(part.get("attrs", {}))
        elif pid == "led1":
            # Branch 1 forward LED
            part["top"] = 0
            part["left"] = 360
        elif pid == "led2":
            # Branch 1 reverse LED (anti-parallel)
            part["top"] = 70
            part["left"] = 360
        elif pid == "r2":
            # Branch 2 series resistor on breadboard
            part["top"] = 150
            part["left"] = 230
        elif pid == "led3":
            # Branch 2 indicator LED
            part["top"] = 150
            part["left"] = 360
        parts.append(part)

    if not has_breadboard:
        parts.insert(
            1,
            {
                "type": "wokwi-breadboard-half",
                "id": "bb1",
                "top": -30,
                "left": 180,
                "attrs": {},
            },
        )

    new_diagram["parts"] = parts

    # Clean Manhattan connections on breadboard
    new_diagram["connections"] = [
        # Power rails to breadboard
        ["esp:3V3.1", "bb1:tp.1", "red", ["h30", "v-60"]],
        ["esp:GND.1", "bb1:tn.1", "black", ["h20", "v-80"]],
        # Button: GPIO7 -> btn1:1.l, btn1:2.l -> GND
        ["btn1:1.l", "esp:7", "green", ["h30", "v30"]],
        ["btn1:2.l", "esp:GND.1", "black", ["v100", "h180"]],
        # Branch 1: GPIO4 -> r1 -> Node X (row 12 on breadboard)
        ["esp:4", "r1:1", "orange", ["h40", "v-20"]],
        ["r1:2", "bb1:12t.a", "blue", ["h10"]],
        ["bb1:12t.b", "led1:A", "blue", ["h20", "v-20"]],
        ["led1:C", "bb1:tn.15", "black", ["v-20"]],
        ["bb1:12t.c", "led2:C", "blue", ["h20", "v20"]],
        ["led2:A", "bb1:tp.15", "red", ["v-40"]],
        # Branch 2: GPIO6 -> r2 -> led3 -> GND rail
        ["esp:6", "r2:1", "purple", ["h50", "v50"]],
        ["r2:2", "led3:A", "red", ["h20"]],
        ["led3:C", "bb1:tn.22", "black", ["v-100"]],
        # Serial monitor
        ["esp:TX", "$serialMonitor:RX", "green", []],
        ["esp:RX", "$serialMonitor:TX", "green", []],
    ]

    return new_diagram


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Wokwi layouts, Schemdraw SVGs, and Mermaid schematics."
    )
    parser.add_argument("directory", help="Homework directory (e.g. homeworks/<id>)")
    parser.add_argument("--mermaid", action="store_true", help="Print generated Mermaid flowchart")
    parser.add_argument(
        "--svg", action="store_true", help="Generate IEEE vector schematic SVG via Schemdraw"
    )
    parser.add_argument(
        "--format", action="store_true", help="Apply clean layout and routing to diagram.json"
    )
    parser.add_argument("--check", action="store_true", help="Check if diagram.json is formatted")
    parser.add_argument(
        "--all", action="store_true", help="Format diagram, generate SVG, and output Mermaid"
    )

    args = parser.parse_args()

    hw_dir = Path(args.directory)
    diagram_path = hw_dir / "assets" / "diagram.json"
    if not diagram_path.is_file():
        diagram_path = hw_dir / "diagram.json"

    if not diagram_path.is_file():
        print(f"ERROR: No diagram.json found in {hw_dir}", file=sys.stderr)
        return 1

    try:
        content = json.loads(diagram_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: Failed to read {diagram_path}: {exc}", file=sys.stderr)
        return 1

    if args.format or args.all:
        formatted = reformat_police_flasher_diagram(content)
        diagram_path.write_text(json.dumps(formatted, indent=2) + "\n", encoding="utf-8")
        print(f"Formatted {diagram_path}")
        content = formatted

    if args.svg or args.all:
        svg_path = hw_dir / "assets" / "schematic.svg"
        generate_schematic_svg(svg_path)
        print(f"Generated schematic SVG: {svg_path}")

    if args.mermaid or args.all:
        mermaid_text = generate_mermaid_from_diagram(content)
        print(mermaid_text)

    if args.check:
        formatted = reformat_police_flasher_diagram(content)
        if content != formatted:
            print(f"ERROR: {diagram_path} is not formatted cleanly", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
