---
phase: 09-agent-workflow-and-skills
plan: 18
subsystem: agent-workflow
tags: [skills, guardrails, markdown, generated-mirror, gap-closure, credential-scan]

requires:
  - phase: 09-agent-workflow-and-skills
    provides: "the widened credential scan admitting a space-separated compound keyword (09-17)"
provides:
  - "the shared guardrails as the single owner of the same-resolved-port rule"
  - "one locator sentence in hw-flash/SKILL.md and every operational port step kept"
  - "the guardrails' capture exception naming the compound shape and its one-separator bound"
  - "dated 2026-10-27 records labelled 09-17, 09-18 in the changelog and lessons"
  - "a regenerated .agents/skills mirror and generated.skills.manifest in sync"
affects: [hw-flash, serial-capture, 09-VERIFICATION]

actuals:
  tokens: 3616
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "One owner for normative policy: the shared guardrails state the rule, every skill points at it"
    - "The .agents/skills mirror and generated.skills.manifest are produced only by scripts/gen_skills.py"

key-files:
  created: []
  modified:
    - .claude/skills/_shared/guardrails.md
    - .claude/skills/hw-flash/SKILL.md
    - .claude/skills/hw-flash/CHANGELOG.md
    - .claude/skills/hw-flash/LESSONS.md
    - .agents/skills/_shared/guardrails.md
    - .agents/skills/hw-flash/SKILL.md
    - .agents/skills/hw-flash/CHANGELOG.md
    - .agents/skills/hw-flash/LESSONS.md
    - generated.skills.manifest

key-decisions:
  - "Replace the five normative restatements with one locator sentence in the port bullet, keeping every operational port step."
  - "Name the space-separated compound shape in the guardrails with the literal one-space/underscore/hyphen bound that 09-17 implements, so policy and scan agree."
  - "Regenerate the mirror with scripts/gen_skills.py inside each task commit, because the gen-skills-check hook requires the mirror in sync at every commit."

patterns-established:
  - "A normative rule lives in the shared guardrails; a skill keeps only operational steps plus one pointer."
  - "A generated projection is repaired by re-running its generator, never by editing the mirror."

requirements-completed: [FLOW-01, FLOW-02, FLOW-03, FLOW-04, FLOW-05, FLOW-06, FLOW-07]

coverage:
  - id: D1
    description: "The shared guardrails own the same-resolved-port rule once; hw-flash keeps every operational port step and one locator sentence."
    requirement: FLOW-07
    verification:
      - kind: other
        ref: "python3 assertion over .claude/skills/hw-flash/SKILL.md (five banned restatements absent, locator count 1)"
        status: pass
      - kind: other
        ref: "python3 assertion over .claude/skills/_shared/guardrails.md (same-port rule appears exactly once)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The guardrails' capture exception names `secret key = <value>` and `SECRET KEY: <value>` with the one-separator bound, and the mirror is regenerated in sync."
    requirement: FLOW-07
    verification:
      - kind: other
        ref: "python3 assertion over .claude/skills/_shared/guardrails.md and the four .agents mirror files"
        status: pass
      - kind: other
        ref: "UV_CACHE_DIR=/private/tmp/claude uv run scripts/gen_skills.py --check (every record UNCHANGED)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The phase gate is green: full Python suite, metadata, generated views, mirror check and pre-commit run --all-files."
    requirement: FLOW-07
    verification:
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

duration: ~5 min
completed: 2026-10-27
status: complete
plan_head_before: 65f61edd0c2afeca08751e2a465c8fc1cf9f4e7c
plan_head_after: de80fb9
commits: 2
---

# Phase 9 Plan 18: Shared Same-Resolved-Port Rule and Compound Credential Shape Summary

**The shared guardrails now own the same-resolved-port rule alone, `hw-flash` points at it once while keeping every operational port step, and the guardrails name the space-separated compound credential shape that the 09-17 scan admits.**

## Performance

- **Duration:** ~5 min
- **Started:** ~2026-10-27T12:38:00Z
- **Completed:** 2026-10-27T12:42:26Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments

- `.claude/skills/_shared/guardrails.md` now names the compound keyword written with one space, underscore or hyphen, with the literal samples `secret key = <value>` and `SECRET KEY: <value>`, matching the `[ _-]` class 09-17 implements.
- `.claude/skills/hw-flash/SKILL.md` lost all five normative restatements of the same-port rule and gained exactly one locator sentence naming `../_shared/guardrails.md`.
- Every operational port step survives: the `pio device list --json-output` listing, the `USB VID:PID=` hwid filter, the single-candidate choice, the zero-candidate stop, the `--port` question and the `/dev` validation.
- Dated `2026-10-27 — gap-closure run, 09-17, 09-18` entries sit at the top of both the changelog and the lessons file.
- The `.agents/skills` mirror and `generated.skills.manifest` were regenerated by `scripts/gen_skills.py` only; `--check` reports every record `UNCHANGED`.
- The phase gate is green: 441 tests OK, metadata PASS, generated views UNCHANGED, and all 14 pre-commit hooks passed.

## Task Commits

Each task was committed atomically:

1. **Task 1: Make the shared guardrails the single owner and trim the skill to operational steps** - `1bb3371` (docs)
2. **Task 2: Record the run, regenerate the mirror, and run the phase gate** - `de80fb9` (docs)

**Plan metadata:** the `docs(09-18)` SUMMARY commit (this file).

## Files Created/Modified

- `.claude/skills/_shared/guardrails.md` — the capture-exception clause naming the compound shape and its one-separator bound.
- `.claude/skills/hw-flash/SKILL.md` — one locator sentence replacing five normative restatements; operational port steps unchanged.
- `.claude/skills/hw-flash/CHANGELOG.md`, `.claude/skills/hw-flash/LESSONS.md` — dated `09-17, 09-18` run entries.
- `.agents/skills/_shared/guardrails.md`, `.agents/skills/hw-flash/SKILL.md`, `.agents/skills/hw-flash/CHANGELOG.md`, `.agents/skills/hw-flash/LESSONS.md`, `generated.skills.manifest` — regenerated projections only.

## Decisions Made

- One locator sentence for the whole skill, in the "Before the gate" port bullet, rather than per-section pointers.
- The guardrails name the literal one-space/underscore/hyphen bound instead of a general "compound keyword", so the policy cannot promise a shape the scan rejects.
- The mirror was regenerated in Task 1 as well as Task 2 because the `gen-skills-check` hook requires the committed mirror to match the canonical tree at every commit.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Regenerated the mirror inside the Task 1 commit**
- **Found during:** Task 1 commit
- **Issue:** The `gen-skills-check` pre-commit hook refused the Task 1 commit because the canonical edits left `.agents/skills/_shared/guardrails.md`, `.agents/skills/hw-flash/SKILL.md` and `generated.skills.manifest` out of sync. The plan assigns mirror regeneration to Task 2, so Task 1 could not be committed atomically without it.
- **Fix:** Ran `uv run scripts/gen_skills.py` after the Task 1 verification (the generator is the only writer) and included the regenerated projections in the Task 1 commit. Task 2 re-ran the generator for the changelog and lessons records.
- **Files modified:** `.agents/skills/_shared/guardrails.md`, `.agents/skills/hw-flash/SKILL.md`, `generated.skills.manifest`
- **Verification:** `gen_skills.py --check` exits 0 with every record `UNCHANGED`; the hook passes on both commits.
- **Committed in:** `1bb3371` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No behavioural or scope change; the mirror remains generator-produced and in sync at every commit.

## Issues Encountered

- **Sandbox write denial during commits (environment, retried outside):** `pre-commit`'s `end-of-file-fixer` failed with `PermissionError: Operation not permitted` on `.claude/skills/**` inside the command sandbox. Both task commits and `pre-commit run --all-files` were re-run outside the sandbox and passed all 14 hooks. Recorded as an environment refusal, not a defect.
- **Sandbox PTY refusal (environment, retried outside):** the full Python suite needs `pty.openpty()`, which the sandbox refuses with `out of pty devices`; it was run outside the sandbox and reported 441 tests, OK, 1 skipped.
- **`uv` cache outside the sandbox:** the default `~/.cache/uv` is not writable in the sandbox; the generator and checkers ran with `UV_CACHE_DIR=/private/tmp/claude`.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None.

## Threat Flags

None — the change implements the planned T-09-52, T-09-53 and T-09-54 mitigations and adds no new trust boundary. T-09-SC remains `accept`: no package was installed.

## Next Phase Readiness

- G-09-3 / truth 42 (WR-03) is closed: the same-port rule has one owner and `hw-flash` points at it.
- The guardrails sentence and the 09-17 scan now agree on the space-separated compound shape, closing the policy/implementation mismatch behind CR-01.
- WR-01 (`-d` resolved against the process cwd) and WR-02 (`pio project config` failure reported as port discovery with exit 1) remain deliberately open and untouched.
- Truth 38 (a real hardware capture) remains human-verified; no task here claims a device capture.
- The shared-ID requirement gate leaves the FLOW-completion writes to the orchestrator after the last declaring plan has a SUMMARY.

---

## Self-Check: PASSED

- `.claude/skills/_shared/guardrails.md` — FOUND
- `.claude/skills/hw-flash/SKILL.md` — FOUND
- `.claude/skills/hw-flash/CHANGELOG.md` — FOUND
- `.claude/skills/hw-flash/LESSONS.md` — FOUND
- `.agents/skills/hw-flash/SKILL.md` — FOUND
- `generated.skills.manifest` — FOUND
- commit `1bb3371` — FOUND (ancestor of HEAD)
- commit `de80fb9` — FOUND (ancestor of HEAD)

---
*Phase: 09-agent-workflow-and-skills*
*Completed: 2026-10-27*
