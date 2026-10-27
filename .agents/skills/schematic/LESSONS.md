<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->
# Lessons

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
