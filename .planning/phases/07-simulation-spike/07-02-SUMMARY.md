---
phase: 07-simulation-spike
plan: 02
subsystem: simulation-evidence
tags: [wokwi, wokwi-cli, platformio, esp32s3, simulation, adr, evidence-record]

# Dependency graph
requires:
  - phase: 07-simulation-spike (plan 01)
    provides: "the promoted scripts/pio/merge_firmware.py post action and the merged flash image wokwi.toml consumes"
provides:
  - "07-SPIKE-EVIDENCE.md: label vocabulary, token discipline, Wokwi and Velxio protocol blocks, free measurement ladder, three-run protocol-A table, quota ledger and the ADR-0014 handoff"
  - "Executed Wokwi evidence: exit 0 on 3/3 runs, cold 3.759 s, warm 6.753 s and 11.238 s, one `I pattern ready` per run, 45 s cumulative quota upper bound"
  - "The machine-readable `**Outcome:** scenario passed` line Plan 04 reads to flip the homework status"
affects: [07-simulation-spike (plan 04 ADR-0014), phase-08 CI cost basis, phase-11 report and README expansion]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 9411
  tasks: 3
  commits: 5
  plan_head_before: 5bd86c47c20537a9a6bd675ff764bcc9ec87087e
  plan_head_after: cef917f0b4e01963ce18f640774b20548dbb3dd1

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Owner-run measurement protocol: the token and the metered session stay outside the command sandbox; the agent only records"
    - "One label per value from a fixed vocabulary, with `calculated (upper bound)` for any number derived from `--timeout`"
    - "Observation, not statistic (D-04): serial reliability is an exact fraction such as 3/3, never a percentage"

key-files:
  created:
    - .planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md
  modified: []

key-decisions:
  - "Protocol A was executed in full: three bounded runs, each exit 0, one `I pattern ready` per run."
  - "Serial reliability is recorded as `3/3 runs observed the expected serial line` — an observation with an exact count."
  - "Simulated minutes is the `--timeout 15000` bound labelled `calculated (upper bound)` on every run, because the owner supplied no dashboard before/after figures."
  - "`scenario passed` is written only because exit 0 and the `pattern ready` line coincide in all three runs; execution alone would not have sufficed."
  - "The literal `<N>` placeholder in `--serial-log-file` is recorded as a deviation rather than papered over: run-specific serial logs are `absent`, and the serial lines are quoted from each stamped output."

patterns-established:
  - "Absent evidence is written as `absent — <reason>`, never inferred from a neighbouring value."
  - "Wall-clock seconds and simulated minutes are separate columns and are never substituted for one another."

requirements-completed: [SIM-02]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "Evidence record with the label vocabulary stated before data, the single permitted token sentence, both copy-ready protocol blocks, and the complete free measurement ladder."
    requirement: "SIM-02"
    verification:
      - kind: other
        ref: "python3 assertion over 07-SPIKE-EVIDENCE.md (labels, `--timeout 15000`, table columns, outcome values, no unpipefail-ed tee)"
        status: pass
      - kind: other
        ref: "wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json — exit 0, Found 1 info"
        status: pass
      - kind: other
        ref: "tracked-source scan: exactly one WOKWI_CLI_TOKEN assignment, value `dummy`; `git grep WOKWI_CLI_TOKEN -- .github` empty"
        status: pass
    human_judgment: false
  - id: D2
    description: "Three executed Wokwi runs recorded with wall clock, cold/warm interval, exit code, serial observation, simulated-minutes bound and quota ledger."
    requirement: "SIM-02"
    verification: []
    human_judgment: true
    rationale: "The session is token-gated and quota-metered and cannot run inside the command sandbox, so no automated backstop can re-run it. A reviewer must check the three pasted stamped captures against the table rows."
  - id: D3
    description: "ADR-0014 handoff carrying exactly one outcome token, the serial fraction, the blocker and the quota consumed."
    requirement: "SIM-02"
    verification:
      - kind: other
        ref: "python3 assertion: `scenario passed` present, `pending — set after the runs` absent"
        status: pass
    human_judgment: true
    rationale: "Plan 04 flips the homework status from this line; the consistency between the outcome token and the three exit codes is a reviewer judgment, not a test."

# Metrics
duration: 1h 16m
completed: 2026-10-26
status: complete
---

# Phase 7 Plan 2: Simulation Spike — Wokwi Evidence and Protocol A Summary

**Three executed Wokwi sessions of the police-flasher scenario, all exit 0 with one `pattern ready` serial line each, recorded in a labelled evidence file that hands ADR-0014 a `scenario passed` outcome.**

## Performance

- **Duration:** ~1h 16m elapsed (includes the owner-run pause while the sessions ran outside the command sandbox)
- **Started:** 2026-10-26T16:17:21+02:00
- **Completed:** 2026-10-26T17:33:19+02:00
- **Tasks:** 3
- **Files modified:** 1 (`.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`)

## Accomplishments

- Created `07-SPIKE-EVIDENCE.md` with the label vocabulary stated before any data, the single permitted token sentence, copy-ready Wokwi and Velxio protocol blocks, and the complete quota-free measurement ladder.
- Recorded protocol A end to end: run 1 (cold) 3.759 s, run 2 (warm) 6.753 s, run 3 (repeat, warm) 11.238 s; wall clocks 5.815 s, 8.559 s and 12.701 s; exit 0 on all three; exactly one `I pattern ready` line per run.
- Closed the `## Handoff to ADR-0014` section with `**Outcome:** scenario passed`, `3/3` observed serial lines, no blocker, and a `calculated (upper bound)` cumulative quota of 3 runs / 45 s.
- Kept the quota ledger cumulative and labelled on every row, and recorded the dashboard figures as not supplied rather than inferring a delta.

## Task Commits

Each task was committed atomically:

1. **Task 1: One measurement lands in the evidence record end to end** - `76c7785` (docs)
2. **Task 2: Run 1 — the cold Wokwi session** - `f5dbd38` (docs)
3. **Task 3: Runs 2 and 3 — warm and repeat, the serial count, and the handoff outcome** - `cef917f` (docs)

**Plan metadata:** the final `docs(07-02): complete evidence record and wokwi protocol A` commit carries this SUMMARY.

_Note: two orchestrator `chore: merge executor worktree` commits (`1524a77`, `d204673`) sit between the task commits; the measured `commits:` count of 5 includes them._

## Files Created/Modified

- `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md` - the raw measurement record: vocabulary, protocol blocks, free ladder, three-run table, quota ledger and the ADR-0014 handoff.

## Decisions Made

- Executed protocol A in full rather than falling back to protocol B, because each run's simulated-minutes bound (15 s) stayed far inside the free-plan budget.
- Recorded simulated minutes as `calculated (upper bound) 15 s` on all three runs: the owner supplied no dashboard before/after figures, so no observed consumption exists to record.
- Fixed the column-rule sentence to state the research definition exactly — `Simulator cold` is **process spawn → first serial byte** on the first invocation, and `Simulator warm` is the same interval on a subsequent invocation — and added `not requested` as the third legal `VCD` cell form.
- Added a warm-interval observation: both warm values exceed the cold one, which is expected under RESEARCH §Step 0 (`warm` means "subsequent invocation", not "faster"), and the variance is dominated by the pre-simulation connection phase rather than the simulated boot.

## Deviations from Plan

### Recording deviations

**1. [Rule 1 - Recording correctness] Serial-log path held the literal `<N>` placeholder**
- **Found during:** Task 3 (runs 2 and 3)
- **Issue:** The owner's invocation passed `--serial-log-file "$HOME/wokwi-run<N>.serial.log"` without substituting the run number, so both runs overwrote one 246-byte file instead of producing run-specific logs.
- **Fix:** Recorded each run-specific serial log as `absent — the invocation used the literal placeholder <N>, …`, quoted the serial lines verbatim from each stamped output, and explained the basis for `scenario passed` in the handoff. No run-specific file contents were invented.
- **Files modified:** `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`
- **Verification:** Each stamped output independently contains `I pattern ready` and `Expected text matched: "pattern ready"`.
- **Committed in:** `cef917f` (Task 3 commit)

**2. [Rule 1 - Recording correctness] Column rules did not match the research definition**
- **Found during:** Task 3 (warm-interval recording)
- **Issue:** The pre-existing rule said `Simulator cold` was "the first serial byte", omitting the process-spawn anchor the research defines, and did not allow a `not requested` VCD cell.
- **Fix:** Rewrote the rule to the RESEARCH §Step 0 wording and added the `not requested` form.
- **Files modified:** `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`
- **Committed in:** `cef917f` (Task 3 commit)

---

**Total deviations:** 2 recording-only fixes. No code changed and no scope was added.

## Issues Encountered

- **No dashboard figures for any run.** The owner did not supply the before/after usage figure for runs 1-3, so every simulated-minutes and quota entry is the `--timeout 15000` bound labelled `calculated (upper bound)`. The flagged assumption on dashboard granularity stays flagged for the ADR.
- **No VCD on any run.** Run 1 requested one and the CLI reported `Error exporting VCD: Error 6: No logic analyzer in diagram`; runs 2 and 3 did not request one. Both are recorded as absent, not inferred.
- **Sandbox tooling.** The command sandbox refused `git status` / `git diff` when invoked through the output-condensing wrapper; the same read-only queries ran through `/usr/bin/git` inside the worktree.

## User Setup Required

The plan carried a `user_setup` entry for `WOKWI_CLI_TOKEN`. The owner supplied it at a silent `read -rs` prompt in a terminal outside the command sandbox; the value was never received, echoed, written to a file, or committed. No further external configuration is required.

## Next Phase Readiness

- ADR-0014 (Plan 04) can read `**Outcome:** scenario passed` and the measured values: lint exit 0, build-cold median 8.13 s, build-warm median 0.49 s, simulator cold 3.759 s, warm 6.753 s / 11.238 s, session wall clock 5.815–12.701 s, serial 3/3, quota 45 s upper bound.
- Phase 8 can use the 15 s per-run timeout bound as the CI cost input, with the quota unit still flagged (simulated versus wall-clock).
- Open, explicitly labelled: the dashboard granularity, the quota unit, and VCD usefulness remain unmeasured; the free-plan terms stay flagged rather than assumed.

---

*Phase: 07-simulation-spike*
*Completed: 2026-10-26*

## Self-Check: PASSED
