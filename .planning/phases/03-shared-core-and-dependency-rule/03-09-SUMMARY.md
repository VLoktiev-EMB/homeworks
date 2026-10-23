---
phase: 03-shared-core-and-dependency-rule
plan: 09
subsystem: testing
tags: [platformio, native, compilation-database, determinism, unity, fixture, dependency-rule]

# Dependency graph
requires:
  - phase: 03-shared-core-and-dependency-rule
    plan: 01
    provides: "the host-only tests/ project, the compiledb hook and the first seven suite cases"
  - phase: 03-shared-core-and-dependency-rule
    plan: 03
    provides: "the final port contract vocabulary the shared sources compile against"
  - phase: 03-shared-core-and-dependency-rule
    plan: 04
    provides: "lib/host fakes for all five contracts"
  - phase: 03-shared-core-and-dependency-rule
    plan: 05
    provides: "the cross-fake suite that completes the seven-suite inventory"
  - phase: 03-shared-core-and-dependency-rule
    plan: 06
    provides: "the adapter sources the relative-include fixture copies"
  - phase: 03-shared-core-and-dependency-rule
    plan: 07
    provides: "the final tree shape with no smoke project"
provides:
  - "Compile-time proof that the native database names only a host compiler and no framework include"
  - "Proof that all nine shared sources and tests/src/main.c are really compiled"
  - "A framework-include fixture that fails the native build"
  - "An executed measurement that a relative cross-library include compiles, so only the checker guards it"
  - "A twenty-run normalized digest proof with all seven suites asserted"
  - "An offline unit test that pins the digest parser"
affects: [03-verify, 06, 08]

# Actuals (#2632) — chars/4 over the realized plan diff (21410 chars), not a harness count.
actuals:
  tokens: 5353
  tasks: 2
  commits: 2
  plan_head_before: ddea02efdcd678ab17c3ef9bd7ecfb1603a25a3a
  plan_head_after: 6c68f1b54256649765019b17dceb02e38db0a343

tech-stack:
  added: []
  patterns:
    - "Compilation-database purity is asserted entry by entry with subTest, resolving a relative file against its directory first"
    - "A negative fixture copies the tree, injects a header and proves the build outcome; every touched path is resolved and asserted inside the temporary root"
    - "A positive fixture records the limit: the compiler accepts a relative cross-library include, so the textual checker is the only guard"
    - "Determinism is a per-line anchored digest of suite/test_name: STATUS plus counts derived from those rows"
    - "The digest parser is pinned offline with a synthetic transcript, so a future widening fails without running PlatformIO"

key-files:
  created:
    - scripts/tests/test_native_purity.py
    - scripts/tests/test_native_determinism.py
  modified: []

key-decisions:
  - "The fixtures build with pio test rather than pio run: PlatformIO generates Unity's unity_config.h only inside the test runner, so a clean pio run cannot compile Unity at all; pio test is the same build the suite uses and the measured outcomes are unchanged"
  - "The database assertion resolves each entry's file against its directory field, because PlatformIO records project sources as src/main.c relative to tests/ while library sources are absolute"
  - "The fixture ignores .pio and compile_commands.json on every copy and never uses symlinks=True, because libdeps symlinks point back into the real tree"
  - "The digest keeps RUNS = 20 with no override; the single pio test command is the local fast path"
  - "ConfigurationGuardTests deliberately repeats one checker rule as a regression guard on the committed tree"

patterns-established:
  - "A proof states its own limit in the module docstring and executes the limit as a passing fixture"
  - "Fixture containment is asserted with Path.resolve().is_relative_to(temporary_root) before any build runs"
  - "A digest counts its statuses from the parsed rows, never from PlatformIO's summary, which does not correspond one-to-one with Unity cases"

requirements-completed: [ARCH-02, ARCH-05, ARCH-06]

coverage:
  - id: D1
    description: "Every entry in tests/compile_commands.json names a host compiler and carries no Xtensa, RISC-V, ESP-IDF or framework include path"
    requirement: ARCH-06
    verification:
      - kind: integration
        ref: "scripts/tests/test_native_purity.py#test_compiledb_build_succeeds"
        status: pass
      - kind: integration
        ref: "scripts/tests/test_native_purity.py#test_every_entry_uses_a_host_compiler"
        status: pass
      - kind: integration
        ref: "scripts/tests/test_native_purity.py#test_database_is_non_empty_and_every_entry_is_well_formed"
        status: pass
    human_judgment: false
  - id: D2
    description: "All nine shared translation units and tests/src/main.c appear in the database, proving they were compiled rather than skipped"
    requirement: ARCH-06
    verification:
      - kind: integration
        ref: "scripts/tests/test_native_purity.py#test_required_shared_sources_are_compiled"
        status: pass
    human_judgment: false
  - id: D3
    description: "A framework include in a copy of lib/common makes the native build fail and the failure names Arduino.h"
    requirement: ARCH-05
    verification:
      - kind: integration
        ref: "scripts/tests/test_native_purity.py#test_framework_include_fails_the_build"
        status: pass
    human_judgment: false
  - id: D4
    description: "A relative cross-library include in a copy of lib/common compiles, recording that the compiler does not enforce that edge"
    requirement: ARCH-05
    verification:
      - kind: integration
        ref: "scripts/tests/test_native_purity.py#test_relative_cross_library_include_compiles"
        status: pass
    human_judgment: false
  - id: D5
    description: "host=symlink:// appears only under [env:native] in every committed platformio.ini"
    requirement: ARCH-03
    verification:
      - kind: unit
        ref: "scripts/tests/test_native_purity.py#test_host_symlink_appears_only_under_env_native"
        status: pass
    human_judgment: false
  - id: D6
    description: "Twenty consecutive suite runs exit zero, produce one identical digest, cover all seven suites and report a nonzero passed count with failed=0"
    requirement: ARCH-06
    verification:
      - kind: integration
        ref: "scripts/tests/test_native_determinism.py#test_twenty_runs_produce_one_identical_digest"
        status: pass
    human_judgment: false
  - id: D7
    description: "The digest parser is pinned offline: it drops paths, assertion messages and durations, separates duplicate names by suite and derives counts from the rows"
    requirement: ARCH-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_native_determinism.py#test_digest_pins_the_exact_normalization"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_native_determinism.py#test_digest_drops_paths_messages_and_durations"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_native_determinism.py#test_duplicate_test_names_stay_separated_by_suite"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_native_determinism.py#test_digest_of_empty_output_has_zero_counts"
        status: pass
    human_judgment: false

duration: 5 min
completed: 2026-10-24
status: complete
---

# Phase 03 Plan 09: Native Purity and Twenty-Run Determinism Summary

**The native compilation database is proven host-only with all nine shared sources compiled, a framework include is proven to fail the build while a relative cross-library include is proven to compile, and twenty consecutive suite runs produce one identical anchored digest covering all seven suites.**

## Performance

- **Duration:** ~5 min (22:39:38Z to 22:44:26Z)
- **Started:** 2026-10-23T22:39:38Z
- **Completed:** 2026-10-23T22:44:26Z
- **Tasks:** 2
- **Files modified:** 2 created (535 insertions, 0 deletions)

## Accomplishments

- `scripts/tests/test_native_purity.py` proves the compile-time half of ARCH-06: every database entry names a host compiler and no target-toolchain or framework token, and the nine shared sources plus `tests/src/main.c` really appear.
- The framework fixture appends `#include <Arduino.h>` to a copy of `lib/common/src/timing.c` and proves the build fails; the relative-include fixture appends `../../arduino/include/arduino/time.h` and proves it succeeds, recording that only the textual checker guards that edge.
- Both fixtures copy into `tempfile.TemporaryDirectory()`, assert every touched path resolves inside it, and leave the real tree unchanged (`git status --short` showed only the two new modules).
- `scripts/tests/test_native_determinism.py` runs the suite twenty times after one warm-up build and asserts one identical digest, every run green, a row for each of the seven suites, a nonzero `passed=` and `failed=0`.
- Four offline unit tests pin the digest parser against a synthetic transcript containing a failure message, a duration line, a PlatformIO summary line, a duplicate test name across suites and an ignored row.
- The full repository gate passes: 142 tests OK, including both new modules.

## Task Commits

Each task was committed atomically:

1. **Task 1: Native purity proof — host-only database, framework fixture, relative-include limit fixture** - `0aa4780` (test)
2. **Task 2: Determinism proof — twenty runs, anchored per-test digest, seven suites, offline parser test** - `6c68f1b` (test)
3. **Plan metadata** - committed after this SUMMARY (not part of the measured two)

## Evidence Recorded by the Plan

### Native database

```text
entries: 11
compiler basenames: ['gcc']  (observed path /usr/bin/gcc)
required files: 10/10 found
  lib/common/src/{timing,ring_buffer,crc,hex}.c
  lib/host/src/{fake_time,fake_gpio,fake_i2c,fake_spi,fake_log}.c
  tests/src/main.c
```

The remaining entry is Unity's own `unity.c`. No command or include flag contains `xtensa`, `riscv32`, `esp-idf`, `framework-arduinoespressif32` or `toolchain-`.

### Framework fixture

The copied build printed:

```text
<tmp>/lib/common/src/timing.c:41:10: fatal error: 'Arduino.h' file not found
   41 | #include <Arduino.h>
      |          ^~~~~~~~~~~
1 error generated.
========================== [FAILED] ==========================
```

This is the compile-time proof that a framework dependency in `lib/common` is rejected (ARCH-05).

### Relative-include fixture and its limit

The second fixture injected `#include "../../arduino/include/arduino/time.h"` into the copy of `lib/common/src/timing.c` and the build **succeeded** (exit code 0, 73/73 cases). That is the measured limit: a relative cross-library include compiles and links, so the compiler does not enforce the `common -> port` edge. `scripts/check_architecture.py` is the only guard for it. The module docstring states this, so a future claim that the compiler rejects the case contradicts an executed test.

### Twenty-run determinism

```text
warm-up runs: 1
measured runs: 20
exit codes: all 0
rows per digest: 73
first-run digest tail: passed=73, failed=0, ignored=0
first row: test_common_crc/test_crc16_check_value: PASSED
suites present: test_common_crc, test_common_hex, test_common_ring_buffer,
                test_common_timing, test_host_fake_time, test_host_fakes,
                test_port_contracts
distinct digests across 20 runs: 1
measured wall time: 54.6 s for the module (21 sequential pio test invocations,
                    ~2.6 s each after the warm-up)
```

The digest drops paths, line numbers, assertion messages, durations and PlatformIO's summary table; counts are derived from the parsed rows.

## Files Created/Modified

- `scripts/tests/test_native_purity.py` - database purity assertions, the shared fixture helper with containment assertions, the framework and relative-include fixtures, and `ConfigurationGuardTests`
- `scripts/tests/test_native_determinism.py` - `RUNS`, `TEST_LINE`, `digest`, four offline parser tests and the twenty-run `DeterminismTests`

## Decisions Made

- **The fixtures build with `pio test`, not `pio run`.** PlatformIO generates Unity's `unity_config.h` only inside the test runner (`platformio/test/runners/unity.py`), so a clean tree cannot compile Unity under `pio run` at all. The measured properties are unchanged and the copy now exercises the same build the suite uses.
- **The database assertion resolves relative entries.** PlatformIO records `tests/src/main.c` relative to the entry's `directory` and library sources absolutely, so the assertion resolves both before comparing.
- **The fixture never copies `.pio`.** Its `libdeps` entries are `symlink://` links back into the real tree, and following them would compile the real sources instead of the copy. Every touched path is asserted inside the temporary root.
- **`RUNS = 20` is a constant.** An overridable count would let a proof pass with fewer runs and silently weaken the phase contract; the single `pio test` command is the local fast path.
- **The configuration guard duplicates one checker rule on purpose.** The checker validates configuration as policy; this test guards the committed tree against regression.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The temporary fixtures build with `pio test` instead of `pio run`**
- **Found during:** Task 1 (fixture construction)
- **Issue:** the plan specified `pio run -d tests -e native` in both fixtures. A clean copy of the tree, made with the plan's own `.pio` exclusion, fails that command with `fatal error: 'unity_config.h' file not found`: PlatformIO generates Unity's config only in the test runner, and the warm real tree masked this. The relative-include fixture could therefore never assert success.
- **Fix:** both fixtures invoke `pio test -d tests -e native` with the same 300-second timeout. The injected include and the asserted outcomes are unchanged, and the fixture now exercises the build the suite actually runs.
- **Files modified:** `scripts/tests/test_native_purity.py`
- **Verification:** a fresh fixture exits 0 with 73/73 cases (`pio test`); the framework fixture still fails naming `Arduino.h`; the relative-include fixture exits 0.
- **Committed in:** `0aa4780` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The fix is confined to the fixture's build command. It preserves every assertion and every measured outcome the plan requires, and it removes a false pass that a warm build directory would otherwise have created.

## Issues Encountered

- The cold-start coupling remains for `NativeDatabaseTests`: it runs `pio run -t compiledb` as the plan specifies, and a completely cold clone cannot compile Unity through `pio run` until a test build has generated `unity_config.h`. The full discovery gate runs `test_native_determinism` first (alphabetical order), which warms the build, so `python3 -m unittest discover -s scripts/tests -v` passes from a clean tree. Phase 8 owns CI ordering; standalone cold-clone invocation of the purity module remains a known constraint, documented here rather than worked around.
- `pio` printed a sandbox `network-outbound` notice while probing for updates. Every command still exited as asserted, so no retry was needed.
- The repository's condensing shell wrapper refused compound `git` invocations; the commits were made with plain `/usr/bin/git` inside the worktree.

## Known Stubs

None. Both modules are complete and stdlib-only; the only PlatformIO dependency is the `pio` executable the proof is explicitly about.

## Threat Model Dispositions

- **T-03-45 (Tampering, compilation database)** mitigated: every entry is asserted host-only, and the framework fixture proves the build fails when a framework header is required.
- **T-03-46 (Repudiation, digest)** mitigated: per-line anchored matches, counts derived from rows, all seven suites, `failed=0`, and an offline parser test.
- **T-03-47 (DoS, twenty sequential runs)** mitigated: one warm-up, a 300-second timeout per call, a constant run count, and a measured 54.6 s module wall time.
- **T-03-48 (Tampering, fixture containment)** mitigated: `.pio` and `compile_commands.json` ignored on copy, no `symlinks=True`, and `is_relative_to(temporary_root)` asserted for every touched path.
- **T-03-SC (package installs)** mitigated: nothing new is installed; both modules are stdlib-only and Unity is served from the already-warm cache.

## Threat Flags

None - this plan adds test modules only and introduces no new endpoint, auth path, file-access pattern or schema at a trust boundary.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both proofs join the repository gate and pass there: `python3 -m unittest discover -s scripts/tests -v` reports 142 tests OK.
- The compile gate's exact reach is now executed: it rejects a framework include and does not reject a relative cross-library include. Plan 03-08's textual checker is named as that edge's guard.
- The determinism contract is twenty runs with no override; Phase 8 can schedule it in CI as-is, with the cold-start ordering constraint above noted.

---

*Phase: 03-shared-core-and-dependency-rule*
*Completed: 2026-10-24*

## Self-Check: PASSED

- `scripts/tests/test_native_purity.py` and `scripts/tests/test_native_determinism.py` exist on disk.
- Commits `0aa4780` and `6c68f1b` are ancestors of HEAD.
- `python3 -m unittest scripts.tests.test_native_purity -v`: 7 tests OK.
- `python3 -m unittest scripts.tests.test_native_determinism -v`: 5 tests OK (twenty runs, one digest).
- `python3 -m unittest discover -s scripts/tests -v`: 142 tests OK.
