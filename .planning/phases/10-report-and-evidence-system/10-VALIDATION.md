---
phase: "10"
slug: "report-and-evidence-system"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-27"
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` (no pytest, no third-party import in any test module) |
| **Config file** | none — discovery conventions only (`scripts/tests/test_*.py`) |
| **Quick run command** | `python3 -m unittest discover scripts/tests -p 'test_report.py' -v` |
| **Full suite command** | `python3 -m unittest discover scripts/tests` |
| **Checker smoke command** | `uv run scripts/check_report.py` |
| **Hook-level command** | `pre-commit run check-report --all-files` |
| **Estimated runtime** | ~15 seconds (quick), ~40 seconds (full) |

---

## Sampling Rate

- **After every task commit:** `python3 -m unittest discover scripts/tests -p 'test_report.py'` plus `uv run scripts/check_report.py`
- **After every plan wave:** `python3 -m unittest discover scripts/tests` and `pre-commit run --all-files`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 40 seconds

---

## Per-Task Verification Map

Per-task rows are seeded at requirement granularity; `/gsd-validate-phase` refines each
row to a concrete `{phase}-{plan}-{task}` id once plans exist.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 10-01-01 | TBD | 1 | REPORT-01 | — | Heading parse skips fenced code | unit | `python3 -m unittest scripts.tests.test_report -k headings` | ❌ W0 | ⬜ pending |
| 10-01-02 | TBD | 1 | REPORT-02 | T-10-01 | BOM `Ref` resolved lexically inside the homework dir | unit | `python3 -m unittest scripts.tests.test_report -k bom` | ❌ W0 | ⬜ pending |
| 10-01-03 | TBD | 1 | REPORT-03 | — | N/A marker requires a reason | unit | `python3 -m unittest scripts.tests.test_report -k pin_map` | ❌ W0 | ⬜ pending |
| 10-01-04 | TBD | 1 | REPORT-04 | — | Eight exact headers; four mandatory cells non-empty | unit | `python3 -m unittest scripts.tests.test_report -k calculations` | ❌ W0 | ⬜ pending |
| 10-01-05 | TBD | 1 | REPORT-05 | — | Safety bullets begin `- **` with a named hazard | unit | `python3 -m unittest scripts.tests.test_report -k safety` | ❌ W0 | ⬜ pending |
| 10-01-06 | TBD | 1 | REPORT-06 | T-10-02 | Ledger label enum; value prefixes; commit identity; duplicate-key YAML rejected | unit | `python3 -m unittest scripts.tests.test_report -k ledger` | ❌ W0 | ⬜ pending |
| 10-01-07 | TBD | 1 | REPORT-07 | T-10-01 | Traceability artifacts resolve and never escape repo root | unit | `python3 -m unittest scripts.tests.test_report -k traceability` | ❌ W0 | ⬜ pending |
| 10-01-08 | TBD | 1 | REPORT-08 | — | Status paragraphs present; `placeholder` exempt, `draft` rejects sentinels | unit | `python3 -m unittest scripts.tests.test_report -k status_claims` | ❌ W0 | ⬜ pending |
| 10-02-01 | TBD | 2 | TOOL-08 | — | Rule registry non-vacuous; every id in the standard | unit | `python3 -m unittest scripts.tests.test_report -k rule_registry` | ❌ W0 | ⬜ pending |
| 10-02-02 | TBD | 2 | Scaffold | — | Rendered `report.md` has no `{{`; file set matches | integration | `python3 -m unittest scripts.tests.test_new_homework -k report` | ✅ update | ⬜ pending |
| 10-03-01 | TBD | 3 | Hook wiring | — | `check-report` check-only, `pass_filenames: false`, `files` coverage | unit | `python3 -m unittest scripts.tests.test_tooling_config -k report` | ✅ update | ⬜ pending |
| 10-03-02 | TBD | 3 | Real tree | — | Checker exits 0 on the retrofitted repository | integration | `uv run scripts/check_report.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `scripts/report/__init__.py` — package marker (one-line docstring, mirroring `scripts/metadata/__init__.py`)
- [ ] `scripts/report/vocabulary.py`, `markdown.py`, `tables.py`, `contract.py` — stdlib-only
- [ ] `scripts/check_report.py` — the only PyYAML-aware module (PEP 723 header)
- [ ] `scripts/tests/test_report.py` — compliant fixture plus one negative fixture per rule, fence case, escaped-pipe case, wrapped-citation case, real-tree case
- [ ] No framework install needed: `unittest` is in the standard library

**Minimum fixture set:** compliant report; one missing data row in each of the three tables
named in success criterion 2; unknown ledger label; bare `observed`; `not measured` without
a reason; `TODO` in a `draft` report; heading inside a fence; out-of-order heading; duplicate
heading; missing required subsection; N/A without a reason; N/A in a forbidden position; BOM
ref absent from the diagram; broken relative link; unresolved `C-NN`; uncited reference;
citation to a missing reference; wrapped continuation line starting `[N]`; `REPORT-01`-free
matrix; identity mismatch per compared field; ledger commit mismatch; Cyrillic character;
`planned` homework with no report block; `in-progress` homework with
`report.status: placeholder` (must fail D-18).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Calculation catalog completeness | REPORT-04 | D-24 keeps catalog membership a human selection aid; machine membership would couple report wording to a growing catalog | Open `docs/standards/electrical-calculations.md`; confirm each family lists formula, units, input provenance, uncertainty method, assumption sensitivity |
| Whether a value was truly measured | REPORT-06 | D-14 forbids semantic judging; a non-deterministic check is a poor gate | Review each ledger row's `Label` against its `Instrument`/`Method` and the session evidence |
| Scored self-audit rubric | TOOL-08 | Deferred until three real reports exist (D-28) | Run the contract-derived checklist in `docs/standards/report.md`; rubric scoring out of scope |

*All other phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 40s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
