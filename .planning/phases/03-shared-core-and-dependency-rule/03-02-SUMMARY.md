---
phase: 03-shared-core-and-dependency-rule
plan: 02
subsystem: documentation
tags: [madr, adr, dependency-rule, ports-and-adapters, consumer-owned-contracts, agents-md, quick-start]

# Dependency graph
requires:
  - phase: 03-shared-core-and-dependency-rule
    plan: 01
    provides: "Consumer-owned port_time_t contract, the native tests/ project and the 19-case Unity suite that the ADR's confirmation cites"
provides:
  - "ADR-0008 (accepted): common depends on port, port depends on nothing, ports are consumer-owned"
  - "The one-sentence supersession clause that leaves ADR-0002 accepted and byte-identical"
  - "The void *ctx interpretation: port owns no global mutable state; the state belongs to the adapter or the fake"
  - "Status-index row 0008 and the advanced next-number footer 0009"
  - "Runnable quick-start commands: pio run -d <project> and pio test -d tests -e native"
affects: [03-03, 03-05, 03-07, 03-08, 03-09, 04, 08]

actuals:
  tokens: 2600
  tasks: 2
  commits: 2
  plan_head_before: b035239026a43deea099ad0aa96639dd882bdc2e
  plan_head_after: 0f52feecbb065c32631fba7c3f5f94344aa5c830

tech-stack:
  added: []
  patterns:
    - "MADR record that supersedes exactly one sentence of a predecessor and leaves the predecessor untouched"
    - "Consumer-owned contract as the reason a port carries an opaque void *ctx"
    - "Quick-start commands written with an explicit project directory so they run from the repository root"

key-files:
  created:
    - docs/decisions/0008-common-depends-on-port.md
  modified:
    - docs/decisions/README.md
    - AGENTS.md

key-decisions:
  - "The allowed edge is common -> port; port depends on nothing, adapters and the host double depend on port only, and a homework depends on common, port and exactly one adapter"
  - "ADR-0008 supersedes only the dependency-rule sentence of ADR-0002; ADR-0002 stays accepted, unedited and byte-identical"
  - "'Port contains no state' means port owns no global mutable state and mutates nothing; the state behind ctx belongs to the adapter or the test double, which is what permits two buses or two timers in one process"
  - "The ADR names the checker, the native suite and the pre-commit hook as this phase's gate and explicitly does not claim CI runs them yet"
  - "The quick-start documents pio test -d tests -e native and pio run -d <project> because the repository root is not a PlatformIO project"

patterns-established:
  - "An ADR that reverses one sentence of an accepted record cites that sentence and states what is not superseded"
  - "A record's Confirmation section names only gates that exist at acceptance time and marks future enforcement as future work"

requirements-completed: [ARCH-01, ARCH-05]

coverage:
  - id: D1
    description: "ADR-0008 exists with the five MADR frontmatter keys, status accepted, the 2026-10-24 date, the eight sections in order and the chosen-option opener"
    requirement: ARCH-01
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_adrs -v"
        status: pass
    human_judgment: false
  - id: D2
    description: "The direction and the ctx rule are stated as normative prose, and the record supersedes only ADR-0002's dependency-rule sentence while ADR-0002 remains byte-identical"
    requirement: ARCH-05
    verification:
      - kind: automated
        ref: "python3 -c phrase assertion over docs/decisions/0008-common-depends-on-port.md"
        status: pass
      - kind: automated
        ref: "git hash-object docs/decisions/0002-... equals git rev-parse HEAD:docs/decisions/0002-..."
        status: pass
    human_judgment: true
    rationale: "Whether the prose supersedes exactly the intended sentence and describes future adapters accurately is a reading judgement; the blob hash only proves ADR-0002 was not rewritten"
  - id: D3
    description: "The status index carries exactly one 0008 row whose title, status and date match the record, and the footer reads Next number: 0009"
    requirement: ARCH-05
    verification:
      - kind: unit
        ref: "scripts/tests/test_adrs.py#test_index_has_a_row_for_every_record"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_adrs.py#test_index_titles_match_record_titles"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both documented quick-start commands run from the repository root as written, and AGENTS.md stays at or below 300 lines"
    verification:
      - kind: integration
        ref: "pio test -d tests -e native"
        status: pass
      - kind: integration
        ref: "pio run -d homeworks/0_0-toolchain-smoke -e native"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_agents_md.py#test_stays_under_the_line_ceiling"
        status: pass
    human_judgment: false

duration: 1 min
completed: 2026-10-24
status: complete
---

# Phase 03 Plan 02: Dependency Direction Record Summary

**ADR-0008 accepts `common → port` with consumer-owned `void *ctx` contracts, supersedes only ADR-0002's dependency-rule sentence while leaving that record byte-identical, and makes both quick-start commands runnable from the repository root.**

## Performance

- **Duration:** 1 min
- **Started:** 2026-10-23T22:27:58Z
- **Completed:** 2026-10-23T22:29:33Z
- **Tasks:** 2
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments

- `docs/decisions/0008-common-depends-on-port.md` records the full edge set of D-01: `port` depends on nothing, `common → port` is the only shared edge, every adapter and `lib/host` depend on `port` only, a homework depends on `common`, `port` and exactly one adapter, and `port → common`, `port → adapter`, `adapter → common` plus any framework header inside `common` or `port` are forbidden.
- The record quotes and supersedes exactly one sentence of ADR-0002 while that file's blob hash still equals `HEAD`'s blob, so the reversal is historical and not a silent edit.
- The `void *ctx` interpretation is normative prose now: `port` owns no global mutable state and mutates nothing; the state behind `ctx` belongs to the adapter or the fake, which is what permits two buses, two timers and isolated tests.
- The status index gained exactly one row and the footer advanced to `Next number: **0009**.`, so numbering stays contiguous and the index title matches the record title mechanically.
- `AGENTS.md` step 3 now runs `pio test -d tests -e native` and step 2 now runs `pio run -d <project>`; both were executed from the repository root successfully, and the rulebook is 200 lines.

## Exact supersession quoted from ADR-0002

> The dependency rule is: `lib/common` depends on nothing; `lib/port` declares the
> interfaces and depends on `common`; each adapter (`lib/arduino`, `lib/espidf`, and later
> the STM32 adapter) implements the ports and depends on `port`; a homework depends on
> `common`, `port`, and exactly one adapter.

ADR-0008 supersedes this sentence only. The record's own words: "AD-0002 remains accepted
and is not edited; its decision — ports and adapters rather than a universal HAL — and
every other paragraph stand unchanged. A reader applies this record to that one sentence
and ADR-0002 to everything else." The comma spelling "and exactly one adapter" and the
absence of the serial comma differ from ADR-0002's typography; the quoted sentence above
reproduces ADR-0002 verbatim.

## Considered options

1. `common` depends on `port`, with consumer-owned contracts — chosen.
2. The ADR-0002 wording: `port` depends on `common`.
3. No ports: copy the shared logic into each homework.

Each option carries at least two `* Good,` / `* Neutral,` / `* Bad,` judgements in the
Pros and Cons section.

## `AGENTS.md` diff for steps 2 and 3

```diff
-| 2 | `pio run` | Build the affected PlatformIO environment. |
-| 3 | `pio test -e native` | Run firmware-side native tests, once `homeworks/` exists (Phase 2). |
+| 2 | `pio run -d <project>` | Build the affected PlatformIO environment from its own project directory. |
+| 3 | `pio test -d tests -e native` | Run the shared-library Unity suite from the top-level `tests/` project, without a target toolchain. |
```

Both rows keep the five-cell table shape. `pio test -d tests -e native` ran 19 tests with
19 successes; `pio run -d homeworks/0_0-toolchain-smoke -e native` ended `[SUCCESS]`.

## Task Commits

1. **Task 1: ADR-0008 — common depends on port; ports are consumer-owned** — `87db7da` (docs)
2. **Task 2: Status index, next-number footer, and runnable quick-start commands** — `0f52fee` (docs)

## Files Created/Modified

- `docs/decisions/0008-common-depends-on-port.md` — accepted MADR: context, five drivers, three options, the outcome with the full edge set and the `ctx` reading, good/bad consequences, the Confirmation citing this phase's gate, per-option judgements and the deferred Arduino `.cpp` exception
- `docs/decisions/README.md` — one new status-index row for 0008 and `Next number: **0009**.`
- `AGENTS.md` — step 2 changed to `pio run -d <project>`, step 3 changed to `pio test -d tests -e native`, both purpose cells rewritten

## Decisions Made

- Chose to quote ADR-0002's sentence verbatim rather than paraphrase it, so the supersession is auditable against the predecessor.
- Kept the record's Confirmation strictly present-tense about this phase's gate and named CI as Phase 8's work, because at acceptance the checker and hook are being introduced in later plans of the same phase.
- Left `docs/decisions/README.md` numbering rules untouched; the row and the footer were the only edits.
- Left `REQUIREMENTS.md` unchanged: `ARCH-01` and `ARCH-05` are declared by several plans in this phase, so marking them belongs to the orchestrator after every declaring plan has a SUMMARY (shared-ID gate).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Task 1's full ADR suite cannot pass before Task 2 adds the index row**
- **Found during:** Task 1 verification
- **Issue:** `scripts/tests/test_adrs.py::IndexAgreementTests` derives its expected rows from
  the ADR files on disk. As soon as `0008-common-depends-on-port.md` exists, the full suite
  fails twice — `0008 is absent from the index` and the same row in the title comparison —
  until Task 2 appends the index row. The plan sequences the record in Task 1 and the index
  in Task 2, then gives Task 1 the whole-suite command.
- **Fix:** no code change. Task 1 was verified with the four classes that do not read the
  index (`AdrSetTests`, `AdrFrontmatterTests`, `MadrStructureTests`,
  `RequiredContentTests`, 14 tests OK) plus the plan's direct phrase assertion and the
  ADR-0002 blob-hash comparison. Task 2 then ran the full command
  (`scripts.tests.test_adrs scripts.tests.test_agents_md`, 30 tests OK), which is the
  plan-level verification and the condition the plan's Task 2 already required.
- **Files modified:** none (verification only)
- **Verification:** Task 1 subset 14/14 OK; the only full-suite failures were the two
  index-agreement tests naming 0008; after Task 2 the combined suite is 30/30 OK; the
  whole repository suite is 122/122 OK.
- **Committed in:** n/a (verification-only; evidence in this summary)

---

**Total deviations:** 1 auto-fixed (1 plan-verification ordering defect; no production change)
**Impact on plan:** None on the artifacts. The record, the index and the rulebook are exactly
as the plan specified; only the order in which the plan's own verification commands can go
green changed.

## Issues Encountered

None beyond the verification-ordering deviation above.

## Known Stubs

None. The record deliberately names unimplemented future work (Arduino I2C/SPI `.cpp`
adapters, CI enforcement in Phase 8) as future work rather than as present capability; that
is a documented deferral, not a stub in shipped behaviour.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The dependency direction is now normative in ADR-0008 and indexed, so plans 03-03 through
  03-09 can build contracts, adapters and `scripts/check_architecture.py` against a stated
  rule instead of two documents that disagree.
- ADR-0002 and ADR-0007 remain valid for everything outside the superseded sentence; no
  history was rewritten.
- The quick-start commands are runnable today; plan 03-07's deletion of
  `homeworks/0_0-toolchain-smoke/` no longer breaks step 2 because it takes an explicit
  project path.

---

*Phase: 03-shared-core-and-dependency-rule*
*Completed: 2026-10-24*

## Self-Check: PASSED

- `docs/decisions/0008-common-depends-on-port.md` exists on disk.
- Both task commits (`87db7da`, `0f52fee`) are ancestors of HEAD.
- `python3 -m unittest scripts.tests.test_adrs scripts.tests.test_agents_md -v`: 30 tests OK.
- `python3 -m unittest discover -s scripts/tests -v`: 122 tests OK.
- `pio test -d tests -e native`: 19/19 passed.
- `pio run -d homeworks/0_0-toolchain-smoke -e native`: SUCCESS.
- ADR-0002's working-tree blob equals its committed blob (`55a4c22`).
- Self-check verdict: PASSED.
