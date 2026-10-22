# Project Research Summary

**Project:** Homeworks — Embedded Engineering Course
**Domain:** Embedded engineering course monorepo — 30+ independent PlatformIO projects (ESP32 Arduino/ESP-IDF, Arduino AVR, STM32), academic reports, simulation evidence, CI, generated documentation site
**Researched:** 2026-10-23
**Confidence:** MEDIUM-HIGH overall. HIGH for build/lint/docs mechanics; MEDIUM for the ESP-IDF language-server path and CI quota fit; MEDIUM-LOW for the final simulator choice, which the spike must settle.

## Executive Summary

This repository is not a product and not a platform: it is an evidence-grade academic and engineering record for 30+ course assignments at 2–3 per week. The research converges on a single architecture: **a monorepo of independent, disposable PlatformIO projects over a small, strictly layered C core, with every repeated artifact generated from one metadata file.** `homework.yaml` is the keystone contract; the README index, MkDocs navigation, VS Code workspace, CI matrix, and shared-library wiring are all derived from it and all carry a `--check` drift gate. The shared layer is `common` (pure C) → `port` (contracts only) → `arduino`/`espidf` adapters plus `host` test doubles. There is no universal HAL — the course assesses Arduino and ESP-IDF themselves.

Three research findings change decisions currently recorded in PROJECT.md and must be settled before scaffolding: `lib_extra_dirs` is deprecated in favour of `lib_deps = name=symlink://...`; "ESP-IDF style" is AStyle-defined (120 columns), not clang-format, so clang-format is a documented approximation; and the simulation priority is Wokwi-first with Velxio as a self-hosted fallback, not Velxio-first. Two further constraints shape the roadmap: MkDocs Material is in maintenance mode with a hard end-of-life on 2027-05-05, and free-tier simulation CI quotas cannot sustain a nightly full simulation matrix.

The dominant risks are structural, not technical: an over-grown `port` layer becoming a shadow framework; secrets or instructor-owned material reaching a public history that the Git policy forbids rewriting; cloud simulation becoming a flaky blocking check; and CI cost exploding at 30 projects. All four are addressed by ordering: policy before the first public push, the dependency rule enforced in the same phase as the first shared library, and a timeboxed simulation spike before any CI simulation gate.

## Key Findings

### Recommended Stack

PlatformIO Core 6.2.0 with `platformio/espressif32` 8.0.0 (Arduino core 3.3.12 / ESP-IDF 5.5.5; ESP-IDF 6.1 for `framework = espidf`) and `platformio/ststm32` 20.0.0. Native Unity tests run on the host. Shared libraries are consumed with `lib_deps = <name>=symlink://../../lib/<name>` and each library carries a `library.json`; this was validated end-to-end locally (native build linked `libcommon.a` and produced a correct `compile_commands.json`). The ESP32-S3-DevKitC-1 N16R8 requires explicit overrides (`qio_opi`, 16 MB flash, octal PSRAM); the stock board manifest is an 8 MB no-PSRAM board and silently misconfigures PSRAM.

Documentation is MkDocs Material 9.7.7 with pymdown-extensions 12.3 and vendored KaTeX 0.19.0, built by a deterministic `gen_docs.py` tree and deployed via `upload-pages-artifact` / `deploy-pages` (never `gh-deploy`). Quality is clang-format 23.1.3, clang-tidy 23.1.3 on host code only, pre-commit 4.7.0, gitleaks 8.30.1, markdownlint-cli2 0.24.0, yamllint 1.38.0, check-jsonschema 0.38.2, ruff 0.17.2. Git LFS uses the 10 GiB/10 GiB free tier with a narrow, size-based policy.

**Core technologies:**
- PlatformIO Core 6.2.0 + espressif32 8.0.0 — single build system for Arduino, ESP-IDF, STM32, native tests — supports all frameworks without a second toolchain; 8.0.0 is only days old, so pin and smoke-test it.
- `symlink://` library dependencies — shared code reuse across 30+ projects — replaces the deprecated `lib_extra_dirs` and makes dependency intent explicit.
- Wokwi CLI 0.29.0 — primary simulation and wiring source of truth — best ESP32 fidelity, `diagram.json`, mature headless assertions/screenshots.
- Velxio (Docker) — self-hosted/offline fallback — AGPLv3, real QEMU ESP32, but self-host image is AVR/RP2040/ESP32 only and CI is paid.
- Renode 1.17.0 — headless STM32 tests — MIT, Robot Framework CI, F103/F4-class platforms.
- MkDocs Material 9.7.7 — public documentation site — stable and well-documented today, but in maintenance mode with 2027-05-05 EOL.
- Git LFS + GitHub Actions + Pages — binary assets and publication — artifact deployment keeps the protected-branch model intact.

### Expected Features

The feature research is explicit that excellence comes from a small set of artifacts that make each homework independently buildable, testable, inspectable, and believable — not from tool count.

**Must have (table stakes):**
- Per-homework project isolation, `module_lesson-name` identity, and a schema-validated `homework.yaml` — the keystone contract for every generator.
- Assignment provenance (`task.md` = English paraphrase + source + retrieval date) — a public repo cannot republish instructor material.
- A complete report package: 10 sections, BOM, pin map/wiring, electrical calculations with assumptions, safety checklist, evidence table with provenance labels, traceability matrix, IEEE references, AI-assistance disclosure.
- Native Unity tests for pure logic; layered CI (pre-commit / pre-push / PR / nightly); pinned toolchain; one documented command path.
- Template plus deterministic `new-homework`; generated index and per-homework README; honest status and limitations.
- License and secret/PII hygiene; asset and LFS policy; a VS Code onboarding path including a no-hardware simulation route.

**Should have (competitive):**
- Simulation evidence in CI (`DF-01`) — rare in course repos, but only after the spike and ADR.
- Metadata-driven MkDocs site and generated multi-root workspace (`DF-03/DF-04`) — after the manifest survives the pilot.
- Metadata-driven selective CI matrix with shared-library fanout (`DF-05`).
- Versioned project-local agent skills (`DF-07`), guided vs one-shot modes (`DF-06`), ADR log (`DF-08`), release bundles and portfolio pages (`DF-09/DF-10`).

**Defer (v2+):**
- HIL (`DF-02`), fault injection (`DF-13`), dev container (`DF-14`), adaptive question bank, concept map. Each has an explicit trigger in FEATURES.md.

**Deliberately excluded:** universal HAL, pre-scaffolding 30 homeworks, DOCX/PDF as source of truth, autograder/gradebook, committed videos, committed course materials, MISRA, per-homework Docker/Nix/Bazel, custom static site generator, mandatory HIL, presenting simulation as hardware evidence, badge walls and coverage theater.

### Architecture Approach

A monorepo of independent PlatformIO projects over a thin shared core, with metadata-driven generation. Allowed dependency edges are `common → port`, adapter → port, host → port, and homework → common + port + exactly one adapter; `common` never depends outward. Each homework carries its own `platformio.ini`, `.clangd`, `diagram.json`, report, and tests; a top-level `tests/` PlatformIO project owns the shared-library suite. `scripts/affected.py` maps a git diff to a build/simulation matrix, including the critical edge that a `lib/**` change fans out to every consumer.

**Major components:**
1. `lib/port` — C function-pointer contracts (`time`, `gpio`, `i2c`, `spi`, `log`); no framework headers, no state.
2. `lib/common` — pure C domain logic (patterns, state machines, timing math, codecs, calculations); never blocks or sleeps.
3. `lib/arduino`, `lib/espidf`, `lib/host` — thin adapters and deterministic test doubles; adapters contain no business logic.
4. `homeworks/<id>` — composition root: wiring, framework idioms, report, evidence.
5. `scripts/` + `schemas/` — deterministic generators with `--check`, metadata validation, architecture check, simulation provider adapter.
6. `tests/` — native PlatformIO project proving the dependency rule by compiling `common`/`port` without a target toolchain.
7. `.github/workflows` — orchestration only: `meta` → `changes` → build/test/simulate → `gate`; nightly full matrix; docs deploy.

### Critical Pitfalls

1. **Shadow HAL** — `port` grows into a private framework and hides the APIs being taught. Prevent with the second-consumer rule, a CI grep for framework includes in `common`/`port`, and a native compile gate.
2. **Secrets and instructor material in public history** — unrecoverable under the no-rewrite Git policy. Prevent in the first phase with `.gitignore`, gitleaks (staged and full history), push protection, and a copyright/academic-integrity ADR before the first public push.
3. **Simulation as a blocking, flaky cloud check** — token/network/timeout failures turn a gate red on correct code. Prevent by making build/native tests the required checks and simulation label-gated or scheduled, with artifacts captured on failure.
4. **CI cost/time explosion** — full matrix per PR plus metered simulation minutes exceeds free tiers by roughly an order of magnitude. Prevent with changed-project detection, cache keys over all `platformio.ini`/`library.json`, and a weekly rather than nightly full simulation.
5. **Unpinned platforms/libraries and fabricated or unlabeled measurements** — both destroy the "verifiable a year later" core value. Prevent with exact pins recorded in the report and a measurement ledger where "not measured" is an allowed explicit value.

## Simulation Tool Decision Matrix

| Criterion | Velxio | Wokwi | Fritzing | Renode |
|---|---|---|---|---|
| **Supported boards/frameworks** | Self-host: AVR, RP2040, ESP32 (Arduino, MicroPython, ESP-IDF). STM32 and Pi only on the hosted service (STM32 also needs Velxio Desktop + paid plan). | ESP32/S3/C3/C6, AVR (Uno/Nano/Mega/ATtiny85), RP2040, 3 STM32 boards (Nucleo-C031C6, Nucleo-L031K6, Blue Pill F103). Arduino, ESP-IDF, MicroPython/CircuitPython, Rust, custom `.bin`/`.elf`/`.uf2`. | Not a simulator. Any board for which a part exists; breadboard/schematic/PCB views only. | Cortex-M/STM32 only: STM32F103, F4/F4-Discovery, F412, F429 (`.repl` platforms covering GPIO, USART, I2C, SPI, timers, DMA, ADC, CAN, Ethernet). No ESP32/AVR. |
| **Self-host / offline** | Yes — Docker image `ghcr.io/.../velxio:master`, port 3080; ~30 s pull, 10–15 min first compose build. Offline capable, but limited board set. | No. Offline VS Code mode is a Pro feature; on-premise deployment on request. | Yes — desktop application, fully offline. | Yes — fully offline and headless. |
| **Wiring visualization** | High: canvas, board/component SVGs, SPICE electrical layer (currents/voltages/shorts), oscilloscope at ~8 ns GPIO resolution, 150+ components. | High: `diagram.json` version 1 (`parts`, `connections`, wire routing), large part library, clean rendering; lintable. | High for illustrations: manual breadboard layout, best-looking output for reports. | None — GPIO/text traces only. |
| **CI / headless** | Hosted `velxio-cli` + `velxio/velxio-ci-action@v1`; `lint` works offline, `run --expect-text` needs a paid token. **No documented self-hosted CI runner.** | Mature `wokwi-cli` 0.29.0: `--expect-text`, `--fail-text`, scenarios, `--screenshot-*`, `--vcd-file`, `--coverage-file`, `--heap-*`, GDB. Cloud service. | Weak: `-svg FOLDER` batch export + `-gerber FOLDER`, requires Qt offscreen/`xvfb`; no stable per-file API. | Excellent: `renode-test` + Robot Framework, `RENODE_CI_MODE=YES`, parallel `-j`, `antmicro/renode-test-action@v4`. |
| **License** | AGPLv3 for personal/educational/OSS; commercial license for proprietary/SaaS; contributor CLA. Network-served modifications trigger source-offer obligations. | Service proprietary; CLI MIT. Free for OSS/personal; commercial/Pro for commercial use. | Application GPLv3; docs and part designs CC BY-SA 3.0; explicit restriction on reusing part graphics in other software systems. | MIT. |
| **Setup effort** | Low (Docker) to medium (CI account and token); ESP-IDF compile and serial reliability unverified. | Low: install script, token, `wokwi.toml` + `diagram.json`. ESP-IDF needs a merged firmware image. | Medium/high: manual drawing; automated export is brittle. | High: platform scripts, Robot tests, device-tree matching. |
| **MkDocs embedding** | No documented iframe/embed API. Link to `velxio.dev` or a self-hosted URL. | Only an experimental alpha endpoint (`/_alpha/wembed/<project-id>`); not officially supported. | Export SVG/PNG and embed as an image — the normal path. | Screenshots and logs only. |
| **Maintenance** | Very active, but young (created 2026-03-03) and docs disagree internally (board counts, core versions). Risky as a long-term dependency. | Mature and active (`wokwi-cli` pushed 2026-10-20). | Active (1.0.8, 2026-08-12). | Active (1.17.0, 2026-09-07), maintained by Antmicro. |
| **Cost / quota** | Self-host free. CI: Free tier 0 minutes; Maker 200 min/month, 1 concurrent job, 5 min/run; Pro 2,000 min/month, 2 jobs, 10 min/run. | Rolling 30-day CI quota: Free 50 min, Hobby 200, Hobby+ 500, Pro 2,000. Session cap 5/5/10/50 min. Free OSS tier qualifies for this public MIT repo; firmware uploaded to cloud and deleted. | Free/paid download tiers; part library free. | Free (MIT). |
| **Recommended role** | Offline/self-hosted ESP32/AVR/RP2040 demo fallback; the spike's second candidate. | **Primary simulator and wiring source of truth.** | Optional report illustration only; `.fzz` never the source of truth. | STM32 headless tests **if** the board matches an existing platform; otherwise STM32 evidence is native tests + HIL. |

**Cost math (from STACK.md §3.7):** 30 homeworks × ~30 s simulated each ≈ 15 min per full pass; nightly for 30 days ≈ 450 min per 30-day window. Wokwi Free (50 min) supports about 3 full passes/month; Hobby+ (500 min) barely fits one nightly pass; Pro (2,000 min) is comfortable. ARCHITECTURE.md models shorter sessions (~10 s each → ~5 min/night, ~150 min/30 days), which is still over Free. **The two files disagree on simulated-seconds-per-homework; this must be measured in the spike, not assumed.** Either way, PR runs must be changed-only.

## Conflicts with PROJECT.md and required decisions

PROJECT.md was written before research. Each row below is a finding that contradicts or materially changes a recorded decision. "ADR" means a MADR file under `docs/decisions/`; "PROJECT.md update" means editing the requirement/Key Decisions table (and, where relevant, moving an item to Out of Scope with a reason).

| # | PROJECT.md says | Research says | Recommended resolution | Required action |
|---|---|---|---|---|
| 1 | Shared libraries consumed through `lib_extra_dirs` (Active requirements and Key Decisions). | PlatformIO docs mark `lib_extra_dirs` deprecated since 6.0, "will be removed in the next major release". Local 6.2.0 still works with no warning — a trap. `lib_deps = name=symlink://../../lib/name` validated end-to-end; target needs `library.json`. | Adopt `symlink://` as the primary mechanism, emitted into a generated per-homework `platformio.shared.ini`, with one generator switch to fall back to `lib_extra_dirs` if a blocking issue appears. Record the change of a stated requirement. | **Both**: ADR-0003 (`lib_extra_dirs` vs `symlink://`) and PROJECT.md update. This must land before scaffolding. |
| 2 | "clang-format (ESP-IDF style)" is the formatting bar. | ESP-IDF does **not** use clang-format; its official style is AStyle, configured by `tools/ci/astyle-rules.yml` (4 spaces, no tabs, 120-character max line, function brace on its own line). clang-format can only approximate it. | Standardize on clang-format 23.1.3 pinned everywhere with an explicit `.clang-format` (ColumnLimit 120, IndentWidth 4, `BreakBeforeBraces: Custom`, function braces on new line). Document it as an approximation, not as ESP-IDF style. Optionally add a separate AStyle check later; do not claim equivalence. | **Both**: ADR (formatting standard and approximation) and PROJECT.md wording update ("ESP-IDF-style approximation via clang-format"). |
| 3 | "clangd + compiledb + `--query-driver`" (Key Decisions) — the binary is unspecified. | Stock clangd 21 can parse `--target=xtensa` since LLVM 20 but does not know Espressif's `-mcpu=esp32s3` / ESP ISA extensions (`xespv`, `xesploop`, `xespdsp`). Espressif's fork (`esp-clang` via ESP-IDF tools, or pioarduino `tool-clangd-esp` 21.1.3) does; it also serves ARM and native. Apple `/usr/bin/clangd` is the wrong default for ESP32. | Use one esp-clangd instance for the whole workspace behind `scripts/clangd-wrapper.sh`, with explicit absolute `--query-driver` globs (`toolchain-*/bin/*`, `tool-*/bin/*`). Per-project `.clangd` provides `CompilationDatabase`; never use `--compile-commands-dir` in a multi-root workspace. Name one installation path in the onboarding guide. | **Both**: ADR (language-server toolchain) and PROJECT.md update. |
| 4 | A full spike evaluates **self-hosted Velxio**, Wokwi CLI, and Fritzing; simulation is framed Velxio-first. | Wokwi is the stronger primary: best ESP32 fidelity, `diagram.json` as a real format, mature headless assertions/screenshots, ESP-IDF support. Velxio is a credible self-hosted fallback but its OSS image excludes STM32 and its CI is paid/hosted. Fritzing is not a simulator and its part graphics are license-restricted. Renode is the only credible headless STM32 path; direct QEMU is not viable (no GPIO/I2C/DMA). | Reverse the priority: **Wokwi primary, Velxio fallback, Fritzing illustration-only, Renode for STM32 if the board matches**. Keep the spike and its pass/fail criteria; the spike now measures cost and ESP-IDF viability rather than deciding an unknown winner. Do not let Velxio become a hard dependency. | **Both**: ADR-0004 (simulator selection) and PROJECT.md update. The spike's decision rule: Wokwi wins unless it shows a blocking ESP-IDF/PlatformIO problem or unacceptable CI cost. |
| 5 | CI "runs tests and simulation, and runs a full matrix nightly." | Free-tier simulation quotas cannot sustain a nightly full simulation matrix: Wokwi Free 50 min/30 days vs ~150–450 min needed; Velxio Free has **no** CI at all. A full nightly *build* matrix is still reasonable; a full nightly *simulation* matrix is not. | Split the tiers: PRs build/test changed projects and simulate changed projects only; nightly runs the full build + native test matrix; full simulation runs **weekly** (or rotating subsets), or on a paid tier if measured cost justifies it. Simulation is never a required check for fork PRs. | **Both**: ADR (CI budget and simulation gating) and PROJECT.md update of the CI requirement. |
| 6 | "MkDocs Material" with no lifecycle note. | Material 9.7.7 entered maintenance mode in November 2025 and reaches **end of life 2027-05-05**. Successor Zensical is 0.0.71 (0.1.0 announced 2026-11-05), still too young for a public course repo. Material 9.7.5+ pins `mkdocs<2`. | Use Material 9.7.7 for the first milestone, but keep configuration **Zensical-compatible**: no `hooks:`, minimal plugins (search only), navigation generated by a script rather than a plugin, no `mkdocs-monorepo-plugin`/`macros`/`awesome-pages`. Set a hard re-evaluation date in Q1 2027, before the May 2027 EOL. | **Both**: ADR (docs platform and migration plan) and PROJECT.md update/note. |
| 7 | "Fritzing SVGs may be added for final report illustrations." | Fritzing's app is GPLv3, but part designs and breadboard graphics are CC BY-SA 3.0 and Fritzing explicitly restricts reuse of part graphics in other software. Embedding Fritzing part SVGs in an MIT repository/site is a licensing problem, not just attribution. | Allow Fritzing only as an **authoring tool for our own circuit illustrations**, with "created with Fritzing" attribution, and do not copy part graphics into the docs site or shared assets. Keep `diagram.json` as the source of truth; generate repo-owned SVG where possible. Prefer not to depend on Fritzing at all. | **PROJECT.md update** (tighten the requirement) plus a short **ADR** recording the license boundary. |
| 8 | "Git LFS is used for large binaries with size limits" — stated without a Pages interaction. | GitHub Pages **cannot serve Git LFS objects**. Any image referenced by the docs site must be a normal git object. LFS bandwidth (10 GiB/month free) is also consumed by every `lfs: true` checkout, and Pages has a 1 GB published-site cap. | Put only genuinely large, non-diffable binaries in LFS (`.fzz`, PDF, STEP/STL, ZIP, firmware dumps, large VCD). Never `.png`/`.jpg`/`.svg`/`.md`/`.yaml`/`.json` destined for the site. Optimize images, commit them normally, link videos externally, and default CI checkout to `lfs: false` except where binaries are needed. | **Both**: ADR (asset/LFS policy) and PROJECT.md update of the LFS requirement. |

### Additional disagreements surfaced between the four research files

These are not conflicts with PROJECT.md, but the files contradict each other and the roadmapper must not silently pick one.

1. **Where the simulation spike sits.** STACK.md puts it at Phase 3 (before the pilot); ARCHITECTURE.md puts the pilot at 5 and simulation at 6 (after the pilot); PITFALLS.md puts the spike at Phase 5 and the pilot at Phase 8; FEATURES.md puts the pilot slice second and simulation fourth. **Resolution:** run the timeboxed spike once the N16R8 build and metadata skeleton exist, and let the pilot's simulation scenario be the spike's validation artifact — the two share work. The ADR must precede any CI simulation gate and any report claim that depends on simulation.
2. **`lib_ignore` necessity.** STACK.md says `lib_ignore` is no longer needed with explicit `symlink://` dependencies; PITFALLS.md (C8, M2) still recommends an explicit `lib_ignore` list for the native environment. **Resolution:** with explicit symlinks the native environment only links `port`, `common`, and `host`, so `lib_ignore` is unnecessary for isolation; keep it only for genuine framework-bundled name conflicts. Verify in Phase 2 rather than assuming.
3. **`test_build_src` vs `build_src_filter`.** STACK.md recommends `test_build_src = true`; ARCHITECTURE.md notes PlatformIO docs mark it NOT RECOMMENDED. **Resolution:** prefer `build_src_filter` excluding the entry point; use `test_build_src = true` plus `#ifndef PIO_UNIT_TESTING` only as a documented fallback.
4. **`.clangd` database location.** STACK.md uses `CompilationDatabase: .` (project root); ARCHITECTURE.md uses `.pio/build/<env>`. Both work depending on where `compiledb` writes. **Resolution:** standardize on `COMPILATIONDB_PATH` = project root via the shared pre-script, then `CompilationDatabase: .`; do not commit the database.
5. **`--query-driver` breadth.** STACK.md warns against `--query-driver='**'` (executes arbitrary binaries); ARCHITECTURE.md calls a broad glob correct. **Resolution:** explicit absolute PlatformIO toolchain globs — broad in coverage, narrow in trust.
6. **Simulated seconds per homework.** STACK.md assumes ~30 s (15 min/pass); ARCHITECTURE.md assumes ~10 s (5 min/night). **Resolution:** measure in the spike; do not let a planning estimate become a quota commitment.

## Implications for Roadmap

Phases must be small, each ships a working increment, and no phase pre-scaffolds speculative work. The ordering below reconciles all four files.

### Phase 0: Repository foundation and policy gate
**Rationale:** Secrets, LFS rules, license, and the copyright/academic-integrity decision cannot be retrofitted under a no-rewrite Git policy. This is a gate, not setup.
**Delivers:** `.gitignore`, `.gitattributes`, LFS policy, MIT license + NOTICE, protected `main`, branch/PR/tag policy, gitleaks (staged + full history), push protection, three PR templates, `AGENTS.md` skeleton, ADR-0001 (monorepo), ADR-0002 (ports and adapters), ADR-0003 (symlink vs `lib_extra_dirs`).
**Addresses:** TS-18/19/20/24, TS-02.
**Avoids:** C4 (secrets), C5 (copyright), C6 (LFS), C14 (traceability), M16 (branch hygiene).

### Phase 1: Toolchain truth
**Rationale:** Every later artifact depends on a working build and a settled library mechanism. espressif32 8.0.0 is days old and the ESP-IDF `compiledb` path is unverified.
**Delivers:** pinned PlatformIO 6.2.0 and espressif32 8.0.0; validated N16R8 configuration (flash/PSRAM/partitions); `pio/base.ini` + `extends`; one native build consuming `lib/common` via `symlink://`; `compiledb` for Arduino and ESP-IDF; `tests/` native project skeleton; a written spike result on `extends` + relative symlink resolution.
**Uses:** STACK §1.
**Avoids:** C7 (unpinned versions), C8 (library leakage), M1/M2.

### Phase 2: Shared core
**Rationale:** The dependency rule must be enforced before consumers accumulate; the shared layer must be built from real duplication, not speculation.
**Delivers:** `lib/port` (time/gpio/i2c/spi/log contracts), minimal `lib/common` (ring buffer, timing math, pattern logic), `lib/host` fakes with explicit fake time, `tests/` suite, `check_architecture.py` grep plus native compile gate.
**Addresses:** TS-13, TS-22 (minimal).
**Avoids:** C1 (shadow HAL), C3 (dependency-rule drift), C15 (premature abstraction), M7/M8/M9.

### Phase 3: Metadata contract and scaffolding
**Rationale:** TS-03 is the keystone; generators built before the contract is stable create four consumers of a moving schema.
**Delivers:** `schemas/homework.schema.json` (`additionalProperties: false`), `boards/*.yaml` + schema, `templates/` (Arduino, ESP-IDF, report), `scripts/new_homework` (idempotent, `--dry-run`, refuses overwrite), `validate_metadata.py`, `gen_index`, `gen_nav`, `gen_workspace`, `gen_shared_ini`, all with `--check`, and `scripts/affected.py`.
**Addresses:** TS-01/02/03/04/16/17 (minimal), DF-05 groundwork, DF-08.
**Avoids:** M12 (generated drift), AF-02/AF-17.

### Phase 4: Developer experience and quality layering
**Rationale:** clangd failures are tolerable for one pilot and corrosive for 30 projects and a novice user; formatting churn must be settled before code volume grows.
**Delivers:** `scripts/clangd-wrapper.sh` (esp-clangd), generated per-project `.clangd`, `.clang-format`, `.clang-tidy` (host code only), pre-commit + pre-push hooks, onboarding guide including a no-hardware path.
**Addresses:** TS-21, TS-25, DF-08.
**Avoids:** C9 (clangd headers), M4/M5/M6 (clangd conflicts, multi-root, GCC flags), AF-07.

### Phase 5: Simulation spike and ADR-0004
**Rationale:** Simulation is the only high-uncertainty decision; its limitations determine the testing tiers, the evidence wording, and whether CI simulation is viable at all.
**Delivers:** measured evidence for Wokwi (ESP32-S3 Arduino, ESP-IDF merged image, CI minutes, STM32 if applicable), Velxio (Docker cold start, ESP-IDF compile, serial, no STM32), Fritzing (headless `-svg FOLDER` under `xvfb`, license note), Renode (matching `.repl`, Robot UART/GPIO test); a simulator limitations matrix; ADR-0004 with measured minutes.
**Uses:** STACK §3.
**Avoids:** C10 (simulation ≠ hardware), C11 (blocking cloud sim), M14 (unsupported parts).

### Phase 6: Pilot homework 1.3 end-to-end
**Rationale:** Close the loop on one homework before scaling; the pilot is the template's real test.
**Delivers:** Police Flasher with all extensions (third LED, variable speed, complex pattern, single-GPIO), native tests, `assets/diagram.json`, `wokwi.toml`, simulation evidence with provenance, full 10-section report with BOM/pin map/calculations/safety/traceability/IEEE references/AI disclosure, `hw/1_3-police-flasher` tag after merge.
**Addresses:** TS-05–TS-12, TS-23, TS-26, TS-14 (initial).
**Avoids:** C10, C12, C13 (fabricated measurements), M13/M15/M17.

### Phase 7: Fast CI
**Rationale:** CI should start with lint/metadata and changed-project builds; adding cloud simulation first creates the exact cost and flakiness traps.
**Delivers:** `meta` job (schema, `--check` drift, lint, gitleaks, `check_architecture`, `wokwi-cli lint`), `affected.py` matrix, native tests, changed builds, `gate` as the single required check; simulation added only for changed projects with an explicit timeout and artifact upload.
**Addresses:** TS-14, DF-01 (partial), DF-05.
**Avoids:** C11, C16, M10/M11.

### Phase 8: Documentation site
**Rationale:** Independent of simulation; can proceed in parallel once metadata generation is stable. Deferring it avoids building a site over an unstable contract.
**Delivers:** `mkdocs.yml` (Zensical-compatible), generated `docs/SUMMARY.md`, `mkdocs-gen-files` report embedding (no copies), board pages from YAML, KaTeX vendored, `build --strict`, Pages artifact deploy, link check.
**Addresses:** DF-04, TS-17, DF-10.
**Avoids:** AF-09, AF-17, M12.

### Phase 9: Scale-out and hardening
**Rationale:** Only after the pilot closes the loop; then 2–3 homeworks per week with measured budgets.
**Delivers:** ESP-IDF adapter and template, remaining skills promoted from stubs (`hw-flash`, `hw-report`, `schematic`, `simulate`, `course-index`), weekly full simulation, sharded nightly build, LFS audit, optional HIL workflow, concept map.
**Addresses:** DF-02/DF-06/DF-07/DF-12/DF-13.
**Avoids:** C16, M17, AF-10.

### Phase Ordering Rationale

- Policy precedes the first public push because history rewriting is forbidden; a secret or course PDF cannot be undone.
- The metadata contract precedes every generator; building generators first creates four consumers of an unstable schema.
- The dependency rule is enforced in the same phase as the first shared library; retrofitting it across 30 homeworks is a repo-wide cleanup.
- The simulation spike precedes the CI simulation gate and the pilot's evidence claims, but the pilot can begin as soon as the N16R8 build works; the spike's scenario and the pilot's scenario are the same artifact.
- Documentation is deliberately deferred to Phase 8: it is independent of simulation and must not consume effort before the manifest stabilizes, but it must exist before scale-out.

**Critical path:** Phase 0 → 1 → 2 → 3 → 6. Phases 4, 5, and 8 can run partly in parallel; Phase 7 needs 2+3; Phase 9 needs 6+7.

### Research Flags

Needs deeper research during planning:
- **Phase 1:** espressif32 8.0.0 regression risk (four days old) and ESP-IDF `compiledb` completeness — the local validation was blocked by a broken ESP-IDF Python environment, not by PlatformIO.
- **Phase 5:** the simulation spike itself; measure minutes and fidelity, do not assume. Also the Wokwi ESP-IDF `merge_bin` workflow with the 16 MB N16R8 layout.
- **Phase 8:** MkDocs topology (`projects` plugin vs a single generated tree), literate-nav vs gen-files, and the Zensical migration trigger.
- **Phase 9:** CI cost/time modeling at 30 projects, LFS bandwidth, and simulation quota cadence.

Standard patterns (skip research-phase):
- **Phase 0:** Git policy, LFS, gitleaks, PR templates.
- **Phase 2:** ports-and-adapters in C and native Unity testing are well documented.
- **Phase 4:** clang-format/clang-tidy/pre-commit configuration.
- **Phase 7:** GitHub Actions matrix, caching, and least-privilege patterns.

## Confidence Assessment

| Area | Confidence | Notes |
|---|---|---|
| Stack | HIGH (core) / MEDIUM (edges) | PlatformIO versions, `symlink://`, clang-format/tidy, LFS limits, MkDocs EOL all verified against official docs; `symlink://` validated locally. MEDIUM for espressif32 8.0.0 stability, ESP-IDF `compiledb`, and the Wokwi CI cost model; MEDIUM-LOW for Velxio capability claims (young project with internally inconsistent docs). |
| Features | MEDIUM | Cross-checked against real course repos, university report guides, and repository standards, but the exact mix is a synthesis, not a single source. HIL value for a single-student course is unproven. |
| Architecture | MEDIUM-HIGH | PlatformIO project model, GitHub Actions, MkDocs, and clangd mechanics verified against official docs; ports-and-adapters convergence is well supported. Velxio maturity is LOW and belongs to the spike. |
| Pitfalls | HIGH (technical) / MEDIUM (policy) | PlatformIO, clangd, Git/GitHub, and simulation facts are HIGH. Institution-specific copyright, academic-integrity, and AI-use policies were not available and must be confirmed by the user. |
| Simulation choice | MEDIUM / MEDIUM-LOW | Wokwi's capabilities, CLI, and quotas are HIGH confidence, but the free-tier CI eligibility and real runtime need measurement; Velxio is MEDIUM at best. |

**Overall confidence:** MEDIUM-HIGH. The build, quality, and docs decisions are safe to plan against. The simulator and CI budget decisions are evidence-based only after Phase 5.

### Gaps to Address

- **Institution policy (copyright, AI use, public posting of solutions)** — unknown; must be resolved before the first public push. Blocks Phase 0 sign-off.
- **STM32 board models** — unconfirmed. Renode and Wokwi support depend on F103/F4-class or Nucleo-C031/L031. Keep the STM32 template and board profile unimplemented until confirmed; fall back to native tests + HIL.
- **Wokwi CI quota on the real workload** — measure a 1.3 simulation and one complex lesson; decide Free (changed-only), Hobby+ (weekly), or Pro.
- **Velxio AGPL deployment scope** — local-only self-hosting is fine; serving a modified instance publicly has source-offer obligations. Keep Velxio at arm's length (Docker image reference, never vendored code).
- **ESP-IDF dual-framework** — treat as an experiment with an ADR; start from PlatformIO's official `examples/espidf-arduino-blink`, never raw IDF docs.
- **MkDocs → Zensical timing** — re-evaluate after Zensical 0.1.x ships (announced 2026-11-05); hard decision before 2027-05-05.
- **Multi-root clangd and per-folder servers** — `vscode-clangd` does not support one server per folder; if upstream changes, the `.clangd` approach remains a compatible fallback.
- **VS Code Wokwi extension and `assets/diagram.json`** — verify whether the extension can open the canonical file directly; otherwise generate a gitignored root copy and never commit two divergent copies.
- **PinViz adoption** — young (single maintainer, small user base); generate and commit output, never a build-time dependency.

### Open Questions Requiring Spikes or User Decisions

1. **User decision:** course/institution policy on public posting, paraphrasing, and AI disclosure; whether solutions may be public during the course.
2. **User decision:** confirm STM32 board models and whether STM32 simulation matters at all.
3. **Spike:** espressif32 8.0.0 stability on the N16R8, and fallback choice (7.x vs pioarduino).
4. **Spike:** ESP-IDF `compiledb` completeness and the clangd binary choice (`esp-clang` vs `tool-clangd-esp`).
5. **Spike:** Wokwi ESP-IDF merged-image workflow with 16 MB flash, custom partitions, and PSRAM.
6. **Spike:** measured Wokwi and Velxio minutes per homework and the resulting CI cadence.
7. **Spike:** Velxio Docker cold start, ESP-IDF compile, serial reliability, and AGPL deployment scope.
8. **Spike:** MkDocs topology (`projects` plugin vs single generated tree) and Fritzing headless export quality under `xvfb`.
9. **Spike:** `extends` across `extra_configs` and relative `symlink://` path resolution before generating 30 projects.
10. **Spike:** native test determinism (repeat the suite ~20× in CI) and whether `lib_ignore` is needed at all with explicit symlinks.

## Sources

### Primary (HIGH confidence)
- PlatformIO docs — `lib_extra_dirs` deprecation, symlink/local-folder libraries, `compiledb`, unit testing, `extra_configs`, GitHub Actions caching — https://docs.platformio.org/
- `platformio/platform-espressif32` v8.0.0 and `platformio/platform-ststm32` v20.0.0 release notes / board manifests.
- ESP-IDF code style guide (AStyle, `tools/ci/astyle-rules.yml`) — https://docs.espressif.com/projects/esp-idf/en/stable/esp32/contribute/style-guide.html
- Espressif-IDE clangd docs; pioarduino `tool-clangd-esp`; clangd compile-commands design and `vscode-clangd` multi-root issues.
- Wokwi docs — diagram format, CLI usage, CI limits/pricing, ESP32 fidelity, STM32 limitations, offline mode, embed alpha.
- Velxio repository and CI docs — architecture, AGPLv3, self-host scope (AVR/RP2040/ESP32 only), CI tiers.
- Fritzing 1.0.8 release, sketch format wiki, licensing FAQ, `main.cpp` CLI flags.
- Renode 1.17.0 release, testing/CI docs, supported STM32 boards; QEMU STM32 machine docs.
- MkDocs Material changelog/releases (9.7.7, maintenance mode, EOL 2027-05-05); Zensical releases; MkDocs Material math/publishing docs.
- GitHub Docs — Pages limits and LFS non-support; LFS billing; Actions limits and secure-use guidance.
- Local validation on 2026-10-23: PlatformIO 6.2.0, native build with `symlink://` succeeded and linked `libcommon.a`; `compiledb` produced two entries including the shared library; `lib_extra_dirs` still works silently on 6.2.0 (documented as deprecated).

### Secondary (MEDIUM confidence)
- FEATURES.md evidence base: Purdue ECE 362 `proton-labs`, Cornell ECE 4760 project pages, Photon Circus repository standards, Embedded Artistry README template.
- University report and safety guides (IIT, Rutgers, UW, UWI, WSU, CMU, UIUC, ASME) for report structure, BOM, traceability, and safety checklists.
- PITFALLS.md integration gotchas: `platform-espressif32` issue #1031, `platformio-core` issue #4092, `vscode-clangd` #38/#438, `vscode-cpptools` #7029/#11610.
- Architecture sources: Stubert ports-and-adapters, Grenning SOLID for embedded C, AUTOSAR layered architecture, Zephyr devicetree, STM32Cube HAL2/UM2298.

### Tertiary (LOW confidence, needs validation)
- Velxio board counts and version claims (internally inconsistent README vs GitHub description).
- HIL cost/benefit for a single-student course.
- Long-term maintenance cost of 30+ generated MkDocs pages and workspaces.
- PinViz maturity.

---

*Research completed: 2026-10-23*
*Ready for roadmap: yes — with the PROJECT.md conflicts in this document resolved first and Phase 5 flagged as the evidence gate for the simulator decision.*
