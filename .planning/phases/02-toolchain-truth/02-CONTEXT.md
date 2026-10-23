# Phase 2: Toolchain Truth - Context

**Gathered:** 2026-10-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Prove the pinned PlatformIO toolchain actually builds the two targets the course depends
on, and that shared libraries link through `symlink://` rather than the deprecated
`lib_extra_dirs`.

This phase ships a **temporary reference project** under `homeworks/` that a developer can
build with one command per environment, plus the shared configuration file those builds
consume, plus the five shared libraries as minimal but framework-real stubs. Nothing about
the shared *core* is designed here: `common` and `port` carry a version constant and one
trivial symbol, not the domain logic, Unity suite, or dependency-rule checker that Phase 3
owns.

What must be true at the end: `pio run` is green for `native`, `esp32s3_arduino`, and
`esp32s3_espidf`; the ESP32-S3 environment uses 16 MB flash and octal PSRAM; and
`compiledb` emits a `compile_commands.json` containing the shared-library sources for both
ESP frameworks.

</domain>

<decisions>
## Implementation Decisions

### Shared configuration

- **D-01:** There is exactly **one** shared configuration file, `platformio.shared.ini` at
  the repository root. Each project consumes it through
  `[platformio] extra_configs = ../../platformio.shared.ini` and inherits named sections
  (`[esp32s3_arduino]`, `[esp32s3_espidf]`, `[native_unity]`) with `extends`.
  — **Reversibility:** costly — moving the file later means editing `extra_configs` in
  every one of the 30+ homework projects, and a missed one builds with unpinned defaults.
- **D-02:** In Phase 2 the shared file is **written by hand and committed**. It is *not*
  generated. The generator arrives in Phase 5 (META-05).
- **D-03:** **Criterion 3 is explicitly re-read.** ROADMAP says "consumed ... from a
  generated `platformio.shared.ini`". In this phase the file is authored manually; only
  the *consumption* half of the criterion is satisfied. Phase 5 adds generation plus a
  `--check` drift gate. The planner and verifier must not claim generation happened here.
- **D-04:** `platformio.shared.ini` is **committed to git**, not gitignored. It is a
  source-of-truth configuration for a reproducible build, not a build product. The
  repository's "generated files are never committed" rule enumerates
  `compile_commands.json`, `site/`, and `.pio/`; this file is not in that list and must not
  be added to it.
- **D-05:** `.planning/research/ARCHITECTURE.md` line 220 ("`platformio.shared.ini` is
  generated per homework") is **superseded** by D-01. Downstream agents must not follow
  it. The research file stays untouched as a historical record.

### Reference project

- **D-06:** The reference project lives at `homeworks/0_0-toolchain-smoke/`. Its ID matches
  the repository pattern `^[0-9]+_[0-9]+-[a-z0-9-]+$`.
- **D-07:** It is **temporary**. When `tests/` and the Unity suite arrive in Phase 3, it is
  removed in a dedicated commit. Phase 3's plan must carry that deletion as an explicit
  task; otherwise a project that was never a homework silently enters the public homework
  index.
- **D-08:** It carries **no** `homework.yaml`, report, or `task.md`. Those artifacts belong
  to Phase 4 and Phase 10, and adding them here would make a throwaway build check look
  like coursework.

### Shared libraries

- **D-09:** `lib/common`, `lib/port`, `lib/arduino`, `lib/espidf`, and `lib/host` each get a
  `library.json` with `name`, `version`, `build.srcDir`, and `build.includeDir`. Every
  library starts at `0.1.0`.
- **D-10:** Each library exports **one trivial symbol** — enough to prove linking, nothing
  more. `common`'s symbol is called from the reference project's entry point so the linker
  cannot drop the library as unused.
- **D-11:** `lib/arduino` **includes `<Arduino.h>`** and calls one trivial Arduino API
  function; `lib/espidf` **includes an ESP-IDF driver header** (e.g. `<driver/gpio.h>` or
  `<esp_err.h>`) and calls one trivial API function. Without a framework header the ESP
  build proves only that the cross-compiler exists, which is not the point of the phase.
- **D-12:** Library versions are declared **only** in `library.json`. `lib_deps` entries
  carry the name and the symlink source, never a version:
  `common=symlink://../../lib/common`.
  — **Reversibility:** costly — the `lib/` directory names become the dependency-rule
  vocabulary (`common → port`, adapters → port) that Phase 3's checker enforces and every
  homework's `lib_deps` repeats.

### Environments and entry points

- **D-13:** The reference project defines **both** ESP environments — `esp32s3_arduino`
  and `esp32s3_espidf` — and both must build. Success criterion 4 names both frameworks,
  so covering one leaves it unproven.
- **D-14:** The N16R8 overrides are exactly: `board_build.arduino.memory_type = qio_opi`,
  `board_build.flash_mode = qio`, `board_build.psram_type = opi`,
  `board_upload.flash_size = 16MB`, `board_upload.maximum_size = 16777216`,
  `board_build.partitions = default_16MB.csv`. The stock `esp32-s3-devkitc-1` manifest
  (8 MB, no PSRAM) is never used unmodified.
- **D-15:** One entry file serves both ESP frameworks through **conditional compilation**:
  `#ifdef ARDUINO` provides `setup()`/`loop()`, the `#else` branch provides `app_main()`.
  PlatformIO defines `ARDUINO` for the Arduino framework, so a single `src/main.c` links in
  both environments.
- **D-16:** The `native` environment is proven by **`pio run -e native` only**. No
  `test_framework`, no `test/` directory, no Unity. The shared Unity suite and the
  top-level `tests/` project are Phase 3's.

### Compilation database

- **D-17:** One shared extra script lives at `scripts/pio/compiledb.py`, wired from
  `platformio.shared.ini` as `extra_scripts = pre:../../scripts/pio/compiledb.py`. There is
  no per-project copy.
- **D-18:** The generated `compile_commands.json` stays **gitignored** (already covered by
  `.gitignore` from Phase 1, D-21). Only the producing script is committed.

### Build order and evidence

- **D-19:** Build order is `native` → `esp32s3_arduino` → `esp32s3_espidf` → `compiledb`.
  The first end-to-end slice is a green native build with the symlinked libraries, which
  needs no toolchain download and proves the wiring; the riskier `espressif32@8.0.0` pin is
  exercised once the wiring is known good.
- **D-20:** The evidence of this phase is a **green `pio run` in the working session**. Build
  logs are **not** committed and not stored under `.planning/`. Committed logs age into
  false claims; the measurement and evidence contract is Phase 10's.

### Decision records

- **D-21:** `docs/decisions/0006-*.md` records the `symlink://` versus `lib_extra_dirs`
  decision, as carried forward from Phase 1 (D-27: numbering is sequential and permanent).
  — **Reversibility:** one-way — the ADR number is permanent and referenced from
  `docs/decisions/README.md` and from the rulebook; renumbering breaks published
  cross-references.

### Claude's Discretion

- Exact content of each stub symbol (a version-string accessor is the natural choice).
- The internal implementation of `scripts/pio/compiledb.py`.
- Whether the smoke project's `README.md` is one line or several, provided it states the
  project is temporary and is not coursework.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning artifacts
- `.planning/PROJECT.md` — core value, constraints, and the locked Key Decisions table
  (`symlink://`, pinned toolchain, `lib/` layout).
- `.planning/REQUIREMENTS.md` — **FOUND-09** (pinned PlatformIO Core 6.2.0,
  `platformio/espressif32` 8.0.0, explicit N16R8 overrides) and **ARCH-04**
  (`symlink://` with `library.json` per library and a `platformio.shared.ini`;
  `lib_extra_dirs` is a generator fallback only).
- `.planning/ROADMAP.md` §Phase 2 — goal, requirements, and the four success criteria.
- `.planning/STATE.md` — current position; records that `espressif32` 8.0.0 is unproven and
  the fallback (7.x or pioarduino) is not yet chosen.
- `.planning/phases/01-repository-foundation-and-policy-gate/01-CONTEXT.md` — D-21
  (`compile_commands.json` and `.pio/` gitignored), D-27 (ADR numbering is permanent; the
  symlink ADR is `0006`).

### Technical research
- `.planning/research/STACK.md` §1.3 — `extra_configs` + `extends` composition and the
  caveat that `extends` does not merge list values.
- `.planning/research/STACK.md` §1.4 — `lib_extra_dirs` deprecation, `symlink://` semantics,
  relative-path resolution, and the local validation on PlatformIO 6.2.0.
- `.planning/research/STACK.md` — the concrete `[esp32s3_arduino]` / `[esp32s3_espidf]` /
  `[native_unity]` block sketch and the N16R8 override values.
- `.planning/research/ARCHITECTURE.md` §"Shared Library Wiring — `lib_extra_dirs` vs
  `symlink://`" — comparison, recommendation, and per-project examples.
- `.planning/research/ARCHITECTURE.md` §compiledb — `pio run -t compiledb` and the extra
  script approach.
- `.planning/research/PITFALLS.md` — platform/board pinning, framework headers leaking into
  native builds, and `.pio/` state assumptions.
- `.planning/research/ARCHITECTURE.md` line 220 — **read only to see what D-05 overrides**;
  do not follow its "generated per homework" claim.

### Repository rules and existing decisions
- `AGENTS.md` — "Assets and generated files" (the enumerated never-commit list),
  "Homework identifiers" (the ID regex), and Conventional Commits.
- `docs/decisions/0001-monorepo-with-independent-projects.md` — one independent PlatformIO
  project per homework.
- `docs/decisions/0002-ports-and-adapters-no-universal-hal.md` — why `port` and the
  adapters exist as separate libraries.
- `docs/decisions/README.md` — the ADR status index that ADR-0006 must be added to.
- `.gitignore` — confirms `compile_commands.json` and `.pio/` are untracked.

### External references
- `https://docs.platformio.org/en/stable/projectconf/sections/platformio/options/generic/extra_configs.html`
  — `extra_configs` semantics, including which side wins on a duplicate key.
- `https://docs.platformio.org/en/latest/projectconf/sections/env/options/advanced/extends.html`
  — `extends` and its no-merge behaviour for list values.
- `https://docs.platformio.org/en/stable/projectconf/interpolation.html` — `${section.option}`
  interpolation as the supported way to merge shared options.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/check_policy.py` and `scripts/check_pr_templates.py` — the established shape for
  a deterministic script with `--check` drift semantics and `scripts/tests/` coverage.
  `scripts/pio/compiledb.py` joins this family as the first non-Python-checking script.
- `scripts/tests/` + `python3 -m unittest discover -s scripts/tests` — the repository test
  entry point any new script is expected to participate in.
- `.github/PULL_REQUEST_TEMPLATE/infra.md` — the template this phase's pull request uses
  (branch prefix `infra/`).

### Established Patterns
- Phase 1 shipped policy as committed data plus a checker; this phase mirrors that by
  committing `platformio.shared.ini` as data while deferring its generator.
- Generated artifacts are gitignored and must never be tracked; `compile_commands.json` is
  already in `.gitignore`.
- PlatformIO Core **6.2.0 is already installed** on the development machine, so the phase
  verifies the pin rather than installing it.

### Integration Points
- `platformio.shared.ini` at the repository root — consumed by every project via
  `extra_configs`; Phase 5 will generate it.
- `lib/{common,port,arduino,espidf,host}/library.json` — the Library Dependency Finder
  surface that Phase 3's dependency rule will enforce.
- `homeworks/0_0-toolchain-smoke/platformio.ini` — the reference composition of two ESP
  environments plus native.
- `scripts/pio/compiledb.py` — the extra script both ESP environments load.
- `docs/decisions/0006-*.md` and `docs/decisions/README.md` — the decision record and its
  index row.

</code_context>

<specifics>
## Specific Ideas

- The user chose the reference project location deliberately as `homeworks/0_0-…` rather
  than an `examples/` directory, then chose a temporary lifecycle: it exists to prove the
  build and is removed once `tests/` supersedes it.
- On the shared configuration file the user's first answer was "треба обговорити" and only
  after the PlatformIO `extra_configs`/`extends` semantics were explained did they choose
  the single root file. The conflict semantics (a duplicate key in the extra file wins) are
  why a single root file was preferred over copies.
- The user explicitly declined a generated file in this phase, accepting that criterion 3's
  "generated" wording is satisfied only in Phase 5.

</specifics>

<deferred>
## Deferred Ideas

- Generation of `platformio.shared.ini` from a board-profile source, plus a `--check` drift
  gate — Phase 5 (META-05).
- `tests/` PlatformIO project, the Unity suite, and `test_framework = unity` — Phase 3.
- Deletion of `homeworks/0_0-toolchain-smoke/` — Phase 3, as an explicit task in that
  phase's plan.
- `homework.yaml`, `task.md`, README index entries, and the report contract for the smoke
  project — not applicable; those belong to Phase 4 and Phase 10 for real homework.
- CI wiring for the builds (matrix, changed-only detection) — Phase 8.
- Fallback to `espressif32` 7.x or pioarduino if 8.0.0 fails — a contingency recorded in
  STATE.md, not a decision made in this phase.
- Architecture checker enforcing `common → port`, adapters → port — Phase 3 (ARCH-05).

</deferred>

---

## Amendments After Research (2026-10-23)

These four decisions were taken with the user after `/gsd-plan-phase 2` research
(`02-RESEARCH.md`) contradicted the original text. They override the bullet they name; every
other decision above stands unchanged.

- **D-15 (amended):** The entry point is **`src/main.cpp`**, not `src/main.c`. It carries three
  thin branches: `#ifdef ARDUINO` → `setup()`/`loop()`; `#elif defined(ESP_PLATFORM)` →
  `extern "C" void app_main()`; `#else` → `int main(void)` for `native`. Reason: Arduino core
  3.3.12 calls C++-mangled `setup`/`loop`, so a `.c` entry fails with
  `undefined reference to '_Z5setupv'`.
  **Library sources stay pure C** (`lib/*/src/*.c`), and each public header in
  `lib/*/include/` carries the standard `#ifdef __cplusplus / extern "C" {` guard so C++
  callers link against C symbols. This keeps future ESP-IDF/STM32 homework in pure C — the
  guard compiles to nothing under a C compiler.
- **D-21 (amended):** The ADR is **`docs/decisions/0007-*.md`**. `0006-public-commit-identity.md`
  already exists and `docs/decisions/README.md` reserves 0007 for this decision. Sequential,
  permanent numbering (Phase 1 D-27) forbids reusing 0006.
- **D-22 (new):** `-DBOARD_HAS_PSRAM` is added to `build_flags` of `[esp32s3_arduino]`. It is a
  separate key, not part of the D-14 override list; without it the Arduino core may not
  initialise octal PSRAM.
- **D-23 (new):** ESP-IDF build-generated files in the project tree — `CMakeLists.txt`,
  `src/CMakeLists.txt`, and `sdkconfig.<env>` — are **added to `.gitignore`**, never committed.
  This extends, and does not weaken, the AGENTS.md "generated files are never committed" rule.

**Additional research findings the plan MUST carry as tasks:**

- P2: the ESP-IDF builder looks for `default_16MB.csv` in
  `framework-espidf/components/partition_table/`, where it does not exist. The project must
  ship its own `default_16MB.csv` (keeping D-14 literal) plus `sdkconfig.defaults` with
  `CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y`, `CONFIG_SPIRAM=y`, `CONFIG_SPIRAM_MODE_OCT=y`.
- P1/P3: the three fixes (entry point, `extern "C"` guards, ESP-IDF partition/sdkconfig) must
  land **before** the first `pio run` of the affected environment, not as a later repair.
- Evidence for criteria 2 and 4 is taken from `esptool image-info` and from Python assertions
  over `compile_commands.json` / `sdkconfig.json` — never from re-reading `platformio.ini`.

---

*Phase: 2-Toolchain Truth*
*Context gathered: 2026-10-23*
*Amended after research: 2026-10-23*
