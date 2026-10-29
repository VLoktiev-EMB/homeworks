---
phase: quick
plan: 261029-3bz
subsystem: homework/firmware
tags: [platformio, esp32-s3, arduino, contact-bounce, refactor]

requires:
  - plan: quick/261027-vxo
    provides: lean homework tree and the shared native suite
provides:
  - "homeworks/1_5-button-bounce with the 256-edge capture and burst analysis inlined in src/main.cpp"
  - "a target-only homework: no homework-private library, no host Unity suite, one esp32s3_arduino environment"
  - "README and report whose evidence claims match the target-only structure"
affects: [1_5-button-bounce, hw-build, hw-report]

actuals:
  tokens: 6263
  tasks: 3
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Inline fixed-capacity ISR capture under portENTER_CRITICAL_ISR, drained by a critical-section memcpy into a snapshot buffer"
    - "Burst summary computed from locals in the consumer, with no stats struct and no validity field"

key-files:
  created: []
  modified:
    - homeworks/1_5-button-bounce/src/main.cpp
    - homeworks/1_5-button-bounce/platformio.ini
    - homeworks/1_5-button-bounce/homework.yaml
    - homeworks/1_5-button-bounce/README.md
    - homeworks/1_5-button-bounce/report.md
  deleted:
    - homeworks/1_5-button-bounce/lib/bounce_logic/
    - homeworks/1_5-button-bounce/test/

key-decisions:
  - "The capture and analysis are owned by src/main.cpp; the homework ships no library and no host suite"
  - "BUTTON_PIN is 16, matching task.md, the README, the report, the diagram, and the schematic"
  - "The report keeps Implementation commit 66f966b because the serial protocol and behaviour are unchanged"

patterns-established:
  - "A homework with no pure logic keeps its native environment out of platformio.ini and declares tests.framework none"

requirements-completed: [QUICK-261029-3bz]

duration: 6min
started: 2026-10-29T00:22:00Z
completed: 2026-10-29T00:28:54Z
plan_head_before: 0e3c278bbac00478b57d6e2091bf7385dbec18ba
plan_head_after: e6f9ad101de4aae08afdb80268dd4d3220e8d91b
status: complete
---

# Quick 261029-3bz: Simplify homework 1_5-button-bounce Summary

**The 256-edge capture and burst analysis now live in `src/main.cpp`, the `bounce_logic` library and both host suites are gone, and the homework builds as a single `esp32s3_arduino` target.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-10-29T00:22:00Z
- **Completed:** 2026-10-29T00:28:54Z
- **Tasks:** 3
- **Files modified:** 10 (5 modified, 5 deleted)

## Accomplishments

- Inlined the ISR capture, the critical-section drain, the burst analysis, and the serial protocol into
  `homeworks/1_5-button-bounce/src/main.cpp`, which is 202 lines against the former 350 lines of
  `main.cpp` + `bounce_logic.h` + `bounce_logic.c`.
- Deleted `lib/bounce_logic/` and both Unity suites under `test/`, and removed the empty `lib/` directory.
- Removed `test_dir` and the whole `[env:native]` section from `platformio.ini`; the only environment left
  is `esp32s3_arduino`.
- Set `homework.yaml` to `tests.framework: none`, `tests.native: false`, `tests.coverage: false`.
- Rewrote the README and the report so no native-suite, host-suite, or removed-path claim survives, keeping
  the ten-section report contract, the ledger, and every `not measured` label honest.

## Task Commits

All three tasks landed in one atomic commit, as the plan requires:

1. **Task 1: Inline the capture and analysis, remove the native harness** — `e6f9ad1` (refactor)
2. **Task 2: Rewrite README for the target-only homework** — `e6f9ad1` (refactor)
3. **Task 3: Rewrite report test claims** — `e6f9ad1` (refactor)

## Files Created/Modified

- `homeworks/1_5-button-bounce/src/main.cpp` — target-only firmware: pin, `CHANGE` interrupt, 256-edge
  capture, burst analysis, serial protocol, online debounce.
- `homeworks/1_5-button-bounce/platformio.ini` — one environment, no `test_dir`.
- `homeworks/1_5-button-bounce/homework.yaml` — `tests` block now `none` / `false` / `false`.
- `homeworks/1_5-button-bounce/README.md` — build section, layout, status line for the target-only tree.
- `homeworks/1_5-button-bounce/report.md` — inline-capture wording, `Test coverage` paragraph, T-09 and T-11
  rows, implementation commit `66f966b` unchanged.
- Deleted: `lib/bounce_logic/include/bounce_logic.h`, `lib/bounce_logic/library.json`,
  `lib/bounce_logic/src/bounce_logic.c`, `test/test_bounce_logic/test_bounce_logic.c`,
  `test/test_homework/test_homework.c`.

## Decisions Made

- Followed the seven locked owner decisions in the plan without revisiting them.
- Moved `micros()` out of the critical section and ahead of it per the plan, so the timestamp is taken at
  interrupt entry and only the store is protected.
- Kept the BURST/E/TOTAL/READY format literals byte-for-byte identical to HEAD, verified by extracting and
  comparing all seven `Serial.printf`/`println` literals.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None. The target build, the shared native suite, the metadata checker, the Python suite, and the
pre-commit gate on the five changed files all exited 0.

## Verification

- `pio run -d homeworks/1_5-button-bounce` — SUCCESS (7.43 s).
- `pio test -d tests -e native` — 73/73 test cases passed.
- `uv run scripts/check_metadata.py` — PASS.
- `pre-commit run --files <five changed files>` — all hooks passed (exit 0).
- `python3 -m unittest discover scripts/tests` — 141 tests, OK (6 skipped).
- `git status --porcelain` — only `.vscode/settings.json` (unstaged, pre-existing) and the untracked
  `assets/wokwi.toml` / `.planning/quick/` remain; neither was staged.
- README and report keyword scans — no `bounce_logic`, `test/test_bounce_logic`, `test/test_homework`,
  `pio test`, `native`, or `10 of 10`.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The homework is ready for the owner's ten-press bench capture, which is the only remaining action before
  the report can leave `draft`.
- `assets/wokwi.toml` and `.vscode/settings.json` remain local and unstaged, as required.

---

## Self-Check: PASSED

- `homeworks/1_5-button-bounce/src/main.cpp` exists and contains `BUTTON_PIN = 16`.
- `homeworks/1_5-button-bounce/lib/bounce_logic` and `homeworks/1_5-button-bounce/test` are absent.
- Commit `e6f9ad1` is an ancestor of HEAD.
