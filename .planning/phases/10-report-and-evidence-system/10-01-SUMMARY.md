---
phase: 10-report-and-evidence-system
plan: 01
subsystem: tooling
tags: [python, markdown-parser, contract-checker, report, stdlib]

requires:
  - phase: 04-metadata-contract
    provides: scripts/metadata/{paths,errors,render,yaml_loader} helpers and check_metadata.py's CLI, record, and exit-code contract
provides:
  - scripts/report/ stdlib-only package with the literal vocabulary, a fence-aware Markdown scan, pipe-table cell helpers, and the rule engine
  - scripts/check_report.py with --dir, --json, variadic paths, and rule+line in both text and JSON records
  - rule ids RPT-001..RPT-004 and RPT-101..RPT-108, each with a violating fixture
affects: [10-02, 10-03, 10-04, 10-05, 10-06, 10-07, 10-08]

actuals:
  tokens: 12608
  tasks: 3
  commits: 3
  plan_head_before: 4ae6c65dae5b5e817f07dab6288425366bb1e752
  plan_head_after: a5bd33992a9c326068607dd1e59252bf9a43c117

tech-stack:
  added: []
  patterns:
    - "Stdlib-only rule modules with one PyYAML-aware entry script (the metadata checker's import ladder)"
    - "One linear fence-aware Markdown pass: classification changes, numbering never does"
    - "Records carry a stable rule id and a line, sorted by (path, line, rule)"

key-files:
  created:
    - scripts/report/__init__.py
    - scripts/report/vocabulary.py
    - scripts/report/markdown.py
    - scripts/report/tables.py
    - scripts/report/contract.py
    - scripts/check_report.py
    - scripts/tests/test_report.py
  modified: []

key-decisions:
  - "The report checker sorts by (path, line, rule) and carries rule and line in both the text and --json records, deliberately unlike check_metadata.py, which sorts by path and drops line from JSON"
  - "The lifecycle and status-pair rules live in the PyYAML-aware CLI while the structure rules stay in the stdlib-only contract module, so the test suite can import the rules under plain python3"
  - "The not-applicable marker is legal only in sections 3 and 5; a marker on section 5 waives its four subsections (the documented reading of Open Question 1 / A2)"
  - "Heading failures short-circuit the structure rules, so one missing section produces one RPT-101 rather than a cascade of subsection errors"
  - "A missing heading and a missing subsection report line 0 because the document has no line to name"

patterns-established:
  - "Fence toggle before the heading test, enumerated once: a fenced heading is invisible but every reported line stays true"
  - "One literal vocabulary module projected into the checker; the template parity test lands in plan 10-05"

requirements-completed: [REPORT-01]

coverage:
  - id: D1
    description: "The stdlib-only scripts/report/ package, the fence-aware Markdown scan and table helpers, and the check_report.py CLI with its record and exit-code contract"
    requirement: REPORT-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#TracerTests"
        status: pass
      - kind: integration
        ref: "uv run scripts/check_report.py --help"
        status: pass
    human_judgment: false
  - id: D2
    description: "The complete structure rules RPT-104..RPT-108, including the section-5 not-applicable waiver and the section-7 extra-subsection tolerance"
    requirement: REPORT-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#HeadingsTests"
        status: pass
    human_judgment: false
  - id: D3
    description: "Lifecycle gating RPT-001/RPT-003, the placeholder exemption, the one-mebibyte bound RPT-004, determinism, and positional semantics"
    requirement: REPORT-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#LifecycleTests"
        status: pass
      - kind: integration
        ref: "python3 -m unittest discover scripts/tests"
        status: pass
    human_judgment: false

duration: 3 min
completed: 2026-10-27
status: complete
---

# Phase 10 Plan 01: Report Contract Skeleton Summary

**A stdlib-only report engine and `check_report.py` CLI that freeze twelve stable rule ids, a fence-aware structural Markdown parse, and the `path:line: STATUS [RULE] — reason` record contract every later report plan composes into.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-10-27T14:05:54Z
- **Completed:** 2026-10-27T14:09:19Z
- **Tasks:** 3
- **Files modified:** 7 created

## Accomplishments

- `scripts/report/` exists as a stdlib-only package: `vocabulary.py` owns every locked
  heading, header, label, marker and the rule registry; `markdown.py` does the single
  fence-aware scan; `tables.py` splits escaped pipes and normalizes cells; `contract.py`
  evaluates the rules with no file I/O.
- `scripts/check_report.py` mirrors `check_metadata.py` — `--dir`, `--json`, variadic
  paths, exit 0/1/2 — with `rule` and `line` added to both the text and the JSON record.
- All twelve rule ids are live and non-vacuous: `RPT-001`…`RPT-004` and `RPT-101`…`RPT-108`
  each have a fixture that fails with that id, plus passing counterparts for the
  section-5 waiver and the section-7 extra subsection.
- The fence case proves both halves of Pitfall 4: a `## 9. Conclusions` inside a fenced
  block is invisible, and an out-of-order heading after the fence reports its true line.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end report check on one fixture** - `c2fb1cc` (feat)
2. **Task 2: Complete the structure rules** - `80e2881` (feat)
3. **Task 3: Lifecycle gating, placeholder exemption, determinism** - `a5bd339` (feat)

**Plan metadata:** this SUMMARY commit (docs)

## Files Created/Modified

- `scripts/report/__init__.py` — package marker naming the stdlib-only structural half.
- `scripts/report/vocabulary.py` — the ten headings, required subsections, six table
  headers, evidence labels, not-applicable marker, `REPORT_MAX_BYTES`, and the `RULES`
  registry with a remediation per id.
- `scripts/report/markdown.py` — `headings()`, `sections()`, `paragraph_starts()`, and
  `paragraph_begins_with()` over one enumerated pass.
- `scripts/report/tables.py` — `split_row()`, `normalize_cell()`, `normalize_platform()`.
- `scripts/report/contract.py` — `validate_report()` with the size gate, the placeholder
  exemption, the heading rules, and the structure rules.
- `scripts/check_report.py` — CLI, YAML read with `StrictSafeLoader`, symlink refusal with
  `read_regular_text`, positional reduction, dedupe, sort, and exit codes.
- `scripts/tests/test_report.py` — `TracerTests`, `HeadingsTests`, `LifecycleTests`, and
  the stdlib-only import-boundary check (26 tests).

## Decisions Made

- **Records differ from the metadata checker on purpose.** They sort by
  `(path, line, rule)` and keep `line` in `--json`, because D-04 promises a specific
  location for every failure. Copying `check_metadata.py` verbatim would have lost it.
- **The status pair is checked in the CLI, the prose structure in the contract module.**
  `RPT-001`/`RPT-003` need the parsed `homework.yaml`, which only the PyYAML-aware entry
  script may load; keeping them out of `contract.py` preserves the stdlib-only boundary.
- **Section 5's marker is the waiver.** A `_Not applicable — …._` on `## 5. Hardware and
  Wiring` skips its four subsection requirements; without the marker all four are
  required. Both shapes are tested, and the rule is commented with D-34 and Open
  Question 1.
- **Heading errors short-circuit structure.** A missing `## 4. Theory` yields `RPT-101`
  only; subsection rules do not re-report the same absence.

## Deviations from Plan

### Intentional scope trims

**1. The fixture root carries no `assets/diagram.json`**
- **Found during:** Task 1
- **Issue:** the task action names `assets/diagram.json` as part of the temporary root.
- **Decision:** no rule this plan implements reads the diagram — BOM referential
  integrity (D-12) is plan 10-02's rule. The fixture gains the diagram when the first
  rule consumes it, so this plan ships no unused artifact.
- **Files modified:** `scripts/tests/test_report.py`
- **Verification:** the full suite is green; plan 10-02 extends the same `FixtureBase`.
- **Committed in:** `c2fb1cc`

---

**Total deviations:** 0 auto-fixed (1 intentional scope trim).
**Impact on plan:** the contract, the rule ids and the CLI are exactly as specified; no
rule was weakened to make a fixture pass.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Verification

- `python3 -m unittest scripts.tests.test_report -v` — 26 tests, green under plain
  `python3` with no third-party import in the test module.
- `python3 -m unittest discover scripts/tests` — 467 tests, `OK (skipped=1)`.
- `uv run scripts/check_report.py --help` — exit 0, names `--dir`.
- `uv run scripts/check_report.py` on the real tree — exit 1 with exactly one
  `RPT-104` naming the missing `### Next Steps` in `homeworks/1_3-police-flasher/report.md`.
  That failure is expected until plan 10-06 retrofits the report and must not be "fixed"
  by weakening the rule.

## Next Phase Readiness

- Plans 10-02 onward compose into `validate_report()` and the CLI shape this plan froze;
  the rule ids, the record keys, the sort order and the exit codes are stable.
- The real tree intentionally fails one `RPT-104` until plan 10-06 adds
  `### Next Steps` to the worked example.
- Template parity (D-23) and the `check-report` hook (D-05) remain with their owning plans.

## Self-Check: PASSED

- Created files exist: `scripts/check_report.py`, `scripts/tests/test_report.py`, and all
  five modules under `scripts/report/`.
- Commits exist on `worktree-agent-a2878c9c7062019a2`: `c2fb1cc`, `80e2881`, `a5bd339`.
- Full suite: `Ran 467 tests — OK (skipped=1)`.

---
*Phase: 10-report-and-evidence-system*
*Completed: 2026-10-27*
