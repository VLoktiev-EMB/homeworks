"""Universal vector schematic generation from a Wokwi `diagram.json`.

The renderer is diagram-driven: it never names a homework, a pin, or a part.
It builds the electrical net graph from `parts` and `connections`, then chooses
one of two layouts.

* Branch layout — every external part has exactly two terminals, every signal
  net carries exactly one branch, and the net graph is a forest rooted at the
  MCU signal pins. Branches are drawn as real wires, series components,
  junctions, ground, and power symbols. This is the readable layout for a
  single chain such as an LED with a series resistor.
* Row layout — every two-terminal chain between two anchor nets (an MCU pin,
  power, or ground) becomes one horizontal row. A shared pin yields one row per
  branch and matching net labels carry the connectivity, so two branches never
  fight for the same space. Internal series nets are drawn directly and are
  never invented as `N` labels.
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
        return f"{component.ref} {value} Ω" if value else component.ref
    if "led" in kind:
        color = attrs.get("color")
        return f"{component.ref} ({color})" if color else component.ref
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

    # Every signal net must belong to exactly one MCU pin and exactly one
    # external branch. A shared pin is a junction in the physical circuit but a
    # fork in the drawing; the branch layout has no room for a second branch
    # and would overlap its labels, so the row layout owns that case.
    for _, net in signal_nets:
        if len(net["mcu_pins"]) != 1:
            raise _FallbackNeeded(f"net {net['label']} is shared by several MCU pins")

    for net_id, net in signal_nets:
        if len(model.incident.get(net_id, [])) != 1:
            raise _FallbackNeeded(f"net {net['label']} has several branches")

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


_PATH_RANK = {"power": 0, "signal": 1, "ground": 2}


def _is_anchor_net(model: _Model, net_id: str) -> bool:
    """A net is an anchor when it ends a chain: an MCU pin, power, or ground."""
    net = model.nets[net_id]
    return net["kind"] in ("power", "ground") or bool(net["mcu_pins"])


def _extract_paths(model: _Model) -> list[dict]:
    """Split the two-terminal graph into simple chains between anchor nets.

    Each component is an edge between two nets. A chain starts at an anchor and
    follows internal degree-two nets until it reaches another anchor. A shared
    anchor, such as one GPIO driving two branches, naturally yields one chain
    per branch instead of a fork with overlapping wires.
    """
    adjacency: dict[str, list[tuple[_Component, str, str, str]]] = defaultdict(list)
    for component in model.components:
        if len(component.pins) != 2:
            raise _FallbackNeeded(f"component {component.ref} is not two-terminal")
        (pin_a, net_a), (pin_b, net_b) = component.pins
        if net_a == net_b:
            raise _FallbackNeeded(f"component {component.ref} shorts one net")
        adjacency[net_a].append((component, pin_a, pin_b, net_b))
        adjacency[net_b].append((component, pin_b, pin_a, net_a))

    used: set[str] = set()
    paths: list[dict] = []
    anchors = sorted(
        (net_id for net_id in model.nets if _is_anchor_net(model, net_id)),
        key=lambda net_id: (model.nets[net_id]["label"], net_id),
    )

    for anchor in anchors:
        for component, pin_from, pin_to, next_net in sorted(
            adjacency.get(anchor, []), key=lambda item: item[0].ref
        ):
            if component.ref in used:
                continue
            used.add(component.ref)
            edges = [(component, pin_from, pin_to, anchor, next_net)]
            current_net = next_net
            while not _is_anchor_net(model, current_net):
                candidates = [
                    entry for entry in adjacency.get(current_net, []) if entry[0].ref not in used
                ]
                if len(adjacency.get(current_net, [])) != 2 or len(candidates) != 1:
                    raise _FallbackNeeded(f"internal net {current_net} does not form a chain")
                component, pin_from, pin_to, next_net = candidates[0]
                used.add(component.ref)
                edges.append((component, pin_from, pin_to, current_net, next_net))
                current_net = next_net
            paths.append({"start": anchor, "end": current_net, "edges": edges})

    if len(used) != len(model.components):
        missing = sorted({component.ref for component in model.components} - used)
        raise _FallbackNeeded(f"unresolved components: {', '.join(missing)}")

    # Draw power-first chains at the top and ground-last chains below, so the
    # page reads from the positive rail down to ground.
    normalized = []
    for path in paths:
        start, end = path["start"], path["end"]
        if _PATH_RANK[model.nets[start]["kind"]] > _PATH_RANK[model.nets[end]["kind"]]:
            edges = [
                (component, pin_to, pin_from, net_to, net_from)
                for component, pin_from, pin_to, net_from, net_to in reversed(path["edges"])
            ]
            normalized.append({"start": end, "end": start, "edges": edges})
        else:
            normalized.append(path)

    return sorted(
        normalized,
        key=lambda path: (
            _PATH_RANK[model.nets[path["start"]]["kind"]],
            model.nets[path["start"]]["label"],
            _PATH_RANK[model.nets[path["end"]]["kind"]],
            model.nets[path["end"]]["label"],
            path["edges"][0][0].ref,
        ),
    )


def _draw_path_endpoint(d, model: _Model, net_id: str, point, elm, left: bool):
    """Draw a rail symbol or a net-label stub at one end of a chain."""
    net = model.nets[net_id]
    x, y = point

    if net["kind"] == "power":
        d.add(elm.Line().at((x, y)).up(0.9))
        d.add(elm.Vdd().at(d.here).label(net["label"], loc="top", fontsize=8))
        if left:
            d.add(elm.Line().at((x, y)).right(0.5))
            return (x + 0.5, y)
        return point

    if net["kind"] == "ground":
        d.add(elm.Line().at((x, y)).down(0.9))
        # The ground symbol is standard and unambiguous; a second text label
        # only crowds the bars.
        d.add(elm.Ground().at(d.here))
        if left:
            d.add(elm.Line().at((x, y)).right(0.5))
            return (x + 0.5, y)
        return point

    d.add(elm.Line().at((x, y)).right(0.5))
    if left:
        d.add(elm.Label().at((x + 0.25, y)).label(net["label"], loc="top", fontsize=8))
    else:
        d.add(elm.Label().at((x + 0.5, y)).label(net["label"], loc="right", fontsize=8))
    return (x + 0.5, y)


def _draw_mcu_block(d, model: _Model, path_count: int, elm) -> None:
    """Draw one labelled MCU block; matching net labels carry connectivity."""
    anchor_nets = sorted(
        ((net_id, net) for net_id, net in model.nets.items() if _is_anchor_net(model, net_id)),
        key=lambda item: (_PATH_RANK[item[1]["kind"]], item[1]["label"]),
    )
    if not anchor_nets:
        return

    # Schemdraw places slot 1 at the bottom; reverse the list so the page reads
    # power, signals, ground from top to bottom.
    pins = [
        elm.IcPin(
            name=net["label"].replace(" ", "_"),
            side="right",
            slot=f"{index + 1}/{len(anchor_nets) + 1}",
        )
        for index, (_, net) in enumerate(reversed(anchor_nets))
    ]
    height = max(3.5, 1.6 * len(anchor_nets) + 1.5)
    top = -((path_count - 1) * 4.0) / 2
    ic = d.add(
        elm.Ic(size=(6.2, height), pins=pins)
        .at((-10.0, top))
        .label("ESP32-S3\nDevKitC-1", loc="center", fontsize=11)
    )
    for _, net in anchor_nets:
        anchor = net["label"].replace(" ", "_")
        d.add(elm.Line().at(ic[anchor]).right(1.0))
        d.add(elm.Label().at(d.here).label(net["label"], loc="right", fontsize=8))


def _draw_paths(model: _Model, d, elm) -> None:
    """Row-per-chain layout for shared pins and other non-forest nets.

    Every chain is drawn as a left-to-right series of real symbols. Its ends
    carry a power symbol, a ground symbol, or a net label, and the MCU block
    repeats the same net labels. No internal net label is invented, so a reader
    sees exactly the nets the wiring declares.
    """
    paths = _extract_paths(model)
    if not paths:
        raise _FallbackNeeded("no chains to draw")

    # Draw the MCU block before the chains: an Ic element inherits the current
    # drawing direction, and a chain that ended on a vertical rail would
    # otherwise rotate the block's pin side.
    _draw_mcu_block(d, model, len(paths), elm)

    for index, path in enumerate(paths):
        y = -index * 4.0
        point = _draw_path_endpoint(d, model, path["start"], (0.0, y), elm, left=True)
        for component, pin_from, pin_to, _net_from, _net_to in path["edges"]:
            x, current_y = point
            d.add(elm.Line().at((x, current_y)).right(0.5))
            x += 0.5
            element = _element_for(component, "right", elm)
            if pin_from == "C" and pin_to == "A":
                element = element.reverse()
            attrs = model.parts.get(component.ref, {}).get("attrs", {})
            d.add(
                element.at((x, current_y)).label(
                    _component_display(component, attrs), loc="top", fontsize=8
                )
            )
            x += 1.8
            point = (x, current_y)
        _draw_path_endpoint(d, model, path["end"], point, elm, left=False)


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
        try:
            svg = _render(model, _draw_paths, schemdraw, elm)
        except _FallbackNeeded:
            svg = _render(model, _draw_net_labels, schemdraw, elm)
    return _with_card_background(svg)


def generate_schematic_svg(diagram: dict, output_path) -> object:
    """Render `diagram` and write the SVG to `output_path`."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_schematic_svg(diagram), encoding="utf-8")
    return output_path
