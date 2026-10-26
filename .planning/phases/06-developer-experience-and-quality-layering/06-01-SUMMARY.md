---
phase: 06-developer-experience-and-quality-layering
plan: 01
subsystem: developer-tooling
tags: [clang-format, pre-commit, formatting, esp-idf-approximation]

# Dependency graph
requires:
  - phase: 05-generated-views-and-documentation-site
    provides: the check-only hook pattern (05/D-21) and the generated-view drift gate
provides:
  - ".clang-format as the single C/C++ style source (D-02, D-03)"
  - "a check-only mirrors-clang-format v23.1.3 hook scoped to the pre-commit stage (D-04, D-06)"
  - "the entire tracked C/C++ tree reformatted by the pinned 23.1.3 binary (D-01)"
  - "ClangFormatConfigTests, the stdlib machine check for the config invariants (D-05)"
affects: [06-02, 06-03, 06-04, 06-05, phase-08-ci]

actuals:
  tokens: 32142
  tasks: 2
  commits: 2
  plan_head_before: 33463255b1092af38a87a47ddd96663b895840f1
  plan_head_after: 2d563201344bcced9d39b3ff52ea797915d3fa56

tech-stack:
  added: [clang-format 23.1.3 via mirrors-clang-format v23.1.3]
  patterns:
    - "Check-only hook: override the mirror's `-i` entry with `--dry-run --Werror`"
    - "`default_stages: [pre-commit]` so a second installed stage cannot inherit every hook"
    - "Text-only, stdlib unittest assertions with exact-once counts to defeat a later duplicate override"

key-files:
  created:
    - .clang-format
    - scripts/tests/test_tooling_config.py
  modified:
    - .pre-commit-config.yaml
    - lib/common/src/hex.c
    - 44 tracked C/C++ files under lib/, homeworks/1_3-police-flasher/, tests/, the two templates, and the two golden fixtures

key-decisions:
  - "The hook is check-only by overriding the mirror's entry; the tree-wide gate is `pre-commit run clang-format --all-files`."
  - "The whole tracked C/C++ set was reformatted in three build-checked groups (lib+tests, homework, templates+goldens) so a SortIncludes regression stays attributable."
  - "SortIncludes was proven reorder-only by comparing both the sorted include multiset and the blank-separated include-block partition against HEAD."

patterns-established:
  - "A formatter gate reports and never repairs: the entry is a dry-run form, proven by a byte comparison across a hook run."
  - "Template and golden C/C++ fixtures are formatted by the same pinned binary, keeping the golden equality test meaningful."

requirements-completed: [TOOL-01]

coverage:
  - id: D1
    description: "`.clang-format` carries D-02's keys, each exactly once, and no `.editorconfig` exists (D-03)"
    requirement: TOOL-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#ClangFormatConfigTests"
        status: pass
      - kind: other
        ref: "uvx --from clang-format==23.1.3 clang-format --dump-config (resolved-value gate)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The clang-format pre-commit hook is check-only, pinned at v23.1.3, scoped to C/C++, and runs only at pre-commit"
    requirement: TOOL-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#ClangFormatConfigTests"
        status: pass
      - kind: integration
        ref: "pre-commit run clang-format --files lib/common/src/hex.c && byte comparison before/after"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every tracked C/C++ file passes the pinned check"
    requirement: TOOL-01
    verification:
      - kind: integration
        ref: "pre-commit run clang-format --all-files (60 tracked files)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Templates and golden fixtures were reformatted together and remain byte-identical"
    requirement: TOOL-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_new_homework.py#GoldenTreeTests"
        status: pass
      - kind: other
        ref: "cmp template vs golden for both templates and both C/C++ files"
        status: pass
    human_judgment: false
  - id: D5
    description: "The reformat is behaviour-neutral: shared native suite, homework native suite, and the ESP32-S3 build stay green"
    requirement: TOOL-01
    verification:
      - kind: integration
        ref: "pio test -d tests -e native (73 cases)"
        status: pass
      - kind: integration
        ref: "pio test -d homeworks/1_3-police-flasher -e native (38 cases)"
        status: pass
      - kind: integration
        ref: "pio run -d homeworks/1_3-police-flasher (esp32s3_arduino SUCCESS)"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-10-26
status: complete
---

# Phase 6 Plan 01: C/C++ Format Contract and Tree-Wide Reformat Summary

**Committed a check-only clang-format 23.1.3 contract and reformatted all 60 tracked C/C++ files in one mechanical, build-verified pass**

## Performance

- **Duration:** 3 min
- **Started:** 2026-10-26T10:53:51Z
- **Completed:** 2026-10-26T10:56:59Z
- **Tasks:** 2
- **Files modified:** 48 (885 insertions, 593 deletions)

## Accomplishments

- `.clang-format` encodes D-02's documented ESP-IDF approximation and no `.editorconfig` exists (D-03).
- The `mirrors-clang-format` hook is pinned at `v23.1.3`, runs `clang-format --dry-run --Werror` on staged C/C++ files, and is explicitly stage-scoped with `default_stages: [pre-commit]`.
- All 60 tracked C/C++ files pass the pinned check; 44 changed, 16 already conformed.
- `SortIncludes: true` was proven reorder-only: the sorted `#include` multiset and the blank-separated include-block partition are unchanged in all 44 modified files.
- Templates and their golden fixtures were reformatted by the same binary and remain byte-identical, so `GoldenTreeTests` keeps its meaning.
- The shared native suite (73 cases), the homework native suite (38 cases), and the ESP32-S3 build all stay green.

## Task Commits

Each task was committed atomically:

1. **Task 1: Committed format contract and a check-only hook, proven on one file** - `9d78405` (feat)
2. **Task 2: Reformat every tracked C/C++ file in one mechanical pass** - `2d56320` (style)

**Plan metadata:** committed separately (docs: complete plan summary).

## Files Created/Modified

- `.clang-format` - the single C/C++ style source; D-02's key set.
- `.pre-commit-config.yaml` - `default_stages: [pre-commit]` plus the pinned check-only clang-format hook.
- `lib/common/src/hex.c` - reformatted as the tracer file.
- `scripts/tests/test_tooling_config.py` - `ClangFormatConfigTests`, six stdlib tests.
- 44 tracked C/C++ files under `lib/`, `homeworks/1_3-police-flasher/`, `tests/`, `templates/homework-{arduino,espidf}/`, and their golden fixtures - mechanical reformat.

## Decisions Made

- The hook's `entry` is overridden to the dry-run form because the mirror's default `-i` would repair the file instead of rejecting it (D-04).
- The reformat ran in three groups (lib+tests, homework, templates+goldens) with a build or test after each, so a `SortIncludes` breakage would be attributable rather than lost in a 60-file diff.
- Include changes were reviewed two ways: the sorted include multiset and the blank-separated block partition, both compared against `HEAD`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The `--dump-config` verify command assumed single-space separators**
- **Found during:** Task 1
- **Issue:** `clang-format --dump-config` aligns values with multiple spaces (`IndentWidth:     4`), so the plan's literal `grep -F "IndentWidth: 4"` either fails or, worse, matches an unrelated `...IndentWidth: 4` line. The plan's own verify text is a defect.
- **Fix:** Ran the same check with whitespace-tolerant anchors (`^IndentWidth: +4$`, `^ColumnLimit: +120$`, `^UseTab: +Never$`, `^ReflowComments: +Never$`, `^ +AfterFunction: +true$`); all five resolved values matched.
- **Files modified:** none (verification form only).
- **Verification:** the five anchored matches printed from `/tmp/cf-dump.txt`.
- **Committed in:** n/a (gate command).

**2. [Rule 3 - Blocking] The Task 1 acceptance check `git status --porcelain lib/common/src/hex.c` is empty cannot hold before the Task 1 commit**
- **Found during:** Task 1
- **Issue:** The task itself reformats `hex.c`, so the file is legitimately modified until the commit lands. The criterion intended to prove the hook did not rewrite the file.
- **Fix:** Proved non-rewrite with a byte comparison against a copy taken immediately before a second hook run; the comparison passed and the hook reported `Passed` both times.
- **Files modified:** none.
- **Verification:** `cmp` exit 0 across the hook run.
- **Committed in:** 9d78405.

---

**Total deviations:** 2 auto-fixed (both Rule 3, both verification-form defects; no production-code change)
**Impact on plan:** None on the shipped contract or the tree; both deviations tightened the evidence rather than widening scope.

## Issues Encountered

- The harness guard rejected `xargs` and command-substitution forms of the reformat command, so the pinned formatter was invoked with explicit relative file arguments in three groups. This is an execution-mechanics change; the tool, its version, and the file set are exactly as planned.
- `pre-commit run --all-files` and the full stdlib suite (`285 tests`) both pass on the committed tree.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The formatting layer is complete and machine-checked; plan 06-02 (and later `clang-tidy`, lint hooks) builds on this hook surface.
- `default_install_hook_types` intentionally stays `[pre-commit]` in this plan; the pre-push half belongs to the clang-tidy plan.
- No blockers.

---
*Phase: 06-developer-experience-and-quality-layering*
*Completed: 2026-10-26*

## Self-Check: PASSED

- `.clang-format`, `scripts/tests/test_tooling_config.py`, and this SUMMARY exist on disk.
- `9d78405` (Task 1) and `2d56320` (Task 2) are ancestors of `HEAD`.
- `pre-commit run --all-files`, `python3 -m unittest discover -s scripts/tests` (285 tests), both native suites, and the ESP32-S3 build all exited 0.
