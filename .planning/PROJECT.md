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
      homework templates.
- [ ] A PlatformIO + export path covers course requirements that mandate another IDE.

**Quality**

- [ ] clang-format 23.1.3 is configured as a documented ESP-IDF approximation (4 spaces,
      120 columns, function brace on a new line), together with clang-tidy (bugprone,
      cert, performance, portability), markdownlint, yamllint, ruff, and gitleaks.
- [ ] esp-clangd (Espressif's LLVM fork) serves the workspace through
      `scripts/clangd-wrapper.sh`, with per-project `.clangd` files and explicit
      `--query-driver` toolchain globs.
- [ ] `scripts/affected.py` maps a git diff to a build/simulation matrix, including
      fanout from `lib/**` changes to every consumer.
- [ ] `scripts/check_architecture.py` and a native compile gate enforce the dependency
      rule.
- [ ] Reports include a measurement ledger labelling every value as measured,
      calculated, simulated, datasheet, or explicitly not measured, with instrument,
      method, uncertainty, and commit hash.
- [ ] Checks are layered: fast hooks in pre-commit, clang-tidy in pre-push, full build and
      tests in CI.
- [ ] Unity tests run on the native environment; shared libraries have a dedicated
      `tests/` PlatformIO project.
- [ ] Testing is tiered: build always; unit tests for pure logic; simulation where
      supported; hardware-in-the-loop when hardware is available.
- [ ] TDD is used for pure logic; hardware behavior is verified by simulation or HIL.
- [ ] CI runs lint, metadata/docs checks, native tests, and builds of changed projects on
      every pull request. Simulation enters CI only after the Phase 5 spike, only for
      changed projects, and never as a required check for fork pull requests. Nightly
      runs the full build and unit-test matrix; full simulation runs weekly if adopted.

**Simulation and diagrams**

- [ ] A full spike measures Wokwi (primary), Velxio (self-hosted fallback), Renode
      (STM32), and Fritzing (illustration) against defined criteria, including a pilot
      simulation of homework 1.3, and records measured minutes and fidelity limits.
- [ ] Spike results are stored in research artifacts and an ADR.
- [ ] `assets/diagram.json` is the source of truth for wiring and simulation.
- [ ] Fritzing SVGs may be used for final report illustrations with attribution; part
      graphics are not copied into shared assets or the docs site, and `diagram.json`
      remains the source of truth.
- [ ] Pinout diagrams are generated from board profiles or linked to official sources.

**Git and publication**

- [ ] `main` is protected; every change goes through a branch and pull request.
- [ ] Conventional Commits; squash merge; tag `hw/<id>` after merge; branches deleted.
- [ ] Three PR templates (`homework`, `infra`, `docs`) with a shared header and
      type-specific checklists; no default template.
- [ ] Git LFS is used only for large, non-diffable binaries; site assets (PNG, JPG, SVG,
      Markdown, YAML, JSON) stay in normal git because GitHub Pages cannot serve LFS
      objects. Videos are linked, not committed.
- [ ] The repository is public under the MIT license.
- [ ] Internal course materials are never committed; assignments are paraphrased in
      English with attribution.
- [ ] A README index and a MkDocs Material 9.7.7 site are generated from `homework.yaml`;
      the configuration stays Zensical-compatible and is re-evaluated in Q1 2027 before
      the 2027-05-05 end-of-life.
- [ ] Infrastructure decisions are recorded as ADRs; homework assumptions are recorded in
      the report.

**Pilot**

- [ ] Homework 1.3 (Police Flasher) is implemented in guided mode with all optional
      extensions: third LED, variable speed, complex pattern, and single-GPIO operation.
- [ ] The pilot validates the template, skill, report, tests, simulation, index, and CI
      end to end.

### Out of Scope

- Raspberry Pi SBC support — unlikely to appear in the course; revisit only if required.
- A universal hardware abstraction layer over Arduino and ESP-IDF — it would hide the
  frameworks the course teaches and become a shadow framework.
- DOCX/PDF report pipeline — Markdown is the single source; PDF can be generated ad hoc.
- Pre-scaffolding all 30+ homework directories — folders are created as assignments
  arrive.
- Grade tracking — the repository records work, not assessments.
- Native ESP-IDF (`idf.py`) as the primary build path — PlatformIO is the single build
  system; native usage is documented for portability.
- Committing internal course materials — copyright and privacy risk in a public
  repository.
- Committing video files — they are linked instead to keep the repository small.
- MISRA C compliance — too heavy for a course; ESP-IDF style plus clang-tidy is the
  agreed quality bar.
- Team collaboration features — assignments are individual.
- Nightly full simulation matrix — free-tier simulation quotas cannot sustain it; use
  changed-only PR simulation and a weekly full run if adopted.
- Git LFS for site assets — GitHub Pages cannot serve LFS objects.
- Copying Fritzing part graphics into shared assets or the docs site — the part library
  license restricts reuse outside Fritzing.

## Context

- The course reveals modules and lessons progressively; there is no complete syllabus at
  the start.
- Assignments are mixed: some have ready specifications, others are free-form.
- Expected pace is 2–3 homeworks per week, with more than 30 over the course.
- Available hardware includes an ESP32-S3-DevKitC-1 (N16R8), several older ESP32 boards,
  Arduino Nano, STM32 boards (models to be confirmed), sensors, components, a multimeter,
  and an oscilloscope.
- ESP32 is the primary platform. Arduino and STM32 may appear. Raspberry Pi is unlikely.
- The user is new to VS Code, so the repository includes an onboarding guide covering
  extensions, tasks, formatting, and clangd.
- Claude Code is the primary agent; Antigravity with Gemini may be used occasionally.
  Core rules therefore live in `AGENTS.md`, and deterministic automation lives in
  scripts so any agent can run it.
- The provided example assignment (Module 1.3) is in Ukrainian; the public repository
  will contain only an English paraphrase and a public source reference.
- The user wants deep, adaptive questioning and industry-standard output rather than
  quick one-shot results.
- Research completed on 2026-10-23 is recorded in `.planning/research/SUMMARY.md`; it
  changes the shared-library mechanism, formatting approximation, language server,
  simulator priority, CI simulation cadence, docs lifecycle, Fritzing licensing, and
  LFS scope.
- The course allows public solutions and does not require AI-assistance disclosure
  (confirmed by the user on 2026-10-23).

## Constraints

- **Language**: User-facing communication follows the user's language; all repository
  artifacts are English.
- **Toolchain**: PlatformIO for every homework, including ESP-IDF projects.
- **Platforms**: ESP32 (Arduino, later ESP-IDF), STM32, and Arduino; Raspberry Pi SBC is
  excluded for now.
- **Scale**: More than 30 homeworks at 2–3 per week; automation and consistency are
  mandatory.
- **Public repository**: Copyright, secrets, and personal data must be handled
  carefully.
- **Simulation**: Simulation without hardware is critical; a full spike is required
  before committing to a tool.
- **Phase size**: Phases must be small, ship a working increment, and avoid speculative
  scaffolding or hundreds of files.
- **Quality bar**: Industry standards and best practices; clang-format and clang-tidy
  are enforced; MISRA is not required.
- **Hardware**: Only the boards and instruments listed in Context are available.
- **Git**: `main` is protected; no direct commits, no force-push, no history rewriting.
- **Spike timebox**: No fixed timebox; the spike runs until the decision is evidence-based.
- **Pinned toolchain**: PlatformIO Core 6.2.0 and espressif32 8.0.0; the N16R8 board
  requires explicit flash/PSRAM overrides.
- **Licensing**: Fritzing part graphics are not redistributed; SVGs used in reports are
  attributed and kept out of shared assets.
- **Assets**: LFS only for large non-diffable binaries; site assets remain normal git
  objects.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Monorepo with independent PlatformIO projects | Isolates dependencies and board configs; each homework is easy to grade and open | — Pending |
| Naming `module_lesson-name` | Preserves course order and conveys topic | — Pending |
| PlatformIO for all homeworks | Single build system, CI, and tooling across platforms | — Pending |
| Arduino uses idiomatic C++; ESP-IDF uses C11; shared logic is C | Idiomatic per framework while keeping logic portable | — Pending |
| Thin core + port + adapters | Reuse without building a shadow framework | — Pending |
| No universal HAL | Hardware abstractions leak; the course must teach framework APIs | — Pending |
| Shared libraries via `lib_deps = <name>=symlink://...` | Replaces deprecated `lib_extra_dirs`; explicit dependency intent; validated locally | — Pending |
| Multi-root VS Code workspace | Per-project clangd and PlatformIO behavior; auxiliary folders available | — Pending |
| esp-clangd + per-project `.clangd` + compiledb | Stock clangd does not understand `-mcpu=esp32s3` and Espressif ISA extensions | — Pending |
| Three-layer checks (pre-commit, pre-push, CI) | Fast local feedback with full verification in CI | — Pending |
| clang-format 120 + clang-tidy (ESP-IDF approximation) | Consistent quality without MISRA overhead; AStyle-based ESP-IDF style is approximated and documented | — Pending |
| 10-section report with BOM, calculations, safety, and industry notes | Academic completeness plus engineering rigor | — Pending |
| `task.md` + `homework.yaml` + `README.md` separation | Separates assignment, metadata, and result | — Pending |
| Unity + native environment | Fast, deterministic tests for pure logic | — Pending |
| Tiered testing | Avoids overhead while keeping evidence proportional to the work | — Pending |
| TDD for pure logic | Improves design and guarantees testability | — Pending |
| Protected `main`, PR, squash merge, tags | Auditable history and a clear entry point per homework | — Pending |
| Three PR templates | Type-specific evidence without a bloated universal template | — Pending |
| Git LFS with limits | Handles large binaries without bloating the repository | — Pending |
| MIT license | Simple public portfolio license | — Pending |
| README index + MkDocs Material | One source of metadata renders both catalog and site | — Pending |
| ADRs for infrastructure, assumptions in reports | Traceable decisions at the right scope | — Pending |
| Wokwi primary, Velxio fallback, Renode for STM32, Fritzing with attribution | Research shows Wokwi has the strongest ESP32 fidelity and CI; Velxio self-host excludes STM32 | — Pending |
| MkDocs Material 9.7.7 with Zensical-compatible config | Stable today; re-evaluate in Q1 2027 before the 2027-05-05 EOL | — Pending |
| Git LFS only for large non-diffable binaries | Pages cannot serve LFS objects; LFS bandwidth is consumed by checkouts | — Pending |
| Pin PlatformIO 6.2.0 and espressif32 8.0.0 | Reproducible builds; 8.0.0 is new and must be smoke-tested | — Pending |
| Pilot 1.3 with all extensions in guided mode | Validates the full workflow before scaling to 30+ homeworks | — Pending |
| Seven thin skills, two fully implemented | Complete inventory without premature design | — Pending |
| Four deterministic scripts | Guarantees consistency for scaffolding, index, workspace, and validation | — Pending |
| Full template set from the first phase | Makes the correct structure the easiest path | — Pending |
| `AGENTS.md` as canonical, imported by `CLAUDE.md` | Portable rules for Claude and Antigravity without duplication | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition**:

1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone**:

1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---

*Last updated: 2026-10-23 after research*
