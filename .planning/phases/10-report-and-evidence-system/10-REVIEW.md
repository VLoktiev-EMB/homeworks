---
phase: 10-report-and-evidence-system
reviewed: 2026-10-27T15:26:45Z
depth: standard
files_reviewed: 25
files_reviewed_list:
  - scripts/report/__init__.py
  - scripts/report/vocabulary.py
  - scripts/report/markdown.py
  - scripts/report/tables.py
  - scripts/report/contract.py
  - scripts/check_report.py
  - scripts/new_homework
  - scripts/tests/test_report.py
  - scripts/tests/test_new_homework.py
  - scripts/tests/test_tooling_config.py
  - .pre-commit-config.yaml
  - templates/report/report.md
  - templates/homework-arduino/homework.yaml
  - templates/homework-espidf/homework.yaml
  - homeworks/1_3-police-flasher/report.md
  - AGENTS.md
  - .github/pull_request_template.md
  - docs/decisions/README.md
  - docs/standards/report.md
  - docs/standards/electrical-calculations.md
  - .claude/skills/hw-report/SKILL.md
  - .claude/skills/hw-report/CHANGELOG.md
  - generated.skills.manifest
  - .agents/skills/hw-report/SKILL.md
  - .agents/skills/hw-report/CHANGELOG.md
findings:
  critical: 3
  warning: 10
  info: 9
  total: 22
status: issues_found
---

# Phase 10: Code Review Report

**Reviewed:** 2026-10-27T15:26:45Z
**Depth:** standard
**Files Reviewed:** 25
**Status:** issues_found

## Summary

The phase delivers a genuinely strong foundation: the vocabulary is single-sourced, the
checker is deterministic and stdlib-only apart from PyYAML, the rule ids are exhaustively
fixtured, and the generated skills mirror matches its manifest byte for byte. The live
worked example satisfies the contract, and the hook is correctly check-only and scoped.

The defects below are the ones the green suite cannot see. They fall into three groups:
(1) unhandled exceptions from hostile-but-plausible repository content crash the gate with a
traceback instead of a structured record; (2) the declared `report.path` is trusted without
the containment logic the rest of the codebase applies, so the checker can be made to read
arbitrary files; and (3) several documented contract claims are not machine-enforced, while
several implementation checks are narrower or broader than the documented rule, producing
false passes and false rejections. All findings were reproduced against the real checker with
temporary fixtures; commands and observed results are cited.

## Narrative Findings (AI reviewer)

### Critical Issues

#### CR-01: A deeply nested `homework.yaml` crashes the checker with a `RecursionError` traceback

**File:** `scripts/check_report.py:132-137`
**Issue:** `_read_metadata` wraps `yaml.load(text, Loader=StrictSafeLoader)` in
`except yaml.YAMLError` only. PyYAML raises `RecursionError` for deeply nested flow
collections, which is a `RuntimeError`, not a `YAMLError`. A ~2 KB `homework.yaml`
containing 1,000 nested flow sequences (valid YAML syntax) is enough. Reproduced:

```text
rc= 1  traceback= True  stdout_empty= True
RecursionError: maximum recursion depth exceeded
```

The checker emits no `--json` array, no record and no exit-2 usage error; it violates the
module's own exit-code contract ("a malformed `homework.yaml` … stays at exit 1") and the
`--json` promise ("prints one array … and nothing else").
**Fix:** catch the parser's runtime failures as a content error, e.g.
`except (yaml.YAMLError, RecursionError) as exc:` and emit RPT-001. Consider adding a depth
guard to `StrictSafeLoader` so the same hardening reaches `check_metadata.py`, which shares
the loader.

#### CR-02: `parse_diagram` raises `RecursionError` on deeply nested JSON, despite "never raises"

**File:** `scripts/report/contract.py:350-363`
**Issue:** `parse_diagram` catches only `json.JSONDecodeError`. A nested-JSON payload of
100,000 `[` characters (200,000 bytes, well inside the 1 MiB gate) raises `RecursionError`.
Reproduced end to end: the checker prints a traceback, exits 1 with empty stdout, and never
emits RPT-207. This directly contradicts the docstring's "`parse_diagram` never raises
(T-10-27)" and the check_report promise that a hostile diagram is "a content error … never a
traceback".
**Fix:** `except (ValueError, RecursionError) as exc:` (JSONDecodeError is a `ValueError`
subclass) and return `Diagram(error=...)`. A bounded-depth pre-scan or `json.loads(...,
parse_float=...)` is not required; catching the recursion error is sufficient for the
documented posture.

#### CR-03: `report.path` is trusted and read without containment, so the checker reads outside the repository

**File:** `scripts/check_report.py:215-233`
**Issue:** `report_path = directory / report_path_value` is used directly for `is_symlink()`,
`is_file()` and `read_regular_text`, with no absolute/`..` rejection and no component walk.
`homework.yaml` is untrusted repository content, and `check_report.py` does not apply the
JSON Schema that constrains `report.path`. Reproduced with a fixture whose metadata declares
`report.path: /etc/passwd`: the checker read and parsed the file and emitted RPT-101 records
for it. A `../../../outside-report.md` path is likewise read from outside the root
(displayed only as the basename, hiding the escape). This is the same class the rest of the
phase defends against: `resolve_artifact` refuses absolute and escaping targets, and
`new_homework._component_conflict` walks every component with `lstat`, but the declared
report path bypasses both.
**Fix:** apply the existing containment posture to `report.path`: reject `Path(value).is_absolute()`
and any lexically escaping path, walk the components with `lstat` (reusing
`new_homework`'s component logic), require lexical and `realpath` containment under the
homework directory (and the repository root, as appropriate), and emit RPT-001/RPT-002 on
failure. The schema is a second gate, not a substitute for this one.

### Warnings

#### WR-01: Marker, citation and cross-reference scanners do not skip fenced code, producing both false passes and false rejections

**File:** `scripts/report/contract.py:399-422`, `scripts/report/contract.py:895-959`,
`scripts/report/markdown.py:135-150`
**Issue:** `_valid_marker`, `_marker_in_range`, `_section_waived`,
`_cross_reference_records` and `markdown.citation_tokens` scan raw lines. Consequences
reproduced against the real checker:

- A fenced code block containing `_Not applicable — software only._` in section 3 waives the
  required assumptions table: a non-compliant report **passes** (exit 0).
- A code sample `x = arr[7];` in section 2 produces a false `RPT-311` ("citation [7] has no
  entry"), and `A-99` in a fence produces a false `RPT-309`. Numeric array indexing such as
  `buf[0]` is common in embedded code snippets, so this is a realistic false rejection.
- Conversely, a reference cited only inside a fence counts as "cited", so a reference entry
  can satisfy RPT-312 without any real in-text citation.

Every other scanner (headings, tables, links) is fence-aware, so this is an inconsistency,
not an intentional subset.
**Fix:** factor the fence state into a shared iterator (the one `markdown.headings`,
`tables.extract_tables` and `contract.link_targets` already implement) and use it for marker
detection, citation collection and cross-reference collection.

#### WR-02: Required-table lookup takes the first table in range, rejecting a compliant report with an earlier unrelated table

**File:** `scripts/report/contract.py:471-474`
**Issue:** `table = next(candidate for candidate in extracted if start <= candidate.header_line <= end)`
selects the first table in the section/subsection range and then compares its header. If a
report opens section 1 or 3 (or a required subsection) with any other table, the check emits
`RPT-201` "header differs" even though the required table is present later with the exact
header. Reproduced: prepending a `| Note | Value |` table before the section-1 metadata table
produces `rc=1`, `RPT-201`. It also means the row/cell checks (`RPT-203`, `RPT-206`) run
against the unrelated table.
**Fix:** select the first table whose header equals `expected` within the range, and report
"absent" only when none matches. If the contract really wants the required table to be the
first one, say so in `docs/standards/report.md` and add a dedicated rule id rather than
overloading RPT-201.

#### WR-03: The section-1 `Implementation commit` row is optional in practice

**File:** `scripts/report/contract.py:640-655`, `scripts/report/contract.py:962-1067`
**Issue:** `_ledger_records` validates the section-1 commit only when a row with
`Field == "Implementation commit"` exists, and `_identity_records` never checks for it. A
report with that row deleted from section 1 still passes: reproduced with the row removed
(`rc=0`, no rules). This contradicts RPT-304 ("record the same … commit in section 1 and in
every ledger row") and the standard's commit-identity rule.
**Fix:** emit RPT-304 (line 0 or the table header line) when the section-1 metadata table has
no `Implementation commit` row, or when its value is empty. Add a fixture that deletes the
row, not just one that corrupts it.

#### WR-04: Section 10 may be empty although the standard requires at least one entry

**File:** `scripts/report/contract.py:923-959`; `docs/standards/report.md:98-104`
**Issue:** With zero citations and zero entries, `_citation_records` returns no records. A
report whose `## 10. References` body is empty passes (reproduced: `rc=0`), while the
standard lists "Section 10 must contain at least one IEEE-numbered entry matching `[N]`" as a
required paragraph. No rule id covers an empty reference list, and the self-audit checklist
does not mention References either.
**Fix:** add a rule (for example a new RPT id) requiring at least one reference entry in
section 10, and add it to the rule reference and the self-audit checklist. If the intent is
review-only, move the claim to "Review-enforced standards" instead.

#### WR-05: Unknown level-2 headings, appendix placement, and marker-beside-artifact are not enforced

**File:** `scripts/report/contract.py:1354-1385`; `docs/standards/report.md:61-62`, `:106-119`
**Issue:** `validate_report` ignores every level-2 heading whose text is not in
`REPORT_HEADINGS`. Reproduced:

- A report with `## 11. Extra Section` passes (`rc=0`).
- `## Decision Appendix` placed *before* `## 10. References` passes (`rc=0`).

The standard says the ten headings form "one uniform skeleton", that the appendix "may
follow the references", and that it is "the only additional level-2 heading the contract
recognizes". Separately, a valid marker placed beside a table is accepted (reproduced:
`rc=0`) although the standard says "it never sits beside one".
**Fix:** reject any level-2 heading outside the ten plus `Decision Appendix`, require the
appendix (when present) to follow section 10, and flag a marker that coexists with the
artifact it claims to replace — or soften the standard so it does not promise enforcement it
does not provide.

#### WR-06: Ledger provenance is checked only in the `Method` cell for calculated/simulated rows, rejecting compliant rows

**File:** `scripts/report/contract.py:739-779`
**Issue:** For `calculated`, the `C-NN` id is searched only in `method`
(`re.search(r"\bC-\d{2}\b", method)`), and for `simulated`, the path is searched only in
`method` (`method.split()`). The documented rule does not restrict the cell, and the
`datasheet` branch deliberately accepts either `Instrument` or `Method`. Reproduced:

- A `calculated` row naming `C-01` in the `Quantity` cell (with `Method` = "computed") is
  rejected with RPT-305.
- A `simulated` row naming `Wokwi scenario.yaml` in the `Instrument` cell (with `Method` =
  "expected high at 100 ms") is rejected with RPT-305.

**Fix:** search the provenance across the ledger cells that can legitimately carry it
(`Quantity`, `Instrument`, `Method`), or state the exact required cell in both the rule text
and `docs/standards/report.md`.

#### WR-07: Combined citations (`[1, 6]`, ranges) are invisible, yielding a false RPT-312 and a false pass

**File:** `scripts/report/markdown.py:111-114`, `scripts/report/contract.py:923-959`
**Issue:** `CITATION = re.compile(r"\[(\d+)\]")` matches only a single number inside the
brackets. Reproduced:

- A body citation `[1, 6]` with entries `[1]` and `[6]` produces `RPT-312`
  "reference entry [6] is never cited" — a false rejection.
- A body citation `[7, 8]` to nonexistent references produces **no** record (`rc=0`) — a
  false pass of the RPT-311 bidirectional rule.

**Fix:** parse a citation group (`[1]`, `[1, 6]`, `[1-3]`) and expand it before the
RPT-311/RPT-312 set comparison, or explicitly document that only the single-number form is
supported and reject the combined form rather than silently mis-handling it.

#### WR-08: The report template omits the `**Native suite.**` paragraph that RPT-407 requires

**File:** `templates/report/report.md:83-96`
**Issue:** `test_status_claim_records` in `scripts/report/contract.py:1147-1158` requires a
section-7 paragraph beginning `**Native suite.**` or `**Native tests.**` whenever
`tests.native is true`. Both `templates/homework-arduino/homework.yaml` and
`templates/homework-espidf/homework.yaml` set `tests.native: true`, but the report skeleton
contains no such paragraph and no TODO prompt for it (verified by grep; the template does
prompt for `Industry note:` and `Status:`). The first flip to `report.status: draft` therefore
fails RPT-407 until the author invents the paragraph, and the template does not teach it.
**Fix:** add a `**Native suite.** TODO …` paragraph to section 7 (and a `**Simulation.**`
prompt for the optional block), and pin it with a template-parity assertion so the template
and the rule cannot drift.

#### WR-09: The size bounds are enforced after the whole file is read, and `homework.yaml` has no bound at all

**File:** `scripts/check_report.py:104-108`, `scripts/check_report.py:233`,
`scripts/report/contract.py:1324-1333`
**Issue:** `_read_diagram` and `_validate_directory` call `read_regular_text` (a full read)
and only then compare `len(text.encode("utf-8"))`; `validate_report` does the same for the
report. The gate therefore does not bound I/O. `homework.yaml` is read with no bound
whatsoever, while `check_metadata` caps metadata at `MAX_INPUT_BYTES = 64 * 1024`
(`scripts/metadata/contract.py:209-210`). A multi-gigabyte report, diagram or metadata file
is fully materialized before the bound can reject it, contradicting the comment that "the
payload is bounded by the same size gate".
**Fix:** check the file size (or stream with a cap) before reading, return RPT-004/RPT-001 on
an oversized input, and apply the same 64 KiB metadata bound in `check_report.py`.

#### WR-10: `scripts/report/contract.py` performs filesystem I/O, contradicting its documented boundary

**File:** `scripts/report/contract.py:202-231` (and module docstring `:1-13`)
**Issue:** The module docstring says "The report contract rules, free of file I/O and
third-party imports (D-02)", and the phase rule is that only `scripts/check_report.py` may
perform file I/O. `resolve_artifact` calls `candidate.exists()` and `os.path.realpath(...)`
on every artifact token. The checks are read-only, but they are I/O, and they make the rule
module depend on the ambient filesystem (and on the current working directory for a relative
root). The unit tests exercise `resolve_artifact` in-process, which hides the boundary drift.
**Fix:** inject a resolver callable from `check_report.py` into `validate_report`, keeping the
contract module pure (or amend the docstring and the phase rule to say "no file reads/writes;
existence checks are allowed").

### Info

#### IN-01: Evidence tokens are over-broad; a URL or prose token in a backticked span is treated as a path

**File:** `scripts/report/contract.py:179-181`, `scripts/report/contract.py:234-243`
**Issue:** `path_like` returns true for any token containing `/`, and `artifact_tokens` yields
every whitespace-separated token inside a backticked span. A traceability `Evidence` cell
containing `` `https://example.invalid/run` `` is therefore resolved as a path and rejected
with RPT-307 (reproduced). Prose such as `` `on/off` `` has the same effect. The contract says
external URLs are never fetched, but this rule turns a URL in an evidence cell into a false
error.
**Fix:** ignore scheme-bearing tokens (reuse `EXTERNAL_SCHEME`) and obviously non-path prose,
or require an explicit path prefix for artifact tokens.

#### IN-02: Report-derived strings are printed without control-character sanitization

**File:** `scripts/report/contract.py:676`, `:807`, `:871`; `scripts/check_report.py:338`
**Issue:** RPT-301/307/308/404 reasons interpolate raw normalized cells and tokens, and the
record path comes from the filesystem. `normalize_cell` collapses whitespace but does not
remove ANSI escapes or other control characters, so a committed report can inject terminal
escape sequences into a developer's or CI runner's output when the checker prints a record.
**Fix:** strip or `repr`-escape control characters (and the path) before printing.

#### IN-03: The checker passes vacuously when `homeworks/` is absent

**File:** `scripts/check_report.py:268-278`, `:340-345`
**Issue:** With no positionals and no `<root>/homeworks` directory, `_directories` returns
`[]` and `main` prints `PASS: report contract satisfied` with exit 0. A sparse checkout or a
mistyped `--dir` reports a clean gate over zero documents. `RealTreeTests` guards the shipped
tree, but the tool itself does not.
**Fix:** fail (exit 2) or emit a record when the default scan finds no homework directory.

#### IN-04: Symlink handling is inconsistent for `homework.yaml` and for `homeworks/<id>`

**File:** `scripts/check_report.py:123`, `scripts/check_report.py:270-278`
**Issue:** `_read_metadata` uses `Path.read_text`, which follows a symlinked `homework.yaml`
(reproduced: a metadata symlink pointing outside the root passes), and the default scan uses
`iterdir()`/`is_dir()`, which follow a symlinked homework directory. The report and diagram
reads refuse symlinks, and `new_homework` refuses a symlinked target, so the posture differs
inside one tool set.
**Fix:** use `read_regular_text` for metadata and `lstat` the scanned directories, matching
the rest of the phase.

#### IN-05: The worked example cites a nonexistent "section 11"

**File:** `homeworks/1_3-police-flasher/report.md:351-352`
**Issue:** Rows T-16 and T-17 say the limitation statements live in "sections 4 and 11"; the
document has no section 11 (the second location is the `## Decision Appendix`). The lines are
pre-existing context rather than additions in this diff, but the retrofitted report is the
worked example authors are told to copy.
**Fix:** change both references to "section 4 and the Decision Appendix".

#### IN-06: The `check-report` hook scope omits the metadata helpers the checker imports

**File:** `.pre-commit-config.yaml:203-207`
**Issue:** The hook comment claims `files` "names every input the contract reads … the
checker and its helpers", but the pattern omits `scripts/metadata/`, while
`check_report.py` imports `resolve_root`/`relative_path` from `scripts.metadata.paths` and
`read_regular_text`/`StrictSafeLoader` from `scripts.metadata.render`/`yaml_loader`. A change
to `read_regular_text` (symlink posture) or `relative_path` (record path) will not re-run the
local hook. CI's `--all-files` still catches it.
**Fix:** add `scripts/metadata/` to the pattern, or narrow the comment to what the pattern
actually covers.

#### IN-07: The documented record format and the self-audit checklist do not match the CLI

**File:** `docs/standards/report.md:37`, `docs/standards/report.md:259-296`;
`scripts/check_report.py:337`
**Issue:** The standard says every record prints `path:line: STATUS [RULE] — reason`, but an
`OK` record prints `path:line: OK — reason` (no rule suffix). The self-audit checklist also
omits the References section even though the standard lists a References requirement.
**Fix:** document the `OK` form and add the References item (or point it at the new rule from
WR-04).

#### IN-08: Reference-style links and autolinks are not resolved, although the standard says every link must be

**File:** `scripts/report/contract.py:169`, `scripts/report/contract.py:287-303`
**Issue:** `INLINE_LINK` matches only `[text](target)` and `![alt](target)`. A reference-style
link (`[text][ref]` plus a `[ref]: path` definition) or an autolink (`<assets/x>` or
`<https://…>`) is never collected, so a missing relative target behind a reference-style link
passes. The standard's cross-file rule says "Every relative Markdown link and image target
resolves" without limiting the form.
**Fix:** either document the inline-only subset in the standard, or resolve reference
definitions and autolinks as well.

#### IN-09: RPT-407/RPT-408 token matching is case-sensitive and negation-blind

**File:** `scripts/report/contract.py:174-176`, `:1179-1200`
**Issue:** `RUN_CLAIM_TOKENS` are the lowercase substrings `"exited 0"` and
`"scenario passed"`, tested with `in`. A pending paragraph that honestly says "no run has
exited 0 yet" is flagged as claiming a run (RPT-408), and a verified paragraph that says
"Exited 0" or "scenario  passed" (double space) is flagged as not claiming one. The same
literal-prefix brittleness applies to `**Native suite.**`.
**Fix:** document the exact literal tokens as the contract, or match case-insensitively and
reject the negative phrasing explicitly (for example, require a structured sentence form).

---

_Reviewed: 2026-10-27T15:26:45Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
