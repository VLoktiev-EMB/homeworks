# Architecture Research

**Domain:** Embedded engineering course monorepo (PlatformIO, 30+ independent homework projects, Arduino + ESP-IDF + STM32, public GitHub)
**Researched:** 2026-10-23
**Confidence:** MEDIUM-HIGH (PlatformIO, GitHub Actions, MkDocs, clangd and Wokwi mechanics verified against official docs; long-term tool choices and quota fit are MEDIUM; Velxio maturity is LOW and belongs to the simulation spike)

---

## Executive Summary

The correct architecture for this repository is **a monorepo of independent, disposable PlatformIO projects over a small, strictly layered shared-library core, with every cross-cutting artifact generated from one metadata file**.

Three forces drive every decision:

1. **30+ projects at 2-3 per week.** Anything repeated per homework must be generated, not hand-written. Anything that can drift (index, nav, workspace, CI matrix) must have a `--check` mode that fails CI on drift.
2. **The course teaches frameworks.** A universal HAL would hide the Arduino and ESP-IDF APIs being assessed and would become a shadow framework. The reusable layer must be a *thin, demand-driven* set of ports (`time`, `gpio`, `i2c`, `spi`, `log`) plus pure logic — never a wrapper over `pinMode`, `delay`, or `esp_lcd_*`.
3. **Evidence must survive a year.** Build and test commands, tool pins, simulation command and observed output are part of the artifact. Store the *recipe*, not raw dumps.

The recommended shape is: `lib/common` (pure C domain logic) → `lib/port` (pure C contracts) → `lib/arduino`, `lib/espidf` (adapters) and `lib/host` (test doubles); `homeworks/<id>` composes `common + port + exactly one adapter`; a top-level `tests/` native PlatformIO project tests the shared libraries; `scripts/` reads `homework.yaml` and emits README index, MkDocs nav, VS Code workspace, CI matrix and board pages; GitHub Actions runs static checks + native tests + changed builds on every PR and a full matrix nightly.

Two research findings change the plan in PROJECT.md and must be handled explicitly:

- **`lib_extra_dirs` is deprecated** since PlatformIO 6.0 and slated for removal. The replacement is `lib_deps = Name=symlink://../../lib/<name>`. The architecture must isolate this choice in one generated file so migration is a one-line change, not a 30-project edit.
- **Per-folder clangd servers are not supported** by the VS Code clangd extension (multi-root PR still open). The multi-root workspace works, but per-project clangd configuration must be done with a `.clangd` file inside each homework that points at that project's compilation database — *not* with per-folder `clangd.arguments`.

---

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      AUTHORING / AGENT SURFACE                            │
│  AGENTS.md (canonical)   .claude/CLAUDE.md (imports AGENTS.md)            │
│  homework.yaml   task.md   README.md   assets/diagram.json               │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │ validated + read by
┌──────────────────────────────▼───────────────────────────────────────────┐
│                      METADATA / GENERATION LAYER                          │
│  schemas/  →  scripts/validate_metadata.py                               │
│  scripts/gen_index.py   gen_nav.py   gen_workspace.py   gen_ci_matrix.py │
│  scripts/affected.py    check_architecture.py   simulate.py              │
│  outputs: README index, docs/SUMMARY.md, *.code-workspace, matrix JSON   │
└───────┬──────────────────────────────┬───────────────────────────┬───────┘
        │                              │                           │
┌───────▼──────────────┐   ┌───────────▼───────────┐   ┌───────────▼──────┐
│  SHARED LIBRARIES    │   │  HOMEWORK PROJECTS    │   │  DOCS PIPELINE   │
│  lib/port   (C, API) │   │  homeworks/<id>/      │   │  docs/ + MkDocs  │
│  lib/common (C, logic)│  │  platformio.ini       │   │  literate-nav    │
│  lib/arduino (C++)   │   │  src/ test/ assets/   │   │  gen-files reads │
│  lib/espidf  (C11)   │   │  one project each     │   │  reports         │
│  lib/host    (fakes) │   │                       │   │                  │
└───────┬──────────────┘   └───────────┬───────────┘   └───────────┬──────┘
        │                              │                           │
┌───────▼──────────────────────────────▼───────────────────────────▼──────┐
│                        VERIFICATION LAYER                                │
│  tests/ (platform=native, shared libs)                                   │
│  per-project [env:native] (pure logic)                                   │
│  wokwi-cli / Velxio adapter (simulation)   HIL runner (optional)         │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────────┐
│                        CI / PUBLICATION LAYER                            │
│  PR: meta + architecture + native tests + changed builds + sim(changed)  │
│  nightly: full build matrix + full simulation + optional HIL             │
│  main: MkDocs build → GitHub Pages; tag hw/<id>                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Owns | Must never | Communicates via |
|-----------|------|-----------|------------------|
| `lib/port` | C contracts (function-pointer structs) for `time`, `gpio`, `i2c`, `spi`, `log` | Include any framework header, own state, call hardware | Headers included by `common`, adapters, `host`, projects |
| `lib/common` | Framework-free domain logic: patterns, state machines, timing math, protocol codecs, calculations | Include `Arduino.h`, `esp_*`, FreeRTOS, `host`; block or sleep | `port` headers only |
| `lib/arduino` | C++ adapters implementing `port` over Arduino APIs | Include `common`; leak Arduino types through headers | Implements `port`; linked only by Arduino projects |
| `lib/espidf` | C11 adapters implementing `port` over ESP-IDF drivers | Include `common`; leak `esp_*` types through headers | Implements `port`; linked only by ESP-IDF projects |
| `lib/host` | Native fakes: fake time, recording GPIO, loopback I2C/SPI, Unity helpers | Include framework headers; contain production logic | Implements `port`; linked by tests and `[env:native]` |
| `homeworks/<id>` | Composition root: wiring, framework idioms, report, evidence | Reimplement shared logic; include another homework | `lib_deps` symlinks; `lib_extra_dirs` if retained |
| `tests/` | Cross-library native test suite | Test adapters that require hardware | PlatformIO native env |
| `scripts/` | Deterministic generation, validation, affected-project detection | Network access, timestamps, unordered output | Reads repo files; writes generated artifacts; prints JSON |
| `boards/*.yaml` | Machine-readable board profiles (MCU, pins, voltage, Wokwi id) | Contain prose only | Read by validators, generators, `simulate.py` |
| `docs/` | Standards, ADRs, board/protocol/theory pages, generated site | Duplicate report content | MkDocs + `mkdocs-gen-files` |
| `.github/workflows` | Orchestration only | Contain business logic that cannot run locally | Calls scripts and `pio` |

### Layer Dependency Rule

```
                 ┌──────────────────────┐
                 │ homeworks/<id>       │  composition root
                 └──────┬───────────────┘
             ┌──────────┼──────────────┐
             ▼          ▼              ▼
      ┌───────────┐ ┌─────────┐ ┌───────────┐
      │ lib/arduino│ │lib/espidf│ │ lib/host │  adapters (choose 1 + host for native)
      └─────┬─────┘ └────┬────┘ └─────┬─────┘
            └────────────┼────────────┘
                         ▼
                  ┌────────────┐
                  │ lib/port   │  contracts only
                  └─────┬──────┘
                        ▼
                  ┌────────────┐
                  │ lib/common │  pure logic
                  └────────────┘
```

Allowed edges only: `common → port`, `adapter → port`, `host → port`, `homework → common + port + one adapter (+ host for native)`, `tests → anything`. The core (`common`) never depends outward. This is the Dependency Inversion Principle applied in C: **interfaces belong to their client**, implemented by adapters.

### When a Full HAL Is Justified vs Harmful

Every mature embedded HAL in the research is backed by tooling that a hand-written course HAL would not have:

| System | Abstraction model | What backs it |
|--------|-------------------|---------------|
| AUTOSAR Classic | Application → RTE → Services → ECU Abstraction → MCAL | Normative spec, ARXML, generated RTE/BSW |
| Zephyr | Devicetree bindings + `DEVICE_API` + Kconfig | Bindings, code generation, emulators for ZTest |
| ESP-IDF | LL → HAL → driver, per-peripheral components | Vendor SDK, build-system target selection |
| STM32Cube | HAL/LL + BSP class/common/bus/component drivers | CubeMX code generation, UM2298 guidelines |

A full HAL is justified when **all** of these hold: many hardware variants in one long-lived product family; a certification or safety argument requires it; vendor-neutral middleware is the product; separate teams own drivers and application; and there is a generator/spec to keep the abstraction honest. None hold for this course. A full HAL here is harmful because it hides the framework APIs being assessed, leaks on every capability that differs (Wi-Fi, deep sleep, RMT, I2S), and turns every homework into debugging the HAL instead of the assignment.

**Rule:** add a port only when the **second** homework needs the same capability. Abstract the **bus**, not the driver: `ssd1306_write(port_i2c_t *bus, ...)` is reusable; a `display_hal_init/draw/log/delay` mega-interface is not.

---

## Recommended Project Structure

```
homeworks/
├── AGENTS.md                          # canonical rulebook, <=300 lines
├── README.md                          # intro + generated homework index
├── LICENSE
├── mkdocs.yml                         # theme/plugins; nav generated elsewhere
├── pyproject.toml                     # ruff config for scripts
├── requirements-ci.txt                # pinned: platformio==6.2.x, mkdocs-material, mkdocs-literate-nav, mkdocs-gen-files, jsonschema, pyyaml, pre-commit
├── homeworks.code-workspace           # GENERATED, committed
├── .clang-format  .clang-tidy  .editorconfig  .gitattributes  .gitignore
├── .pre-commit-config.yaml
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                     # PR + main
│   │   ├── nightly.yml                # schedule: full matrix, full sim
│   │   ├── docs.yml                   # main: build + deploy Pages
│   │   └── hil.yml                    # workflow_dispatch / nightly, self-hosted
│   ├── actions/
│   │   ├── setup-pio/action.yml
│   │   └── build-homework/action.yml
│   └── PULL_REQUEST_TEMPLATE/{homework.md,infra.md,docs.md}
├── boards/
│   ├── esp32-s3-devkitc-1.yaml
│   ├── arduino-nano.yaml
│   └── stm32-<model>.yaml
├── schemas/
│   ├── homework.schema.json
│   └── board.schema.json
├── pio/
│   ├── base.ini                       # [env:*_base] shared by all projects
│   └── README.md                      # why these defaults exist
├── templates/
│   ├── arduino/{platformio.ini,src/main.cpp,test/test_logic/test_main.cpp,...}
│   ├── espidf/{...}
│   └── report/{README.md,...}
├── lib/
│   ├── port/{library.json,include/port/*.h}
│   ├── common/{library.json,include/common/*.h,src/*.c}
│   ├── arduino/{library.json,include/arduino/*.h,src/*.cpp}
│   ├── espidf/{library.json,include/espidf/*.h,src/*.c}
│   └── host/{library.json,include/host/*.h,src/*.c}
├── tests/                             # PlatformIO project, platform = native
│   ├── platformio.ini
│   └── test/test_common_patterns/test_patterns.c
├── scripts/
│   ├── lib/                           # shared Python package (yaml load, paths, git)
│   ├── validate_metadata.py
│   ├── gen_index.py
│   ├── gen_nav.py
│   ├── gen_workspace.py
│   ├── gen_ci_matrix.py
│   ├── gen_board_pages.py
│   ├── affected.py
│   ├── check_architecture.py
│   ├── gen_compile_db.py
│   └── simulate.py
├── docs/
│   ├── index.md                       # intro (hand-written)
│   ├── homeworks.md                   # GENERATED catalog
│   ├── SUMMARY.md                     # GENERATED nav for literate-nav
│   ├── onboarding.md                  # VS Code, extensions, tasks, clangd
│   ├── boards/                        # GENERATED from boards/*.yaml
│   ├── protocols/  components/  theory/
│   ├── standards/{coding,reports,testing,git,evidence}.md
│   ├── decisions/0001-....md          # ADRs (MADR)
│   └── sources.md                     # citation registry [SRC-001]
└── homeworks/
    └── 1_3-police-flasher/
        ├── task.md                    # English paraphrase + source
        ├── homework.yaml              # SINGLE SOURCE OF TRUTH
        ├── README.md                  # academic report (10 sections)
        ├── platformio.ini             # extends pio/base.ini
        ├── platformio.shared.ini      # GENERATED lib_deps (see ADR-0003)
        ├── wokwi.toml
        ├── .clangd                    # points at .pio/build/<env>
        ├── src/main.cpp
        ├── include/
        ├── test/test_logic/test_main.cpp
        └── assets/
            ├── diagram.json           # wiring source of truth
            ├── diagram.sim.json       # OPTIONAL documented deviation
            ├── bom.csv
            ├── fritzing/*.svg
            └── evidence/simulation.md # curated, reproducible evidence
```

### Structure Rationale

- **`homeworks/<id>` is the unit of independence.** It has its own `platformio.ini`, so `pio run -d homeworks/<id>`, grading, and deletion are local operations. Never make one `platformio.ini` govern several homeworks.
- **`pio/base.ini` + `extends`** removes per-project boilerplate without a generator having to rewrite `platformio.ini`. All homework directories sit at the same depth, so relative paths such as `../../lib/common` are stable.
- **`platformio.shared.ini` is generated per homework** from `homework.yaml`. This is the hinge that isolates the `lib_extra_dirs` vs `symlink://` decision (below) and prevents a project from accidentally linking an ESP-IDF adapter into an Arduino build.
- **`lib/` at the root, not inside each homework**, is what makes reuse real across 30+ projects. Each library has `library.json`; without a manifest, `symlink://` and LDF fail with a missing-package-manifest error.
- **Top-level `tests/` is a real PlatformIO project**, not a folder of loose tests, because that is the only way `pio test -e native` works uniformly and the only place where a framework-independence check is meaningful.
- **`assets/` is inside the homework**, so a homework directory can be copied out and still be complete.
- **`docs/` is the only place for prose shared across homeworks.** Reports link to it; they do not copy it.

### Shared Library Wiring — `lib_extra_dirs` vs `symlink://`

PROJECT.md requires `lib_extra_dirs`. Research shows the option is **deprecated since PlatformIO 6.0** ("will be removed in the next major release"); official docs recommend:

```ini
[env:myenv]
lib_deps =
    FooLib=symlink://../../shared-libraries/FooLib
```

Comparison for this repo:

| Criterion | `lib_extra_dirs = ../../lib` | `lib_deps = common=symlink://../../lib/common` |
|-----------|------------------------------|-----------------------------------------------|
| Deprecation | Deprecated, removal pending | Current, supported |
| Dependency explicitness | LDF scans *all* five libs; can link the wrong adapter | Explicit: only declared libs |
| Per-project adapter choice | Easy to get wrong | Encoded in generated file |
| Boilerplate | One line | 2-3 lines per project, generated |
| Known friction | None today | `.pio-link` stale-file issues reported; nested `src_dir` edge cases |

**Recommendation:** use `symlink://` as the primary mechanism, emitted into `platformio.shared.ini` by `gen_*`, and keep a single switch in the generator to fall back to `lib_extra_dirs`. Record this as **ADR-0003** because it changes a stated requirement. Do not let each homework hand-write its library list.

Generated file for an Arduino homework:

```ini
; platformio.shared.ini — GENERATED from homework.yaml; do not edit
[env]
lib_deps =
    symlink://../../lib/port
    symlink://../../lib/common
    symlink://../../lib/arduino
```

For an ESP-IDF homework, substitute `lib/espidf`. For the `native` env, substitute `lib/host`.

---

## Architectural Patterns

### Pattern 1: Ports and Adapters in C, Owned by the Core

**What:** `lib/port` defines C structs of function pointers. The *consumer* (`common`) declares the interface it needs; adapters provide implementations; the composition root injects them.

**When to use:** whenever pure logic needs time, GPIO, a bus, logging or storage. Do not use it for framework idioms the course must teach.

**Trade-offs:** one indirect call plus pointer storage; slightly more ceremony at `main()`. In exchange: deterministic host tests, no framework headers in `common`, and adapters replaceable per board. For a one-off homework the ceremony is not worth it — this pattern earns its keep at 30+.

```c
/* lib/port/include/port/time.h — C99, extern "C", no framework headers */
typedef struct port_time {
    uint32_t (*now_ms)(void *ctx);
    void *ctx;
} port_time_t;

static inline uint32_t port_now_ms(const port_time_t *t) {
    return t->now_ms(t->ctx);
}

/* lib/host/include/host/fake_time.h — deterministic test double */
typedef struct { uint32_t now_ms; } host_fake_time_t;
port_time_t host_fake_time_create(host_fake_time_t *state);
void        host_fake_time_advance(host_fake_time_t *state, uint32_t ms);

/* lib/arduino/src/time.cpp — adapter, no logic */
static uint32_t arduino_now_ms(void *ctx) {
    (void)ctx;
    return millis();
}
port_time_t arduino_time_create(void) {
    return (port_time_t){ .now_ms = arduino_now_ms, .ctx = NULL };
}
```

**Enforcement:** `scripts/check_architecture.py` (see below) plus a CI job that compiles `lib/common` and `lib/port` against `platform = native` in the `tests/` project. If it compiles natively, it has no framework dependency.

### Pattern 2: Metadata-Driven Generation with Drift Checks

**What:** `homework.yaml` is the only editable metadata. Every derived artifact is written by a deterministic script that supports `--check`.

**When to use:** any artifact repeated per homework: README index row, MkDocs nav entry, workspace folder, CI matrix entry, board page table.

**Trade-offs:** you must run a script after editing metadata; mitigated by `--check` in CI and a `pio`/`make` alias. Without `--check`, generated files silently rot, which is worse than hand-editing.

```yaml
# homework.yaml (illustrative)
schema: 1
id: 1_3-police-flasher
module: 1
lesson: "1.3"
title: Police Flasher
board: esp32-s3-devkitc-1
framework: arduino          # arduino | espidf
language: cpp               # cpp | c
libs: [common, port, arduino]
simulation:
  provider: wokwi           # wokwi | velxio | none | unsupported
  diagram: assets/diagram.json
tests:
  unit: true
  simulation: true
report: README.md
assets: [assets/bom.csv, assets/diagram.json]
status: in-progress         # draft | in-progress | complete
source: "Course handout 1.3 (paraphrased)"
```

| Generated artifact | Script | Consumed by |
|--------------------|--------|-------------|
| `README.md` index section | `gen_index.py` | Humans, GitHub landing page |
| `homeworks/README.md` | `gen_index.py` | Navigation at 30+ items |
| `docs/homeworks.md` | `gen_index.py` | MkDocs catalog |
| `docs/SUMMARY.md` | `gen_nav.py` | `mkdocs-literate-nav` |
| `homeworks.code-workspace` | `gen_workspace.py` | VS Code |
| CI matrix JSON | `gen_ci_matrix.py` / `affected.py` | GitHub Actions |
| `docs/boards/*.md` | `gen_board_pages.py` | MkDocs |
| `platformio.shared.ini` | `gen_shared_ini.py` | PlatformIO LDF |

**Determinism rules:** sort by `(module, lesson)`, never emit timestamps or absolute paths, write with `\n`, and expose `--check` that re-renders into memory and exits `1` on any difference.

### Pattern 3: Shared PlatformIO Configuration via `extra_configs` + `extends`

**What:** `pio/base.ini` holds environment templates; each homework's `platformio.ini` is 5-10 lines.

```ini
; pio/base.ini
[arduino_esp32s3_base]
platform = espressif32
framework = arduino
board = esp32-s3-devkitc-1
monitor_speed = 115200
build_flags = -Wall -Wextra -Werror
test_dir = test

[native_base]
platform = native
build_flags = -std=c11 -Wall -Wextra -Werror -DPIO_UNIT_TESTING
lib_deps =
    symlink://../../lib/port
    symlink://../../lib/host
```

```ini
; homeworks/1_3-police-flasher/platformio.ini
[platformio]
default_envs = esp32s3
extra_configs = ../../pio/base.ini

[env:esp32s3]
extends = arduino_esp32s3_base
lib_deps =
    symlink://../../lib/port
    symlink://../../lib/common
    symlink://../../lib/arduino
```

**Trade-off:** `extends` and interpolation across `extra_configs` are powerful but can be surprising; prefer explicit `lib_deps` in the generated shared file over clever interpolation. Phase 1 must verify `extends` resolution on PlatformIO 6.2 before scaling it.

### Pattern 4: Simulator as a Provider Adapter

**What:** `scripts/simulate.py --provider wokwi|velxio` owns build artifact discovery, diagram path, timeout and expected-output assertions. CI calls the script, not the vendor CLI directly.

**When to use:** from the moment more than one simulator is under evaluation (the spike).

**Trade-offs:** a thin abstraction is justified because the spike explicitly compares Velxio, Wokwi and Fritzing. Keep the contract narrow: `(elf, diagram, timeout, expect_text) -> (exit_code, serial_log)`. Do not attempt to abstract simulator internals.

### Pattern 5: Hub-and-Leaf Multi-Root Workspace

**What:** the workspace's first folder is the repository root ("hub" for `.github`, `schemas`, `pio`, `.planning`), followed by `docs`, `lib`, `scripts`, and one leaf per homework.

**When to use:** every day, for this repository.

**Trade-offs:** 30+ folders is heavy in the Explorer and causes overlapping file watchers. Mitigate with `files.watcherExclude` / `search.exclude` for `**/.pio/**`, `**/site/**`, and generate a second, *uncommitted* `focus.code-workspace` containing only the active homework.

### Pattern 6: Evidence as a Reproducibility Triple

**What:** every simulation/measurement evidence file records `(exact command, pinned versions/commit, observed excerpt)`. Machine logs are CI artifacts; the committed file is a short, curated excerpt.

**When to use:** reports, traceability matrices, the `hw-report` skill.

**Trade-offs:** slightly more writing than pasting a screenshot. It is the difference between an academic artifact and an unreproducible claim.

---

## Data Flow

### Flow 1: Authoring a Homework

```
task.md + course handout
        │
        ▼
new-homework skill ──► templates/ ──► homeworks/<id>/ skeleton
        │
        ▼
author edits homework.yaml ──► validate_metadata.py (schema + invariants)
        │                              │ fail → stop, explain
        ▼                              ▼
generators (index, nav, workspace, shared ini, matrix) ──► derived files
        │
        ▼
code + tests + diagram.json + report
        │
        ▼
pre-commit (format, lint, metadata --check) ──► commit ──► PR
```

### Flow 2: CI Change Detection

```
git diff --name-only origin/main...HEAD
        │
        ▼
scripts/affected.py  (single source of mapping logic)
   homeworks/<id>/**        → {<id>}
   lib/<lib>/**             → every project whose homework.yaml lists <lib>
   schemas/** scripts/** pio/** templates/** .github/** → ALL projects + infra flag
   docs/**                  → docs job only
   boards/*.yaml            → projects using that board + docs
        │
        ▼
{"include":[{"project":"1_3-police-flasher","env":"esp32s3","sim":true}, ...]}
        │
        ▼
GitHub Actions matrix via fromJSON, guarded against an empty array
```

This replaces hand-maintained `paths:` filters. The critical edge — **a change in `lib/common` must rebuild every consumer** — is a git-diff query, not a path-filter list that drifts.

### Flow 3: Build and Language Server

```
pio run -d homeworks/<id> -e <env>
        │
        ├──► .pio/build/<env>/firmware.{bin,elf}  ──► simulation / flash
        └──► pio run -t compiledb  ──► compile_commands.json
                                         │
                                         ▼
                              homeworks/<id>/.clangd
                              CompileFlags:
                                CompilationDatabase: .pio/build/<env>
                                         │
                                         ▼
                              clangd (single server, per-file CDB lookup)
```

### Flow 4: Tests

```
                 ┌──────────────────────────────┐
                 │ tests/  platform = native    │  shared libs, every PR
                 └──────────────┬───────────────┘
                                │
   pure logic in homework ──────┤
        [env:native]            │
                                ▼
                 ┌──────────────────────────────┐
                 │ Unity + lib/host fakes       │  deterministic, milliseconds
                 └──────────────┬───────────────┘
                                │ (cannot catch timing/wiring)
                                ▼
                 ┌──────────────────────────────┐
                 │ simulation (wokwi/velxio)    │  changed PRs + nightly
                 └──────────────┬───────────────┘
                                │ (cannot catch analog/power/EMC)
                                ▼
                 ┌──────────────────────────────┐
                 │ HIL (self-hosted, nightly)   │  scarce, serialized
                 └──────────────────────────────┘
```

### Flow 5: Documentation Publication

```
homework.yaml ──► docs/homeworks.md (catalog)
homeworks/<id>/README.md ──► mkdocs-gen-files (virtual page, no copy)
docs/standards|boards|protocols|theory|decisions (hand-written)
        │
        ▼
docs/SUMMARY.md (generated) + mkdocs.yml (hand-written theme/plugins)
        │
        ▼
mkdocs build --strict ──► site/ ──► actions/upload-pages-artifact ──► deploy-pages
```

### Flow 6: Simulation and Evidence

```
pio run ──► firmware.elf/.bin ──┐
assets/diagram.json ────────────┼──► scripts/simulate.py --provider wokwi
wokwi.toml (firmware paths) ────┘         │
                                          ├── exit code (0/42 timeout/other)
                                          ├── serial.log (CI artifact)
                                          └── expect_text assertion
                                                   │
                                                   ▼
                                  assets/evidence/simulation.md (curated)
                                  + traceability matrix row in README
```

---

## Editor / Tooling Architecture

### Multi-Root Workspace

Generated `homeworks.code-workspace`:

```json
{
  "folders": [
    { "name": "repo",    "path": "." },
    { "name": "docs",    "path": "docs" },
    { "name": "lib",     "path": "lib" },
    { "name": "scripts", "path": "scripts" },
    { "name": "1.3 Police Flasher", "path": "homeworks/1_3-police-flasher" }
  ],
  "settings": {
    "files.watcherExclude": { "**/.pio/**": true, "**/site/**": true, "**/.git/**": true },
    "search.exclude":       { "**/.pio/**": true, "**/site/**": true },
    "clangd.arguments": [
      "--query-driver=**/.platformio/packages/toolchain-*/bin/*",
      "--background-index",
      "--header-insertion=never"
    ]
  }
}
```

Notes that matter:

- **Overlapping folders** (root plus `docs`, `lib`, `scripts`) duplicate file watchers and search results. Acceptable for a hub, but exclude `.pio` aggressively.
- **`--query-driver` is global and intentionally broad.** It is an allowlist for clangd to query cross compilers, not a per-project setting; a glob covering all PlatformIO toolchains is correct here.
- **Do not put `--compile-commands-dir` in workspace `clangd.arguments`.** It globally overrides nested `.clangd` configuration.
- As of research, `vscode-clangd` does **not** support one server per folder (`clangd.enablePerFolderServer` is an unmerged PR). Per-project behavior must come from `.clangd` files, which clangd discovers per file.

Per-homework `.clangd`:

```yaml
CompileFlags:
  CompilationDatabase: .pio/build/esp32s3
  Add: [-std=gnu++17]
```

Generate `compile_commands.json` with:

```bash
pio run -d homeworks/1_3-police-flasher -e esp32s3 -t compiledb
```

PlatformIO writes it to the project directory by default. clangd loads a compilation database lazily when a file in that tree is opened, so a single server serves all 30 projects without cross-contamination of *settings* (though the background index is shared; wrong-symbol navigation across projects is a known limitation).

### PlatformIO Project Detection

- The PlatformIO IDE treats a folder as a project when it contains `platformio.ini`. In a multi-root workspace, each homework folder is therefore a distinct project — this is the reason to use multi-root rather than one root.
- In CI and scripts, always address projects explicitly: `pio run -d homeworks/<id> -e <env>`. Never rely on the current working directory.
- `pio project config --json-output` returns computed config (a list of `[section, [[key, value], ...]]` pairs) and is the reliable way to discover `default_envs` for a matrix; its JSON shape is positional, so prefer reading `homework.yaml` for project identity and use `pio project config` only for environment discovery.
- `pio project metadata --json-output -e <env>` provides build metadata for IDE integration; useful when debugging clangd include paths.

---

## CI Architecture

### Workflow Topology

| Workflow | Trigger | Jobs | Permissions | Notes |
|----------|---------|------|-------------|-------|
| `ci.yml` | `pull_request`, push to `main` | `meta` → `changes` → `native-tests`, `build` (matrix), `simulate` (matrix), `docs-build` → `gate` | `contents: read`; `pull-requests: read` for change detection | `gate` is the single required status check |
| `nightly.yml` | `schedule`, `workflow_dispatch` | full build matrix, full simulation, optional HIL | `contents: read` | No deployment |
| `docs.yml` | push to `main`, `workflow_dispatch` | `build` → `deploy` | workflow: `contents: read`; deploy job: `pages: write`, `id-token: write` | `environment: github-pages`, `concurrency: group: pages` |
| `hil.yml` | `workflow_dispatch`, nightly | flash + serial assertions | `contents: read` | `runs-on: [self-hosted, esp32]`; never on fork PRs |

### `meta` Job (always full, fast)

`validate_metadata.py --check` · `gen_* --check` (drift) · markdownlint · yamllint · ruff · gitleaks · clang-format check · `check_architecture.py` · `wokwi-cli lint` for every `diagram.json` · link check. Target under two minutes; this is the job that protects repository integrity.

### Change Detection

Preferred: `scripts/affected.py` (git diff + `homework.yaml` `libs`), because it handles shared-library consumers and is testable locally. `dorny/paths-filter@v4` is acceptable only if filters are generated from the same metadata; hand-written filters are a known drift source.

```yaml
changes:
  runs-on: ubuntu-latest
  permissions: { contents: read, pull-requests: read }
  outputs:
    matrix: ${{ steps.affected.outputs.matrix }}
  steps:
    - uses: actions/checkout@v5
      with: { fetch-depth: 0, persist-credentials: false }
    - id: affected
      run: echo "matrix=$(python scripts/affected.py --base origin/main --format matrix)" >> "$GITHUB_OUTPUT"

build:
  needs: changes
  if: ${{ needs.changes.outputs.matrix != '[]' && needs.changes.outputs.matrix != '' }}
  strategy:
    fail-fast: false
    matrix: ${{ fromJSON(needs.changes.outputs.matrix) }}
  runs-on: ubuntu-latest
  timeout-minutes: 25
  steps:
    - uses: actions/checkout@v5
      with: { persist-credentials: false }
    - uses: actions/cache@v4
      with:
        path: |
          ~/.cache/pip
          ~/.platformio/.cache
        key: ${{ runner.os }}-pio-${{ hashFiles('requirements-ci.txt', '**/platformio.ini', 'lib/**/library.json') }}
        restore-keys: ${{ runner.os }}-pio-
    - uses: ./.github/actions/setup-pio
    - run: pio run -d "homeworks/${{ matrix.project }}" -e "${{ matrix.env }}"
```

### Caching

- **Do:** cache `~/.cache/pip` and `~/.platformio/.cache` (official guidance). Key on OS + pinned requirements + all `platformio.ini` + `library.json`.
- **Optionally:** cache a shared `PLATFORMIO_BUILD_CACHE_DIR` for object files across jobs; measure before adopting.
- **Do not:** cache `homeworks/*/.pio/build`. It is large, project-specific, and stale-object bugs are hard to diagnose.
- Pin `platformio==6.2.x` in `requirements-ci.txt`. An unpinned `pip install -U platformio` makes nightly failures non-reproducible.

### Simulation Job and Quota Budget

Wokwi CI is metered on a rolling 30-day window: 50 min (Free), 200 (Hobby), 500 (Hobby+), 2000 (Pro), with a maximum wall-clock per session of 5/5/10/50 min. A naive nightly run of 30 homeworks at 10 simulated seconds each is ~5 min per night, ~150 min per 30 days — over Free and close to Hobby. Architecture:

- PRs: simulate **changed projects only**, 10-20 s each.
- Nightly: full simulation **once or twice per week**, not every night; split across jobs to stay under the per-session wall clock.
- `--timeout` every test and assert on expected serial text; a timeout exit code (42) must be treated as failure, not success.
- `WOKWI_CLI_TOKEN` as a repository secret; jobs skip with a clear notice when the secret is absent (fork PRs).

### Permissions and Security

- Workflow-level `permissions: contents: read`; elevate only in the Pages deploy job.
- Never use `pull_request_target` with a checkout of the PR head. Use `pull_request` for untrusted builds; if privileged post-processing is needed, use `workflow_run` on artifacts.
- Pin third-party actions to commit SHAs; set `persist-credentials: false`.
- Do not run HIL or simulation with secrets on fork PRs.
- Pages deploy requires `pages: write` **and** `id-token: write`, plus `environment: github-pages`; use `configure-pages`, `upload-pages-artifact`, `deploy-pages`.

### Required Status Check

Matrix job names vary with the matrix and a fully skipped matrix produces no checks. Add a `gate` job (`if: always()`, `needs: [...]`) that fails if any dependency failed or was cancelled, and make **only `gate`** required in branch protection.

---

## Testing Architecture

### Layout

```
tests/                              # shared libraries, platform = native
├── platformio.ini
└── test/
    ├── test_common_patterns/test_patterns.c
    ├── test_common_timing/test_timing.c
    └── test_port_contracts/test_contracts.c

homeworks/<id>/
├── test/
│   └── test_logic/test_logic.cpp   # PIO requires test_<name> directories
└── platformio.ini                  # [env:native] + [env:<target>]
```

`test_dir` defaults to `test` (singular); keep that default inside homeworks. The top-level shared suite lives in `tests/` (plural) only to distinguish it from any single project.

### Configuration

```ini
; tests/platformio.ini
[env:native]
platform = native
test_dir = test
build_flags = -std=c11 -Wall -Wextra -Werror
lib_deps =
    symlink://../lib/port
    symlink://../lib/common
    symlink://../lib/host
    throwtheswitch/Unity@^2.6.0
```

Per-homework native environment uses source filtering rather than `test_build_src` (which official docs mark **NOT RECOMMENDED** and which requires `PIO_UNIT_TESTING` guards):

```ini
[env:native]
extends = native_base
build_src_filter = +<*> -<main.cpp>   ; exclude setup()/loop() or app_main()
test_filter = test_logic
```

If a project truly cannot separate its entry point, `test_build_src = true` plus `#ifndef PIO_UNIT_TESTING` around `setup/loop/app_main` is the documented fallback — treat it as a smell.

### Test Pyramid for This Course

| Tier | What it proves | Runs | Cost |
|------|----------------|------|------|
| Static | formatting, lint, architecture, metadata, schema | every commit / PR | seconds |
| Unit (native) | pure logic, math, state machines, codecs | every PR | milliseconds |
| Integration (native + fakes) | composition of logic with fake time/bus | every PR | milliseconds |
| Simulation | wiring, pin map, peripheral behaviour, boot | changed PRs + scheduled | seconds-minutes, metered |
| HIL | analog, power, real timing, real sensors | nightly/manual | minutes, scarce |

A fake HAL has no concept of time; timing bugs structurally escape native tests. Simulation advances simulated time deterministically; it still cannot catch analog, power or EMC behaviour. That is why the tiers are complementary, not substitutes.

### Fake Time and Determinism

- `lib/host` provides `host_fake_time_t` with explicit `advance(ms)`. Pure logic never calls `delay()`, `millis()`, `vTaskDelay()` or `esp_timer_get_time()` directly.
- Tests assert on logical time: "after advancing 500 ms, the pattern index is 2". No sleeps.
- Serial output is asserted as substrings, not full dumps; normalise line endings.
- Every test is independent and order-free; no shared global state in `common` (pass state explicitly).

### Coverage

Optional and scoped: gcov/lcov on the `tests/` native project only, with a gate on `lib/common` and `lib/port`. Adapters are exercised by simulation/HIL, not coverage. Do not chase coverage on Arduino/ESP-IDF adapters.

---

## Simulation Integration

### Source of Truth

`assets/diagram.json` is canonical. It defines parts, connections and pin usage; the report's pin map and BOM must agree with it. Validation in `meta`:

- `wokwi-cli lint` (catches unknown part types, invalid pins, duplicate IDs) — offline, no token.
- Cross-check every connection pin against `boards/<board>.yaml` allowed pins.
- Cross-check BOM component references against `assets/bom.csv`.

### File Placement Problem and Resolution

Wokwi tooling defaults to `diagram.json` at the project root, while PROJECT.md requires `assets/diagram.json`. Resolution:

- Canonical: `assets/diagram.json` (committed, reviewed, referenced by the report).
- CLI: `wokwi-cli --diagram-file assets/diagram.json` (explicit, no copy).
- VS Code Wokwi extension: generate a root-level `diagram.json` copy via `scripts/simulate.py prepare` (gitignored), or document opening the canonical file if the extension version supports it. Do not commit two divergent copies.
- `wokwi.toml` at the project root points at build artifacts:

```toml
[wokwi]
version = 1
firmware = ".pio/build/esp32s3/firmware.bin"
elf = ".pio/build/esp32s3/firmware.elf"
```

### Headless CI and Evidence

```bash
python scripts/simulate.py \
  --project homeworks/1_3-police-flasher --env esp32s3 \
  --provider wokwi --timeout 15000 \
  --expect "PATTERN=police" \
  --serial-log artifacts/1_3/serial.log
```

- Exit `0` only on expected text; exit `42` (Wokwi timeout) is failure.
- CI uploads `serial.log` and screenshots as artifacts (short retention).
- Committed evidence (`assets/evidence/simulation.md`) records command, firmware commit, Wokwi/Velxio version, expected text, and a 5-15 line observed excerpt.
- The traceability matrix in the report links requirement → test/evidence file → result.

### Fallback Ladder for Unsupported Hardware

1. **Native board alias.** Use the closest supported Wokwi board (ESP32-S3 DevKitC-1 is supported) and note the difference.
2. **Documented simulation overlay.** `assets/diagram.sim.json` substitutes a supported board/peripheral; `homework.yaml.simulation.deviation` records what differs. Real wiring stays in `diagram.json`.
3. **Logic-only simulation.** Run the same logic on host with `lib/host` fakes; mark the evidence as logic-only, not wiring.
4. **Custom chip WASM.** Only if the missing part is central and the spike proves it is maintainable; otherwise it is over-engineering.
5. **`simulation: unsupported`.** CI skips with a visible notice; the report must state why and provide manual/HIL evidence. `validate_metadata.py` requires a `reason` field for this status.

### Provider Contract

`simulate.py` normalises `wokwi` and `velxio` behind `(project, env, diagram, timeout, expect) -> (exit_code, serial_log_path)`. The simulation spike (Velxio vs Wokwi vs Fritzing) produces **ADR-0004** and fills in provider-specific details. Fritzing is an output format for report illustrations, never a source of truth.

---

## Documentation Layering

| Layer | File(s) | Audience | Rule |
|-------|---------|----------|------|
| Agent rulebook | `AGENTS.md` (~300 lines) | Claude, Gemini, humans | Canonical; commands, layout, enforcement tags, routing table |
| Claude entry | `.claude/CLAUDE.md` | Claude Code | Imports `AGENTS.md` (`@../AGENTS.md`); no duplicated rules |
| Standards | `docs/standards/*.md` | Author/agent | Coding, report, testing, git, evidence standards; normative |
| Decisions | `docs/decisions/NNNN-*.md` | Future maintainers | MADR; accepted ADRs are frozen, superseded not edited |
| Board profiles | `boards/*.yaml` → `docs/boards/*.md` | Author/agent | YAML is machine truth; pages are generated |
| Protocols / components / theory | `docs/protocols`, `docs/components`, `docs/theory` | Reader | Shared conceptual pages; reports link, never copy |
| Sources | `docs/sources.md` | Reports | Stable `[SRC-001]` registry; a script validates citations |
| Homework artifact | `homeworks/<id>/README.md` | Grader/reader | 10-section academic report, self-contained |
| Site | `mkdocs.yml`, generated `docs/SUMMARY.md` | Public | Material theme; nav generated; `build --strict` in CI |

Key rules:

- **`AGENTS.md` is the only rulebook.** Nested `AGENTS.md` files are allowed only where rules genuinely differ (e.g., `lib/AGENTS.md` for the dependency rule). Agents read the nearest file, so keep nested files additive.
- **ADRs are the place for "why".** `0001-monorepo`, `0002-ports-and-adapters`, `0003-lib-extra-dirs-vs-symlink`, `0004-simulator-selection`, `0005-docs-generation`. Any structural change without an ADR is rejected ([review] tag).
- **No report duplication in `docs/`.** `mkdocs-gen-files` reads `homeworks/<id>/README.md` into the virtual docs tree; `docs/homeworks.md` is only a catalog.
- **Citations are stable IDs.** Reports cite `[SRC-001]`; `validate_metadata.py` checks the ID exists and `docs/sources.md` checks it is used.

---

## Scaling Considerations

| Scale | What changes |
|-------|--------------|
| 0-5 homeworks | Manual generation is tolerable; still use `tests/` and the dependency rule from day one to avoid a rewrite. |
| 5-15 | `--check` drift gates and `affected.py` become mandatory; multi-root Explorer gets noisy → add `focus.code-workspace`. |
| 15-30 | CI matrix sharding; per-project build time dominates → shared object cache; simulation quota forces weekly full runs. |
| 30+ | Split nightly into module groups; consider sharding builds across 2-4 jobs; docs nav needs pagination/grouping by module; LFS audit; consider a "tooling version" tag. |

### Scaling Priorities

1. **First bottleneck: CI wall clock and cost.** 30 projects × 2 environments × ~2-4 min. Fix with change detection, PIO package cache, `fail-fast: false`, and per-job timeouts before adding runners.
2. **Second bottleneck: simulation quota.** Metered minutes and 5-10 minute session caps. Fix with changed-only PR runs, weekly full runs, and short timeouts.
3. **Third bottleneck: human navigation.** 30+ folders and 30+ reports. Fix with generated index, docs nav grouped by module, and focus workspaces.
4. **Fourth: repository size.** Firmware binaries and media. LFS with limits; videos linked; evidence curated, not dumped.

---

## Anti-Patterns

### Anti-Pattern 1: Universal HAL / Shadow Framework

**What people do:** wrap `pinMode`, `delay`, `log`, `i2c`, `wifi`, `sleep` into one `hal_*` API used by every homework.
**Why it's wrong:** it hides the Arduino and ESP-IDF APIs the course assesses; every divergence (Wi-Fi, RMT, I2S, deep sleep) leaks or forces the HAL to grow; the student debugs the HAL, not the assignment.
**Do instead:** thin ports for time/GPIO/bus/log, added on second use; framework idioms stay in homework code; bus-level driver reuse.

### Anti-Pattern 2: Pre-Scaffolding 30 Homework Directories

**What people do:** generate all folders and templates up front.
**Why it's wrong:** speculative structure, empty projects that fail CI, stale templates, noise in the workspace and docs.
**Do instead:** generate on demand with `new-homework`; the pilot validates the template before scale.

### Anti-Pattern 3: `lib_extra_dirs` Pointing at the Whole `lib/` Tree

**What people do:** `lib_extra_dirs = ../../lib` in every project.
**Why it's wrong:** LDF scans all libraries, so an Arduino project can link the ESP-IDF adapter; the option is deprecated; dependency intent is invisible.
**Do instead:** explicit generated `symlink://` entries per project; one switch to fall back if required.

### Anti-Pattern 4: Hand-Maintained CI Path Filters

**What people do:** list `homeworks/**` and `lib/**` filters by hand.
**Why it's wrong:** shared-library consumers are missed; adding a homework requires editing YAML; drift is silent.
**Do instead:** `affected.py` over `git diff` + `homework.yaml.libs`.

### Anti-Pattern 5: Committed Generated Files Without Drift Checks

**What people do:** commit the index, nav and workspace but never verify them.
**Why it's wrong:** they diverge from metadata; readers trust a stale catalog.
**Do instead:** `--check` for every generator in the `meta` job.

### Anti-Pattern 6: One Giant Nightly Matrix

**What people do:** 30 projects × all envs × all simulators in one job graph, no cache, no timeouts.
**Why it's wrong:** one failure cancels everything; cost explodes; simulation quota is consumed by unchanged projects.
**Do instead:** changed-first PRs, sharded nightly, cache, `fail-fast: false`, explicit timeouts.

### Anti-Pattern 7: `pull_request_target` + PR Head Checkout

**What people do:** use the privileged event to comment on PRs while checking out PR code.
**Why it's wrong:** fork code executes with secrets and a write token ("pwn request").
**Do instead:** unprivileged `pull_request` for builds; `workflow_run` on artifacts for privileged follow-up; minimal `GITHUB_TOKEN`.

### Anti-Pattern 8: Expecting Per-Folder clangd Servers

**What people do:** set `clangd.arguments` per workspace folder and expect per-project compilation databases.
**Why it's wrong:** unsupported; the argument is global and overrides nested configuration.
**Do instead:** one `.clangd` per homework with `CompileFlags.CompilationDatabase`; broad global `--query-driver`.

### Anti-Pattern 9: Raw Evidence Dumps

**What people do:** commit full serial logs, 40 screenshots, random timestamps.
**Why it's wrong:** unreviewable, unreproducible, bloats the repo, and ages badly.
**Do instead:** reproducibility triple + short excerpt; full logs as CI artifacts.

### Anti-Pattern 10: Reports Copied Into the Docs Site

**What people do:** duplicate or symlink each `README.md` into `docs/`.
**Why it's wrong:** two sources drift; links break; edits happen in the wrong file.
**Do instead:** `mkdocs-gen-files` reads the report from its canonical location into the virtual site.

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| PlatformIO CLI/Core | `pio run -d`, `pio test -e native`, `pio project config --json-output`, `-t compiledb` | Pin version; address projects explicitly |
| GitHub Actions | Workflows call local scripts + composite actions | `contents: read` default; `pages: write` only for deploy |
| Wokwi CI | `wokwi/wokwi-ci-action@v1` or `wokwi-cli`; `WOKWI_CLI_TOKEN` | Metered quota; fork PRs have no secret |
| Velxio | Self-hosted; called through `simulate.py --provider velxio` | Maturity pending spike (ADR-0004) |
| GitHub Pages | `configure-pages` → `upload-pages-artifact` → `deploy-pages` | `pages: write` + `id-token: write`, `environment: github-pages` |
| MkDocs Material | `mkdocs build --strict`; literate-nav; gen-files | Nav generated; theme hand-written |
| clangd / VS Code | `.clangd` per project; global `--query-driver` | No per-folder server support |
| Git LFS | `.gitattributes` patterns for binaries/media | Limits enforced in review/CI |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `homework.yaml` → generators | Read-only file contract | Schema is the API; `additionalProperties: false` |
| generators → repo artifacts | Deterministic write + `--check` | No network, no timestamps |
| `lib/common` ↔ `lib/port` | C headers, `extern "C"` | Dependency direction only inward |
| adapter ↔ port | Function-pointer structs | Adapter never exposes framework types in headers |
| homework ↔ adapter | Generated `lib_deps` / `lib_extra_dirs` | Exactly one framework adapter per target env |
| `scripts/affected.py` ↔ CI | JSON `{include: [...]}` | Same script runs locally |
| `simulate.py` ↔ providers | Narrow `(elf, diagram, timeout, expect)` contract | Provider-specific flags stay inside |
| reports ↔ docs | gen-files virtual pages | No copies |

---

## Suggested Build Order

Phases are ordered by dependency; each ships a working increment and avoids speculative scaffolding.

| Order | Phase | Depends on | Ships |
|-------|-------|-----------|-------|
| 0 | **Foundations** — repo skeleton, `AGENTS.md`, `docs/standards/`, ADR 0001-0003, `schemas/homework.schema.json`, `boards/*.yaml`, `pio/base.ini` | — | A validating, lintable empty repo |
| 1 | **Shared core** — `lib/port`, `lib/host` fakes, minimal `lib/common`, `tests/` native project, `check_architecture.py` | 0 | Native tests proving the dependency rule |
| 2 | **Metadata pipeline** — templates, `validate_metadata.py`, `gen_index`, `gen_nav`, `gen_workspace`, `gen_shared_ini`, `new-homework` skill | 0, 1 | One pilot skeleton, all derived artifacts in sync |
| 3 | **Developer experience** — clangd/compiledb, `.clangd` generation, clang-format/tidy, pre-commit, tasks | 2 | A homework opens with working navigation and formatting |
| 4 | **Fast CI** — `meta`, `affected.py`, native tests, changed builds, docs build, `gate` | 1, 2 | PRs verified in minutes |
| 5 | **Pilot 1.3 end-to-end** — full code, tests, diagram, report, evidence, simulation | 2-4 | The template and workflow validated on a real homework |
| 6 | **Simulation** — spike (Wokwi/Velxio/Fritzing), ADR 0004, `simulate.py`, PR/nightly sim jobs, fallback ladder | 5 | Reproducible simulation evidence |
| 7 | **Docs site** — `mkdocs.yml`, literate-nav, gen-files report embedding, board pages, Pages deploy | 2, 4 | Public site generated from the same metadata |
| 8 | **Scale-out** — ESP-IDF adapter/template, remaining skills, HIL workflow, full nightly, sharding | 5-7 | 30+ homeworks at 2-3/week |

**Critical path:** 0 → 1 → 2 → 4 → 5. Documentation (7) can proceed in parallel with simulation (6) once metadata generation is stable. Do not start scale-out before the pilot closes the loop.

---

## Confidence Assessment

| Area | Confidence | Reason |
|------|------------|--------|
| Repository structure | HIGH | Standard PlatformIO project model and lib layout verified in official docs; monorepo pattern is well established |
| Ports & adapters | HIGH | Multiple authoritative sources (Stubert, Grenning, Beningo) plus vendor layering (AUTOSAR, Zephyr, ESP-IDF, STM32Cube) converge |
| Tooling / clangd | MEDIUM | `compile_commands.json` and `compiledb` verified; multi-root per-folder limitation comes from issue/PR reports, not official PlatformIO docs |
| Metadata generation | HIGH | Deterministic generation is a design decision; MkDocs literate-nav/gen-files mechanics verified |
| CI architecture | HIGH | GitHub Actions official docs + PlatformIO official CI docs + established monorepo patterns |
| Simulation | MEDIUM | Wokwi CLI/action/quota verified from docs; Velxio maturity and long-term quota fit unverified |
| Testing | HIGH | PlatformIO unit-test docs verified; test pyramid consensus across sources |
| `lib_extra_dirs` migration | MEDIUM | Official deprecation notice confirmed; relative-path semantics and edge cases not fully documented |

## Open Questions

- Does `extends` across `extra_configs` resolve relative `symlink://` paths from the project directory or the config file? Verify in Phase 1 before generating 30 projects.
- Wokwi plan choice: Hobby (200 min/30 days) is tight for a full weekly suite; confirm actual simulated seconds per homework and either reduce cadence or budget for Pro.
- Velxio feature parity and self-hosting cost — belongs to the simulation spike (ADR-0004).
- Whether the VS Code Wokwi extension can open `assets/diagram.json` directly in the current version; otherwise the generated root copy is required.
- STM32 board models are still unconfirmed; board profiles and the STM32 template wait for hardware confirmation.
- `vscode-clangd` multi-root support may land; if it does, per-folder `clangd.arguments` becomes viable and the `.clangd` approach remains a compatible fallback.

## Sources

- PlatformIO docs — `lib_extra_dirs` (deprecation notice, storage-directory semantics): https://docs.platformio.org/en/latest/projectconf/sections/env/options/library/lib_extra_dirs.html — MEDIUM
- PlatformIO docs — compilation database / `compiledb` target: https://docs.platformio.org/en/latest/integration/compile_commands.html — MEDIUM
- PlatformIO docs — unit testing structure, `test_dir`, `test_build_src` (NOT RECOMMENDED), `test_filter`: https://docs.platformio.org/en/latest/advanced/unit-testing/structure/shared-code.html — MEDIUM
- PlatformIO docs — GitHub Actions CI and caching: https://docs.platformio.org/en/latest/integration/ci/github-actions.html — MEDIUM
- PlatformIO docs — `pio project config`, `default_envs`, environment variables: https://docs.platformio.org/en/latest/core/userguide/project/cmd_config.html — MEDIUM
- Wokwi docs — CI/GitHub Actions, CLI options, `--diagram-file`, `--timeout`: https://docs.wokwi.com/wokwi-ci/getting-started — MEDIUM
- Wokwi docs — diagram format and supported boards (ESP32-S3 DevKitC-1): https://docs.wokwi.com/diagram-format — MEDIUM
- Wokwi pricing/CI quotas: https://wokwi.com/pricing — MEDIUM (verify before committing to a plan)
- MkDocs Material — navigation features: https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/ — MEDIUM
- mkdocs-literate-nav — `SUMMARY.md` nav, wildcards, "supplants awesome-pages": https://oprypin.github.io/mkdocs-literate-nav/ — MEDIUM
- mkdocs-gen-files / `build_literate_nav` — programmatic pages and nav — MEDIUM
- clangd VS Code multi-root issue and `.clangd` `CompilationDatabase`: https://github.com/clangd/vscode-clangd/issues/705 — LOW-MEDIUM
- dorny/paths-filter — changed-filter JSON output and matrix wiring: https://github.com/dorny/paths-filter — MEDIUM
- GitHub Docs — secure use of Actions, least privilege, `pull_request_target`: https://docs.github.com/en/actions/reference/security/secure-use — HIGH
- GitHub Docs — custom Pages workflows; `actions/deploy-pages` permissions: https://docs.github.com/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages — HIGH
- Burkhard Stubert — ports-and-adapters for embedded (ASR-7 I/O-free core, ASR-8 outside depends on inside): https://www.smallstepsystems.com/ports-and-adapters-architecture-the-pattern/ — MEDIUM
- Grenning — SOLID Design for Embedded C (DIP via function pointers): https://wingman-sw.com/papers/SOLIDInC.grenning.v1r0.pdf — MEDIUM
- Beningo — hardware abstraction layers in C: https://www.beningo.com/how-to-write-epic-hardware-abstraction-layers-hal-in-c/ — MEDIUM
- AUTOSAR — Layered Software Architecture (R22-11): https://autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_EXP_LayeredSoftwareArchitecture.pdf — HIGH
- ESP-IDF — Hardware Abstraction (LL/HAL/driver layering): https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/hardware-abstraction.html — HIGH
- STM32Cube — HAL2 architecture and UM2298 BSP guidelines: https://dev.st.com/stm32cube-docs/embedded-software/2.2.0/en/architecture/hal2-architecture.html — HIGH
- Zephyr — devicetree-driven device model (ZDS/ELC material): https://static.sched.com/hosted_files/osseu2025/aa/Linz-K%C3%A4stner-Devicetree-Similarities-and-Differences-OSSE25-ZDS.pdf — MEDIUM
- Embedded test pyramid / simulation vs HIL: https://veecle.ai/blog/simulation-vs-hil-what-belongs-in-ci and https://sigilipelli.github.io/embedded-mastery-path/level-4/05-hil-testing-ci/ — LOW-MEDIUM
- BabbleSim `native_simulator` design — deterministic simulated time: https://github.com/BabbleSim/native_simulator/blob/main/docs/Design.md — MEDIUM
- AGENTS.md format and nested-file guidance: https://agents.md/ — MEDIUM

---

*Architecture research for: embedded engineering course monorepo (PlatformIO, 30+ homeworks)*
*Researched: 2026-10-23*
