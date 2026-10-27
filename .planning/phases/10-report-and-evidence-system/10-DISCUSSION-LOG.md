# Phase 10: Report and Evidence System - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-27
**Phase:** 10-Report and Evidence System
**Areas discussed:** Checker shape, section applicability, gate severity, TOOL-08 scope,
self-audit follow-up

---

## Checker shape

| Option | Description | Selected |
|--------|-------------|----------|
| Standalone `scripts/check_report.py` | A deterministic checker with its own hook, sharing only the metadata helpers and record format | ✓ (via delegation) |
| Extend `scripts/check_metadata.py` | Fold report validation into the existing metadata checker | |
| Custom `markdownlint` rule | Reuse the pinned Node linter for the report structure | |

**User's choice:** All four areas selected, with "все up to you на основі бест практіс" —
the user delegated the decisions to Claude.

**Notes:** A standalone checker was chosen because the report contract needs structural
parsing plus `homework.yaml` and `assets/diagram.json` cross-checks, while the metadata
checker is a schema validator. A `markdownlint` rule was rejected because the pinned
linter is line-oriented and has no section-template or cross-file checks, and a Node rule
would add a second configuration surface. `scripts/report/` holds the stdlib-only helpers.

---

## Section applicability

| Option | Description | Selected |
|--------|-------------|----------|
| One uniform skeleton | All ten headings and six tables always present; inapplicability is `_Not applicable — <reason>._` | ✓ (via delegation) |
| Declare required sections in `homework.yaml` | A schema change listing the applicable sections and tables | |
| Infer from board, framework, tests, and simulation | No metadata; implicit rules | |

**User's choice:** Delegated to Claude.

**Notes:** The uniform skeleton was chosen for one doctype and one rule set. It avoids a
schema change, a second source of truth, and implicit inference, and it forces an explicit
reason for every inapplicable section. The research pass showed that type-specific
templates are common in docs-as-code, but this repository has one report doctype and a
deliberately minimal metadata schema, so a declared-applicability field would cost more
than it buys.

---

## Gate severity

| Option | Description | Selected |
|--------|-------------|----------|
| Always a blocker | Any `report.md` must satisfy the contract regardless of status | |
| Blocker at `draft` and `complete`; `placeholder` exempt | The scaffolded skeleton is exempt; authoring enforces the contract | ✓ (via delegation) |
| Advisory until Phase 11 | The checker reports but never blocks in this phase | |

**User's choice:** Delegated to Claude.

**Notes:** The status-gated model was chosen because the scaffold must be able to ship a
skeleton. `placeholder` is the only exemption; `draft` and `complete` enforce the whole
contract. Cross-status consistency is checked (`planned` → `placeholder`;
`complete`/`verified` → `complete`). The check is a merge gate from Phase 10, and the 1.3
report is retrofitted rather than grandfathered.

---

## TOOL-08 scope

| Option | Description | Selected |
|--------|-------------|----------|
| Full rubric plus `hw-report` promotion | A scored rubric and a real report-assembly skill | |
| Contract-derived checklist, `hw-report` stays a stub | A human checklist derived from the checker rule ids; promotion waits for Phase 11 | ✓ (via delegation) |
| Defer TOOL-08 again | Ship only the template, checker, and catalog | |

**User's choice:** Delegated to Claude.

**Notes:** TOOL-08's mapping is satisfied by a checklist derived from the checker's stable
rule ids, so the human checklist and the machine gate cannot drift. The scored rubric stays
deferred under its original "three real reports" condition. `hw-report` stays a stub
because FLOW-07 promotes a skill after its first real use, and the first use with the
standard in place is the Phase 11 pilot.

---

## Research notes

- Structural Markdown validation should parse structure rather than pattern-match source
  text; `markdownlint` has no built-in section-template support.
- Evidence practice separates provenance from uncertainty and records a
  claim → method → result → evidence → status chain.
- A lightweight pre-PR checklist derived from the contract is preferred over a heavy
  scored rubric; deterministic rules belong in CI, prose judgement in review.

## Self-audit follow-up (2026-10-27)

The user asked whether every gray area had been identified and requested a self-check with
research. The audit checked each proposed rule against the real 1.3 report. It found two
scoping defects in the recorded decisions and eight additional machine-checkable gaps:

- **C-1:** the `observed` label rule was document-wide; it is scoped to the ledger `Label`
  and `Value` cells because the 1.3 prose legitimately contains the word (lines 254, 295,
  352).
- **C-2:** the identity cross-check compared display prose; it now compares normalized
  machine values and leaves `Board`/`Language` as display text.
- **N-1:** N/A allowlist.
- **N-2:** `complete` semantics and the absence of a measured-value floor.
- **N-3:** cross-reference integrity for IDs and IEEE citations.
- **N-4:** claim consistency for tests, simulation, status, and toolchain.
- **N-5:** internal Markdown link integrity.
- **N-6:** evidence provenance depth per label.
- **N-7:** English-only Cyrillic scan for the report.
- **N-8:** traceability coverage for `REPORT-01`…`REPORT-08`.

**Research:** GUM Clause 7 and NIST TN 1297 (uncertainty reporting), NASA SWE-072, FAA
VRTM, and HHS EPLC (traceability completeness), alint and linklint (internal link
resolution), the IEEE Reference Guide and Citation-Cross-Checker (bidirectional citations).

**User's choice:** "Усі рекомендовані" — N-1…N-8 plus C-1/C-2 were folded into CONTEXT.md
as D-34…D-44.

## Claude's Discretion

- Rule-id numbering and message wording.
- The internal split of `scripts/report/`.
- Template sentinel wording, provided `placeholder` ignores it and `draft` rejects it.
- Self-audit checklist wording and ordering.
- Calculation catalog family names.
- The default invocation scope (all reports from the root; positional paths for focused
  runs).
- The path-likeness heuristic, provided it is documented and tested against the 1.3
  matrix.

## Deferred Ideas

- Scored self-audit rubric (after three real reports).
- `hw-report` promotion (Phase 11 pilot).
- Pin-map net-level validation against `diagram.json`.
- Calculation-catalog membership enforcement.
- A `markdownlint` custom rule or a `remark`/`mdast` dependency.
- Automatic decision-appendix cross-check against the friction log.
- ESP-IDF- or STM32-specific report variants.
- Report validation in the `affected.py` build matrix.
