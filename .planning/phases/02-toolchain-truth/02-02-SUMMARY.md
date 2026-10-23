---
phase: 02-toolchain-truth
plan: 02
subsystem: repo-hygiene
tags: [gitignore, pre-commit, esp-idf, build-artifacts, d-23]

# Dependency graph
requires:
  - phase: 01-repository-foundation-and-policy-gate
    provides: The `.gitignore` categories and the `scripts/tests/test_gitignore.py` contract suite; the `no-generated-files` pre-commit hook
provides:
  - Scoped `.gitignore` rules for the three ESP-IDF build outputs written into a project tree
  - The order-sensitive negation that keeps the authored `sdkconfig.defaults` visible
  - A `D-23` category and two new `VISIBLE` entries in the gitignore contract suite
  - A `no-generated-files` hook covering the same path list, with git's exit status bound
affects: [02-04, 03, 08]

# Actuals (#2632) — chars/4 over the realized diff, same scale as the plan's estimate.
actuals:
  tokens: 1506
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-layer generated-file gate: `.gitignore` for the accidental add, the `no-generated-files` hook for `git add -f`"
    - "Order-sensitive negation after a broad glob, pinned as a visibility pair in one test"

key-files:
  created: []
  modified:
    - .gitignore
    - scripts/tests/test_gitignore.py
    - .pre-commit-config.yaml

key-decisions:
  - "Scoped every D-23 pattern under `homeworks/*/` instead of banning a filename repository-wide, so a future authored CMake project stays committable"
  - "Placed `!homeworks/*/sdkconfig.defaults` immediately after `homeworks/*/sdkconfig.*`; the order is load-bearing (P7)"
  - "Kept two separate CMake patterns because a project-root pattern does not match the nested `src/` file (P6, verified)"
  - "Extended the `no-generated-files` hook rather than deferring it, so `git add -f` cannot bypass the ignore rules"
  - "Bound git's exit status with `|| exit 1` before testing the captured list, so a git error cannot pass as an empty result"

patterns-established:
  - "Ignore-pattern changes ship with a paired visibility assertion, never a one-direction-only test"
  - "Every hook pathspec wildcard is double-quoted inside the single-quoted `bash -c` body"

requirements-completed: [FOUND-09]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "ESP-IDF build outputs written into a project tree (`CMakeLists.txt`, `src/CMakeLists.txt`, `sdkconfig.<env>`) are ignored by git"
    requirement: FOUND-09
    verification:
      - kind: integration
        ref: "scripts/tests/test_gitignore.py#test_ignored_categories (category 'esp-idf build-generated (D-23)')"
        status: pass
      - kind: manual_procedural
        ref: "git check-ignore -v homeworks/0_0-toolchain-smoke/{CMakeLists.txt,src/CMakeLists.txt,sdkconfig.esp32s3_espidf}"
        status: pass
    human_judgment: false
  - id: D2
    description: "The authored `sdkconfig.defaults` stays visible to git despite the broad `sdkconfig.*` pattern"
    requirement: FOUND-09
    verification:
      - kind: integration
        ref: "scripts/tests/test_gitignore.py#test_sdkconfig_defaults_is_visible_and_env_output_is_not"
        status: pass
      - kind: manual_procedural
        ref: "git check-ignore -q homeworks/0_0-toolchain-smoke/sdkconfig.defaults -> exit 1"
        status: pass
    human_judgment: false
  - id: D3
    description: "Bare `sdkconfig` and a repository-root `CMakeLists.txt` stay visible, so no global filename is banned"
    requirement: FOUND-09
    verification:
      - kind: integration
        ref: "scripts/tests/test_gitignore.py#test_visible_paths_are_not_ignored (VISIBLE includes 'sdkconfig' and 'CMakeLists.txt')"
        status: pass
      - kind: manual_procedural
        ref: "git check-ignore -q CMakeLists.txt -> exit 1"
        status: pass
    human_judgment: false
  - id: D4
    description: "The `no-generated-files` hook covers the same ESP-IDF paths and fails on a tracked-but-ignored path"
    requirement: FOUND-09
    verification:
      - kind: manual_procedural
        ref: "pre-commit run no-generated-files --all-files -> Passed; forced-stage probe (git add -f homeworks/zz-hookcheck/CMakeLists.txt) -> Failed with the path listed, then unstaged"
        status: pass
      - kind: manual_procedural
        ref: "git ls-files -ci --exclude-standard -- compile_commands.json site .pio \"homeworks/*/CMakeLists.txt\" \"homeworks/*/src/CMakeLists.txt\" \"homeworks/*/sdkconfig.*\" -> empty"
        status: pass
    human_judgment: false

# Metrics
duration: ~1 min
completed: 2026-10-23
status: complete
---

# Phase 02 Plan 02: ESP-IDF Build-Generated Ignore Hygiene Summary

**Scoped `.gitignore` block plus a matching `no-generated-files` hook keep the three ESP-IDF build outputs out of history while the authored `sdkconfig`, `sdkconfig.defaults` and a root `CMakeLists.txt` stay committable.**

## Performance

- **Duration:** ~1 min
- **Started:** 2026-10-23T19:48:53Z
- **Completed:** 2026-10-23T19:49:44Z
- **Tasks:** 2/2
- **Files modified:** 3

## Accomplishments

- `.gitignore` now ignores `homeworks/*/CMakeLists.txt`, `homeworks/*/src/CMakeLists.txt` and `homeworks/*/sdkconfig.*`, with `!homeworks/*/sdkconfig.defaults` immediately after the broad pattern.
- `scripts/tests/test_gitignore.py` carries a new `esp-idf build-generated (D-23)` IGNORED category, two new `VISIBLE` entries (`homeworks/0_0-toolchain-smoke/sdkconfig.defaults`, root `CMakeLists.txt`) and a dedicated visibility-pair test.
- The `no-generated-files` pre-commit hook covers the same pathspecs, double-quotes every wildcard inside its `bash -c` body, and binds git's exit status before testing the captured list.

## Final `.gitignore` block

Placed directly after the existing `# ESP-IDF artifacts` block, patterns at lines 24-28:

```gitignore
homeworks/*/CMakeLists.txt
homeworks/*/src/CMakeLists.txt
homeworks/*/sdkconfig.*
# Order-sensitive: re-includes the authored fragment after the broad pattern (P7).
!homeworks/*/sdkconfig.defaults
```

The comment above the block names D-23 and distinguishes the three `sdkconfig` forms: bare `sdkconfig` (per-project configuration, tracked), `sdkconfig.defaults` (authored Kconfig fragment, tracked), `sdkconfig.<env>` (build-written, ignored). No repository-wide `sdkconfig` or `CMakeLists.txt` pattern exists, and `platformio.shared.ini` was deliberately left out of the file (D-04).

## `git check-ignore` evidence

```text
$ git check-ignore -v homeworks/0_0-toolchain-smoke/CMakeLists.txt \
      homeworks/0_0-toolchain-smoke/src/CMakeLists.txt \
      homeworks/0_0-toolchain-smoke/sdkconfig.esp32s3_espidf
.gitignore:24:homeworks/*/CMakeLists.txt        homeworks/0_0-toolchain-smoke/CMakeLists.txt
.gitignore:25:homeworks/*/src/CMakeLists.txt    homeworks/0_0-toolchain-smoke/src/CMakeLists.txt
.gitignore:26:homeworks/*/sdkconfig.*           homeworks/0_0-toolchain-smoke/sdkconfig.esp32s3_espidf

$ git check-ignore -q homeworks/0_0-toolchain-smoke/sdkconfig.defaults ; echo $?
1

$ git check-ignore -q CMakeLists.txt ; echo $?
1
```

Both `-q` checks return 1 (not ignored), which is what the suite and the plan's `<verify>` assert.

## The hook decision and its reason

The hook was **extended, not deferred**. `.gitignore` only stops an accidental `git add .`; `git add -f` bypasses it entirely, so extending the ignore rules without extending the hook would have left the second control blind to exactly the files D-23 adds. The entry now runs

```text
git ls-files -ci --exclude-standard -- compile_commands.json site .pio \
  "homeworks/*/CMakeLists.txt" "homeworks/*/src/CMakeLists.txt" "homeworks/*/sdkconfig.*"
```

- Every wildcard pathspec is double-quoted inside the single-quoted `bash -c` body; unquoted, the inner shell would expand it against the working tree and the pathspec would silently degrade.
- `|| exit 1` is bound to the substitution before `[ -n "$tracked" ]` is tested, so a git failure cannot read as "nothing tracked".
- No `:(exclude)` pathspec for `sdkconfig.defaults` was added: `-i` lists only tracked paths git considers ignored, and the negation keeps that file non-ignored. If the negation were ever removed, the test suite fails first and the hook then reports the file — both layers fail loudly.
- Evidence that the hook actually fires: a temporary `homeworks/zz-hookcheck/CMakeLists.txt` was force-staged, `pre-commit run no-generated-files --all-files` failed with `tracked generated paths: homeworks/zz-hookcheck/CMakeLists.txt`, and the file was then unstaged and removed. The tree is clean.

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend .gitignore for ESP-IDF build-generated files** - `e541519` (chore)
2. **Task 2: Extend the no-generated-files hook and record the reason** - `2395695` (chore)

**Plan metadata:** committed separately as `docs(02-02): complete ESP-IDF ignore hygiene plan`.

## Files Created/Modified

- `.gitignore` - new `# ESP-IDF build-generated files ... (D-23)` comment block plus four scoped patterns with the `sdkconfig.defaults` negation
- `scripts/tests/test_gitignore.py` - `IGNORED["esp-idf build-generated (D-23)"]`, the `VISIBLE` entries for `homeworks/0_0-toolchain-smoke/sdkconfig.defaults` and root `CMakeLists.txt`, and `test_sdkconfig_defaults_is_visible_and_env_output_is_not`
- `.pre-commit-config.yaml` - the D-23 comment and the extended `no-generated-files` entry with quoted wildcard pathspecs and `|| exit 1`

## Decisions Made

- Patterns are scoped to `homeworks/*/` rather than banning `CMakeLists.txt` or `sdkconfig.*` repository-wide. A global `CMakeLists.txt` rule would hide a future authored CMake homework; a global `sdkconfig.*` rule would reach outside project trees. The root-`CMakeLists.txt` VISIBLE entry makes a regression fail the suite.
- Two CMake patterns are kept because a pattern for the project-root file does not match the nested `src/` one (P6, verified). The `02-PATTERNS.md` remark that one pattern covers both depths is superseded by P6, as the plan states.
- The negation sits immediately after the broad pattern — git resolves the last matching pattern, so reversing the order would make `sdkconfig.defaults` ignored again (P7).
- `platformio.shared.ini` was not added to `.gitignore` (D-04): it is committed configuration, not a build product, and the new test asserts it stays visible.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- **`git check-ignore -v` and a negation.** Verbose mode exits 0 for a path whose *last matching pattern is a negation*, while `-q` exits 1 (not ignored). Measured here: `-v` on `homeworks/0_0-toolchain-smoke/sdkconfig.defaults` printed `.gitignore:28:!homeworks/*/sdkconfig.defaults` and exited 0; `-q` exited 1, and `-v` on `README.md` (no matching pattern) exited 1. The suite and the plan's `<verify>` both use the `-q` form, so the assertions are correct — but a future maintainer must not "fix" the exit status by switching to `-v`, which would make the visibility test pass for the wrong reason.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **For plan 02-04:** the ESP-IDF project can commit `homeworks/0_0-toolchain-smoke/sdkconfig.defaults` with a plain `git add`; the negation keeps it visible and the hook will not report it.
- **For Phase 3 (D-07):** the two scoped CMake patterns (`homeworks/*/CMakeLists.txt`, `homeworks/*/src/CMakeLists.txt`) must be removed in the same change that deletes `homeworks/0_0-toolchain-smoke/`, so the ignore block does not outlive the only project it serves. The `homeworks/*/sdkconfig.*` pattern and its negation are generic and stay.
- **For Phase 8 (TOOL-05):** the CI meta job should re-run `pre-commit run --all-files`, which carries both defence layers forward; this plan deliberately did not add a workflow.
- **Verification state:** `python3 -m unittest scripts.tests.test_gitignore -v` — 12 tests, OK. Full repository suite (`python3 -m unittest discover -s scripts/tests -v`) — 111 tests, OK. `pre-commit run no-generated-files --all-files` — Passed.

## Self-Check: PASSED

---

*Phase: 02-toolchain-truth*
*Completed: 2026-10-23*
