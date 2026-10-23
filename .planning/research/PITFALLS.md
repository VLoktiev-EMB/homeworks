# Pitfalls Research

**Domain:** Embedded engineering course monorepo (PlatformIO, multi-framework, public, simulation-backed, academic reports)
**Researched:** 2026-10-23
**Overall confidence:** HIGH for PlatformIO, clangd, Git/GitHub, and simulation facts; MEDIUM for course-policy specifics (institution-dependent) and for long-term maintenance behavior at 30+ projects.

## How to read this document

Phase names below are indicative and should be mapped by name, not number, to the eventual
roadmap. Suggested phase vocabulary:

| Label | Indicative scope |
|-------|------------------|
| Phase 1 - Repository Foundation | License, `.gitignore`, `.gitattributes`, LFS policy, secrets scanning, protected `main`, branch/PR policy |
| Phase 2 - Templates and Metadata | Homework template, `homework.yaml` schema, validation scripts, docs skeleton |
| Phase 3 - Shared Libraries | `core` + `port` + adapters, dependency rule, native test project |
| Phase 4 - Developer Tooling | Multi-root workspace, clangd, `compile_commands.json`, tasks |
| Phase 5 - Simulation Spike | Velxio vs Wokwi vs Fritzing, pilot of homework 1.3 |
| Phase 6 - CI Pipeline | Lint, metadata checks, changed-project builds, tests, simulation, nightly matrix |
| Phase 7 - Testing Infrastructure | Unity native tier, HIL tier, contract tests, determinism rules |
| Phase 8 - Pilot Homework 1.3 | End-to-end validation of template, skills, report, CI |
| Phase 9 - Scale-out | 30+ homeworks, course operations, index/MkDocs |
| Phase 10 - Publication Hardening | Report audit, copyright review, disclosure, portfolio polish |

---

## Critical Pitfalls

Mistakes that cause rewrites, leaked secrets, unusable history, or a repo that cannot be
trusted a year later.

### Pitfall C1: Building a shadow HAL over Arduino and ESP-IDF

**What goes wrong:**
`lib/port` slowly grows `port_gpio_set()`, `port_delay_ms()`, `port_i2c_transfer()`,
`port_log()`, and a `port_result_t` enum. Every homework is then written against this
private framework instead of the framework the course teaches. The abstraction cannot
express ISR context, FreeRTOS task affinity, `esp_err_t` codes, Arduino `String`, or
`TickType_t`, so escape hatches appear (`port_get_native_handle()`). The result is a worse
version of Arduino with none of its documentation.

**Why it happens:**
"Reuse across 30+ homeworks" creates pressure to normalize everything. The first two
homeworks look similar enough that a common API seems obvious, and each new platform
difference is patched rather than accepted.

**How to avoid:**
- Enforce the stated architecture: thin `core` (pure C, no hardware), `port` (narrow
  capability interfaces only, e.g. "monotonic clock", "byte transport"), and per-framework
  adapters that are idiomatic Arduino/ESP-IDF.
- Apply the rule of three: a `port` interface is introduced only after the third concrete
  consumer, and only for behavior that is genuinely identical across frameworks.
- Review every new `port_*` function with the question: "Does this hide a framework concept
  the course is teaching?" If yes, reject it.
- Keep adapters thin enough that a student can read the adapter and the framework call side
  by side.

**Warning signs:**
- `lib/port` contains functions with more than two boolean parameters or an opaque
  `void *handle`.
- Adapters contain business logic, retries, or buffering.
- New homework code imports `port` for things that are one-liners in the native framework.
- `port_result_t` keeps gaining error codes that mirror `esp_err_t` one-for-one.
- Reviewers cannot explain what `port` would look like on a third platform.

**Phase to address:**
Phase 3 - Shared Libraries. Re-audit at Phase 8 and again after every fifth homework.

---

### Pitfall C2: Treating `framework = arduino, espidf` as a free combination

**What goes wrong:**
A project enables both frameworks expecting to call Arduino APIs and ESP-IDF APIs freely.
Builds fail with missing components, undefined `setup()`/`loop()`, or generated headers
that `idf.py` finds but `pio run` does not. Custom ESP-IDF components with
`target_include_directories(INTERFACE)` or `add_custom_command` produce headers that
PlatformIO's CMake-codemodel parsing does not propagate into the SCons environment.
`src_filter` is silently unsupported in ESP-IDF builds, and Arduino-as-component pins the
project to a specific IDF/Arduino-core pairing.

**Why it happens:**
The combination is documented and examples exist, so it looks first-class. The failure
modes are build-system-specific and only appear once real components are added.

**How to avoid:**
- Decide per homework which framework owns the project. Use dual-framework only when the
  course explicitly requires it, and start from PlatformIO's official
  `examples/espidf-arduino-blink`, never from raw IDF documentation.
- Keep custom ESP-IDF components in `components/` with real `CMakeLists.txt`; do not try to
  consume them through `lib_deps` or `lib_extra_dirs`.
- Pin the platform version and the Arduino core version together; record the compatible
  IDF version in the homework report.
- Treat dual-framework as an experiment with a written ADR, not the default template.

**Warning signs:**
- "works with `idf.py build` but not `pio run`" in any issue or commit message.
- `sdkconfig` changes that must be replicated manually after every clean build.
- Errors about `esp_driver_*`, `build_info.h`, or duplicate `setup`/`loop`.
- A homework's `platformio.ini` diverges substantially from the template.

**Phase to address:**
Phase 2 - Templates (separate templates), validated in Phase 8. Any dual-framework work
gets its own spike before entering a homework.

---

### Pitfall C3: Dependency-rule drift between shared layers

**What goes wrong:**
`lib/common` includes `<Arduino.h>`, `<freertos/FreeRTOS.h>`, or `<driver/gpio.h>`
"temporarily". Native tests stop compiling, or worse, compile with host headers and test
code paths that never run on target. Over months, the layering becomes decorative and the
only way to test is to build firmware.

**Why it happens:**
Framework headers are convenient, include order hides violations, and header-only
libraries make it easy to add a dependency without changing a build file. PlatformIO's
Library Dependency Finder also pulls in libraries transitively, so a violation can appear
without an explicit include in `common`.

**How to avoid:**
- CI job that greps `lib/common` and `lib/port` for forbidden framework includes and fails
  the build. Allowlist exact files if necessary.
- Compile `lib/common` in the native test environment on every PR. If it needs a framework
  header, it is not portable.
- Keep `extern "C"` headers for shared C code and compile the same sources in C and C++.
- Add a negative test: a tiny CI check that a framework header in `common` fails the build.

**Warning signs:**
- Native tests require `-I` paths pointing into `.pio/packages` or `.platformio`.
- `#ifdef ARDUINO` or `#ifdef ESP_PLATFORM` blocks multiplying in `common`.
- A shared library only builds after the firmware environment has been built once.
- Includes in `common` change when a new board is added.

**Phase to address:**
Phase 3 - Shared Libraries, enforced continuously from Phase 6 - CI.

---

### Pitfall C4: Secrets reach a public repository and its history

**What goes wrong:**
Wi-Fi SSID/password, API tokens, MQTT credentials, or a `secrets.h` file land in a commit.
Even after deletion, the blob remains reachable in history, forks, and cached views.
Because `main` is protected and force-push is forbidden, history cannot be rewritten;
rotation is the only real remedy, and by then the credential may already be scraped.

**Why it happens:**
Embedded examples hard-code credentials, `.gitignore` is added late, and `sdkconfig` or
build artifacts capture values. Local builds "work", so nobody audits the diff before the
first push.

**How to avoid:**
- Phase 1, before the first public push: `.gitignore` covering `secrets.h`, `.env`,
  `sdkconfig`, `.pio/`, `*.pem`, `*.key`, and local credential files.
- `gitleaks` in pre-commit and CI, plus GitHub secret scanning and push protection enabled.
- Credential injection via environment or a generated ignored header; document the pattern
  in the template and in `AGENTS.md`.
- Never commit real capture logs, config dumps, or `.pio` build trees.
- Rotate immediately on any suspected exposure; treat history rewriting as unavailable
  under the project's Git rules.

**Warning signs:**
- A diff contains a 20+ character high-entropy string, a base64 blob, or a private-key
  header.
- Homework config mentions a real network name.
- `git status` shows an ignored-looking file that is actually tracked.
- CI logs echo environment variables or full `platformio.ini` contents.

**Phase to address:**
Phase 1 - Repository Foundation. Re-verify in Phase 6 - CI and Phase 10.

---

### Pitfall C5: Publishing instructor-owned course materials or solutions under active assessment

**What goes wrong:**
Original assignment PDFs, slides, or Ukrainian task text are committed verbatim, or full
solutions are published while the course is still running. Course materials usually carry
automatic copyright owned by the instructor or university, and solutions may be derivative
works. Many institutions explicitly forbid public code repositories; publishing can trigger
academic-integrity action against the author and enable plagiarism by others.

**Why it happens:**
The repository is framed as a portfolio, and "it's my own work" feels sufficient. The
distinction between the student's code and the instructor's problem statement is easy to
miss, especially when the assignment is stored locally as a PDF.

**How to avoid:**
- Publish only an English paraphrase of the task plus a citation to a public source;
  never commit the original document, slides, or screenshots of them.
- Check the course's academic-integrity and IP policy before making the repo public, and
  record the decision in an ADR. If the policy is unclear, keep the repo private until the
  course ends.
- If solutions must be public during the course, delay publication per homework until after
  the submission deadline, or gate the repo behind a private period.
- Keep a `sources.md` with citations; do not paste long excerpts.
- The MIT license covers original code only; it does not grant rights to course text or
  third-party assets.

**Warning signs:**
- `task.md` contains long verbatim passages or embedded images from course slides.
- Assets include PDFs with course branding, or filenames matching instructor handouts.
- The repo is public before the course's policy has been read.
- Homework solutions appear before their deadlines.

**Phase to address:**
Phase 1 (policy decision and ADR) and Phase 10 (publication audit). Phase 8 pilot is the
first real test of the paraphrase workflow.

---

### Pitfall C6: Git LFS quota exhaustion and permanent history bloat

**What goes wrong:**
Photos, oscilloscope captures, screen recordings, PDFs, and board images are committed
directly or added to LFS retroactively. Even on a public repo, GitHub Free provides 10 GiB
LFS storage and 10 GiB monthly bandwidth; CI clones, forks, and repeated fresh clones
consume bandwidth. Deleting a file later does not reclaim storage because the object
remains in history. Migrating existing large files to LFS requires a history rewrite, which
the project forbids.

**Why it happens:**
Hardware work generates images and captures naturally. LFS is treated as unlimited because
the repo is public, and the migration path (rewrite history) is invisible until it is too
late.

**How to avoid:**
- Phase 1: define asset rules before the first homework. Prefer SVG for diagrams, compress
  images, keep screenshots under a size budget, and link videos instead of committing them.
- Add `.gitattributes` for known binary extensions on day one, not after files exist.
- Set a per-file size guard in pre-commit and a repository budget check in CI.
- Configure CI checkout with `lfs: true` only where needed, and avoid unnecessary full
  clones in matrix jobs.
- If a large file is committed by mistake, remove it in the next commit and accept the
  storage cost rather than attempting a forbidden rewrite.

**Warning signs:**
- `git count-objects -vH` grows quickly or `.git` exceeds the source size.
- `git lfs ls-files` lists files that should be linked instead.
- Clone time in CI increases steadily.
- A PR includes `.png`, `.jpg`, `.mp4`, `.pdf`, or `.zip` without review.
- LFS bandwidth warnings from GitHub.

**Phase to address:**
Phase 1 - Repository Foundation, with a per-homework check in Phase 2 and CI enforcement in
Phase 6.

---

### Pitfall C7: Unpinned platforms, frameworks, and libraries make builds irreproducible

**What goes wrong:**
`platform = espressif32` and `lib_deps = SomeLib` resolve to whatever is current. Six
months later a homework builds against a different Arduino core, a library API changes, and
the report's measured results no longer match the code. PlatformIO has no enforced lockfile,
so exact pins are the lockfile.

**Why it happens:**
Unpinned configuration is the documented default and works during the course. Reproducibility
only matters after the grade is issued, which is exactly when it is needed.

**How to avoid:**
- Pin the platform (`espressif32@x.y.z`), framework/core where selectable, and every
  `lib_deps` entry to an exact version or commit.
- Record tool versions, platform version, and commit hash in the report's methodology.
- Run a nightly job that verifies pinned versions still resolve; never auto-upgrade.
- Use per-homework `platformio.ini` as the single source of truth; do not rely on a global
  `~/.platformio` state.
- Keep a shared `platformio.ini` base with pins and include it per project.

**Warning signs:**
- `platformio.ini` contains version ranges (`^`, `>=`, `~`), branch names, or unversioned
  Git URLs.
- A rebuild downloads new packages despite no code change.
- "It built last week" reports.
- The report does not state the firmware commit or tool versions.

**Phase to address:**
Phase 2 - Templates, enforced by Phase 6 - CI (lock/pin check).

---

### Pitfall C8: Framework libraries leak into native unit tests

**What goes wrong:**
A native environment builds `src/` and the shared libraries, but the Library Dependency
Finder pulls in Arduino or ESP-IDF libraries because they are visible through
`lib_extra_dirs`. The test binary then needs target-only headers, or compiles host-incompatible
code and fails with obscure errors. Alternatively tests "pass" while linked against a
different library version than firmware.

**Why it happens:**
`lib_extra_dirs` is global to the project, `test_build_src` pulls in main sources, and LDF
does not know the environment is native. The common fix (`lib_ignore`) is easy to
misconfigure because it takes library names, not folder names.

**How to avoid:**
- Give the native environment its own `[env:native]` with `platform = native`, no framework,
  and an explicit `lib_ignore` list of every target-only library and adapter.
- Keep `lib/common` portable so it needs no ignore list; only adapters should be excluded.
- Use `build_src_filter` to exclude adapter sources from the native build rather than
  relying solely on link-time exclusion.
- Validate with a clean native build in CI (`pio test -e native`) on a machine without the
  target toolchain installed.
- Keep a dedicated `tests/` PlatformIO project for shared libraries so test dependencies
  never mix with firmware dependencies.

**Warning signs:**
- Native test includes resolve into `.platformio/packages`.
- `lib_ignore` entries change whenever a new library is added.
- Tests pass only after a firmware build has populated `.pio`.
- `pio test -e native` works locally but fails in a fresh CI container.

**Phase to address:**
Phase 3 - Shared Libraries and Phase 7 - Testing Infrastructure.

---

### Pitfall C9: clangd cannot see cross-compiler system headers

**What goes wrong:**
The editor shows red squiggles over `<stdio.h>`, `<Arduino.h>`, `stdint.h`, or vendor
headers even though the build succeeds. Or clangd reports errors for GCC-specific flags
such as `-mlongcalls`, `-mtext-section-literals`, or `-fno-tree-switch-conversion`.
Developers lose trust in the language server and fall back to cpptools, reintroducing
duplicate diagnostics.

**Why it happens:**
clangd does not inherit the GCC cross-compiler's include search path. It must be told which
drivers it may query, and `compile_commands.json` often contains a bare compiler name
(`xtensa-esp32-elf-g++`) that clangd cannot resolve or whose path does not match the
`--query-driver` allowlist. Xtensa and RISC-V also need toolchain-aware handling.

**How to avoid:**
- Generate `compile_commands.json` with `pio run -t compiledb`, then point clangd at it via
  a per-project `.clangd` file.
- Set `--query-driver` to absolute globs covering the PlatformIO toolchains, for example
  the `toolchain-*/bin/*` and `tool-*/bin/*` directories under the PlatformIO core
  directory. Use absolute paths; `~` is not reliably expanded.
- Ensure the compiler in `compile_commands.json` is an absolute path; the pioarduino
  extension's `fixupCompileCommands()` exists precisely for this.
- Add `.clangd` `CompileFlags: Remove:` entries for flags clang does not understand.
- Consider Espressif's patched clangd for Xtensa/RISC-V ISA extensions.
- Diagnose with `clangd --check=<file>` to see the exact command and include list.

**Warning signs:**
- Missing system headers only in the editor, never in the build.
- Unknown-argument warnings from clangd for target flags.
- Diagnostics change after `platformio.ini` edits but the database is not regenerated.
- Different behavior between a terminal and the editor.

**Phase to address:**
Phase 4 - Developer Tooling, validated by the onboarding guide and Phase 8.

---

### Pitfall C10: Assuming simulator behavior equals hardware behavior

**What goes wrong:**
A homework passes in simulation and fails on the bench: LEDs are dim or burn out, buttons
bounce, I2C devices NAK, PWM frequency is wrong, or timing loops run at the wrong speed.
The report then claims a result that was never observed on hardware. Simulation CPU
frequency is capped (Wokwi runs around 8 MHz by default and documents that peripheral
timing is unaffected while instruction timing is), so busy-wait and bit-bang code diverges
from real execution.

**Why it happens:**
Simulation is presented as a substitute for hardware because hardware is not always
available. The gaps are peripheral-specific and rarely listed in tutorials.

**How to avoid:**
- Define evidence tiers explicitly: built, unit-tested, simulated, hardware-verified.
  Reports must state which tier produced each measurement.
- Treat simulation as a design check, not a measurement instrument.
- For anything electrical (current, brightness, voltage drop, rise time), require a
  calculation and, when hardware is available, a measurement.
- Model the physical circuit in the simulator: resistors, current limits, and real part
  numbers, not idealized components.
- Keep a known list of simulator limitations per board in `docs/boards/` and reference it
  in the homework template.

**Warning signs:**
- A report contains "measured" values with no instrument, method, or photo.
- A design works in simulation but has no current-limiting resistor.
- Timing-sensitive code has no hardware verification note.
- Simulation results are reported with more precision than the model supports.

**Phase to address:**
Phase 5 - Simulation Spike (produce the limitations matrix), applied in Phase 7 and Phase 8.

---

### Pitfall C11: Making cloud simulation a required, blocking CI check

**What goes wrong:**
Wokwi CLI requires a token and network access, has a default 30-second timeout, and is a
hosted service. Rate limits, token expiry, service incidents, or a slow run turn a required
check red on an otherwise correct PR. Contributors learn to re-run until green, which
destroys the signal. Velxio self-hosted may avoid the token but adds its own infrastructure
and coverage gaps.

**Why it happens:**
"Run simulation in CI" sounds like full verification. The external dependency and its
failure modes are not modeled as a distinct tier.

**How to avoid:**
- Split checks: deterministic build and native tests are required; simulation is required
  only for homeworks that declare simulation support and only on a schedule or a
  simulation-specific label.
- Add a retry budget and classify infrastructure failures separately from assertion
  failures; never use blanket `continue-on-error`.
- Keep simulation artifacts (VCD, serial log, coverage) so a failure can be diagnosed
  without re-running.
- If simulation is required, pin the CLI version and document the token/secret setup; make
  the check skippable with an explicit label for infrastructure outages.
- Prefer local/offline runners for gating; use cloud simulation for evidence capture.

**Warning signs:**
- Simulation jobs failing with network, auth, or timeout errors rather than test failures.
- Frequent manual re-runs of the same commit.
- PRs blocked for hours by a third-party incident.
- No artifacts uploaded on simulation failure.

**Phase to address:**
Phase 5 decides the tool; Phase 6 implements the tiering.

---

### Pitfall C12: Hardware mocks drift from the real driver contract

**What goes wrong:**
Tests pass against a hand-written mock that returns success for every transfer, ignores
addressing, or never models a NAK. The real sensor behaves differently, and the bug is
found only on the bench. Because the mock duplicates the API instead of implementing the
same interface, signature changes are not caught.

**Why it happens:**
Mocks are written quickly to unblock TDD, and nothing forces them to stay honest. On
embedded targets the real driver is hard to exercise in CI.

**How to avoid:**
- Mock at the narrowest seam: byte transport or register map, not the whole driver.
- Make the mock implement the same header as the real adapter so signature drift is a
  compile error.
- Add contract tests that run the same test suite against the mock and, when hardware is
  attached, against the real driver.
- Record known deviations (timing, error injection) in the mock and reference them in tests.
- Use captured bus traces from the real device to build realistic mock responses when
  possible.
- Add at least one HIL test per homework when hardware is available; mark it clearly and do
  not fake it in CI.

**Warning signs:**
- Mock methods return fixed success values with no error paths.
- Tests never exercise timeout, NAK, or malformed data.
- The mock interface differs from the production interface.
- Bugs found on hardware are not reproducible in tests.
- Coverage is high but adapter code is untested.

**Phase to address:**
Phase 7 - Testing Infrastructure, with the first contract test in Phase 8.

---

### Pitfall C13: Fabricated, unlabeled, or non-reproducible measurements

**What goes wrong:**
Reports contain plausible numbers (current draw, response time, temperature) that were
never measured, or measured values mixed with calculated and simulated ones without labels.
Safety checks are omitted. Results cannot be reproduced because board revision, firmware
commit, tool versions, and instrument settings are missing.

**Why it happens:**
Academic reports reward completeness, and hardware access is intermittent. It is easier to
estimate than to measure, and the distinction is not enforced by any check.

**How to avoid:**
- Require a measurement ledger in `homework.yaml` or the report: value, source
  (measured/calculated/simulated/datasheet), instrument, method, uncertainty, date.
- Make "not measured" an allowed, explicit value. Never leave a blank that invites invention.
- Add a safety checklist template (supply voltage, current limit, polarity, thermal, mains
  isolation, LiPo handling) and require it for every hardware homework.
- Record firmware commit hash, platform version, board revision, and instrument model in
  methodology.
- Peer-review reports against raw evidence (serial logs, scope screenshots, photos) before
  merging; the PR template should link the evidence.
- Require IEEE-style citations for datasheet values and theory.

**Warning signs:**
- Numbers with unrealistic precision or suspiciously round values.
- "Measured" claims with no instrument named and no photo or log.
- Safety section absent or generic.
- Report results cannot be linked to a commit or test run.
- Calculated values presented as experimental results.

**Phase to address:**
Phase 2 (report template and schema), Phase 8 (pilot review), Phase 10 (audit).

---

### Pitfall C14: Squash merge, tags, and protected `main` without a traceability policy

**What goes wrong:**
Every homework becomes one squashed commit, so the evolution from failing test to working
firmware is lost. Tags are created on branches or before merge, so they do not point at
what shipped. Required checks on `main` block urgent fixes, tempting bypass. Stale branches
accumulate, and the `hw/<id>` tag scheme diverges from the directory naming.

**Why it happens:**
Squash merge is chosen for a clean history, and branch protection is enabled for safety,
without defining how evidence and tags survive the squash.

**How to avoid:**
- Put the evidence in the PR: test output, simulation artifacts, report link, and a short
  decision log. The squash commit body should summarize the phases.
- Create `hw/<id>` tags only on `main` after merge, from an automated workflow, and verify
  the tag points at the merge commit.
- Keep branches short-lived and delete on merge; enable automatic branch deletion.
- Define a documented bypass path for emergencies (admin merge with a follow-up PR), rather
  than disabling protection.
- Ensure the required-check set is small and reliable; move slow/flaky checks to nightly.

**Warning signs:**
- Tags exist on non-`main` commits or are missing after merge.
- PR bodies contain no evidence links.
- Branch list grows monotonically.
- Protection is disabled "temporarily" and not restored.
- A homework's squash commit message is just "feat: add homework".

**Phase to address:**
Phase 1 - Repository Foundation (policy), Phase 6 (automated tagging), Phase 9 (hygiene).

---

### Pitfall C15: Premature shared abstraction before a second consumer exists

**What goes wrong:**
`lib/port` and `lib/common` are designed up front for 30 hypothetical homeworks. Interfaces
encode guesses about sensors, buses, and scheduling that do not survive the first three
real assignments. Because everything depends on them, correcting the design becomes a
repo-wide refactor, and the abstractions ossify.

**Why it happens:**
The monorepo and the "reuse" requirement create anticipation. Designing for the full course
feels efficient, and there is no cost signal until the wrong seam is used widely.

**How to avoid:**
- Build shared code only from real duplication: copy twice, extract on the third use.
- Keep the first two homeworks self-contained; let the shared API emerge from their diffs.
- Timebox shared-library work and review it as an ADR with explicit non-goals.
- Prefer small, composable utilities (ring buffer, fixed-point math, CRC) over framework-like
  layers.
- Make it cheap to change: shared code is versioned by the repo, and adapters are thin.

**Warning signs:**
- `port` has interfaces with no implementation or no consumer.
- Documentation describes behavior no homework uses.
- The shared library changes on almost every homework.
- Contributors ask for "the right way" before a second use exists.

**Phase to address:**
Phase 3 - Shared Libraries, with a deliberate "no speculative interfaces" rule.

---

### Pitfall C16: CI cost and time explosion across 30+ projects

**What goes wrong:**
A full matrix builds every homework on every PR. Toolchain downloads (often hundreds of
megabytes to over a gigabyte per platform) dominate runtime, caches miss, jobs approach the
6-hour limit, and the nightly matrix hits the 256-job cap or exhausts patience. Eventually
checks are disabled, which is worse than having none.

**Why it happens:**
Matrix CI is easy to write and looks thorough. The cost is invisible until the repo has
dozens of projects and multiple frameworks.

**How to avoid:**
- Build changed projects only on PRs (path filtering or a script that maps changed paths to
  homework IDs); run the full matrix nightly.
- Cache `~/.platformio` (packages, platforms, and cache), keyed on a hash of all
  `platformio.ini` files, not just the root one.
- Use `concurrency` groups to cancel superseded runs.
- Split lint/metadata (seconds) from build/test (minutes) so fast feedback is never blocked.
- Keep the matrix dimension count small: platform and framework, not every board variant.
- Set explicit `timeout-minutes` per job well below the 6-hour default.
- Measure and publish CI duration; treat a regression as a bug.

**Warning signs:**
- PR feedback takes more than 15 minutes.
- Cache hit rate is low or the key never changes.
- The same toolchain downloads on every run.
- Jobs are regularly cancelled or time out.
- Contributors push multiple empty commits to retrigger CI.

**Phase to address:**
Phase 6 - CI Pipeline; revisit at Phase 9 when the project count grows.

---

## Moderate Pitfalls

These cause friction and wasted time but are recoverable.

### Pitfall M1: `lib_extra_dirs` pointed at a library instead of a storage folder

**What goes wrong:**
`lib_extra_dirs = ../lib/common` silently finds nothing, or finds the wrong library, because
the option expects a storage directory containing library folders, not a library directory
itself. Builds fail with missing headers and the error points elsewhere.

**Why it happens:**
The name suggests "extra library directories", and the documentation warning is easy to miss.

**How to avoid:**
Point `lib_extra_dirs` at the parent (for example the repo `lib/` directory) and place each
library in its own subfolder with a `library.json`. Verify with the LDF dependency graph in
the build output.

**Warning signs:**
- "Library not found" despite the path existing.
- The dependency graph lists unrelated libraries.
- Changing the path "fixes" it intermittently.

**Phase to address:**
Phase 2 - Templates.

---

### Pitfall M2: `lib_ignore` uses folder names instead of library names

**What goes wrong:**
An ignored library still builds because `lib_ignore` matches the LDF library name, not the
folder. Conversely, an over-broad ignore silently removes a needed dependency.

**Why it happens:**
Folder and library names usually match, so the mistake hides until one differs (spaces,
version suffixes, `library.json` overrides).

**How to avoid:**
Copy names from the dependency graph (`<Name>` entries), not from `ls`. Add a CI assertion
that the native environment's dependency graph contains no target-only library.

**Warning signs:**
- Ignored libraries still appear in the build.
- Native tests need target headers after an ignore change.
- Dependency graph names differ from folder names.

**Phase to address:**
Phase 3 / Phase 7.

---

### Pitfall M3: Mixing ESP-IDF managed components with PlatformIO library semantics

**What goes wrong:**
An `idf_component.yml` dependency or a `components/` folder is expected to work like
`lib_deps`. It does not: IDF components need the CMake build system, and `lib_extra_dirs`
does not apply. Headers are missing or the component is built twice.

**Why it happens:**
Both look like "dependencies", and PlatformIO documentation covers libraries more prominently.

**How to avoid:**
Keep IDF components as real components with `CMakeLists.txt`, and keep Arduino libraries in
`lib_deps`. Document the split in the ESP-IDF homework template. Do not bridge them with a
precompiled `.a` unless there is no alternative.

**Warning signs:**
- Component headers exist but are not found by `pio run`.
- `idf.py build` and `pio run` disagree.
- Duplicate symbol errors from two copies of a component.

**Phase to address:**
Phase 2 (ESP-IDF template), Phase 5 (spike if dual-framework).

---

### Pitfall M4: clangd and cpptools both provide IntelliSense

**What goes wrong:**
Two language engines produce duplicate errors, conflicting formatting, and different
go-to-definition results. `C_Cpp.intelliSenseEngine: "disabled"` only takes effect at the
workspace level in multi-root setups, so a per-folder disable does not work.

**Why it happens:**
Both extensions are commonly recommended, and the conflict is subtle until diagnostics
diverge.

**How to avoid:**
Pick one. If clangd is canonical, disable cpptools IntelliSense in the `.code-workspace`
file and document it in the onboarding guide. Use clangd's enable/disable setting (v0.1.30+)
if both must stay installed. Pin extension recommendations in `extensions.json`.

**Warning signs:**
- Duplicate diagnostics on the same line.
- Different errors in the Problems panel versus `clangd --check`.
- Formatting changes when saving depending on which extension is active.

**Phase to address:**
Phase 4 - Developer Tooling.

---

### Pitfall M5: Multi-root workspace runs one clangd instance

**What goes wrong:**
Folder-level clangd settings are ignored in multi-root workspaces, and `--compile-commands-dir`
with `${workspaceFolder}` applies only to the folder containing the workspace file. Indexes
bleed across projects, so go-to-definition lands in another homework's copy of a symbol.

**Why it happens:**
The multi-root workspace is a core project decision, but the clangd extension's multi-root
support is incomplete.

**How to avoid:**
Put a `.clangd` file with `CompileFlags: CompilationDatabase: <path>` in each project root
instead of relying on folder settings. Prefer one workspace per active project if index
bleed becomes a problem, or run per-root clangd instances. Document the workaround.

**Warning signs:**
- Settings appear greyed out at folder scope.
- Navigation jumps to the wrong homework.
- A project works when opened alone but not in the workspace.

**Phase to address:**
Phase 4 - Developer Tooling.

---

### Pitfall M6: clangd rejects GCC-only target flags

**What goes wrong:**
`compile_commands.json` contains flags clang does not implement (`-mlongcalls`,
`-mtext-section-literals`, `-fno-tree-switch-conversion`, and similar). clangd emits
unknown-argument diagnostics or misparses the command, producing false errors.

**Why it happens:**
The database is generated from GCC invocations, and clang is not flag-compatible with every
GCC target option.

**How to avoid:**
Add `.clangd` `CompileFlags: Remove:` patterns for the known flags, and keep the list in
the shared template. Re-check after platform upgrades. Use the Espressif-patched clangd for
targets with custom ISA extensions.

**Warning signs:**
- Unknown-argument warnings only in clangd.
- Diagnostics appear at the first line of every file.
- Removing one flag fixes many unrelated errors.

**Phase to address:**
Phase 4 - Developer Tooling.

---

### Pitfall M7: A portable API that hides concurrency and blocking semantics

**What goes wrong:**
`port_delay_ms()` works in a task but is illegal or harmful in an ISR. A shared callback
signature does not express ISR context, so code that is correct on Arduino breaks under
FreeRTOS, or vice versa. Blocking I2C calls inside an ISR cause watchdog resets.

**Why it happens:**
Arduino's `loop()` model hides scheduling, while ESP-IDF exposes tasks and ISR constraints.
A least-common-denominator API erases the distinction.

**How to avoid:**
- Name functions by context (`_from_isr`, `_blocking`) or separate interfaces entirely.
- Document ISR safety per function in headers.
- Prefer passing a clock/timer abstraction over calling `delay()` in shared logic.
- Test ISR-adjacent logic with fake time and explicit context assertions.
- Let adapters keep native idioms rather than forcing one signature.

**Warning signs:**
- Shared code calls `delay()`, `millis()`, or blocking bus functions unguarded.
- ISR handlers call functions with no documented context.
- Watchdog resets under load.
- Reviews debate "is this called from an ISR?" repeatedly.

**Phase to address:**
Phase 3 - Shared Libraries.

---

### Pitfall M8: Non-deterministic tests

**What goes wrong:**
Tests depend on wall-clock time, random values, uninitialized memory, float rounding, test
order, or filesystem state. They pass locally and fail intermittently in CI. Flaky tests
are then ignored, and real failures hide among them.

**Why it happens:**
Embedded code naturally uses `millis()`, timers, and entropy; native tests inherit those
calls unchanged.

**How to avoid:**
Inject a clock and a random source. Seed deterministically. Avoid sleeping; advance fake
time. Make tests independent and order-agnostic. Run the native suite repeatedly (for
example 20 iterations) in CI to surface flakes. Fail on warnings that indicate undefined
behavior.

**Warning signs:**
- Re-running the same commit changes the result.
- Tests pass alone but fail in the full suite.
- `sleep` or real delays in test code.
- Timing assertions with tight tolerances.

**Phase to address:**
Phase 7 - Testing Infrastructure.

---

### Pitfall M9: Trying to unit-test ISR and RTOS timing on the host

**What goes wrong:**
Native tests attempt to validate interrupt latency, preemption, or real-time deadlines.
The host has no interrupts and a different scheduler, so the test proves nothing while
appearing rigorous.

**Why it happens:**
"Test everything" is the stated goal, and timing is part of the homework requirements.

**How to avoid:**
Test the logic that the ISR calls, not the ISR mechanism. Model time and events explicitly.
Verify real timing with a logic analyzer, oscilloscope, or HIL tier, and report it as
hardware evidence. Use simulation only for functional sequencing, not latency claims.

**Warning signs:**
- Host tests assert on microsecond timing.
- Tests mock FreeRTOS primitives and then claim real-time correctness.
- No hardware measurement backs a timing claim.

**Phase to address:**
Phase 7 - Testing Infrastructure, Phase 8 (pilot evidence).

---

### Pitfall M10: CI cache keys that miss per-homework changes

**What goes wrong:**
The cache is keyed on the root `platformio.ini` or only on the runner OS. A homework adds a
library or bumps a platform, the key does not change, and CI restores a stale toolchain or
package set. Failures look random and disappear after "clear cache".

**Why it happens:**
The common example keys on a single file, while this repo has 30+ project configs.

**How to avoid:**
Key on `hashFiles('**/platformio.ini', '**/library.json')` plus OS and a manually bumped
cache version. Include the PlatformIO core version. Prefer exact pins so the key is stable
and meaningful. Add a scheduled cache-clean job.

**Warning signs:**
- Intermittent "package not found" or version mismatch errors.
- CI passes after manually deleting caches.
- A new dependency does not trigger a download.

**Phase to address:**
Phase 6 - CI Pipeline.

---

### Pitfall M11: Over-broad GitHub Actions permissions and unsafe PR triggers

**What goes wrong:**
Workflows default to write permissions, or use `pull_request_target` with checkout of PR
code. A fork PR can then exfiltrate secrets or push to the repository. Third-party actions
pinned to tags can be moved under you.

**Why it happens:**
Copy-pasted workflows often grant broad permissions, and `pull_request_target` is suggested
for labeling or commenting on fork PRs.

**How to avoid:**
Set `permissions: contents: read` at workflow level and elevate per job. Never run untrusted
PR code in a `pull_request_target` context with secrets. Pin third-party actions to full
commit SHAs. Do not expose Wokwi tokens or other secrets to fork PRs; gate simulation on
trusted branches or maintainers' labels.

**Warning signs:**
- Workflows without a `permissions:` block.
- `pull_request_target` combined with `actions/checkout` of the PR head.
- Actions referenced by `@v3` or `@main`.
- Secrets available in jobs that build fork code.

**Phase to address:**
Phase 6 - CI Pipeline.

---

### Pitfall M12: Generated artifacts committed and silently drifting

**What goes wrong:**
The multi-root workspace file, README index, and MkDocs pages are generated from metadata
but also committed. Someone edits generated output by hand, or forgets to regenerate after
adding a homework. The site and index disagree with `homework.yaml`.

**Why it happens:**
Committing generated files is required for the workspace, but the generation step is manual
and not enforced.

**How to avoid:**
- One command regenerates all derived artifacts; CI runs it and fails on a dirty diff.
- Generated files carry a header saying "do not edit; run `make generate`".
- Pre-commit hook regenerates and stages.
- Schema validation runs before generation, so bad metadata fails early.

**Warning signs:**
- CI diff shows only generated files.
- README index lists a homework that does not exist.
- Workspace folders point at deleted directories.
- Manual edits disappear after regeneration.

**Phase to address:**
Phase 2 - Templates and Metadata; Phase 6 enforcement.

---

### Pitfall M13: Personal data in photos, logs, and screenshots

**What goes wrong:**
Bench photos show a name badge, a room, a serial number, or a monitor with accounts.
Serial logs include a real MAC address, SSID, or local IP. Screenshots show a home
directory with a username. The repo is public forever.

**Why it happens:**
Evidence capture is informal, and the privacy risk is not obvious in a hardware photo.

**How to avoid:**
Crop and review every asset before commit. Scrub MAC addresses and IPs in logs. Use
placeholder credentials. Add a checklist item to the homework PR template. Prefer diagrams
over photos when a photo adds no evidence. Blur or replace serial numbers.

**Warning signs:**
- Photos of a desk rather than the circuit.
- Full serial logs pasted into reports.
- Screenshots including OS usernames or notifications.
- Assets not reviewed in the PR diff.

**Phase to address:**
Phase 2 (template checklist), Phase 8 (pilot review), Phase 10 (audit).

---

### Pitfall M14: Assuming a simulator supports the board or part you chose

**What goes wrong:**
The chosen board or component is unsupported, so it is replaced with a similar-looking part.
The simulation passes, but the electrical or protocol behavior differs. Multi-MCU diagrams
and some peripherals (BLE, MCPWM, full I2S, 10-bit I2C addressing, deep sleep wakeup) are
not available, and the workaround changes the design.

**Why it happens:**
Support matrices are long and change; the spike evaluates tools but not every future part.

**How to avoid:**
- Maintain a supported-parts matrix per simulator in `docs/boards/` and `docs/components/`,
  checked at homework intake.
- If a part is unsupported, record the substitution and its fidelity impact in the report.
- Prefer parts with simulation support for homeworks that must be graded without hardware.
- Re-run the support check when a tool updates.

**Warning signs:**
- `diagram.json` references a generic part standing in for the real one.
- The report does not mention a substitution.
- Simulation results differ from the datasheet in an unexplained way.

**Phase to address:**
Phase 5 - Simulation Spike; per-homework intake from Phase 8.

---

### Pitfall M15: Weak traceability from requirement to evidence

**What goes wrong:**
The report has theory, code, and results, but no matrix connecting the assignment
requirements to design decisions, tests, and measured evidence. A reviewer cannot tell
whether a requirement was met or skipped. Assumptions are implicit.

**Why it happens:**
The sections are written independently, often at the end, and the traceability matrix is
treated as a formality.

**How to avoid:**
- Put requirement IDs in `task.md` (paraphrased) and reference them in the design, tests,
  and results.
- Make the traceability matrix a required section with status and evidence links.
- Review the matrix before writing conclusions; any gap is either a missing test or a
  documented deviation.
- Record assumptions in a numbered list and reference them where they affect results.

**Warning signs:**
- Conclusions mention behavior no test covers.
- Requirements appear only in the introduction.
- Assumptions are scattered in prose.
- The matrix has "yes" without evidence links.

**Phase to address:**
Phase 2 (report template), Phase 8 (pilot), Phase 10 (audit).

---

### Pitfall M16: Branch and tag hygiene decay

**What goes wrong:**
Branches live for weeks, diverge from `main`, and merge with large conflicts. Tags are
missing or inconsistent. PRs mix homework and infrastructure changes, making review and
rollback hard.

**Why it happens:**
Course pace is 2-3 homeworks per week; branch discipline slips when work is interrupt-driven.

**How to avoid:**
Keep branches short-lived and scoped to one homework or one infra change. Rebase or merge
`main` frequently. Use the three PR templates to force classification. Automate tagging and
branch deletion. Add a weekly hygiene check for stale branches.

**Warning signs:**
- Branches older than a week.
- PRs touching both `homeworks/` and `.github/`.
- Merge conflicts in generated files.
- Missing `hw/<id>` tags.

**Phase to address:**
Phase 1 (policy), Phase 9 (operations).

---

### Pitfall M17: Coverage numbers that hide untested adapters

**What goes wrong:**
Line coverage looks high because pure logic is well tested, while every adapter, ISR path,
and error branch is untested. The report implies the firmware is verified. Coverage is also
measured with host instrumentation that cannot see target-only code.

**Why it happens:**
Native coverage is easy to collect; hardware paths are not. One aggregate number hides the
gap.

**How to avoid:**
Report coverage per layer (core, port, adapter) and mark target-only code as not covered by
native tests. Define what the adapter/HIL tier covers. Do not set a single global threshold
that incentivizes testing trivial code. Track error-path tests explicitly.

**Warning signs:**
- One coverage percentage for the whole repo.
- Adapter files at 0% but overall coverage high.
- No error-injection tests.
- Coverage claims in the report without a method.

**Phase to address:**
Phase 7 - Testing Infrastructure.

---

## Minor Pitfalls

| Pitfall | What goes wrong | Prevention | Phase |
|---------|-----------------|------------|-------|
| Stale `compile_commands.json` | Editor shows errors that do not match the current `platformio.ini` | Regenerate on config change; pre-commit hook or task; document in onboarding | 4 |
| `String`/STL in shared C code | Shared logic becomes C++-only and bloats embedded builds | Ban STL in `common`; use fixed buffers; enforce in review | 3 |
| `millis()` wraparound | Comparison logic fails after about 49 days or on rollover | Use unsigned subtraction or a clock abstraction; add a unit test | 3, 7 |
| Float on MCU without FPU | Unexpected code size/latency on some targets | Prefer fixed-point where appropriate; document the choice | 3 |
| Uninitialized globals | Non-deterministic startup behavior | Enable warnings, `-Werror`, static analysis; initialize explicitly | 3, 7 |
| `delay()` in production code | Blocks the loop, breaks responsiveness | Use non-blocking state machines; fake time in tests | 3, 7 |
| Missing `volatile`/atomics | ISR-shared variables optimized away | Static analysis and code review checklist; document ISR contract | 3 |
| Simulator timeout too short | Long-running demo truncated in CI | Set `--timeout` explicitly; split long scenarios | 5, 6 |
| Wokwi token in logs | Token leakage in CI output | Mask secrets; never echo; rotate on exposure | 6 |
| Artifact retention bloat | Large simulation artifacts fill storage | Short retention for bulky logs; keep only failures | 6 |
| Non-ASCII in reports | Inconsistent rendering and lint failures | English-only artifact rule; markdownlint; encoding check | 2 |
| Filename case collisions | macOS case-insensitive clone hides conflicts; Linux CI fails | Enforce lowercase, hyphenated names; CI check | 2, 6 |
| Deep directory paths | Windows path-length failures for long homework names | Keep nesting shallow; check at scaffold time | 2 |
| Missing license headers | Ambiguous provenance for shared code | SPDX headers in shared libs; documented in `AGENTS.md` | 1, 3 |
| Screenshot-only evidence | Unverifiable and unsearchable | Require logs/CSV where possible; screenshots as supplement | 8, 10 |

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Copy a shared library into a homework instead of using `lib_extra_dirs` | Build works in five minutes | Divergent copies, bug fixes missed, 30x maintenance | Never, except a throwaway spike |
| Skip pinning versions "for now" | No version-conflict work | Builds change under you; report results unreproducible | Never for committed homeworks |
| One giant `platformio.ini` for all projects | Fewer files | Cross-project leakage, impossible per-board pinning | Never |
| Hand-written mocks with no contract | TDD unblocked quickly | False confidence; bugs found on hardware | Only for a first exploratory test, then replace |
| Disable a flaky CI check | Unblocks a PR | Signal erosion; failures ignored | Only with an issue and a deadline |
| Publish solutions immediately | Portfolio visible sooner | Academic-integrity risk, plagiarism enablement | Only after the course policy permits |
| Commit binaries directly because "it's one file" | No LFS setup | Permanent history bloat and quota use | Never |
| Single global coverage threshold | Simple gate | Tests trivial code, ignores adapters | Never as the only metric |
| Manual workspace/index regeneration | No script work | Drift and broken links | Only before automation exists |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| PlatformIO + ESP-IDF components | Treating components as `lib_deps` | Real `components/` with CMake; keep libraries in `lib_deps` |
| PlatformIO + Arduino-as-component | Adopting raw IDF examples | Start from `examples/espidf-arduino-blink`; pin a compatible IDF/core pair |
| clangd + PlatformIO | Bare compiler names, no `--query-driver` | Absolute compiler paths; absolute driver globs; `.clangd` flag filtering |
| clangd + cpptools | Both enabled | Disable one at workspace level; pin extensions |
| Multi-root workspace + clangd | Folder-level settings | Per-root `.clangd` with `CompilationDatabase` |
| Wokwi CLI + CI | Token in public workflow, default timeout | Secret on trusted runs only; explicit timeout; artifacts on failure |
| GitHub Actions + forks | `pull_request_target` with PR checkout | `pull_request` with read-only token; no secrets for fork code |
| Git LFS + CI | Checkout without LFS | `lfs: true` only where assets are needed; avoid full clones |
| MkDocs + metadata | Editing generated pages | Generate from `homework.yaml`; CI dirty-diff check |
| Dependabot/renovate + PlatformIO | Auto-bumping platform | Manual review; pins are the reproducibility contract |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Full matrix on every PR | 20+ minute feedback | Changed-project detection; nightly full run | Around 10 projects |
| Toolchain re-download every run | Minutes of setup per job | Cache `~/.platformio` keyed on all configs | First multi-platform job |
| Cache key on root config only | Stale packages, random failures | Hash `**/platformio.ini` and `**/library.json` | First per-homework dependency change |
| No build cache for ESP-IDF | Full rebuild each run | `build_cache_dir` outside `.pio`; ccache where supported | First large IDF project |
| Serialized package installs | Slow, rate-limited CI | Cache; avoid Git-URL deps; prefer archives | Several concurrent jobs |
| Oversized simulation artifacts | Storage and upload time | Retain only on failure; compress | Nightly full matrix |
| 30+ `pio run` invocations in one job | Approaches 6-hour limit | Split by project; shard the matrix | Dozens of projects |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Real Wi-Fi/API credentials in source or `sdkconfig` | Public exposure; unauthorized access | Ignored secrets file; env injection; gitleaks; push protection |
| Secret in Git history "fixed" by a later commit | Still recoverable | Rotate immediately; avoid rewriting under project rules; scan history before first push |
| Broad `GITHUB_TOKEN` permissions | A compromised workflow can push | `permissions: contents: read`; per-job elevation |
| `pull_request_target` running fork code | Secret exfiltration / repo takeover | Use `pull_request`; never checkout untrusted code with secrets |
| Unpinned third-party actions | Supply-chain compromise | Pin to full commit SHA |
| Simulation/CI tokens echoed in logs | Token leakage | Mask secrets; no `set -x` around auth; rotate on exposure |
| Personal data in images/logs | Privacy harm, doxxing | Review assets; scrub MAC/IP; crop photos |
| Course materials committed verbatim | Copyright infringement, takedown, discipline | Paraphrase + cite; policy check; private until course ends |
| Third-party code without license | License incompatibility in an MIT repo | Record licenses in `sources.md`; vendor only permissive code |

## "Looks Done But Isn't" Checklist

- [ ] **Homework template:** Often missing a working native test environment and pinned versions - verify `pio test -e native` and an exact-pin audit pass on a clean checkout.
- [ ] **Shared library:** Often missing a dependency-rule check - verify `common` compiles natively and contains no framework includes.
- [ ] **clangd setup:** Often missing driver paths - verify `clangd --check` reports no missing system headers for a target file.
- [ ] **Multi-root workspace:** Often missing per-root `.clangd` - verify navigation does not cross into another homework.
- [ ] **Git LFS:** Often missing `.gitattributes` coverage - verify new binary types are tracked by LFS before commit.
- [ ] **Public repo:** Often missing history scan - verify gitleaks has scanned the full history, not just the working tree.
- [ ] **Simulation:** Often missing a fidelity disclaimer - verify the report labels simulated vs measured results.
- [ ] **Tests:** Often missing error paths - verify NAK, timeout, and malformed-input cases exist.
- [ ] **CI:** Often missing changed-project filtering - verify a docs-only PR does not build all homeworks.
- [ ] **Report:** Often missing traceability - verify every requirement maps to a test or a documented deviation.
- [ ] **Tagging:** Often missing post-merge tags - verify `hw/<id>` points at the squash commit on `main`.
- [ ] **Generated artifacts:** Often missing regeneration - verify `generate` produces no diff on a clean tree.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Secret committed | HIGH | Rotate the credential first; remove from working tree; assess exposure; if history rewrite is forbidden, document and monitor; enable push protection |
| Large binary in history | HIGH | Remove forward; accept storage cost; add LFS/ignore rules; do not rewrite under current Git policy |
| Shadow HAL ossified | HIGH | Freeze new `port_*` APIs; migrate homework by homework; shrink the interface to two or three capabilities; document the exit |
| Dual-framework project broken | MEDIUM | Revert to a single framework; move IDF-only code behind a component; record an ADR; re-run the pilot |
| Framework leaked into `common` | MEDIUM | Move the code into an adapter; add the CI grep; rebuild native tests |
| clangd unusable | LOW | Regenerate the database; fix the driver glob; add `.clangd` flag removals |
| Flaky simulation check | LOW | Demote to nightly/label-gated; add retries and artifact capture; pin CLI |
| Stale CI cache | LOW | Bump the cache version; fix the key; re-run |
| Report measurement discovered as fabricated | HIGH | Correct the report, mark the source honestly, add review gate, notify per course policy |
| Copyright issue | HIGH | Make the repo private or remove the material; replace with paraphrase; consult the course |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| C1 Shadow HAL | Phase 3 | Architecture review rejects `port_*` with no third consumer; adapters contain no logic |
| C2 Dual-framework fragility | Phase 2, spike before use | Dual-framework build passes from the official example; ADR recorded |
| C3 Dependency-rule drift | Phase 3, CI Phase 6 | CI grep and native compile of `common` pass |
| C4 Secrets exposure | Phase 1, Phase 6 | gitleaks full-history scan; push protection enabled; no high-entropy hits |
| C5 Copyright / academic integrity | Phase 1, Phase 10 | Policy ADR; `task.md` paraphrase-only review; no course PDFs in `assets/` |
| C6 LFS and history bloat | Phase 1, Phase 6 | `.gitattributes` covers binaries; size budget check; `.git` size trend flat |
| C7 Unpinned versions | Phase 2, Phase 6 | Pin audit passes; rebuild from a clean cache matches |
| C8 Test library leakage | Phase 3, Phase 7 | `pio test -e native` passes in a fresh container without target toolchains |
| C9 clangd headers | Phase 4 | `clangd --check` clean on a target source file |
| C10 Simulation vs hardware | Phase 5, Phase 8 | Limitations matrix exists; reports label evidence tier |
| C11 Simulation as blocking CI | Phase 5, Phase 6 | Simulation is label-gated or nightly; artifacts on failure |
| C12 Mock drift | Phase 7 | Same-header compilation; contract tests; at least one HIL/real-device run per driver |
| C13 Fabricated measurements | Phase 2, Phase 8, Phase 10 | Measurement ledger complete; evidence linked in PR |
| C14 Squash/tag traceability | Phase 1, Phase 6 | Automated tag on `main`; PR body contains evidence; branch auto-delete |
| C15 Premature abstraction | Phase 3 | No interface without two consumers; ADR lists non-goals |
| C16 CI cost explosion | Phase 6, Phase 9 | Changed-project filtering; CI duration budget tracked |
| M1 `lib_extra_dirs` | Phase 2 | Dependency graph shows expected libraries |
| M2 `lib_ignore` names | Phase 3 | Native graph contains no target-only library |
| M3 IDF components | Phase 2 | ESP-IDF template builds without `lib_deps` for components |
| M4 clangd/cpptools conflict | Phase 4 | One diagnostics source in the workspace |
| M5 Multi-root clangd | Phase 4 | Per-root `.clangd` present; navigation stays local |
| M6 GCC-only flags | Phase 4 | No unknown-argument diagnostics |
| M7 Concurrency semantics | Phase 3 | ISR-safety documented per function; no blocking calls in ISR paths |
| M8 Non-determinism | Phase 7 | Repeated native runs are stable |
| M9 ISR timing on host | Phase 7 | Timing claims backed by hardware evidence only |
| M10 Cache key | Phase 6 | New dependency triggers a cache miss |
| M11 Actions permissions | Phase 6 | Workflow starts with `contents: read`; actions pinned to SHA |
| M12 Generated drift | Phase 2, Phase 6 | `generate` leaves a clean tree |
| M13 Personal data | Phase 2, Phase 8, Phase 10 | Asset checklist completed; logs scrubbed |
| M14 Unsupported parts | Phase 5, Phase 8 | Support matrix checked at intake |
| M15 Traceability | Phase 2, Phase 8 | Every requirement has evidence or a deviation |
| M16 Branch hygiene | Phase 1, Phase 9 | No branch older than one week; tags consistent |
| M17 Coverage gaps | Phase 7 | Per-layer coverage; adapters tracked separately |

## Ordering Implications for the Roadmap

These pitfalls force a few ordering constraints:

1. **Repository policy must precede the first public push.** Secrets scanning, `.gitignore`,
   `.gitattributes`/LFS rules, license, and the copyright/academic-integrity ADR cannot be
   retrofitted without history rewrites that the Git policy forbids. Phase 1 is not
   optional setup; it is a gate.
2. **The dependency rule must be enforced before shared libraries accumulate consumers.**
   A rule added after ten homeworks requires a repo-wide cleanup. Build the CI grep and
   native compile in the same phase as the first shared library.
3. **The simulation spike must precede any CI simulation gate and any homework that depends
   on simulation evidence.** Tool limitations (BLE, MCPWM, multi-MCU, timing, token,
   timeout) determine the testing tiers and the evidence wording in reports.
4. **Developer tooling can be parallel to shared libraries but must precede scale-out.**
   clangd failures are tolerable for one pilot and corrosive for 30+ projects and a novice
   user.
5. **CI should start with lint/metadata and changed-project builds, then add simulation.**
   Starting with a full matrix and cloud simulation creates the exact cost and flakiness
   traps above.
6. **Report and evidence gates belong in the pilot.** If the measurement ledger, safety
   checklist, and traceability matrix are not enforced on homework 1.3, thirty later reports
   will not have them.

## Sources

- PlatformIO docs: `lib_extra_dirs`, `lib_ignore`, `test_build_src`, `test_filter`, and ESP-IDF builder behavior (Context7: `/platformio/platformio-docs`, HIGH).
- PlatformIO + ESP-IDF integration issues and community threads: `platform-espressif32` issue #1031, "Conflicting build systems when finding components" (MEDIUM-HIGH; concrete failure modes, some version-specific).
- clangd documentation: System Headers guide, Troubleshooting, Compile Commands design (HIGH).
- pioarduino VS Code extension `docs/intellisense.md` — `fixupCompileCommands()`, `--query-driver` globs, patched clangd (HIGH for the recommended recipe).
- `platformio/platformio-core` issue #4092 — GCC-specific flag diagnostics after `--query-driver` (MEDIUM).
- clangd/vscode-clangd issues #38 and #438; microsoft/vscode-cpptools issues #7029 and #11610 (HIGH for multi-root and IntelliSense conflicts).
- Wokwi docs: ESP32 simulation feature table, supported hardware, CLI README, roadmap (HIGH for stated limitations; support matrices change over time).
- GitHub Docs: Actions limits (6-hour job, 10 GB cache, 256-job matrix), `GITHUB_TOKEN` and secure-use guidance, Git LFS billing (10 GiB storage and bandwidth on Free) (HIGH).
- PlatformIO CI documentation and community reports on caching `~/.platformio`, `build_cache_dir`, and LDF-triggered rebuilds (MEDIUM).
- University academic-integrity and IP policies (MIT 6.102/6.4500, University of Waterloo, University of Sheffield, Georgetown) — representative, not authoritative for the specific institution (MEDIUM; verify the actual course policy).
- Practical embedded testing and abstraction experience encoded in the project's own architecture decisions (`PROJECT.md`) — no speculative HAL, thin port, adapters (project-specific, HIGH as a design constraint).

---

*Pitfalls research for: embedded engineering course monorepo*
*Researched: 2026-10-23*
