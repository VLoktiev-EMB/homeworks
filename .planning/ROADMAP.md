# Roadmap: Homeworks — Embedded Engineering Course

## Overview

Build the repository as a policy-gated monorepo of independent PlatformIO projects over a
small, enforced C core, with every repeated artifact generated from one metadata contract.
The journey starts with the irreversible decisions (public history, licensing, assets),
proves the pinned toolchain and shared-library wiring, then adds the shared core, the
metadata contract, developer experience, the simulation spike, fast CI, the agent skills,
and the report system. It closes with homework 1.3 delivered end to end as the reference
artifact before scaling to 30+ homeworks.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Repository Foundation and Policy Gate** - Public history, licensing, asset, and contribution rules that cannot be repaired later (completed 2026-10-23)
- [x] **Phase 2: Toolchain Truth** - Pinned PlatformIO builds for native and ESP32-S3 N16R8 with `symlink://` shared libraries (completed 2026-10-23)
- [x] **Phase 3: Shared Core and Dependency Rule** - Framework-free `common`/`port`, thin adapters, and an enforced native test gate (completed 2026-10-24)
- [ ] **Phase 4: Metadata Contract and Scaffolding** - Schema-validated `homework.yaml`, templates, and a deterministic `new_homework`
- [ ] **Phase 5: Generated Views and Documentation Site** - Index, workspace, shared ini, CI matrix, and MkDocs site generated from metadata
- [ ] **Phase 6: Developer Experience and Quality Layering** - Formatting, clang-tidy, esp-clangd, hooks, and beginner onboarding
- [ ] **Phase 7: Simulation Spike** - Measured Wokwi/Velxio/Renode/Fritzing evidence and ADR-0004
- [ ] **Phase 8: Fast CI** - `meta` + `changes` + changed builds, one required gate, optional simulation
- [ ] **Phase 9: Agent Workflow and Skills** - Seven versioned skills with `new-homework` and `hw-build` fully implemented
- [ ] **Phase 10: Report and Evidence System** - The 10-section report contract, calculations catalog, checks, and self-audit rubric
- [ ] **Phase 11: Pilot Homework 1.3** - Police Flasher delivered end to end with all extensions

## Phase Details

### Phase 1: Repository Foundation and Policy Gate

**Goal**: A public repository whose history, licensing, asset, and contribution rules are safe by construction and cannot be repaired later.
**Depends on**: Nothing (first phase)
**Requirements**: FOUND-02, FOUND-03, FOUND-04, FOUND-05, FOUND-06, FOUND-07, FOUND-08, FOUND-10, TOOL-07
**Success Criteria** (what must be TRUE):
  1. A direct push to `main` is rejected; every change in the history arrives through a branch and a merged pull request.
  2. `gitleaks` blocks a staged secret locally and scans the full history in CI; `.gitignore` and `.gitattributes` cover secrets, build output, and generated files.
  3. The three PR templates (`homework`, `infra`, `docs`) share a header and carry distinct Definition of Done checklists, with no default template.
  4. The MIT license, `NOTICE`, LFS policy, and the first MADR ADRs exist; infrastructure decisions are recorded under `docs/decisions/`.
  5. `AGENTS.md` is the canonical rulebook with enforcement tags and short examples, and `.claude/CLAUDE.md` imports it without duplicating rules.

**Plans:** 8/8 plans complete
**Wave 1**
- [x] 01-01-PLAN.md — Policy as code: ruleset/settings JSON, check_policy.py, environment bootstrap, live hardening (tracer)

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 01-02-PLAN.md — .gitignore / .gitattributes, LFS routing, research-cache untrack
- [x] 01-03-PLAN.md — Pre-commit hooks and the full-history gitleaks workflow
- [x] 01-04-PLAN.md — MIT/CC-BY-4.0 licensing, NOTICE, LICENSES/, REUSE.toml
- [x] 01-05-PLAN.md — Three PR templates and the marker-slice drift checker
- [x] 01-07-PLAN.md — Five MADR ADRs and the status index
- [x] 01-08-PLAN.md — tag_homework.sh with precondition gates

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 01-06-PLAN.md — AGENTS.md rulebook, thin CLAUDE.md adapter, foundation README

### Phase 2: Toolchain Truth

**Goal**: A pinned PlatformIO toolchain builds the ESP32-S3 N16R8 target and a native target, with shared libraries wired through `symlink://`.
**Depends on**: Phase 1
**Requirements**: FOUND-09, ARCH-04
**Success Criteria** (what must be TRUE):
  1. `pio run` succeeds for a native environment and an ESP32-S3-DevKitC-1 N16R8 environment using PlatformIO Core 6.2.0 and `platformio/espressif32` 8.0.0.
  2. The N16R8 build uses 16 MB flash and octal PSRAM, not the stock 8 MB no-PSRAM board manifest.
  3. A project consumes `common`, `port`, and one adapter through `lib_deps = <name>=symlink://../../lib/<name>` from a generated `platformio.shared.ini`, and every library has a `library.json`.
  4. `compiledb` produces a `compile_commands.json` that contains the shared-library sources for both Arduino and ESP-IDF environments.

**Plans:** 5/5 plans complete

**Wave 1**
- [x] 02-01-PLAN.md — Shared config, five libraries, native smoke build, compiledb hook (tracer)

**Wave 1** *(independent of the tracer: ignore rules only)*
- [x] 02-02-PLAN.md — ESP-IDF generated-file ignore rules and the no-generated-files hook

**Wave 2** *(blocked on Wave 1)*
- [x] 02-03-PLAN.md — ESP32-S3 Arduino environment and N16R8 artifact evidence

**Wave 3** *(blocked on Wave 2)*
- [x] 02-04-PLAN.md — ESP-IDF environment, project partition table and sdkconfig defaults

**Wave 4** *(blocked on Wave 3)*
- [x] 02-05-PLAN.md — ADR-0007 and the phase gate

### Phase 3: Shared Core and Dependency Rule

**Goal**: A minimal, framework-free shared C core with enforced dependency edges and a deterministic native test suite.
**Depends on**: Phase 2
**Requirements**: ARCH-01, ARCH-02, ARCH-03, ARCH-05, ARCH-06, ARCH-07
**Success Criteria** (what must be TRUE):
  1. `common` and `port` build in the native environment with no framework headers and no target toolchain.
  2. The top-level `tests/` PlatformIO project runs the shared Unity suite and passes.
  3. `scripts/check_architecture.py` rejects a forbidden include (`common` → framework, `common` → adapter) and the native compile gate fails the build.
  4. The suite produces identical results over 20 consecutive runs, using fake time from `lib/host`.
  5. Public headers expose only C contracts with `extern "C"`; no universal HAL or whole-driver abstraction is present.

**Plans:** 9/9 plans complete

**Wave 1**
- [x] 03-01-PLAN.md — Native suite spine: `tests/` project, port time contract, common timing, host fake clock (tracer)

**Wave 2** *(blocked on Wave 1)*
- [x] 03-02-PLAN.md — ADR-0008 dependency direction, decisions index, runnable quick-start command
- [x] 03-03-PLAN.md — Port contracts for GPIO, I2C, SPI and logging (tracer: GPIO)
- [x] 03-04-PLAN.md — Common primitives: ring buffer, CRC-16, hex codecs (tracer: ring buffer)

**Wave 3** *(blocked on Wave 2)*
- [x] 03-05-PLAN.md — Host doubles for GPIO, I2C, SPI and logging (tracer: GPIO)
- [x] 03-06-PLAN.md — Arduino and ESP-IDF adapters for time, GPIO and logging (tracer: Arduino time)

**Wave 4** *(blocked on Wave 3)*
- [x] 03-07-PLAN.md — Phase 2 carry-forward: partitions move, smoke-project deletion, stub retirement, manifests 0.2.0

**Wave 5** *(blocked on Wave 4)*
- [x] 03-08-PLAN.md — `check_architecture.py`, allowlist, header contract suite, pre-commit hook (tracer: checker core)
- [x] 03-09-PLAN.md — Native purity and 20-run determinism proofs (tracer: purity)

### Phase 4: Metadata Contract and Scaffolding

**Goal**: One schema-validated homework contract and a deterministic scaffold that produces a buildable homework from a template.
**Depends on**: Phase 3
**Requirements**: FOUND-01, META-01, META-02, META-03, META-04
**Success Criteria** (what must be TRUE):
  1. `scripts/new_homework` scaffolds from either the Arduino or ESP-IDF template, is idempotent, supports `--dry-run`, and refuses to overwrite existing files.
  2. The scaffolded project contains `platformio.ini`, `src/`, `include/`, `test/`, `assets/`, `README.md`, `task.md`, and `homework.yaml`, and builds immediately.
  3. `homework.yaml` is validated against a JSON Schema with `additionalProperties: false`; an unknown key is rejected and every required field is recorded.
  4. `task.md` contains an English paraphrase, the source reference, retrieval date, and attribution, and no original internal material.
  5. `templates/` provides the Arduino homework, ESP-IDF homework, report, task, ADR, and board-profile templates.

**Plans:** 2/5 plans executed

**Wave 1**
- [x] 04-01-PLAN.md — Contract core: JSON Schema, shared validation module, checker exit codes (tracer)
- [x] 04-02-PLAN.md — Arduino and ESP-IDF homework templates, build-proven at homework depth

**Wave 2** *(blocked on Wave 1)*
- [ ] 04-03-PLAN.md — Provenance rules, allowlist, task/report/ADR/board-profile templates (tracer: task.md)

**Wave 3** *(blocked on Wave 2)*
- [ ] 04-04-PLAN.md — `scripts/new_homework`, golden trees, pre-commit metadata hook (tracer: scaffold)

**Wave 4** *(blocked on Wave 3)*
- [ ] 04-05-PLAN.md — ADR-0009/0010, AGENTS.md and REUSE.toml updates, phase build gate (tracer: ADRs)

### Phase 5: Generated Views and Documentation Site

**Goal**: Every repeated view of the repository is generated from `homework.yaml`, and the documentation site builds and deploys from that tree.
**Depends on**: Phase 4
**Requirements**: META-05, META-06, META-07, META-08
**Success Criteria** (what must be TRUE):
  1. The README index, MkDocs navigation, multi-root workspace, `platformio.shared.ini`, and CI matrix regenerate from `homework.yaml`; each generator's `--check` exits non-zero on drift.
  2. `scripts/affected.py` maps a `lib/**` diff to every consumer project in the build and simulation matrix.
  3. The committed `homeworks.code-workspace` contains `repo`, `docs`, `lib`, `scripts`, and every homework as roots, with ASCII paths.
  4. `mkdocs build --strict` succeeds on the generated tree with MkDocs Material 9.7.7, a Zensical-compatible configuration, and vendored KaTeX; GitHub Pages deploys the artifact.

**Plans**: TBD

### Phase 6: Developer Experience and Quality Layering

**Goal**: A novice can open the workspace, get correct ESP32 IntelliSense, and have formatting and layered quality checks run without guesswork.
**Depends on**: Phase 4
**Requirements**: TOOL-01, TOOL-02, TOOL-03, TOOL-04
**Success Criteria** (what must be TRUE):
  1. `clang-format --dry-run --Werror` passes with 4-space indent, a 120-column limit, and function braces on a new line, documented as an ESP-IDF approximation rather than equivalence.
  2. clang-tidy runs bugprone, cert, performance, and portability checks on host code in pre-push.
  3. esp-clangd resolves ESP32-S3 includes through per-project `.clangd` files and explicit absolute `--query-driver` globs, and cpptools IntelliSense is disabled.
  4. pre-commit runs format, markdownlint, yamllint, ruff, and gitleaks; pre-push runs clang-tidy.
  5. `docs/standards/vscode.md` takes a VS Code beginner from install to format-on-save, Problems panel, clangd, and a no-hardware check.

**Plans**: TBD

### Phase 7: Simulation Spike

**Goal**: An evidence-based simulator decision recorded in ADR-0004, with measured costs and fidelity limits.
**Depends on**: Phase 4
**Requirements**: SIM-02, SIM-03
**Success Criteria** (what must be TRUE):
  1. ADR-0004 records measured cold start, compile time, serial reliability, simulated minutes, and fidelity limits for Wokwi, Velxio, Renode, and Fritzing.
  2. A homework 1.3 scenario runs in Wokwi from `diagram.json` and `wokwi.toml`, or the ADR records a blocking failure and the chosen fallback with evidence.
  3. `wokwi-cli lint` validates the canonical `diagram.json`.
  4. Fritzing output is used only as an attributed illustration; no part graphics are copied into shared assets or the docs site.
  5. The ADR states which simulator serves each platform and the measured CI cost basis for the cadence decision.

**Plans**: TBD

### Phase 8: Fast CI

**Goal**: Pull requests are gated by a fast, changed-only CI pipeline with one required check; simulation is optional and never blocks forks.
**Depends on**: Phase 3, Phase 4, Phase 7
**Requirements**: TOOL-05, TOOL-06, SIM-04
**Success Criteria** (what must be TRUE):
  1. A pull request runs a fast `meta` job (schema, `--check` drift, lint, gitleaks, architecture, `wokwi-cli lint`) and a `changes` job that computes the affected matrix.
  2. CI builds and unit-tests changed projects on every pull request and exposes a single required `gate` check.
  3. Simulation runs only for changed projects after the spike, with explicit timeouts and artifact upload, and is never a required check for fork pull requests.
  4. Nightly runs the full build and unit-test matrix without simulation.

**Plans**: TBD

### Phase 9: Agent Workflow and Skills

**Goal**: Seven versioned agent skills exist, with `new-homework` and `hw-build` fully usable in guided and one-shot modes.
**Depends on**: Phase 4
**Requirements**: FLOW-01, FLOW-02, FLOW-03, FLOW-04, FLOW-05, FLOW-06, FLOW-07
**Success Criteria** (what must be TRUE):
  1. Seven skills exist at version 0.1 in the project skills directory, each carrying a changelog and lessons-learned section.
  2. `new-homework` supports guided and one-shot modes and asks from an adaptive question bank covering board, framework, language, mode, specification, simulation, tests, and deliverables.
  3. Guided mode pauses after each explanation → code → run → questions block and deepens the explanation when the user is stuck.
  4. Both modes checkpoint after intake, after code, and after the report; flashing and commit/PR require confirmation, and conflicts or ambiguity produce a recorded recommended assumption.
  5. `hw-build` fixes a failing build at most twice before explaining and escalating; `hw-flash` captures serial logs only after explicit confirmation; the four remaining skills are documented stubs.

**Plans**: TBD

### Phase 10: Report and Evidence System

**Goal**: A report and evidence contract that every homework must satisfy, with automated checks and a self-audit rubric.
**Depends on**: Phase 4
**Requirements**: REPORT-01, REPORT-02, REPORT-03, REPORT-04, REPORT-05, REPORT-06, REPORT-07, REPORT-08, TOOL-08
**Success Criteria** (what must be TRUE):
  1. The report template and check enforce the 10 academic sections plus BOM, pin map, calculations, safety checklist, measurement ledger, traceability matrix, honest status, and IEEE references.
  2. A report missing a BOM row, a ledger provenance label, or a traceability entry fails the check with a specific message.
  3. `docs/standards/electrical-calculations.md` lists the calculation catalog, and each calculation records formula, units, input provenance, result, uncertainty, and assumption impact.
  4. The self-audit rubric maps every report artifact and evidence item to the pre-PR checklist.

**Plans**: TBD

### Phase 11: Pilot Homework 1.3

**Goal**: Homework 1.3 ships end to end as the reference artifact and validates the whole system before scale-out.
**Depends on**: Phase 4, Phase 5, Phase 7, Phase 8, Phase 9, Phase 10
**Requirements**: PILOT-01, PILOT-02, SIM-01
**Success Criteria** (what must be TRUE):
  1. `homeworks/1_3-police-flasher/` contains the scaffolded artifacts, native tests, and all four extensions: third LED, variable speed, complex pattern, and single-GPIO operation.
  2. Native tests pass and the Wokwi simulation reproduces the four patterns with provenance-labeled evidence.
  3. The report satisfies Phase 10 and includes measured versus simulated values, commit hashes, known limitations, and next steps.
  4. The README index, workspace, and docs site include homework 1.3, and the documented local simulation path is recorded.
  5. The pull request passes CI and the merged commit is tagged `hw/1_3-police-flasher`.

**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11.
Phases 5, 6, 7, 9, and 10 may proceed in parallel once Phase 4 is complete; Phase 8 needs 3, 4, and 7; Phase 11 needs 4–10.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Repository Foundation and Policy Gate | 8/8 | Complete    | 2026-10-23 |
| 2. Toolchain Truth | 5/5 | Complete    | 2026-10-23 |
| 3. Shared Core and Dependency Rule | 9/9 | Complete    | 2026-10-24 |
| 4. Metadata Contract and Scaffolding | 2/5 | In Progress | - |
| 5. Generated Views and Documentation Site | 0/TBD | Not started | - |
| 6. Developer Experience and Quality Layering | 0/TBD | Not started | - |
| 7. Simulation Spike | 0/TBD | Not started | - |
| 8. Fast CI | 0/TBD | Not started | - |
| 9. Agent Workflow and Skills | 0/TBD | Not started | - |
| 10. Report and Evidence System | 0/TBD | Not started | - |
| 11. Pilot Homework 1.3 | 0/TBD | Not started | - |
