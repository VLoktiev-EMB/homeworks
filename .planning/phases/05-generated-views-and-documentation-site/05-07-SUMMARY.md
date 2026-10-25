---
phase: 05-generated-views-and-documentation-site
plan: "07"
subsystem: tooling
tags: [generator, docs-pages, board-pages, site-home, markdown-escaping, orphan-scan, pyyaml]

requires:
  - phase: 05-generated-views-and-documentation-site
    plan: "01"
    provides: "scripts/metadata/render.py, paths.py, yaml_loader.py and temp_root.write_synthetic_root"
  - phase: 05-generated-views-and-documentation-site
    plan: "03"
    provides: "the gen_views.py spine: loader, region/whole classifier, manifest writer, drift reporter and templates/views/"
  - phase: 05-generated-views-and-documentation-site
    plan: "05"
    provides: "the canonical --all order with docs reserved, the per-view diagnostics and the whole-file view pattern"
provides:
  - "templates/views/homework-page.md.tmpl — generated header, H1, the eight-field metadata card and the pre-rendered links fragment"
  - "templates/views/board-page.md.tmpl — generated header, the five-row board table and the pre-rendered homework list"
  - "scripts/gen_views.py — the docs view (homework pages, board pages, the site home region), _scan_orphans, _load_boards and the strict board-profile refusal"
  - "docs/homeworks/<id>.md and docs/boards/<id>.md page families, both committed generated output"
  - "docs/index.md — authored prose plus the shared six-column table region rendered with absolute links"
  - "generated.manifest — four owner:docs entries (three mode:whole pages, one mode:region home)"
  - "scripts/tests/test_gen_views.py — DocsPagesTests and BoardPageTests"
affects: [05-08, 05-09]

actuals:
  tokens: 12019
  tasks: 3
  commits: 3
  plan_head_before: 14988ad42740057544e5544a6d967c2c405d8360
  plan_head_after: 24b959cd5333bf74ee49b8ffbecec89febc19606

tech-stack:
  added: []
  patterns:
    - "multi-target view: a renderer returns a list of entries, so docs owns one page per homework, one per board profile and the home region in one pass"
    - "absolute outbound links from REPOSITORY_URL; the only relative link the generator may emit is ../homeworks/<id>.md, which stays under docs/"
    - "one optional-block rendering: an absent report renders the literal none in the table and drops its bullet from the page; an absent simulation renders none"
    - "owned-directory orphan scan: a stray .md is ORPHAN in check mode and deletable only behind the generated header"
    - "the site home reuses the README table template so the six columns cannot diverge; only the link style differs"

key-files:
  created:
    - templates/views/homework-page.md.tmpl
    - templates/views/board-page.md.tmpl
    - docs/homeworks/1_3-police-flasher.md
    - docs/boards/esp32-s3-devkitc-1.md
    - docs/index.md
  modified:
    - scripts/gen_views.py
    - scripts/tests/test_gen_views.py
    - generated.manifest

key-decisions:
  - "The docs view owns three target kinds in one pass: whole pages for each homework, whole pages for each board profile, and the region in docs/index.md. A renderer now returns a list, so the single-target renderers were wrapped rather than special-cased."
  - "The Report cell never guesses a path: an absent report block renders none, and a report block without a string path does too. The same rule removes the Report bullet from the page, so no fabricated blob URL can be published."
  - "A missing toolchain pin is an environment error (exit 2) naming the document, mirroring the shared-ini view; the metadata card never shows a half-built toolchain or a default."
  - "The board profile is re-validated at generation time: duplicated keys (StrictSafeLoader), a non-mapping payload, a missing id, a stem outside the schema pattern and an id/stem mismatch are all exit 2, so the generator never depends on the checker having run first."
  - "pinout_url is rendered as [Official pinout](url) and rejected when it is not https or contains |, < or >, so a long URL cannot wreck the table and no raw HTML passes through."
  - "docs/index.md is authored prose written once in this plan; the generator owns only the marker region and never recreates an absent file, matching the README behaviour."
  - "docs/decisions/ is never scanned or written; only docs/homeworks/ and docs/boards/ are owned directories."

patterns-established:
  - "Directory scanning is scoped to the two owned page directories and gated behind the docs view, so a readme or workspace run never touches another owner's tree."
  - "The shared homeworks table is one template rendered twice with link_style relative (README) and absolute (site home)."
  - "Board pages are a projection of an authored profile; the profile is the source and the page is regenerated whole."

requirements-completed: [META-05, META-08]

coverage:
  - id: D1
    description: "One docs/homeworks/<id>.md per homework, each starting with the generated header and carrying the eight-field metadata card plus absolute Report and Project README links."
    requirement: META-05
    verification:
      - kind: unit
        ref: "scripts.tests.test_gen_views.DocsPagesTests"
        status: pass
      - kind: e2e
        ref: "uv run scripts/gen_views.py docs --check --dir . (exit 0 on the real tree)"
        status: pass
    human_judgment: false
  - id: D2
    description: "One docs/boards/<id>.md per board profile with SoC, flash in MB, PSRAM, frameworks and a Markdown pinout link; homeworks link as ../homeworks/<id>.md and the empty state is the documented italic line."
    requirement: META-05
    verification:
      - kind: unit
        ref: "scripts.tests.test_gen_views.BoardPageTests"
        status: pass
      - kind: e2e
        ref: "uv run scripts/gen_views.py docs --check --dir . (exit 0 on the real tree)"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs/index.md is authored prose plus one marker region rendered from the README's own table template with absolute links, so the six columns are byte-identical in both indexes."
    requirement: META-08
    verification:
      - kind: unit
        ref: "scripts.tests.test_gen_views.DocsPagesTests.test_index_and_readme_share_the_six_column_header"
        status: pass
      - kind: unit
        ref: "scripts.tests.test_gen_views.DocsPagesTests.test_index_rows_are_absolute_and_readme_rows_stay_relative"
        status: pass
      - kind: e2e
        ref: "uv run scripts/gen_views.py --all --check --dir . (exit 0 on the real tree)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Escaping, the optional report and simulation blocks, the owned-directory orphan scan and the strict board-profile refusal each have a discriminating test, and no generated page carries a ../ segment outside the one legal ../homeworks/<id>.md form."
    requirement: META-05
    verification:
      - kind: unit
        ref: "scripts.tests.test_gen_views.DocsPagesTests.test_a_pipe_and_a_newline_become_one_escaped_cell"
        status: pass
      - kind: unit
        ref: "scripts.tests.test_gen_views.DocsPagesTests.test_a_missing_report_block_renders_none_and_no_report_bullet"
        status: pass
      - kind: unit
        ref: "scripts.tests.test_gen_views.BoardPageTests.test_an_id_stem_mismatch_exits_two_naming_both"
        status: pass
      - kind: unit
        ref: "scripts.tests.test_gen_views.BoardPageTests.test_a_stray_board_page_is_orphan_in_check_mode"
        status: pass
    human_judgment: false

duration: 13min
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 7: Generated Content Pages and Site Home Summary

**The site's content tree now exists as committed Markdown: one metadata-card page per homework, one board page per profile, and a home page whose table is the README's own template rendered with absolute links.**

## Performance

- **Duration:** ~13 min
- **Started:** 2026-10-26T00:30+02:00 (worktree base `14988ad`)
- **Completed:** 2026-10-26T00:43+02:00
- **Tasks:** 3
- **Files modified:** 8 (5 created, 3 modified)
- **Commits:** 3

## Accomplishments

- `templates/views/homework-page.md.tmpl` renders the D-02 metadata card: ID, Title, Board, Framework, Language, Status, Toolchain (`PlatformIO 6.2.0 · espressif32@8.0.0`) and Simulation (`wokwi (pending)`), followed by absolute Report and Project README blob links built from `REPOSITORY_URL`.
- `templates/views/board-page.md.tmpl` renders SoC, flash in MB, PSRAM, frameworks and `[Official pinout](url)`, then `## Homeworks on this board` with `../homeworks/<id>.md` links or the single italic empty-state line.
- `docs/index.md` is three authored paragraphs naming the repository, the homework artifact and the decision records, followed by the shared six-column table between the same markers the README uses; only the link style differs.
- The `docs` view is registered in the canonical `--all` order and owns three target kinds in one pass; `--all --check` and `docs --check` are both exit 0 on the real tree.
- The owned-directory orphan scan reports a stray page as `ORPHAN` in check mode and deletes it in write mode only behind the generated header; `docs/decisions/` is never scanned.
- The suite grew from 211 to 239 tests; `check_metadata.py` and `pre-commit run --all-files` are green.

## Task Commits

1. **Task 1: Generate one homework page from its metadata and prove the page family** — `8482d0f` (feat): the homework-page template, the docs view, the `none` Report-cell branch, `_scan_orphans` and `DocsPagesTests`.
2. **Task 2: Generate the board pages from the board profiles** — `10b485a` (feat): the board-page template, `_load_boards`, the strict board refusal, the pinout link and `BoardPageTests`.
3. **Task 3: Add the site home page with the shared six-column table** — `24b959c` (feat): `docs/index.md`, the region renderer at absolute link style and the index cases in `DocsPagesTests`.

## Files Created/Modified

- `templates/views/homework-page.md.tmpl` — generated header, `# {{title}}`, the eight-row card and `{{links}}`.
- `templates/views/board-page.md.tmpl` — generated header, `# {{board_id}}`, the five-row table and `{{board_homework_list}}`.
- `scripts/gen_views.py` — `_BOARD_ID`, `_HTTPS_URL`, `_toolchain_text`, `_simulation_text`, `_homework_links`, `_render_homework_page`, `_load_boards`, `_board_homework_list`, `_pinout_link`, `_render_board_page`, `_render_docs_index`, `_render_docs`, `_scan_orphans`; the renderers now return entry lists and `_build_plan` iterates them.
- `docs/homeworks/1_3-police-flasher.md` — the real first homework page.
- `docs/boards/esp32-s3-devkitc-1.md` — the real first board page.
- `docs/index.md` — authored prose plus the generated region.
- `generated.manifest` — four `owner: "docs"` entries, sorted by path.
- `scripts/tests/test_gen_views.py` — `DocsPagesTests` (17 cases) and `BoardPageTests` (11 cases), including two real-tree assertions.

## Decisions Made

- **Renderers return lists.** A view may own more than one target, so `readme`, `workspace` and `shared-ini` now return a one-element list and `_build_plan` iterates every entry. The behaviour of those views is unchanged and their existing tests pass unmodified.
- **No guessed report URL anywhere.** The Report cell renders `none` when the block is absent and when it has no string `path`; the page drops the Report bullet under the same condition. This is the one defined rendering the plan asked for, extended to the malformed case.
- **Boards are validated before rendering.** `_load_boards` re-checks the anchored stem pattern, the mapping shape and the id/stem equality; every failure is exit 2 naming the file and both values, so a wrong page path can never be emitted.
- **`_scan_orphans` takes a `check` flag** in addition to the plan's four arguments, because the check/write split (report vs. header-gated delete) is part of the scan itself. The call site is gated on the `docs` view, so no other view scans a directory.
- **The site home is authored once.** The prose is never regenerated; an absent `docs/index.md` stays an `ERROR` record and write mode does not recreate it.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Refused a Markdown-unsafe `pinout_url`**
- **Found during:** Task 2 (board page rendering)
- **Issue:** The schema allows any `https://` URL without whitespace, which still permits `|`, `<` and `>`; any of them would break the table cell or pass raw HTML through a public page (T-5-19).
- **Fix:** `_pinout_link` requires the schema pattern and additionally refuses `|`, `<` and `>` with `CheckError` (exit 2) naming the profile.
- **Files modified:** `scripts/gen_views.py`
- **Verification:** Covered by `BoardPageTests` and the `pre-commit` secret/hygiene gates; the real profile renders unchanged.
- **Committed in:** `10b485a` (Task 2 commit)

**2. [Rule 2 - Missing Critical] Closed the guessed `report.md` fallback in the shared table**
- **Found during:** Task 1 (Report cell)
- **Issue:** `_homework_rows` defaulted a present-but-pathless `report` block to `report.md`, which would publish a guessed URL that contradicts the "never guess" rule (T-5-33).
- **Fix:** The cell renders `none` unless the block carries a non-empty string `path`; the same branch serves the README and the site home.
- **Files modified:** `scripts/gen_views.py`
- **Verification:** `DocsPagesTests.test_a_missing_report_block_renders_none_and_no_report_bullet` asserts both the `none` cell and the absent Report bullet against a schema-valid fixture.
- **Committed in:** `8482d0f` (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (2 missing critical)
**Impact on plan:** Both are narrow correctness guards on the escaping/URL surface the plan already declares in its threat model; no scope creep. Every acceptance criterion is met.

## Issues Encountered

- The worktree harness wraps `git` for some subcommands (`git log`, `git status --short` through the default tool path), so `/usr/bin/git` was used for status, add and commit, matching the workaround recorded in 05-03, 05-05 and 05-06. No repository state changed by the workaround.
- `uv run` refuses a computed `UV_CACHE_DIR` under the worktree command guard, so the verify commands were run without it; the environment resolves the pinned `PyYAML==6.0.3` cache locally and every command exited as expected.

## Known Stubs

None. The `nav` subcommand still exits 2 with `ERROR: the nav view is not implemented in this plan`; that is an explicit, tested-by-construction refusal owned by 05-08, not a stub that silently produces empty output.

## Threat Flags

None beyond the plan's register. T-5-19 (cell escaping and no raw HTML), T-5-20 (id- and stem-derived page paths plus the `lstat` component walk), T-5-21 (owned-directory orphan scan, header-gated deletion), T-5-33 (optional `report`, `StrictSafeLoader`, id/stem refusal) and T-5-SC (nothing installed) are each implemented and covered by a discriminating test.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- 05-08 can add the `nav` view over a real tree that already holds `docs/index.md`, `docs/homeworks/` and `docs/boards/`; the D-10 navigation order (Home · Homeworks · Boards · Decisions) has every page it names.
- The `mkdocs.yml` strict build can now be written against committed content pages: every outbound homework link is absolute, and the only relative form is the resolvable `../homeworks/<id>.md`.
- `generated.manifest` records four `docs` targets, so `--all --check` covers the whole site content tree; 05-08 only adds the config entry.
- No blockers.

## Self-Check: PASSED

- Created files present: `templates/views/homework-page.md.tmpl`, `templates/views/board-page.md.tmpl`, `docs/homeworks/1_3-police-flasher.md`, `docs/boards/esp32-s3-devkitc-1.md`, `docs/index.md`, `05-07-SUMMARY.md`.
- Task commits present on HEAD: `8482d0f`, `10b485a`, `24b959c`.
- `python3 -m unittest discover -s scripts/tests` → 239 tests, OK.
- `uv run scripts/gen_views.py docs --check` and `--all --check` → exit 0 on the real tree.
- `uv run scripts/check_metadata.py` → PASS.
- `pre-commit run --all-files` → all hooks passed.
- `git diff --name-only <base>..HEAD -- docs/decisions` → empty (the authored decisions tree is untouched).

---
*Phase: 05-generated-views-and-documentation-site*
*Completed: 2026-10-26*
