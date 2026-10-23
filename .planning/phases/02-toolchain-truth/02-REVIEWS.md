---
phase: 2
reviewers: [codex, antigravity]
reviewed_at: 2026-10-23T22:15:00Z
plans_reviewed: [02-01-PLAN.md, 02-02-PLAN.md, 02-03-PLAN.md, 02-04-PLAN.md, 02-05-PLAN.md]
models:
  codex: "glm-5.3-flash:cloud (reasoning=high)"
  antigravity: "gemini-3.8-flash-high"
model_sources:
  codex: "pinned"
  antigravity: "pinned"
---

# Cross-AI Plan Review — Phase 2

<!-- gsd:plan-revision-conflicts:begin -->
## Plan-Revision Conflicts
<!-- gsd:plan-revision-conflicts:end -->

## Codex Review

## Cross-AI Plan Review Request

You are reviewing implementation plans for a software project phase.
Provide structured feedback on plan quality, completeness, and risks.

## Project Context
# Homeworks — Embedded Engineering Course

## What This Is

A public GitHub monorepo for 30+ homework assignments from an embedded engineering
course. Each homework is an independent PlatformIO project containing code, tests, an
academic report in Markdown, wiring diagrams, a bill of materials, engineering
calculations, and measured evidence. The repository also provides shared portable
libraries, central documentation, templates, deterministic scripts, CI, and a MkDocs
site generated from the same metadata.

## Core Value

Every homework ships as a self-contained, reproducible, industry-standard engineering
artifact — code, evidence, and report — that can be understood and verified a year later.

## Requirements

### Validated

(None yet — ship to validate)

### Active

**Repository and tooling**

- [ ] Monorepo with one independent PlatformIO project per homework under `homeworks/`.
- [ ] Shared libraries in `lib/` (`common`, `port`, `arduino`, `espidf`, `host`) consumed
      through `lib_deps = <name>=symlink://../../lib/<name>` with a `library.json` per
      library and a generated `platformio.shared.ini`; `lib_extra_dirs` remains a
      generator fallback only.
- [ ] Toolchain is pinned: PlatformIO Core 6.2.0, `platformio/espressif32` 8.0.0, and
      explicit ESP32-S3-DevKitC-1 N16R8 overrides (16 MB flash, octal PSRAM).
- [ ] Homework directories named `module_lesson-name`, e.g. `1_3-police-flasher`.
- [ ] Multi-root VS Code workspace containing `repo`, `docs`, `lib`, `scripts`, and each
      homework; generated from metadata and committed.
- [ ] `AGENTS.md` as the canonical rulebook (up to ~300 lines) with enforcement tags,
      short good/bad examples, and an agent quick-start; `.claude/CLAUDE.md` imports it.
- [ ] `docs/` organized into `boards/`, `protocols/`, `components/`, `theory/`,
      `standards/`, `decisions/`, and `sources.md`.

**Homework artifacts**

- [ ] Every homework contains `task.md` (English paraphrase + source), `homework.yaml`
      (validated metadata), `README.md` (academic report), `assets/`, code, and tests.
- [ ] `homework.yaml` is validated by a JSON Schema and records identity, board,
      framework, language, simulation, tests, report, assets, status, and source.
- [ ] Reports use the 10-section academic structure: title/metadata, objective,
      assumptions, theory, hardware and wiring, methodology, results, analysis
      (including industry notes), conclusions, and IEEE references.
- [ ] Reports include a BOM, pin map, electrical calculations, safety checklist,
      measurements, a traceability matrix, and explicit assumptions.
- [ ] All repository artifacts are written in English; communication with the user is
      in the user's language.

**Workflow and skills**

- [ ] Seven project-local skills at version 0.1: `new-homework`, `hw-build`, `hw-flash`,
      `hw-report`, `schematic`, `simulate`, and `course-index`.
- [ ] `new-homework` and `hw-build` are fully implemented first; the remaining skills are
      thin stubs promoted after first real use.
- [ ] `new-homework` supports guided and one-shot modes with an adaptive question bank.
- [ ] Guided mode follows explanation → code → run → questions at block granularity and
      deepens explanations when the user is stuck.
- [ ] Checkpoints occur after intake, after code, and after the report; guardrails for
      flashing, commit/PR, spec-vs-best-practice conflicts, and ambiguity apply in both
      modes.
- [ ] A failing build is fixed automatically at most twice, then explained and escalated.
- [ ] Skills carry a changelog and lessons-learned section updated after each use.

**Architecture**

- [ ] Thin `core` + `port` + adapters architecture; no universal HAL over Arduino and
      ESP-IDF.
- [ ] `lib/common` and `lib/port` contain no framework-specific headers; the dependency
      rule is enforced in CI.
- [ ] Arduino code is idiomatic C++ with minimal STL; ESP-IDF code is C11; shared logic
      is pure C with `extern "C"` headers.
- [ ] Reusable drivers abstract the bus (I2C/SPI), not the whole driver.
- [ ] Both `framework = arduino` and `framework = espidf` are supported through separate

## Phase 2: Toolchain Truth
### Roadmap Section
### Phase

## 02-01

**Summary**

02-01 is a strong tracer. It correctly carries the amended D-15 (`src/main.cpp`, three branches, pure-C library sources with `extern "C"` guards), the amended D-21 ADR-number implication by not touching ADRs, D-22 PSRAM behavior, and the cheap native-first build order. It also correctly avoids importing the SCons-only `compiledb.py` module in tests. The executable slice lines up well with ARCH-04 and the research findings.

**Strengths**

- The entry-point treatment is now correct: `02-01-PLAN.md:199-205` requires `.cpp`, `extern "C" app_main`, and a `#else` host `main()`, avoiding the reproduced Arduino linker failure described in the research.
- The native-first ordering is valuable: `02-01-PLAN.md:121-123` explicitly isolates symlink/manifest errors from toolchain/package errors before spending ~1.5 GB on ESP packages.
- `extra_scripts` is deliberately deferred until after `scripts/pio/compiledb.py` exists, avoiding a first `pio run` failure on a missing script (`02-01-PLAN.md:176-177`, `02-01-PLAN.md:254-257`).
- The test design for the SCons hook is correct: `02-01-PLAN.md:258-266` avoids importing `scripts/pio/compiledb.py` because the top-level `Import("env")` is undefined outside SCons.
- The native CDB check verifies actual compile participation, not just configuration text (`02-01-PLAN.md:272-275`).

**Concerns**

- **MEDIUM — `main.cpp` may still need `#include <stdio.h>` explicitly.** `02-01-PLAN.md:202-204` requires calling `printf`, but the action only names `_Z"stdio`include `"common.h"` and `"port.h"`; the `#include <stdio.h>` comes from the research example, not the action. Make it explicit to avoid an executor discrepancy.
- **MEDIUM — shared config contract is under-tested at this stage.** The plan tests manifests and hook wiring (`02-01-PLAN.md:258-266`), but acceptance criteria also demand exactly three named sections, no `[env:]`, no `lib_extra_dirs`, and the D-22 flag (`02-01-PLAN.md:225-227`). Those criteria are not yet automated in this plan.
- **LOW — runtime version strings duplicate library metadata.** `02-01-PLAN.md:188-190` says each `.c` returns `"0.1.0"` while D-12 says the version lives only in `library.json`. This is likely test scaffolding, but the plan should avoid calling it a version source or should document it as a non-authoritative build ID.
- **LOW — native dependency proof could be stronger.** It calls `common_version()` and the corresponding adapter, but `port_version()` is not explicitly called (`02-01-PLAN.md:202-204`). Compilation may still occur, but calling all three native symbols makes the smoke proof stronger.

**Suggestions**

- Add a small static/data-level test for `platformio.shared.ini` here: exactly the three named sections, required pinned values, absence of `[env:]` and `lib_extra_dirs`, and presence of `-DBOARD_HAS_PSRAM` plus `extra_scripts`.
- Explicitly add `#include <stdio.h>` or `#include <cstdio>` to the `main.cpp` instructions.
- Rename the runtime accessor concept to “build identity” or explicitly state that `library.json` remains the sole declared authoritative version while the C string is only a linker-exercising fixture.
- Broaden the absolute-path guard beyond `/Users/` and `C:\`, using a simple absolute-path syntax check.

**Risk Assessment**

**LOW-to-MEDIUM.** The design is correct and the native slice is cheap. Risks are mostly incomplete machine assertions rather than wrong architecture or dependency ordering.

---

## 02-02

**Summary**

02-02 addresses a real, concrete hygiene gap: ESP-IDF creates files in the project tree that the current ignore rules do not cover. The two-layer design of `.gitignore` plus the existing `no-generated-files` hook is appropriate. However, the proposed `sdkconfig.*` pattern is dangerously overbroad and will also ignore the required authored `sdkconfig.defaults` introduced by plan 02-04.

**Strengths**

- The current gap is real. `.gitignore:8-13` still only ignores `sdkconfig.old`, `sdkconfig.old.*`, and `managed_components/`; `compile_commands.json` and `.pio/` are already ignored (`*.gitignore:15-18`).
- The test contract is already based on `git check-ignore`, not text matching (`scripts/tests/test_gitignore.py:14-18`, `47-54`), so plan 02-02 extends the right mechanism.
- The pre-commit hook correctly catches tracked-but-ignored paths, defending against `git add -f` beyond what `.gitignore` does (`.pre-commit-config.yaml:19-34`).
- The plan explicitly prevents weakening the bare `sdkconfig` visibility rule (`02-02-PLAN.md:101-104`, `47-50`).

**Concerns**

- **HIGH — `sdkconfig.*` will ignore `sdkconfig.defaults`.** Plan 02-04 requires `homeworks/0_0-toolchain-smoke/sdkconfig.defaults` as a tracked source artifact (`02-04-PLAN.md:7-10`, `31-33`, `117-118`). But git globbing semantics mean `sdkconfig.*` matches `sdkconfig.defaults` just as it matches `sdkconfig.esp32s3_espidf`. As written, 02-02 both (a) tells the executor to track `sdkconfig.defaults`, and (b) creates an ignore rule and hook pathspec that will block it. This is an execution contradiction, not just a style issue.
- **MEDIUM — the existing VISIBLE contract is insufficient for this flaw.** `scripts/tests/test_gitignore.py:122-126` keeps bare `sdkconfig` visible, and plan 02-02 preserves that (`02-02-PLAN.md:111-122`). It does not add `sdkconfig.defaults` to `VISIBLE`, so the exact failure will slip through the planned tests.
- **MEDIUM — `CMakeLists.txt` is repo-wide and may hide future authored CMake.** Plan 02-02 chooses a bare, slash-free `CMakeLists.txt` pattern (`02-02-PLAN.md:101-102`). That is convenient for the temporary ESP-IDF smoke project but makes any future intentional CMake source an ignored path. Scoped patterns for `homeworks/0_0-toolchain-smoke/` would be safer.
- **LOW — requirements tag is questionable.** `02-02-PLAN.md:12` tags this with `FOUND-09`, but it is really D-23/generated-file hygiene rather than the toolchain-pin requirement itself.

**Suggestions**

- Replace `sdkconfig.*` with an exact env-specific pattern such as `sdkconfig.esp32s3_espidf`, or use a precise negative exemption immediately after a broad pattern, e.g. `!sdkconfig.defaults`.
- Add `homeworks/0_0-toolchain-smoke/sdkconfig.defaults` to `VISIBLE` in `scripts/tests/test_gitignore.py` and assert `git check-ignore` returns non-zero for it.
- Update the existing `.gitignore` comment so it explicitly distinguishes bare `sdkconfig`, authored `sdkconfig.defaults`, and generated `sdkconfig.<env>`.
- Prefer scoped ignore patterns for the temporary smoke project rather than a repository-wide `CMakeLists.txt` pattern.
- Convert `git ls-files -ci --exclude-standard -- ...` verification into `test -z "$(…)"` so an unexpected tracked path fails automatically rather than relying on the reviewer reading output (`02-02-PLAN.md:154-158`).

**Risk Assessment**

**MEDIUM-to-HIGH until the `sdkconfig.defaults` bug is fixed.** The plan catches an important real gap, but as written it makes one required source artifact impossible to commit normally and will likely fail the very hook it creates.

---

## 02-03

**Summary**

02-03 is the critical proof for the Arduino-side N16R8 configuration and CDB participation. It correctly adds only `extends` and `lib_deps` to the project environment, uses artifact-level evidence rather than trusting `platformio.ini`, and handles `qio_opi`, partition selection, and `BOARD_HAS_PSRAM` specifically. This is well aligned with the research.

**Strengths**

- The environment shape correctly avoids the `extends` list-replacement trap: `02-03-PLAN.md:101-106` requires only `extends` and `lib_deps`, matching the confirmed behavior that `extends` replaces rather than merges lists.
- Evidence is correctly artifact-based: CDB tokens for `qio_opi/include`, `ARDUINO_PARTITION_default_16MB`, and `BOARD_HAS_PSRAM`, plus `esptool image-info` for flash size (`02-03-PLAN.md:149-169`).
- The plan explicitly forbids silently substituting `espressif32@8.0.0` with 7.x or pioarduino (`02-03-PLAN.md:51-54`, `108-113`).
- I verified the pinned environment locally: `pio --version` reports `PlatformIO Core, version 6.2.0`, and `pio pkg show platformio/espressif32` reports version `8.0.0`.

**Concerns**

- **MEDIUM — “all entries” is not actually asserted.** The truth statement says `qio_opi`, partition, and `BOARD_HAS_PSRAM` are in all TU records (`02-03-PLAN.md:22`), but the verify only greps for their presence (`02-03-PLAN.md:164-165`). A Python-count assert over `compile_commands.json` would match the stated guarantee.
- **MEDIUM — `src/main.cpp` is required in prose but not in the automated CDB check.** `02-03-PLAN.md:153` says it must be present, but the automated check only checks the three library sources (`02-03-PLAN.md:166-167`). Add a grep or JSON-source assertion for `src/main.cpp`.
- **LOW — Task 2’s `files` field is misleading.** It lists `homeworks/0_0-toolchain-smoke/platformio.ini` (`02-03-PLAN.md:138`), but Task 2 modifies no source file; it only generates and reads evidence.
- **LOW — direct `esptool` path is less portable than `pio pkg exec`.** The hardcoded `~/.platformio/packages/tool-esptool/esptool` works here, but a PlatformIO-mediated command would be more portable across machines.

**Suggestions**

- Replace presence-only greps with Python assertions over the CDB: required source files, token counts, and optionally total entry counts.
- Assert `src/main.cpp` in the Arduino CDB.
- Use `pio pkg exec` or a documented esptool path resolution helper where practical.
- In Task 2, either omit the source-file `files` field or mark it as evidence-only.

**Risk Assessment**

**LOW-to-MEDIUM.** The architecture and evidence path are correct. This plan mainly needs stronger automated assertions and minor metadata cleanup.

---

## 02-04

**Summary**

02-04 correctly addresses the ESP-IDF-specific failure modes: the missing project-local `default_16MB.csv` and the Kconfig-level flash/PSRAM settings. Its evidence method is strong: read generated `sdkconfig.json`, inspect CDB contents immediately after generation, and verify generated files stay ignored. It depends correctly on the earlier hygiene plan.

**Strengths**

- The project-local partition and `sdkconfig.defaults` are justified precisely: plan 02-04 requires their project-root location and exact three Kconfig lines (`02-04-PLAN.md:112-119`), matching the reproduced ESP-IDF failure in the research.
- The ESP-IDF evidence is based on the actual generated config, not the `16MB Flash` build banner (`02-04-PLAN.md:156-160`).
- The CDB check verifies the three shared sources after the correct ESP-IDF environment (`02-04-PLAN.md:161-178`), satisfying criterion 4 for the second framework.
- The dependency on 02-02 is appropriate because plan 02-04 relies on generated ESP-IDF files remaining ignored (`02-04-PLAN.md:6`, `109`).

**Concerns**

- **HIGH — the same `sdkconfig.*` bug also affects this plan.** This plan’s own required tracked source artifact is `sdkconfig.defaults` (`02-04-PLAN.md:8-10`, `117-118`), while 02-02 ignores `sdkconfig.*` (`02-02-PLAN.md:101-104`). Without an exemption, this environment cannot build and ship the intended default file cleanly.
- **MEDIUM — `src/main.cpp` is again prose-only evidence.** `02-04-PLAN.md:161-164` says the ESP-IDF CDB must include it, but the automated verify checks only the three library sources (`02-04-PLAN.md:177-178`).
- **MEDIUM — no ESP-IDF `esptool image-info` is included.** For the Arduino side, plan 03 uses image-level flash-size evidence. For ESP-IDF, plan 04 relies only on `sdkconfig.json`. That may be defensible, but adding `esptool image-info` on the IDF firmware would make criterion 2 uniformly artifact-level.
- **LOW — Task 2’s `files` field again lists a file it does not modify.** `02-04-PLAN.md:148` lists `platformio.ini`, but the task only proves artifacts.

**Suggestions**

- Block 02-04 execution until `sdkconfig.defaults` is guaranteed visible; include it in `VISIBLE` and a `git check-ignore` negative test.
- Add an automated CDB assertion for `src/main.cpp`.
- Add `esptool --chip esp32s3 image-info` for the ESP-IDF firmware and record both `Flash size` and the relevant sdkconfig values.
- Use `test -z` around `git ls-files -ci` instead of only checking for printed output manually (`02-04-PLAN.md:179-182`).

**Risk Assessment**

**MEDIUM-to-HIGH** because of the `sdkconfig.*` contradiction. The ESP-IDF design itself is otherwise solid and correctly scoped.

---

## 02-05

**Summary**

02-05 is the right final phase gate: ADR-0007, status-index update, all three builds, CDB checks, repository tests, pre-commit, and hygiene. It has the right intent and good ordering. However, it under-verifies criterion 2 in the final gate and includes one human-check command that contradicts its own artifact plan.

**Strengths**

- ADR-0007 is the correct amended number. The existing index indeed has 0006 and reserves 0007 (`docs/decisions/README.md:20-31`), and the structural contract enforced by `scripts/tests/test_adrs.py` is real (`scripts/tests/test_adrs.py:36-45`).
- The plan requires a real final gate: all three builds, three CDB checks, full unittest discovery, policy/template checks, and pre-commit (`02-05-PLAN.md:163-190`).
- The human-check for D-03 correctly distinguishes “consumption proven” from generation (`02-05-PLAN.md:194-198`).
- The ADR structure requirements match the actual MADR contract (`scripts/tests/test_adrs.py:36-45`, `219-241`).

**Concerns**

- **HIGH — the final gate does not rerun the two criterion-2 checks.** `.planning/phases/02-toolchain-truth/02-VALIDATION.md:35-36` says the pre-verification phase gate should include full builds, CDB assertions, and `esptool image-info: 16MB`. Plan 02-05 verifies builds and CDB (`02-05-PLAN.md:181-189`), but its automated checks omit both `esptool image-info` and the ESP-IDF `sdkconfig.json` assertions. It merely says the SUMMARY must contain those values (`02-05-PLAN.md:177-179`). This is a phase-evidence gap.
- **MEDIUM — the D-03 human check conflicts with planned content.** Plan 02-05 says `grep -rn 'platformio.shared.ini' scripts/` should not show an entry (`02-05-PLAN.md:194-198`). But plan 02-01 explicitly creates `scripts/tests/test_pio_scripts.py` that mentions `platformio.shared.ini` when checking hook wiring (`02-01-PLAN.md:258-266`, `303-307`). The proposed grep will therefore return matches. It must search for writing/creation semantics, not any mention.
- **MEDIUM — final git hygiene does not directly test tracked-but-ignored artifacts.** `git status --porcelain` will not show ignored files by default (`02-05-PLAN.md:174-176`, `192`). Plan 04 already has the right idea with `git ls-files -ci --exclude-standard` (`02-04-PLAN.md:179-182`); plan 05 should repeat that final check.
- **LOW — final pin proof could be explicit.** The final gate reruns builds, but it does not rerun `pio --version` and `pio pkg show` directly. This is acceptable if the summaries are trusted, but the final phase gate is stronger with both commands.

**Suggestions**

- Add final automated checks:
  1. `esptool --chip esp32s3 image-info …/esp32s3_arduino/firmware.bin | grep -q 'Flash size: 16MB'`
  2. Python assertions over `.pio/build/esp32s3_espidf/config/sdkconfig.json` for `flashsize_16MB = true`, `SPIRAM_MODE_OCT = true`, and `SPIRAM_MODE_QUAD = false`.
    3. Possibly also inspect the ESP-IDF firmware image.
- Rewrite the D-03 human check as a bounded source audit: verify no committed script opens/writes/creates `platformio.shared.ini`, not merely that no script mentions its name.
- Run final `git ls-files -ci --exclude-standard -- compile_commands.json site .pio CMakeLists.txt 'sdkconfig.*'` and fail if non-empty; remember to first fix the `sdkconfig.defaults` exemption.
- Add explicit `pio --version` and `pio pkg show platformio/espressif32` checks to the final gate.
- Confirm new ADR and smoke README text are in English, per `AGENTS.md:11-14`, which says repository artifacts are English.

**Risk Assessment**

**HIGH until amended.** The phase can still execute, but its final gate would rely on earlier transient summaries for a core requirement and its proposed D-03 audit command is already contradicted by an intended test file. Both are small, specific fixes, but they materially affect the evidence contract.

---

## Cross-plan observations

**Dependency and waves are otherwise sound.** 02-01 and 02-02 can run independently in Wave 1 without file conflicts; 02-03 correctly depends on 02-01, 02-04 depends on all preceding implementation plans, and 02-05 closes the phase.

**The most important fix is in 02-02.** The broad `sdkconfig.*` pattern will ignore the authored `sdkconfig.defaults` required by 02-04. This creates a cross-plan contradiction and may block the final pre-commit gate.

**Coverage is complete across the four phase success criteria.** Criterion 1 is covered by builds across 02-01/02-03/02-04; criterion 2 by Arduino image evidence and IDF sdkconfig evidence; criterion 3 by symlink consumption, manifests, and manual-authored shared-config evidence; criterion 4 by CDB checks in both ESP frameworks.

**One language note:** `AGENTS.md:11-14` requires repository artifacts to be English. The reviewed plan and research files contain substantial Ukrainian prose while the user/context decisions are English. If `.planning/**` remains tracked in this public repo, translate or normalize planning artifacts before merge, or explicitly decide that `.planning/` is excluded from that rule.

## Overall Risk

**HIGH before the two corrections below, LOW-to-MEDIUM afterward.**

Required fixes:

1. Fix 02-02 so `sdkconfig.defaults` remains visible and the pre-commit hook does not treat it as generated.
2. Add final automated artifact checks for `esptool image-info` and ESP-IDF `sdkconfig.json` in 02-05.

---

## Antigravity Review

# Phase 2 Plan Review: Toolchain Truth

Review of implementation plans `02-01-PLAN.md` through `02-05-PLAN.md` for Phase 2 ("Toolchain Truth"), verified against codebase state and rules at `/Users/vloktiev/Dev/miltech/homeworks`.

---

## 02-01

### 1. Summary
Plan `02-01` establishes the foundational tracer for Phase 2: a hand-authored root `platformio.shared.ini`, five shared library stubs with `library.json` manifests, the temporary smoke project `homeworks/0_0-toolchain-smoke/`, and an initial green native build (`pio run -e native`). It also adds the SCons pre-script `scripts/pio/compiledb.py` and its AST-based test `scripts/tests/test_pio_scripts.py`. The design is well-isolated and prioritizes early validation of the `symlink://` resolution mechanism before invoking heavy cross-compilation toolchains. However, an error in the automated verification command for Task 1 will cause immediate failure during execution.

### 2. Strengths
- **Fast tracer loop**: Verifies `symlink://` package discovery, library linking, and LDF behavior with `pio run -e native` (`.planning/phases/02-toolchain-truth/02-01-PLAN.md:121-123`) before incurring the ~1.5 GB download of `platformio/espressif32` 8.0.0.
- **Task sequencing defensively decoupled**: Task 1 creates `platformio.shared.ini` without `extra_scripts` (`.planning/phases/02-toolchain-truth/02-01-PLAN.md:176-177`), ensuring the initial native build does not fail on a missing SCons script before Task 2 authors `scripts/pio/compiledb.py`.
- **AST testing for SCons hooks**: In `scripts/tests/test_pio_scripts.py` (`.planning/phases/02-toolchain-truth/02-01-PLAN.md:258-266`), the test parses `compiledb.py` via `ast.parse` rather than importing it, preventing `NameError` on SCons's global `Import("env")`.
- **C/C++ boundary hygiene**: Complies with amended D-15 by wrapping all public headers in `#ifdef __cplusplus / extern "C"` (`.planning/phases/02-toolchain-truth/02-01-PLAN.md:42, 183-187`), ensuring clean linkage between the `.cpp` entry point and pure `.c` library implementations.

### 3. Concerns
- **[HIGH] Broken automated verification command in Task 1** (`.planning/phases/02-toolchain-truth/02-01-PLAN.md:221`):
  Task 1 verification executes:
  ```python
  python3 -c "import pathlib,sys; h=[pathlib.Path('lib',n,'include',f'{n}.h') for n in ['common','port','arduino','espidf','host']]; bad=[str(p) for p in h if 'extern \"C\"' not in p.read_text()]; print('missing extern C:',bad); sys.exit(1 if bad else 0)"
  ```
  The files created in Task 1 (`.planning/phases/02-toolchain-truth/02-01-PLAN.md:18-22, 184`) are `arduino_adapter.h` and `espidf_adapter.h`, not `arduino.h` and `espidf.h`. When `p.read_text()` tries to read `lib/arduino/include/arduino.h`, Python raises `FileNotFoundError: [Errno 2] No such file or directory: 'lib/arduino/include/arduino.h'`, halting automated execution.
- **[MEDIUM] Flag diagnostic noise in native build** (`.planning/phases/02-toolchain-truth/02-01-PLAN.md:170, 213-216`):
  `[native_unity]` defines `build_flags = -std=c11 -Wall -Wextra`. Because `src/main.cpp` is C++, `g++` receives `-std=c11` and outputs `warning: command-line option '-std=c11' is valid for C/ObjC but not for C++`. While non-fatal without `-Werror`, passing C-specific standard flags to a C++ translation unit pollutes compiler output.
- **[LOW] Large file surface in single task** (`.planning/phases/02-toolchain-truth/02-01-PLAN.md:161-164`):
  Task 1 modifies/creates 19 files across 6 directory hierarchies. Although the files are minimal stubs, any single syntax error across the manifests or headers complicates rollback.

### 4. Suggestions
- Update the verification command in `.planning/phases/02-toolchain-truth/02-01-PLAN.md:221` to inspect actual header names:
  ```python
  python3 -c "import pathlib,sys; bad=[str(p) for p in pathlib.Path('lib').glob('*/include/*.h') if 'extern \"C\"' not in p.read_text()]; print('missing extern C:',bad); sys.exit(1 if bad else 0)"
  ```
- Replace `-std=c11` in `[native_unity]` `build_flags` with a toolchain-appropriate C/C++ configuration (or defer `-std=c11` to pure C compilation flags via `build_src_flags`).

### 5. Risk Assessment
- **Risk Level**: MEDIUM
- **Justification**: The build and linkage architecture is sound and thoroughly researched, but the automated test script in Task 1 will deterministically crash on `FileNotFoundError`, requiring manual developer intervention during execution.

---

## 02-02

### 1. Summary
Plan `02-02` updates repository hygiene for ESP-IDF generated files. It expands `.gitignore`, updates the `no-generated-files` pre-commit hook in `.pre-commit-config.yaml`, and extends contract tests in `scripts/tests/test_gitignore.py`. While the dual-layer protection (`.gitignore` + `git ls-files -ci` hook) correctly enforces the repository's rule that generated files are never committed, the plan introduces a severe glob collision with `sdkconfig.*` that breaks Plan `02-04`.

### 2. Strengths
- **Defense in depth**: Pairs `.gitignore` patterns with the `no-generated-files` pre-commit hook (`.pre-commit-config.yaml:24-34`), preventing developers from bypassing ignore rules via `git add -f` (`.planning/phases/02-toolchain-truth/02-02-PLAN.md:143-150`).
- **Preserves existing test contracts**: Keeps `sdkconfig` in `VISIBLE` (`scripts/tests/test_gitignore.py:124-126`) and adds dedicated tests to verify that bare `sdkconfig` remains un-ignored (`.planning/phases/02-toolchain-truth/02-02-PLAN.md:111-114`).

### 3. Concerns
- **[HIGH] Pattern collision between `sdkconfig.*` and `sdkconfig.defaults`** (`.planning/phases/02-toolchain-truth/02-02-PLAN.md:101-105, 143-145` vs `.planning/phases/02-toolchain-truth/02-04-PLAN.md:9, 117-119`):
  Plan `02-02` introduces the ignore pattern `sdkconfig.*` to suppress `sdkconfig.esp32s3_espidf`. However, `sdkconfig.defaults` (created in Plan `02-04` as a committed configuration source) also matches `sdkconfig.*`. This creates three critical failures in Plan `02-04`:
  1. `git add homeworks/0_0-toolchain-smoke/sdkconfig.defaults` will be blocked by git with an ignored file error.
  2. If forced with `-f`, the `no-generated-files` hook (`git ls-files -ci --exclude-standard -- ... 'sdkconfig.*'`) will flag `sdkconfig.defaults` as a tracked generated file and fail pre-commit.
  3. `scripts/tests/test_gitignore.py` does not include `sdkconfig.defaults` in its `VISIBLE` list (`scripts/tests/test_gitignore.py:100-126`), so `test_gitignore.py` will pass in Plan `02-02` while silently masking this blocker.

### 4. Suggestions
- Add an explicit negation rule immediately after `sdkconfig.*` in `.gitignore`:
  ```gitignore
  sdkconfig.*
  !sdkconfig.defaults
  !sdkconfig.defaults.*
  ```
  Or restrict the pattern to target environment build outputs specifically: `sdkconfig.*_*` or `sdkconfig.esp32*`.
- Add `"homeworks/0_0-toolchain-smoke/sdkconfig.defaults"` to the `VISIBLE` list in `scripts/tests/test_gitignore.py`.

### 5. Risk Assessment
- **Risk Level**: HIGH
- **Justification**: As written, executing Plan `02-02` directly blocks the execution and pre-commit checks of Plan `02-04`.

---

## 02-03

### 1. Summary
Plan `02-03` implements the Arduino environment (`esp32s3_arduino`) on the ESP32-S3 N16R8 target within `homeworks/0_0-toolchain-smoke/platformio.ini`. It verifies toolchain versions (`pio --version` 6.2.0, `platformio/espressif32` 8.0.0), ensures the Arduino build links against `common`, `port`, and `arduino` libraries via `symlink://`, and validates 16 MB flash and octal PSRAM settings directly against build artifacts (`esptool image-info` and `compile_commands.json` tokens).

### 2. Strengths
- **Artifact-level validation**: Adheres strictly to the requirement that configuration intent is proven by build products rather than reading `platformio.ini` (`.planning/phases/02-toolchain-truth/02-03-PLAN.md:149-157`). Validates `Flash size: 16MB` in the image binary and checks compiler define tokens (`qio_opi/include`, `ARDUINO_PARTITION_default_16MB`, `BOARD_HAS_PSRAM`) in `compile_commands.json`.
- **Inheritance preservation**: Confirms that `[env:esp32s3_arduino]` contains only `extends` and `lib_deps` via `configparser` checks (`.planning/phases/02-toolchain-truth/02-03-PLAN.md:121-122`), avoiding accidental overriding of list options from `platformio.shared.ini` (Pitfall P4).
- **Addresses D-22**: Verifies the inclusion of `-DBOARD_HAS_PSRAM` in compilation commands to ensure the Arduino core configures octal PSRAM correctly.

### 3. Concerns
- **[LOW] Hardcoded tool path**:
  Task 2 verification executes `~/.platformio/packages/tool-esptool/esptool` directly (`.planning/phases/02-toolchain-truth/02-03-PLAN.md:154, 168`). While verified present in the local environment (`/Users/vloktiev/.platformio/packages/tool-esptool/esptool`), hardcoding paths under `~/.platformio` will break in environments where `PLATFORMIO_CORE_DIR` is customized or in CI runners.

### 4. Suggestions
- Use `pio pkg exec -p tool-esptool -- esptool` (as noted in research `.planning/phases/02-toolchain-truth/02-RESEARCH.md:1355`) instead of hardcoding `~/.platformio/packages/...`.

### 5. Risk Assessment
- **Risk Level**: LOW
- **Justification**: Highly focused, well-specified verification tasks with clear pass/fail criteria and correct handling of PlatformIO LDF symlink semantics.

---

## 02-04

### 1. Summary
Plan `02-04` integrates the ESP-IDF framework environment (`esp32s3_espidf`) into the reference project. It provides the project-level `default_16MB.csv` partition table and `sdkconfig.defaults` required by the ESP-IDF builder, runs the build, and validates that `sdkconfig.json` reflects 16 MB flash size and octal PSRAM configuration while ensuring the compilation database indexes all shared library sources.

### 2. Strengths
- **Resolves missing partition table gap (Pitfall P3)**: Correctly identifies that ESP-IDF does not ship `default_16MB.csv` within `framework-espidf/components/partition_table/` and places a valid 16 MB partition table in the project directory (`.planning/phases/02-toolchain-truth/02-04-PLAN.md:112-116`).
- **Kconfig integration**: Uses `sdkconfig.defaults` with `CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y`, `CONFIG_SPIRAM=y`, and `CONFIG_SPIRAM_MODE_OCT=y` (`.planning/phases/02-toolchain-truth/02-04-PLAN.md:117-119`), bypassing the limitation where `-D` flags in `build_flags` do not reach ESP-IDF Kconfig.
- **Direct verification of generated configuration**: Validates `.pio/build/esp32s3_espidf/config/sdkconfig.json` using Python assertions (`.planning/phases/02-toolchain-truth/02-04-PLAN.md:175`) to confirm `ESPTOOLPY_FLASHSIZE == "16MB"` and `SPIRAM_MODE_OCT is True`.
- **Clean CDB ordering**: Recognizes that `pio run -t compiledb` overwrites `compile_commands.json` (Pitfall P7) and validates ESP-IDF entries immediately following the build (`.planning/phases/02-toolchain-truth/02-04-PLAN.md:161-164`).

### 3. Concerns
- **[HIGH] Blocked by ignore rules in Plan 02-02**:
  Because Plan `02-02` adds `sdkconfig.*` to `.gitignore` without excluding `sdkconfig.defaults`, committing `homeworks/0_0-toolchain-smoke/sdkconfig.defaults` (`.planning/phases/02-toolchain-truth/02-04-PLAN.md:10, 117-119`) will fail `git add` and fail the pre-commit hook `no-generated-files`.
- **[LOW] Incomplete path check in hygiene verification** (`.planning/phases/02-toolchain-truth/02-04-PLAN.md:181`):
  Task 2 verification runs `git ls-files -ci --exclude-standard -- homeworks/0_0-toolchain-smoke/CMakeLists.txt homeworks/0_0-toolchain-smoke/sdkconfig.esp32s3_espidf`, but omits `homeworks/0_0-toolchain-smoke/src/CMakeLists.txt`, which ESP-IDF also generates in the sub-tree.

### 4. Suggestions
- Require the fix for `sdkconfig.*` in Plan `02-02` before executing Plan `02-04`.
- Include `homeworks/0_0-toolchain-smoke/src/CMakeLists.txt` in the `git ls-files -ci` verification command in Task 2.

### 5. Risk Assessment
- **Risk Level**: HIGH (conditional on Plan 02-02) / LOW (if Plan 02-02 is adjusted)
- **Justification**: The technical ESP-IDF and PlatformIO configuration is accurate and proven by session research, but execution will fail at git commit time due to the ignore pattern conflict from Plan `02-02`.

---

## 02-05

### 1. Summary
Plan `02-05` concludes Phase 2 by drafting and indexing ADR-0007 (`docs/decisions/0007-symlink-shared-libraries.md`), updating `docs/decisions/README.md`, and executing the comprehensive phase gate across all three environments (`native`, `esp32s3_arduino`, `esp32s3_espidf`), compilation databases, repository unit tests, policy checks, and pre-commit hooks.

### 2. Strengths
- **Strict adherence to ADR governance**: Correctly numbers the record as `0007` (fixing the outdated `0006` reference from `02-CONTEXT.md:248-253` because `docs/decisions/0006-public-commit-identity.md` already exists). Follows all MADR 4.0 structural requirements enforced by `scripts/tests/test_adrs.py:28-46`.
- **Comprehensive phase gate**: Task 2 sequences all builds (`native` → `esp32s3_arduino` → `esp32s3_espidf`), validates CDB contents for each target, executes `python3 -m unittest discover -s scripts/tests -v`, runs `python3 scripts/check_policy.py --check` and `python3 scripts/check_pr_templates.py`, and completes with `pre-commit run --all-files` (`.planning/phases/02-toolchain-truth/02-05-PLAN.md:182-193`).
- **Integrity of D-03**: Explicitly enforces human verification that `platformio.shared.ini` was written manually and not generated, correctly deferring generation to Phase 5 (`.planning/phases/02-toolchain-truth/02-05-PLAN.md:194-199`).

### 3. Concerns
- **[LOW] Sensitive next-number grep in verification** (`.planning/phases/02-toolchain-truth/02-05-PLAN.md:137`):
  Verification tests `grep -q 'Next number: \*\*0008\*\*' docs/decisions/README.md`. In `docs/decisions/README.md:31`, the existing line is `Next number: **0007** (reserved for the Phase 2 symlink decision).` If the author includes notes in parentheses, the grep passes, but explicit guidance ensures exact matching.

### 4. Suggestions
- Specify the exact replacement line for `docs/decisions/README.md`: `Next number: **0008**`.

### 5. Risk Assessment
- **Risk Level**: LOW
- **Justification**: Well-structured governance plan backed by automated structural tests and rigorous regression verification.

---

## Cross-Plan Findings & Overall Assessment

### Cross-Plan Defect Summary
1. **Blocker between Plan 02-02 and Plan 02-04**:
   Adding `sdkconfig.*` to `.gitignore` and `no-generated-files` in Plan `02-02` matches `sdkconfig.defaults`, blocking its commit in Plan `02-04`.
   *Remediation*: Update Plan `02-02` to include `!sdkconfig.defaults` in `.gitignore` and add `homeworks/0_0-toolchain-smoke/sdkconfig.defaults` to `VISIBLE` in `scripts/tests/test_gitignore.py`.
2. **Defect in Plan 02-01 verification command**:
   Plan `02-01` Task 1 verification constructs paths with `f'{n}.h'`, which fails on `arduino_adapter.h` and `espidf_adapter.h`.
   *Remediation*: Update `.planning/phases/02-toolchain-truth/02-01-PLAN.md:221` to query actual adapter header paths.

### Goal Coverage
- **Criterion 1 (`pio run` succeeds for native & ESP32-S3 N16R8)**: Covered by Plans 02-01 (native), 02-03 (Arduino), 02-04 (ESP-IDF), and 02-05 (phase gate).
- **Criterion 2 (16 MB flash & octal PSRAM verified by artifacts)**: Covered by Plan 02-03 (`esptool image-info` + `qio_opi` token) and Plan 02-04 (`sdkconfig.json` assert).
- **Criterion 3 (`symlink://` shared libraries + `library.json`)**: Covered by Plan 02-01 (stubs, manifests, native link) and Plan 02-05 (ADR-0007).
- **Criterion 4 (`compiledb` contains shared-library sources for both frameworks)**: Covered by Plans 02-01, 02-03, 02-04, and 02-05.

### Overall Phase Risk: MEDIUM
Once the two concrete defects (the Task 1 header verification command in `02-01` and the `sdkconfig.*` pattern collision in `02-02`) are resolved, the plan suite is ready for execution.

---

## Consensus Summary

Both prompt-fed reviewers (Codex, Antigravity) exercised the repository and cited
`path:line` evidence, so both count at full consensus weight. CodeRabbit was not
selected and no reviewer carried a no-repo-access or no-source-citations marker.

### Agreed Strengths

- **Native-first tracer ordering.** Both reviewers credit 02-01 for proving
  `symlink://` resolution and linking with `pio run -e native` before the
  ~1.5 GB `platformio/espressif32` download (02-01-PLAN.md:121–123).
- **Artifact-level evidence instead of config intent.** Both reviewers highlight
  that 02-03 and 02-04 prove 16 MB flash / octal PSRAM from `esptool image-info`,
  `compile_commands.json` tokens, and generated `sdkconfig.json` rather than by
  re-reading `platformio.ini`.
- **AST-based SCons hook test.** Both note that `scripts/tests/test_pio_scripts.py`
  parses `compiledb.py` with `ast.parse` instead of importing it, avoiding the
  undefined `Import("env")` outside SCons.
- **Correct ADR governance.** Both confirm ADR-0007 is the right next number and
  that the planned record satisfies the MADR structure enforced by
  `scripts/tests/test_adrs.py`.

### Agreed Concerns

1. **HIGH — `sdkconfig.*` collides with `sdkconfig.defaults` (02-02 vs 02-04).**
   Both reviewers independently flag that the proposed `sdkconfig.*` ignore pattern
   in 02-02 also matches the authored `homeworks/0_0-toolchain-smoke/sdkconfig.defaults`
   required by 02-04. Consequences: `git add` refuses the file, `git add -f`
   trips the `no-generated-files` hook, and `scripts/tests/test_gitignore.py`
   does not catch it because `sdkconfig.defaults` is absent from `VISIBLE`.
   Fix: add `!sdkconfig.defaults` (or narrow the pattern to `sdkconfig.esp32*`) and
   add the path to `VISIBLE` in `scripts/tests/test_gitignore.py`.
2. **MEDIUM — `src/main.cpp` is required in prose but not asserted in either CDB
   check (02-03, 02-04).** The verification greps only the three shared-library
   sources; add a JSON/source assertion for `src/main.cpp`.
3. **LOW — hardcoded esptool path.** 02-03 calls
   `~/.platformio/packages/tool-esptool/esptool` directly; both reviewers prefer
   `pio pkg exec -p tool-esptool -- esptool` for portability.

### Divergent Views

- **02-01 Task 1 verification command.** Antigravity rates this HIGH: the check builds
  header paths as `lib/<name>/include/<name>.h`, which does not exist for
  `arduino_adapter.h` / `espidf_adapter.h`, so it dies with `FileNotFoundError`.
  Codex did not flag it. This should be verified directly against the plan text and
  the created file list before execution.
- **02-05 phase-gate risk.** Codex rates HIGH because the final gate does not re-run
  the criterion-2 evidence (`esptool image-info`, `sdkconfig.json` assertions),
  relying instead on earlier summaries; Antigravity rates 02-05 LOW and calls the
  gate comprehensive. Codex also flags that the D-03 audit
  (`grep -rn 'platformio.shared.ini' scripts/`) will match the intended
  `test_pio_scripts.py`, so it must check write/create semantics rather than any
  mention.
- **Repository language rule.** Codex additionally notes that planning artifacts
  contain substantial Ukrainian prose while `AGENTS.md` requires English repository
  artifacts; whether `.planning/**` falls under that rule deserves an explicit
  decision.

### Overall Phase Risk

Both reviewers converge on **MEDIUM-to-HIGH before fixes, LOW-to-MEDIUM after**.
The two corrections that matter most are (1) the `sdkconfig.*` / `sdkconfig.defaults`
collision in 02-02 and (2) the 02-01 Task 1 header-path verification command.
