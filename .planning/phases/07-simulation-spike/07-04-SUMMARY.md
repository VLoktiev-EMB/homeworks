---
phase: 07-simulation-spike
plan: 04
subsystem: simulation-decision
tags: [adr, wokwi, velxio, renode, fritzing, simulation, generated-views, metadata]

# Dependency graph
requires:
  - phase: 07-simulation-spike (plan 02)
    provides: "07-SPIKE-EVIDENCE.md with the labelled Wokwi protocol-A values and the `**Outcome:** scenario passed` handoff"
  - phase: 07-simulation-spike (plan 03)
    provides: "the Velxio self-host record: digest, boot readiness, board coverage and the pilot `not measured` rows"
provides:
  - "docs/decisions/0014-simulator-selection.md: the platform-role matrix, evidence-supported costs, fidelity limits, calculated CI cost basis and the SIM-03 licence boundary"
  - "A one-row decision-table index entry for ADR-0014 and the regenerated MkDocs nav"
  - "homeworks/1_3-police-flasher: `simulation.status: verified`, reconciled §7/L-08/T-15/§9/Decision Appendix prose and the README pointer"
  - "The regenerated docs/homeworks/1_3-police-flasher.md rendering `wokwi (verified)` and the refreshed generated.manifest"
affects: [phase-08 CI simulation gate and cost basis, phase-10 report contract and checker, phase-11 pilot finalization]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 7488
  tasks: 2
  commits: 2
  plan_head_before: aa3ab02d5357529921a69757a554387bd2f6bb4e
  plan_head_after: 475abb3f5391749a1da3ab06a42ae377966c2f1d

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "The status flip is gated on the evidence outcome token, never on the mere existence of a run row"
    - "An ADR cites the evidence file as a code span when the evidence lives outside the docs tree, because a relative link would not resolve on the site"
    - "A calculated cost basis carries every input's label and propagates `calculated (upper bound)` into the result"

key-files:
  created:
    - docs/decisions/0014-simulator-selection.md
  modified:
    - docs/decisions/README.md
    - homeworks/1_3-police-flasher/homework.yaml
    - homeworks/1_3-police-flasher/report.md
    - homeworks/1_3-police-flasher/README.md
    - docs/homeworks/1_3-police-flasher.md
    - mkdocs.yml
    - generated.manifest

key-decisions:
  - "Branch A applies: `**Outcome:** scenario passed` with 3/3 observed serial lines, so `simulation.status` becomes `verified` and no other `simulation` key changes."
  - "The ADR promotes a platform-role matrix to the primary artefact while the five-label value vocabulary stays unchanged; a simulator value remains `simulated`."
  - "Serial reliability is carried as the exact observation `3/3`, never a percentage."
  - "The CI cost basis is labelled `calculated` with `PRs_per_month = 20` and sensitivity at 5 and 50; no CI run is claimed."
  - "Velxio pilot compile and serial stay `not measured — the self-hosted editor does not consume a PlatformIO project`."
  - "Renode carries a reasoned `not measured` row (unconfirmed course model, no STM32 homework or board profile, not installed); the record never states that Renode lacks STM32 support."

patterns-established:
  - "Generated views change only through `uv run scripts/gen_views.py --all`; `--check` gates the result and the manifest is refreshed in the same change."
  - "A stale-prose sweep is a whole-file forbidden-phrase list, not a single-sentence patch, so a contradiction cannot ship beside a passing grep."

requirements-completed: [SIM-02, SIM-03]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "ADR-0014 is on the generated site with the eight MADR sections, one title heading, the platform-role matrix, and a single decision-table row linking it."
    requirement: "SIM-02"
    verification:
      - kind: other
        ref: "UV_CACHE_DIR=\"$TMPDIR/uvcache\" uv run scripts/gen_views.py --all --check — exit 0, every record UNCHANGED"
        status: pass
      - kind: unit
        ref: "scripts.tests.test_docs_pins.PinConsistencyTests.test_nav_lists_every_markdown_file_under_docs — ok"
        status: pass
      - kind: other
        ref: "python3 assertion over docs/decisions/0014-simulator-selection.md (MADR sections, Chosen option, calculated, not measured, 3/3, Fritzing, AGPL, evidence path, PRs_per_month, forbidden Renode claim)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The ADR records each quantity in the form its evidence supports: exact serial fraction, Velxio pilot `not measured`, Renode/STM32 reasoned row, calculated CI basis, and no category implied as measured that the evidence does not measure."
    requirement: "SIM-02"
    verification: []
    human_judgment: true
    rationale: "No test can decide whether a prose sentence overclaims; the labels and their reasons were checked against 07-SPIKE-EVIDENCE.md by review."
  - id: D3
    description: "`simulation.status` is `verified` on the `scenario passed` handoff and the generated homework page renders `wokwi (verified)`, with the schema untouched."
    requirement: "SIM-02"
    verification:
      - kind: other
        ref: "branch-aware outcome assertion over 07-SPIKE-EVIDENCE.md, homework.yaml, report.md, README.md and docs/homeworks/1_3-police-flasher.md — PASS outcome=scenario passed"
        status: pass
      - kind: other
        ref: "UV_CACHE_DIR=\"$TMPDIR/uvcache\" uv run scripts/check_metadata.py — PASS"
        status: pass
      - kind: other
        ref: "schema assertion at $defs.simulation.properties: enum [none, pending, verified], no evidence key, additionalProperties false; git diff empty"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every stale simulation claim in report.md and the homework README is reconciled, the shared `../../scripts/pio/merge_firmware.py` is named, and T-15's status cell matches the outcome."
    requirement: "SIM-02"
    verification:
      - kind: other
        ref: "whole-file forbidden-phrase assertion over report.md and README.md — PASS; no `stays pending` regex match remains"
        status: pass
      - kind: other
        ref: "merge-path count assertion in report.md — PASS n=1 m=1"
        status: pass
    human_judgment: false
  - id: D5
    description: "The five-label vocabulary is unchanged and no `simulated` value was promoted to `measured`; no Fritzing artifact was added."
    requirement: "SIM-03"
    verification:
      - kind: other
        ref: "git status/diff over docs/assets and homeworks/*/assets — no new path; report ledger definition untouched"
        status: pass
    human_judgment: true
    rationale: "Whether a prose value was implicitly upgraded is a reviewer judgment; the automated checks prove only the file-level constraints."

# Metrics
duration: 4 min
completed: 2026-10-26
status: complete
---

# Phase 7 Plan 4: Simulator Decision and Outcome Application Summary

**ADR-0014 selects Wokwi as the primary executed simulator behind a platform-role matrix, and `simulation.status` becomes `verified` on a `3/3` scenario-passed handoff, with every stale simulation claim reconciled and every generated view regenerated.**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-10-26T15:49:31Z
- **Completed:** 2026-10-26T15:53:05Z
- **Tasks:** 2
- **Files modified:** 8 (1 created, 7 modified regenerated/included)

## Accomplishments

- Wrote `docs/decisions/0014-simulator-selection.md` in the ADR-0013 MADR shape, with Wokwi, Velxio, Renode and Fritzing each carrying a role, a platform scope and the evidence depth the spike actually produced.
- Carried the measured costs exactly as labelled: build cold median `8.13 s`, build warm `0.49 s`, simulator cold `3.759 s`, warm `6.753 s` and `11.238 s`, wall clock `5.815–12.701 s`, serial `3/3`, and simulated minutes `calculated (upper bound)` `15 s` per run.
- Recorded the calculated CI cost basis with `PRs_per_month = 20`, sensitivity at 5 and 50, and the separate session-cap check, labelling all of it `calculated`.
- Added the SIM-03 licence paragraph (Fritzing illustration-only with attribution, no part graphics copied, `diagram.json` canonical) and the AGPL reference-only boundary for the Velxio image.
- Read `**Outcome:** scenario passed` and applied Branch A: `simulation.status: verified`, T-15 `verified`, and `docs/homeworks/1_3-police-flasher.md` rendering `wokwi (verified)`.
- Reconciled the §7 simulation paragraph, L-08, T-15, the §9 industry note and conclusion paragraph, the §9 status paragraph, Decision Appendix item 7 and the homework README, then swept both files for nine forbidden stale phrases.
- Regenerated `mkdocs.yml`, `docs/homeworks/1_3-police-flasher.md` and `generated.manifest` once through `gen_views.py --all`; `--all --check` is green.

## Task Commits

Each task was committed atomically:

1. **Task 1: ADR-0014 reaches the generated site end to end** - `003db97` (docs)
2. **Task 2: Apply the outcome to the metadata and reconcile every stale simulation claim** - `475abb3` (docs)

**Plan metadata:** the SUMMARY commit that follows this file.

## Files Created/Modified

- `docs/decisions/0014-simulator-selection.md` - the decision: role matrix, measured costs, calculated CI basis, fidelity limits, licence boundary and confirmation commands.
- `docs/decisions/README.md` - one appended row linking `0014`, in date order after the last existing row.
- `homeworks/1_3-police-flasher/homework.yaml` - `simulation.status: pending` to `verified`; no other `simulation` key touched.
- `homeworks/1_3-police-flasher/report.md` - the reconciled §7, L-08, T-15, §9 and Decision Appendix statements, with `../../scripts/pio/merge_firmware.py`.
- `homeworks/1_3-police-flasher/README.md` - the §Simulation pointer to the evidence and the ADR, replacing the deferral sentences.
- `docs/homeworks/1_3-police-flasher.md` - regenerated page; `Simulation` cell is now `wokwi (verified)`.
- `mkdocs.yml` - regenerated nav entry for ADR-0014.
- `generated.manifest` - refreshed digest and byte count for the regenerated page, nav and manifest.

## Decisions Made

- Applied Branch A because the handoff carries `**Outcome:** scenario passed`; the status is not inferred from the presence of run rows.
- Kept the five-label vocabulary and the `simulated` label: the execution changes the metadata status, not the provenance class of a simulator-produced value.
- Added `###` subsections inside `## Decision Outcome` for the matrix, the cold/warm definition, the measured costs, the CI basis, fidelity limits and the licence boundary; ADR-0013 already uses this shape before `### Consequences`.
- Placed the `# ` title on line 8, immediately after the frontmatter, so the plan's `head -8` assertion holds; markdownlint MD022 accepts a heading directly after the frontmatter block.
- Named the evidence file as a repository-relative code span in both the ADR and the prose, never as a link that would not resolve on the site.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Verification defect] The plan's schema assertion reads a key the schema does not have**
- **Found during:** Task 2 verification
- **Issue:** The plan's automated check uses `s['$defs']['simulation']['status']['enum']`, but `schema/homework.schema.json`
  stores the enum at `$defs.simulation.properties.status.enum`; the command raises `KeyError: 'status'` on an unchanged schema.
- **Fix:** Ran the equivalent invariant against the real path (enum is exactly `[none, pending, verified]`, no `evidence` property, `additionalProperties: false`) and proved `git diff -- schema/homework.schema.json` is empty. No schema edit was made, so the intent of the check (D-10) is satisfied.
- **Files modified:** none (verification only)
- **Verification:** the corrected assertion prints PASS; the schema diff is empty.
- **Committed in:** n/a — no file changed; recorded here as a plan-verification defect.

**2. [Rule 1 - Stale claim] The §9 opening clause denied any simulator claim**
- **Found during:** Task 2 (§9 reconciliation)
- **Issue:** Beyond the enumerated site at line 421, the same paragraph opened with "The evidence does not
  support any claim about the bench, the serial port, or the simulator", which became false once the executed
  run existed.
- **Fix:** Narrowed the clause to the bench and the serial port, and stated that the simulation evidence is
  simulation-only. The following sentence now records the executed outcome and points at the evidence file.
- **Files modified:** `homeworks/1_3-police-flasher/report.md`
- **Verification:** the branch-aware whole-file assertion passes and no forbidden phrase remains.
- **Committed in:** `475abb3`

---

**Total deviations:** 1 plan-verification defect handled without a file change, 1 stale-claim correction (Rule 1).
**Impact on plan:** No scope was added, the schema is untouched, and the reconciled paragraph now agrees with the rest of §9.

## Issues Encountered

- **Sandbox wrapper and git.** Several compound `git` invocations were refused by the worktree guard when the command was too complex to prove worktree-local (for example `git status --short` behind the output-condensing wrapper). They were run as plain `/usr/bin/git` commands from the worktree root, the same pattern Plans 02 and 03 recorded.
- **Plan verify JSON path.** Recorded as deviation 1 above; the defect is in the assertion, not in the repository.

## User Setup Required

None - no external service configuration required. This plan consumed recorded measurements only and performed no package-manager install.

## Next Phase Readiness

- Phase 8 can build the changed-only CI simulation gate on `session_minutes_per_run = 0.25 min`, `runs_per_PR = 1` and the stated `PRs_per_month = 20`, with the `calculated (upper bound)` qualifier carried through.
- Phase 10 owns the report contract and checker; the reconciled §7/§9 text and T-15 now state what was executed and what remains `not measured`.
- Phase 11 owns the homework README expansion and an SVG schematic; this plan deliberately added neither.
- Open and explicitly labelled: the dashboard quota delta is still unmeasured (every quota figure is a timeout upper bound), Velxio pilot compile/serial remain `not measured`, and the STM32/Renode row stays a reasoned `not measured` pending the course model.

---

*Phase: 07-simulation-spike*
*Completed: 2026-10-26*

## Self-Check: PASSED
