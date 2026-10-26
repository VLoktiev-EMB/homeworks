---
phase: 06-developer-experience-and-quality-layering
plan: 06
subsystem: developer-experience
tags: [esp-clangd, clangd, vscode, pre-commit, regression-test, documentation]

# Dependency graph
requires:
  - phase: 06-developer-experience-and-quality-layering
    plan: 03
    provides: "scripts/clangd-wrapper.sh and the onboarding guide's headless check section"
  - phase: 06-developer-experience-and-quality-layering
    plan: 05
    provides: "the live phase verification report and validation table whose manual-test commands are corrected here"
provides:
  - "The working headless esp-clangd invocation --check=<file> in the guide and both live planning contracts"
  - "A three-case stdlib regression guard that fails on a detached source path and on a missing attached command"
affects: [07-simulation, 08-ci-and-quality-gates, re-verification of phase 06]

# Actuals (#2632) — chars/4 over the realized diff, same scale as the plan estimate.
actuals:
  tokens: 1100
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A documented command the tool rejects is guarded by a positive, negative, and non-vacuity test in the module that already owns the guide"

key-files:
  created: []
  modified:
    - docs/standards/vscode.md
    - .planning/phases/06-developer-experience-and-quality-layering/06-VERIFICATION.md
    - .planning/phases/06-developer-experience-and-quality-layering/06-VALIDATION.md
    - scripts/tests/test_tooling_config.py

key-decisions:
  - "esp-clangd 21.1.3 declares --check[=<string>], so every live copy of the command attaches the value with =; the wrapper forwards arguments verbatim and stays unchanged."
  - "Historical records stay byte-identical: the ADR body, the executed 06-02 plan and summary, and 06-UAT.md are not edited; only the live contracts move."
  - "The regression guard keeps the recorded defect line as a fixture constant so the detector is proven non-vacuous without reintroducing the defect into authored Markdown."

patterns-established:
  - "Command-documentation guard: assert the exact attached command, assert the detached pattern is absent, and assert the same pattern matches the recorded defect line."

requirements-completed: [TOOL-02, TOOL-04]

coverage:
  - id: D1
    description: "The onboarding guide and both live phase contracts document the working attached-value esp-clangd check command."
    requirement: TOOL-02
    verification:
      - kind: other
        ref: "scripts/clangd-wrapper.sh --check=homeworks/1_3-police-flasher/src/main.cpp -> exit 0, 'All checks completed, 0 errors'"
        status: pass
      - kind: unit
        ref: "python3 -c count assertion over docs/standards/vscode.md (1), 06-VERIFICATION.md (2), 06-VALIDATION.md (1)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A stdlib regression guard fails when the attached command is removed or a detached source path returns, and proves the detector matches the recorded defect."
    requirement: TOOL-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#ClangdCheckCommandTests"
        status: pass
    human_judgment: false

duration: 2min
completed: 2026-10-26
status: complete
---

# Phase 6 Plan 06: Attached esp-clangd Check Command Summary

**The guide and both phase manual-test contracts now document `--check=<file>` — the only form
esp-clangd 21.1.3 accepts — held by a three-case stdlib regression guard proven against the
recorded defect.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-10-26T12:16:30Z
- **Completed:** 2026-10-26T12:18:57Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Reproduced the root cause before editing: `--check=<path>` exits 0 with `All checks completed,
  0 errors`; the documented `--check <path>` exits 1 with clangd's unknown-argument diagnostic.
- Corrected every live occurrence — the guide (once), `06-VERIFICATION.md` (twice), and
  `06-VALIDATION.md` (once) — and added one sentence naming the declared `--check[=<string>]`
  syntax as the reason the value is attached.
- Added `ClangdCheckCommandTests` with positive, negative, and non-vacuity cases; the detached
  form, a removed `=`, and a deleted command each fail the class, and the recorded UAT line is
  matched by the same pattern.
- Kept all historical records byte-identical: blob hashes at the plan base and at HEAD match for
  the ADR body, `06-02-PLAN.md`, `06-02-SUMMARY.md`, `06-UAT.md`, and `scripts/clangd-wrapper.sh`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Prove the attached-value invocation, then correct every live copy of it** -
   `7f98992` (docs)
2. **Task 2: Add a non-vacuous regression guard to the guide's test module** - `a56554f` (test)

**Plan metadata:** committed separately after this summary.

## Files Created/Modified

- `docs/standards/vscode.md` - the headless check section now runs
  `"$HOME/.local/bin/clangd-wrapper" --check=homeworks/1_3-police-flasher/src/main.cpp` and
  states why the value is attached.
- `.planning/phases/06-developer-experience-and-quality-layering/06-VERIFICATION.md` - the
  `behavior_unverified_items` test line and Human Verification item 1 use the attached form;
  nothing else changed.
- `.planning/phases/06-developer-experience-and-quality-layering/06-VALIDATION.md` - the
  manual-only verification row uses the attached form; nothing else changed.
- `scripts/tests/test_tooling_config.py` - `ClangdCheckCommandTests` plus the
  `CHECK_COMMAND`, `DETACHED_CHECK_PATTERN`, and `RECORDED_DEFECT_LINE` module constants.

## Decisions Made

- The fix belongs in documentation, not in the wrapper: `scripts/clangd-wrapper.sh` forwards
  `"$@"` verbatim, so the invocation is the only variable and the wrapper stays untouched.
- The negative pattern requires whitespace after `--check` (so the attached form cannot match)
  and a negative lookahead for `-` (so `--check --version` is not a false positive).
- Only the live contracts move; the ADR body, the executed plan and summary, and the UAT record
  are the historical record of the defect and stay byte-identical.

## Deviations from Plan

None - plan executed exactly as written. The absent compilation database was regenerated with the
guide's documented command, which the plan names as the required precondition rather than a
deviation.

## Issues Encountered

- The homework compilation database was absent in this worktree; `pio run -d
  homeworks/1_3-police-flasher -t compiledb` regenerated it in 2.1 s (the file remains untracked).
- The full suite initially failed on `uv` cache writes denied by the execution sandbox. Re-run
  with a writable `UV_CACHE_DIR`: 356 tests, 0 failures, 0 errors.
- `pre-commit run --all-files` passed every hook except `end-of-file-fixer`, which opens
  `.vscode/settings.json` read-write and is denied by the sandbox (`Operation not permitted` on an
  untouched file). The same hooks over the touched files — clang-format (skipped, no C/C++),
  ruff, markdownlint, yamllint, gitleaks, hygiene, and the generated-view drift check — all pass.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- G-06-1 is closed: a re-verifier copying the command from the guide, the verification report, or
  the validation table now runs the form that exits 0.
- The guard runs in the existing stdlib suite; no new dependency or hook was added.
- Phase 7/8 are untouched; CI wiring of the quality layers remains Phase 8 scope.

## Self-Check: PASSED

- `docs/standards/vscode.md`, `scripts/tests/test_tooling_config.py`, `06-VERIFICATION.md`, and
  `06-VALIDATION.md` all exist.
- `7f98992` and `a56554f` are ancestors of HEAD.
- Attached invocation verified: exit 0 with `All checks completed, 0 errors`.
- Detached reproduction verified: exit 1.
- Full suite verified: 356 tests OK.

---
*Phase: 06-developer-experience-and-quality-layering*
*Completed: 2026-10-26*
