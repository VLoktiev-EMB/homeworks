---
phase: 04-metadata-contract-and-scaffolding
plan: "05"
subsystem: documentation
tags: [madr, adr-0009, adr-0010, agents-md, reuse-toml, license-split, phase-gate, pio-run, sdkconfig, provenance]

# Dependency graph
requires:
  - phase: 04-metadata-contract-and-scaffolding
    plan: "01"
    provides: schema/homework.schema.json, scripts/metadata/contract.py and the 0/1/2 checker contract
  - phase: 04-metadata-contract-and-scaffolding
    plan: "02"
    provides: templates/homework-arduino and templates/homework-espidf proven at homeworks/<id> depth
  - phase: 04-metadata-contract-and-scaffolding
    plan: "03"
    provides: task/report/adr/board-profile templates, the D-39 sentinel and the Cyrillic allowlist
  - phase: 04-metadata-contract-and-scaffolding
    plan: "04"
    provides: scripts/new_homework, the golden trees, the check-metadata hook and test_metadata_deps.py
provides:
  - docs/decisions/0009-homework-metadata-contract.md — the durable reason behind the schema, field set and sentinel rule
  - docs/decisions/0010-python-dependency-policy.md — the durable reason behind PEP 723 plus the isolated pre-commit environment
  - docs/decisions/README.md — index rows 0009 and 0010, next number 0011
  - AGENTS.md — the rulebook describing the tree as it exists (at 227 lines)
  - REUSE.toml — document templates resolve to CC-BY-4.0 under the MIT catch-all
  - phase-gate evidence — both templates scaffolded into a temp root and built with pio run
affects: [phase-5-generators, phase-8-ci, phase-9-skills, phase-11-pilot]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
actuals:
  tokens: 7096
  tasks: 3
  commits: 2

commits: 2
plan_head_before: bd609765160286f18f25f67d5d7ba801add822ab
plan_head_after: 9ed378e6fd02e1e7516dbd5e6c669cc690bb0cae

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Normative prose names the phase that owns CI, so no consumer cites a job that does not exist"
    - "The REUSE catch-all stays first because the last matching annotation wins"
    - "The phase gate builds from scaffolded output, never from a hand-rendered fixture"

key-files:
  created:
    - docs/decisions/0009-homework-metadata-contract.md
    - docs/decisions/0010-python-dependency-policy.md
  modified:
    - docs/decisions/README.md
    - AGENTS.md
    - REUSE.toml

key-decisions:
  - "ADR-0009 records the five sentinel-bearing fields as one normative list — four task.md provenance fields plus homework.yaml source.reference — and states that body TODOs are manual-review signals, not status-gated values"
  - "ADR-0009 fixes the title-case derivation exactly: split at the first underscore, split the remainder at the first hyphen, replace remaining hyphens with spaces and title-case each word"
  - "Both ADR Confirmation sections name only commands runnable today and name Phase 8 as the CI owner; neither claims CI runs them now"
  - "AGENTS.md refers to `### Homework identifiers` instead of re-quoting the anchored pattern, so the file keeps exactly one backticked anchored regex"
  - "AGENTS.md moves homeworks/, lib/, schema/ and templates/ into Present today and leaves only docs/standards/ and the skills path planned"
  - "templates/**/*.md was appended to the existing CC-BY-4.0 annotation rather than added as a third annotation, so the MIT catch-all remains index 0"

patterns-established:
  - "An ADR states what is true today and names the phase that extends it, so documentation never overclaims enforcement"
  - "The rulebook references a rules section by heading rather than repeating a machine-checked literal"
  - "A phase gate scaffolds into a disposable root and builds generated output, proving the shipped path instead of a fixture"

requirements-completed: [FOUND-01, META-01, META-02, META-03, META-04]

coverage:
  - id: D1
    description: "ADR-0009 and ADR-0010 exist with the five MADR frontmatter keys, the eight sections in order, a chosen-option opening sentence, at least three (0009) / three (0010) options with judgement bullets, and index rows that agree on title, status and date; the next number is 0011"
    requirement: META-01
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_adrs -v (20 tests, OK)"
        status: pass
      - kind: other
        ref: "index/CI-boundary check: rows=2, next=0011, both records contain 'Phase 8 wires CI'"
        status: pass
    human_judgment: false
  - id: D2
    description: "ADR-0009 records the locked field set, enums, derived title rule, additionalProperties strictness, patterns-over-format rule, the split authority between source.reference and task.md, and all five sentinel-bearing fields in one normative list"
    requirement: META-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_adrs.py#MadrStructureTests (sections, options, pros and cons, chosen option)"
        status: pass
      - kind: other
        ref: "manual read against 04-05-PLAN Task 1 action; both records carry the D-39 five-field list"
        status: pass
    human_judgment: false
  - id: D3
    description: "AGENTS.md describes the tree truthfully: schema/, templates/, lib/ and homeworks/<id>/ are present today, the quick-start carries uv run scripts/check_metadata.py, the two routing rows exist, the file is 227 lines, and exactly one backticked anchored regex remains"
    requirement: META-03
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_agents_md scripts.tests.test_homework_id -v"
        status: pass
      - kind: other
        ref: "span/line check: anchored_spans=['^[0-9]+_[0-9]+-[a-z0-9-]+$'], lines=227"
        status: pass
    human_judgment: false
  - id: D4
    description: "REUSE.toml declares templates/**/*.md as CC-BY-4.0 after the MIT catch-all, and reuse lint is green"
    requirement: FOUND-01
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_license_hygiene -v"
        status: pass
      - kind: integration
        ref: "reuse --no-multiprocessing lint (exit 0, 243/243 files licensed)"
        status: pass
    human_judgment: false
  - id: D5
    description: "A scaffolded Arduino project and a scaffolded ESP-IDF project both build with pio run from a temporary root that contains the shared configuration, partitions, schema and templates"
    requirement: FOUND-01
    verification:
      - kind: integration
        ref: "pio run -d <tmp>/homeworks/1_3-gate-arduino (SUCCESS, 5.89 s; Flash max 6,553,600)"
        status: pass
      - kind: integration
        ref: "pio run -d <tmp>/homeworks/1_3-gate-espidf (SUCCESS, 24.57 s; Flash max 6,553,600)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The scaffolded Arduino project's native environment runs the rendered Unity test tree, not just compiling it"
    requirement: META-04
    verification:
      - kind: integration
        ref: "pio test -d <tmp>/homeworks/1_3-gate-arduino -e native (2 test cases PASSED, no FAILED)"
        status: pass
    human_judgment: false
  - id: D7
    description: "The scaffolded ESP-IDF project's generated sdkconfig.json reports 16 MB flash, SPIRAM enabled and octal PSRAM"
    requirement: META-04
    verification:
      - kind: other
        ref: "sdkconfig.json: ESPTOOLPY_FLASHSIZE_16MB=True, SPIRAM=True, SPIRAM_MODE_OCT=True, SPIRAM_MODE_QUAD=False"
        status: pass
    human_judgment: false
  - id: D8
    description: "The full repository suite and every pre-commit hook are green, including the new check-metadata hook"
    requirement: META-04
    verification:
      - kind: unit
        ref: "UV_CACHE_DIR=<sandbox-writable> python3 -m unittest discover -s scripts/tests -v (298 tests, OK)"
        status: pass
      - kind: integration
        ref: "pre-commit run --all-files (exit 0, all eight hooks Passed)"
        status: pass
    human_judgment: false
  - id: D9
    description: "Documentation never claims that CI enforces the metadata contract in Phase 4; every Confirmation names only commands a developer runs today"
    requirement: FOUND-01
    verification:
      - kind: other
        ref: "verify command: both records contain 'Phase 8 wires CI'; missing_ci_boundary=[]"
        status: pass
    human_judgment: false

# Metrics
duration: 5min
completed: 2026-10-24
status: complete
---

# Phase 4 Plan 5: Decisions, Rulebook and Phase Gate Summary

**ADR-0009 and ADR-0010 recorded as the durable contract, an AGENTS.md and REUSE.toml that describe the tree as it actually exists, and a phase gate that scaffolded and built both homework templates from generated output**

## Performance

- **Duration:** 5 min
- **Started:** 2026-10-24T21:12:07Z
- **Completed:** 2026-10-24T21:17:11Z
- **Tasks:** 3 (2 committed, 1 verification-only)
- **Files modified:** 5 paths (2 created, 3 modified)

## Accomplishments

- `docs/decisions/0009-homework-metadata-contract.md` records the contract itself: the
  `schema/homework.schema.json` path, the nine required fields and four typed optional
  blocks, the integer `schema_version: 1`, the four-value status model, the exact
  derived-title rule, `additionalProperties: false` at every level, patterns rather than
  `format`, and the deliberate split of authority between `source.reference` and `task.md`.
  Its More Information section carries the D-39 rule as **one normative list of exactly five
  fields** — `task.md` `source_url`, `retrieved`, `attribution`, `license` plus
  `homework.yaml` `source.reference` — legal as the literal `TODO` only while
  `status: planned`, with body TODOs explicitly marked as manual-review signals.
- `docs/decisions/0010-python-dependency-policy.md` records the two delivery paths (PEP 723
  under `uv`; an isolated `language: python` pre-commit environment with explicit
  `additional_dependencies`), the two rejected alternatives, and the stdlib drift test that
  binds the declarations. Both Confirmation sections name only today's commands and state
  that Phase 8 wires CI, so neither overclaims enforcement.
- `AGENTS.md` now describes the repository as it exists: `schema/`, `templates/`, `lib/` and
  `homeworks/<id>/` moved into "Present today", the quick-start gained
  `uv run scripts/check_metadata.py`, a `### Metadata and provenance` rules subsection added
  four MUST rules, and the routing table gained the create-a-homework and validate-metadata
  rows. The file is **227 lines** (ceiling 300) and still contains exactly one backticked
  anchored regex — the canonical homework-ID pattern.
- `REUSE.toml` resolves `templates/**/*.md` to CC-BY-4.0 by extending the existing annotation,
  leaving template `.ini`/`.json` and `schema/**` on the MIT catch-all and keeping that
  catch-all first. `reuse --no-multiprocessing lint` reports 243/243 files licensed.
- **Phase gate:** a disposable root with `platformio.shared.ini`, `partitions/`, `schema/`,
  `templates/`, `scripts/pio/`, `scripts/metadata/allowlist.json` and a `lib/` symlink was
  scaffolded twice with `scripts/new_homework`. `pio run` returned SUCCESS for the Arduino
  project (5.89 s, Flash max 6,553,600 = 16 MB table) and for the ESP-IDF project (24.57 s,
  Flash max 6,553,600). `pio test -e native` on the scaffolded Arduino project ran 2 rendered
  Unity cases, both `[PASSED]`, with no `[FAILED]` line. The generated `sdkconfig.json`
  reports `ESPTOOLPY_FLASHSIZE_16MB=True`, `SPIRAM=True`, `SPIRAM_MODE_OCT=True` and
  `SPIRAM_MODE_QUAD=False`.
- Full suite green at **298 tests**, and `pre-commit run --all-files` passes all eight hooks
  including `check-metadata`.

## Task Commits

Each committing task was committed atomically:

1. **Task 1: Record the contract — ADR-0009, ADR-0010 and the index rows** - `cd94daf` (feat)
2. **Task 2: Update AGENTS.md and the license declaration for the new tree** - `9ed378e` (docs)
3. **Task 3: Phase gate — scaffold both templates, build both, run the full suite** - no commit
   (verification-only task; it writes no tracked file and creates no repository `homeworks/`
   directory)

**Plan metadata:** the docs commit that carries this file, made after the measured range above.

## Files Created/Modified

- `docs/decisions/0009-homework-metadata-contract.md` — the metadata contract, the locked
  vocabulary, the five-field sentinel rule and the CI boundary.
- `docs/decisions/0010-python-dependency-policy.md` — PEP 723 plus the isolated pre-commit
  environment, the rejected alternatives, and the drift test.
- `docs/decisions/README.md` — index rows for 0009 and 0010; `Next number: **0011**.`.
- `AGENTS.md` — quick-start row, present-today layout, metadata rules, routing rows.
- `REUSE.toml` — `templates/**/*.md` joins the CC-BY-4.0 annotation.

## Decisions Made

- The two ADRs were written as the *reason* behind the contract, not a restatement of the
  schema: each states the options it rejected and what makes the chosen one survivable.
- `source.reference`'s sentinel extension is stated as a first-class decision sentence, so a
  reader cannot mistake it for an implementation detail.
- Body TODOs are documented as manual-review signals and explicitly not status-gated, so no
  reader infers a machine check that does not exist.
- `templates/**/*.md` was appended to the existing CC-BY-4.0 annotation rather than introduced
  as a third one, preserving the single catch-all at index 0 and the last-match-wins contract.
- `AGENTS.md` names the `### Homework identifiers` section instead of quoting the ID pattern,
  which is what keeps the exactly-one-anchored-regex invariant intact.
- Task 3 produced no commit by design: the gate builds into `$TMPDIR` and touches no tracked
  file, so committing would add an empty change.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The plan's `sdkconfig.json` assertion used `CONFIG_`-prefixed keys**
- **Found during:** Task 3 (phase gate)
- **Issue:** The verify block reads `CONFIG_ESPTOOLPY_FLASHSIZE_16MB`, `CONFIG_SPIRAM` and
  `CONFIG_SPIRAM_MODE_OCT`; ESP-IDF 6.1 writes unprefixed Kconfig names
  (`ESPTOOLPY_FLASHSIZE_16MB`, `SPIRAM`, `SPIRAM_MODE_OCT`), so the literal command returns
  `None` and fails despite a correct configuration. This is the same finding 04-02 recorded.
- **Fix:** Asserted the same three facts through a lookup that accepts both spellings; the
  observed values match the research evidence exactly.
- **Files modified:** none (verification only)
- **Verification:** `flash16= True spiram= True oct= True quad= False`
- **Committed in:** n/a (verification only)

**2. [Rule 3 - Blocking] The plan's single compound `<automated>` gate command was refused**
- **Found during:** Task 3 verification
- **Issue:** The worktree harness refuses a compound shell command that passes runtime-computed
  paths (`$TMPDIR`) into `uv`, `pio` and `python3`; the plan's gate is one such command.
- **Fix:** Ran the identical steps as separate plain commands against a fixed root
  (`/tmp/claude-501/hw-gate-YaZBWi`), preserving the same layout, scaffold flags, build
  commands, log destinations and assertions.
- **Files modified:** none (verification only)
- **Verification:** Both scaffolds, both builds, the native test and the sdkconfig evidence
  reproduced exactly as the plan specifies.
- **Committed in:** n/a (verification only)

**3. [Rule 3 - Blocking] The full suite initially failed on the sandbox-denied `uv` cache**
- **Found during:** Task 3 (full suite)
- **Issue:** The first `python3 -m unittest discover -s scripts/tests` run reported 25 failures
  and 2 errors; every failure traced to `uv` being unable to create a temporary file in
  `~/.cache/uv` ("Operation not permitted"). The tests invoke `uv run` as a subprocess and
  inherit the environment.
- **Fix:** Re-ran the suite with `UV_CACHE_DIR=/tmp/claude-501/uv-cache`, the sandbox-writable
  cache the earlier waves documented.
- **Files modified:** none (environment only)
- **Verification:** 298 tests, OK.
- **Committed in:** n/a (environment only)

### Verification-only workarounds

**4. [Rule 3 - Blocking] The plan's Task 1 and Task 2 verify commands carry no absolute paths**
- Not a deviation: both task verify suites and the two Python assertions ran verbatim, in the
  worktree, and passed. Recorded here only so the absence of a workaround is auditable.

---

**Total deviations:** 3 auto-fixed (1 bug, 2 blocking) plus 1 non-deviation note.
**Impact on plan:** No scope creep. All three are verification-mechanics corrections; no
product source, schema, template or script behaviour changed in this plan.

## Issues Encountered

- `pio run` and `pio test` each attempted an outbound connection to `185.199.110.153:80`
  (GitHub Pages) which the sandbox denied. Both commands still returned SUCCESS/PASSED; the
  same denial is recorded by earlier waves for an unrelated existing test, so it is
  environmental and out of scope.
- The full suite's 298-test count matches the 04-04 baseline; no test was added or removed by
  this plan, which is the intended shape for a documents-and-gate plan.
- `REQUIREMENTS.md` was not modified: under parallel execution the orchestrator owns shared
  tracking artifacts. The five requirement IDs are declared in this summary's
  `requirements-completed` for that central update.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. The literal `TODO` values seen in the temporary gates are the D-39 provenance sentinel
generated by `scripts/new_homework` while `status: planned`; they live only in the disposable
`$TMPDIR` root and are the intended scaffold output, not placeholder data returned by shipped
code.

## Threat Flags

None beyond the plan's threat model. The records implement T-04-12 (Confirmation sections name
today's commands and Phase 8 as the CI owner), T-04-13 (MIT catch-all stays first with the
CC-BY annotation after it), T-04-14 (existing paths moved out of "Planned") and T-04-19
(exactly one backticked anchored regex, 227 lines against a 300-line ceiling). The gate
installed nothing new, reusing the pins fixed by 04-01 and 04-04 (T-04-SC).

## Next Phase Readiness

- Phase 4's success criteria are now evidenced: the contract, the checker, both templates, the
  scaffold, the four cross-cutting documents and a buildable scaffolded project for each
  template.
- The Phase 3 target-compilation carry-forward is discharged with build evidence: the
  scaffolded Arduino and ESP-IDF projects each compiled the matching adapter and reported
  SUCCESS, and the scaffolded Arduino native test ran green.
- Phase 5 can consume `schema/homework.schema.json` and the derived-title rule exactly as
  ADR-0009 states; Phase 8 owns wiring the same commands into CI.
- No blockers.

---
*Phase: 04-metadata-contract-and-scaffolding*
*Completed: 2026-10-24*

## Self-Check: PASSED

- `docs/decisions/0009-homework-metadata-contract.md`, `docs/decisions/0010-python-dependency-policy.md`,
  `docs/decisions/README.md`, `AGENTS.md` and `REUSE.toml` all exist on disk.
- Task commits `cd94daf` and `9ed378e` are ancestors of HEAD; the measured range
  `bd60976..9ed378e` contains exactly 2 commits.
- `python3 -m unittest scripts.tests.test_adrs` — 20 tests, OK.
- `python3 -m unittest scripts.tests.test_agents_md scripts.tests.test_homework_id scripts.tests.test_license_hygiene` — 33 tests, OK.
- `reuse --no-multiprocessing lint` — exit 0, 243/243 files licensed.
- `UV_CACHE_DIR=/tmp/claude-501/uv-cache python3 -m unittest discover -s scripts/tests` — 298 tests, OK.
- `pre-commit run --all-files` — exit 0, all hooks Passed.
- Both scaffolded projects built with SUCCESS; the native test printed `[PASSED]` and no `[FAILED]`;
  `sdkconfig.json` reports 16 MB flash, SPIRAM and octal PSRAM.
- No repository `homeworks/` directory and no build output were created by the gate.
