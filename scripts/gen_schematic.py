#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3", "schemdraw==0.23"]
# ///
"""Generate clean Schemdraw vector SVGs and Mermaid schematics from a diagram.

The renderer is diagram-driven and names no homework, pin, or part. It chooses
a wired branch layout when every part is two-terminal and the net graph is a
forest, and a labelled net-stub layout otherwise, so an arbitrary component or
topology still produces a schematic.

Usage:
  uv run scripts/gen_schematic.py <homework_dir> [--mermaid] [--svg] [--check] [--all]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

# The renderer lives beside this script. Resolve it both when the file is run
# as `uv run scripts/gen_schematic.py` and when a test imports
# `scripts.gen_schematic`.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from schematic_svg import generate_schematic_svg as _generate_schematic_svg  # noqa: E402
from schematic_svg import render_schematic_svg as _render_schematic_svg  # noqa: E402


def generate_mermaid_from_diagram(diagram: dict) -> str:
    """Generate a GitHub-flavored Mermaid flowchart from diagram parts and connections.

    Produces a clean, unidirectional left-to-right (LR) signal flow:
    - Resolves intermediate breadboard row nets so components connect directly.
    - Redirects Ground returns to terminal GND nodes rather than looping backward into MCU.
    - Collapses a component-to-component ground bus into one GND sink per part.
    - Redirects Power rails (3.3V/5V) to dedicated source nodes rather than cutting across MCU.
    - Excludes debug serial monitor connections.
    """
    parts = {p["id"]: p for p in diagram.get("parts", [])}
    connections = diagram.get("connections", [])

    board_part = next((p for p in parts.values() if "board" in p.get("type", "")), None)
    b_id = board_part["id"] if board_part else None

    def is_ground_terminal(part: str, pin: str) -> bool:
        board_ground = part == b_id and "GND" in pin.upper()
        breadboard_ground = part.startswith("bb") and "tn" in pin.lower()
        symbol_ground = parts.get(part, {}).get("type") == "wokwi-gnd"
        return board_ground or breadboard_ground or symbol_ground

    def is_power_terminal(part: str, pin: str) -> bool:
        board_power = part == b_id and (
            "3V3" in pin.upper() or "5V" in pin.upper() or "VIN" in pin.upper()
        )
        symbol_power = parts.get(part, {}).get("type") == "wokwi-vcc"
        return board_power or symbol_power

    # Parts that reach the ground net through any pin. A shared ground bus
    # between two of them is a sink relationship, not a signal edge.
    ground_components: set[str] = set()
    power_components: set[str] = set()
    for conn in connections:
        if len(conn) < 2:
            continue
        for terminal, other in ((conn[0], conn[1]), (conn[1], conn[0])):
            part, _, pin = str(terminal).partition(":")
            other_part, _, _ = str(other).partition(":")
            if is_ground_terminal(part, pin):
                ground_components.add(other_part)
            if is_power_terminal(part, pin):
                power_components.add(other_part)
    ground_components = {
        part
        for part in ground_components
        if part and part != b_id and not part.startswith("$") and not part.startswith("bb")
    }
    power_components = {
        part
        for part in power_components
        if part and part != b_id and not part.startswith("$") and not part.startswith("bb")
    }
    ground_edges: set[str] = set()

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
        edge_label = f"|{src_pin} -> {dst_pin}|" if src_pin and dst_pin else ""

        # Ignore direct breadboard internal jumpers
        if "bb" in src_part and "bb" in dst_part:
            continue

        # Skip MCU power rail feeds to breadboard rails in top-level diagram
        if src_part == b_id and ("3V3" in src_pin or "GND" in src_pin) and "bb" in dst_part:
            continue

        # A cathode-to-cathode link is a shared ground bus, not a signal edge.
        # Both parts are anchored to the GND sink after the loop.
        if src_pin.upper() == "C" and dst_pin.upper() == "C":
            ground_components.update((src_part, dst_part))
            continue

        # Direct 3V3 power rail feeds to components, in either connection
        # order: the generator must not turn a rail feed into an MCU loopback.
        if src_part == b_id and "3V3" in src_pin and "bb" not in dst_part:
            edge_lbl = f"|{src_pin} -> {dst_pin}|" if src_pin and dst_pin else ""
            resolved_edges.append(('pwr["3.3V"]', edge_lbl, dst_part))
            continue
        if dst_part == b_id and "3V3" in dst_pin and "bb" not in src_part:
            edge_lbl = f"|{src_pin} -> {dst_pin}|" if src_pin and dst_pin else ""
            resolved_edges.append(('pwr["3.3V"]', edge_lbl, src_part))
            continue

        # A Wokwi VCC symbol is a rail source, just like the board 3V3 pin.
        if parts.get(src_part, {}).get("type") == "wokwi-vcc":
            edge_lbl = f"|{dst_pin}|" if dst_pin else ""
            resolved_edges.append(('pwr["3.3V"]', edge_lbl, dst_part))
            continue
        if parts.get(dst_part, {}).get("type") == "wokwi-vcc":
            edge_lbl = f"|{src_pin}|" if src_pin else ""
            resolved_edges.append(('pwr["3.3V"]', edge_lbl, src_part))
            continue

        # Redirect Ground connections to terminal GND
        is_dst_gnd = is_ground_terminal(dst_part, dst_pin)
        if is_dst_gnd:
            edge_lbl = f"|{src_pin}|" if src_pin else ""
            resolved_edges.append((src_part, edge_lbl, "gnd[GND]"))
            ground_edges.add(src_part)
            continue

        is_src_gnd = is_ground_terminal(src_part, src_pin)
        if is_src_gnd:
            edge_lbl = f"|{dst_pin}|" if dst_pin else ""
            resolved_edges.append(("gnd[GND]", edge_lbl, dst_part))
            ground_edges.add(dst_part)
            continue

        # A ground bus between two components is not a signal edge. Both parts
        # are anchored to gnd below, so the block diagram keeps one sink.
        if src_part in ground_components and dst_part in ground_components:
            continue

        # A component fed from a power rail is the source end of a chain. The
        # connection order in diagram.json is electrical, not directional, so
        # reverse the edge when the rail-fed part is written second.
        if src_part in power_components and dst_part not in power_components:
            resolved_edges.append((src_part, edge_label, dst_part))
            continue
        if dst_part in power_components and src_part not in power_components:
            reverse_label = f"|{dst_pin} -> {src_pin}|" if src_pin and dst_pin else ""
            resolved_edges.append((dst_part, reverse_label, src_part))
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

        resolved_edges.append((src_part, edge_label, dst_part))

    # Resolve breadboard row nets into direct component-to-component edges
    for _row, items in bb_nets.items():
        srcs = [it for it in items if it[0] == "src"]
        dsts = [it for it in items if it[0] == "dst"]
        for s in srcs:
            for d in dsts:
                label = f"|{s[2]} -> {d[2]}|" if s[2] and d[2] else ""
                resolved_edges.append((s[1], label, d[1]))

    # A part that reaches ground only through another part's cathode still
    # belongs at the GND sink, not at a component-to-component edge.
    for component in sorted(ground_components):
        if component not in ground_edges:
            resolved_edges.append((component, "", "gnd[GND]"))

    lines = ["```mermaid", "flowchart LR"]

    # Board subgraph
    if board_part:
        lines.append(f'    subgraph Board["{board_part.get("type", "Board")}"]')
        lines.append(f"        {b_id}[{b_id}]")
        lines.append("    end")

    # Parts
    for pid, part in parts.items():
        ptype = part.get("type", "")
        if (
            "board" in ptype
            or "breadboard" in ptype
            or ptype in ("wokwi-gnd", "wokwi-vcc", "wokwi-text", "wokwi-junction")
        ):
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


def generate_schematic_svg(diagram: dict, output_path: Path) -> Path:
    """Render an IEEE vector schematic from the diagram.

    The layout is chosen by `scripts/schematic_svg.py`: real wires for discrete
    two-terminal branches, labelled net stubs for anything else. No homework,
    pin, or part is named here, so a new diagram needs no new renderer code.
    """
    return _generate_schematic_svg(diagram, output_path)


def validate_diagram(diagram: dict) -> None:
    """Check that a diagram is structurally usable; raise ValueError on a defect.

    The check is deliberately about referential integrity, not about a specific
    circuit: every part id is unique, and every connection names a part that
    exists. A renderer needs no more than that.
    """
    parts = diagram.get("parts")
    if not isinstance(parts, list):
        raise ValueError("parts must be a list")
    ids = [part.get("id") for part in parts]
    if any(not isinstance(part_id, str) or not part_id for part_id in ids):
        raise ValueError("every part needs a non-empty string id")
    if len(set(ids)) != len(ids):
        raise ValueError("part ids must be unique")
    connections = diagram.get("connections", [])
    if not isinstance(connections, list):
        raise ValueError("connections must be a list")
    for connection in connections:
        if not isinstance(connection, list) or len(connection) < 2:
            raise ValueError("every connection must name two terminals")
        for terminal in connection[:2]:
            part_id, separator, pin = str(terminal).partition(":")
            if part_id.startswith("$"):
                continue
            if not separator or not pin:
                raise ValueError(f"malformed terminal {terminal!r}")
            if part_id not in ids:
                raise ValueError(f"connection names unknown part {part_id!r}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Schemdraw SVGs and Mermaid schematics from diagram.json."
    )
    parser.add_argument("directory", help="Homework directory (e.g. homeworks/<id>)")
    parser.add_argument("--mermaid", action="store_true", help="Print generated Mermaid flowchart")
    parser.add_argument(
        "--svg", action="store_true", help="Generate IEEE vector schematic SVG via Schemdraw"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate diagram.json and fail when assets/schematic.svg is stale",
    )
    parser.add_argument(
        "--all", action="store_true", help="Generate the SVG and print the Mermaid flowchart"
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

    try:
        validate_diagram(content)
    except ValueError as exc:
        print(f"ERROR: {diagram_path}: {exc}", file=sys.stderr)
        return 1

    if args.svg or args.all:
        svg_path = hw_dir / "assets" / "schematic.svg"
        generate_schematic_svg(content, svg_path)
        print(f"Generated schematic SVG: {svg_path}")

    if args.mermaid or args.all:
        mermaid_text = generate_mermaid_from_diagram(content)
        print(mermaid_text)

    if args.check:
        svg_path = hw_dir / "assets" / "schematic.svg"
        if not svg_path.is_file():
            print(f"ERROR: {svg_path} is missing; run --svg", file=sys.stderr)
            return 1
        if svg_path.read_text(encoding="utf-8") != _render_schematic_svg(content):
            print(f"ERROR: {svg_path} is stale; run --svg", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
