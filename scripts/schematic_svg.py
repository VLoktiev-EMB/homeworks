"""Universal vector schematic generation from a Wokwi `diagram.json`.

The renderer is diagram-driven: it never names a homework, a pin, or a part.
It builds the electrical net graph from `parts` and `connections`, then chooses
one of two layouts.

* Branch layout — every external part has exactly two terminals and the net
  graph is a forest rooted at the MCU signal pins. Branches are drawn as real
  wires, series components, junctions, ground, and power symbols. This is the
  readable layout for discrete circuits such as an LED with a series resistor.
* Net-label layout — the universal fallback. Every pin of every part, including
  the MCU, ends in a short stub labelled with its net name. Connectivity is
  expressed by matching labels, which is a standard schematic technique and
  works for any number of pins, cyclic nets, multi-pin ICs, and unknown part
  types.

The output always carries a solid white card rectangle so the drawing stays
legible in a dark theme.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field

# Rail words are matched case-insensitively inside an MCU pin name.
_GROUND_WORDS = ("GND", "VSS", "0V")
_POWER_WORDS = ("3V3", "3.3V", "5V", "VCC", "VDD", "VIN", "VBUS")


class _FallbackNeeded(Exception):
    """The branch layout cannot represent this diagram; use net labels."""


class _UnionFind:
    def __init__(self) -> None:
        self._parent: dict[str, str] = {}

    def find(self, item: str) -> str:
        self._parent.setdefault(item, item)
        root = item
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[item] != root:
            parent = self._parent[item]
            self._parent[item] = root
            item = parent
        return root

    def union(self, left: str, right: str) -> None:
        left_root, right_root = self.find(left), self.find(right)
        if left_root != right_root:
            self._parent[right_root] = left_root


@dataclass
class _Component:
    ref: str
    part_type: str
    pins: list[tuple[str, str]] = field(default_factory=list)

    @property
    def net_ids(self) -> list[str]:
        return [net for _, net in self.pins]

    def other_net(self, net_id: str) -> str:
        for _, net in self.pins:
            if net != net_id:
                return net
        raise _FallbackNeeded(f"component {self.ref} has no second net")


@dataclass
class _Model:
    mcu_id: str | None
    parts: dict[str, dict]
    nets: dict[str, dict]
    components: list[_Component]
    incident: dict[str, list[_Component]]


def _split_terminal(term: str) -> tuple[str, str]:
    part, _, pin = term.partition(":")
    return part, pin


def _normalize_terminal(term: str, mcu_id: str | None) -> str:
    """Collapse the terminals that are electrically one node.

    Ground and power pins of the MCU merge into single nets, so a part wired to
    `GND.1` and another wired to `GND.2` share one ground. Breadboard row pins
    lose their letter suffix so `5t.a` and `5t.b` share the row net.
    """
    part, pin = _split_terminal(term)
    if part.startswith("$"):
        return term
    if mcu_id is not None and part == mcu_id:
        upper = pin.upper()
        if any(word in upper for word in _GROUND_WORDS):
            return f"{mcu_id}:GND"
        if "5V" in upper or "VIN" in upper or "VBUS" in upper:
            return f"{mcu_id}:5V"
        if any(word in upper for word in _POWER_WORDS):
            return f"{mcu_id}:3V3"
        return term
    if part.lower().startswith("bb"):
        prefix = pin.split(".")[0] if "." in pin else pin
        return f"{part}:{prefix}"
    return term


def _prettify_pin(pin: str) -> str:
    upper = pin.upper()
    if any(word in upper for word in _GROUND_WORDS):
        return "GND"
    if "3V3" in upper or "3.3V" in upper:
        return "3V3"
    if "5V" in upper or "VIN" in upper or "VBUS" in upper:
        return "5V"
    if any(word in upper for word in _POWER_WORDS):
        return pin
    if pin.isdigit():
        return f"GPIO{pin}"
    return pin


def _build_model(diagram: dict) -> _Model:
    parts = {part["id"]: part for part in diagram.get("parts", []) if "id" in part}
    mcu = next((part for part in parts.values() if "board" in str(part.get("type", ""))), None)
    mcu_id = mcu["id"] if mcu else None

    union = _UnionFind()
    terminals: set[str] = set()
    for connection in diagram.get("connections", []):
        if len(connection) < 2:
            continue
        left, right = connection[0], connection[1]
        if "$serialMonitor" in left or "$serialMonitor" in right:
            continue
        left_net = _normalize_terminal(left, mcu_id)
        right_net = _normalize_terminal(right, mcu_id)
        union.union(left_net, right_net)
        terminals.update((left_net, right_net))
    for terminal in terminals:
        union.find(terminal)

    grouped: dict[str, list[str]] = defaultdict(list)
    for terminal in terminals:
        grouped[union.find(terminal)].append(terminal)

    nets: dict[str, dict] = {}
    for index, (root, members) in enumerate(sorted(grouped.items())):
        mcu_pins = [
            pin
            for terminal in members
            for part, pin in [_split_terminal(terminal)]
            if part == mcu_id
        ]
        if mcu_pins:
            joined = " ".join(mcu_pins).upper()
            if any(word in joined for word in _GROUND_WORDS):
                kind, label = "ground", "GND"
            elif any(word in joined for word in _POWER_WORDS):
                kind, label = "power", _prettify_pin(mcu_pins[0])
            else:
                kind, label = "signal", _prettify_pin(mcu_pins[0])
        else:
            kind, label = "internal", f"N{index + 1}"
        nets[root] = {"label": label, "kind": kind, "mcu_pins": mcu_pins}

    components: list[_Component] = []
    for ref, part in parts.items():
        if ref == mcu_id or ref.startswith("$"):
            continue
        pins: dict[str, str] = {}
        for connection in diagram.get("connections", []):
            for terminal in connection[:2]:
                term_part, pin = _split_terminal(terminal)
                if term_part != ref:
                    continue
                pins[pin] = union.find(_normalize_terminal(terminal, mcu_id))
        components.append(_Component(ref, str(part.get("type", "")), sorted(pins.items())))

    incident: dict[str, list[_Component]] = defaultdict(list)
    for component in components:
        for net_id in dict.fromkeys(component.net_ids):
            incident[net_id].append(component)

    return _Model(mcu_id, parts, nets, components, incident)


def _is_button(component: _Component) -> bool:
    kind = component.part_type.lower()
    return "button" in kind or "switch" in kind


def _component_display(component: _Component, attrs: dict) -> str:
    kind = component.part_type.lower()
    if "resistor" in kind:
        value = attrs.get("value")
        return f"{component.ref} {value}Ω" if value else component.ref
    if "led" in kind:
        return f"{component.ref} {attrs.get('color', 'LED')} LED"
    if "pushbutton" in kind or "button" in kind:
        return f"{component.ref} {attrs.get('label', 'BTN')}"
    if "capacitor" in kind:
        return f"{component.ref} {attrs.get('value', 'C')}"
    if "inductor" in kind:
        return f"{component.ref} {attrs.get('value', 'L')}"
    return component.ref


def _element_for(component: _Component, direction: str, elm) -> object:
    kind = component.part_type.lower()
    if "resistor" in kind:
        element = elm.Resistor()
    elif "led" in kind:
        element = elm.LED()
    elif "diode" in kind:
        element = elm.Diode()
    elif "capacitor" in kind:
        element = elm.Capacitor()
    elif "pushbutton" in kind or "button" in kind:
        element = elm.Button()
    elif "switch" in kind:
        element = elm.Switch()
    elif "inductor" in kind:
        element = elm.Inductor()
    else:
        element = elm.RBox()
    getattr(element, direction)(1.8)
    if direction == "up" and ("led" in kind or "diode" in kind):
        element.reverse()
    return element


def _preferred_direction(net_kind: str, parent_direction: str) -> str:
    if net_kind == "ground":
        return "down"
    if net_kind == "power":
        return "up"
    return parent_direction


def _place_terminal(d, elm, kind: str, point, direction: str, label: str = "3V3") -> None:
    if direction in ("left", "right"):
        turn = "down" if kind == "ground" else "up"
        d.add(elm.Line().at(point).__getattribute__(turn)(0.8))
        point = d.here
    symbol = elm.Ground() if kind == "ground" else elm.Vdd()
    symbol = symbol.at(point)
    if kind == "ground":
        d.add(symbol)
    else:
        d.add(symbol.label(label, loc="top", fontsize=8))


def _label_location(direction: str) -> str:
    """Horizontal elements label above; vertical ones label beside the body."""
    return "top" if direction in ("left", "right") else "bottom"


def _draw_net(d, model: _Model, net_id: str, point, direction: str, came_from: str | None,
              placed: set[str], seen: set[str], elm) -> None:
    net = model.nets[net_id]
    if net["kind"] in ("ground", "power"):
        _place_terminal(d, elm, net["kind"], point, direction, net["label"])
        return
    if net_id in seen:
        d.add(elm.Dot(open=True).at(point))
        d.add(elm.Label().at(point).label(net["label"], fontsize=8))
        return
    seen.add(net_id)

    edges = [
        component
        for component in model.incident.get(net_id, [])
        if component.ref != came_from and component.ref not in placed
    ]
    if not edges:
        d.add(elm.Dot(open=True).at(point))
        d.add(elm.Label().at(point).label(net["label"], fontsize=8))
        return
    if len(edges) == 1:
        component = edges[0]
        other = component.other_net(net_id)
        child_direction = _preferred_direction(model.nets[other]["kind"], direction)
        element = _element_for(component, child_direction, elm)
        attrs = model.parts.get(component.ref, {}).get("attrs", {})
        d.add(element.at(point).label(_component_display(component, attrs),
                                      loc=_label_location(child_direction), fontsize=8))
        placed.add(component.ref)
        _draw_net(d, model, other, d.here, child_direction, component.ref, placed, seen, elm)
        return

    # A junction: one child continues in the parent direction, the others turn.
    d.add(elm.Dot().at(point))
    slots: dict[str, int] = defaultdict(int)
    for component in edges:
        other = component.other_net(net_id)
        preferred = _preferred_direction(model.nets[other]["kind"], direction)
        offset = slots[preferred]
        slots[preferred] += 1
        start = point
        if offset:
            delta = 0.9 * offset
            if preferred in ("up", "down"):
                start = (point[0] + delta, point[1])
            else:
                start = (point[0], point[1] - delta)
            d.add(elm.Line().at(point).to(start))
        attrs = model.parts.get(component.ref, {}).get("attrs", {})
        element = _element_for(component, preferred, elm)
        d.add(element.at(start).label(_component_display(component, attrs),
                                      loc=_label_location(preferred), fontsize=8))
        placed.add(component.ref)
        _draw_net(d, model, other, d.here, preferred, component.ref, placed, seen, elm)


def _draw_branches(model: _Model, d, elm) -> None:
    for component in model.components:
        if len(component.pins) != 2 or len(set(component.net_ids)) != 2:
            raise _FallbackNeeded(f"component {component.ref} is not two-terminal")

    signal_nets = [
        (net_id, net) for net_id, net in model.nets.items() if net["kind"] == "signal"
    ]
    if not signal_nets:
        raise _FallbackNeeded("no MCU signal net")

    # Every signal net must belong to exactly one MCU pin; a shared signal net
    # would be drawn twice.
    for _, net in signal_nets:
        if len(net["mcu_pins"]) != 1:
            raise _FallbackNeeded(f"net {net['label']} is shared by several MCU pins")

    left = []
    right = []
    for net_id, net in sorted(signal_nets, key=lambda item: item[1]["label"]):
        adjacent = model.incident.get(net_id, [])
        first = adjacent[0] if adjacent else None
        (left if first is not None and _is_button(first) else right).append((net_id, net))

    pins = []
    layout: dict[str, tuple[str, str]] = {}
    for side, group in (("left", left), ("right", right)):
        for index, (net_id, net) in enumerate(group):
            anchor = net["label"].replace(" ", "_")
            pins.append(elm.IcPin(name=anchor, side=side, slot=f"{index + 1}/{len(group) + 1}"))
            layout[net_id] = (side, anchor)

    if not pins:
        raise _FallbackNeeded("no MCU pins to draw")

    # Generous pin pitch: a branch that turns upward at a junction needs room
    # for a component plus a rail symbol before the next pin row.
    height = max(8.0, 4.5 * max(len(left), len(right)) + 2.0)
    ic = d.add(
        elm.Ic(size=(6.2, height), pins=pins).label(
            "ESP32-S3\nDevKitC-1", loc="center", fontsize=11
        )
    )

    # Route every signal from its pin into its own vertical lane. The upper
    # branch takes the outer lane, so its vertical drop runs beyond every lower
    # branch's horizontal run and no wire crosses another.
    placed: set[str] = set()
    for side, group in (("left", left), ("right", right)):
        if not group:
            continue
        ordered = sorted(
            ((net_id, net, layout[net_id][1], ic[layout[net_id][1]]) for net_id, net in group),
            key=lambda item: item[3][1],
            reverse=True,
        )
        sign = 1.0 if side == "right" else -1.0
        for rank, (net_id, _net, _anchor, point) in enumerate(ordered):
            lane = 1.2 + (len(ordered) - 1 - rank) * 1.0
            d.add(elm.Line().at(point).to((point[0] + sign * lane, point[1])))
            _draw_net(d, model, net_id, d.here, side, None, placed, set(), elm)

    if len(placed) != len(model.components):
        missing = sorted({component.ref for component in model.components} - placed)
        raise _FallbackNeeded(f"unplaced components: {', '.join(missing)}")


def _draw_net_labels(model: _Model, d, elm) -> None:
    mcu_nets = [(net_id, net) for net_id, net in model.nets.items() if net["mcu_pins"]]
    if mcu_nets:
        pins = []
        layout: dict[str, str] = {}
        for index, (net_id, net) in enumerate(sorted(mcu_nets, key=lambda item: item[1]["label"])):
            anchor = net["label"].replace(" ", "_")
            pins.append(
                elm.IcPin(name=anchor, side="right", slot=f"{index + 1}/{len(mcu_nets) + 1}")
            )
            layout[net_id] = anchor
        ic = d.add(
            elm.Ic(size=(6.2, max(3.5, 1.6 * len(mcu_nets) + 1.5)), pins=pins).label(
                "ESP32-S3\nDevKitC-1", loc="center", fontsize=11
            )
        )
        for net_id, net in sorted(mcu_nets, key=lambda item: item[1]["label"]):
            d.add(elm.Line().right(1.0).at(ic[layout[net_id]]))
            d.add(elm.Label().at(d.here).label(net["label"], fontsize=8))

    # Each external part is drawn as a symbol or a box with one labelled stub
    # per net. Matching labels carry the connectivity.
    for component in model.components:
        nets = list(dict.fromkeys(net_id for _, net_id in component.pins))
        if not nets:
            d.add(elm.RBox().label(component.ref, fontsize=8))
            continue
        pins = []
        anchors = []
        for index, net_id in enumerate(nets):
            anchor = f"p{index}"
            pins.append(elm.IcPin(name=anchor, side="right", slot=f"{index + 1}/{len(nets) + 1}"))
            anchors.append((net_id, anchor))
        attrs = model.parts.get(component.ref, {}).get("attrs", {})
        box = d.add(
            elm.Ic(size=(2.2, max(1.5, 0.7 * len(nets) + 0.8)), pins=pins).label(
                _component_display(component, attrs), loc="center", fontsize=8
            )
        )
        for net_id, anchor in anchors:
            d.add(elm.Line().right(0.8).at(box[anchor]))
            d.add(elm.Label().at(d.here).label(model.nets[net_id]["label"], fontsize=7))


def _render(model: _Model, builder, schemdraw, elm) -> str:
    with schemdraw.Drawing(show=False) as drawing:
        drawing.config(unit=2.0, fontsize=10, margin=3.0, bgcolor="white")
        builder(model, drawing, elm)
        return drawing.get_imagedata("svg").decode("utf-8")


def _with_card_background(svg: str) -> str:
    match = re.search(r'viewBox="([^"]+)"', svg)
    if not match:
        return svg if svg.endswith("\n") else svg + "\n"
    view_x, view_y, view_width, view_height = (float(value) for value in match.group(1).split())
    # Matplotlib sizes the viewBox from the drawn elements, while a label
    # attached to a terminal can extend past it. Widening the viewBox keeps
    # those labels visible instead of clipping them at the right edge.
    pad_x = view_width * 0.18
    pad_y = view_height * 0.08
    widened = (
        f'viewBox="{view_x - pad_x} {view_y - pad_y} '
        f'{view_width + 2 * pad_x} {view_height + 2 * pad_y}"'
    )
    svg = svg.replace(match.group(0), widened, 1)
    rect = (
        f'<rect x="{view_x - pad_x}" y="{view_y - pad_y}" '
        f'width="{view_width + 2 * pad_x}" height="{view_height + 2 * pad_y}" '
        'fill="#ffffff" rx="8"/>'
    )
    svg = re.sub(r"(<svg[^>]*>)", r"\1" + rect, svg, count=1)
    if not svg.endswith("\n"):
        svg += "\n"
    return svg


def render_schematic_svg(diagram: dict) -> str:
    """Return the SVG document for `diagram`, choosing a layout automatically."""
    try:
        import schemdraw
        import schemdraw.elements as elm
    except ImportError as exc:  # pragma: no cover - exercised through uv run
        raise RuntimeError(
            "schemdraw is required to generate vector SVGs. Run via uv run."
        ) from exc

    model = _build_model(diagram)
    try:
        svg = _render(model, _draw_branches, schemdraw, elm)
    except _FallbackNeeded:
        svg = _render(model, _draw_net_labels, schemdraw, elm)
    return _with_card_background(svg)


def generate_schematic_svg(diagram: dict, output_path) -> object:
    """Render `diagram` and write the SVG to `output_path`."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_schematic_svg(diagram), encoding="utf-8")
    return output_path
