---
phase: 09-agent-workflow-and-skills
plan: 09
subsystem: agent-workflow
tags: [skills, platformio, serial-capture, guardrails, generated-mirror]

requires: []
provides:
  - "monitor_speed = 115200 in the generated shared PlatformIO config for both ESP sections"
  - "one scoped, fail-closed capture exception in the shared guardrails"
  - "fail-closed baud resolution and a corrected capture snippet in hw-flash"
  - "regenerated skills mirror and manifest"
  - "CR-01, CR-02 and WR-01 recorded as fixed"
affects: [09-agent-workflow-and-skills]

actuals:
  tokens: 5092
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "A generated config value is declared in the authored template, then read fail-closed by the consumer"
    - "A policy exception has one owner in the shared guardrails and is referenced, never restated"

key-files:
  created: []
  modified:
    - templates/views/shared-ini.ini.tmpl
    - platformio.shared.ini
    - generated.manifest
    - scripts/tests/test_gen_views.py
    - .claude/skills/_shared/guardrails.md
    - .claude/skills/hw-flash/SKILL.md
    - .claude/skills/hw-flash/CHANGELOG.md
    - .claude/skills/hw-flash/LESSONS.md
    - .agents/skills/_shared/guardrails.md
    - .agents/skills/hw-flash/SKILL.md
    - .agents/skills/hw-flash/CHANGELOG.md
    - .agents/skills/hw-flash/LESSONS.md
    - generated.skills.manifest
    - .planning/phases/09-agent-workflow-and-skills/09-REVIEW-DISPOSITION.md

key-decisions:
  - "Declare monitor_speed = 115200 in the shared template, not a homework file, so every project inherits one source of truth"
  - "Resolve the baud from pio project config and stop when absent rather than accept PlatformIO's 9600 default"
  - "State one scoped capture exception in the shared guardrails and have hw-flash reference it"

patterns-established:
  - "Fail-closed config read: resolve the generated value, stop when absent, announce the effective value at the gate"
  - "Single-owner policy: shared guardrails own the exception; skills reference it"

requirements-completed: [FLOW-01, FLOW-02, FLOW-03, FLOW-04, FLOW-05, FLOW-06, FLOW-07]

coverage:
  - id: D1
    description: "The shared PlatformIO config declares monitor_speed = 115200 for both ESP sections and the real homework resolves it"
    requirement: FLOW-07
    verification:
      - kind: unit
        ref: "scripts/tests/test_gen_views.py#SharedIniTests.test_both_esp_sections_declare_the_monitor_baud"
        status: pass
      - kind: other
        ref: "pio project config -d homeworks/1_3-police-flasher --json-output resolves monitor_speed=115200"
        status: pass
    human_judgment: false
  - id: D2
    description: "The shared guardrails own one scoped, fail-closed capture exception and hw-flash references it"
    requirement: FLOW-07
    verification:
      - kind: other
        ref: "token assertion over .claude/skills/_shared/guardrails.md and hw-flash/SKILL.md"
        status: pass
    human_judgment: true
    rationale: "The token assertions prove the policy wording exists; a human must confirm the exception is correctly scoped and not restated."
  - id: D3
    description: "The capture snippet implements the -e rule, OSError, returncode, the credential scan and the atomic write"
    requirement: FLOW-07
    verification:
      - kind: other
        ref: "canonical/mirror body comparison plus required-token assertion"
        status: pass
    human_judgment: true
    rationale: "The snippet is prose-embedded and not executed by a test; a human must confirm the code and its surrounding bullets agree."
  - id: D4
    description: "Canonical tree and generated mirror are in sync and the three findings are recorded fixed"
    requirement: FLOW-01
    verification:
      - kind: other
        ref: "uv run scripts/gen_skills.py --check; disposition assertion over 09-REVIEW-DISPOSITION.md"
        status: pass
    human_judgment: false

plan_head_before: 8af175f0037ad2176231ece9e63ff7bc250de05b
plan_head_after: 91a6aa1f11c13ab615b8fc07c75f8b51188a4cad

duration: ~20min
completed: 2026-10-26
status: complete
---

# Phase 9 Plan 9: Gap Closure for hw-flash Capture Summary

**A declared and machine-checked 115200 baud, one scoped fail-closed capture exception, and a capture snippet that now implements every rule it states**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-10-26T22:45:00Z (approximate; exact start not captured)
- **Completed:** 2026-10-26T23:05:00Z
- **Tasks:** 3
- **Files modified:** 14

## Accomplishments

- Declared `monitor_speed = 115200` in `templates/views/shared-ini.ini.tmpl` for both ESP sections and regenerated `platformio.shared.ini` and `generated.manifest`; `pio project config -d homeworks/1_3-police-flasher --json-output` now resolves the real homework to 115200.
- Added a `SharedIniTests` regression test that pins the baud in both sections while leaving every existing assertion intact.
- Rewrote the `## Secrets` section of `_shared/guardrails.md` to own exactly one scoped, fail-closed capture exception, and made `hw-flash` reference it rather than restate it.
- Made `hw-flash` resolve the baud fail-closed before the gate, announce `Baud: <n>`, and stop when `monitor_speed` is absent.
- Corrected the capture snippet: `needs_e_flag` branch, `OSError` handling, pre-bound `returncode` check, credential-shape scan, and the announced `write_log_atomically` write.
- Regenerated the mirror and manifest; marked CR-01, CR-02 and WR-01 `fixed` with the other twelve still `open` (`open: 12`).

## Task Commits

Each task was committed atomically:

1. **Task 1: Declare the serial baud in the generated shared PlatformIO source and lock it with a test** - `322504e` (feat)
2. **Task 2: State one scoped capture exception and rewrite the hw-flash capture contract** - `b3b005d` (feat)
3. **Task 3: Regenerate the mirror, record the three dispositions, and run the phase gate** - `91a6aa1` (docs)

## Files Created/Modified

- `templates/views/shared-ini.ini.tmpl` - authored source of the shared config; both ESP sections now declare the baud
- `platformio.shared.ini` - regenerated projection carrying the baud
- `generated.manifest` - regenerated ledger for the shared ini
- `scripts/tests/test_gen_views.py` - new `test_both_esp_sections_declare_the_monitor_baud`
- `.claude/skills/_shared/guardrails.md` - one scoped capture exception
- `.claude/skills/hw-flash/SKILL.md` - baud resolution, gate announcement, corrected snippet
- `.claude/skills/hw-flash/CHANGELOG.md`, `LESSONS.md` - dated 2026-10-27 entries
- `.agents/skills/**` (four files), `generated.skills.manifest` - regenerated mirror and ledger
- `.planning/phases/09-agent-workflow-and-skills/09-REVIEW-DISPOSITION.md` - CR-01, CR-02, WR-01 fixed

## Decisions Made

- Declare the baud in the shared template rather than a homework file: the value is repository policy, every project inherits it, and a homework duplicate would be a second source of truth.
- Read the resolved value from `pio project config` and stop when absent: a read that falls through to PlatformIO's 9600 default is not a read.
- Keep the log persistence because D-20 locks the capture to an ignored path, and close the secrets conflict with one scoped, fail-closed exception rather than removing persistence.
- Keep `metadata.version: "0.1"` per D-16 and pass `-b <n>` only for a user-named value, never a hardcoded 115200.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Regenerated the skills mirror in Task 2 instead of Task 3**
- **Found during:** Task 2 commit
- **Issue:** The `gen-skills-check` pre-commit hook runs `gen_skills.py --check` and fails on canonical/mirror drift. Task 2 deliberately changed only `.claude/skills/**`, so the commit was blocked; `--no-verify` is forbidden.
- **Fix:** Ran `uv run scripts/gen_skills.py` before the Task 2 commit and included the four regenerated mirror files and `generated.skills.manifest` in it. Task 3 still re-ran the generator (every record `UNCHANGED`) and owns the disposition update.
- **Files modified:** `.agents/skills/_shared/guardrails.md`, `.agents/skills/hw-flash/{SKILL,CHANGELOG,LESSONS}.md`, `generated.skills.manifest`
- **Verification:** `gen_skills.py --check` exits 0 with every record `UNCHANGED`; the full pre-commit gate passes.
- **Committed in:** `b3b005d` (Task 2 commit)

**2. [Rule 1 - Bug] The plan's baud assertion compared an integer to a string**
- **Found during:** Task 1 verification
- **Issue:** `pio project config --json-output` emits `monitor_speed` as the integer `115200`, so the plan's `env.get("monitor_speed") == "115200"` assertion failed despite the resolved value being correct.
- **Fix:** Verified the same fact with `str(env.get("monitor_speed")) == "115200"`. No repository change; the production artifact is correct.
- **Files modified:** None
- **Verification:** Resolved value prints `115200`; the unit regression test and the full gate pass.
- **Committed in:** N/A (verification-command correction only)

---

**Total deviations:** 2 (1 blocking, 1 bug in the plan's own check)
**Impact on plan:** Both were necessary to keep the commit gate honest; neither changes the shipped behavior or scope.

## Issues Encountered

- The sandbox blocked `pre-commit`'s `end-of-file-fixer` from opening `.claude/skills/**` (`PermissionError`), matching the denial recorded in `09-VERIFICATION.md`; the commit and the full gate were re-run outside the sandbox as the plan directs. Not a repository defect.
- `uv run` needs `UV_CACHE_DIR` under the sandbox-writable temp directory; the suite was run with `UV_CACHE_DIR=/tmp/claude-501/uv-cache`.

## User Setup Required

None - no external service configuration required.

## Threat Flags

None - the changes add no network endpoint, auth path, or schema surface beyond the plan's threat model. The capture scan narrows the existing device-to-log boundary.

## Next Phase Readiness

- CR-01, CR-02 and WR-01 are closed; the twelve remaining review findings stay `open` by design and are not silently fixed or dropped.
- The full gate is green: `pre-commit run --all-files`, `check_metadata.py`, the Python suite (377 tests, `OK`), `gen_views.py --all --check`, and `gen_skills.py --check`.
- The out-of-scope findings (WR-02 through WR-08, IN-01 through IN-05) need their own triage before the phase can claim a clean review.

---

## Self-Check: PASSED

- Modified files exist on disk (all 14 verified by path).
- All three task commits (`322504e`, `b3b005d`, `91a6aa1`) are ancestors of HEAD.
- The plan-level verification commands all passed in this run.

---
*Phase: 09-agent-workflow-and-skills*
*Completed: 2026-10-26*
