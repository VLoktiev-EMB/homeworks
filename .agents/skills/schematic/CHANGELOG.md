<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->
# Changelog

## 2026-10-27 — updated to v1.1, SDO and writing-skills compliance

- Updated description to trigger-first SDO format ("Use when...").
- Added Overview, When to Use / When NOT to Use, Quick Reference, and Common Mistakes & Red Flags.
- Added comprehensive unit tests in `scripts/tests/test_gen_schematic.py`.

## 2026-10-27 — promoted to v1.0, phase 10.1

- Promoted `schematic` from stub to active skill.
- Added `scripts/gen_schematic.py` for automated Wokwi layout, Manhattan routing,
  and Mermaid diagram generation.
- Established clean layout rules (board center, inputs left, outputs right, >=80px spacing,
  wire color coding).

## 2026-10-26 — initial stub, phase 9

- Added the `schematic` stub contract during the phase 9 planning run: the skill
  is a placeholder for editing the Wokwi diagram, and it names the diagram
  editor and the offline lint command as the manual fallback.
