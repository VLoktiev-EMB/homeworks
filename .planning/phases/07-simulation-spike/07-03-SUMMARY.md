---
phase: 07-simulation-spike
plan: 03
subsystem: simulation-evidence
tags: [velxio, docker, self-host, esp32s3, stm32, simulation, agpl, evidence-record]

# Dependency graph
requires:
  - phase: 07-simulation-spike (plan 02)
    provides: "07-SPIKE-EVIDENCE.md with the label vocabulary, the Velxio protocol block and the Wokwi quota ledger"
provides:
  - "07-SPIKE-EVIDENCE.md §Velxio self-host attempt: RepoDigests digest, separate docker-run/first-200 timings, the 47-board simulator catalogue capture, the 182-FQBN compile backend list as a distinct row, the vendor datasheet row, and the AGPL boundary"
  - "A role-proportional second measurement that consumed no Wokwi quota"
  - "Observed ESP32-S3 and STM32 support in the self-hosted simulator catalogue, against the plan's earlier expectation"
affects: [07-simulation-spike (plan 04 ADR-0014), phase-08 CI cost basis, phase-11 report and README expansion]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 4859
  tasks: 2
  commits: 1
  plan_head_before: a4cd846cb55b664d4ae79ed94e400f158396be41
  plan_head_after: 6d2a4ce78277f794de7d89f4a079d139b700769c

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Observed UI catalogue and compile backend FQBN list are distinct surfaces; neither substitutes for the other"
    - "An owner-supplied capture outranks a planner assumption: record the observation and note the contradiction"
    - "An absent measurement is written as `not measured — <exact reason>`, never inferred from a neighbouring value"

key-files:
  created:
    - .planning/phases/07-simulation-spike/07-03-SUMMARY.md
  modified:
    - .planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md

key-decisions:
  - "The recorded image identity is the immutable RepoDigests digest `@sha256:5d673722…`, never the mutable `:master` tag."
  - "`docker run` wall time (0.335 s) and the first HTTP 200 (16.988 s) are separate measured values; boot readiness is the 16.988 s interval."
  - "The 47-board simulator catalogue (owner screenshot) is the primary board observation; the 182-FQBN arduino-cli compile list is a separate observed row, not the catalogue."
  - "ESP32-S3 and STM32 are recorded as present because the screenshot shows them, contradicting the plan's prior expectation of their absence."
  - "Pilot compile and serial are `not measured` because the editor consumes sketches, not a PlatformIO project; board support is not the blocker."
  - "No Wokwi quota was consumed by this attempt."

patterns-established:
  - "A vendor page count and the live UI count are different evidence classes; both are recorded, neither is merged."
  - "Toolchain presence in the image is recorded as a toolchain observation, not as a board entry."

requirements-completed: [SIM-02]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "Velxio self-host section carries a RepoDigests digest, separate docker-run and first-HTTP-200 timings, container name and the five named volumes, and the cleanup record."
    requirement: "SIM-02"
    verification:
      - kind: other
        ref: "python3 assertion over 07-SPIKE-EVIDENCE.md (digest, observed/vendor rows, STM32 mention, AGPL, Wokwi quota, capture, datasheet label)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Board coverage keeps the 47-board simulator catalogue (owner screenshot `$HOME/velxio-boards.png` plus the page URL) separate from the 182-FQBN compile backend list and from the vendor 19-board datasheet row."
    requirement: "SIM-02"
    verification: []
    human_judgment: true
    rationale: "The screenshot lives outside the repository at $HOME/velxio-boards.png and cannot be read by an automated check; whether each row is honestly labelled is a reviewer judgment, not a test."
  - id: D3
    description: "Pilot compile and serial are recorded as `not measured` with the PlatformIO-format reason, and no sketch port was manufactured."
    requirement: "SIM-02"
    verification:
      - kind: other
        ref: "python3 assertion over 07-SPIKE-EVIDENCE.md (`not measured — the self-hosted editor does not consume a PlatformIO project`)"
        status: pass
    human_judgment: true
    rationale: "The absence of a genuine UI pilot run is a reviewer judgment; the assertion can only confirm the reason text is present."

# Metrics
duration: ~15 min (continuation session; the owner-run protocol interval was not captured)
completed: 2026-10-26
status: complete
---

# Phase 7 Plan 3: Simulation Spike — Velxio Self-Host Attempt Summary

**The Velxio image was pinned by digest and booted in 16.988 s, its 47-board simulator catalogue captured by an owner screenshot showing ESP32-S3 and STM32 present, with the 182-FQBN compile list kept as a separate surface and the pilot compile/serial honestly `not measured`.**

## Performance

- **Duration:** ~15 min in this continuation session; the owner-run protocol interval before the Task 1 checkpoint was not captured by this agent
- **Started:** not captured (continuation agent resumed at the Task 1 checkpoint)
- **Completed:** 2026-10-26T17:46:51+02:00
- **Tasks:** 2
- **Files modified:** 1 (`07-SPIKE-EVIDENCE.md`); 1 created (this SUMMARY)

## Accomplishments

- Recorded the immutable image identity `ghcr.io/davidmonterocrespo24/velxio@sha256:5d673722f66cf2c5c8cef1fe4a04421a7d88fd863a7a266f8661ff269b3b3bc5`, with `:master` kept as the pull reference only.
- Recorded boot as two separate measured values: `docker run` wall time 0.335 s and first HTTP 200 at attempt 9 of 60, 16.988 s after the run start; boot readiness is the 16.988 s interval.
- Captured the simulator catalogue from the owner's live screenshot (`$HOME/velxio-boards.png`, 587620 bytes) and the page URL `http://localhost:3080`: 47 boards including ESP32-S3 DevKit, XIAO ESP32-S3, Arduino Nano ESP32, ESP32-C3 boards, STM32 Blue Pill, STM32 Black Pill and RP2040/Pico boards.
- Kept the `/api/compile/boards` output (182 FQBNs = 27 `arduino:avr` + 155 `rp2040:rp2040`) as its own observed row and explained it as the arduino-cli compile backend's core list, not the simulator catalogue.
- Recorded the vendor `19 boards` root-page claim as a `datasheet` row, corroborating ESP32-S3 and never merged with the observations.
- Recorded pilot compile and serial as `not measured` — the editor consumes sketches, not a PlatformIO project — and stated that the ESP32-S3 board is available, so board support is not the blocker.
- Stated the AGPLv3 reference-only boundary, the role of the five named volumes, the cleanup record, and that no Wokwi quota was consumed.

## Task Commits

Each task was committed atomically:

1. **Task 1 + Task 2: Velxio boot record and honest capability depth** - `6d2a4ce` (docs)
2. **Plan metadata: this SUMMARY** - committed separately as `docs(07-03): complete velxio capability record`

Task 1 reached its `checkpoint:human-action`; the repository owner disabled the command sandbox and the orchestrator executed the Velxio protocol in the owner's environment. The evidence section records that provenance plainly, distinguishing the owner's screenshot from the agent-executed protocol output.

## Files Created/Modified

- `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md` — added `## Velxio self-host attempt` (130 lines): provenance, digest, run configuration, separate boot timings, three board-coverage rows, toolchain observation, pilot depth, licence boundary, volumes rationale, cleanup and quota statement.
- `.planning/phases/07-simulation-spike/07-03-SUMMARY.md` — this record.

## Decisions Made

- Treated the owner screenshot as the authoritative board observation and recorded ESP32-S3 and STM32 as present, even though the plan's assumptions expected both to be unavailable. Observation wins over expectation; the contradiction is written down rather than hidden.
- Kept three board rows strictly separate: the simulator catalogue (observed), the arduino-cli compile backend list (observed, different surface), and the vendor page count (`datasheet`).
- Reported boot readiness as the first-HTTP-200 interval and explicitly refused to subtract the `docker run` wall time from it.
- Left pilot compile and serial unmeasured rather than porting the homework to a sketch.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Recording correctness] Plan assumptions about ESP32-S3 and STM32 contradicted by the owner's screenshot**
- **Found during:** Task 2 (recording the observed board row)
- **Issue:** The plan's `must_haves` and Task 2 acceptance criteria expected STM32 to be absent and the board coverage to come from the compile API text. The owner supplied a live UI screenshot showing a 47-board simulator catalogue with ESP32-S3 and STM32 boards present.
- **Fix:** Rewrote the observed row around the screenshot, demoted the 182-FQBN list to a separately labelled compile-backend row, restated the vendor row as a corroborating `datasheet` row, and replaced the "STM32 absence" paragraph with an explicit presence-and-contradiction record. The plan's automated assertion still passes unchanged.
- **Files modified:** `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`
- **Verification:** Task 2 assertion `TASK 2 VERIFY: PASS`; no occurrence of "absent" applied to ESP32-S3 or STM32 remains in the section.
- **Committed in:** `6d2a4ce` (Task 1+2 commit)

---

**Total deviations:** 1 recording-correctness correction, applied before the commit. No code changed and no scope was added.

## Issues Encountered

- **Sandbox tooling.** The command sandbox refused `git status`, `git log`, `git add` and similar commands when invoked through the output-condensing `rtk` wrapper, reporting that it could not prove the operation stayed inside the worktree. The same commands ran through `/usr/bin/git` inside the worktree, which is the pattern Plan 02 also recorded.
- **Two timings, one definition.** The `time` output (0.335 s) and the first-200 poll (16.988 s) could easily be conflated; the record states twice that the difference is not the boot interval.
- **Board-list ambiguity.** The compile API and the simulator catalogue report different things (182 FQBNs versus 47 boards). The record names both surfaces and explains why ESP32 compilation goes through the ESP-IDF/arduino-esp32 toolchains rather than the FQBN list.

## User Setup Required

The plan carried a `user_setup` entry for `velxio-self-host`. The owner disabled the command sandbox and confirmed Docker/ghcr.io reachability; the orchestrator then ran the protocol in the owner's environment. The container was removed after capture and the five named volumes persist intentionally. No further external configuration is required.

## Next Phase Readiness

- ADR-0014 (Plan 04) can cite this section for Velxio: digest-pinned identity, 16.988 s boot readiness, a 47-board simulator catalogue with ESP32-S3 and STM32 present, pilot compile/serial `not measured` because of PlatformIO project format, and zero Wokwi quota consumed.
- The ADR must not upgrade the vendor `19 boards` row or the 182-FQBN compile list into a pilot compile; the roles stay distinct.
- Open, explicitly labelled: pilot compile and serial in Velxio remain unmeasured; whether the editor can ingest anything PlatformIO-shaped was not tested.

---

*Phase: 07-simulation-spike*
*Completed: 2026-10-26*

## Self-Check: PASSED
