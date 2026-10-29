# Homeworks

A public GitHub monorepo of independent PlatformIO homework projects for an embedded
engineering course. Each homework ships as a self-contained engineering artifact — code,
tests, an academic report, wiring, a bill of materials, engineering calculations, and
labelled evidence — understandable and verifiable a year later.

## What this repository is

A homework here is an artifact, not an exercise dump. It carries its PlatformIO project,
host-testable logic with a native test suite when that logic exists, an academic report in
Markdown, wiring as a diagram and schematic, a bill of materials, engineering
calculations, and evidence labelled by how it was obtained (`measured`, `calculated`,
`simulated`, `datasheet`, `not measured`). The shared libraries under `lib/` and the
metadata contract under `schema/` keep every artifact consistent across assignments.

## Homeworks

<!-- BEGIN GENERATED: homeworks -->

| ID | Project | Board | Framework | Status | Report |
| --- | --- | --- | --- | --- | --- |
| 1_3-police-flasher | [Police Flasher](homeworks/1_3-police-flasher/) | esp32-s3-devkitc-1 | arduino | in-progress | [report](homeworks/1_3-police-flasher/report.md) |
| 1_4-dual-led-button-modes | [Dual LED Modes with External and BOOT Buttons](homeworks/1_4-dual-led-button-modes/) | esp32-s3-devkitc-1 | arduino | planned | [report](homeworks/1_4-dual-led-button-modes/report.md) |
| 1_5-button-bounce | [Button Contact Bounce Analysis with a Logic Analyzer and a Microcontroller](homeworks/1_5-button-bounce/) | esp32-s3-devkitc-1 | arduino | complete | [report](homeworks/1_5-button-bounce/report.md) |

<!-- END GENERATED -->

## Repository map

- `homeworks/<id>/` — one homework project per assignment, created only by
  `scripts/new_homework`.
- `lib/` — the shared libraries `port`, `common`, and `host`, plus the thin Arduino and
  ESP-IDF adapters.
- `scripts/` — deterministic checks, `gen_readme.py`, the `new_homework` scaffold,
  `tag_homework.sh`, `gen_clangd_db.py`, and `scripts/tests/`.
- `schema/` — `homework.schema.json` and `board-profile.schema.json`, the metadata
  contracts.
- `boards/` — one validated board profile per supported board.
- `templates/` — the scaffold source rendered by `scripts/new_homework`.
- `.agents/standards/` — the report, electrical-calculation, and editor standards.
- `.agents/skills/` — the authored workflow skills, symlinked as `.claude/skills`.
- `.planning/` — the GSD roadmap, phase plans, and decision records.
- `.github/workflows/` — `ci.yml`, the pull-request gate, and `nightly.yml`, the scheduled
  full build, native-test matrix, and full-history secret scan.

## Getting started

Prerequisites:

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- PlatformIO Core 6.2.0
- pre-commit 4.7.0
- optional: `wokwi-cli` 0.28.1 for headless simulation

Install the git hooks and run the baseline checks:

```bash
pre-commit install
pio test -d tests -e native
uv run scripts/check_metadata.py
python3 scripts/gen_clangd_db.py --generate
```

The installed hook refuses to commit while `main` is checked out; work on a branch and
open a pull request instead.

The last command builds the root compile database that gives `lib/` working IntelliSense
in the editor.

## Working on a homework

1. Scaffold the project — this is the only supported creation path:

   ```bash
   scripts/new_homework {id} --template {name}
   ```

   The template names are `arduino` and `espidf`.
2. Build it from its own directory:

   ```bash
   pio run -d homeworks/{id}
   ```

3. Run its native suite when the homework has host-testable logic:

   ```bash
   pio test -d homeworks/{id} -e native
   ```

4. Author `report.md` against the structure in `.agents/standards/report.md`.
5. Open a pull request through `.github/pull_request_template.md`.
6. Tag only after the pull request is merged:

   ```bash
   scripts/tag_homework.sh {id}
   ```

## Quality gates

Run these from the repository root before opening a pull request:

| Step | Command | What it proves |
|------|---------|----------------|
| 1 | `pio run -d <project>` | The affected PlatformIO environment builds. |
| 2 | `pio test -d tests -e native` | The shared libraries pass their native suite without a target toolchain. |
| 3 | `pre-commit run --all-files` | Hygiene, secret scan, format, lint, and the metadata and README-index contracts. |
| 4 | `uv run scripts/check_metadata.py` | Homework metadata and provenance satisfy the schema. |
| 5 | `python3 -m unittest discover scripts/tests` | The repository's Python test suite passes. |

CI runs the same surface plus the target builds and exposes one required status check, the
literal `gate` job.

## Repository status

As of 2026-10-29 the shared libraries, the metadata contract, the scaffolding tools, the CI
gate, and the developer tooling are in place. Three homework projects exist: `1_3` is in
progress, `1_4` is planned, and `1_5` is complete. See
[`.planning/ROADMAP.md`](.planning/ROADMAP.md) for the current plan.

## Rules

[`AGENTS.md`](AGENTS.md) is the canonical rulebook for humans and agents alike.
`.claude/CLAUDE.md` imports it rather than duplicating it.

## License

Original code, documentation, and homework reports are released under the MIT license — see
[`LICENSE`](LICENSE).

**Copyright holder:** VLoktiev-EMB.
