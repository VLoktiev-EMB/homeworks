---
phase: 10-report-and-evidence-system
plan: "04"
subsystem: tooling
tags: [python, report-checker, identity, internal-links, cyrillic, sentinels, claim-consistency, stdlib]

requires:
  - phase: 10-report-and-evidence-system
    provides: plan 10-01's report engine and rule/record contract, plan 10-02's table extraction, and plan 10-03's resolve_artifact and section-scoped helpers
provides:
  - rule ids RPT-401, RPT-402, RPT-403 for identity and toolchain normalization
  - rule ids RPT-404, RPT-405, RPT-406 for internal links, English-only text, and authoring sentinels
  - rule ids RPT-407, RPT-408 for native-suite and simulation claim consistency
  - lookup_row(table, key) in scripts/report/tables.py
  - link_targets, is_cyrillic, and paragraph helpers in scripts/report/contract.py
affects: [10-05, 10-06, 10-07, 10-08]

actuals:
  tokens: 9378
  tasks: 3
  commits: 3
  plan_head_before: 64ffb77dbdaeb31a172cf21c4e01a8667b0784d1
  plan_head_after: f02a4b1a41c71614993f83ee08a8717db35f2a37

tech-stack:
  added: []
  patterns:
    - "Identity comparisons use normalized machine values; display prose is never compared"
    - "Every cross-file check names the cell, target, or paragraph it reads and never scans the whole document"
    - "External link schemes are dropped before any filesystem call, so a URL is never resolved or fetched"
    - "Fenced constructs are invisible to link and paragraph scans, matching the heading and table posture"

key-files:
  created: []
  modified:
    - scripts/report/contract.py
    - scripts/report/tables.py
    - scripts/report/vocabulary.py
    - scripts/tests/test_report.py

key-decisions:
  - "Board and Language stay display text: the worked example writes a prose board description against the metadata slug, so string-comparing them would reject a compliant report (D-11)"
  - "lookup_row returns the normalized Value cell for a Field key, so identity records name a field rather than a positional column"
  - "The Cyrillic scan reimplements the four D-40 ranges locally instead of importing scripts.metadata.contract, which would drag PyYAML and jsonschema into the stdlib-only package"
  - "A sentinel is a word-bounded TODO or TBD, and the scan is unreachable for a placeholder report because validate_report returns its waiver first"
  - "Link extraction skips every scheme-bearing target, not only http/https/mailto, and strips an optional title, fragment, and query before resolve_artifact"
  - "Simulation claim consistency inspects only the first **Simulation.** paragraph and only the two run-claim tokens; semantic truth remains review-enforced (D-14)"

patterns-established:
  - "A cross-file rule reports the line of the cell, target, or paragraph it inspected, not the document heading"
  - "The compliant fixture grows once per contract family: identity rows, tests/simulation blocks, and the two claim paragraphs"

requirements-completed: [REPORT-08]

coverage:
  - id: D1
    description: "Identity and toolchain normalization: one H1 equals title, four section-1 cells equal id/title/status/report.status, and Framework, PlatformIO Core, and Platform compare against homework.yaml"
    requirement: REPORT-08
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#IdentityTests"
        status: pass
      - kind: integration
        ref: "uv run scripts/check_report.py --json (real tree has no RPT-401/402/403 record)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Internal link resolution, the English-only scan, and the draft/complete sentinel scan"
    requirement: REPORT-08
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#LanguageTests"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_report.py#LinkTests"
        status: pass
      - kind: integration
        ref: "uv run scripts/check_report.py --json (real tree has no RPT-404/405/406 record)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Native-suite and simulation claim consistency against tests.native and simulation.status"
    requirement: REPORT-08
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#StatusClaimsTests"
        status: pass
      - kind: integration
        ref: "uv run scripts/check_report.py --json (real tree has no RPT-407/408 record)"
        status: pass
    human_judgment: false

duration: 8 min
completed: 2026-10-27
status: complete
---

# Phase 10 Plan 04: Identity, Links, and Claim Consistency Summary

**The report's honest-status surface is now machine-checked end to end: the H1 and four identity cells match `homework.yaml`, toolchain spellings normalize, every relative link resolves without fetching a URL, Cyrillic and `TODO`/`TBD` are rejected, and the native-suite and simulation paragraphs agree with the metadata.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-10-27T14:30:30Z
- **Completed:** 2026-10-27T14:38:48Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- `RPT-401`/`RPT-402`/`RPT-403` compare the document against normalized machine
  values: exactly one H1 equal to `title`; `Homework ID`, `Title`, `Homework status`,
  and `Report status` equal to `id`, `title`, `status`, and `report.status`; and
  `Framework` (casefold), `PlatformIO Core`, and `Platform` (normalized) equal to their
  toolchain values. `Board` and `Language` are deliberately never compared.
- `RPT-404` extracts inline links and images, strips an optional title, fragment, and
  query, skips every external scheme, and resolves the remainder through the plan-10-03
  `resolve_artifact`, so `../../../etc/passwd` is refused and no URL is fetched.
- `RPT-405` rejects any Cyrillic codepoint in `report.md` with its line; `RPT-406`
  rejects a word-bounded `TODO` or `TBD` in a draft or complete report while a
  placeholder report stays exempt.
- `RPT-407`/`RPT-408` require the section-7 native paragraph when `tests.native` is
  true and the `**Simulation.**` paragraph when a simulation block exists, and they
  check that a `verified` run claims `exited 0`/`scenario passed` while a `pending`
  run claims neither.
- The live 1.3 report emits no `RPT-401`…`RPT-408` record under the normalized
  comparison: its H1, identity cells, both links, English text, native paragraph, and
  verified simulation paragraph all pass.

## Task Commits

Each task was committed atomically:

1. **Task 1: Identity and toolchain normalization** - `3fd5a96` (feat)
2. **Task 2: Internal links, English-only scan, sentinel scan** - `df6a738` (feat)
3. **Task 3: Native-suite and simulation claim consistency** - `f02a4b1` (feat)

**Plan metadata:** this SUMMARY commit (docs)

## Files Created/Modified

- `scripts/report/tables.py` — `lookup_row(table, key)` returns the normalized `Value`
  cell of the row whose `Field` is the key.
- `scripts/report/contract.py` — `RPT-401`…`RPT-408` with `_identity_records`,
  `_link_records`, `_language_records`, `_sentinel_records`, `_status_claim_records`,
  the `link_targets`/`is_cyrillic`/`_paragraphs` helpers, and the constants they read.
- `scripts/report/vocabulary.py` — registry entries for `RPT-401`…`RPT-408` with a
  summary and remediation each.
- `scripts/tests/test_report.py` — `IdentityTests`, `LanguageTests`, `LinkTests`,
  `StatusClaimsTests`, the identity/toolchain fixture rows, the `tests` and `simulation`
  fixture blocks, and the two section-7 claim paragraphs.

## Decisions Made

- **Identity is a comparison of normalized machine values.** Backticks and mixed inline
  code are stripped by `normalize_cell`; `Framework` is `casefold()`ed and `Platform`
  goes through `normalize_platform`, so `espressif32@8.0.0` equals
  `` `platformio/espressif32` 8.0.0 ``.
- **`Board` and `Language` are excluded from every comparison.** The worked example
  writes `ESP32-S3-DevKitC-1 (N16R8: …)` against the slug `esp32-s3-devkitc-1`, and the
  language cell is prose; comparing either would reject a compliant report (D-11).
- **The Cyrillic scan owns its four ranges.** Importing `scripts.metadata.contract`
  for the existing `is_cyrillic_char` would pull PyYAML and jsonschema into the
  stdlib-only `scripts/report/` package; the D-40 ranges are four tuples instead.
- **Links are extracted only outside fences.** The scan toggles on the shared
  `markdown.FENCE` definition, so a sample link in a code block is not a document link.
- **Claim consistency is presence plus two tokens.** The checker proves the paragraph
  and the run claim exist; whether the run actually happened stays review-enforced
  (D-14, T-10-14). At most one `RPT-408` is emitted per defect.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task 1's verification selector needed `IdentityTests` in Task 1**
- **Found during:** Task 1
- **Issue:** Task 1's `<verify>` runs `-k identity`, but its `<files>` list omitted
  `scripts/tests/test_report.py`; without an `IdentityTests` class the selector would
  report `Ran 0 tests`.
- **Fix:** added `IdentityTests` (sixteen `test_identity_*` methods) in Task 1.
- **Files modified:** `scripts/tests/test_report.py`
- **Verification:** `python3 -m unittest scripts.tests.test_report -k identity -v` —
  16 tests, green.
- **Committed in:** `3fd5a96`

**2. [Rule 2 - Missing Critical] The compliant fixture grew to satisfy the new rules**
- **Found during:** Tasks 1 and 3
- **Issue:** the plan-10-03 fixture carried only `Homework ID`, `Title`, and
  `Implementation commit` in section 1; it had no `tests` or `simulation` block and no
  section-7 claim paragraphs. Once `RPT-402`, `RPT-403`, `RPT-407`, and `RPT-408`
  existed, every accepted fixture would fail for an unrelated reason.
- **Fix:** added the `Board`, `Framework`, `Language`, `PlatformIO Core`, `Platform`,
  `Homework status`, and `Report status` rows; extended `homework_yaml` with `native`
  and `simulation_status`; and added the `**Native suite.**` and `**Simulation.**`
  paragraphs to the section-7 body and the one manual section-7 fixture.
- **Files modified:** `scripts/tests/test_report.py`
- **Verification:** the full suite is green; each negative fixture fails only because
  of its single mutation.
- **Committed in:** `3fd5a96` (identity rows), `f02a4b1` (claim blocks and paragraphs)

**3. [Rule 3 - Blocking] Task 2's rule ids also needed `vocabulary.py` registration**
- **Found during:** Task 2
- **Issue:** Task 2's `<files>` list omitted `scripts/report/vocabulary.py`, but a rule
  that is not in `RULES` is not part of the stable contract the tests and the future
  `docs/standards/report.md` assert.
- **Fix:** registered `RPT-404`, `RPT-405`, and `RPT-406` with their summaries and
  remediations.
- **Files modified:** `scripts/report/vocabulary.py`
- **Verification:** the registry is complete; `ruff` is clean and the suite is green.
- **Committed in:** `df6a738` (and `RPT-407`/`RPT-408` in `f02a4b1`)

---

**Total deviations:** 3 auto-fixed (2 blocking, 1 missing critical).
**Impact on plan:** the rules are exactly as specified. The fixture grew because the
contract now consumes it; no rule was weakened to make the real tree pass.

## Issues Encountered

- The plan's verification text says the real tree exits 1 "only for the records plan
  10-06 fixes". The measured run reports exactly five expected records: `RPT-104`
  (missing `### Next Steps`), `RPT-201` (the live pin-map header `ESP32-S3 pin` vs
  `Pin`), and three `RPT-310` (REPORT-01, REPORT-05, REPORT-08). No `RPT-401`…`RPT-408`
  record appears. The checker is not weakened; the actual output is recorded below.

## User Setup Required

None — no external service configuration required.

## Verification

- `python3 -m unittest scripts.tests.test_report -k identity -v` — 16 tests, green.
- `python3 -m unittest scripts.tests.test_report -k language -v` — 8 tests, green.
- `python3 -m unittest scripts.tests.test_report -k status_claims -v` — 9 tests, green.
- `python3 -m unittest scripts.tests.test_report -k link -v` — 11 tests, green.
- `python3 -m unittest scripts.tests.test_report` — 120 tests, green.
- `python3 -m unittest discover scripts/tests` — 569 tests, `OK (skipped=1)`.
- `uv run ruff check` on every changed Python file — no issues.
- `uv run scripts/check_report.py` on the real tree — exit 1 with exactly five expected
  records: `RPT-104`, `RPT-201`, and three `RPT-310`. No identity, link, language,
  sentinel, or claim record.
- No commit bypassed the hooks; `ruff`, the secret scan, and the generated-file,
  generated-view, and skills-mirror gates passed on all three task commits.

## Next Phase Readiness

- The checker is feature-complete: `RPT-401`…`RPT-408` close REPORT-08's honest-status
  surface, and `docs/standards/report.md` (plan 10-07) can carry all eight
  remediations from `RULES`.
- Plan 10-05 (template parity) and 10-08 (gate wiring) can assert the full registry;
  plan 10-06 still owns the bounded 1.3 retrofit of the pin-map header,
  `### Next Steps`, and the three missing traceability rows.
- The real tree still intentionally fails `RPT-104`, `RPT-201`, and the three
  `RPT-310` records until plan 10-06.

## Self-Check: PASSED

- Modified files exist: `scripts/report/contract.py`, `scripts/report/tables.py`,
  `scripts/report/vocabulary.py`, `scripts/tests/test_report.py`.
- Commits exist on `worktree-agent-a663899b6fd2d0be5`: `3fd5a96`, `df6a738`, `f02a4b1`.
- Full suite: `Ran 569 tests — OK (skipped=1)`.

---
*Phase: 10-report-and-evidence-system*
*Completed: 2026-10-27*
