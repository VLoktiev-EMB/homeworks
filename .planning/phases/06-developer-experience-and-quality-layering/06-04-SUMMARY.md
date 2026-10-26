---
phase: 06-developer-experience-and-quality-layering
plan: 04
subsystem: developer-tooling
tags: [clang-tidy, pre-push, compilation-database, hook-layering, signed-bitwise]

# Dependency graph
requires:
  - phase: 06-developer-experience-and-quality-layering
    provides: the check-only hook posture and `default_stages: [pre-commit]` (06-01); the full fast-hook surface (06-03)
provides:
  - ".clang-tidy as the host-only, warnings-first static-analysis policy (D-07a)"
  - "scripts/clang-tidy-db, a read-only guard that owns the missing/stale database failure (D-09)"
  - "a pinned cpp-linter-hooks v1.8.1 clang-tidy 23.1.3 hook, and both hook stages installed by one command (D-07, D-10)"
  - "ClangTidyConfigTests, ClangTidyDbGuardTests, and HookLayeringTests as stdlib machine checks"
affects: [06-05, phase-08-ci]

actuals:
  tokens: 8103
  tasks: 2
  commits: 3
  plan_head_before: c74113935ed2c3ec32aa526bebc8a3bde10d131c
  plan_head_after: 0680181d713fcefb43a4a41bb679de1aa35a11e8

tech-stack:
  added: [clang-tidy 23.1.3 via cpp-linter-hooks v1.8.1]
  patterns:
    - "A local guard owns a failure the upstream hook deliberately skips, and runs before it in file order"
    - "Resolve a compile-database `file` against that entry's own `directory`, never the repository root"
    - "Declare every hook's stage explicitly as well as `default_stages`: an upstream manifest's `stages` overrides the default"
    - "Prove a static-analysis gate non-vacuous by injecting a defect and requiring a named diagnostic, then restoring byte-for-byte"

key-files:
  created:
    - .clang-tidy
    - scripts/clang-tidy-db
  modified:
    - .pre-commit-config.yaml
    - lib/common/src/hex.c
    - lib/common/src/crc.c
    - scripts/tests/test_tooling_config.py

key-decisions:
  - "The guard runs as its own local repo placed above cpp-linter-hooks, because pre-commit executes repositories in file order and cpp-linter-hooks skips silently without a database."
  - "`file` entries are composed against the entry's `directory` field before the mtime test; resolving against the repository root would report false staleness for `src/main.c` and the Unity source."
  - "Both push hooks keep the widened `(src|include)` pattern: the header probe exited 0 for a common header and a port header, so no narrowing branch was taken."
  - "Four additional readability rules are disabled as repository style policy; the seven `bugprone-signed-bitwise` findings are real and fixed in source rather than suppressed."
  - "Every fast hook declares `stages: [pre-commit]` explicitly, because the pinned pre-commit-hooks manifest gives three hooks their own pre-push stage."

patterns-established:
  - "A hook's own `stages` beats `default_stages`; with two installed stages, declare the stage twice or the layering silently widens."
  - "A guard that blocks a push must name the exact developer command that repairs the condition, and must never run it."
  - "A compile database is stale after any described source edit; regenerate it as a developer action, never inside the hook."

requirements-completed: [TOOL-01, TOOL-03]

coverage:
  - id: D1
    description: "`.clang-tidy` selects bugprone, cert, performance, portability, readability, and clang-analyzer; disables the pragma-once policy; and keeps `WarningsAsErrors` empty"
    requirement: TOOL-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#ClangTidyConfigTests"
        status: pass
    human_judgment: false
  - id: D2
    description: "The guard exits 1 with `pio run -d tests -e native -t compiledb` when the database is absent or stale, 2 when unreadable, 0 when fresh, and resolves relative `file` entries from their own `directory`"
    requirement: TOOL-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#ClangTidyDbGuardTests"
        status: pass
      - kind: integration
        ref: "python3 scripts/clang-tidy-db (fresh worktree database)"
        status: pass
    human_judgment: false
  - id: D3
    description: "pre-push runs exactly the database guard and the pinned clang-tidy hook; every fast hook runs only at pre-commit; the guard precedes cpp-linter-hooks"
    requirement: TOOL-03
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#HookLayeringTests"
        status: pass
      - kind: integration
        ref: "pre-commit run --all-files --hook-stage pre-push (two hooks, exit 0)"
        status: pass
    human_judgment: false
  - id: D4
    description: "clang-tidy 23.1.3 analyses every in-scope host source with no diagnostic, and a deliberately injected signed-bitwise defect makes the same hook fail and name the injected function"
    requirement: TOOL-01
    verification:
      - kind: integration
        ref: "pre-commit run clang-tidy --hook-stage pre-push --all-files (exit 0)"
        status: pass
      - kind: integration
        ref: "deliberate-violation probe on lib/common/src/hex.c (exit 1, bugprone at the injected line, file restored identical)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Both pre-push hooks reach `lib/common/include/**` and `lib/host/include/**` as well as the source tree"
    requirement: TOOL-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#HookLayeringTests.test_the_guard_pattern_reaches_both_include_trees"
        status: pass
      - kind: integration
        ref: "pre-commit run clang-tidy --hook-stage pre-push --files lib/common/include/common/hex.h and lib/port/include/port/gpio.h (both exit 0)"
        status: pass
    human_judgment: true
    rationale: "A zero exit for a bare header is the plan's documented criterion, but it does not by itself prove the borrowed translation unit analysed the header rather than skipping it. Plan 06-05 records the conclusion in ADR 0013."
  - id: D6
    description: "The seven real `bugprone-signed-bitwise` findings are fixed by explicit unsigned casts, and the native suite stays green"
    requirement: TOOL-01
    verification:
      - kind: integration
        ref: "pio test -d tests -e native (73 cases)"
        status: pass
      - kind: integration
        ref: "pre-commit run clang-tidy --hook-stage pre-push --all-files (no diagnostic)"
        status: pass
    human_judgment: false
  - id: D7
    description: "The local fast gate stays green with the new hook surface"
    requirement: TOOL-03
    verification:
      - kind: integration
        ref: "pre-commit run --all-files (13 hooks)"
        status: pass
      - kind: integration
        ref: "python3 -m unittest discover -s scripts/tests (331 tests)"
        status: pass
      - kind: integration
        ref: "python3 scripts/check_architecture.py"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-10-26
status: complete
---

# Phase 6 Plan 04: Pre-Push Static Analysis Summary

**A pinned clang-tidy 23.1.3 pre-push layer with a read-only database guard that fails loudly with the exact regeneration command, and the seven real signed-bitwise findings fixed in source**

## Performance

- **Duration:** 5 min
- **Started:** 2026-10-26T11:07:45Z
- **Completed:** 2026-10-26T11:12:49Z
- **Tasks:** 2
- **Files modified:** 6 (2 created, 4 modified; 637 insertions, 7 deletions)

## Accomplishments

- `.clang-tidy` selects the six families (bugprone, cert, performance, portability, readability, clang-analyzer), disables the `#pragma once` policy, and keeps `WarningsAsErrors` empty.
- `scripts/clang-tidy-db` (mode 100755) owns the failure `cpp-linter-hooks` deliberately skips: absent → exit 1, stale → exit 1, unreadable → exit 2, fresh → exit 0. It never compiles, never runs PlatformIO, and never writes a file.
- Relative `file` entries are resolved against their own `directory`, proven by a fixture whose entries mix an absolute path, `src/main.c`, and the nested Unity source.
- Both pre-push hooks carry the widened `(src|include)` pattern for `lib/common` and `lib/host` plus the `lib/port` headers, and the guard is ordered above the clang-tidy repository.
- pre-push runs exactly two hooks; every fast hook is pinned to `pre-commit` explicitly, because three pinned upstream hooks declare their own pre-push stage.
- clang-tidy 23.1.3 reports no diagnostic over the in-scope tree, and the deliberate-violation probe proves the hook analyses rather than skips.
- All seven `bugprone-signed-bitwise` findings are fixed with explicit unsigned casts; `pio test -d tests -e native` stays green (73 cases).

## Task Commits

Each task was committed atomically:

1. **Task 1: A missing database fails the push with the exact regeneration command, and a fresh one runs clang-tidy** - `c4e2703` (feat)
2. **Task 2: Machine-check the tidy policy, the guard behaviour, and the stage layering** - `bef71e2` (test)
3. **Task 1 fix: Pin every fast hook to the pre-commit stage** - `0680181` (fix)

**Plan metadata:** committed separately (docs: complete plan summary).

## Files Created/Modified

- `.clang-tidy` - the host-only, warnings-first policy; six families, empty `WarningsAsErrors`.
- `scripts/clang-tidy-db` - the read-only guard with the 0/1/2 vocabulary and the `--dir` override.
- `.pre-commit-config.yaml` - both hook stages installed, the guard above `cpp-linter-hooks`, the pinned 23.1.3 hook, and an explicit `stages: [pre-commit]` on every fast hook.
- `lib/common/src/hex.c` - four signed-bitwise sites fixed; behaviour unchanged.
- `lib/common/src/crc.c` - the other three signed-bitwise sites fixed.
- `scripts/tests/test_tooling_config.py` - `ClangTidyConfigTests`, `ClangTidyDbGuardTests`, `HookLayeringTests`.

## Decisions Made

- The guard is a separate `local` repo placed above `cpp-linter-hooks`: file order is execution order, and a guard after the hook could never protect the gate.
- `--compile-commands=tests` is kept, because the plan requires it; the guard, not the hook, owns the database-presence failure.
- The widened pattern stays on both hooks because both header probes exited 0; no narrowing branch was taken and no include flags were hand-maintained.
- The four extra readability rules are disabled as policy, not as suppression of a defect: the tree's lowercase `0u` convention and its plain arithmetic are deliberate.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The prescribed readability family produced 69 findings the plan did not anticipate**
- **Found during:** Task 1
- **Issue:** The plan states that the only remaining in-scope findings are the seven `bugprone-signed-bitwise` sites. With `readability-*` enabled as instructed, clang-tidy 23.1.3 also reports 65 `readability-uppercase-literal-suffix`, 3 `readability-math-missing-parentheses`, 1 `readability-implicit-bool-conversion`, and 1 `readability-trailing-comma` in seven files.
- **Fix:** Disabled those four rules in `.clang-tidy` as repository style policy, alongside the four the plan already disables. The six families and the empty `WarningsAsErrors` stay as specified; no `NOLINT` was added.
- **Files modified:** `.clang-tidy`
- **Verification:** `pre-commit run clang-tidy --hook-stage pre-push --all-files` exits 0 with no diagnostic.
- **Committed in:** `c4e2703`

**2. [Rule 1 - Bug] Three of the seven signed-bitwise findings are in `crc.c`, not `hex.c`**
- **Found during:** Task 1
- **Issue:** The plan says the seven findings are all in `lib/common/src/hex.c`. The measured split is four in `hex.c` and three in `crc.c`.
- **Fix:** Fixed all seven at their real sites in both files with `unsigned int` casts (including the shift-amount literals, which were the remaining signed operands). Behaviour and comments unchanged.
- **Files modified:** `lib/common/src/hex.c`, `lib/common/src/crc.c`
- **Verification:** clang-tidy reports no diagnostic; `pio test -d tests -e native` (73 cases) and `clang-format` both pass.
- **Committed in:** `c4e2703`

**3. [Rule 1 - Bug] Three pinned upstream hooks override `default_stages` and ran at pre-push**
- **Found during:** Task 1 close-out, verified with `pre-commit run --all-files --hook-stage pre-push`
- **Issue:** The must-have requires pre-push to run exactly the two clang-tidy hooks. The pinned `pre-commit-hooks` v6.0.0 manifest declares `stages: [pre-commit, pre-push, manual]` for `trailing-whitespace`, `end-of-file-fixer`, and `check-added-large-files`; a hook's own stages override the top-level `default_stages`, so five hooks ran at pre-push.
- **Fix:** Every fast hook now declares `stages: [pre-commit]` explicitly (RESEARCH Pattern 2, "declared twice"), and `HookLayeringTests` asserts the per-hook stage for all thirteen fast hooks and the absence of a pre-commit stage on the two push hooks.
- **Files modified:** `.pre-commit-config.yaml`, `scripts/tests/test_tooling_config.py`
- **Verification:** `pre-commit run --all-files --hook-stage pre-push` lists exactly `clang-tidy-db` and `clang-tidy`, exit 0.
- **Committed in:** `0680181`

**4. [Rule 3 - Blocking] Task 1's first verify names a test class that Task 2 authors**
- **Found during:** Task 1
- **Issue:** Task 1's `<verify>` runs `scripts.tests.test_tooling_config.ClangTidyDbGuardTests`, but Task 2's `<files>` owns `scripts/tests/test_tooling_config.py`; the class does not exist during Task 1.
- **Fix:** During Task 1 the guard was exercised directly (absent, malformed, mixed-relative fixture, fresh), and the class was run after Task 2 landed. Verification-form defect only; no production change.
- **Files modified:** none
- **Verification:** `python3 -m unittest scripts.tests.test_tooling_config.ClangTidyDbGuardTests -v` passes after Task 2.
- **Committed in:** n/a

---

**Total deviations:** 4 auto-fixed (3 Rule 1, 1 Rule 3; one verification-form defect)
**Impact on plan:** Two deviations correct plan text that contradicted measured behaviour (the finding set and the finding locations); one closes a layering hole the plan's stated mechanism could not close; one is a task-ordering defect. No contract was weakened, no rule disabled where a real defect existed, and no include flags were manufactured.

## Issues Encountered

- `tests/compile_commands.json` was absent at plan start; it was regenerated once with `pio run -d tests -e native -t compiledb` as a developer action, holding the expected 11 entries.
- After the source fixes the guard correctly reported the database stale (sources newer than the database); it was regenerated again before the final gate. This is the intended contract: any described-source edit invalidates the database, and only the developer regenerates it.
- The header probe exited 0 for both `lib/common/include/common/hex.h` and `lib/port/include/port/gpio.h`, so the widened pattern was kept on both hooks. ADR 0013 (plan 06-05) must record that header diagnostics surface through the borrowed translation unit, and that `lib/port` has no translation unit of its own.
- `pre-commit run --all-files` does not exercise the pre-push hooks; the plan gate runs `pre-commit run clang-tidy --hook-stage pre-push --all-files` separately, and the layering is proven by `pre-commit run --all-files --hook-stage pre-push`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Success criterion 2 is met: clang-tidy 23.1.3 runs bugprone, cert, performance, portability, readability, and clang-analyzer checks on host code at pre-push.
- Success criterion 4's layering half is met and machine-checked: pre-push runs exactly the guard and clang-tidy.
- TOOL-01 and TOOL-03 are marked complete in `REQUIREMENTS.md`; the shared-ID gate for TOOL-03 was satisfied because 06-03's summary exists.
- Plan 06-05 owns ADR 0013 and must record the header-probe outcome and the D-08a native-test-TU gap.
- No blockers.

---
*Phase: 06-developer-experience-and-quality-layering*
*Completed: 2026-10-26*

## Self-Check: PASSED

- `.clang-tidy`, `scripts/clang-tidy-db`, and this SUMMARY exist on disk.
- `c4e2703`, `bef71e2`, and `0680181` are ancestors of `HEAD`.
- `python3 -m unittest discover -s scripts/tests` (331), `pre-commit run --all-files`,
  `pre-commit run clang-tidy --hook-stage pre-push --all-files`,
  `pre-commit run --all-files --hook-stage pre-push`, `pio test -d tests -e native`,
  and `python3 scripts/check_architecture.py` all exited 0.
