---
phase: 09-agent-workflow-and-skills
plan: 19
subsystem: agent-workflow
tags: [skills, guardrails, serial-capture, credential-scan, generated-mirror, gap-closure]

requires:
  - phase: 09-agent-workflow-and-skills
    provides: "the regenerated mirror and the compound credential shape (09-17, 09-18)"
provides:
  - "hw-flash/SKILL.md with no ambiguous-port restatement, every operational port step, and one corrected locator"
  - "the serial_capture module docstring naming the compound keyword family and the policy owner"
  - "the connector ceiling pinned at 128/129 by test_the_connector_ceiling_is_128_characters"
  - "dated 2026-10-27 records labelled 09-19 in the changelog and lessons"
  - "six 09-19 rows in the phase verification map and a green phase gate"
affects: [hw-flash, serial-capture, 09-VALIDATION, 09-VERIFICATION]

actuals:
  tokens: 3693
  tasks: 4
  commits: 4

tech-stack:
  added: []
  patterns:
    - "One owner for normative policy: the shared guardrails state the rule, the skill keeps only operational steps and one accurate locator"
    - "A generated projection is repaired only by re-running scripts/gen_skills.py"

key-files:
  created: []
  modified:
    - .claude/skills/hw-flash/SKILL.md
    - .claude/skills/hw-flash/CHANGELOG.md
    - .claude/skills/hw-flash/LESSONS.md
    - .agents/skills/hw-flash/SKILL.md
    - .agents/skills/hw-flash/CHANGELOG.md
    - .agents/skills/hw-flash/LESSONS.md
    - generated.skills.manifest
    - scripts/serial_capture.py
    - scripts/tests/test_serial_capture.py
    - .planning/phases/09-agent-workflow-and-skills/09-VALIDATION.md

key-decisions:
  - "Option A: remove both normative ambiguity sentences and keep the operational --port prompt, because the prompt states no rule and gives no rationale."
  - "The locator now says 'the steps here only apply it' instead of claiming a non-restatement, so the claim is true."
  - "The compound-family sentence names only the separator forms secret(?:[ _-]?key)? already admits, with the guardrails as policy owner."
  - "The ceiling test is renamed rather than supplemented, because the old name asserted every suffix over 32 matches and the 129 case falsifies it."
  - "The mirror was regenerated in Task 1 as well as Task 4, because the gen-skills-check hook requires the committed mirror in sync at every commit."

patterns-established:
  - "A locator may claim a non-restatement only when the same paragraph carries no normative variant."
  - "An enumerated family contract names every separator form the implementation admits and pins the boundary at the boundary."

requirements-completed: [FLOW-01, FLOW-07]

coverage:
  - id: D1
    description: "hw-flash/SKILL.md carries no ambiguity restatement, keeps every operational port step, and its one locator no longer claims `it is not restated here`."
    requirement: FLOW-01
    verification:
      - kind: other
        ref: "python3 text assertion over .claude/skills/hw-flash/SKILL.md (ten banned tokens absent; locator count 1; all operational tokens present)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The shared guardrails still own the same-resolved-port rule and the ambiguous-candidate rule exactly once."
    requirement: FLOW-01
    verification:
      - kind: other
        ref: "python3 text assertion over .claude/skills/_shared/guardrails.md (each rule count 1)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The serial_capture module docstring names the compound keyword family and the shared guardrails as policy owner, and the scan agrees with it."
    requirement: FLOW-07
    verification:
      - kind: other
        ref: "python3 docstring assertion over scripts/serial_capture.py plus the direct find_credential probe"
        status: pass
    human_judgment: false
  - id: D4
    description: "The connector ceiling is pinned at 128 matching and 129 refused, with every prior positive and benign negative unchanged."
    requirement: FLOW-07
    verification:
      - kind: unit
        ref: "scripts.tests.test_serial_capture.CredentialScanTests (12 tests, OK)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The regenerated mirror matches the canonical tree and the phase gate is green: full suite, metadata, generated views and pre-commit."
    requirement: FLOW-01
    verification:
      - kind: other
        ref: "uv run scripts/gen_skills.py --check (every record UNCHANGED)"
        status: pass
      - kind: unit
        ref: "python3 -m unittest discover scripts/tests (441 tests, OK, 1 skipped)"
        status: pass
      - kind: other
        ref: "uv run scripts/check_metadata.py (PASS)"
        status: pass
      - kind: other
        ref: "uv run scripts/gen_views.py --all --check (all UNCHANGED)"
        status: pass
      - kind: integration
        ref: "pre-commit run --all-files (14 hooks passed)"
        status: pass
    human_judgment: false

duration: ~2 min
completed: 2026-10-27
status: complete
plan_head_before: c4de88b0e33ba9aee11a22b477c25dd87f788a38
plan_head_after: be44ebf58c7146f5f02a4a1473d09ea3bd66b08c
commits: 4
---

# Phase 9 Plan 19: Residual Ambiguous-Port Restatements, Compound Keyword Contract and Connector Ceiling Summary

**`hw-flash` now carries only operational port steps and one truthful locator, the serial-capture docstring names the compound keyword family, and the 128-character connector ceiling is pinned at its boundary.**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-10-27T13:05:52Z
- **Completed:** 2026-10-27T13:07:57Z
- **Tasks:** 4
- **Files modified:** 10

## Accomplishments

- Removed both remaining normative ambiguity restatements from `.claude/skills/hw-flash/SKILL.md` and replaced them with the operational prompt `When more than one candidate remains, announce every path and ask the user for `--port`.`
- Corrected the single locator to `Port handling follows the shared flashing rule in ../_shared/guardrails.md; the steps here only apply it.`, so it no longer denies a restatement.
- Deleted the closing two-cable paragraph from "The two serial paths" while keeping the `Re-enumeration:` paragraph.
- Every operational port step survives: `pio device list --json-output`, the `USB VID:PID=` hwid filter, the single-candidate choice, the zero-candidate stop, the `--port` prompt and the absolute `/dev` validation.
- `scripts/serial_capture.py` now documents that a compound keyword may use one space, underscore, hyphen or no separator, and names the shared guardrails as policy owner.
- `test_the_connector_ceiling_is_128_characters` pins 128 matching and 129 refused, with all prior fixtures unchanged.
- Dated `2026-10-27 — gap-closure run, 09-19` records sit at the top of the changelog and lessons; six `09-19` rows were appended to the verification map.
- The `.agents/skills` mirror and `generated.skills.manifest` were regenerated by `scripts/gen_skills.py` only; `--check` reports every record `UNCHANGED`.
- The phase gate is green: 441 tests OK (1 skipped), metadata PASS, generated views UNCHANGED, and all 14 pre-commit hooks passed.

## Task Commits

Each task was committed atomically:

1. **Task 1: Remove the residual ambiguous-port restatements and correct the locator** - `27eee01` (docs)
2. **Task 2: Document the compound keyword family in the module contract** - `ae5df7d` (docs)
3. **Task 3: Pin the 128-character connector ceiling** - `5794a2e` (test)
4. **Task 4: Record the run, regenerate the mirror, append validation rows and run the phase gate** - `be44ebf` (docs)

**Plan metadata:** the `docs(09-19)` SUMMARY commit (this file).

## Files Created/Modified

- `.claude/skills/hw-flash/SKILL.md` — the operational port bullet, one corrected locator, and the two-cable paragraph removed.
- `.claude/skills/hw-flash/CHANGELOG.md`, `.claude/skills/hw-flash/LESSONS.md` — dated `09-19` run entries.
- `.agents/skills/hw-flash/SKILL.md`, `.agents/skills/hw-flash/CHANGELOG.md`, `.agents/skills/hw-flash/LESSONS.md`, `generated.skills.manifest` — regenerated projections only.
- `scripts/serial_capture.py` — the compound-family docstring sentence and policy-owner pointer.
- `scripts/tests/test_serial_capture.py` — the renamed 128/129 ceiling test.
- `.planning/phases/09-agent-workflow-and-skills/09-VALIDATION.md` — six appended `09-19` rows, marked `⬜ pending`.

## Decisions Made

- Option A was selected in Task 1: remove both normative sentences and keep the operational `--port` prompt.
- The locator was rewritten to make no non-restatement claim rather than merely rewording the old one.
- The ceiling test was renamed, not supplemented, because the old name asserted every suffix over 32 matches.
- The mirror was regenerated in Task 1 as well as Task 4 to keep the `gen-skills-check` hook green at every commit.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- **Sandbox PTY refusal (environment, rerun outside):** the full Python suite needs `pty.openpty()`, which the command sandbox refuses with `out of pty devices`; it was rerun outside the sandbox and reported 441 tests, OK, 1 skipped.
- **Sandbox `uv` cache denial (environment, rerun outside):** inside the sandbox, `uv` could not create its default `~/.cache/uv` temporary file and the suite's generator-setup modules errored; the rerun outside the sandbox passed.
- **Sandbox write denial during commit (environment, rerun outside):** `pre-commit`'s `end-of-file-fixer` failed with `PermissionError: Operation not permitted` on `.claude/skills/**` inside the sandbox. All four task commits and `pre-commit run --all-files` were rerun outside the sandbox and passed all 14 hooks.
- **`uv` cache path:** the generator and checkers ran with `UV_CACHE_DIR=/tmp/claude-501/uv-cache`, because the default cache is not writable in the sandbox.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None.

## Threat Flags

None — the change implements the planned T-09-55, T-09-56 and T-09-57 mitigations and adds no new trust boundary. T-09-SC remains `accept`: no package was installed.

## Next Phase Readiness

- G-09-3 / truth 42 (WR-03, WR-13) is closed: no ambiguity restatement remains in `hw-flash`, and the locator claims nothing false.
- WR-14 is closed: the docstring names the no-separator shape and the policy owner.
- IN-11 is closed: the connector ceiling is pinned at 128/129.
- WR-01, WR-02, truth 38, IN-12 and IN-13 remain deliberately open and untouched.
- Requirement completion (`FLOW-01`, `FLOW-07`) is left to the orchestrator, because both IDs are declared by sibling plans in this phase and the shared-ID gate must see every SUMMARY first.

---

## Self-Check: PASSED

- `.claude/skills/hw-flash/SKILL.md` — FOUND
- `.claude/skills/hw-flash/CHANGELOG.md` — FOUND
- `.claude/skills/hw-flash/LESSONS.md` — FOUND
- `.agents/skills/hw-flash/SKILL.md` — FOUND
- `.agents/skills/hw-flash/CHANGELOG.md` — FOUND
- `.agents/skills/hw-flash/LESSONS.md` — FOUND
- `generated.skills.manifest` — FOUND
- `scripts/serial_capture.py` — FOUND
- `scripts/tests/test_serial_capture.py` — FOUND
- `.planning/phases/09-agent-workflow-and-skills/09-VALIDATION.md` — FOUND
- commit `27eee01` — FOUND (ancestor of HEAD)
- commit `ae5df7d` — FOUND (ancestor of HEAD)
- commit `5794a2e` — FOUND (ancestor of HEAD)
- commit `be44ebf` — FOUND (ancestor of HEAD)

---
*Phase: 09-agent-workflow-and-skills*
*Completed: 2026-10-27*
