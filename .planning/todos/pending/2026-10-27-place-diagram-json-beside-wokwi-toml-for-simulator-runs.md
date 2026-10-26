---
created: 2026-10-26T23:26:31.646Z
title: Place diagram.json beside wokwi.toml for simulator runs
area: tooling
severity: major
files:
  - homeworks/1_3-police-flasher/wokwi.toml:1
  - homeworks/1_3-police-flasher/assets/diagram.json:1
  - homeworks/1_3-police-flasher/README.md:17-45
  - homeworks/1_3-police-flasher/scenario.yaml:1
---

## Problem

`wokwi.toml` lives in `homeworks/1_3-police-flasher/` while `diagram.json` lives one level
down in `assets/`. Wokwi resolves the diagram relative to the project root and defaults to
`diagram.json` **in that root**, so every invocation that does not pass `--diagram-file`
aborts before it opens a connection:

```text
$ WOKWI_CLI_TOKEN=dummy wokwi-cli homeworks/1_3-police-flasher --timeout 2
Error: diagram.json not found in .../homeworks/1_3-police-flasher/diagram.json.
Run `wokwi-cli init` to automatically create a diagram.json file.
```

That is the bare `wokwi-cli <project-dir>` form and, more importantly, the VS Code Wokwi
extension, which looks for `diagram.json` next to `wokwi.toml`. The repository owner
reported being unable to start the simulation; this is the reproduced cause.

Only the documented workaround resolves the paths:

```text
$ WOKWI_CLI_TOKEN=dummy wokwi-cli homeworks/1_3-police-flasher \
    --diagram-file assets/diagram.json --scenario scenario.yaml --timeout 2
...
Error: Error connecting to wss://wokwi.com/api/ws/beta: getaddrinfo ENOTFOUND wokwi.com
```

The run reaches the WebSocket stage, so both option values resolve; the connection error
on that machine is network, not layout. `firmware.merged.bin` (374.5 kB) is present, so the
firmware side of `wokwi.toml` is satisfied and is not part of this defect.

Evidence:
- Wokwi docs, "Wokwi CLI Usage": `--diagram-file <path>` is *"relative to project root
  (default: `diagram.json`)"*; `--scenario` is likewise relative to the project root.
- `wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json` passes, so
  the wiring itself is valid — only the lookup path is wrong.
- Reproduced with wokwi-cli 0.28.1 (`7cf4ffaebfd8`).

## Solution

TBD — candidate shape:

1. Move `assets/diagram.json` to the project root so `wokwi-cli homeworks/<id>` and the
   VS Code extension both work with no flag, then update every reference: the README
   command forms and the `lint` example, and any test or generator that names
   `assets/diagram.json`.
2. Prefer the default over the flag: keep `--diagram-file` in the documentation only as
   the escape hatch, and make the primary documented command flag-free.
3. If the asset must stay under `assets/` for report or BOM reasons, keeping the flag in
   every command is not enough for the extension — a root-level `diagram.json` would be
   required, which duplicates the wiring source of truth. Record the decision before
   choosing this.
4. Settle the layout in the homework template, so new assignments do not inherit the
   split.

Related: `2026-10-25-expand-homework-readme-and-add-a-proper-svg-schematic.md` touches the
same files but is scoped to reader-facing documentation and an SVG schematic, not to the
simulator lookup path.
