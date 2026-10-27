# Phase 10: Report and Evidence System - Research

**Researched:** 2026-10-27
**Domain:** Repository-internal deterministic tooling — a stdlib Markdown/report contract checker, a scaffold extension, a pre-commit hook, and two authored standards. No new external dependency, no network, no framework.
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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
- **D-10:** The evidence vocabulary is exactly `measured`, `calculated`, `simulated`,
  `datasheet`, `not measured`, plus the single qualified form `measured (observed)`. A bare
  `observed` is an `ERROR`. A `not measured` value must begin `not measured:` with a
  reason; a `measured` value must begin `user-reported:` or `serial-log:`; a
  `measured (observed)` value must begin `serial-log:`. This locks Phase 7 and 04.2
  D-13/D-14 rather than re-opening them. The vocabulary rules are scoped to the `Label`
  and `Value` cells of ledger rows only: prose elsewhere may legitimately contain the
  words `observed` or `not measured` (the worked example explains both), and a
  document-wide scan would false-positive on that prose.
- **D-11:** Identity and commit consistency are machine-checked against normalized
  machine values, never display prose. The H1 must equal `homework.yaml.title`; the
  section-1 `Homework ID`, `Title`, `Homework status`, and `Report status` cells must equal
  `id`, `title`, `status`, and `report.status`; `Framework` is compared case-insensitively;
  `PlatformIO Core` and `Platform` are compared after normalization (`espressif32@8.0.0`
  equals `platformio/espressif32 8.0.0`). `Board` and `Language` are display text and are
  not string-compared, because the worked example writes
  `ESP32-S3-DevKitC-1 (N16R8: 16 MB flash, 8 MB octal PSRAM)` against the metadata slug
  `esp32-s3-devkitc-1`. The `Implementation commit` cell must be a 7–40 character lowercase
  hex string and every ledger row's `Implementation commit` cell must be identical to it.
  A mismatch is an `ERROR`: a ledger that names a different code tree is not evidence for
  this report.
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
  default path does not produce a valid artifact set.
  — **Reversibility:** costly — the scaffold's golden file sets and rendered-output tests change.
- **D-23:** The template is not itself checked as a report (it contains placeholders). A
  stdlib test asserts that the template contains every literal heading and table header
  from `vocabulary.py`, so the template and the checker cannot drift.
- **D-24:** `docs/standards/electrical-calculations.md` is an authored selection catalog:
  stable family ids, the formula, units, the expected input provenance, the uncertainty
  method, and the assumption sensitivity. It is a human selection aid, not a machine
  contract. The checker validates the calculation table's eight columns and the non-empty
  cells (D-15), not catalog membership, because membership enforcement would couple report
  wording to a growing catalog and create a second source of truth. REPORT-04's "used to
  select the relevant set" is a human step.
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
- **D-34:** The `_Not applicable — <reason>._` marker is allowed only where the artifact
  can genuinely be absent. Sections 1, 2, 4, 6, 7, 8, 9, and 10 are never N/A; section 3
  may be N/A only with a reason; section 5 and its four subsections may be N/A for a
  software-only assignment; each required table must contain at least one data row or the
  marker. An N/A in a non-allowed position, or without a reason, is an `ERROR`.
- **D-35:** `report.status: complete` certifies that the report satisfies the checked
  contract and that every claim carries a label; it does **not** assert that a bench
  measurement exists. A report may be `complete` with `not measured` rows when the
  `Status:` paragraph states the evidence basis and the self-audit checklist confirms the
  honesty. There is no machine floor on `measured` rows, because the honest answer for a
  session without bench access is `not measured`, and a floor would pressure an author to
  relabel a calculation.
- **D-36:** Cross-reference integrity is machine-checked inside `report.md`. IDs must be
  unique within their table (`A-NN`, `C-NN`, `L-NN`, `T-NN`); every token matching one of
  those shapes must resolve to a row of that table, whether it appears in prose, another
  table, or a ledger method; every in-text `[N]` citation must resolve to a section-10
  entry, and every section-10 entry must be cited at least once in sections 1–9 or the
  appendix. An unresolved ID or citation is an `ERROR`.
- **D-37:** Claim consistency is machine-checked against `homework.yaml`. When
  `tests.native` is true, section 7 must contain a native-suite result paragraph; when a
  `simulation` block exists, section 7 must contain a `**Simulation.**` paragraph; when
  `simulation.status` is `verified`, that paragraph must state an executed-run outcome
  (`exited 0`, `scenario passed`, or equivalent), and when it is `pending`, the paragraph
  must not claim a run. The exact prose is review-enforced; the presence and the run-claim
  token are machine-checked.
- **D-38:** Internal link integrity is machine-checked: every relative Markdown link and
  image target in `report.md` must resolve under the homework directory or the repository
  root, and a target that escapes either root is an `ERROR`. External URLs are not fetched:
  third-party liveness is flaky and belongs to a scheduled audit, not a merge gate.
- **D-39:** Evidence provenance depth is machine-checked in the ledger: a `datasheet`
  row's `Method` or `Instrument` cell must contain a `[N]` citation; a `calculated` row
  must name a `C-NN` calculation; a `simulated` row must name a scenario or run artifact
  path; a `measured` row must name an instrument. The bounded token is the machine check;
  whether the cited source actually supports the value is review-enforced.
- **D-40:** `report.md` is English-only, and the Cyrillic scan that INV-01 already applies
  to `task.md` is extended to the report. Any Cyrillic codepoint in `report.md` is an
  `ERROR`. This closes the gap where the repository artifact rule was enforced only on the
  assignment paraphrase.
- **D-41:** The traceability matrix must cover every report requirement: at least one row
  must cite each of `REPORT-01` through `REPORT-08`. This follows the
  no-missing-relationships practice (NASA SWE-072, FAA VRTM) and makes the matrix auditable
  rather than illustrative. The 1.3 matrix needs three added rows (`REPORT-01`,
  `REPORT-05`, `REPORT-08`).
- **D-42:** Two standards are documented but not machine-enforced. Uncertainty follows a
  GUM-lite convention: each uncertainty cell states its basis (tolerance, meter accuracy,
  datasheet, or coverage) and, where an expanded uncertainty is claimed, the coverage
  factor or that the value is a tolerance bound; a bare `±` without a basis is discouraged
  in review. Instruments use a preferred vocabulary (`multimeter`, `oscilloscope`, `logic
  analyzer`, `power supply`, `thermal camera`, `Wokwi`, `none`), but a new instrument is
  allowed without a checker change. A keyword rule for either would be brittle and would
  fail legitimate prose.
- **D-43:** The status transition is a documented process, not a machine rule: the author
  flips `placeholder → draft` when authoring starts and `→ complete` when the self-audit
  checklist passes; Phase 11 flips the pilot to `complete` after the final evidence pass.
  `docs/standards/report.md` carries a rule-id remediation table, so every `RPT-…` failure
  names the fix as well as the defect.
- **D-44:** The 1.3 retrofit is bounded: change the pin-map header `ESP32-S3 pin` to `Pin`,
  add `### Next Steps` under `## 9. Conclusions`, and add three traceability rows for
  `REPORT-01`, `REPORT-05`, and `REPORT-08`. The report already passes the identity,
  citation, link, provenance, Cyrillic, toolchain, native-suite, and simulation checks
  under the normalized comparison.

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

### Deferred Ideas (OUT OF SCOPE)

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
- **A nightly run of `scripts/check_report.py`** — PR `meta` plus the required `gate`
  already cover every merge; nightly would add cost without a new trust boundary.
- **External link liveness** — third-party checks are flaky in a merge gate; schedule them
  only if the repository ever grows an external-link audit.
- **Commit reachability (`git cat-file`) for the implementation commit** — it needs
  `fetch-depth: 0` in `meta`; the hex-shape and ledger-consistency checks stay, and
  reachability is review-enforced.
- **Recomputing every calculation from its formula** — parsing arbitrary engineering
  formulas is fragile; the printed formula, inputs, and uncertainty stay review-enforced.
- **Report YAML frontmatter** — it would duplicate the section-1 metadata table, which is
  the canonical record.
- **A minimum prose depth or line count per section** — non-empty is machine-checked;
  depth and quality stay review-enforced.

### Reviewed Todos (not folded)

- *Generate a root compile database so `lib/` has working IntelliSense* — resolved by
  Phase 06.1.
- *Remove the generated documentation site* — completed 2026-10-26.
- *Revisit Phase 8 scope before planning* — resolved by Phase 8.
- *Expand homework README and add a proper SVG schematic* — homework content; Phase 11.
- *Standardize pull request titles across homeworks* — folded into Phase 8.
- *Trim governance ceremony (Phase 4.1)* — completed in Phase 4.1.
- *Promote `merge_firmware.py` into a shared tool* — executed in Phase 7.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REPORT-01 | 10-section academic report | D-07 literal heading block lives in `scripts/report/vocabulary.py`; the fence-aware heading scanner (§ "Structural parser") yields the section tree; order/duplicate/N-A rules are `RPT-1xx`. |
| REPORT-02 | BOM with ref, part/value, quantity, package, source/link, notes | D-08 BOM header constant; D-12 BOM `Ref` ↔ `assets/diagram.json` part-id check. The 1.3 diagram has exactly the seven ids `esp, r1, led1, led2, r2, led3, btn1` (`assets/diagram.json:5-58`), matching the seven BOM rows (`report.md:145-151`). |
| REPORT-03 | Pin map, `diagram.json` as wiring source of truth | D-08 pin-map header; the retrofit renames the live header (`report.md:155`). Net-level validation is explicitly deferred; the source-of-truth claim is review-enforced. |
| REPORT-04 | Calculations with formula, units, input provenance, result, uncertainty, assumption effect; catalog in `docs/standards/electrical-calculations.md` | D-08 eight-column header; D-15 non-empty cells; D-24 catalog is authored, not machine-checked. The live table already carries all eight columns (`report.md:174-181`). |
| REPORT-05 | Electrical safety checklist | D-15 bullet rule (`- **` with a named hazard); the live list satisfies it (`report.md:185-199`). |
| REPORT-06 | Measurement ledger with label, instrument, method, uncertainty, commit | D-10 vocabulary + value prefixes, D-11 commit identity, D-39 provenance depth. The live ledger uses `not measured`, `calculated`, `simulated`, `datasheet` only (`report.md:301-314`). |
| REPORT-07 | Traceability matrix: claim → design artifact → method → evidence → status | D-13 artifact existence, D-15 status enum, D-36 cross-references, D-41 `REPORT-01…08` coverage. Live matrix has 17 rows and is missing `REPORT-01`, `REPORT-05`, `REPORT-08`. |
| REPORT-08 | Honest status, verified board/toolchain, limitations, next steps | D-07 `### Limitations`, `Status:`, `### Next Steps`; D-11 identity/toolchain normalization; D-18 status consistency; D-37 native/simulation claim consistency. |
| TOOL-08 | Self-audit rubric mapping artifacts to the pre-PR checklist | D-25 `docs/standards/report.md` checklist derived from rule ids; D-26 PR-template edit; D-43 remediation table. |

</phase_requirements>

## Summary

Phase 10 is a repository-internal tooling phase, not a library-integration phase. Every
fact the planner needs is already in the tree: the CLI it must mirror, the record shape it
must extend, the module-boundary discipline it must preserve, the scaffold composition path
it must follow, the one real report it must retrofit, and the exact hooks and CI jobs that
carry the gate. There is no new dependency, no network access, no schema change, and no new
CI job. The research below is therefore mostly a precise map of existing code, plus a
verification of the D-44 claim that the 1.3 retrofit is bounded to three edits.

The highest-value findings are these. First, `check_metadata.py` and `scripts/metadata/*`
already establish every convention the new checker must copy — record shape, path helpers,
strict YAML loading, closed `{{name}}` rendering, import-boundary tests — and the split
between stdlib-only, PyYAML-only, and jsonschema-importing modules is load-bearing because
`python3 -m unittest discover scripts/tests` runs with no third-party packages installed.
Second, the scaffold's candidate composition is a four-point edit (`_candidates`,
`_build_plan`'s required set, two template manifests, and the test helpers that hard-code
"eight paths"), and `assert_matches_live_template` will fail with a `file set differs`
assertion the moment `report.md` is composed without updating the test's expected map.
Third, D-44's "bounded to three edits" claim is **verified against the file**, with one
caveat: the three new traceability rows must carry resolvable artifacts and a non-`pending`
status or they will fail D-13 trivially. Fourth, the live report already contains a
line that starts with `[1] ` inside a wrapped paragraph in section 8
(`report.md:370`), so a line-anchored reference-list parser is wrong — reference entries
must be scoped to the `## 10. References` section.

**Primary recommendation:** Copy `check_metadata.py`'s CLI and record shape literally, put
every literal string in `scripts/report/vocabulary.py` as the single source, keep
`scripts/report/*` stdlib-only and do the YAML read in the entry script, and make every
rule non-vacuous with a fixture that violates it. Then wire the hook, extend the scaffold,
retrofit 1.3, and update the four documentation surfaces.

## Architectural Responsibility Map

This is a single-tier repository-tooling phase; "tiers" here are the repository's own
layers, and the point of the table is to keep each responsibility in exactly one place.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Report contract definition (headings, headers, labels, marker) | `scripts/report/vocabulary.py` | `templates/report/report.md` | One Python constant set; the template is a projection of it, asserted by a parity test (D-08/D-23). |
| Structural Markdown parsing | `scripts/report/markdown.py` + `tables.py` | — | Stdlib only, fence-aware, no AST dependency (D-02/D-03). |
| Rule evaluation and records | `scripts/report/contract.py` | — | Pure functions over `(text, metadata dict, diagram dict)`; no I/O, importable under plain `python3`. |
| CLI, I/O, exit codes | `scripts/check_report.py` | — | The only module allowed to read files, load YAML, and touch `sys.exit` (mirrors `check_metadata.py`). |
| Cross-file integrity (identity, BOM, links, artifacts) | `scripts/check_report.py` (I/O) → `contract.py` (rules) | `scripts/metadata/paths.py` | Reuses `resolve_root`, `relative_path`; never re-validates the metadata schema. |
| Scaffold composition | `scripts/new_homework` | `templates/report/report.md` | Same `_candidates`/`_mapping`/`_build_plan` path as `task.md` (D-22). |
| Merge gate | `.pre-commit-config.yaml` → `meta` job → `gate` | — | No new CI job; the hook is the only new enforcement point (D-05). |
| Human standard / self-audit / catalog | `docs/standards/report.md`, `docs/standards/electrical-calculations.md` | `AGENTS.md`, PR template, decisions table | Authored prose; the checklist derives from rule ids (D-25). |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python (stdlib) | 3.11+ (repo runs 3.13.13) | Parser, rules, CLI, tests | `pathlib`, `re`, `json`, `argparse`, `unicodedata` cover the whole task; D-02/D-03 forbid a new dependency. |
| PyYAML | 6.0.3 | Read `homework.yaml` and `assets/diagram.json` companions | Already pinned in `check_metadata.py` and `new_homework` PEP 723 headers and in the `check-metadata` pre-commit hook [VERIFIED: scripts/check_metadata.py:3-4] [VERIFIED: .pre-commit-config.yaml:171-177]. |
| `scripts.metadata` helpers | in-repo | `resolve_root`, `relative_path`, `HOMEWORK_ID`, `StrictSafeLoader`, `CheckError`, `read_text`, `render` | Single implementation; re-exported by `contract.py` so the tool and the scaffold cannot drift [VERIFIED: scripts/metadata/paths.py:15-27] [VERIFIED: scripts/metadata/render.py:28-52]. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `uv` | 0.13.5 (observed) | Runs the entry script with its PEP 723 environment | `uv run scripts/check_report.py` in docs and local use. |
| `pre-commit` | 4.7.0 (pinned `minimum_pre_commit_version`) | Hosts the `check-report` hook | Hook definition only; no change to the pinned hook set. |
| `markdownlint-cli2` | v0.24.0 (pinned) | Lints the new authored Markdown | Applies automatically to `docs/standards/*.md` and `templates/report/report.md`. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Bounded stdlib parser (D-03) | `remark`/`mdast` or a `markdown-it-py` dependency | Correct AST, but a new toolchain plus a Node/Python config surface for a 500-line document; explicitly rejected (D-03, Deferred). |
| Custom `markdownlint` rule | A Node rule in the pinned linter | The linter is line-oriented and has no section-template or cross-file checks; would add a second config surface (D-03). |
| Standalone `check_report.py` (D-01) | Fold rules into `check_metadata.py` | Mixes prose structure and cross-file evidence with the schema validator; also forces jsonschema into the report path. |

**Installation:** none. No package is added. The only dependency declaration change is the
new entry script's PEP 723 header (`dependencies = ["PyYAML==6.0.3"]`) and the matching
`additional_dependencies` on the hook.

**Version verification:** PyYAML 6.0.3 and jsonschema 4.26.0 are the repository's pinned
pair [VERIFIED: scripts/check_metadata.py:3-4] [VERIFIED: .pre-commit-config.yaml:174]. The
report checker deliberately declares **PyYAML only**: it reads metadata values and never
re-validates the schema, so it must not import `scripts.metadata.contract`, which imports
jsonschema at module scope [VERIFIED: scripts/metadata/contract.py:50-51].

## Package Legitimacy Audit

**This phase installs no external package.** The only third-party import in the new code is
`yaml`, already a pinned, reviewed repository dependency with an existing hook
environment. No `package-legitimacy check` run is required; running one against an empty
addition set would produce no signal.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| PyYAML | PyPI | existing pin | — | github.com/yaml/pyyaml | OK (already reviewed in Phase 4) | Reused, not added |
| jsonschema | PyPI | existing pin | — | github.com/python-jsonschema/jsonschema | OK (already reviewed in Phase 4) | Not used by the new checker |

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

## Architecture Patterns

### System Architecture Diagram

```
                    repository root (resolve_root)
                              |
        +---------------------+----------------------+
        |                     |                      |
 homeworks/*/           templates/             docs/standards/
        |                     |                      |
        v                     |                      |
 check_report.py  <-----------+ (parity test only)   |
   |        |        |                               |
   |        |        +--> vocabulary literals <------+  (report.md checklist
   |        |                                             names rule ids)
   |        |
   |        +--> homework.yaml  --(StrictSafeLoader)--> metadata dict
   |        |                                            (no schema re-validation)
   |        +--> report.md      --(fence-aware scan)--> headings + sections
   |        |                                |
   |        |                                +--> pipe tables --> rows/cells
   |        |                                |
   |        +--> assets/diagram.json --(json)--> part ids
   |
   v
 records [{path, status, rule, line, reason}]
   |
   +--> stdout "PATH: STATUS — reason"  +  "PASS:/FAIL:" summary   -> exit 0/1
   +--> --json array                                                 -> exit 0/1
   +--> CheckError on stderr                                         -> exit 2

 Enforcement fan-out:
   .pre-commit-config.yaml  check-report (pass_filenames: false)
        -> local: pre-commit run --all-files
        -> CI meta job: pre-commit run --all-files --show-diff-on-failure
        -> CI gate job: aggregates meta (unchanged)
```

The primary use case traces as: an author edits `homeworks/<id>/report.md` → the hook fires
(the `files` pattern matches) → the checker locates every homework, reads three files,
parses prose into a section tree, evaluates rules, and prints one line per violation with a
rule id and line number → `meta` fails → `gate` fails. There is no other path.

### Pattern 1: CLI mirror — copy, do not reinvent

**What:** `check_metadata.py` defines the repository's checker contract: argparse with
`--dir` / `--json` / variadic `PATH`, a `_record(root, path, status, reason, line)` helper
that renders a repository-relative POSIX path, sorted output, a blank line, then
`FAIL: N … violation(s)` and exit 1 or `PASS: … satisfied` and exit 0; `CheckError` on
stderr and exit 2.

**When to use:** The report checker must reproduce this exactly (D-04), adding `rule` to
the record.

**Example (existing, verbatim):**

```python
def _record(root, path, status, reason, line=0):
    """Render one record with a repository-relative POSIX path."""
    return {
        "path": relative_path(root, path),
        "status": status,
        "reason": reason,
        "line": line,
    }
```

Source: `scripts/check_metadata.py:68-75` [VERIFIED: scripts/check_metadata.py:68-75]

The summary and JSON branches are at `scripts/check_metadata.py:354-377`
[VERIFIED: scripts/check_metadata.py:354-377]. Note two deliberate deviations the planner
must decide and pin:

1. `check_metadata.py` prints `line` **only** inside some reason strings and **drops** it
   from `--json` (`payload` maps `path`/`status`/`reason` only)
   [VERIFIED: scripts/check_metadata.py:357-367]. D-04 requires a line number per ERROR,
   so the report checker should carry `rule` and `line` in both text and JSON and assert
   that shape in a test.
2. `check_metadata.py` sorts by `path` only [VERIFIED: scripts/check_metadata.py:354];
   the report checker should sort by `(path, line, rule)` so two errors on one file print
   in reading order deterministically.

### Pattern 2: fence-aware structural parse, then rules

**What:** one linear scan producing `Heading(level, text, line)` and `Table(header, rows,
line)` records; a second pass that groups headings into sections and evaluates rules over
the structured result. D-03 forbids a regex sweep and an AST dependency.

**When to use:** all structure rules.

**Sketch the planner can put in a task action:**

```python
FENCE = re.compile(r"^\s*(```|~~~)")

def scan(lines):
    """Yield headings and table blocks; skip every line inside a fence."""
    in_fence = False
    for number, line in enumerate(lines, start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = ATX.match(line)          # ^(#{1,6})\s+(.*?)\s*#*\s*$
        if heading:
            yield ("heading", number, heading.group(1), heading.group(2))
            continue
        if line.lstrip().startswith("|"):
            yield ("row", number, line)
```

Critical detail: the fence toggle must run **before** the heading test, and the line
counter must increment even for skipped lines, or every reported line number after the
first fence is wrong.

### Pattern 3: one literal vocabulary, two projections

**What:** `scripts/report/vocabulary.py` holds `H1`-independent constants: the ten heading
strings, the seven subsection strings, the six-plus-one table header tuples, the evidence
label set, the `N/A` marker prefix, the status enums. The template contains the same
strings; a stdlib test asserts containment both ways.

**When to use:** D-08/D-23.

**Example (shape, not final text):**

```python
REPORT_HEADINGS = (
    "1. Title and Metadata", "2. Objective", "3. Assumptions", "4. Theory",
    "5. Hardware and Wiring", "6. Methodology", "7. Results", "8. Analysis",
    "9. Conclusions", "10. References",
)
LEDGER_HEADER = (
    "ID", "Quantity", "Value", "Label", "Instrument", "Method",
    "Uncertainty", "Implementation commit",
)
NOT_APPLICABLE = "_Not applicable — "
EVIDENCE_LABELS = frozenset(
    {"measured", "calculated", "simulated", "datasheet", "not measured",
     "measured (observed)"}
)
```

The headings are locked verbatim by D-07, the headers by D-08, the labels by D-10, and the
marker by D-06/D-34 — the research restates them only to fix their home.

### Pattern 4: preserve the import-boundary ladder

**What:** the repository has three module classes, and tests police them by AST-parsing the
source rather than importing it:

- stdlib-only: `scripts/metadata/{render,paths,platformio}.py`
- PyYAML-only: `scripts/metadata/yaml_loader.py`
- validation stack: `scripts/metadata/contract.py` (PyYAML + jsonschema)

**Why it matters here:** `python3 -m unittest discover scripts/tests` (AGENTS step 5, the
`python-tests` CI job) runs with **no third-party package installed**, so every module a
test imports must be stdlib-only. The existing guard is
`ModuleBoundaryTests` with `STDLIB_ONLY_MODULES` / `PYYAML_ONLY_MODULES` and an
`_import_roots` AST helper [VERIFIED: scripts/tests/test_new_homework.py:676-716]
[VERIFIED: scripts/tests/test_new_homework.py:763-775].

**Consequence the planner must encode:** `scripts/report/{markdown,tables,vocabulary,
contract}.py` are stdlib-only, and the `homework.yaml` read happens **in
`scripts/check_report.py`**, which is the only module with a PyYAML PEP 723 header. If
`scripts/report/contract.py` imports `yaml`, `test_report.py` cannot import it under plain
`python3` and the suite fails at discovery.

### Pattern 5: scaffold composition is a fixed four-point edit

**What:** `new_homework` computes every rendered file in memory, classifies every target,
validates the candidate, prints, then writes.

**When to use:** adding `report.md` (D-22).

**Exact points:**

```python
TASK_MD = "task.md"
TASK_TEMPLATE = Path("templates") / "task" / TASK_MD
```
[VERIFIED: scripts/new_homework:86-87]

`_candidates` appends the task template after the template tree, refuses a symlink, refuses
a missing file, and rejects a duplicate target [VERIFIED: scripts/new_homework:205-229].
`_mapping` builds the closed six-key map [VERIFIED: scripts/new_homework:232-242]. The
required-set check is:

```python
for required in (HOMEWORK_YAML, TASK_MD):
    if required not in rendered:
        raise CheckError(f"the candidate set provides no {required}")
```
[VERIFIED: scripts/new_homework:395-397]

So the edit is: two constants (`REPORT_MD`, `REPORT_TEMPLATE`), one appended candidate,
one extra entry in the required tuple, and one extra key in the template manifests.

### Pattern 6: negative fixtures per rule (non-vacuity)

**What:** every rule id is exercised by a fixture that violates exactly it, and a compliant
fixture returns zero records. The metadata suite's `FixtureBase` is the precedent: a temp
root with `schema/` and `platformio.shared.ini` copied in, one `write_homework` helper, and
`assert_accepted` / `assert_rejected` / `assert_environment_error`
[VERIFIED: scripts/tests/test_homework_metadata.py:199-253].

**When to use:** the whole `test_report.py`.

### Anti-Patterns to Avoid

- **Regex-sweeping the source.** Fenced code, escaped pipes, and the section-8 line that
  starts with `[1] ` all defeat line-anchored regexes (D-03, Pitfall 1 below).
- **Document-wide vocabulary scanning.** The live report's prose contains `observed` and
  `not measured` outside the ledger; a global scan false-positives (D-10, and the report
  itself explains why at `report.md:293-299`) [VERIFIED: homeworks/1_3-police-flasher/report.md:293-299].
- **Requiring subsection order inside a section.** Section 7 carries an extra
  `### Interpreting the Forward-Voltage Row` between the two required subsections
  [VERIFIED: homeworks/1_3-police-flasher/report.md:316]; a strict "first child" rule fails
  a compliant report.
- **Re-validating the metadata schema in the report checker.** It duplicates work, drags
  jsonschema into the hook environment, and turns a metadata defect into two reports.
- **Storing a golden scaffold tree.** Phase 06.1/`261026-x78` replaced stored fixtures with
  property assertions against the live template; a new stored `report.md` copy would reverse
  that decision.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Repository root discovery | `Path.cwd()` or a relative-path guess | `scripts.metadata.paths.resolve_root` | Handles `--dir`, `git rev-parse`, symlinked roots; already the contract [VERIFIED: scripts/metadata/paths.py:30-47]. |
| Repo-relative display paths | string slicing | `scripts.metadata.paths.relative_path` | Resolves both sides and degrades to a basename outside the root [VERIFIED: scripts/metadata/paths.py:50-60]. |
| YAML loading | `yaml.safe_load` | `StrictSafeLoader` | Rejects duplicated keys that PyYAML would silently overwrite [VERIFIED: scripts/metadata/yaml_loader.py:26-60]. |
| Template substitution | `str.replace` loops or Jinja | `scripts.metadata.render.render` | One non-recursive pass, closed map, refuses `${...}` [VERIFIED: scripts/metadata/render.py:32-52]. |
| Homework ID validation | a second regex | `scripts.metadata.paths.HOMEWORK_ID` | One literal shared by schema, checker, and docs [VERIFIED: scripts/metadata/paths.py:27]. |
| Exit-code/record vocabulary | a new shape | `check_metadata.py`'s record + `CheckError` | The repository documents and tests this vocabulary; a second one is a second contract. |
| Import-boundary enforcement | trust | the `_import_roots` AST pattern | Already proven; a real import in a test would fail under plain `python3` only at runtime. |
| Markdown AST | a hand-rolled CommonMark parser | a bounded ATX + pipe-table scanner | The contract needs headings and tables only; full CommonMark is out of scope and D-03 bounds it. |

**Key insight:** almost every infrastructure sub-problem here has exactly one existing
implementation in `scripts/metadata/`. The only genuinely new work is the Markdown
structure scanner and the rule set; everything else is composition.

## Existing Contracts to Mirror

### `scripts/check_metadata.py` — the CLI contract

| Contract point | Exact behaviour | Where |
|---|---|---|
| Entry shebang | `#!/usr/bin/env -S uv run --script` | `check_metadata.py:1` |
| PEP 723 header | `requires-python = ">=3.11"`, `dependencies = ["PyYAML==6.0.3", "jsonschema==4.26.0"]` | `check_metadata.py:2-5` |
| Path bootstrap | `sys.path.insert(0, str(Path(__file__).resolve().parent.parent))` | `check_metadata.py:51` |
| Flags | `--dir PATH`, `--json`, variadic `paths` | `check_metadata.py:309-331` |
| Exit 0 | every record is `OK`; prints `PASS: metadata contract satisfied` | `check_metadata.py:376-377` |
| Exit 1 | at least one `ERROR` record; prints `FAIL: N metadata violation(s)` | `check_metadata.py:373-375` |
| Exit 2 | `CheckError` → `ERROR: <msg>` on **stderr**, no stdout records | `check_metadata.py:350-352` |
| Content vs environment | a bad document payload is exit 1; only a broken environment is exit 2 | `check_metadata.py:19-28` (docstring) |
| Record shape | `{"path", "status", "reason", "line"}` where `status` is `OK`/`ERROR` | `contract.py:501-502` |
| Text output | `f"{record['path']}: {record['status']} — {record['reason']}"`, then a blank line | `check_metadata.py:369-371` |
| JSON output | one array of `{"path","status","reason"}`, **no** summary line, **no** `line` | `check_metadata.py:357-367` |
| Determinism | sorted by `path`; no clock, no writes, byte-identical consecutive runs | `check_metadata.py:37-40`, `:354` |
| Positional handling | a file positional is reduced to its parent directory; a non-directory is exit 2 | `check_metadata.py:158-194` |
| Default scope | with no positionals, every direct child directory of `homeworks/` | `check_metadata.py:179-189` |
| Missing document | a directory with neither contract file is an `ERROR` on the directory path, never a silent skip | `check_metadata.py:106-114` |
| Decode failure | `UnicodeDecodeError` is a content `ERROR`; `OSError` is exit 2 | `check_metadata.py:78-91` |
| Size cap | `MAX_INPUT_BYTES = 64 * 1024` | `contract.py:80` |

Two consequences for the report checker:

- **Reuse `_directories`' semantics** for positionals, because D-04 says positional
  "homework directories or report paths". A report path positional must reduce to its
  homework directory the same way `homework.yaml` does.
- **Decide the size cap deliberately.** The live 1.3 report is **42,344 bytes** (496 lines)
  — under 64 KiB, but only ~1.5× headroom. A report that grows past 64 KiB would fail for
  a reason unrelated to the contract. Recommend a separate, larger constant for reports
  (for example 1 MiB) or no cap at all, and document the choice.

### The `scripts/metadata/` module ladder

| Module | May import | Re-exported by `contract.py` | Use from the report checker |
|---|---|---|---|
| `errors.py` | stdlib only | `CheckError` | yes — the shared exit-2 exception |
| `paths.py` | stdlib only | `HOMEWORK_ID`, `derive_parts`, `relative_path`, `resolve_root` | yes — root, display paths, id shape |
| `render.py` | `os`, `re`, `stat`, `CheckError` | not re-exported | only the parity/read helpers if needed |
| `yaml_loader.py` | `yaml` + stdlib | `StrictSafeLoader` | yes — inside `check_report.py` only |
| `contract.py` | `yaml` + `jsonschema` + the above | — | **no** — would drag jsonschema into the hook and the test import graph |

Evidence: `contract.py` imports `yaml` and `Draft202012Validator` at module scope
[VERIFIED: scripts/metadata/contract.py:50-51]; `paths.py` is stdlib-only and documents why
it was split out [VERIFIED: scripts/metadata/paths.py:1-27]; `render.py` imports only `os`,
`re`, `stat` and `CheckError` [VERIFIED: scripts/metadata/render.py:18-24];
`yaml_loader.py` imports `yaml` and nothing third-party [VERIFIED: scripts/metadata/yaml_loader.py:11-13].

### The reader it needs from `homework.yaml`

The fields the contract cross-checks are all present on the live document: `id`, `title`,
`board`, `framework`, `language`, `status`, `toolchain.platformio`, `toolchain.platform`,
`simulation.status`, `tests.native`, `report.path`, `report.status`
[VERIFIED: homeworks/1_3-police-flasher/homework.yaml:1-27]. The schema's `report` block
requires `path` and `status` and allows only the three statuses
[VERIFIED: schema/homework.schema.json:80-91]:

```
    "report": {
      "type": "object",
      "additionalProperties": false,
      "required": ["path", "status"],
      "properties": {
        "path": {
          "type": "string",
          "pattern": "^(?!/)(?!.*(?:^|/)\\.\\.(?:/|$))(?!.*\\\\)[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*$"
        },
        "status": { "enum": ["placeholder", "draft", "complete"] }
      }
    }
```

`report` is **not** in the root `required` list — the root requires exactly
`["schema_version","id","title","board","framework","language","status","source","toolchain"]`
[VERIFIED: schema/homework.schema.json:6-16], and the `status` enum is
`["planned","in-progress","complete","verified"]` [VERIFIED: schema/homework.schema.json:24].
That absence is exactly why D-31 says the *report* checker enforces `report` presence for a
non-`planned` homework rather than the schema.

## Scaffold: the exact composition surface

The scaffold today emits nine plan records for the Arduino template (`.clangd`,
`README.md`, `assets/.gitkeep`, `homework.yaml`, `include/.gitkeep`, `platformio.ini`,
`src/main.cpp`, `task.md`, `test/test_homework/test_homework.c`); `report.md` would be the
tenth. Observed by `uv run scripts/new_homework 9_9-fixture --template arduino --dry-run`
in this session.

The production path is [VERIFIED: scripts/new_homework:205-242] [VERIFIED: scripts/new_homework:379-415]:

```python
def _candidates(root, template_dir):
    candidates = _template_files(template_dir)
    task_template = root / TASK_TEMPLATE
    if task_template.is_symlink():
        raise CheckError("templates/task/task.md is a symlink; refusing to follow it")
    if not task_template.is_file():
        raise CheckError("missing templates/task/task.md")
    candidates.append((Path(TASK_MD), task_template))
    ...
```

and

```python
def _mapping(root, homework_id, manifest):
    parts = derive_parts(homework_id)
    return {
        "homework_id": homework_id,
        "title": parts["title"],
        "framework": manifest["framework"].strip(),
        "board": BOARD,
        "platformio_version": PLATFORMIO_CORE,
        "platform_version": read_shared_platform_pin(root),
    }
```

Both templates currently **lack** a `report` block — the Arduino and ESP-IDF
`homework.yaml` both end at `tests:` [VERIFIED: templates/homework-arduino/homework.yaml:1-17]
[VERIFIED: templates/homework-espidf/homework.yaml:1-17]. So D-22's `report:` addition is a
real change, not a re-statement.

**Edits required, and the tests that will fail if one is missed:**

| Edit | File | Test that catches the omission |
|---|---|---|
| `REPORT_MD` / `REPORT_TEMPLATE` constants | `scripts/new_homework:86-87` | `TemplateParityTests` — `file set differs` |
| Append the report candidate with symlink/missing checks | `_candidates` | a new negative test; without it `_build_plan` raises "provides no report.md" |
| Add `REPORT_MD` to the required tuple | `_build_plan:395` | every scaffold test |
| `report: {path: report.md, status: placeholder}` | both `templates/homework-*/homework.yaml` | `test_rendered_homework_yaml_carries_title_and_status` does not assert it today — add an assertion |
| Expected map gains `report.md` | `assert_matches_live_template` [VERIFIED: scripts/tests/test_new_homework.py:140-177] | `file set differs` |
| `SHARED_PATHS` / `eight_paths` gains `report.md` | [VERIFIED: scripts/tests/test_new_homework.py:40-57] | `InventoryTests` and `test_fresh_root_creates_nested_parents` would still pass but would stop covering the new file — a vacuity risk, not a failure |
| `authored_template_files` skip rules | [VERIFIED: scripts/tests/test_new_homework.py:60-88] | none — `report.md` is a normal template file |

Note the vacuity trap: `eight_paths()` is a hand-maintained tuple, so adding `report.md` to
the scaffold without adding it there produces **green tests that no longer assert the new
path**. The plan should include an explicit edit plus a rename (`declared_paths`) so the
name stops lying.

## Retrofit Audit: `homeworks/1_3-police-flasher/report.md`

D-44 claims the retrofit is bounded to three edits. Verified against the file, **the claim
holds**, with one caveat about the new rows.

| Contract item | Live state | Verdict | Retrofit action |
|---|---|---|---|
| H1 equals `homework.yaml.title` | `# Police Flasher` vs `title: "Police Flasher"` | pass | none |
| Ten headings, ascending, exact text | `## 1.` … `## 10.` all present and exact | pass | none |
| `### Limitations` in section 4 | present at line 115 | pass | none |
| `### Bill of Materials` | line 141, header `Ref | Part or value | Quantity | Package | Source or link | Notes` | pass | none |
| `### Pin Map` header | line 155 is `| Signal | ESP32-S3 pin | Connects to | Notes |` | **FAIL** | rename `ESP32-S3 pin` → `Pin` (edit 1) |
| `### Electrical Calculations` | line 166, eight columns exactly | pass | none |
| `### Safety Checklist` | lines 185-199, every bullet `- **Hazard.**` | pass | none |
| `### Measurement Ledger` | line 291, eight columns exactly | pass | none |
| `### Traceability Matrix` | line 327, six columns exactly | pass | none |
| `### Next Steps` in section 9 | absent — section 9 ends after the `Status:` paragraph and section 10 begins at 438 | **FAIL** | add the subsection (edit 2) |
| Section 8 `Industry note:` | three paragraphs begin `Industry note:` (lines 389, 395, 402) | pass | none |
| Section 9 `Status:` | line 430 begins `Status:` | pass | none |
| Identity cells | `Homework ID`, `Title`, `Homework status` `in-progress`, `Report status` `draft`, `Framework` `Arduino`, `PlatformIO Core` `6.2.0`, `Platform` `` `platformio/espressif32` 8.0.0 `` | pass under normalization | none |
| Implementation commit | `9e1238d` in the metadata row (line 19) and in all twelve ledger rows | pass | none |
| Ledger labels | `not measured` (7), `calculated` (3), `simulated` (1), `datasheet` (1); no `measured`, no bare `observed` | pass | none |
| `not measured:` reason prefix | every `not measured` value begins `not measured: bench equipment offline …` | pass | none |
| BOM refs ↔ diagram part ids | BOM: `esp, r1, led1, led2, r2, led3, btn1`; diagram parts: the same seven ids | pass | none |
| Traceability artifact existence | all backticked path-like tokens in `Design artifact`/`Evidence` resolve (probe run this session) | pass | none |
| Cross-references `A-/C-/L-/T-NN` | 8 + 6 + 12 + 17 ids, all unique, zero unresolved tokens | pass | none |
| IEEE citations | `[1]`–`[6]` defined in section 10; all six cited in sections 1-9 | pass | none |
| `REPORT-NN` coverage | `REPORT-02, 03, 04, 06, 07` only | **FAIL** | add three rows (edit 3) |
| Internal links | both `[assets/diagram.json](assets/diagram.json)` targets exist | pass | none |
| Cyrillic | zero hits | pass | none |
| `TODO`/`TBD` sentinel | zero hits | pass | none |
| Native-suite / simulation claim | `**Native suite.**` and `**Simulation.**` paragraphs both present; simulation says "all three counted runs exited 0" | pass | none |

The caveat on edit 3: D-13 exempts only `pending` rows, and D-19 forbids grandfathering, so
the three new rows must name artifacts that exist and must not be `pending` merely to dodge
the check. A defensible shape is `verified` with `scripts/check_report.py` or the relevant
report section as the `Design artifact`, and `Status` `verified`/`manual` as appropriate.
The new ids must be appended as `T-18`, `T-19`, `T-20` to keep D-36 uniqueness.

One more measured fact: the file is 496 lines / 42,344 bytes, and it contains **no escaped
pipes** (`\|`) today. The table parser must still support them, but no retrofit edit is
needed for them.

## Hook and CI Wiring

The `check-metadata` hook is the exact shape to copy
[VERIFIED: .pre-commit-config.yaml:171-178]:

```yaml
      - id: check-metadata
        name: homework metadata contract
        language: python
        additional_dependencies: ["PyYAML==6.0.3", "jsonschema==4.26.0"]
        entry: python scripts/check_metadata.py
        files: ^(homeworks/|boards/|schema/|scripts/(check_metadata\.py|new_homework$|gen_views\.py$|metadata/))
        pass_filenames: false
        stages: [pre-commit]
```

For `check-report`, the research recommends:

```yaml
      - id: check-report
        name: report and evidence contract
        language: python
        additional_dependencies: ["PyYAML==6.0.3"]
        entry: python scripts/check_report.py
        files: (?x)^(homeworks/.*/(report\.md|homework\.yaml|assets/diagram\.json)$|templates/report/|docs/standards/(report|electrical-calculations)\.md$|scripts/(check_report\.py|report/))
        pass_filenames: false
        stages: [pre-commit]
```

Notes that matter:

- `language: python` builds a pre-commit-managed environment; it must **not** need
  jsonschema, hence the PyYAML-only import rule above.
- The `(?x)` free-spacing flag and folding are the repository's established trick for a
  long pattern in YAML [VERIFIED: .pre-commit-config.yaml:204-209].
- The hook belongs in the same `repo: local` block as `check-metadata` (or a new one —
  pre-commit runs repositories in file order, so either works; adjacency is clearer).
- `pass_filenames: false` plus a whole-tree scan means the hook checks **every** homework,
  so a stale report anywhere fails a pull request that touches none of them. That is the
  intended merge-gate semantics (D-19), and it is why the retrofit must land in the same
  phase.

CI: `meta` already runs the whole hook surface
[VERIFIED: .github/workflows/ci.yml:89-90]:

```yaml
      - name: Run the hook surface
        run: pre-commit run --all-files --show-diff-on-failure
```

and `gate` already needs `meta` [VERIFIED: .github/workflows/ci.yml:427-431]:

```yaml
  gate:
    name: gate
    needs: [changes, meta, build, python-tests, static-analysis, simulate]
    if: ${{ !cancelled() }}
```

No workflow edit is required. The workflow test `jobs - {"gate"} == needs_ids(gate)` keeps
holding, and `python-tests` picks up `test_report.py` automatically because it runs
`python -m unittest discover scripts/tests`.

## Test Harness Conventions

| Convention | Evidence | Consequence for `test_report.py` |
|---|---|---|
| Standard-library `unittest`, no pytest | whole `scripts/tests/` | `import unittest`; `python3 -m unittest discover scripts/tests` must work with no third-party package |
| Tests never import `yaml`/`jsonschema` | module docstring [VERIFIED: scripts/tests/test_homework_metadata.py:1-8] | import `scripts.report.*` only (stdlib-only); shell out for the real CLI |
| The real script runs as a subprocess via `uv run` | `run_checker` [VERIFIED: scripts/tests/test_homework_metadata.py:121-129] | add `run_report_checker(*args, cwd=REPO_ROOT)` with a timeout |
| Disposable roots; the repository tree is never touched | `temp_root.build_root` [VERIFIED: scripts/tests/temp_root.py:77-99] | reuse `build_root` for scaffold tests; write report fixtures into a temp root |
| Real-tree regression exists for metadata | the 04.2 decision recorded in STATE.md: "every real-tree record is `OK`, exists on disk, and is sorted by path" | add a real-tree test: `check_report.py` exits 0 and every real `report.md` has one `OK` record |
| Import-boundary guard is AST-based | `ModuleBoundaryTests` [VERIFIED: scripts/tests/test_new_homework.py:676-716] | add `scripts/report/{markdown,tables,vocabulary,contract}.py` to a stdlib-only list |
| Hook layering is asserted by a hand-maintained tuple | [VERIFIED: scripts/tests/test_tooling_config.py:1245-1260] | add `check-report`; see Pitfall 12 for the vacuity fix |

Where the new suite belongs: `scripts/tests/test_report.py`. Fixtures can be written by
string assembly inside that module (the metadata suite's `document()` builder is the
precedent) or via a small `write_report(...)` helper; the shared `temp_root.py` should gain
nothing unless a second suite needs it.

## Skills Mirror

`hw-report` is a canonical skill with a stub body that explicitly says "Phase 10 owns the
report format and its validation" and points at `templates/report/report.md` and
`homeworks/1_3-police-flasher/report.md`
[VERIFIED: .claude/skills/hw-report/SKILL.md:1-27]. Editing it requires:

```bash
uv run scripts/gen_skills.py
```

because `.agents/skills/` is generated and `gen-skills-check` is the drift gate
[VERIFIED: .pre-commit-config.yaml:229-239]. The skill also carries `CHANGELOG.md`
[VERIFIED: .claude/skills/hw-report/CHANGELOG.md:1-7]; the repository's skill convention is
one dated entry per change. The description field and `metadata.status: stub` stay as they
are (D-27 keeps the stub).

## Runtime State Inventory

This phase is a contract retrofit, not a rename, but the checklist answers every category
so the planner can see there is no hidden migration.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no database, index, or cache stores a report heading, label, or id. | none |
| Live service config | None — no external service holds report vocabulary. The GitHub ruleset's required check stays `gate`; no new required check. | none |
| OS-registered state | None — no scheduler, service, or plist references the report contract. | none |
| Secrets/env vars | None — the contract reads no secret. `WOKWI_CLI_TOKEN` is untouched (no simulation run in this phase). | none |
| Build artifacts | `homeworks/1_3-police-flasher/.pio/` and `compile_commands.json` are untracked build output, regenerated by PlatformIO; the report retrofit changes neither. `templates/homework-espidf/compile_commands.json` exists but is on the scaffold's ignore list. | none |

## Common Pitfalls

### Pitfall 1: A line-anchored `[N]` reference parser misreads wrapped prose

**What goes wrong:** section 8 contains a hard-wrapped paragraph whose continuation line
begins with a citation marker:

```
[1] bounds the design: C-06 computes 9.33 mA and a 30.67 mA margin, so the 150 ohm choice is
```

Source: `homeworks/1_3-police-flasher/report.md:370` [VERIFIED: homeworks/1_3-police-flasher/report.md:370]

A `^\[(\d+)\] ` scan over the whole document therefore reports **seven** reference entries
for six references, and a naive "each entry must be cited" rule would treat `[1]` as
duplicated.

**Why it happens:** IEEE reference lists are one convention, and a citation token at the
start of a wrapped line is indistinguishable from a list entry without section scope.

**How to avoid:** collect reference entries **only** from the `## 10. References` section
body, and collect citation tokens from sections 1-9 plus `## Decision Appendix` only.
Assert exactly this shape in a fixture that reproduces the wrapped-line case.

**Warning signs:** a reference count that exceeds the number of distinct markers, or an
"entry [N] is never cited" error naming a marker that is cited.

### Pitfall 2: Comparing display cells without normalizing markup

**What goes wrong:** identity comparisons fail on a compliant report because the live cells
carry backticks and mixed inline code:

```
| Homework ID | `1_3-police-flasher` |
| Report status | `draft` |
| Platform | `platformio/espressif32` 8.0.0 |
| Implementation commit | `9e1238d` |
```

Source: `homeworks/1_3-police-flasher/report.md:10-19` [VERIFIED: homeworks/1_3-police-flasher/report.md:10-19]

`Platform` mixes a code span with plain text, so a single "strip one pair of backticks"
rule is not enough.

**How to avoid:** one `normalize_cell(value)` used by every comparison: strip all `` ` ``,
unescape `\|` → `|`, collapse internal whitespace, strip. Then apply the type-specific
comparison: equality, `casefold()` for `Framework`, and a platform normalizer (drop a
`platformio/` prefix, replace `@` with a space, collapse whitespace) so
`espressif32@8.0.0` equals `platformio/espressif32 8.0.0`. Pin both spellings in a test.

**Warning signs:** a compliant report failing only on a backticked cell.

### Pitfall 3: Scanning the whole document for evidence vocabulary

**What goes wrong:** the live report's prose deliberately discusses the vocabulary:

```text
D-14 reserves the qualified form `measured (observed)` for a debounce result read from a
serial log, but no row uses that form today ...
`observed` is never used as a label of its own.
```

Source: `homeworks/1_3-police-flasher/report.md:250-255` [VERIFIED: homeworks/1_3-police-flasher/report.md:250-255]

A document-wide "bare `observed` is an error" rule rejects a compliant report.

**How to avoid:** scope every vocabulary rule to the `Value` and `Label` cells of ledger
rows only, as D-10 states. Add a positive fixture that keeps the explanatory prose and
still passes.

### Pitfall 4: Losing line numbers across a fenced block

**What goes wrong:** section 6 contains two fenced `text` blocks
[VERIFIED: homeworks/1_3-police-flasher/report.md:206-208] [VERIFIED: homeworks/1_3-police-flasher/report.md:217-219].
A scanner that filters lines before enumerating them reports offsets shifted by the fence
width, and every downstream `line` is wrong.

**How to avoid:** enumerate the original lines once with `enumerate(lines, start=1)`, and
let the fence state decide *classification*, never *numbering*. Test it by putting a `## 2.
Objective` inside a fence and asserting the checker does not see it **and** that a real
violation after the fence reports the true line.

### Pitfall 5: Splitting table rows on every pipe

**What goes wrong:** GFM tables allow an escaped `\|` inside a cell, and a code span may
contain a pipe in practice even where GFM would split it. The live report has no escaped
pipes today (verified: zero matches for `\|`), so this defect would ship silently and only
appear on a future homework.

**How to avoid:** split on unescaped `|` only, keep the escape in the cell until after the
split, then unescape. A row without a leading pipe is still a row if the previous line was
a header/separator; decide and document. Fixture: a ledger cell containing
`` `a \| b` `` and a six-column row.

**Warning signs:** a "row has 5 cells, expected 6" error on a visually correct table.

### Pitfall 6: Requiring a subsection order that the worked example does not follow

**What goes wrong:** section 7 contains `### Interpreting the Forward-Voltage Row` between
`### Measurement Ledger` and `### Traceability Matrix`
[VERIFIED: homeworks/1_3-police-flasher/report.md:316]. A rule "section 7 children are
exactly [Measurement Ledger, Traceability Matrix] in that order" fails.

**How to avoid:** require *presence within the section* for each required subsection;
enforce order only for the ten numbered `##` headings (D-09). Ignore unknown subsections.

### Pitfall 7: Checking presence globally instead of within its section

**What goes wrong:** `### Limitations` must belong to section 4 and `### Next Steps` to
section 9. A global "contains `### Limitations`" rule passes a report that puts it under
section 8.

**How to avoid:** build a section tree (heading → child headings → body line range) and
resolve every subsection requirement against its parent section.

### Pitfall 8: The N/A marker's interaction with section 5 is underspecified

**What goes wrong:** D-34 allows section 5 and its four subsections to be N/A for a
software-only assignment, but does not say whether an N/A section 5 satisfies the four
subsection requirements. Read literally, a software-only report must still carry four
`### Bill of Materials`-style headings, each N/A, inside an N/A section.

**How to avoid:** pick the narrower reading and document it in `docs/standards/report.md`:
**if `## 5. Hardware and Wiring` carries the N/A marker, its four subsections are not
required; otherwise all four are required, each with a data table or its own N/A marker.**
Test both shapes. This is the one genuine ambiguity found; see Open Question 1.

### Pitfall 9: A PyYAML import in `scripts/report/contract.py` breaks the suite

**What goes wrong:** `python3 -m unittest discover scripts/tests` runs with no third-party
packages. A test module that imports `scripts.report.contract` which imports `yaml` fails
at discovery with `ModuleNotFoundError`, and the failure is attributed to the *test* rather
than to the boundary.

**How to avoid:** keep `scripts/report/*` stdlib-only; load YAML in `check_report.py` and
pass the resulting `dict` into the rules. Add the four modules to the AST import-boundary
test's stdlib-only list (the `_import_roots` pattern).

### Pitfall 10: `Path.resolve()` on a temp root and on artifact tokens

**What goes wrong:** `resolve_root()` returns a **resolved** path (on macOS a
`tempfile.TemporaryDirectory` under `/var/folders/...` resolves to `/private/var/...`), so a
naive `str(path).startswith(str(root))` containment check fails for every fixture. A blind
`resolve()` on an artifact token also follows a symlink out of the repository.

**How to avoid:** use `relative_path()` for display (it resolves both sides), and do
containment **lexically first** with `Path(os.path.abspath(...))`, then a resolved
`relative_to()` as defence in depth — exactly the posture in `contract.py`'s
`_homework_directory` and `check_metadata.py`'s `_relative_lexical`
[VERIFIED: scripts/metadata/contract.py:465-487] [VERIFIED: scripts/check_metadata.py:197-211].

### Pitfall 11: The path-likeness heuristic trips on commands

**What goes wrong:** traceability cells contain commands such as
`` `pio run -d homeworks/1_3-police-flasher` `` and `` `python3 scripts/check_architecture.py` ``.
Treating the whole backticked span as a path fails (it contains spaces); ignoring it means
the check never runs.

**How to avoid:** tokenize a backticked span on whitespace, then test each token for
path-likeness (`/` present, or a known extension). This exact split was needed to make the
live matrix pass in this session's probe; without it, four rows fail. Document the
heuristic and pin it with a fixture containing both a command and a bare path.

### Pitfall 12: Adding a hook to a hand-maintained tuple is vacuous

**What goes wrong:** `test_every_fast_hook_keeps_the_pre_commit_stage` iterates a literal
tuple of hook ids [VERIFIED: scripts/tests/test_tooling_config.py:1245-1260]. A new
`check-report` hook that is not added to the tuple is simply never inspected and the suite
stays green.

**How to avoid:** add `check-report`, **and** add a closed-set assertion: every `- id:` in
`.pre-commit-config.yaml` must appear in either the fast-hook tuple or the push-hook tuple.
That converts a maintenance chore into a failing test.

### Pitfall 13: Extending the scaffold without extending `eight_paths`

**What goes wrong:** `SHARED_PATHS` and `eight_paths()` are hand-maintained
[VERIFIED: scripts/tests/test_new_homework.py:40-57]. `report.md` would be scaffolded but
never asserted, and `assert_matches_live_template` would fail independently because its
expected map is built from the template tree plus `task.md`
[VERIFIED: scripts/tests/test_new_homework.py:140-177].

**How to avoid:** update both, and rename `eight_paths` to `declared_paths` so the name
stops asserting a count that changes.

### Pitfall 14: Reusing the 64 KiB metadata cap for reports

**What goes wrong:** the live report is 42,344 bytes; the metadata cap is 65,536
[VERIFIED: scripts/metadata/contract.py:80]. A realistic expanded report would cross it and
fail for a reason the standard never states.

**How to avoid:** choose and document a report-specific bound (or none), and put the
constant in `vocabulary.py` next to the other contract constants.

### Pitfall 15: `AGENTS.md` is already at its soft limit

**What goes wrong:** `AGENTS.md` is **303 lines**, against the rulebook's own "up to ~300
lines" statement. D-29 adds a rule block, a quick-start row, a Definition of Done rewrite,
and two routing-table edits.

**How to avoid:** write the new block tightly (three or four bullets), and remove the
`Planned: report structure … (Phase 10)` line it replaces
[VERIFIED: AGENTS.md:81]. Do not add a second report section elsewhere.

### Pitfall 16: Unrecognised paths widen the CI build matrix

**What goes wrong:** `NO_BUILD_IMPACT` lists `docs/`, `.claude/`, `.agents/`, `AGENTS.md`,
`templates/views/`, and a few named scripts, but **not** `templates/report/`,
`scripts/report/`, `scripts/check_report.py`, or `scripts/tests/`
[VERIFIED: scripts/affected.py:100-124]. Any of those paths is "unrecognised", which widens
the matrix to **every** project.

**How to avoid:** accept it — D-32 explicitly keeps `affected.py` unchanged, and this
phase's pull request legitimately touches the scaffold, which can affect every project.
Note it in the plan so the longer `build` job is expected rather than investigated.

### Pitfall 17: Reaching for git or the network in the checker

**What goes wrong:** D-11 deliberately drops commit **reachability** (that would need
`git cat-file`) and D-38 drops external-link liveness. A checker that shells out to git or
fetches a URL becomes non-deterministic and slow in a hook that runs on every pull request.

**How to avoid:** hex-shape plus ledger-consistency only; parse the diagram with `json`;
never open a socket.

### Pitfall 18: `report` absent on a `planned` homework

**What goes wrong:** the schema does not require `report`, so a planned homework without it
is valid metadata. A report checker that treats "no `report` block" as an error on every
directory breaks the scaffold's own output before the template change lands — and breaks
any planned homework authored before Phase 10.

**How to avoid:** if `status: planned` and the block is absent, emit `OK` with "no report
declared" and skip; if `status` is anything else and the block or `report.path` is absent,
emit an `ERROR`. If the block is present, validate the file at `report.path` in every case.

## Validation Architecture

`workflow.nyquist_validation` is `true` in `.planning/config.json`, so this section is
required.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` (no pytest, no third-party import in any test module) |
| Config file | none — discovery conventions only (`scripts/tests/test_*.py`) |
| Quick run command | `python3 -m unittest discover scripts/tests -p 'test_report.py' -v` |
| Full suite command | `python3 -m unittest discover scripts/tests` |
| Checker smoke command | `uv run scripts/check_report.py` (exit 0 on the real tree) |
| Hook-level command | `pre-commit run check-report --all-files` |

### How each success criterion becomes a deterministic check

| Success criterion | Deterministic mechanism | Test |
|---|---|---|
| **1.** Template and check enforce the ten sections plus BOM, pin map, calculations, safety, ledger, traceability, honest status, IEEE references | Literal heading/header constants in `vocabulary.py`; structure rules `RPT-1xx`; table rules `RPT-2xx`; D-23 parity test | `test_template_contains_every_literal` (stdlib, reads the template and the constants); `test_compliant_report_has_no_errors`; one negative fixture per rule |
| **2.** Missing BOM row / provenance label / traceability entry fails with a specific message | BOM: zero data rows and no N/A marker → `ERROR` naming the BOM table and its header line. Ledger: a `Label` outside the vocabulary → `ERROR` naming the row id and the offending label. Traceability: a missing `REPORT-NN` → `ERROR` naming the missing requirement | three focused fixtures, each asserting **rule id + line + message fragment** (not just exit 1) |
| **3.** `docs/standards/electrical-calculations.md` lists the catalog; each calculation records formula, units, provenance, result, uncertainty, assumption impact | The eight-column header and the non-empty-cell rules are machine-checked (`RPT-2xx`); the catalog's completeness is authored (D-24) | `test_calculation_row_with_empty_uncertainty_is_rejected`; `test_calculation_header_is_exact`; the catalog itself is review-enforced (no prose-sync test, per the 261026-ky7 pruning) |
| **4.** Self-audit rubric maps every artifact and evidence item to the pre-PR checklist | Rule registry (`id → summary → remediation`) in `scripts/report/`, plus the checklist in `docs/standards/report.md` | `test_every_registered_rule_fires_once` (non-vacuity); `test_rule_ids_are_unique`; a narrow assertion that every registered id appears in the standard (see Open Question 3) |
| Cross-cutting: the retrofit is real | Real-tree regression: `check_report.py` exits 0 and every real `report.md` yields one `OK` record | `test_real_tree_passes` (mirrors the metadata suite's real-tree test) |
| Cross-cutting: the gate is wired | Hook id present, check-only, `pass_filenames: false`, `files` reaches every declared path | `test_tooling_config` extension + closed-set assertion |
| Cross-cutting: the scaffold emits a report | Scaffold test asserts the file set includes `report.md` and the rendered text has no `{{` | `InventoryTests` + `TemplateParityTests` extension |

**Why rule ids, not message text, are the stable contract:** D-04 makes the id stable and
D-43 makes the remediation table map id → fix. A test should assert the id and the line;
the prose fragment assertion should be short and specific (for example
`"ledger label"`), so wording can improve without a test rewrite.

### Phase Requirements → Test Map

| Req ID | Behaviour | Test Type | Automated Command | File Exists? |
|--------|-----------|-----------|-------------------|--------------|
| REPORT-01 | Ten headings present, ordered, unique; required subsections scoped to their section | unit | `python3 -m unittest scripts.tests.test_report -k headings` | ❌ Wave 0 |
| REPORT-02 | BOM header exact; ≥1 data row or N/A; every `Ref` is a diagram part id | unit | `... -k bom` | ❌ Wave 0 |
| REPORT-03 | Pin-map header exact; N/A allowed; source-of-truth claim review-only | unit | `... -k pin_map` | ❌ Wave 0 |
| REPORT-04 | Calculation header 8 columns; four mandatory cells non-empty | unit | `... -k calculations` | ❌ Wave 0 |
| REPORT-05 | Safety checklist ≥1 bullet, each beginning `- **` | unit | `... -k safety` | ❌ Wave 0 |
| REPORT-06 | Ledger header 8 columns; label vocabulary; value prefixes; commit identity; provenance depth | unit | `... -k ledger` | ❌ Wave 0 |
| REPORT-07 | Traceability header; status enum; artifact existence; `REPORT-01..08` coverage | unit | `... -k traceability` | ❌ Wave 0 |
| REPORT-08 | `Status:` and `Industry note:` paragraphs; `### Limitations`; `### Next Steps`; status consistency; native/simulation claims | unit | `... -k status_claims` | ❌ Wave 0 |
| TOOL-08 | Rule registry ↔ standard checklist; PR template names the checker | unit + review | `... -k rule_registry` | ❌ Wave 0 |
| Scaffold | `report.md` composed, rendered, idempotent, conflict-refused | integration | `python3 -m unittest scripts.tests.test_new_homework -k report` | ✅ update existing |
| Hook wiring | `check-report` exists, pre-commit stage, `pass_filenames: false`, `files` coverage | unit | `python3 -m unittest scripts.tests.test_tooling_config -k report` | ✅ update existing |
| Real tree | `uv run scripts/check_report.py` exits 0 on the repository | integration | `uv run scripts/check_report.py` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python3 -m unittest discover scripts/tests -p 'test_report.py'` plus `uv run scripts/check_report.py`.
- **Per wave merge:** `python3 -m unittest discover scripts/tests` and `pre-commit run --all-files`.
- **Phase gate (D-33):** `pio run` for the affected environment, `pio test -d tests -e native`, `pre-commit run --all-files`, `uv run scripts/check_metadata.py`, `python3 -m unittest discover scripts/tests`, `uv run scripts/check_report.py`, and a green `gate`.

### Wave 0 Gaps

- [ ] `scripts/report/__init__.py` — package marker (mirror `scripts/metadata/__init__.py`, which is a one-line docstring). `scripts/` itself has no `__init__.py`; namespace packages make the import work.
- [ ] `scripts/report/vocabulary.py`, `markdown.py`, `tables.py`, `contract.py` — stdlib-only.
- [ ] `scripts/check_report.py` — the only PyYAML-aware module.
- [ ] `scripts/tests/test_report.py` — compliant fixture, one negative fixture per rule, fence case, escaped-pipe case, wrapped-citation case, real-tree case.
- [ ] No framework install needed: `unittest` is in the standard library.

**Fixtures the suite must contain (minimum):** a fully compliant report; a report missing
one data row in each of the three tables named in success criterion 2; an unknown ledger
label; a bare `observed`; a `not measured` value without a reason; a `TODO` in a `draft`
report; a heading inside a fence; a heading out of order; a duplicate heading; a missing
required subsection; an N/A marker without a reason; an N/A in a forbidden position; a
BOM ref absent from the diagram; a broken relative link; an unresolved `C-NN`; an
uncited reference; a citation to a missing reference; a wrapped continuation line starting
`[N]`; a `REPORT-01`-free matrix; an identity mismatch for each compared field; a commit
mismatch in one ledger row; a Cyrillic character; a `planned` homework with no report block;
an `in-progress` homework with `report.status: placeholder` (must fail D-18).

## Security Domain

`security_enforcement` is `true` and `security_asvs_level` is `1`; `security_block_on` is
`high`.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No identity, no session, no credential in this phase. |
| V3 Session Management | no | Not applicable to a CLI checker. |
| V4 Access Control | no | The gate is GitHub's; the phase changes no permission. |
| V5 Input Validation | **yes** | Strict YAML loading (duplicate-key rejection), bounded file size, `json` for the diagram, exact-shape table/heading parsing, explicit enums for label and status, `argparse` for the CLI. |
| V6 Cryptography | no | No hashing or encryption is introduced. |
| V12 File and Resources | **yes** (ASVS 1 maps this to file handling) | Lexical containment for artifact existence and Markdown links; refuse a path that escapes the homework directory and the repository root; never follow a symlink for a scanned document. |

### Known Threat Patterns for a Markdown/YAML/JSON checker

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via a traceability token or a Markdown link (`../../../etc/passwd`, absolute path) | Tampering / Information disclosure | Reject absolute targets and `..` that escapes the repository root; resolve lexically first, then verify containment; report as `ERROR`, never read the file. |
| Symlink escape: a `report.md` replaced by a symlink to an outside file | Tampering | `os.lstat` on the final component before reading; refuse and report (mirrors `read_regular_text` [VERIFIED: scripts/metadata/render.py:65-82]). |
| YAML duplicate-key override (`report.status` written twice) | Tampering | `StrictSafeLoader` [VERIFIED: scripts/metadata/yaml_loader.py:26-60]. |
| Unbounded input (a 50 MB report) | Denial of service | A documented size cap, checked before parsing. |
| Malformed JSON diagram | Tampering | `json.loads` in a `try`, reported as a content `ERROR` (exit 1), not a traceback and not exit 2. |
| Hook-environment drift (a second pin) | Tampering / supply chain | The new hook declares the **already-pinned** `PyYAML==6.0.3`; no new package, no `rev` change. |
| Non-determinism from the network or clock | Repudiation | No network, no clock; the checker is read-only and byte-identical across runs. |

**Not a threat this phase creates:** the checker never executes report content, never
evaluates a formula, and never shells out, so there is no command-injection surface.

## Code Examples

### Record, output and exit codes (mirror `check_metadata.py`)

```python
# scripts/check_report.py — shape only; source: scripts/check_metadata.py:68-75, 354-377
def _record(root, path, status, rule, reason, line=0):
    return {
        "path": relative_path(root, path),
        "status": status,
        "rule": rule,
        "line": line,
        "reason": reason,
    }

records.sort(key=lambda item: (item["path"], item["line"], item["rule"]))

if args.json:
    print(json.dumps(records, indent=2))
    return 1 if violations else 0

for record in records:
    suffix = f" [{record['rule']}]" if record["rule"] else ""
    print(f"{record['path']}:{record['line']}: {record['status']}{suffix} — {record['reason']}")
```

### Cell normalization (identity and commit comparisons)

```python
# scripts/report/tables.py — stdlib only
_WHITESPACE = re.compile(r"\s+")

def normalize_cell(value):
    """Strip inline-code markers, unescape pipes, collapse whitespace."""
    text = value.replace("\\|", "|").replace("`", "")
    return _WHITESPACE.sub(" ", text).strip()

def normalize_platform(value):
    text = normalize_cell(value)
    if text.startswith("platformio/"):
        text = text[len("platformio/"):]
    return _WHITESPACE.sub(" ", text.replace("@", " ")).strip()

# "espressif32@8.0.0"                      -> "espressif32 8.0.0"
# "`platformio/espressif32` 8.0.0"         -> "espressif32 8.0.0"
```

### Lexical containment for an artifact token (D-13/D-38)

```python
# scripts/report/contract.py — stdlib only; takes roots and an already-split token
def resolve_artifact(token, homework_dir, repo_root):
    """Return True when *token* resolves under one of the two allowed roots.

    Lexical first (abspath normalizes '.'/'..' without following a symlink),
    then a resolved containment check as defence in depth.
    """
    candidate = Path(os.path.abspath(homework_dir / token))
    for base in (Path(os.path.abspath(homework_dir)), Path(os.path.abspath(repo_root))):
        try:
            candidate.relative_to(base)
        except ValueError:
            continue
        if candidate.exists():
            return True
    return False
```

Absolute tokens must be rejected before this call, and a token that escapes both roots is
an `ERROR` rather than a silent `False`.

### Scaffold candidate addition

```python
# scripts/new_homework
REPORT_MD = "report.md"
REPORT_TEMPLATE = Path("templates") / "report" / REPORT_MD

def _candidates(root, template_dir):
    candidates = _template_files(template_dir)
    for relative_name, template_path in (
        (TASK_MD, TASK_TEMPLATE),
        (REPORT_MD, REPORT_TEMPLATE),
    ):
        source = root / template_path
        if source.is_symlink():
            raise CheckError(f"{template_path.as_posix()} is a symlink; refusing to follow it")
        if not source.is_file():
            raise CheckError(f"missing {template_path.as_posix()}")
        candidates.append((Path(relative_name), source))
    ...
```

Note the refactor hazard: the existing code names the `task.md` error strings literally
(`"templates/task/task.md is a symlink…"`, `"missing templates/task/task.md"`). A loop that
generalises the message changes those strings; any test asserting them must move with it.

### Hook block

See "Hook and CI Wiring" above for the exact YAML; the pattern is `language: python`,
`additional_dependencies: ["PyYAML==6.0.3"]`, `entry: python scripts/check_report.py`,
`pass_filenames: false`, `stages: [pre-commit]`.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Line-oriented Markdown lint only | Structural section/table validation plus cross-file integrity | Adopted here; external tools such as `doc-structure-lint` do structural section validation, and `remark-lint` does AST rules | The contract can enforce section templates and cross-file evidence, which a line linter cannot (D-03) |
| Stored golden scaffold fixtures | Property assertions against the live template | Phase 06.1 / quick task `261026-x78` (2026-10-27) | A new `report.md` golden file would reverse a recorded decision; assert against `templates/report/report.md` instead |
| Prose/doc-sync tests in general | Behavioural guards only; text assertions only for load-bearing sentences | Quick task `261026-ky7` (2026-10-26) | The TOOL-08 rule-id mapping is the deliberate narrow exception; do not add prose assertions about the standard |
| Unlabelled measurements | Five provenance labels plus one qualified form, with per-row instrument/method/uncertainty/commit | Phase 04.2 D-13/D-14, Phase 7 | The checker now enforces what was a human reading task |
| Hand-assembled traceability matrix | Matrix checked for ids, artifact existence, status enum, and requirement coverage | This phase (D-36/D-41) | F-13's manual assembly becomes machine-checked |

**Deprecated/outdated:**
- The six-line `templates/report/report.md` skeleton (`# {{title}}` plus a "later phase"
  note and `TODO: Report body.`) — replaced wholesale (D-21) [VERIFIED: templates/report/report.md:1-6].
- The `Planned: report structure under docs/standards/ (Phase 10)` line in `AGENTS.md`
  [VERIFIED: AGENTS.md:81] — removed (D-29).
- The Definition of Done clause "BOM, calculations, measurement ledger, and traceability
  are guidance, not a merge gate until Phase 10" in `REQUIREMENTS.md` — becomes the checked
  contract (D-19).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The section-1 table header should be `Field | Value`; D-08 does not list it, but D-11 requires row keys. | Retrofit audit / validation | Low. If the planner leaves it unpinned, the checker still works by key lookup; pinning it adds one literal and one template row. Either way the live report already uses `Field | Value` [VERIFIED: homeworks/1_3-police-flasher/report.md:8-9]. |
| A2 | An N/A section 5 waives its four subsection requirements. | Pitfall 8 | Medium. The opposite reading forces four N/A subsection headings in a software-only report; both are defensible, so the standard must state one. |
| A3 | The `--json` payload for the report checker should include `rule` and `line`, unlike `check_metadata.py`. | Existing contracts | Low. D-04 requires specificity; including them is additive, and a test pins it. |
| A4 | The report size cap should be larger than 64 KiB (or absent). | Pitfall 14 | Low. The live report is 42,344 bytes; a reused 64 KiB cap would be a latent failure. |
| A5 | The three new traceability rows should be `verified` or `manual`, not `pending`. | Retrofit audit | Medium. `pending` is exempt from artifact existence (D-13) but would make the retrofit cosmetic and contradict D-19's no-grandfathering stance. |
| A6 | `check-report` sits in the same `repo: local` block as `check-metadata`. | Hook and CI wiring | None functionally; pre-commit runs repositories in file order, and both are local. |
| A7 | A rule-id family scheme (`RPT-0xx` lifecycle, `RPT-1xx` structure, `RPT-2xx` tables, `RPT-3xx` cross-file) is a good default. | Validation Architecture | Low — numbering is explicitly Claude's discretion. The only hard requirement is stability (D-04). |
| A8 | The template's sentinel text can be the literal `TODO` rows plus an N/A example. | Scaffold | Low. D-16 rejects `TODO` for `draft`/`complete` and D-17 exempts `placeholder`; the exact text is discretion. |

## Open Questions

1. **How does the N/A marker interact with section 5's subsections?**
   - What we know: D-34 allows section 5 and its four subsections to be N/A; D-06 says a
     section is never omitted.
   - What's unclear: whether an N/A `## 5.` requires four N/A `###` headings.
   - Recommendation: waive them (A2) and state the rule in `docs/standards/report.md`; test
     both the N/A-section case and the four-subsection case.

2. **Should the section-1 `Field | Value` header be pinned?**
   - What we know: D-11 names the row keys; D-08 omits this table from its header list.
   - What's unclear: whether pinning it is an unrecorded contract addition.
   - Recommendation: pin it in `vocabulary.py` and the template; it is a one-line addition
     with no downside and the live report already conforms.

3. **Is a narrow doc-sync assertion for TOOL-08 acceptable after the prose-test pruning?**
   - What we know: `261026-ky7` pruned prose and doc-sync tests; TOOL-08 explicitly requires
     the artifact→checklist mapping.
   - What's unclear: whether "every rule id appears in `docs/standards/report.md`" counts as
     a prose assertion.
   - Recommendation: make the *behavioural* guard primary (every registered rule fires in a
     fixture; ids are unique; every rule id names a remediation) and add only the id-presence
     assertion, which is a contract check rather than a prose check. If the owner prefers,
     drop the id-presence assertion and rely on review, recording why.

4. **What exactly fills `### Next Steps` in 1.3?**
   - What we know: section 9 already states Phase 11 owns the tag and the polish.
   - What's unclear: whether the subsection should be one sentence or a short list.
   - Recommendation: a short list of the Phase 11 items already named in the `Status:`
     paragraph (bench evidence pass, tag, scale-out), so no new claim is introduced.

5. **Should `check_report.py` validate `templates/report/report.md` directly?**
   - What we know: D-23 says no, because the template contains placeholders; the parity test
     covers drift.
   - Recommendation: keep it out, and let the template parity test be the only template
     guard.

6. **What is the final rule-id list and message wording?**
   - What we know: discretion (D-04 fixes only stability and specificity).
   - Recommendation: freeze the registry early (before writing messages), because every test,
     the standard's table, and the remediation column reference it.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `python3` | Checker, tests | ✓ | 3.13.13 | — |
| `uv` | `uv run scripts/check_report.py`, PEP 723 env, tests that shell out | ✓ | 0.13.5 | `python3 -m venv` + pip, but the repository contract is `uv` |
| `git` | `resolve_root()` when `--dir` is absent | ✓ | 2.54.0 | pass `--dir` |
| `pre-commit` | `pre-commit run --all-files`, the new hook | ✓ | 4.7.0 | CI `meta` runs the same command |
| `node` | `markdownlint-cli2` hook (pre-commit-managed npm env) | ✓ | v26.7.0 | CI installs its own; the hook pulls its own dependencies |
| `wokwi-cli` | **not needed** — the checker only parses `diagram.json`; the offline lint stays in `meta` | ✓ in CI | 0.28.1 | — |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none.

## Sources

### Primary (HIGH confidence) — in-repo, read this session

- `scripts/check_metadata.py` — CLI, record shape, exit codes, positional and directory
  handling, JSON payload.
- `scripts/metadata/contract.py` — record shape, size cap, strict loading, path identity,
  re-exports.
- `scripts/metadata/paths.py`, `render.py`, `yaml_loader.py`, `errors.py` — import
  boundaries and the reusable helpers.
- `scripts/new_homework` — `_candidates`, `_mapping`, `_build_plan`, the required-set check.
- `templates/report/report.md`, `templates/task/task.md`, both `templates/homework-*/homework.yaml`.
- `homeworks/1_3-police-flasher/{report.md,homework.yaml,assets/diagram.json}` — the worked
  example, its identity values, its table headers, and the seven diagram part ids.
- `schema/homework.schema.json` — `report` definition, root `required`, status enum.
- `.pre-commit-config.yaml`, `.github/workflows/ci.yml` — hook shape, `meta`, `gate`.
- `scripts/tests/{temp_root.py,test_new_homework.py,test_homework_metadata.py,test_tooling_config.py}` — harness, boundary guard, real-tree precedent, hook assertions.
- `scripts/affected.py` — `NO_BUILD_IMPACT` / `WIDEN_ALL`.
- `scripts/gen_skills.py`, `.claude/skills/hw-report/{SKILL.md,CHANGELOG.md}` — mirror
  regeneration and the stub text.
- `AGENTS.md`, `.github/pull_request_template.md`, `docs/decisions/README.md`,
  `docs/standards/vscode.md` — the documentation surfaces and their format.
- `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md` — F-07, F-11, F-12, F-13.

### Secondary (MEDIUM confidence)

- `.planning/phases/10-report-and-evidence-system/10-CONTEXT.md` — the 44 locked decisions,
  including the external standards the contract adopts (PROV-O, ETIS, NASA SWE-072, FAA
  VRTM, GUM/NIST TN 1297, IEEE reference style, `doc-structure-lint`, `remark-lint`,
  `markdownlint`). These URLs were **not** fetched this session; they are carried as the
  decision's rationale, not as implementation facts, and the research makes no claim that
  depends on their content.

### Tertiary (LOW confidence)

- None used for any recommendation. The one external comparison (structural vs line-oriented
  Markdown validation) is recorded as context for D-03 and does not change the plan.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every dependency is already pinned in-repo and read this session; no new package is proposed.
- Architecture: HIGH — the CLI, module ladder, scaffold path, hook shape, and test harness are all existing, verified code; the only new component is the bounded parser.
- Pitfalls: HIGH — most were observed directly in the live report (the `[1]` wrapped line, backticked cells, prose vocabulary mentions, the extra section-7 subsection) or in existing test vacuity patterns.
- Retrofit scope: HIGH — verified field by field against `report.md`; the three-edit claim holds, with the recorded caveat about the new rows' status.

**Research date:** 2026-10-27
**Valid until:** 2026-11-26 (30 days; the repository moves a few commits a week, and the
facts here are file- and line-anchored, so a drift is visible as a failed re-read rather
than a silent assumption).
