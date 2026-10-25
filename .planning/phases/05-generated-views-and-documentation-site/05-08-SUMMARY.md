---
phase: 05-generated-views-and-documentation-site
plan: "08"
subsystem: docs
tags: [mkdocs-material, nav-generation, mkdocs-config, katex-pins, stdlib-tests, drift-check]

requires:
  - phase: 05-generated-views-and-documentation-site
    plan: "03"
    provides: "the gen_views.py spine: loader, whole/region classifier, manifest writer and drift reporter"
  - phase: 05-generated-views-and-documentation-site
    plan: "06"
    provides: "the vendored KaTeX 0.19.0 tree and its byte-integrity gate"
  - phase: 05-generated-views-and-documentation-site
    plan: "07"
    provides: "docs/index.md, docs/homeworks/ and docs/boards/ — every page the nav must list"
provides:
  - "templates/views/mkdocs.yml.tmpl — the single reviewed owner of the whole site configuration"
  - "scripts/gen_views.py — the nav view, the three nav fragments and the frontmatter-aware ADR label extractor"
  - "mkdocs.yml — the generated Material 9.7.7 configuration with a four-section nav, drift-checked by --all --check"
  - "scripts/tests/test_docs_pins.py — PinConsistencyTests: pins, theme/plugin constraints, KaTeX paths and nav completeness"
  - "scripts/tests/test_gen_views.py — NavTests including the real-tree --all contract"
affects: ["05-09-site-build-and-publication"]

actuals:
  tokens: 7379
  tasks: 2
  commits: 2
  plan_head_before: a5e74412904e7f0671d1548b6e6e7f11f9651cf3
  plan_head_after: 417c96fe5d9561811f1829d66ef7d0902a910adc

tech-stack:
  added:
    - "MkDocs Material 9.7.7 configuration generated from one reviewed template (the pins already existed)"
  patterns:
    - "one reviewed template owns the whole mkdocs.yml; every nav fragment is pre-rendered text (D-20)"
    - "nav labels from the first ATX heading after the YAML frontmatter, quote-neutralized for a double-quoted YAML scalar"
    - "line-based nav matcher behind an explicit ASCII docs-relative path contract"
    - "requirements, theme, KaTeX path and nav coverage cross-checked from stdlib only"

key-files:
  created:
    - templates/views/mkdocs.yml.tmpl
    - mkdocs.yml
  modified:
    - scripts/gen_views.py
    - generated.manifest
    - scripts/tests/test_gen_views.py
    - scripts/tests/test_docs_pins.py
    - docs/index.md

key-decisions:
  - "Every nav entry, the four section headers included, is written `- \"<label>\": <path>` so one shape covers the block and the separator colon stays outside the quotes (Pitfall 1)."
  - "Decision labels come from the first `# ` heading after the frontmatter block; a heading containing a double quote becomes a single quote, and a file with no heading falls back to the title-cased filename slug."
  - "A symlinked file under docs/decisions/ is refused (exit 2) rather than followed, so a nav entry can never point outside the authored directory."
  - "The authored site-home link now names decisions/README.md: the directory form is an unrecognized relative link under `validation.links.unrecognized_links: warn` and fails --strict."
  - "`nav --check` is a drift check only; the strict build stays a separate command and a separately named CI step in 05-09."

patterns-established:
  - "A whole-file YAML view is rendered from a template, never dumped from a dict, so review sees the exact committed bytes."
  - "A fragment placeholder sits at column zero while the generated lines carry their own indentation, so one template serves 4-space and 6-space nesting."
  - "A line-based matcher is allowed only after asserting that every path it must represent fits its character contract."

requirements-completed: [META-05, META-08]

coverage:
  - id: D1
    description: "mkdocs.yml is generated whole from templates/views/mkdocs.yml.tmpl and carries exactly the Home, Homeworks, Boards and Decisions sections in order."
    requirement: META-05
    verification:
      - kind: unit
        ref: "scripts.tests.test_gen_views.NavTests.test_the_four_sections_appear_once_in_order"
        status: pass
      - kind: e2e
        ref: "uv run scripts/gen_views.py nav --check"
        status: pass
    human_judgment: false
  - id: D2
    description: "The nav lists every Markdown file under docs/ exactly once: index.md, the homework page, the board page, decisions/README.md and the eleven ADRs."
    requirement: META-05
    verification:
      - kind: unit
        ref: "scripts.tests.test_docs_pins.PinConsistencyTests.test_nav_lists_every_markdown_file_under_docs"
        status: pass
      - kind: unit
        ref: "scripts.tests.test_gen_views.NavTests.test_every_homework_board_and_decision_target_appears_once"
        status: pass
    human_judgment: false
  - id: D3
    description: "Decision labels come from the first heading after frontmatter; quote, colon, frontmatter/no-frontmatter and no-heading fixtures all render a valid single-line entry."
    requirement: META-05
    verification:
      - kind: unit
        ref: "scripts.tests.test_gen_views.NavTests.test_frontmatter_and_prose_only_files_label_from_their_heading"
        status: pass
      - kind: unit
        ref: "scripts.tests.test_gen_views.NavTests.test_a_quoted_heading_becomes_a_single_quote_label"
        status: pass
      - kind: unit
        ref: "scripts.tests.test_gen_views.NavTests.test_a_heading_with_a_colon_stays_one_valid_entry"
        status: pass
      - kind: unit
        ref: "scripts.tests.test_gen_views.NavTests.test_a_file_without_a_heading_falls_back_to_the_title_cased_slug"
        status: pass
    human_judgment: false
  - id: D4
    description: "PinConsistencyTests cross-checks the three exact pins, material with no custom_dir, search as the only plugin, no hooks or INHERIT, and the exact KaTeX stylesheet and three scripts from stdlib only."
    requirement: META-08
    verification:
      - kind: unit
        ref: "scripts.tests.test_docs_pins.PinConsistencyTests"
        status: pass
    human_judgment: false
  - id: D5
    description: "`mkdocs build --strict` exits 0 against the generated tree and writes only into the gitignored site/ directory."
    requirement: META-08
    verification:
      - kind: e2e
        ref: "uv run --python 3.13 --with-requirements requirements-docs.txt mkdocs build --strict"
        status: pass
    human_judgment: false
  - id: D6
    description: "A second nav run reports only UNCHANGED, a hand edit makes nav --check exit 1 and writes nothing, and a full --all --check is clean on the real tree."
    requirement: META-05
    verification:
      - kind: unit
        ref: "scripts.tests.test_gen_views.NavTests.test_a_second_run_reports_only_unchanged"
        status: pass
      - kind: unit
        ref: "scripts.tests.test_gen_views.NavTests.test_a_hand_edit_is_modified_drift_and_check_writes_nothing"
        status: pass
      - kind: unit
        ref: "scripts.tests.test_gen_views.NavTests.test_real_tree_all_check_is_clean"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 08: Generated Site Configuration Summary

**`mkdocs.yml` is now generated whole from one reviewed template: a four-section nav covering all 15 pages under `docs/`, ADR labels taken from the first heading after frontmatter, a warnings-as-errors build that exits 0, and stdlib-only pin and nav-completeness tests.**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-10-26T00:44:47+02:00 (worktree base `a5e7441`)
- **Completed:** 2026-10-26T00:47:18+02:00
- **Tasks:** 2
- **Files modified:** 7 (2 created, 5 modified)
- **Commits:** 2 (measured: `git rev-list --count a5e7441..HEAD`)

## Accomplishments

- `templates/views/mkdocs.yml.tmpl` reproduces the RESEARCH skeleton field for field: project `site_url`, Material with the three features and two palette entries, `plugins: [search]`, the strict `validation:` block, the full `markdown_extensions` list including `pymdownx.arithmatex` with `generic: true`, and the three vendored KaTeX `extra_javascript` entries after the single `extra_css` entry.
- The `nav` view builds three pre-rendered fragments: homework entries in `_load_homeworks` order, board entries sorted by id, and ADR entries from a sorted `docs/decisions/*.md` scan. Labels are quoted, the separator colon is unquoted, and the two nesting depths are carried by the fragment lines.
- ADR labels skip the YAML frontmatter block before taking the first `^#\s+(.+)$` heading, replace a double quote with a single quote, and fall back to the title-cased filename slug; quote, colon, frontmatter, no-frontmatter and no-heading fixtures are each asserted.
- `PinConsistencyTests` proves the three exact pins (with no hashes or extras), Material without `custom_dir`, `search` as the only plugin, no `hooks:`/`INHERIT:`, the exact `assets/vendor/katex/0.19.0/katex.min.css` and the three scripts in order, and that `docs/assets/vendor/katex/` has exactly the `0.19.0` child.
- The nav matcher's contract is asserted first: every `*.md` path under `docs/`, as a docs-relative POSIX path, matches `^[A-Za-z0-9_./-]+$`; the target set then equals the set of docs Markdown files with no duplicates and no whole-entry quoted scalar.
- `mkdocs build --strict` is green on the real tree; `nav --check` and `--all --check` report every view UNCHANGED. The suite grew from 239 to 264 tests.

## Task Commits

1. **Task 1: Generate the whole site configuration and build it with warnings as errors** — `6633238` (feat): the template, the `nav` view and fragments, `mkdocs.yml`, the manifest entry, `NavTests`, and the site-home link fix.
2. **Task 2: Cross-check the docs pins, the theme constraints and the nav coverage from stdlib only** — `417c96f` (test): `PinConsistencyTests` and the real-tree `--all` assertion.

**Plan metadata:** committed with this SUMMARY (docs).

## Files Created/Modified

- `templates/views/mkdocs.yml.tmpl` — the single reviewed owner of the whole site configuration; placeholders `{{homework_nav_entries}}`, `{{board_nav_entries}}`, `{{decision_nav_entries}}`.
- `mkdocs.yml` — the generated Material 9.7.7 configuration with the four-section nav.
- `scripts/gen_views.py` — `_nav_label`, `_decision_label`, `_homework_nav_entries`, `_board_nav_entries`, `_decision_nav_entries`, `_render_nav`; `nav` registered in `RENDERERS`.
- `generated.manifest` — one `owner: "nav"`, `mode: "whole"` entry for `mkdocs.yml`.
- `scripts/tests/test_gen_views.py` — `NavTests` (11 cases, including the real-tree `--all` contract).
- `scripts/tests/test_docs_pins.py` — `PinConsistencyTests` (14 cases) and the module-level pin/KaTeX/nav constants.
- `docs/index.md` — the authored ADR-index link now names `decisions/README.md` (deviation fix, outside the generated region).

## Decisions Made

- **One quoted shape for the whole nav block.** Section headers and child entries both use `- "<label>": <path>`, while `- "Homeworks":`/`- "Boards":`/`- "Decisions":` remain key-only section nodes. The line-based matcher can therefore accept exactly one entry form, and the separator colon is never swallowed into a scalar.
- **Frontmatter is skipped before the heading scan.** Every real ADR opens with a `---` block, so a first-line scan would label pages `status: accepted`; the skip rule plus fixtures with and without frontmatter pins the correct label.
- **A symlinked ADR is refused rather than followed.** The generator only reads that directory, but a symlink would let a nav entry name a page outside `docs/decisions/`, so it is an exit-2 environment error consistent with the rest of the loader.
- **`nav --check` is drift only.** The strict build is a separate command here and a separately named CI step in 05-09; the plan and tests never claim that a clean drift check proves the site builds.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed the site-home link that the strict build rejects**
- **Found during:** Task 1 (first `mkdocs build --strict` run)
- **Issue:** The authored `docs/index.md` linked `[decision records](decisions/)`. MkDocs treats that as an unrecognized relative link, and `validation.links.unrecognized_links: warn` plus `--strict` promotes the warning to a build failure. The page itself is authored, so this was outside the plan's `files_modified`.
- **Fix:** The link now names `decisions/README.md`, the real file; MkDocs still publishes it as the directory index, and the warning is gone. The edit is outside the generated marker region, so `docs --check` remains UNCHANGED.
- **Files modified:** `docs/index.md`
- **Verification:** the strict build exits 0; `--all --check` reports every view UNCHANGED; the full 264-test suite is green.
- **Committed in:** `6633238` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Necessary for the plan's own acceptance criterion (a green `--strict` build). No scope creep: one authored link target changed, no generated behaviour weakened.

## Issues Encountered

- The first `nav` render emitted `decisions/<file>.md.md` because the entry builder appended `.md` to an already-suffixed filename. Caught by inspecting the generated file before commit and fixed in the same task; `PinConsistencyTests` now asserts the exact target set so the class cannot recur silently.
- The worktree harness wraps `git` for several subcommands, so `/usr/bin/git` was used for status, add and commit, matching the workaround recorded in 05-03, 05-05, 05-06 and 05-07.
- `uv run --python 3.13 --with-requirements requirements-docs.txt` prints Material's MkDocs 2.0 banner on stderr but exits 0; Pitfall 10 documents this as informational, not a warning (verified again here).

## Known Stubs

None. Every earlier `nav is not implemented in this plan` refusal is now replaced by the real view, and the generated `mkdocs.yml` lists every docs page.

## Threat Flags

None beyond the plan's register. T-5-22 (frontmatter-aware labels, quote neutralization, fixtures), T-5-23 (one template, no plugin beyond `search`, no `hooks:`/`INHERIT:`/`custom_dir`), T-5-24 (ASCII path contract asserted before matching, set equality, named omissions) and T-5-SC (no package installed; the build uses only the three named pins) are each implemented and covered by a discriminating test.

## User Setup Required

None — no external service configuration required. The strict build is a local command and uses the already-pinned docs requirements.

## Next Phase Readiness

- 05-09 can add the separate `docs` CI step and Pages deployment over a configuration that already exits 0 under `--strict`.
- `PinConsistencyTests` will fail locally if a pin, the KaTeX version or a nav entry drifts, and `nav --check` covers the theme, extensions, plugins and navigation in one comparison.
- `generated.manifest` now carries the `nav` entry, so `--all --check` covers the whole generated surface.
- No blockers.

## Self-Check: PASSED

- Created files present: `templates/views/mkdocs.yml.tmpl`, `mkdocs.yml`; modified `scripts/tests/test_docs_pins.py`, `scripts/tests/test_gen_views.py`.
- Task commits on HEAD: `6633238`, `417c96f`.
- `python3 -m unittest discover -s scripts/tests` → 264 tests, OK.
- `uv run scripts/gen_views.py --all --check` → exit 0, every view UNCHANGED.
- `uv run --python 3.13 --with-requirements requirements-docs.txt mkdocs build --strict` → exit 0.
- `git check-ignore -q site` → exit 0.

---
*Phase: 05-generated-views-and-documentation-site*
*Completed: 2026-10-26*
