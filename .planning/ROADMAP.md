# Roadmap: Homeworks — Embedded Engineering Course

## Overview

Build the repository as a monorepo of independent PlatformIO projects over a small,
enforced C core, with every repeated artifact generated from one metadata contract. Four
foundation phases proved the toolchain, the shared core, and the metadata contract. Phase
4.1 removes governance ceremony that a single-author course repository does not need;
Phase 4.2 runs homework 1.3 end to end manually as a tracer and records the friction.
Phases 5–10 then automate only what that log proves painful — generated views, developer
experience, the simulation decision, CI, the agent skills, and the report system — before
Phase 11 ships the polished pilot and scales to 30+ homeworks.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Repository Foundation and Policy Gate** - Public history, licensing, asset, and contribution rules that cannot be repaired later (completed 2026-10-23)
- [x] **Phase 2: Toolchain Truth** - Pinned PlatformIO builds for native and ESP32-S3 N16R8 with `symlink://` shared libraries (completed 2026-10-23)
- [x] **Phase 3: Shared Core and Dependency Rule** - Framework-free `common`/`port`, thin adapters, and an enforced native test gate (completed 2026-10-24)
- [x] **Phase 4: Metadata Contract and Scaffolding** - Schema-validated `homework.yaml`, templates, and a deterministic `new_homework` (completed 2026-10-25)
- [ ] **Phase 4.1: Ceremony Trim (INSERTED)** - Remove governance bureaucracy; keep four invariants and a short Definition of Done
- [ ] **Phase 4.2: Tracer Homework 1.3 (INSERTED)** - Run homework 1.3 end to end manually and record the friction log
- [ ] **Phase 5: Generated Views and Documentation Site** - Index, workspace, shared ini, CI matrix, and MkDocs site generated from metadata
- [ ] **Phase 6: Developer Experience and Quality Layering** - Formatting, clang-tidy, esp-clangd, hooks, and beginner onboarding
- [ ] **Phase 7: Simulation Spike** - Measured Wokwi/Velxio/Renode/Fritzing evidence and ADR-0004
- [ ] **Phase 8: Fast CI** - `meta` + `changes` + changed builds, one required gate, optional simulation
- [ ] **Phase 9: Agent Workflow and Skills** - Seven versioned skills with `new-homework` and `hw-build` fully implemented
- [ ] **Phase 10: Report and Evidence System** - The 10-section report contract, calculations catalog, checks, and self-audit rubric
- [ ] **Phase 11: Pilot Homework 1.3 — Finalization** - The polished tracer shipped end to end, tagged, and ready for scale-out

## Phase Details

> **Automation rule (Phases 5–10)**: Each phase in this group automates only work that the Phase 4.2 friction log proves painful. An automation with no entry in the log is not built.

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

**Plans:** 9/9 plans complete (5 executed, 3 gap-closure)
- [x] 04-09-PLAN.md

**Wave 1**
- [x] 04-01-PLAN.md — Contract core: JSON Schema, shared validation module, checker exit codes (tracer)
- [x] 04-02-PLAN.md — Arduino and ESP-IDF homework templates, build-proven at homework depth

**Wave 2** *(blocked on Wave 1)*
- [x] 04-03-PLAN.md — Provenance rules, allowlist, task/report/ADR/board-profile templates (tracer: task.md)

**Wave 3** *(blocked on Wave 2)*
- [x] 04-04-PLAN.md — `scripts/new_homework`, golden trees, pre-commit metadata hook (tracer: scaffold)

**Wave 4** *(blocked on Wave 3)*
- [x] 04-05-PLAN.md — ADR-0009/0010, AGENTS.md and REUSE.toml updates, phase build gate (tracer: ADRs)

**Gap closure** *(wave 1, after verification)*
- [x] 04-06-PLAN.md — Refuse symlinked and non-directory target components in `scripts/new_homework` (CR-01, WR-02)
- [x] 04-07-PLAN.md — Whole-path allowlist suppression and composed-YAML-key ERROR records (WR-01, CR-02)
- [x] 04-08-PLAN.md — Refuse a symlinked `homeworks` base and derive the id-match directory lexically (CR-01 one component higher)

### Phase 4.1: Ceremony Trim (INSERTED)

**Goal**: Remove the governance ceremony that costs time on every change while keeping the four cross-cutting invariants and a short homework Definition of Done.
**Depends on**: Phase 4
**Requirements**: INV-01, INV-02, INV-03, INV-04 (cross-cutting)
**Success Criteria** (what must be TRUE):
  1. `policy/`, `check_policy.py`, `REUSE.toml`, `NOTICE`, `LICENSES/`, the `reuse` CI job, `check_pr_templates.py`, the three-template split, the Cyrillic allowlist, and the tag preconditions are gone; one MIT `LICENSE` and one default PR template remain.
  2. `scripts/tests/` keeps only the metadata and scaffold smoke modules; the other meta-test modules are deleted.
  3. `AGENTS.md` has a four-step quick-start, no policy/licence-split/PR-drift rules, a proportional GSD rule (`/gsd-fast` for trivial, `/gsd-quick` for multi-step, the phase workflow for architectural work or homework delivery), and a short Definition of Done.
  4. `pio test -d tests -e native`, the smoke build, `pre-commit run --all-files`, and `python3 scripts/check_metadata.py` pass after the trim.
  5. No dangling references to deleted files remain in `README.md`, `AGENTS.md`, `docs/`, or `.github/`.
  6. `docs/decisions/README.md` is a one-page decision table linking to the 11 existing ADRs; a new decision defaults to a row, and an ADR file is created only when the decision needs real argumentation; superseded decisions are marked in the table.

**Plans**: 3/7 plans executed
**Wave 1**
- [x] 04.1-01-PLAN.md — Decouple the survivors (allowlist removal, canonical-ID move); Wave 0 repair.

**Wave 2** *(blocked on Wave 1 completion)*
- [ ] 04.1-02-PLAN.md — Delete policy-as-code and PR-template drift tooling with their tests.
- [ ] 04.1-03-PLAN.md — Delete the licence split, its CI job, and the ADR index test.
- [x] 04.1-05-PLAN.md — Reduce tag_homework.sh to the minimal script.
- [x] 04.1-06-PLAN.md — Delete the remaining independent meta-tests; prove the architecture rule green.

**Wave 3** *(blocked on Wave 2 completion)*
- [ ] 04.1-04-PLAN.md — Rewrite AGENTS.md, README.md, the decision table, and add the default PR template.

**Wave 4** *(blocked on Wave 3 completion)*
- [ ] 04.1-07-PLAN.md — Phase gate: smoke builds, full suites, pre-commit, structural assertions.

**Cross-cutting constraints:**
- The surviving Python suite stays green after each deletion group.

### Phase 4.2: Tracer Homework 1.3 (INSERTED)

**Goal**: Run homework 1.3 through the complete cycle manually with the trimmed tooling and record every friction point, so Phases 5–10 automate only what the log proves painful.
**Depends on**: Phase 4.1
**Requirements**: INV-01, INV-02, INV-03, INV-04, PILOT-01 (first pass), META-02 (paraphrase check)
**Success Criteria** (what must be TRUE):
  1. `homeworks/1_3-police-flasher/` is scaffolded through `scripts/new_homework`, builds for ESP32-S3 N16R8, and its pure pattern logic has native Unity tests.
  2. The homework contains a real `assets/diagram.json`, a Wokwi scenario, and a report with BOM, pin map, calculations, measurement ledger, and traceability.
  3. README index, workspace, shared ini, and CI matrix entries are edited manually and are correct for the one real homework.
  4. The pull request passes CI, and no `hw/` tag is created in this phase.
  5. A friction log exists in the phase directory with one entry per friction point: step, what hurt, frequency, cheap fix, automation candidate.
  6. The deferred UAT item on `task.md` paraphrase originality is reviewed on this first real homework.

**Plans**: TBD

### Phase 5: Generated Views and Documentation Site

**Goal**: Every repeated view of the repository is generated from `homework.yaml`, and the documentation site builds and deploys from that tree.
**Friction-log justification**: The Phase 4.2 log must contain at least one entry for generated views or the docs site; otherwise the automation is not built.
**Depends on**: Phase 4.2
**Requirements**: META-05, META-06, META-07, META-08
**Success Criteria** (what must be TRUE):
  1. The README index, MkDocs navigation, multi-root workspace, `platformio.shared.ini`, and CI matrix regenerate from `homework.yaml`; each generator's `--check` exits non-zero on drift.
  2. `scripts/affected.py` maps a `lib/**` diff to every consumer project in the build and simulation matrix.
  3. The committed `homeworks.code-workspace` contains `repo`, `docs`, `lib`, `scripts`, and every homework as roots, with ASCII paths.
  4. `mkdocs build --strict` succeeds on the generated tree with MkDocs Material 9.7.7, a Zensical-compatible configuration, and vendored KaTeX; GitHub Pages deploys the artifact.

**Plans**: TBD

### Phase 6: Developer Experience and Quality Layering

**Goal**: A novice can open the workspace, get correct ESP32 IntelliSense, and have formatting and layered quality checks run without guesswork.
**Friction-log justification**: The Phase 4.2 log must contain at least one entry for formatting, IntelliSense, or local feedback; otherwise the tooling is not added.
**Depends on**: Phase 4.2
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
**Friction-log justification**: The Phase 4.2 log must contain at least one entry for simulation or wiring; otherwise the spike is not run.
**Depends on**: Phase 4.2
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
**Friction-log justification**: The Phase 4.2 log must contain at least one entry for CI feedback time or changed-only builds; otherwise the pipeline is not built.
**Depends on**: Phase 3, Phase 4.2, Phase 5, Phase 6, Phase 7
**Requirements**: TOOL-05, TOOL-06, SIM-04
**Success Criteria** (what must be TRUE):
  1. A pull request runs a fast `meta` job (schema, `--check` drift, lint, gitleaks, architecture, `wokwi-cli lint`) and a `changes` job that computes the affected matrix.
  2. CI builds and unit-tests changed projects on every pull request and exposes a single required `gate` check.
  3. Simulation runs only for changed projects after the spike, with explicit timeouts and artifact upload, and is never a required check for fork pull requests.
  4. Nightly runs the full build and unit-test matrix without simulation.

**Plans**: TBD

### Phase 9: Agent Workflow and Skills

**Goal**: Seven versioned agent skills exist, with `new-homework` and `hw-build` fully usable in guided and one-shot modes.
**Friction-log justification**: The Phase 4.2 log must contain at least one entry for the intake, build, or report workflow; otherwise the corresponding skill is not written.
**Depends on**: Phase 4.2
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
**Friction-log justification**: The Phase 4.2 log must contain at least one entry for report structure, BOM, calculations, measurements, or traceability; otherwise the checker is not built.
**Depends on**: Phase 4.2
**Requirements**: REPORT-01, REPORT-02, REPORT-03, REPORT-04, REPORT-05, REPORT-06, REPORT-07, REPORT-08, TOOL-08
**Success Criteria** (what must be TRUE):
  1. The report template and check enforce the 10 academic sections plus BOM, pin map, calculations, safety checklist, measurement ledger, traceability matrix, honest status, and IEEE references.
  2. A report missing a BOM row, a ledger provenance label, or a traceability entry fails the check with a specific message.
  3. `docs/standards/electrical-calculations.md` lists the calculation catalog, and each calculation records formula, units, input provenance, result, uncertainty, and assumption impact.
  4. The self-audit rubric maps every report artifact and evidence item to the pre-PR checklist.

**Plans**: TBD

### Phase 11: Pilot Homework 1.3 — Finalization

**Goal**: The tracer from Phase 4.2 becomes the shipped reference artifact: polished, verified through the complete automated chain, tagged, and ready to scale to the remaining homeworks.
**Depends on**: Phase 4.2, Phase 5, Phase 7, Phase 8, Phase 9, Phase 10
**Requirements**: PILOT-01, PILOT-02, SIM-01
**Success Criteria** (what must be TRUE):
  1. `homeworks/1_3-police-flasher/` contains the scaffolded artifacts, native tests, and all four extensions: third LED, variable speed, complex pattern, and single-GPIO operation.
  2. Native tests pass and the Wokwi simulation reproduces the four patterns with provenance-labeled evidence.
  3. The report satisfies Phase 10 and includes measured versus simulated values, commit hashes, known limitations, and next steps.
  4. The README index, workspace, and docs site include homework 1.3 through the generated path, and the documented local simulation path is recorded.
  5. The pull request passes CI and the merged commit is tagged `hw/1_3-police-flasher`.
  6. The Phase 4.2 friction log is closed: every automation candidate has a phase or a recorded decision not to build it.

**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 4.1 → 4.2 → 5 → 6 → 7 → 8 → 9 → 10 → 11.
Phase 4.1 trims ceremony; Phase 4.2 runs the tracer and produces the friction log. Phases 5, 6, 7, 9, and 10 may proceed in parallel once Phase 4.2 is complete and are justified by the log; Phase 8 needs 3, 4.2, 5, 6, and 7; Phase 11 needs 4.2 and 5–10.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Repository Foundation and Policy Gate | 8/8 | Complete    | 2026-10-23 |
| 2. Toolchain Truth | 5/5 | Complete    | 2026-10-23 |
| 3. Shared Core and Dependency Rule | 9/9 | Complete    | 2026-10-24 |
| 4. Metadata Contract and Scaffolding | 9/9 | Complete    | 2026-10-25 |
| 4.1. Ceremony Trim | 3/7 | In Progress | - |
| 4.2. Tracer Homework 1.3 | 0/TBD | Not started | - |
| 5. Generated Views and Documentation Site | 0/TBD | Not started | - |
| 6. Developer Experience and Quality Layering | 0/TBD | Not started | - |
| 7. Simulation Spike | 0/TBD | Not started | - |
| 8. Fast CI | 0/TBD | Not started | - |
| 9. Agent Workflow and Skills | 0/TBD | Not started | - |
| 10. Report and Evidence System | 0/TBD | Not started | - |
| 11. Pilot Homework 1.3 — Finalization | 0/TBD | Not started | - |

## Backlog

### Phase 999.1: Follow-up — Phase 04 deferred UAT follow-up: Test 1 (BACKLOG)

**Goal:** Resolve the UAT checkpoint deferred during Phase 04 verification
**Source phase:** 04
**Deferred at:** 2026-10-25 during /gsd-verify-work 04 session completion
**Follow-ups:**
- [ ] Test 1: No homework exists yet; review paraphrase originality when the first real task.md lands. (deferred 2026-10-25)
  *Phase 4.2 resolves this: the tracer is the first real `task.md`.*

### Phase 999.2: Return bureaucracy after stabilization, if needed (BACKLOG)

**Goal:** Reintroduce governance ceremony only if the repository gains contributors or a second maintainer.
**Source phase:** 04.1
**Deferred at:** 2026-10-25 during the ceremony trim exploration
**Candidate items:**
- [ ] Policy-as-code and a live ruleset drift check
- [ ] REUSE/SPDX licence compliance and the MIT/CC-BY split
- [ ] Multi-type PR templates and the shared-header drift check
- [ ] The ADR status index and ADR-per-decision rule
