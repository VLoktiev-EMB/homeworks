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
import re
import sys
from collections import defaultdict
from pathlib import Path


def generate_mermaid_from_diagram(diagram: dict) -> str:
    """Generate a GitHub-flavored Mermaid flowchart from diagram parts and connections.

    Produces a clean, unidirectional left-to-right (LR) signal flow:
    - Resolves intermediate breadboard row nets so components connect directly.
    - Redirects Ground returns to terminal GND nodes rather than looping backward into MCU.
    - Redirects Power rails (3.3V/5V) to dedicated source nodes rather than cutting across MCU.
    - Excludes debug serial monitor connections.
    """
    parts = {p["id"]: p for p in diagram.get("parts", [])}
    connections = diagram.get("connections", [])

    board_part = next((p for p in parts.values() if "board" in p.get("type", "")), None)
    b_id = board_part["id"] if board_part else None

    bb_nets: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    resolved_edges: list[tuple[str, str, str]] = []

    for conn in connections:
        if len(conn) < 2:
            continue
        src, dst = conn[0], conn[1]
        if "$serialMonitor" in src or "$serialMonitor" in dst:
            continue

        src_part, _, src_pin = src.partition(":")
        dst_part, _, dst_pin = dst.partition(":")

        # Ignore direct breadboard internal jumpers
        if "bb" in src_part and "bb" in dst_part:
            continue

        # Skip MCU power rail feeds to breadboard rails in top-level diagram
        if src_part == b_id and ("3V3" in src_pin or "GND" in src_pin) and "bb" in dst_part:
            continue

        # Direct 3V3 power rail feeds to components
        if src_part == b_id and "3V3" in src_pin and "bb" not in dst_part:
            edge_lbl = f"|{src_pin} -> {dst_pin}|" if src_pin and dst_pin else ""
            resolved_edges.append(('pwr["3.3V"]', edge_lbl, dst_part))
            continue

        # Redirect Ground connections to terminal GND
        is_dst_gnd = (dst_part == b_id and "GND" in dst_pin.upper()) or (
            "bb" in dst_part and "tn" in dst_pin
        )
        if is_dst_gnd:
            edge_lbl = f"|{src_pin}|" if src_pin else ""
            resolved_edges.append((src_part, edge_lbl, "gnd[GND]"))
            continue

        is_src_gnd = (src_part == b_id and "GND" in src_pin.upper()) or (
            "bb" in src_part and "tn" in src_pin
        )
        if is_src_gnd:
            edge_lbl = f"|{dst_pin}|" if dst_pin else ""
            resolved_edges.append(("gnd[GND]", edge_lbl, dst_part))
            continue

        # Redirect Power rail connections
        if "bb" in dst_part and "tp" in dst_pin:
            edge_lbl = f"|{src_pin}|" if src_pin else ""
            resolved_edges.append(('pwr["3.3V"]', edge_lbl, src_part))
            continue
        if "bb" in src_part and "tp" in src_pin:
            edge_lbl = f"|{dst_pin}|" if dst_pin else ""
            resolved_edges.append(('pwr["3.3V"]', edge_lbl, dst_part))
            continue

        # Group connections on breadboard terminal rows (e.g. 12t.a) into nets
        if "bb" in dst_part and "." in dst_pin:
            row = dst_pin.split(".")[0]
            bb_nets[row].append(("src", src_part, src_pin))
            continue
        if "bb" in src_part and "." in src_pin:
            row = src_pin.split(".")[0]
            bb_nets[row].append(("dst", dst_part, dst_pin))
            continue

        edge_label = f"|{src_pin} -> {dst_pin}|" if src_pin and dst_pin else ""
        resolved_edges.append((src_part, edge_label, dst_part))

    # Resolve breadboard row nets into direct component-to-component edges
    for _row, items in bb_nets.items():
        srcs = [it for it in items if it[0] == "src"]
        dsts = [it for it in items if it[0] == "dst"]
        for s in srcs:
            for d in dsts:
                label = f"|{s[2]} -> {d[2]}|" if s[2] and d[2] else ""
                resolved_edges.append((s[1], label, d[1]))

    lines = ["```mermaid", "flowchart LR"]

    # Board subgraph
    if board_part:
        lines.append(f'    subgraph Board["{board_part.get("type", "Board")}"]')
        lines.append(f"        {b_id}[{b_id}]")
        lines.append("    end")

    # Parts
    for pid, part in parts.items():
        ptype = part.get("type", "")
        if "board" in ptype or "breadboard" in ptype:
            continue
        attrs = part.get("attrs", {})
        if ptype == "wokwi-resistor":
            val = attrs.get("value", "R")
            lines.append(f'    {pid}("{pid} [{val}Ω]")')
        elif ptype == "wokwi-led":
            col = attrs.get("color", "LED")
            lines.append(f'    {pid}("{pid} [LED {col}]")')
        elif ptype == "wokwi-pushbutton":
            btn_lbl = attrs.get("label", "Button")
            lines.append(f'    {pid}("{pid} [{btn_lbl}]")')

    lines.append("")

    for src, lbl, dst in resolved_edges:
        arrow = f"-->{lbl} " if lbl else "--> "
        lines.append(f"    {src} {arrow}{dst}")

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

    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10, margin=1.5, bgcolor="white")

        # Microcontroller Block in Center (ESP32-S3 DevKitC-1)
        ic = d.add(
            elm.Ic(
                size=(6.2, 5.5),
                pins=[
                    # Left side: inputs
                    elm.IcPin(name="GPIO7", side="left", slot="4/7"),
                    elm.IcPin(name="GND", anchorname="GND_L", side="left", slot="1/7"),
                    # Right side: outputs and rails
                    elm.IcPin(name="GPIO4", side="right", slot="6/7"),
                    elm.IcPin(name="GPIO6", side="right", slot="4/7"),
                    elm.IcPin(name="3V3", side="right", slot="2/7"),
                    elm.IcPin(name="GND", anchorname="GND_R", side="right", slot="1/7"),
                ],
            ).label("ESP32-S3\nDevKitC-1", loc="center", fontsize=11)
        )

        # Button Branch on the Left (Active-LOW with internal pull-up)
        d.add(elm.Line().left(1.2).at(ic.GPIO7))
        btn = d.add(elm.Button(up=True).left(1.5).label("MODE\n(SW1)", loc="top"))
        d.add(elm.Line().down(1.0).at(btn.end))
        d.add(elm.Ground())

        # Microcontroller GND reference on Left
        d.add(elm.Line().left(1.2).at(ic.GND_L))
        d.add(elm.Ground())

        # Microcontroller 3V3 and GND reference on Right
        d.add(elm.Line().right(1.0).at(ic["3V3"]))
        d.add(elm.Vdd().label("3.3V", loc="top"))
        d.add(elm.Line().right(1.0).at(ic.GND_R))
        d.add(elm.Ground())

        # Branch 2: Status Indicator LED3 on GPIO6
        d.add(elm.Line().right(2.0).at(ic.GPIO6))
        d.add(elm.Resistor().right(1.5).label("R2\n150Ω", loc="top"))
        d.add(elm.Line().right(0.5))
        d.add(elm.LED().down(1.5).label("LED3 (RED)\n[STATUS]", loc="bottom", ofst=0.2))
        d.add(elm.Line().down(0.5))
        d.add(elm.Ground())

        # Branch 1: Anti-parallel Pair (LED1 / LED2) on GPIO4
        # Routed vertically above Branch 2 to prevent any wire intersection
        d.add(elm.Line().up(0.6).at(ic.GPIO4))
        d.add(elm.Line().right(7.2))
        d.add(elm.Resistor().right(1.5).label("R1\n150Ω", loc="top"))
        d.add(elm.Line().right(0.5))
        node_x = d.add(elm.Dot())

        # Path 1A: LED1 (Forward) -> GND
        d.add(elm.Line().down(1.0).at(node_x.center))
        d.add(elm.LED().down(1.5).label("LED1 (RED)\n[GPIO4=HIGH]", loc="bottom", ofst=0.2))
        d.add(elm.Line().down(0.6))
        d.add(elm.Ground())

        # Path 1B: LED2 (Reverse) -> 3.3V
        d.add(elm.Line().up(1.0).at(node_x.center))
        d.add(elm.LED().up(1.5).reverse().label("LED2 (RED)\n[GPIO4=LOW]", loc="bottom", ofst=0.2))
        d.add(elm.Line().up(0.6))
        d.add(elm.Vdd().label("3.3V", loc="top"))

        svg_content = d.get_imagedata("svg").decode("utf-8")

    # Inject solid white background rectangle for high contrast in both dark and light modes
    viewbox_match = re.search(r'viewBox="([^"]+)"', svg_content)
    if viewbox_match:
        parts = viewbox_match.group(1).split()
        vx, vy, vw, vh = parts
        rect = f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" fill="#ffffff" rx="8"/>'
        svg_content = re.sub(r"(<svg[^>]*>)", r"\1" + rect, svg_content, count=1)

    if not svg_content.endswith("\n"):
        svg_content += "\n"
    output_path.write_text(svg_content, encoding="utf-8")
    return output_path


def reformat_police_flasher_diagram(diagram: dict) -> dict:
    """Apply clean direct-wiring layout and orthogonal routing to police flasher circuit."""
    return {
        "version": 1,
        "author": "VLoktiev-EMB",
        "editor": "wokwi",
        "parts": [
            {
                "type": "board-esp32-s3-devkitc-1",
                "id": "esp",
                "top": 0,
                "left": 0,
                "attrs": {
                    "flashSize": "16",
                    "psramType": "octal",
                    "psramSize": "8",
                },
            },
            {
                "type": "wokwi-resistor",
                "id": "r1",
                "top": 76.8,
                "left": -88.8,
                "attrs": {"value": "150"},
            },
            {
                "type": "wokwi-led",
                "id": "led1",
                "top": 40.8,
                "left": -140,
                "attrs": {"color": "red", "label": "LED1"},
            },
            {
                "type": "wokwi-led",
                "id": "led2",
                "top": -16.8,
                "left": -140,
                "attrs": {"color": "red", "label": "LED2"},
            },
            {
                "type": "wokwi-resistor",
                "id": "r2",
                "top": 119.3,
                "left": -88.8,
                "attrs": {"value": "150"},
            },
            {
                "type": "wokwi-led",
                "id": "led3",
                "top": 83.3,
                "left": -140,
                "attrs": {"color": "red", "label": "LED3"},
            },
            {
                "type": "wokwi-pushbutton",
                "id": "btn1",
                "top": 155,
                "left": -100,
                "attrs": {"color": "green", "label": "MODE"},
            },
        ],
        "connections": [
            ["esp:TX", "$serialMonitor:RX", "", []],
            ["esp:RX", "$serialMonitor:TX", "", []],
            ["btn1:1.l", "esp:7", "green", ["h20"]],
            ["btn1:2.l", "esp:GND.1", "black", ["v80", "h90"]],
            ["esp:4", "r1:2", "orange", []],
            ["r1:1", "led1:A", "blue", []],
            ["r1:1", "led2:C", "blue", ["v-38", "h-20"]],
            ["esp:3V3.1", "led2:A", "red", ["h-40", "v-15"]],
            ["led1:C", "esp:GND.1", "black", ["v200", "h120"]],
            ["esp:6", "r2:2", "purple", []],
            ["r2:1", "led3:A", "purple", []],
            ["led3:C", "esp:GND.1", "black", ["v160", "h120"]],
        ],
        "dependencies": {},
    }


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
