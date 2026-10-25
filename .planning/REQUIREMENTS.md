# Requirements: Homeworks — Embedded Engineering Course

**Defined:** 2026-10-23
**Core Value:** Every homework ships as a self-contained, reproducible, industry-standard
engineering artifact — code, evidence, and report — that can be understood and verified a
year later.

## v1 Requirements

Requirements for the initial release. Each maps to a roadmap phase.

### Repository Foundation and Policy

- [x] **FOUND-01**: The repository contains one independent PlatformIO project per
      homework under `homeworks/<id>/`, with its own `platformio.ini`, `src/`, `include/`,
      `test/`, `assets/`, `README.md`, `task.md`, and `homework.yaml`.
- [x] **FOUND-02**: Homework IDs follow `module_lesson-name` (for example,
      `1_3-police-flasher`) and remain stable after publication.
- [x] **FOUND-03**: `main` is protected; every change reaches it through a branch and a
      pull request; force-push and published-history rewriting are forbidden.
- [x] **FOUND-04**: Commits follow Conventional Commits; pull requests are squash-merged;
      a `hw/<id>` tag is created after merge and the source branch is deleted.
- [x] **FOUND-05**: Three pull-request templates exist (`homework`, `infra`, `docs`) with
      a shared header and type-specific Definition of Done checklists.
      *(Superseded 2026-10-25: one default PR template.)*
- [x] **FOUND-06**: The repository is MIT-licensed for original work, with a `NOTICE` and
      attribution for third-party assets; internal course materials and PII are never
      committed.
      *(Simplified 2026-10-25: a single MIT `LICENSE`; `NOTICE`/`REUSE` removed.)*
- [x] **FOUND-07**: `gitleaks` runs in pre-commit and over the full history in CI;
      `.gitignore` and `.gitattributes` cover secrets, build output, and generated files.
- [x] **FOUND-08**: Git LFS is used only for large non-diffable binaries; site assets
      remain normal git objects because GitHub Pages cannot serve LFS; videos are linked.
- [x] **FOUND-09**: The toolchain is pinned: PlatformIO Core 6.2.0,
      `platformio/espressif32` 8.0.0, and explicit ESP32-S3-DevKitC-1 N16R8 overrides
      (16 MB flash, octal PSRAM).
- [x] **FOUND-10**: `AGENTS.md` is the canonical rulebook (up to ~300 lines) with
      enforcement tags, short examples, and an agent quick-start; `.claude/CLAUDE.md`
      imports it.

### Metadata and Generation

- [x] **META-01**: `homework.yaml` is validated by a JSON Schema with
      `additionalProperties: false` and records identity, board, framework, language,
      simulation, tests, report, assets, status, source, and toolchain.
- [ ] **META-02**: `task.md` contains an English paraphrase, the source reference, the
      retrieval date, and attribution; it never contains the original internal material.
      *Shape, sentinel and Cyrillic rules are enforced by the checker; paraphrase
      originality is deferred to the first real homework (Phase 4.2, D-09 review).*
      *(Mechanism simplified 2026-10-25: one grep, no allowlist.)*
- [x] **META-03**: `templates/` provides an Arduino homework template, an ESP-IDF
      homework template, a report template, a task template, an ADR template, and a
      board-profile template.
- [x] **META-04**: `scripts/new_homework` scaffolds a homework from a template, is
      idempotent, supports `--dry-run`, and refuses to overwrite existing files.
- [ ] **META-05**: The README index, MkDocs navigation, multi-root workspace file,
      `platformio.shared.ini`, and CI matrix are generated from `homework.yaml`; every
      generator supports `--check` and CI fails on drift.
- [ ] **META-06**: `scripts/affected.py` maps a git diff to a build and simulation
      matrix, including fanout from `lib/**` changes to every consumer.
- [ ] **META-07**: A committed multi-root `homeworks.code-workspace` is generated with
      `repo`, `docs`, `lib`, `scripts`, and every homework as a root; display names may
      use emoji, paths remain ASCII.
- [ ] **META-08**: MkDocs Material 9.7.7 builds a site from the generated docs tree; the
      configuration stays Zensical-compatible, uses vendored KaTeX, and deploys to
      GitHub Pages through artifact upload.

### Shared Architecture

- [x] **ARCH-01**: `lib/port` defines C function-pointer contracts for time, GPIO, I2C,
      SPI, and logging; it contains no framework headers and no state.
- [x] **ARCH-02**: `lib/common` contains pure C domain logic (ring buffers, timing math,
      pattern/state-machine logic, codecs, calculations) and never blocks or sleeps.
- [x] **ARCH-03**: `lib/arduino`, `lib/espidf`, and `lib/host` contain thin adapters and
      deterministic test doubles; adapters contain no business logic.
- [x] **ARCH-04**: Shared libraries are consumed through
      `lib_deps = <name>=symlink://../../lib/<name>` with a `library.json` per library
      and a generated `platformio.shared.ini`; `lib_extra_dirs` remains a generator
      fallback only.
- [x] **ARCH-05**: `scripts/check_architecture.py` and a native compile gate enforce the
      dependency rule (`common → port`, adapters → port, homework → common + port + one
      adapter).
- [x] **ARCH-06**: A top-level `tests/` PlatformIO project compiles `common` and `port`
      natively and runs the shared-library Unity suite without a target toolchain.
- [x] **ARCH-07**: No universal HAL is introduced; reusable drivers abstract the bus
      (I2C/SPI), not the whole driver, and framework APIs remain idiomatic in homework
      code.

### Homework Artifacts and Reports

- [ ] **REPORT-01**: Every homework has a 10-section academic report in Markdown:
      title/metadata, objective, assumptions, theory, hardware and wiring, methodology,
      results, analysis with industry notes, conclusions, and IEEE references.
- [ ] **REPORT-02**: The report includes a BOM with ref, part/value, quantity, package,
      source/link, and notes.
- [ ] **REPORT-03**: The report includes a pin map and uses `assets/diagram.json` as the
      source of truth for wiring.
- [ ] **REPORT-04**: Electrical calculations show formula, units, input provenance,
      result, tolerance/uncertainty, and the effect of assumptions; the calculation
      catalog in `docs/standards/electrical-calculations.md` is used to select the
      relevant set.
- [ ] **REPORT-05**: Every code homework includes an electrical safety checklist.
- [ ] **REPORT-06**: Results use a measurement ledger labelling each value as measured,
      calculated, simulated, datasheet, or explicitly not measured, with instrument,
      method, uncertainty, and commit hash.
- [ ] **REPORT-07**: Every report includes a compact traceability matrix mapping
      requirement/claim to design artifact, verification method, evidence, and status.
- [ ] **REPORT-08**: Every report includes honest status, verified board/toolchain,
      known limitations, and next steps.

### Simulation and Diagrams

- [ ] **SIM-01**: Every homework with supported hardware has a documented local
      simulation path; `diagram.json` is canonical and `wokwi-cli lint` validates it.
- [ ] **SIM-02**: A full spike measures Wokwi (primary), Velxio (self-hosted fallback),
      Renode (STM32), and Fritzing (illustration) on the pilot, including cold start,
      compile, serial reliability, measured minutes, and fidelity limits; the result is
      recorded in ADR-0004.
- [ ] **SIM-03**: Fritzing SVGs may be used in reports with attribution; part graphics
      are not copied into shared assets or the docs site, and `diagram.json` remains the
      source of truth.
- [ ] **SIM-04**: Simulation in CI is introduced only after the spike, only for changed
      projects, with explicit timeouts and artifact upload, and is never a required
      check for fork pull requests.

### Tooling and Quality

- [ ] **TOOL-01**: clang-format 23.1.3 is configured as a documented ESP-IDF
      approximation (4 spaces, 120 columns, function brace on a new line); clang-tidy
      runs bugprone, cert, performance, and portability checks on host code.
- [ ] **TOOL-02**: esp-clangd serves the workspace through `scripts/clangd-wrapper.sh`
      with per-project `.clangd` files, `compiledb`-generated databases, and explicit
      absolute `--query-driver` globs; cpptools IntelliSense is disabled.
- [ ] **TOOL-03**: Checks are layered: fast hooks (format, markdownlint, yamllint, ruff,
      gitleaks) in pre-commit; clang-tidy in pre-push; full build, tests, schema, docs,
      architecture, and simulation checks in CI.
- [ ] **TOOL-04**: `docs/standards/vscode.md` onboards a VS Code beginner: extensions,
      tasks, format-on-save, Problems panel, clangd, and a no-hardware simulation path.
- [ ] **TOOL-05**: CI has a fast `meta` job (schema, `--check` drift, lint, gitleaks,
      architecture check) and a `changes` job that computes the affected matrix.
- [ ] **TOOL-06**: CI builds and tests changed projects on every pull request and exposes
      a single required `gate` check; nightly runs the full build and unit-test matrix.
- [x] **TOOL-07**: Infrastructure decisions are recorded as MADR ADRs in
      `docs/decisions/`; homework assumptions live in the report with impact-if-wrong and
      validation.
      *(Narrowed 2026-10-25: ADRs for irreversible decisions only; no status index.)*
- [ ] **TOOL-08**: A self-audit rubric maps the report, BOM, calculations, safety,
      evidence, and traceability to the pre-PR checklist.
      *(Deferred 2026-10-25 until the report system has three real uses.)*

### Agent Workflow and Skills

- [ ] **FLOW-01**: Seven project-local skills exist at version 0.1 (`new-homework`,
      `hw-build`, `hw-flash`, `hw-report`, `schematic`, `simulate`, `course-index`);
      `new-homework` and `hw-build` are fully implemented first.
- [ ] **FLOW-02**: `new-homework` supports guided and one-shot modes with an adaptive
      question bank covering board, framework, language, mode, specification,
      simulation, tests, and deliverables.
- [ ] **FLOW-03**: Guided mode follows explanation → code → run → questions at block
      granularity, pauses after each block, and deepens the explanation when the user is
      stuck.
- [ ] **FLOW-04**: Both modes checkpoint after intake, after code, and after the report;
      guardrails for flashing, commit/PR, spec-vs-best-practice conflicts, and ambiguity
      always apply.
- [ ] **FLOW-05**: Spec-vs-best-practice conflicts and ambiguous requirements are
      presented with a recommended assumption; the decision is recorded in the report.
- [ ] **FLOW-06**: A failing build is fixed automatically at most twice, then the cause
      is explained and direction is requested.
- [ ] **FLOW-07**: `hw-flash` requires explicit confirmation before flashing and captures
      serial logs; `hw-report`, `schematic`, `simulate`, and `course-index` remain thin
      stubs until their first real use.

### Pilot

- [x] **PILOT-01**: Homework 1.3 (Police Flasher) is delivered end to end in guided mode
      with all optional extensions: third LED, variable speed, complex pattern, and
      single-GPIO operation.
- [ ] **PILOT-02**: The pilot validates the template, skill, report, native tests, local
      simulation, index, workspace, and CI chain before scale-out.

## Invariants and Homework Acceptance (2026-10-25)

The ceremony trim keeps four cross-cutting invariants and replaces the per-homework
acceptance checklist with a short Definition of Done. The reasoning lives in
`.planning/notes/ceremony-vs-engineering-principle.md`.

### Invariants

- [x] **INV-01 (Public safety)**: No secret, private datum, or original internal course
      material ever enters the public history. gitleaks runs in pre-commit and over the
      full history in CI; repository artifacts are English-only. Enforcement is a secret
      scan plus a Cyrillic grep, not a licence-compliance pipeline.
- [x] **INV-02 (Build and tests)**: Every homework builds for its declared target
      environment; pure logic has native Unity tests. The invariant is the green build
      and the green suite, not a fixed number of tests or a determinism proof.
- [x] **INV-03 (Uniform structure)**: Every homework directory carries `task.md`,
      `homework.yaml`, `README.md`, and a report skeleton, and validates against
      `schema/homework.schema.json`. IDs follow `^[0-9]+_[0-9]+-[a-z0-9-]+$`.
- [x] **INV-04 (Architecture boundary)**: `lib/common` and `lib/port` contain no
      framework headers; `common` does not depend on adapters. One lightweight check
      enforces the edge.

### Definition of Done for a homework

A homework is done when:

1. `pio run` is green for its target environment.
2. `pio test -e native` is green when the homework contains pure logic.
3. `task.md`, `homework.yaml`, `README.md`, and `report.md` exist, and metadata
   validation passes.
4. The report contains the sections that apply to the assignment; BOM, calculations,
   measurement ledger, and traceability are guidance, not a merge gate until Phase 10.
5. The pull request is merged and tagged `hw/<id>`.

### Superseded or simplified requirements

- **FOUND-05** (three PR templates with a shared header) is superseded by one default
  PR template.
- **FOUND-06** is simplified to a single repo-wide MIT `LICENSE`; `NOTICE`, `REUSE.toml`,
  `LICENSES/`, and SPDX headers are removed.
- **META-02** keeps the provenance and English-only invariants; the Cyrillic allowlist
  is replaced by a single grep.
- **TOOL-03** and **TOOL-05** keep their CI intent, but the `meta` job no longer runs
  policy or REUSE checks.
- **TOOL-07** is narrowed: ADRs are recorded for irreversible decisions, not for every
  infrastructure choice, and the status index is no longer mandatory.
- **TOOL-08** is deferred until the report system has been used on at least three
  homeworks.
- **REPORT-02..07** remain the report contract, but they are not an automated merge gate
  until Phase 10.

These invariants are cross-cutting: they apply from Phase 4.1 onward and are not counted
in the phase-mapped v1 totals above.

## v2 Requirements

Deferred to a future release. Tracked but not in the current roadmap.

### Scale-Out

- **SCALE-01**: ESP-IDF homework template and adapter when the course reaches ESP-IDF.
- **SCALE-02**: STM32 homework template and board profile when the course reaches STM32.
- **SCALE-03**: Hardware-in-the-loop tests when a claim depends on physics, timing,
  analog behavior, or power that simulation cannot establish.
- **SCALE-04**: Fault-injection and negative-path scenarios after happy-path simulation
  is stable.
- **SCALE-05**: A dev container when a second machine or contributor cannot reproduce the
  setup with the onboarding guide.
- **SCALE-06**: Per-homework release bundles and GitHub Release artifacts after the first
  public release.
- **SCALE-07**: A portfolio-quality project page after the first public release.
- **SCALE-08**: A course concept map once enough modules are known.
- **SCALE-09**: A fully adaptive question bank after the pilot exposes which questions
  actually help.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Universal HAL over Arduino and ESP-IDF | Hides the frameworks the course teaches; leaks on non-trivial peripherals; becomes a shadow framework |
| Pre-scaffolding all 30+ homework directories | The syllabus is revealed progressively; stale scaffolds create noise |
| DOCX/PDF report pipeline as source of truth | Dual sources drift; binary diffs are unreviewable |
| Gradebook, autograder, or rubric engine | Introduces PII and a second product; grading stays external |
| Committing videos and large binaries | Bloats clones; hits GitHub/LFS limits; LFS is not served by Pages |
| Committing internal course materials or PII | Copyright, privacy, and academic-integrity risk |
| MISRA C or a full static-analysis gate | High noise and cost; distracts from the course's learning goals |
| Per-homework Docker/Nix/Bazel/Nx orchestration | Duplicates metadata; PlatformIO already isolates projects |
| Custom static site generator | Reinvents MkDocs; creates maintenance burden |
| Mandatory HIL for every homework | Hardware is scarce; many assignments teach logic that host tests cover |
| Presenting simulation as hardware evidence | Misleads reviewers; every result carries a provenance label |
| Automatic pinout generation for every board | Board profiles drift; a wrong generated diagram is worse than a linked official one |
| One giant PlatformIO project with a shared `src/` | Couples every homework and prevents independent grading and flashing |
| Bespoke tooling or templates per homework | 30× maintenance; reviewers cannot compare work |
| Badge walls and 100% coverage targets | Vanity metrics; coverage is not evidence of correctness |
| Fully autonomous agent mode without checkpoints | Silent assumptions, unsafe flashing, accidental commits |
| Hand-maintained index, workspace, and navigation | Guaranteed drift at 30+ homeworks |
| Mandatory AI-assistance disclosure | The course does not require it (user decision, 2026-10-23); voluntary mention is allowed |
| Nightly full simulation matrix | Free-tier simulation quotas cannot sustain it; weekly full simulation if adopted |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 4 | Complete |
| FOUND-02 | Phase 1 | Complete |
| FOUND-03 | Phase 1 | Complete |
| FOUND-04 | Phase 1 | Complete |
| FOUND-05 | Phase 1 | Complete |
| FOUND-06 | Phase 1 | Complete |
| FOUND-07 | Phase 1 | Complete |
| FOUND-08 | Phase 1 | Complete |
| FOUND-09 | Phase 2 | Complete |
| FOUND-10 | Phase 1 | Complete |
| META-01 | Phase 4 | Complete |
| META-02 | Phase 4 | In review (D-09 paraphrase check) |
| META-03 | Phase 4 | Complete |
| META-04 | Phase 4 | Complete |
| META-05 | Phase 5 | Pending |
| META-06 | Phase 5 | Pending |
| META-07 | Phase 5 | Pending |
| META-08 | Phase 5 | Pending |
| ARCH-01 | Phase 3 | Complete |
| ARCH-02 | Phase 3 | Complete |
| ARCH-03 | Phase 3 | Complete |
| ARCH-04 | Phase 2 | Complete |
| ARCH-05 | Phase 3 | Complete |
| ARCH-06 | Phase 3 | Complete |
| ARCH-07 | Phase 3 | Complete |
| REPORT-01 | Phase 10 | Pending |
| REPORT-02 | Phase 10 | Pending |
| REPORT-03 | Phase 10 | Pending |
| REPORT-04 | Phase 10 | Pending |
| REPORT-05 | Phase 10 | Pending |
| REPORT-06 | Phase 10 | Pending |
| REPORT-07 | Phase 10 | Pending |
| REPORT-08 | Phase 10 | Pending |
| SIM-01 | Phase 11 | Pending |
| SIM-02 | Phase 7 | Pending |
| SIM-03 | Phase 7 | Pending |
| SIM-04 | Phase 8 | Pending |
| TOOL-01 | Phase 6 | Pending |
| TOOL-02 | Phase 6 | Pending |
| TOOL-03 | Phase 6 | Pending |
| TOOL-04 | Phase 6 | Pending |
| TOOL-05 | Phase 8 | Pending |
| TOOL-06 | Phase 8 | Pending |
| TOOL-07 | Phase 1 | Complete |
| TOOL-08 | Phase 10 | Pending |
| FLOW-01 | Phase 9 | Pending |
| FLOW-02 | Phase 9 | Pending |
| FLOW-03 | Phase 9 | Pending |
| FLOW-04 | Phase 9 | Pending |
| FLOW-05 | Phase 9 | Pending |
| FLOW-06 | Phase 9 | Pending |
| FLOW-07 | Phase 9 | Pending |
| PILOT-01 | Phase 11 | Complete |
| PILOT-02 | Phase 11 | Pending |

**Coverage:**
- v1 requirements: 54 total
- Mapped to phases: 54
- Unmapped: 0

**Phase summary:**
- Phase 1: 9 requirements (FOUND-02–08, FOUND-10, TOOL-07)
- Phase 2: 2 requirements (FOUND-09, ARCH-04)
- Phase 3: 6 requirements (ARCH-01–03, ARCH-05–07)
- Phase 4: 5 requirements (FOUND-01, META-01–04)
- Phase 5: 4 requirements (META-05–08)
- Phase 6: 4 requirements (TOOL-01–04)
- Phase 7: 2 requirements (SIM-02, SIM-03)
- Phase 8: 3 requirements (TOOL-05, TOOL-06, SIM-04)
- Phase 9: 7 requirements (FLOW-01–07)
- Phase 10: 9 requirements (REPORT-01–08, TOOL-08)
- Phase 11: 3 requirements (PILOT-01, PILOT-02, SIM-01)

---

*Requirements defined: 2026-10-23*
*Last updated: 2026-10-25 after the ceremony trim exploration*
