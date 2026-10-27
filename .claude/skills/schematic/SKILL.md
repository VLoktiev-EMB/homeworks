---
name: schematic
description: Placeholder for editing the Wokwi project diagram until this skill is promoted. Use only to look up the manual diagram-editor and lint fallback.
disable-model-invocation: true
metadata:
  version: "0.1"
  status: stub
---

# Schematic (stub)

> **Stub (v0.1).** This skill does not open or edit `assets/diagram.json`,
> validate part placement, or update the pin map. Until it is promoted, edit the
> diagram in the Wokwi diagram editor, keep the file under
> `homeworks/<id>/assets/diagram.json`, and lint it with
> `wokwi-cli lint --offline homeworks/<id>/assets/diagram.json`. A wiring change
> must be reflected in the report's wiring table, and simulation is never bench
> evidence.

## Manual fallback

1. Edit the diagram in the Wokwi diagram editor.
2. Keep the result at `homeworks/<id>/assets/diagram.json`.
3. Lint it offline with
   `wokwi-cli lint --offline homeworks/<id>/assets/diagram.json`.
4. Update the report's wiring table in the same change.
