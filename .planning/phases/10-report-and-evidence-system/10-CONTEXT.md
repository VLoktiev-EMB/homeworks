# Phase 10: Report and Evidence System - Context

**Gathered:** 2026-10-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Turn the homework report and its evidence into a checked contract. The phase delivers:

- `templates/report/report.md` — the full report skeleton: the ten numbered academic
  sections, the four hardware subsections, the two evidence subsections, the required
  table headers, and the evidence vocabulary.
- `scripts/check_report.py` plus the stdlib-only helpers under `scripts/report/` — the
  deterministic checker with stable rule ids and specific messages.
- `docs/standards/report.md` — the human-readable standard and the contract-derived
  self-audit checklist.
- `docs/standards/electrical-calculations.md` — the calculation selection catalog.
- The `check-report` pre-commit hook; CI needs no new job because `meta` runs the whole
  hook surface and `gate` aggregates it.
- `scripts/new_homework` composing `report.md` from the new template, with a `report`
  block in both homework templates.
- The retrofit of `homeworks/1_3-police-flasher/report.md` to the checked contract.
- The `AGENTS.md`, pull-request-template, decisions-table, and `hw-report` stub updates
  that point at the new contract.

**Requirements covered:** REPORT-01, REPORT-02, REPORT-03, REPORT-04, REPORT-05,
REPORT-06, REPORT-07, REPORT-08, TOOL-08.

**Friction-log justification:** F-07 (report must state the half-bridge fidelity limits),
F-11 (the bare template and the ambiguous heading block), F-12 (the evidence-label
vocabulary and the `not measured` reason), and F-13 (the hand-assembled traceability matrix
and missing artifact links). These four entries are the phase's owners.

**Explicitly not this phase:** `hw-report` promotion (Phase 11), the scored self-audit
rubric (after three real reports), pilot polish and the `hw/<id>` tag (Phase 11), a report
for an ESP-IDF or STM32 homework that does not exist yet, and any change to
`schema/homework.schema.json`.

</domain>

<decisions>
## Implementation Decisions

### Checker architecture and placement

- **D-01:** A standalone `scripts/check_report.py` owns the report contract;
  `scripts/check_metadata.py` keeps the metadata and provenance contract only. The report
  checker reads `homework.yaml`, `report.md`, and `assets/diagram.json`; folding this into
  the metadata checker would mix prose structure and cross-file evidence with the schema
  validator. — **Reversibility:** costly — the hook, the docs, the pull-request template,
  and the `hw-report` stub all name the command.
- **D-02:** Shared structural helpers live under `scripts/report/` (`markdown.py`,
  `tables.py`, `vocabulary.py`, `contract.py`), stdlib-only and mirroring the
  `scripts/metadata/` split. The stdlib-only rule keeps the existing test suite able to
  import the helpers without PyYAML or jsonschema.
- **D-03:** The parser is a structural ATX-heading and pipe-table parser that tracks fenced
  code blocks; it is not a regex sweep over the source, and no Markdown AST dependency is
  added. A custom `markdownlint` rule is rejected: the pinned linter is line-oriented, has
  no section-template or cross-file checks, and a Node rule would add a second config
  surface. The research pass supports AST/structural parsing over regex, and a bounded
  parser with fixtures satisfies that requirement without a new toolchain.
  — **Reversibility:** reversible — the parser can be replaced by `remark`/`mdast` later
  without changing the contract.
- **D-04:** The CLI mirrors `check_metadata.py`: `--dir`, `--json`, optional positional
  homework directories or report paths, `PATH: STATUS — reason` records, a `PASS`/`FAIL`
  summary, and exit codes 0/1/2. Every `ERROR` carries a stable rule id (for example
  `RPT-005`) and a line number, so a failure message is specific and the standard can map
  each rule to its checklist item. — **Reversibility:** costly — tests and documents assert
  the rule ids.
- **D-05:** One new local pre-commit hook `check-report` runs
  `python scripts/check_report.py`, with `pass_filenames: false` and a `files` pattern
  covering `homeworks/**/report.md`, `homeworks/**/homework.yaml`,
  `homeworks/**/assets/diagram.json`, `templates/report/`, `docs/standards/report.md`,
  `docs/standards/electrical-calculations.md`, `scripts/check_report.py`, and
  `scripts/report/`. The hook is check-only and never rewrites or stages. CI needs no new
  job: the `meta` job runs `pre-commit run --all-files`, and `gate` already aggregates
  `meta`. — **Reversibility:** reversible — the hook and its pattern are local.

### Section applicability and required structure

- **D-06:** Every report carries one uniform skeleton: all ten numbered headings and all
  six evidence tables are always present. A section or table that does not apply is
  replaced by the literal marker `_Not applicable — <reason>._`; it is never omitted and is
  never declared in metadata. Rationale: one doctype, one rule set; an explicit reason
  forces a justification; and the alternative — a schema flag or inference from
  board/framework — creates either a schema change and a second source of truth or
  implicit magic. — **Reversibility:** costly — every report and the template follow this
  shape.
- **D-07:** The literal heading contract is fixed:
  `## 1. Title and Metadata`, `## 2. Objective`, `## 3. Assumptions`, `## 4. Theory`,
  `## 5. Hardware and Wiring`, `## 6. Methodology`, `## 7. Results`, `## 8. Analysis`,
  `## 9. Conclusions`, `## 10. References`, and an optional `## Decision Appendix` after
  the references. The required subsections are `### Limitations` in section 4;
  `### Bill of Materials`, `### Pin Map`, `### Electrical Calculations`, and
  `### Safety Checklist` in section 5; `### Measurement Ledger` and
  `### Traceability Matrix` in section 7; and `### Next Steps` in section 9. Section 8 must
  contain at least one paragraph beginning `Industry note:`; section 9 must contain a
  paragraph beginning `Status:`.
- **D-08:** Table headers are fixed and shared: assumptions
  `ID | Assumption | Impact if wrong | Validation`; BOM
  `Ref | Part or value | Quantity | Package | Source or link | Notes`; pin map
  `Signal | Pin | Connects to | Notes`; calculations
  `ID | Quantity | Formula | Units | Input provenance | Result | Uncertainty | Assumption effect`;
  ledger
  `ID | Quantity | Value | Label | Instrument | Method | Uncertainty | Implementation commit`;
  traceability
  `ID | Claim or requirement | Design artifact | Verification method | Evidence | Status`.
  The same literals live in `scripts/report/vocabulary.py` and in the template, and a
  stdlib test asserts the template contains every one of them. — **Reversibility:** costly
  — every report table and the checker depend on the literals.
- **D-09:** Heading order is significant: the checker requires the ten numbered headings in
  ascending order with no duplicates. A table that does not apply is replaced by the N/A
  marker, never by an empty table. An N/A marker without a reason is an `ERROR`.

### Evidence and cross-file integrity

- **D-10:** The evidence vocabulary is exactly `measured`, `calculated`, `simulated`,
  `datasheet`, `not measured`, plus the single qualified form `measured (observed)`. A bare
  `observed` is an `ERROR`. A `not measured` value must begin `not measured:` with a
  reason; a `measured` value must begin `user-reported:` or `serial-log:`; a
  `measured (observed)` value must begin `serial-log:`. This locks Phase 7 and 04.2
  D-13/D-14 rather than re-opening them.
- **D-11:** Identity and commit consistency are machine-checked. The section-1 table's
  `Homework ID`, `Title`, `Board`, and `Framework` rows must equal `homework.yaml`; the
  `Implementation commit` cell must be a 7–40 character lowercase hex string and every
  ledger row's `Implementation commit` cell must be identical to it. A mismatch is an
  `ERROR`: a ledger that names a different code tree is not evidence for this report.
- **D-12:** BOM referential integrity is machine-checked when the BOM applies and
  `assets/diagram.json` exists: every BOM `Ref` must be a part id in the diagram. Extra
  diagram parts without a BOM row are allowed, because the diagram may include virtual
  instruments such as the serial monitor.
- **D-13:** Traceability artifact existence is machine-checked for `verified` and `manual`
  rows: every backticked token in `Design artifact` and `Evidence` that looks like a path
  (contains `/` or ends in a known code, document, or data extension) must resolve under
  the homework directory or the repository root. `pending` rows are exempt, because their
  named artifact may not exist yet. This is F-13's "link each row to an artifact that
  exists" made real.
- **D-14:** The checker validates structure and referential integrity, never semantic truth.
  It cannot decide whether a value was really measured; that remains a review duty. No LLM
  judging is introduced as a blocking gate, because a non-deterministic check is a poor
  gate and would weaken the "evidence before assertion" rule.
- **D-15:** Required-cell and shape rules: every assumption row has a non-empty
  `Impact if wrong` and `Validation`; every calculation row has a non-empty
  `Input provenance`, `Result`, `Uncertainty`, and `Assumption effect`; the safety
  checklist has at least one bullet and each bullet begins `- **` with a named hazard;
  section 10 has at least one IEEE-numbered entry matching `^\[[0-9]+\] `; the traceability
  `Status` cell is one of `verified`, `manual`, `pending`, or `not applicable`.
- **D-16:** A report that is `draft` or `complete` must contain no `TODO` or `TBD`
  sentinel; a sentinel is an `ERROR` with its line number. `placeholder` is exempt (D-18).
  This extends the repository's sentinel discipline from `task.md` to the report without
  changing the metadata checker.

### Gate severity and lifecycle

- **D-17:** `report.status: placeholder` is the only exemption from content checks: the
  file must exist and be non-empty, but its headings and tables are not validated.
  `draft` and `complete` enforce the full contract. Rationale: a scaffolded homework must
  be able to ship a skeleton, and the contract starts when authoring starts.
  — **Reversibility:** costly — every homework's `report.status` pair and the gate depend
  on this split.
- **D-18:** Cross-status consistency is enforced: `homework.yaml` `status: planned`
  requires `report.status: placeholder`; `in-progress` allows `draft` or `complete`;
  `complete` and `verified` require `report.status: complete`. An inconsistent pair is an
  `ERROR`.
- **D-19:** The check is a merge gate from Phase 10 onward, not advisory. It runs in the
  local hook, in `meta`, and through the `gate` fan-in. Definition of Done clause 4 changes
  from "guidance" to "the checked contract". `homeworks/1_3-police-flasher/report.md` is
  retrofitted in this phase — the pin-map header and the `### Next Steps` subsection are
  the expected small edits — rather than grandfathered, because a grandfather clause would
  make the contract decorative. — **Reversibility:** one-way — once the contract gates
  merges, weakening it is a policy reversal visible in every open pull request.
- **D-20:** There is no `--strict` or `--lenient` mode. One contract and one exemption
  (`placeholder`). A second mode invites the weaker one to become the default.

### Template and scaffold ownership

- **D-21:** `templates/report/report.md` becomes the full skeleton: the literal heading
  block, the required table headers, the N/A marker, the evidence vocabulary, and
  placeholder sentinel rows. It uses only the closed scaffold placeholders
  `{{homework_id}}`, `{{title}}`, `{{board}}`, `{{framework}}`, `{{platformio_version}}`,
  and `{{platform_version}}`; `${...}` is never used. — **Reversibility:** costly — the
  scaffold output and every new homework follow it.
- **D-22:** `scripts/new_homework` composes `report.md` from
  `templates/report/report.md`, exactly as it composes `templates/task/task.md`, and both
  `templates/homework-arduino/homework.yaml` and
  `templates/homework-espidf/homework.yaml` gain
  `report: {path: report.md, status: placeholder}`. Rationale: INV-03 and the Definition of
  Done require a report skeleton, but today the scaffold emits no `report.md`, so the
  default path does not produce a valid artifact set. — **Reversibility:** costly — the
  scaffold's golden file sets and rendered-output tests change.
- **D-23:** The template is not itself checked as a report (it contains placeholders). A
  stdlib test asserts that the template contains every literal heading and table header
  from `vocabulary.py`, so the template and the checker cannot drift.

### Calculation catalog

- **D-24:** `docs/standards/electrical-calculations.md` is an authored selection catalog:
  stable family ids, the formula, units, the expected input provenance, the uncertainty
  method, and the assumption sensitivity. It is a human selection aid, not a machine
  contract. The checker validates the calculation table's eight columns and the non-empty
  cells (D-15), not catalog membership, because membership enforcement would couple report
  wording to a growing catalog and create a second source of truth. REPORT-04's "used to
  select the relevant set" is a human step.

### Self-audit checklist and TOOL-08

- **D-25:** `docs/standards/report.md` is the human-readable standard: the contract, the
  rule ids, the applicability rule, the evidence vocabulary, the cross-file rules, and a
  self-audit checklist that maps each artifact — sections, BOM, calculations, safety,
  ledger, traceability, status, references — to a pre-pull-request checklist item. The
  checklist is derived from the checker's rule ids, so the human checklist and the machine
  gate share one source. This satisfies TOOL-08's mapping at a proportional level; the
  scored rubric remains deferred.
- **D-26:** `.github/pull_request_template.md` replaces "The report contains the sections
  that apply" with `uv run scripts/check_report.py` and adds a short report self-audit
  checklist (BOM rows trace to the diagram, labels are honest, the commit is consistent,
  limitations and next steps are stated).
- **D-27:** `hw-report` remains a stub through Phase 10. Its body is updated to point at
  `docs/standards/report.md` and `scripts/check_report.py`, and promotion is recorded as a
  Phase 11 candidate: the pilot is the first real use with the standard in place. Writing a
  report-assembly skill before that use would be speculative and would repeat the mistake
  FLOW-07's "promote after first real use" rule exists to prevent. Editing the canonical
  skill requires regenerating the `.agents/skills/` mirror with
  `uv run scripts/gen_skills.py`.
- **D-28:** TOOL-08's 2026-10-25 deferral note ("until the report system has three real
  uses") is resolved by D-25 only for the contract-derived checklist. The heavier scored
  rubric stays deferred, and the three-real-uses condition still governs it.

### Documentation and repository integration

- **D-29:** `AGENTS.md` gains a "Reports and evidence" rule block at
  `[MUST]`/`[ENFORCED: pre-commit]`, the agent quick-start gains
  `uv run scripts/check_report.py`, Definition of Done clause 4 is rewritten, the routing
  table points report structure at `docs/standards/report.md`, and the "Planned: report
  structure under `docs/standards/` (Phase 10)" line is removed.
- **D-30:** `docs/decisions/README.md` gains one row recording the checked-contract
  decision: a standalone deterministic checker, one uniform skeleton, a status-gated gate,
  and a checklist derived from the rule ids. No ADR file: the decision fits one row and
  the table is the default record.
- **D-31:** No schema change. `schema/homework.schema.json` already models
  `report.path` and `report.status`. The scaffold gains the block and the checker enforces
  its presence for a non-`planned` homework. A new field would be a schema change and is
  not needed.
- **D-32:** `scripts/affected.py` is unchanged. A `homeworks/**/report.md` change already
  selects that homework for a build, and the report check is a whole-tree `meta` concern,
  not a build-matrix concern.
- **D-33:** The phase gate is the repository quick-start: `pio run` for the affected
  environment, `pio test -d tests -e native`,
  `pre-commit run --all-files`, `uv run scripts/check_metadata.py`,
  `python3 -m unittest discover scripts/tests`, plus the new
  `uv run scripts/check_report.py` and a green `gate` on the pull request.

### Claude's Discretion

The user delegated all four gray areas to Claude on a best-practices basis. The following
remain implementation choices:

- Rule-id numbering and exact message wording.
- The internal split of `scripts/report/` and whether the parser returns a section tree or
  a flat heading list.
- The exact sentinel text in the template, provided `placeholder` ignores it and `draft`
  rejects it (D-16).
- The exact wording and ordering of the self-audit checklist.
- The number and naming of the calculation families in the catalog.
- Whether the manual invocation defaults to all reports or requires positional paths.
  Default: all reports from the repository root, positional paths for focused runs.
- The precise path-likeness heuristic in D-13, provided it is documented and tested
  against the 1.3 matrix.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements

- `.planning/ROADMAP.md` §Phase 10 — goal, success criteria 1–4, requirements, and the
  friction-log justification.
- `.planning/REQUIREMENTS.md` §Homework Artifacts and Reports — REPORT-01…REPORT-08;
  §Tooling and Quality — TOOL-08; and the Definition of Done clause 4 that this phase
  flips from guidance to gate.
- `.planning/PROJECT.md` §Key Decisions — the 10-section report row and the five semantic
  evidence labels; §Constraints — English artifacts, Ukrainian conversation.

### Locked prior decisions

- `.planning/phases/04.2-tracer-homework-1-3/04.2-CONTEXT.md` — D-11 (hybrid evidence),
  D-13 (five labels plus instrument, method, uncertainty, commit), D-14 (`measured
  (observed)`), D-15 (structurally complete but concise report and decision appendix).
- `.planning/phases/07-simulation-spike/07-CONTEXT.md` — the evidence vocabulary and the
  rule that simulation is never bench evidence.
- `.planning/phases/08-fast-ci/08-CONTEXT.md` — D-13 (the `meta` job runs the whole
  pre-commit surface) and D-2 (the literal `gate` fan-in).
- `.planning/phases/09-agent-workflow-and-skills/09-CONTEXT.md` — D-15 (ambiguity becomes a
  report assumption), D-19/D-20 (stub policy; `hw-report` stays a stub), and D-27's
  promotion trigger.
- `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md` — F-07, F-11, F-12, and
  F-13; §Top automation candidates maps them to Phase 10.

### Repository contracts and existing artifacts

- `AGENTS.md` — the canonical rulebook; the report rule, quick-start, Definition of Done,
  routing table, and planned-scope line are updated.
- `.github/pull_request_template.md` — the single Definition of Done that gains the checker
  command and the self-audit checklist.
- `.github/workflows/ci.yml` — the `meta` job that runs `pre-commit run --all-files` and
  the `gate` fan-in; no new job is added.
- `.pre-commit-config.yaml` — the pinned hook surface and the `check-metadata` hook whose
  shape the new `check-report` hook follows.
- `schema/homework.schema.json` — the `report` block (`path`, `status` enum
  `placeholder|draft|complete`); unchanged by this phase.
- `scripts/check_metadata.py` and `scripts/metadata/contract.py` — the record format, exit
  codes, path-safety helpers, and provenance rules the report checker mirrors.
- `scripts/metadata/render.py` — the closed `{{name}}` renderer and the refusal of
  `${...}` that the report template must obey.
- `scripts/metadata/paths.py` — the lexical path helpers reused for the report path and
  the artifact-existence check.
- `scripts/new_homework` — the all-or-nothing scaffold and the `task.md` composition
  pattern that `report.md` follows.
- `templates/report/report.md` — the six-line skeleton replaced by the full contract.
- `templates/homework-arduino/homework.yaml` and `templates/homework-espidf/homework.yaml`
  — the scaffolds that gain the `report` block.
- `homeworks/1_3-police-flasher/report.md` — the worked example and the retrofit target;
  its headings, table headers, evidence labels, and traceability rows are the reference
  shapes.
- `homeworks/1_3-police-flasher/homework.yaml` — `report.path: report.md`,
  `report.status: draft`, `status: in-progress`, and the identity values the checker
  cross-checks.
- `homeworks/1_3-police-flasher/assets/diagram.json` — the BOM referential-integrity
  source; part ids `esp`, `r1`, `led1`, `led2`, `r2`, `led3`, `btn1`.
- `docs/standards/vscode.md` — the precedent for an authored standard under
  `docs/standards/`.
- `docs/decisions/README.md` — the table-first decision index that gains one row.
- `.claude/skills/hw-report/SKILL.md` — the stub whose fallback is updated; the canonical
  tree is mirrored to `.agents/skills/` by `scripts/gen_skills.py`.
- `scripts/gen_skills.py` — the only writer of the skills mirror; a `hw-report` edit
  requires regeneration.
- `scripts/tests/` — the stdlib-only suite; `test_new_homework.py`,
  `test_homework_metadata.py`, and `test_gen_skills.py` are the tests affected by the
  scaffold, metadata, and mirror changes.

### Standards to create

- `docs/standards/report.md` — the contract, rule ids, applicability rule, evidence
  vocabulary, cross-file rules, and self-audit checklist.
- `docs/standards/electrical-calculations.md` — the calculation selection catalog.

### External references

- `https://github.com/hawkeyexl/doc-structure-lint` — structural Markdown/HTML validation
  against section templates; evidence for structural parsing over regex.
- `https://github.com/remarkjs/remark-lint` — AST-based Markdown linting and custom rules;
  the alternative considered and rejected for this phase.
- `https://github.com/DavidAnson/markdownlint` — the line-oriented linter already pinned;
  it has no section-template or cross-file checks.
- `https://www.w3.org/TR/prov-o/` — the W3C provenance model; the vocabulary separates
  provenance from uncertainty.
- `https://etisframework.org/assets/publications/white-papers/ETIS_WP-003_Engineering_Evidence.pdf`
  — the claim → method → result → evidence → disposition model.
- `https://github.com/voxmedia/open-agent-toolkit/blob/main/.agents/skills/authoring-docs/references/review-rubric.md`
  — a scored documentation rubric; the heavier alternative deferred here.
- `https://rulehub.github.io/rulehub/editorial-checklist/` — a lightweight pre-PR
  editorial checklist; the shape adopted for the self-audit checklist.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `scripts/check_metadata.py` — the CLI, the `_record` format, the `--json` payload, the
  summary line, and the exit-code contract are copied rather than reinvented.
- `scripts/metadata/contract.py` — the strict text loader, the ERROR/OK record shape, and
  the provenance validator the report checker composes with.
- `scripts/metadata/paths.py` — the lexical path-safety helpers for the report path and
  the artifact-existence check.
- `scripts/metadata/render.py` — the closed placeholder map and the `${...}` refusal; the
  report template uses the same vocabulary.
- `scripts/new_homework` — `_candidates` and `_mapping` show exactly how `task.md` is
  composed; `report.md` follows the same shape.
- `scripts/tests/` — the stdlib-only test harness and temp-root helpers; the report
  checker's fixtures belong here.
- `homeworks/1_3-police-flasher/report.md` — a complete worked example of every table and
  label; the template is its generalisation.

### Established Patterns

- Deterministic scripts print `PATH: STATUS — reason`, support `--json`, and exit 0/1/2.
- Hooks are check-only and never rewrite or stage (05/D-21).
- Tests never import `yaml` or `jsonschema`; they shell out to `uv run` (04/D-14).
- Template rendering is a single non-recursive `{{name}}` pass over a closed map; there is
  no Jinja and `${...}` is forbidden.
- `AGENTS.md` rules carry a severity and an enforcement point.
- Generated files are committed and drift-checked; the skills mirror is regenerated, never
  hand-edited.
- Prose and doc-sync tests were pruned in `261026-ky7`; a new guard should be behavioural,
  not a prose assertion about a document.

### Integration Points

- `.pre-commit-config.yaml` — the new `check-report` hook beside `check-metadata`.
- `.github/workflows/ci.yml` — the existing `meta` job; no new job and no new required
  check.
- `scripts/new_homework` — the new `report.md` composition and `REPORT_MD` constant.
- `templates/homework-arduino/homework.yaml` and
  `templates/homework-espidf/homework.yaml` — the `report` block.
- `templates/report/report.md` — the full skeleton.
- `homeworks/1_3-police-flasher/report.md` — the retrofit.
- `AGENTS.md` — the report rule block, quick-start, Definition of Done, routing table.
- `.github/pull_request_template.md` — the checker command and self-audit checklist.
- `docs/decisions/README.md` — one decision row.
- `.claude/skills/hw-report/SKILL.md` and `.agents/skills/hw-report/SKILL.md` — the stub
  pointer and the regenerated mirror.

</code_context>

<specifics>
## Specific Ideas

- The user delegated all four gray areas to Claude on a best-practices basis; the decisions
  above are the result and should be treated as locked.
- The user values honest evidence over impressive numbers: `not measured` is an acceptable
  and expected label, and a calculated value must never be relabelled as measured
  (04.2 `specifics`).
- F-11's literal heading block and F-12's label vocabulary were the two manual contracts
  that cost a second pass; both become machine-owned here.
- F-13's matrix was assembled by hand from six artifacts; the checker's artifact-existence
  rule is the direct answer.
- The report is a year-later artifact: a reviewer must be able to separate evidence from
  expectation without reading the session transcript.
- The checker must stay deterministic. Prose quality and whether a value was actually
  measured remain human review duties.
- Repository artifacts are English; the conversation is Ukrainian.
- `docs/standards/report.md` is the human entry point the `hw-report` stub already points
  at; publishing it lets the stub stop referring to a future phase.

</specifics>

<deferred>
## Deferred Ideas

- **Scored self-audit rubric** — after three real reports; TOOL-08's original deferral
  condition still governs the scored form. The contract-derived checklist ships now.
- **`hw-report` promotion** — Phase 11, after the pilot is the first real use with the
  standard in place.
- **Pin-map net-level validation against `diagram.json`** — the pin map's "Connects to"
  column is prose; net parsing is review-enforced for now.
- **Calculation-catalog membership enforcement** — the catalog remains a selection guide;
  machine membership would couple report wording to the catalog.
- **A `markdownlint` custom rule or a `remark`/`mdast` dependency** — rejected for this
  phase; revisit only if the structural parser proves insufficient.
- **Automatic decision-appendix cross-check against the friction log** — the appendix is
  optional and duplicates by design (F-13); a machine cross-check would add a fragile
  coupling.
- **ESP-IDF- or STM32-specific report variants** — no such homework exists; the uniform
  skeleton and the N/A marker cover them until one does.
- **Report validation in the `affected.py` build matrix** — the report check is a
  whole-tree `meta` concern; the build matrix is unchanged.

### Reviewed Todos (not folded)

- *Generate a root compile database so `lib/` has working IntelliSense* — resolved by
  Phase 06.1.
- *Remove the generated documentation site* — completed 2026-10-26.
- *Revisit Phase 8 scope before planning* — resolved by Phase 8.
- *Expand homework README and add a proper SVG schematic* — homework content; Phase 11.
- *Standardize pull request titles across homeworks* — folded into Phase 8.
- *Trim governance ceremony (Phase 4.1)* — completed in Phase 4.1.
- *Promote `merge_firmware.py` into a shared tool* — executed in Phase 7.

</deferred>

---

*Phase: 10-Report and Evidence System*
*Context gathered: 2026-10-27*
