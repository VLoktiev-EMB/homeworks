---
phase: 09-agent-workflow-and-skills
plan: 10
subsystem: skills-tooling
tags: [serial-capture, pseudo-terminal, credential-scan, atomic-write, skills-mirror, pre-commit]

# Dependency graph
requires:
  - phase: 09-agent-workflow-and-skills
    provides: 09-09 fail-closed baud resolution and the single scoped capture exception
provides:
  - "scripts/serial_capture.py: PTY capture, widened credential scan, root-anchored atomic write, CLI"
  - "scripts/tests/test_serial_capture.py: 26 hardware-free tests over a fake serial source"
  - "hw-flash contract pointed at the helper; piped monitor snippet removed"
  - "shared guardrails again forbid a credential in any log outside the scoped exception"
  - "AGENTS.md names every Phase 9 no-build-impact path, including the helper"
  - "regenerated .agents/skills/ mirror and generated.skills.manifest"
  - "09-REVIEW-DISPOSITION.md: eleven fixed findings and the new WR-09"
affects: [phase-09-verification, gsd-verify-work, skill-promotion]

# Actuals (#2632) — chars/4 over the realized diff, same scale as the plan estimate.
actuals:
  tokens: 16530
  tasks: 3
  commits: 3
plan_head_before: bc804ab84e917b32bf2866ec659fc621075ce712
plan_head_after: 2a67afd32ac60a4d8fbda18a87f613a9ffbe90d4

tech-stack:
  added: []
  patterns:
    - "PTY capture: pty.openpty + tty.setraw + select on a monotonic deadline"
    - "Fail-closed credential scan on exact bytes before any file exists"
    - "Atomic write through O_DIRECTORY | O_NOFOLLOW descriptors with dir_fd"
    - "Generated mirror repaired only by its generator, never hand-edited"

key-files:
  created:
    - scripts/serial_capture.py
    - scripts/tests/test_serial_capture.py
  modified:
    - scripts/affected.py
    - scripts/tests/test_affected.py
    - .claude/skills/hw-flash/SKILL.md
    - .claude/skills/hw-flash/CHANGELOG.md
    - .claude/skills/hw-flash/LESSONS.md
    - .claude/skills/_shared/guardrails.md
    - AGENTS.md
    - .agents/skills/hw-flash/SKILL.md
    - .agents/skills/hw-flash/CHANGELOG.md
    - .agents/skills/hw-flash/LESSONS.md
    - .agents/skills/_shared/guardrails.md
    - generated.skills.manifest
    - .planning/phases/09-agent-workflow-and-skills/09-REVIEW-DISPOSITION.md

key-decisions:
  - "A helper script replaces the prose snippet: a snippet cannot be executed by the suite, and the verifier requires a deterministic check."
  - "The PTY wraps pio device monitor rather than reading the serial port directly, so PlatformIO keeps port selection and monitor_speed inheritance."
  - "The space-separated scan alternative has a six-character floor: it catches password abc123 while accepting occasional false positives, which are safe because a match writes nothing."
  - "The log write uses directory descriptors and dir_fd rather than a path-based lstat loop, so a component swapped for a symlink is refused rather than followed."
  - "metadata.version stays 0.1 per D-16; the changelog records the behaviour change without a bump."

patterns-established:
  - "A TTY-gated tool is tested by proving the same child fails when its stdio is a pipe."
  - "A credential scan is tested against the exact shapes the review executed, including quoted and space-separated forms."
  - "A shipped projection is changed only by regenerating it and committing the generator output."

requirements-completed: [FLOW-01, FLOW-02, FLOW-03, FLOW-04, FLOW-05, FLOW-06, FLOW-07]

coverage:
  - id: D1
    description: "PTY capture that returns the exact bytes the child wrote and refuses an early exit, a missing command, or the deadline without a TTY"
    requirement: FLOW-03
    verification:
      - kind: unit
        ref: "scripts/tests/test_serial_capture.py#CapturePtyTests.test_capture_preserves_every_byte_and_sees_a_tty"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_serial_capture.py#CapturePtyTests.test_a_pipe_capture_would_fail_the_same_child"
        status: pass
    human_judgment: false
  - id: D2
    description: "Fail-closed credential scan over the six review shapes plus passwd, uppercase PASSWORD, and the space-separated form"
    requirement: FLOW-07
    verification:
      - kind: unit
        ref: "scripts/tests/test_serial_capture.py#CredentialScanTests"
        status: pass
    human_judgment: false
  - id: D3
    description: "Root-anchored atomic log write that refuses a symlinked component, replaces rather than appends, and leaves one whole payload under concurrency"
    requirement: FLOW-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_serial_capture.py#AtomicLogWriteTests"
        status: pass
    human_judgment: false
  - id: D4
    description: "hw-flash and the shared guardrails contract: helper invocation, --raw --quiet, int(str(value)), conditional -e, no piped snippet, any-log prohibition"
    requirement: FLOW-07
    verification:
      - kind: other
        ref: "python3 -c assertion over .claude/skills/hw-flash/SKILL.md, .claude/skills/_shared/guardrails.md and AGENTS.md"
        status: pass
    human_judgment: false
  - id: D5
    description: "Regenerated mirror and manifest in sync with the canonical tree, and the review disposition recording eleven fixed findings"
    requirement: FLOW-01
    verification:
      - kind: other
        ref: "uv run scripts/gen_skills.py --check"
        status: pass
      - kind: other
        ref: "python3 -c assertion over 09-REVIEW-DISPOSITION.md"
        status: pass
    human_judgment: false
  - id: D6
    description: "Full local gate: pre-commit surface, metadata contract, Python suite, generated views, skills mirror"
    requirement: FLOW-06
    verification:
      - kind: integration
        ref: "pre-commit run --all-files"
        status: pass
      - kind: integration
        ref: "python3 -m unittest discover scripts/tests"
        status: pass
    human_judgment: false

duration: 4min
completed: 2026-10-27
status: complete
---

# Phase 09 Plan 10: PTY Serial Capture and Review Disposition Summary

**A tested pseudo-terminal capture helper with a widened fail-closed credential scan and an atomic no-follow log write, plus a corrected `hw-flash` contract and a reconciled review ledger**

## Performance

- **Duration:** 4 min
- **Started:** 2026-10-26T23:26:36Z
- **Completed:** 2026-10-26T23:30:51Z
- **Tasks:** 3
- **Files modified:** 15 (2 created, 13 modified)
- **Commits:** 3

## Accomplishments

- Closed CR-01: `scripts/serial_capture.py` captures `pio device monitor --raw --quiet` through a
  pseudo-terminal in raw mode, so the monitor no longer refuses a non-TTY stdout. The suite proves
  exact `bytes(range(256))` preservation and proves the same child exits non-zero under a pipe.
- Closed CR-02: the credential scan matches `secret = hunter2`, `PASSWORD = hunter2`, JSON `token`
  and `apiKey` assignments, `password abc123`, and `Authorization: Bearer …`, while a benign boot
  log and `secret is` do not match. A match writes nothing and reports `capture unavailable`.
- Closed WR-01/WR-02/WR-06: the log is written under the resolved root through
  `O_DIRECTORY | O_NOFOLLOW` descriptors and `dir_fd`, with an exclusive temporary file and
  `os.replace`; a symlink at any component is refused, and `--quiet` keeps the banner out.
- Closed WR-03/WR-04/IN-01/IN-02: the outcome table calls the designed bound a success, the
  consent example announces the conditional `-e` segment, the unrunnable snippet is gone, and
  `monitor_speed` is normalized with `int(str(value))`.
- Closed WR-05: the shared guardrails' general prohibition again covers the state file and any
  log outside the one scoped capture exception, and names the fail-closed scan shapes.
- Closed WR-09: `AGENTS.md` now names every Phase 9 no-build-impact path, including the helper.
- Regenerated the `.agents/skills/` mirror and `generated.skills.manifest`; every record is
  `UNCHANGED` under `gen_skills.py --check`, and `scripts/serial_capture.py` maps to no build.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build and test the capture path** — `338e678` (feat)
2. **Task 2: Rewrite the hw-flash contract and regenerate the mirror** — `9a626a7` (docs)
3. **Task 3: Record the dispositions and run the phase gate** — `2a67afd` (docs)

## Files Created/Modified

- `scripts/serial_capture.py` — PTY capture, credential scan, root-anchored atomic write, CLI
- `scripts/tests/test_serial_capture.py` — 26 hardware-free tests across five test classes
- `scripts/affected.py` — `scripts/serial_capture.py` added to `NO_BUILD_IMPACT`
- `scripts/tests/test_affected.py` — the same path in `NoBuildImpactTests.NO_BUILD_IMPACT_PATHS`
- `.claude/skills/hw-flash/SKILL.md` — helper invocation, corrected bound/path/outcome prose
- `.claude/skills/hw-flash/CHANGELOG.md`, `LESSONS.md` — dated 2026-10-27 entries
- `.claude/skills/_shared/guardrails.md` — restored any-log prohibition and scan shapes
- `AGENTS.md` — the no-build-impact paragraph names every Phase 9 path
- `.agents/skills/**`, `generated.skills.manifest` — regenerated projections
- `.planning/phases/09-agent-workflow-and-skills/09-REVIEW-DISPOSITION.md` — eleven fixed rows and WR-09

## Decisions Made

- A helper script, not a longer snippet: the verifier requires a deterministic check, and prose
  cannot be executed by the suite.
- The PTY wraps `pio device monitor` instead of reading the device directly, so PlatformIO keeps
  port selection and `monitor_speed` inheritance.
- The space-separated scan branch has a six-character floor. It catches the review's
  `password abc123` and accepts occasional false positives, which are safe because a match writes
  nothing.
- `metadata.version` stays `"0.1"` per D-16; the behaviour change is recorded in the changelog.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Test compared a resolved path with the unresolved temp root**
- **Found during:** Task 1 (capture and write tests)
- **Issue:** `write_log_atomically` resolves the root by design, while `/tmp/claude-501` is a
  symlink to `/private/tmp/claude-501`; the equality assertion and the credential/empty-log paths
  compared the two spellings.
- **Fix:** Resolve the temporary root in each test's `setUp`, matching the helper's documented
  contract.
- **Files modified:** `scripts/tests/test_serial_capture.py`
- **Verification:** the full 26-test capture suite passes outside the sandbox
- **Committed in:** `338e678` (Task 1 commit)

**2. [Rule 3 - Blocking] Ruff UP022 rejected the piped-child invocation**
- **Found during:** Task 1 (first commit attempt; the pre-commit `ruff-check` hook failed)
- **Issue:** `subprocess.run(..., stdout=PIPE, stderr=PIPE)` is reported by UP022.
- **Fix:** Used `capture_output=True`; the child's stdout is still a pipe, so the test still
  proves a pipe is not a terminal.
- **Files modified:** `scripts/tests/test_serial_capture.py`
- **Verification:** `ruff check` passes and the test still asserts a non-zero exit
- **Committed in:** `338e678` (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking)
**Impact on plan:** Both are local test corrections; no scope creep and no change to the shipped
helper's behaviour.

## Issues Encountered

- **Environment: PTY denied in the sandbox.** `pty.openpty()` raises `out of pty devices` inside
  the command sandbox, as the plan anticipated. `python3 -m unittest scripts.tests.test_serial_capture`
  and the full discover suite were re-run outside the sandbox: 26/26 capture tests pass and the
  full suite is `OK (skipped=1)`.
- **Environment: `end-of-file-fixer` denied on `.claude/skills`.** The pre-commit commit for Task 2
  failed inside the sandbox with `PermissionError: Operation not permitted`; the commit was
  re-run outside the sandbox and all hooks passed. The final `pre-commit run --all-files` also ran
  outside the sandbox: every hook passed and no file was modified.
- **Pre-existing skip.** The full suite reports one skip, `ClangdGuideCommandTests` because
  `homeworks/1_3-police-flasher/compile_commands.json` is absent. It is unrelated to this plan.
- **No hardware.** The capture leg was exercised against fake `sys.executable -c` serial sources;
  no board was flashed. The plan's deliverables are the helper, its tests and the contract.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- GAP 1 and GAP 2 are closed and covered by deterministic tests; the mirror, manifest and views are
  in sync and the full gate is green.
- The phase verifier can re-run `python3 -m unittest scripts.tests.test_serial_capture` (outside the
  sandbox on this host) and `uv run scripts/gen_skills.py --check` as the evidence for FLOW-03,
  FLOW-04 and FLOW-07.
- `WR-07`, `WR-08`, `IN-03`, `IN-04` and `IN-05` remain open by design; they are out of this
  gap-closure scope.

## Self-Check: PASSED

- `scripts/serial_capture.py` — FOUND
- `scripts/tests/test_serial_capture.py` — FOUND
- `.planning/phases/09-agent-workflow-and-skills/09-REVIEW-DISPOSITION.md` — FOUND
- `338e678` — FOUND (ancestor of HEAD)
- `9a626a7` — FOUND (ancestor of HEAD)
- `2a67afd` — FOUND (ancestor of HEAD)

---
*Phase: 09-agent-workflow-and-skills*
*Completed: 2026-10-27*
