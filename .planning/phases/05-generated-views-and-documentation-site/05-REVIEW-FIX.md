---
phase: 05-generated-views-and-documentation-site
fixed_at: 2026-10-25T23:07:23Z
review_path: .planning/phases/05-generated-views-and-documentation-site/05-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 05: Code Review Fix Report

**Fixed at:** 2026-10-25T23:07:23Z
**Source review:** `.planning/phases/05-generated-views-and-documentation-site/05-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 4 (CR-01, CR-02, WR-02, WR-03)
- Fixed: 4
- Skipped: 0

The other 20 review findings (WR-01, WR-04 through WR-14, IN-01 through IN-08) were
deliberately out of scope for this run and remain open and recorded in `05-REVIEW.md`.

## Verification

All gates ran **inside the isolated review-fix worktree**
`/Users/vloktiev/Dev/miltech/homeworks/.claude/worktrees/rf-05-98310-1792969435` on branch
`gsd-reviewfix/05-98310`; the commits were fast-forwarded onto
`gsd/phase-05-generated-views-and-documentation-site` by the cleanup tail afterwards. A
worktree-environment run is therefore reproducible from the phase branch, not from a stale
main-checkout snapshot.

- `python3 -m unittest discover -s scripts/tests` — **279 tests, OK** (baseline was 272; five
  new tests were added).
- `uv run scripts/gen_views.py --all --check` — **exit 0**, eight records `UNCHANGED` on the
  real tree.
- `pre-commit run --all-files` — **all hooks passed** (gitleaks, whitespace, EOF, large
  files, generated-file guard, architecture, metadata contract, generated views).
- No generated artifact changed: the real tree reports byte-identical output after every fix.
- No schema change was required. `schema/homework.schema.json` already declares the
  `report.path` rule; the generator now re-checks that same rule instead of trusting that the
  checker ran first.

Each new test was written first and executed against the pre-fix source to prove it fails;
the captured failure and the post-fix result are recorded per finding below.

## Fixed Issues

### CR-01: Metadata reaches the published site as raw HTML — stored XSS via `title`, and unvalidated `report.path` breaks the link destination

**Files modified:** `scripts/gen_views.py`, `scripts/tests/test_gen_views.py`
**Commit:** `fd38588`
**Applied fix:** `_escape_cell` now escapes `&` first and then `<` and `>`, preserving the
existing `|`, `[` and `]` escaping, so every cell surface (homework table, docs index,
homework page, board page) inherits HTML neutralization. A new `_report_path` helper
re-checks the schema's `report.path` rule before the value enters any Markdown link
destination; it refuses rather than sanitizes, raising `CheckError` (exit 2) naming the
document. Both the relative/absolute table links in `_homework_rows` and the page's Report
bullet in `_homework_links` call it. Schema left unchanged deliberately: the generator is the
rendering trust boundary, and the schema already declares this path rule.
**Verification:** pre-fix, the three new tests produced 11 failures (raw `<img>` and `<b>`
reached README, homework page and board page; hostile `report.path` values exited 0). After
the fix all pass. `EscapeTests.test_html_metacharacters_are_escaped_and_never_live` asserts
`&amp;`, `&lt;`, `&gt;` ordering and the absence of a live tag;
`BoardPageTests.test_html_in_a_profile_field_is_escaped` covers the board surface;
`ReportPathTests.test_a_hostile_report_path_is_refused` covers `report).md`, `../escape.md`,
`/etc/passwd.md` and a backslash-bearing path through both the `readme` and `docs` views.

### CR-02: The generator follows symlinked `homework.yaml` and view templates, unlike every other input it guards

**Files modified:** `scripts/metadata/render.py`, `scripts/gen_views.py`, `scripts/tests/test_gen_views.py`
**Commit:** `a5b24ef`
**Applied fix:** Added one shared `read_regular_text` helper beside the existing `read_text`
in `scripts/metadata/render.py`. It `lstat`s the final component, refuses a symlink with
`CheckError` ("is a symlink; refusing to follow it"), refuses a non-regular file, and only
then reads UTF-8. Every generator read now goes through it: `homeworks/<id>/homework.yaml`,
all seven `templates/views/*.tmpl` reads, and the board profile read (which was already
guarded but now shares the single helper). `read_text` itself is unchanged, so the scaffold's
existing behavior and its test stay intact.
**Verification:** pre-fix, `SymlinkInputTests` produced 8 failures — a symlinked
`homework.yaml` was followed and exited 0, and each of the seven template reads followed its
symlink and exited 0. After the fix both tests pass: every case exits 2, prints no record, and
names the symlink on stderr.

### WR-02: `_nav_label` is not a YAML double-quoted-scalar encoder — a title/heading with `\` or a newline emits an invalid `mkdocs.yml`

**Files modified:** `scripts/gen_views.py`, `scripts/tests/test_gen_views.py`
**Commit:** `cdabbe5`
**Applied fix:** `_nav_label` now returns a real double-quoted YAML scalar by passing the
label through `json.dumps(..., ensure_ascii=False)`, which escapes backslashes, newlines and
control characters; the three call sites no longer add their own quotes. The pre-existing
display choice of rendering a double quote as a single quote is applied before encoding, so
every existing label stays byte-identical and the quoted-heading test remains valid.
**Verification:** pre-fix, `NavTests.test_a_backslash_and_newline_title_yields_valid_yaml`
failed with PyYAML's `found unknown escape character 'q'` while the generator exited 0 — the
exact silent breakage in the review. After the fix the generated `mkdocs.yml` loads with
`yaml.safe_load`, and the nav entry round-trips to `1.3 Alpha \q 'quoted'\nsecond line`
(the title is written as a YAML block scalar containing a backslash, a quote and a newline).
The real-tree `--all --check` stayed byte-identical.

### WR-03: A deleted generated whole file is unrecoverable — `DELETED` blocks every run and the manifest keeps listing it

**Files modified:** `scripts/gen_views.py`, `scripts/tests/test_gen_views.py`
**Commit:** `c373a31`
**Applied fix:** `_classify_produced` now takes the check flag. For a whole-file target that
a selected view still produces, a missing file is `DELETED` in check mode (still blocking and
never silently passed) and `CREATE` with the rendered payload in write mode, so the documented
`uv run scripts/gen_views.py --all` repair path recreates the file and the manifest entry is
regenerated normally. `DELETED` was removed from `BLOCKING_STATUSES` because write mode can no
longer emit it; `ERROR` and `ORPHAN` still block. Region-owned behavior is unchanged: a deleted
region file remains `ERROR` and is never recreated.
**Verification:** pre-fix, `WholeFileRecoveryTests` produced 3 failures — write mode exited 1
and left the deleted file absent for `workspace`, `shared-ini` and a `docs` page. After the
fix the test proves, for all three surfaces: check mode reports `DELETED` and exits 1;
write mode reports `CREATE`, exits 0, restores the exact original bytes and keeps the manifest
entry; a following check mode reports `UNCHANGED` and exits 0. `DriftTests` and `MarkerTests`
(including the deleted-region-file case) stay green.

## Skipped Issues

None. Every finding in this run's scope was fixed. The remaining 20 findings in
`05-REVIEW.md` were not attempted by design.

---

_Fixed: 2026-10-25T23:07:23Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
