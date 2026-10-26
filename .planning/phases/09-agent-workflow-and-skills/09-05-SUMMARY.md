---
phase: 09-agent-workflow-and-skills
plan: 05
subsystem: tooling
tags: [agent-skills, hw-flash, consent-gate, serial-capture, generated-mirror]

# Dependency graph
requires:
  - phase: 09-agent-workflow-and-skills
    plan: 01
    provides: scripts/gen_skills.py, the generated.skills.manifest ledger and the gen-skills-check hook
  - phase: 09-agent-workflow-and-skills
    plan: 02
    provides: .claude/skills/_shared/guardrails.md, the shared flashing rules the gate restates
  - phase: 09-agent-workflow-and-skills
    plan: 04
    provides: the hw-build contract the failed-upload path hands back to
  - phase: 04.2-tracer-homework-1-3
    provides: the esp32-s3-devkitc-1 homework fixture and its one default_envs environment
provides:
  - .claude/skills/hw-flash/SKILL.md, the consent gate, upload leg and bounded capture contract
  - the hw-flash CHANGELOG.md and LESSONS.md records
  - their generated .agents/skills mirror and the updated generated.skills.manifest ledger
affects: [09-08-dry-run, phase-10-report-format]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 4932
  tasks: 2
  commits: 2

plan_head_before: bb791d8f01eba652ad3d7e83315df715d5d87fc4
plan_head_after: 25e01c9b7d976da35fff334c141ac7d23efaeebd

tech-stack:
  added: []
  patterns:
    - a consent gate that prints the target and the exact command before asking and accepts only a literal affirmative
    - a bounded raw serial capture that inherits monitor_speed instead of hardcoding a baud
    - four named outcome states where a capture failure never becomes a flash failure

key-files:
  created:
    - .claude/skills/hw-flash/SKILL.md
    - .claude/skills/hw-flash/CHANGELOG.md
    - .claude/skills/hw-flash/LESSONS.md
    - .agents/skills/hw-flash/SKILL.md
    - .agents/skills/hw-flash/CHANGELOG.md
    - .agents/skills/hw-flash/LESSONS.md
  modified:
    - generated.skills.manifest

key-decisions:
  - "Tasks 1 and 2 were committed separately: Task 1 created SKILL.md, so scripts/gen_skills.py could mirror it and the gen-skills-check hook passed; Task 2 added the companions and regenerated the same mirror again."
  - "allowed-tools is omitted from the frontmatter entirely rather than declared without upload, so no client can read a pre-approval the gate cannot see."
  - "Reaching the 20-second bound is written as the designed end of a capture; the capture fails only when the monitor cannot start, exits non-zero before the bound, or the log write is refused."

patterns-established:
  - "A hardware skill names the board, the environment and the exact command before asking, and treats every answer but the literal affirmative as a stop."
  - "A capture that cannot succeed reports capture unavailable while the upload exit code stays the flash result."
  - "A log write reuses the state-file path discipline: component lstat, symlink refusal, parent creation after the check, atomic replace."

requirements-completed: [FLOW-07]

coverage:
  - id: D1
    description: "SKILL.md carries the consent gate (board, environment, exact command, the capture it covers), the literal так/yes rule, the upload leg reporting the real exit code, and the bounded --raw capture with monitor_speed inheritance and the state-file path discipline"
    requirement: FLOW-07
    verification:
      - kind: integration
        ref: "test -s .claude/skills/hw-flash/SKILL.md"
        status: pass
      - kind: integration
        ref: "pre-commit run markdownlint-cli2 --files .claude/skills/hw-flash/SKILL.md"
        status: pass
    human_judgment: true
    rationale: "D-18 makes the gate and capture behaviour review-enforced; the 09-08 dry-run transcript that stops at the gate is the behavioural evidence."
  - id: D2
    description: "The canonical directory and its generated mirror carry SKILL.md and both dated companion records; the ledger lists all three and the drift check is clean"
    requirement: FLOW-07
    verification:
      - kind: integration
        ref: "uv run scripts/gen_skills.py --check"
        status: pass
      - kind: integration
        ref: "pre-commit run gen-skills-check --all-files"
        status: pass
      - kind: integration
        ref: "python3 -m unittest discover scripts/tests"
        status: pass
    human_judgment: false

duration: 14 min
completed: 2026-10-26
status: complete
---

# Phase 9 Plan 05: hw-flash Consent Gate and Bounded Capture Summary

**An explicit hardware gate that prints the board, environment and exact upload command, accepts only a literal `так` or `yes`, then uploads and writes a bounded raw serial log to an ignored path without interpreting it.**

## Performance

- **Duration:** 14 min
- **Started:** 2026-10-26T21:26:00Z
- **Completed:** 2026-10-26T21:40:34Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- The gate prints the board id from `homework.yaml`, the environment from `default_envs`
  (with an explicit `-e` when it is absent or plural), the exact command
  `pio run -d homeworks/<id> -t upload`, and the fact that the same confirmation covers a
  roughly 20-second serial capture written to `.skill-state/logs/<id>.log`.
- Only the exact `так` or `yes`, case-insensitive and with no other text, proceeds. An
  empty answer, a refusal, a question or a conditional is a stop; a refusal ends the
  action and needs a new invocation; the confirmation is never remembered, and `upload`
  is never declared in `allowed-tools`.
- The upload leg runs exactly `pio run -d homeworks/<id> -t upload`, reports the real
  command and exit code, and on a non-zero exit stops with no repair and no second
  upload, naming `/hw-build` as the separate repair path.
- The capture runs `pio device monitor -d homeworks/<id> --raw` bounded with a stdlib
  `subprocess` timeout of 20 seconds, inherits `monitor_speed` instead of hardcoding
  `-b 115200`, and accepts `-b <n>` only from an explicitly named, positive-integer user
  value.
- The log write reuses the state-file discipline: `lstat` every path component, refuse a
  symlink at any component, create `.skill-state/logs/` only after that check, and move a
  temporary file into place with `os.replace`.
- The body names exactly four outcome states (consent refused; upload failed; upload and
  capture succeeded; upload succeeded with `capture unavailable`), and a capture failure
  never turns the upload exit code into a failed flash.
- The log is never interpreted: no success claim, no measurement, no measurement-ledger
  row and no log content quoted into a report or commit; a token is never echoed, and a
  simulation is never described as a flash.
- The canonical files and their generated mirror carry the same three files, and
  `uv run scripts/gen_skills.py --check` is clean.

## Task Commits

Each task's work was committed atomically:

1. **Task 1: the consent gate, upload leg and bounded capture** - `99764a6` (feat)
2. **Task 2: the companion records and the regenerated mirror** - `25e01c9` (docs)

**Plan metadata:** this SUMMARY commit (docs: complete plan)

## Files Created/Modified

- `.claude/skills/hw-flash/SKILL.md` - the gates, upload and bounded capture contract
- `.claude/skills/hw-flash/CHANGELOG.md` - the dated 0.1 delivery record
- `.claude/skills/hw-flash/LESSONS.md` - the no-interpretation v0.1 lesson
- `.agents/skills/hw-flash/{SKILL,CHANGELOG,LESSONS}.md` - the generated mirror
- `generated.skills.manifest` - the updated mirror ledger with three new entries

## Decisions Made

- Task 1's commit carries the regenerated mirror because the `gen-skills-check` hook runs
  the generator over the whole tree; leaving the mirror out would leave the committed
  ledger drifting. Task 2 regenerates the same mirror for the two companions, so both
  commits are drift-clean.
- `allowed-tools` is omitted rather than declared without `upload`: an absent field cannot
  be mistaken for a pre-approval, and the body states the rule explicitly.
- The 20-second bound is the designed end of a capture, because the monitor otherwise runs
  forever. A capture is reported unavailable only when the monitor cannot start, exits
  non-zero before the bound, or the bytes cannot be written, so a healthy bounded capture
  is not mislabelled a timeout.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The worktree's rtk guard refuses bare `git`, compound git invocations and
  runtime-expanded environment variables, so every git call ran as a plain `/usr/bin/git`
  command and `uv` ran without a computed `UV_CACHE_DIR`. No hook was bypassed.
- `pio device monitor --help` was read only to confirm that `-d`, `-e` and `--raw` exist;
  no upload or monitor process was started, because this plan authors documentation only
  and flashing is forbidden.

## Known Stubs

None - `hw-flash` is minimally real per D-20: it uploads and captures, and the deferred
piece is log parsing, which the skill explicitly declines rather than fakes. The four
stubs in this phase are owned by plan 09-02.

## Threat Flags

None - the surfaces this plan adds (the gated upload, the serial log path, the id in the
commands and the reported capture outcome) are the ones the plan's threat register
already covers as T-09-21, T-09-22, T-09-23, T-09-24 and T-09-29. No package install and
no new network endpoint were introduced.

## User Setup Required

None - no external service configuration required. A connected board and serial port are
needed only for a real invocation, and the 09-08 dry run stops at the gate.

## Next Phase Readiness

- The 09-08 dry run can invoke `/hw-flash 1_3-police-flasher`, observe the full gate text,
  decline, and prove that no upload command ran.
- `git check-ignore -v .skill-state/logs/1_3-police-flasher.log` names the `.gitignore:83`
  rule, so the capture path is ignored as designed.
- `uv run scripts/gen_skills.py --check` and `pre-commit run gen-skills-check --all-files`
  exit 0, `git ls-files '.claude/skills/*/SKILL.md'` lists seven skills, and
  `python3 -m unittest discover scripts/tests` reports 375 tests with 1 skip.
- No blockers.

## Self-Check: PASSED

- `99764a6` and `25e01c9` are ancestors of HEAD; all three canonical files and all three
  mirror files exist and are non-empty; the ledger lists three `hw-flash` entries; the
  mirror carries the explicit-only banner; the drift check and the tooling suite are green.
