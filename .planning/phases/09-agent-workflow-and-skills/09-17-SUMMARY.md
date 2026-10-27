---
phase: 09-agent-workflow-and-skills
plan: 17
subsystem: security
tags: [python, regex, serial-capture, credential-scan, unittest, gap-closure]

requires:
  - phase: 09-agent-workflow-and-skills
    provides: "the serial capture helper with its fail-closed credential scan (09-14/09-15)"
provides:
  - "`find_credential` admits a compound keyword written with one space between its words"
  - "an end-to-end refusal test proving no log and no `.skill-state` directory are written"
  - "the compound shape pinned in `REVIEW_SHAPES` plus a named fixture tuple and test"
  - "a source comment that matches the implemented separator class"
affects: [09-18, hw-flash, serial-capture]

actuals:
  tokens: 1119
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Fail-closed credential scan: a match short-circuits before any filesystem write"
    - "Literal separator class `[ _-]` rather than a whitespace class, so a compound keyword cannot span a line break"

key-files:
  created: []
  modified:
    - scripts/serial_capture.py
    - scripts/tests/test_serial_capture.py

key-decisions:
  - "Widen the `secret` alternative to `secret(?:[ _-]?key)?`, mirroring the existing `api[ _-]?key` compound, and keep the connector and six-character floor untouched."
  - "Use a literal space/underscore/hyphen class, never a whitespace class, so a compound keyword cannot span a newline in a device log."
  - "Run PTY-dependent checks outside the command sandbox (`pty.openpty()` is refused with `out of pty devices`) and record the caveat rather than a failure."

patterns-established:
  - "A new positive shape gets its own named fixture tuple and named test rather than riding on `test_the_review_shapes_match`."
  - "A regex widening is proven end to end through `capture_and_store`, not only by a direct `find_credential` probe."

requirements-completed: [FLOW-01, FLOW-02, FLOW-03, FLOW-04, FLOW-05, FLOW-06, FLOW-07]

coverage:
  - id: D1
    description: "A capture whose child prints a space-separated compound credential line refuses with `capture unavailable`, writes no log and creates no `.skill-state` directory."
    requirement: FLOW-07
    verification:
      - kind: unit
        ref: "scripts/tests/test_serial_capture.py#CaptureAndStoreTests.test_a_space_separated_compound_credential_child_writes_nothing"
        status: pass
      - kind: other
        ref: "python3 -c direct `find_credential` probe over the CR-01 shapes and the pinned benign negative"
        status: pass
    human_judgment: false
  - id: D2
    description: "The compound shape is pinned in `REVIEW_SHAPES` and `SPACE_SEPARATED_COMPOUND_ASSIGNMENTS` with a named test, and the source comment documents the literal separator class."
    requirement: FLOW-07
    verification:
      - kind: unit
        ref: "scripts/tests/test_serial_capture.py#CredentialScanTests.test_space_separated_compound_assignments_match"
        status: pass
      - kind: other
        ref: "python3 -c fixture/comment assertion over test_serial_capture.py and serial_capture.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every previously pinned positive still matches and every pinned benign negative (`auth mode = WPA2`, `the cpwd tool reports ready`, `author wrote nothing here`, `secret is`, the benign boot log) still does not."
    requirement: FLOW-07
    verification:
      - kind: unit
        ref: "scripts/tests/test_serial_capture.py#CredentialScanTests (12 tests)"
        status: pass
      - kind: other
        ref: "python3 -c all-shapes probe over positives and benign samples"
        status: pass
    human_judgment: false

duration: ~12 min
completed: 2026-10-27
status: complete
plan_head_before: e4fdde13b8d5a0a794f1a9eafb52040977d7ee31
plan_head_after: 82474750e3c60fe747bddc82095cedc72ba76c8c
commits: 2
---

# Phase 9 Plan 17: Space-Separated Compound Credential Refusal Summary

**`find_credential` now refuses a space-separated compound credential line end to end, with the shape pinned by its own fixture tuple and a refused write leaving no log and no `.skill-state`.**

## Performance

- **Duration:** ~12 min (start time not captured in the agent context; approximate)
- **Started:** ~2026-10-27T12:21:00Z
- **Completed:** 2026-10-27T12:33:01Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- The `_KEYWORDS` `secret` alternative is now `secret(?:[ _-]?key)?`, so the CR-01 shape reaches the assignment branch's separator.
- A tracer test wires fixture bytes through `find_credential` into `capture_and_store` and proves a compound-keyword child is refused with no log and no state directory.
- `REVIEW_SHAPES` carries both CR-01 samples, and `SPACE_SEPARATED_COMPOUND_ASSIGNMENTS` pins the case and separator variants under `test_space_separated_compound_assignments_match`.
- The comment above `_KEYWORDS` names the space-separated compound shape, its literal separator class, and why it is not a whitespace class.
- Every pinned benign negative still returns False; the capture suite reports 64 tests, `OK`, no skips.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end: a space-separated compound credential child writes nothing** - `a6d9317` (fix)
2. **Task 2: Pin the compound shape across fixtures and document it in the source comment** - `8247475` (test)

**Plan metadata:** the `docs(09-17)` SUMMARY commit (this file).

## Files Created/Modified

- `scripts/serial_capture.py` — the `secret(?:[ _-]?key)?` alternative and the extended `_KEYWORDS` comment block; the assignment connector, six-character floor, `capture_and_store`, `write_log_atomically`, the CLI and the exit-code table are unchanged.
- `scripts/tests/test_serial_capture.py` — `test_a_space_separated_compound_credential_child_writes_nothing`, the two CR-01 samples appended to `REVIEW_SHAPES`, `SPACE_SEPARATED_COMPOUND_ASSIGNMENTS`, and `test_space_separated_compound_assignments_match`.

## Decisions Made

- Mirrored the existing `api[ _-]?key` compound instead of introducing a new scan branch: the change is one alternation and inherits the fail-closed path unchanged.
- Chose a literal `[ _-]` class over the review's suggested `[\s_-]`, because `\s` includes a newline and would let a compound keyword span a line break in a device log.
- Left the shared guardrails sentence for `09-18` (D-21: the shared file owns policy) and kept the source comment scoped to the shape the code implements.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Ruff E501 on the widened `_KEYWORDS` line**
- **Found during:** Task 1 commit (pre-commit `ruff check`)
- **Issue:** The single-line alternation reached 105 characters, above the repository's 100-character limit, so the task commit was blocked.
- **Fix:** Wrapped the constant in parentheses as two adjacent byte literals; semantics are byte-identical.
- **Files modified:** `scripts/serial_capture.py`
- **Verification:** `ruff check` passed on the retried commit; the full capture suite re-ran 63/63 green before committing.
- **Committed in:** `a6d9317` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Formatting only, no behavioural or scope change.

## Issues Encountered

- **Sandbox PTY refusal (expected, recorded not failed):** inside the command sandbox `pty.openpty()` fails with `out of pty devices`, which blocks the ten PTY-dependent tests. Every PTY-dependent command in this plan (`CaptureAndStoreTests`, the full capture suite) was run with the sandbox disabled; the pure-regex `CredentialScanTests` also passed inside the sandbox (12 tests).
- **Sandbox write denial during the gate (expected, retried outside):** `pre-commit run --all-files` inside the sandbox failed `end-of-file-fixer` with `PermissionError: Operation not permitted` on `.claude/skills/**`, because the sandbox denies writes there. Re-running the same command outside the sandbox passed all 14 hooks.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None.

## Threat Flags

None — the change implements the planned T-09-50 mitigation and adds no new trust boundary. T-09-SC remains `accept`: no package was installed.

## Next Phase Readiness

- G-09-2 / CR-01 is closed for the scan: the policy sentence in the shared guardrails and the shipped regex now agree on the space-separated compound shape.
- Truth 38 (a real hardware capture) remains human-verified and untouched; no task here claims a device capture.
- `09-18` owns the guardrails sentence; this plan deliberately did not edit `.claude/skills/_shared/guardrails.md`.
- FLOW-03 (adjacency/empty/ordering) and FLOW-04 (idempotency/concurrency) remain recorded as unresolved beyond the empty and adjacency substance this plan pins; the shared-ID requirement gate leaves the FLOW writes to the orchestrator after the last declaring plan (`09-18`) has a SUMMARY.

---

## Self-Check: PASSED

- `scripts/serial_capture.py` — FOUND
- `scripts/tests/test_serial_capture.py` — FOUND
- commit `a6d9317` — FOUND (ancestor of HEAD)
- commit `8247475` — FOUND (ancestor of HEAD)

---
*Phase: 09-agent-workflow-and-skills*
*Completed: 2026-10-27*
