# Phase 4: Metadata Contract and Scaffolding - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-24
**Phase:** 4-Metadata Contract and Scaffolding
**Areas discussed:** Schema shape, Validator and enforcement, `new_homework` behaviour,
Template depth and build, `task.md` provenance, Environment names, `AGENTS.md` and layout,
Optional block subschemas, Checker contract, Board profile, Output format, Tooling tests,
Phase 5 contract, Template extensibility, Required block subschemas

---

## Schema shape

| Option | Description | Selected |
|--------|-------------|----------|
| Minimum + optional blocks | Required identity/build fields; optional typed blocks | ✓ |
| Everything required | All eleven domains mandatory from day one | |
| Minimal contract | Only id, title, board, framework, status, source | |

**User's choice:** Minimum + optional blocks.
**Notes:** Chosen to avoid speculative field design while still recording every domain
META-01 names.

| Option | Description | Selected |
|--------|-------------|----------|
| Derive from id | `module`, `lesson`, `slug` computed from `id` | ✓ |
| Separate fields | Store them beside `id` and validate agreement | |

**User's choice:** Derive from id.

| Option | Description | Selected |
|--------|-------------|----------|
| Integer + enum | `schema_version: 1`; status enum | ✓ |
| Semver + free text | Semver string; status as free text | |
| Version in filename | No field; version in the schema filename | |

**User's choice:** Integer + enum.

---

## Validator and enforcement

| Option | Description | Selected |
|--------|-------------|----------|
| requirements + pre-commit venv | Pinned `requirements-dev.txt` plus a hook environment | |
| pre-commit env only | Versions only in `additional_dependencies` | |
| system + manual install | `language: system` with manual installation | |

**User's choice (free text):** dependencies handled only through `uv`, with pre-commit
separate. Follow-up clarification selected the hybrid below.
**Notes:** After a plain-text follow-up the user chose two independent environments:
PEP 723 inline metadata with `uv run` for manual script runs, and a `language: python`
pre-commit hook with `additional_dependencies` so pre-commit builds its own venv. The user
asked whether this was the best approach; the answer is recorded in CONTEXT.md, including
the stdlib-only drift test that keeps the two declarations equal.

| Option | Description | Selected |
|--------|-------------|----------|
| schema/ + checker | Schema at `schema/`, checker in `scripts/` | ✓ |
| templates/ + scaffold only | Schema beside templates; no repository checker | |
| docs/standards + scripts | Published prose contract plus machine schema | |

**User's choice:** schema/ + checker.

| Option | Description | Selected |
|--------|-------------|----------|
| Strict everywhere | `additionalProperties: false` at every level | ✓ |
| Strict top-level only | Nested blocks open to extension | |
| unevaluatedProperties | Use the 2020-12 composition keyword | |

**User's choice:** Strict everywhere.

---

## `new_homework` behaviour

| Option | Description | Selected |
|--------|-------------|----------|
| ID + --template | Positional id, required template flag | ✓ |
| ID + --framework | Framework flag selects the template | |
| Interactive mode | Guided prompts with recommended answers | |

**User's choice:** ID + --template.
**Notes:** Interactive guided mode is Phase 9 (FLOW-02/03), not this phase.

| Option | Description | Selected |
|--------|-------------|----------|
| Hash + all-or-nothing | Identical content is a no-op; other content is a conflict with zero writes | ✓ |
| Any existing path = error | Even identical content fails | |
| Allow --force | Explicit overwrite of conflicting files | |

**User's choice:** Hash + all-or-nothing.

| Option | Description | Selected |
|--------|-------------|----------|
| Per-path plan | CREATE / UNCHANGED / CONFLICT with exit 0/1 | ✓ |
| Plan + content | Also print rendered file contents | |
| File list only | Names only, no statuses | |

**User's choice:** Per-path plan.

| Option | Description | Selected |
|--------|-------------|----------|
| No build | Scaffold only writes files | ✓ |
| Optional --build | Run `pio run` on request | |
| Always build | Run `pio run` after every scaffold | |

**User's choice:** No build.

---

## Template depth and build

| Option | Description | Selected |
|--------|-------------|----------|
| Through port + adapter | Starter code blinks through `lib/port` and the matching adapter | ✓ |
| Framework API directly | Blink with `digitalWrite` / `gpio_set_level` | |
| Empty entry | Empty `setup`/`loop` and `app_main` | |

**User's choice:** Through port + adapter.
**Notes:** Chosen to discharge the Phase 3 carry-forward with real target compilation.

| Option | Description | Selected |
|--------|-------------|----------|
| Unity + native env | Real Unity test and `[env:native]` | ✓ |
| Placeholder | A test file with no framework | |
| Empty | `.gitkeep` only | |

**User's choice:** Unity + native env.

| Option | Description | Selected |
|--------|-------------|----------|
| Task skeleton + short README | Full `task.md` skeleton, short README, report template only in `templates/` | ✓ |
| Full report skeleton | Ten-section report scaffold in README | |
| Minimal stubs | Empty README, heading-only `task.md` | |

**User's choice:** Task skeleton + short README.

| Option | Description | Selected |
|--------|-------------|----------|
| Directories + {{...}} | One directory per template; `{{name}}` placeholders; ADR template moves | ✓ |
| Flat files | Flat template files | |
| Jinja template | One conditional Jinja template | |

**User's choice:** Directories + {{...}}.

---

## `task.md` provenance

| Option | Description | Selected |
|--------|-------------|----------|
| Canon in task.md | Frontmatter plus body; `homework.yaml` cross-checked | ✓ |
| Canon in homework.yaml | `task.md` links to YAML | |
| Duplicate both | No consistency check | |

**User's choice:** Canon in task.md.

| Option | Description | Selected |
|--------|-------------|----------|
| Fields + language check | Fields, formats, and a Cyrillic ban with an allowlist | ✓ |
| Fields only | Structure and formats; content reviewed by a human | |
| Fields + markers | Fields plus TODO/FIXME/internal markers | |

**User's choice:** Fields + language check.

---

## Environment names

| Option | Description | Selected |
|--------|-------------|----------|
| esp32s3_* + native | `esp32s3_arduino` / `esp32s3_espidf` plus `native` | ✓ |
| Short names | `arduino` / `espidf` plus `native` | |
| hw_<id>_* | Per-homework unique names | |

**User's choice:** esp32s3_* + native.

| Option | Description | Selected |
|--------|-------------|----------|
| Target env only | `default_envs` names the firmware environment | ✓ |
| Target + native | `pio run` also builds the test environment | |
| No default_envs | Build every declared environment | |

**User's choice:** Target env only.

---

## `AGENTS.md` and layout

| Option | Description | Selected |
|--------|-------------|----------|
| Full update | Layout, quick-start, routing table, hook list | ✓ |
| Layout + routing | Skip the quick-start step | |
| Do not touch | Rulebook diverges from the tree | |

**User's choice:** Full update.

| Option | Description | Selected |
|--------|-------------|----------|
| Two ADRs | 0009 metadata contract, 0010 dependency policy | ✓ |
| One ADR | A single combined record | |
| No ADR | CONTEXT.md only | |

**User's choice:** Two ADRs.

| Option | Description | Selected |
|--------|-------------|----------|
| By extension | `templates/**/*.md` CC-BY-4.0; ini/json and `schema/**` MIT | ✓ |
| Do not touch | Everything new under the MIT catch-all | |
| Whole templates/ | All templates CC-BY-4.0 | |

**User's choice:** By extension.

---

## Optional block subschemas

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit minimal subschemas | Typed fields for simulation, tests, report, assets | ✓ |
| Free-form details | One open object | |
| Report only | Only `report` typed now | |

**User's choice:** Explicit minimal subschemas.

---

## Checker contract

| Option | Description | Selected |
|--------|-------------|----------|
| Scan all + exit 0/1/2 | All `homeworks/*/`, optional paths, `--json`, no `--check` | ✓ |
| Require --check | Mandatory flag, no JSON output | |
| JSON only | Machine output only | |

**User's choice:** Scan all + exit 0/1/2.

---

## Board profile

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal profile | Id, MCU, flash, PSRAM, frameworks, pinout URL | ✓ |
| Full pin map | GPIO-to-function mapping | |
| Link only | Official documentation link, no fields | |

**User's choice:** Minimal profile.
**Notes:** A full pin map is explicitly out of scope in `REQUIREMENTS.md`.

---

## Output format

| Option | Description | Selected |
|--------|-------------|----------|
| Stable record | `PATH: STATUS — reason` with a fixed vocabulary | ✓ |
| Free text | Human-oriented prose | |
| JSON only | Structured output only | |

**User's choice:** Stable record.

---

## Tooling tests

| Option | Description | Selected |
|--------|-------------|----------|
| Golden + assertions | Golden tree for the scaffold plus targeted assertions | ✓ |
| Assertions only | File existence and exit codes | |
| Snapshot | Custom snapshot mechanism | |

**User's choice:** Golden + assertions.

---

## Phase 5 contract

| Option | Description | Selected |
|--------|-------------|----------|
| CONTEXT.md only | A "Phase 5 implications" section, no artifact | ✓ |
| Separate mapping | `schema/consumers.md` | |
| Extend the schema | Add generator-oriented fields now | |

**User's choice:** CONTEXT.md only.

---

## Template extensibility

| Option | Description | Selected |
|--------|-------------|----------|
| Directory + local manifest | `templates/homework-<name>/template.yaml` | ✓ |
| Central registry | `templates/registry.json` | |
| Hard-coded choices | `argparse` choices list | |

**User's choice:** Directory + local manifest.

---

## Required block subschemas

| Option | Description | Selected |
|--------|-------------|----------|
| Board id string | Details resolved from the Phase 5 board profile | ✓ |
| Nested object | Inline MCU, flash, PSRAM | |
| id + profile path | Explicit path to a profile file | |

**User's choice:** Board id string.

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal reference | `source.reference` only; provenance canonical in `task.md` | ✓ |
| Full duplication | Repeat url, date, attribution, license | |
| Path only | `source.task: task.md` | |

**User's choice:** Minimal reference.

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit pins + check | Pins in metadata, cross-checked against the shared configuration | ✓ |
| Section name | Reference the shared configuration section only | |
| Path only | Path to the shared configuration file | |

**User's choice:** Explicit pins + check.

---

## Claude's Discretion

- Internal module layout and helper names for shared validation.
- Renderer implementation, allowlist file shape, and the `--json` record shape.
- Golden-fixture content and per-file assertions.
- Board-profile field names beyond the agreed minimum.

## Deferred Ideas

- CI wiring for the checker and scaffold tests — Phase 8.
- Shared-configuration generator and board-profile population — Phase 5.
- The report contract and measurement ledger — Phase 10.
- Interactive guided mode — Phase 9.
- ESP-IDF and STM32 templates beyond the two shipped here — v2.
- Automatic pinout generation — out of scope.
- `--force` overwrite — rejected for this phase.
- `requirements-dev.txt` or a root project manifest — rejected in favour of PEP 723 plus an
  isolated pre-commit environment.
