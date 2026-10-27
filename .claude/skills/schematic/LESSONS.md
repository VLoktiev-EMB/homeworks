# Lessons

## 2026-10-27 — 3-tier schematic architecture (quick task)

- A single schematic format cannot serve all purposes:
  - Wokwi is ideal for interactive simulation and breadboard bench wiring, but awkward for academic reports.
  - Mermaid is great for quick GitHub browser scanning, but lacks standard electronic circuit symbols.
  - Schemdraw generates publication-quality IEEE/IEC vector schematics (SVG) in milliseconds with zero GUI dependencies.
  - Combining all three provides the best engineering documentation experience without overhead.

## 2026-10-27 — promoted to v1.0, phase 10.1

- Wokwi auto-routing without Manhattan instructions produces spaghetti wiring
  where wires cross through components. Adding explicit `["h...", "v..."]` waypoints
  and zoning inputs on the left and outputs on the right yields clean, professional
  schematics that are easily readable in the simulator.

## 2026-10-26 — initial stub, phase 9

- The phase 9 planning run kept `schematic` a stub because the wiring is still
  edited by hand in the Wokwi diagram editor. The rule it implies: a wiring
  change belongs in the report's wiring table in the same change, and a
  simulation never becomes bench evidence.
