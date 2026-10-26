# Homeworks — Embedded Engineering Course

## What This Is

A public GitHub monorepo for 30+ homework assignments from an embedded engineering
course. Each homework is an independent PlatformIO project containing code, tests, an
academic report in Markdown, wiring diagrams, a bill of materials, engineering
calculations, and measured evidence. The repository also provides shared portable
libraries, central documentation, templates, deterministic scripts, and CI; the authored
decision and standards documents render directly in the repository view.

## Core Value

Every homework ships as a self-contained, reproducible, industry-standard engineering
artifact — code, evidence, and report — that can be understood and verified a year later.

## Requirements

### Validated

- ✓ Pinned PlatformIO toolchain — Core 6.2.0 and `platformio/espressif32` 8.0.0 build the
  ESP32-S3-DevKitC-1 N16R8 target (native, Arduino and ESP-IDF) with 16 MB flash and octal
  PSRAM proven from build artifacts — Phase 2 (FOUND-09)
- ✓ Shared libraries consumed through `lib_deps = <name>=symlink://../../lib/<name>` with one
  `library.json` per library; `platformio.shared.ini` was hand-authored in Phase 2 and is
  generated from the metadata pins since Phase 5 — Phase 2 (ARCH-04)
- ✓ Framework-free `lib/port` function-pointer contracts and pure `lib/common` primitives,
  with thin Arduino/ESP-IDF adapters and host fakes — Phase 3 (ARCH-01, ARCH-02, ARCH-03,
  ARCH-07)
- ✓ `scripts/check_architecture.py` plus a native compile gate enforce the dependency rule;
  the checker is green on the real tree, red on forbidden fixtures, and wired into
  pre-commit — Phase 3 (ARCH-05)
- ✓ A top-level `tests/` PlatformIO project compiles `common` and `port` natively and runs
  the Unity suite: 73 cases in 7 suites, identical results over 20 runs — Phase 3 (ARCH-06)
- ✓ `homework.yaml` validated by a JSON Schema 2020-12 with `additionalProperties: false`
  at every level; the checker exits 0 on a valid tree and 1 on every invalid probe — Phase 4
  (META-01)
- ✓ Six templates (`homework-arduino`, `homework-espidf`, `task`, `report`, `adr`,
  `board-profile`) exist and are covered by the template test suite — Phase 4 (META-03)
- ✓ `scripts/new_homework` is the only scaffold path: it is idempotent, supports `--dry-run`,
  refuses every overwrite and symlink escape, and produces a project that builds immediately
  (Arduino and ESP-IDF) — Phase 4 (FOUND-01, META-04)
- ✓ Homework IDs follow `^[0-9]+_[0-9]+-[a-z0-9-]+$` and must match the containing
  `homeworks/<dir>/`; the scaffold and checker enforce the same anchored pattern — Phase 4
- ✓ `task.md` carries the four provenance fields and a Cyrillic gate with an exact-path
  allowlist; the paraphrase-originality review was confirmed by the repository owner on
  2026-10-25 against the first real homework — Phase 4, confirmed in Phase 4.2 (META-02)
- ✓ Homework 1.3 runs end to end through the trimmed tooling as the tracer: scaffold,
  pattern library, Wokwi wiring, report, single-project CI, and a recorded friction log —
  Phase 4.2 (PILOT-01 first pass)
- ✓ One generator owns every repeated view: `scripts/gen_views.py` writes the root README
  index, `homeworks.code-workspace` and `platformio.shared.ini` from `homework.yaml`,
  recorded in a committed `generated.manifest` with a SHA-256 and byte count per entry;
  `--check` reports drift and never writes — Phase 5 (META-05, META-07)
- ✓ `scripts/affected.py` maps a git diff to a build/simulation matrix with `lib/**` fanout
  to every consumer, an explicit no-build-impact set, and fail-safe widening for any
  unrecognised path — Phase 5 (META-06)
- ✓ A MkDocs Material 9.7.7 site is generated from the same tree and published to GitHub
  Pages by an OIDC workflow after a warnings-as-errors build; the generated navigation and
  the vendored KaTeX 0.19.0 (checksum-pinned, no CDN) were verified on the live site —
  Phase 5 (META-08). **Superseded 2026-10-26:** the site is cut and the authored documents
  render in the repository view; see the 2026-10-26 row in `docs/decisions/README.md`.
- ✓ clang-format 23.1.3 as a documented ESP-IDF approximation (4 spaces, 120 columns,
  function brace on a new line), plus clang-tidy (bugprone, cert, performance, portability),
  markdownlint-cli2, yamllint, ruff and gitleaks, are pinned through pre-commit; the
  tracked tree is byte-clean under the check-only clang-format hook — Phase 6 (TOOL-01)
- ✓ esp-clangd serves the multi-root workspace through `scripts/clangd-wrapper.sh`, with
  per-project `.clangd` files and explicit `--query-driver` toolchain globs; the headless
  check is the attached form `--check=<file>`, because esp-clangd declares
  `--check[=<string>]` — Phase 6 (TOOL-02)
- ✓ Checks are layered locally: fast hooks in pre-commit (format, markdownlint, yamllint,
  ruff, gitleaks) and clang-tidy in pre-push, with a compile-database freshness guard;
  the CI layer remains Phase 8 — Phase 6 (TOOL-03)
- ✓ `docs/standards/vscode.md` onboards a VS Code beginner from install to the
  no-hardware check, and the committed editor contract matches `.vscode/settings.json` —
  Phase 6 (TOOL-04)
- ✓ The simulator decision is evidence-based: ADR-0014 records measured Wokwi costs (3/3
  runs, cold 3.759 s, warm 6.753/11.238 s), a digest-pinned Velxio self-host attempt, and
  explicit `not measured` rows for Renode and Fritzing, plus a calculated CI cost basis —
  Phase 7 (SIM-02)
- ✓ Homework 1.3 executes its Wokwi scenario end to end (3/3 exit 0, exactly one
  `pattern ready` line each); `simulation.status: verified` follows only a
  `scenario passed` outcome, and the shared `scripts/pio/merge_firmware.py` produces the
  merged image in a clean build — Phase 7 (SIM-02)
- ✓ The AGPL boundary holds: no Velxio source, image layer or Fritzing part graphic is
  vendored into the MIT tree; `diagram.json` remains the wiring source of truth — Phase 7
  (SIM-03)

### Active

**Repository and tooling**

- [ ] Shared libraries in `lib/` (`common`, `port`, `arduino`, `espidf`, `host`) consumed
      through `lib_deps = <name>=symlink://../../lib/<name>` with a `library.json` per
      library and a generated `platformio.shared.ini`; `lib_extra_dirs` remains a
      generator fallback only.
- [ ] Toolchain is pinned: PlatformIO Core 6.2.0, `platformio/espressif32` 8.0.0, and
      explicit ESP32-S3-DevKitC-1 N16R8 overrides (16 MB flash, octal PSRAM).
- [ ] `AGENTS.md` as the canonical rulebook (up to ~300 lines) with enforcement tags,
      short good/bad examples, and an agent quick-start; `.claude/CLAUDE.md` imports it.
- [ ] `docs/` organized into `boards/`, `protocols/`, `components/`, `theory/`,
      `standards/`, `decisions/`, and `sources.md`.

**Homework artifacts**

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
- [ ] A PlatformIO + export path covers course requirements that mandate another IDE.

**Quality**

- [ ] `scripts/check_architecture.py` and a native compile gate enforce the dependency
      rule.
- [ ] Reports include a measurement ledger labelling every value as measured,
      calculated, simulated, datasheet, or explicitly not measured, with instrument,
      method, uncertainty, and commit hash.
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
- [ ] The MkDocs Material configuration is re-evaluated in Q1 2027, before the 2027-05-05
      end-of-life; it stays Zensical-compatible until then.
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
| Thin core + port + adapters | Reuse without building a shadow framework | ✓ Phase 3 — five libraries, 21 headers, no framework leakage |
| No universal HAL | Hardware abstractions leak; the course must teach framework APIs | ✓ Phase 3 — bus-level I2C/SPI contracts; framework bus adapters deferred (ADR-0008 D-08) |
| Shared libraries via `lib_deps = <name>=symlink://...` | Replaces deprecated `lib_extra_dirs`; explicit dependency intent; validated locally | ✓ Phase 2 — ADR-0007; all three environments resolve the symlinked libraries |
| Multi-root VS Code workspace | Per-project clangd and PlatformIO behavior; auxiliary folders available | ✓ Phase 5 — generated whole from a template, committed, drift-checked |
| esp-clangd + per-project `.clangd` + compiledb | Stock clangd does not understand `-mcpu=esp32s3` and Espressif ISA extensions | ✓ Phase 6 — ADR-0013 multi-root contract; the headless check is `--check=<file>` because esp-clangd declares `--check[=<string>]` |
| Three-layer checks (pre-commit, pre-push, CI) | Fast local feedback with full verification in CI | ✓ Phase 6 — pre-commit and pre-push layers live; the CI layer is Phase 8 |
| clang-format 120 + clang-tidy (ESP-IDF approximation) | Consistent quality without MISRA overhead; AStyle-based ESP-IDF style is approximated and documented | ✓ Phase 6 — ADR-0012; clang-format 23.1.3 dry-run clean over 60 tracked C/C++ files |
| A documented command is regression-guarded | A guide command the tool rejects is worse than no command; a guard keeps the live form honest | ✓ Phase 6 — historical records left byte-identical; the prose guard is replaced by a behavioral one in the test-prune follow-up |
| One generated root compile database serves the shared libraries | clangd resolves a file from the nearest ancestor database; the per-project databases are siblings of `lib/`, so the shared sources had none | ✓ Phase 06.1 — `scripts/gen_clangd_db.py` merges the native, Arduino and ESP-IDF databases into one untracked root `compile_commands.json`; the root `.clangd` carries the proven keys; `templates/**/src/*` remain out of scope |
| 10-section report with BOM, calculations, safety, and industry notes | Academic completeness plus engineering rigor | — Pending |
| `task.md` + `homework.yaml` + `README.md` separation | Separates assignment, metadata, and result | ✓ Phase 4 — schema-validated contract; `task.md` carries provenance frontmatter (ADR-0009) |
| JSON Schema 2020-12 as the single metadata contract | One declarative field set read by editors, the checker, the scaffold and Phase 5 generators; anchored patterns instead of `format` | ✓ Phase 4 — `additionalProperties: false` at every level; unknown keys rejected |
| Pinned Python dependencies via PEP 723 + pre-commit `additional_dependencies` | One pin set shared by the scaffold, the checker and the hook; drift fails the suite | ✓ Phase 4 — ADR-0010; PyYAML 6.0.3 and jsonschema 4.26.0 |
| Unity + native environment | Fast, deterministic tests for pure logic | ✓ Phase 3 — 73 cases, 7 suites, 20 identical runs |
| Tiered testing | Avoids overhead while keeping evidence proportional to the work | — Pending |
| TDD for pure logic | Improves design and guarantees testability | — Pending |
| Protected `main`, PR, squash merge, tags | Auditable history and a clear entry point per homework | — Pending |
| Three PR templates | Type-specific evidence without a bloated universal template | ✗ Superseded by one default template — Phase 4.1 |
| Git LFS with limits | Handles large binaries without bloating the repository | — Pending |
| MIT license | Simple public portfolio license | — Pending |
| README index + MkDocs Material | One source of metadata renders both catalog and site | ✗ Superseded 2026-10-26 — the README index stays generated from the metadata; the site is cut and the authored docs render in the repository view |
| ADRs for infrastructure, assumptions in reports | Traceable decisions at the right scope | — Pending |
| Wokwi primary, Velxio fallback, Renode for STM32, Fritzing with attribution | Research shows Wokwi has the strongest ESP32 fidelity and CI; Velxio self-host excludes STM32 | ✓ Phase 7 — ADR-0014; Wokwi executed 3/3, Velxio digest-pinned, Renode and Fritzing `not measured` with reasons |
| Evidence labels are semantic: `measured`, `calculated`, `simulated`, `datasheet`, `not measured` | A simulated value presented as a bench reading is a defect, and quota cannot be inferred from wall clock | ✓ Phase 7 — the five-label ledger plus `calculated (upper bound)`; simulation is never bench evidence |
| The simulation status flip is gated by the evidence outcome token | Execution alone is not success; a failed or blocked scenario must not produce `verified` | ✓ Phase 7 — `simulation.status: verified` only on `**Outcome:** scenario passed` |
| MkDocs Material 9.7.7 with Zensical-compatible config | Stable today; re-evaluate in Q1 2027 before the 2027-05-05 EOL | ✗ Superseded 2026-10-26 — no site is built or deployed, so the theme pin and its EOL no longer apply |
| Git LFS only for large non-diffable binaries | Pages cannot serve LFS objects; LFS bandwidth is consumed by checkouts | — Pending |
| Pin PlatformIO 6.2.0 and espressif32 8.0.0 | Reproducible builds; 8.0.0 is new and must be smoke-tested | ✓ Phase 2 — smoke-tested; 16 MB and octal PSRAM proven from `sdkconfig.json` and image headers |
| Pilot 1.3 with all extensions in guided mode | Validates the full workflow before scaling to 30+ homeworks | — Pending |
| Seven thin skills, two fully implemented | Complete inventory without premature design | — Pending |
| Four deterministic scripts | Guarantees consistency for scaffolding, index, workspace, and validation | — Pending |
| Full template set from the first phase | Makes the correct structure the easiest path | ✓ Phase 4 — six templates, golden-tree tests, both homework templates build |
| `AGENTS.md` as canonical, imported by `CLAUDE.md` | Portable rules for Claude and Antigravity without duplication | — Pending |
| Ceremony trim: rule by frequency of execution | Bureaucracy that costs time on every change does not pay for itself; the GSD tiers and atomic commits stay | ✓ Phase 4.1 — policy-as-code, REUSE/SPDX, PR-template drift, tag gates and 16 meta-tests removed; four invariants kept |
| Decision records are table-first | A six-column index answers most questions without an ADR file | ✓ Phase 4.1 — `docs/decisions/README.md` is the index; 11 ADR bodies archived |
| One default PR template | Three type-specific templates were ceremony; one Definition of Done covers every type | ✓ Phase 4.1 — `.github/pull_request_template.md` is the only template |
| Minimal `tag_homework.sh` (D-3) | Git's own refusal semantics already prevent moving a published tag | ✓ Phase 4.1 — fetch and directory/merged-PR gates removed; consequences accepted as review rules (CR-01/CR-02 deferred in the review ledger) |
| Tracer before automation | Running homework 1.3 by hand records which friction is real; Phases 5–10 automate only what the log proves painful | ✓ Phase 4.2 — 19-entry friction log; every candidate owned by Phases 5–11 or recorded `not built` |
| One read-only CI job per homework | The first real run proves the job, not a matrix; matrix expansion waits for measured need | ✓ Phase 4.2 — `homework-1_3-police-flasher` green in 1m38s against a 45-minute timeout |
| `merge_firmware.py` stays project-local | espressif32@8.0.0 ships esptool 5 (`merge-bin`), so the published Wokwi script cannot run; promotion to `scripts/pio/` waits for Phase 7/8 | — Pending (tracked as a todo) |
| Wokwi execution deferred to Phase 7 | Only `wokwi-cli lint --offline` is a verified result; a simulation claim needs an executed run | ✓ Phase 4.2 — `simulation.status: pending`; the runnable command is documented |
| One generator + one committed manifest own every repeated view | A single owner removes the per-homework manual edits F-01/F-14/F-18 recorded, and a manifest with a digest per entry makes drift detectable without re-rendering | ✓ Phase 5 — `scripts/gen_views.py` over 8 paths; `--check` fails on `MODIFIED`/`DELETED`/`ORPHAN` and never writes |
| `--check` is a pure check, enforced at two points | A hook that repairs drift makes the gate meaningless; local feedback and a PR gate catch different trust boundaries | ✓ Phase 5, narrowed 2026-10-26 — the check-only pre-commit hook and the read-only PR job still guard the three core views; the Pages deploy is gone |
| Vendor third-party site assets, never a CDN | `--strict` builds must not depend on the network, and a missing `extra_css` target produces no MkDocs warning at all | ✗ Superseded 2026-10-26 — no vendored site asset remains; the three core views still render from their reviewed templates |
| Two critical code-review findings fixed before merge | A title could reach the published site as live HTML, and the generator followed symlinked inputs it otherwise refused | ✓ Phase 5 — `_escape_cell` escapes `&`/`<`/`>`; `read_regular_text` refuses symlinks; 20 lower findings recorded in the disposition ledger |

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

*Last updated: 2026-10-26 after Phase 07*
