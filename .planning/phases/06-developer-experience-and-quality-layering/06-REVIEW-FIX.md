---
phase: 06-developer-experience-and-quality-layering
fixed_at: 2026-10-26T11:45:27Z
review_path: .planning/phases/06-developer-experience-and-quality-layering/06-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 06: Code Review Fix Report

**Fixed at:** 2026-10-26T11:45:27Z
**Source review:** `.planning/phases/06-developer-experience-and-quality-layering/06-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 5 (CR-01, CR-02, WR-01, WR-02, WR-03)
- Fixed: 5
- Skipped: 0

## Fixed Issues

### CR-01: `HeaderFilterRegex` discarded every header diagnostic

**Files modified:** `.clang-tidy`, `scripts/tests/test_tooling_config.py`
**Commit:** `476c5fa`
**Applied fix:** `HeaderFilterRegex` is now `"(^|/)(lib|homeworks)/.*"`, which
matches both the repository-relative form and the absolute `FileEntry` path
clang emits for the database's absolute include directories. `ClangTidyConfigTests`
gained a regression probe that compiles the committed pattern and requires it to
match every header sample in both forms with `re.search` (mirroring clang-tidy's
unanchored `Regex::match`), plus a negative check for a system header.

**Runtime probe (not part of the unit suite):** with pinned clang-tidy 23.1.3, a
`readability-else-after-return` violation injected into
`lib/common/include/common/probe_header.h` was printed when the translation unit
that includes it was analysed under the committed config, and was reported as
"Suppressed 1 warnings (1 in non-user code)" under the old
`--header-filter='^(lib|homeworks)/.*'`. Temporary probe files were removed and
the working tree is clean.

### CR-02: a header-only push passed the pre-push gate with no analysis

**Files modified:** `.pre-commit-config.yaml`, `AGENTS.md`,
`docs/decisions/0013-clangd-multi-root-contract.md`, `scripts/clang-tidy-hook`
(new), `scripts/tests/test_tooling_config.py`
**Commit:** `9d7e4e7`
**Applied fix:** took the review's narrow-contract option. Both pre-push `files`
patterns are now `^(lib/(common|host)/src/.*\.c)$`; the clang-tidy hook `entry`
is overridden with `scripts/clang-tidy-hook`, which (a) reads the compilation
database and fails before running when a source argument has no command, and
(b) fails when cpp-linter output contains `Compile command not found`.
`AGENTS.md`, ADR 0013, and the guide now state that headers are analysed only
through an including translation unit and that a header-only change is not
analysed locally.

**Review premise correction:** the review says pinned clang-tidy prints
`Skipping <file>. Compile command not found.` On 23.1.3 the skip is completely
silent — exit 0 with no stdout or stderr. The silent no-op defect does
reproduce, and marker detection alone would not fix it, so the database
membership pre-check is the primary guard and the marker check covers older
builds. Verified end to end: `pre-commit run clang-tidy --hook-stage pre-push
--files lib/common/src/probe_skip.c` fails with the `FAIL clang-tidy:` remedy,
and the same hook passes over the real described set.

### WR-01: the database guard passed when a new source was missing

**Files modified:** `scripts/clang-tidy-db`, `scripts/tests/test_tooling_config.py`
**Commit:** `9c4e0fb`
**Applied fix:** the guard now compares the database's resolved `file` set with
every existing `.c` under `lib/common/src` and `lib/host/src`. A scoped source
the database does not describe exits 1 with the existing regeneration remedy;
headers are deliberately excluded. Added
`test_a_new_scoped_source_absent_from_the_database_exits_one` with the new
source's mtime set *older* than the database, so only the description check can
fail it, and `test_a_header_absent_from_the_database_is_not_stale`.

### WR-02: the wrapper could select a non-executable esp-clangd

**Files modified:** `scripts/clangd-wrapper.sh`, `scripts/tests/test_tooling_config.py`
**Commit:** `b366eac`
**Applied fix:** discovered esp-clangd candidates are filtered with `[ -x ]`
before the newest one is selected, so a partially installed newest build falls
back to an executable older build, and a tree with no executable candidate
still exits 2 with `FAIL clangd-wrapper:`. The iteration is guarded by the array
count because bash 3.2 treats an empty `"${array[@]}"` as unbound under
`set -u`. Added two cases: only-candidate non-executable exits 2 without
`Permission denied`, and non-executable newest falls back to the executable one.

### WR-03: the onboarding guide overstates what is pinned and the hook count

**Files modified:** `docs/standards/vscode.md`, `scripts/tests/test_tooling_config.py`
**Commit:** `b434aa7`
**Applied fix:** the guide now says the *gate's* formatters and linters are
pinned and that esp-clangd is the one hand-installed editor component; the hook
section states 13 commit hooks and 2 push hooks and lists every declared hook as
a bullet with its remedy. `test_the_guide_lists_every_hook` derives the ids from
`.pre-commit-config.yaml` (so a new hook cannot be undocumented) and asserts the
bullet form, which also closes IN-03's `clang-tidy`/`clang-tidy-db` substring
hole; `test_the_guide_states_the_real_hook_counts` derives the counts from the
config's stages.

## Verification

All gates ran in the isolated review-fix worktree
(`.claude/worktrees/rf-06-99419-1793014449`), not in the main checkout, against
the committed state (`b434aa7`):

| Command | Result |
|---------|--------|
| `python3 -m unittest discover -s scripts/tests` | 353 tests, OK |
| `pre-commit run --all-files` | all 13 hooks pass |
| `pre-commit run --all-files --hook-stage pre-push` | both hooks pass |
| `python3 scripts/clang-tidy-db` (worktree) | PASS, exit 0 |
| `uv run scripts/gen_views.py --all --check` | all views UNCHANGED, exit 0 |

The worktree has no build output, so `tests/compile_commands.json` was copied
from the main checkout with its absolute paths rewritten to the worktree root
(the file is gitignored and was not committed). The guard was additionally run
from the worktree script against the **main checkout** database —
`python3 <worktree>/scripts/clang-tidy-db --dir /Users/vloktiev/Dev/miltech/homeworks`
— and printed PASS with exit 0. `pre-commit` used `PRE_COMMIT_HOME` under the
project cache, so the cpp-linter/clang-tidy environments were local to this
repository.

## Notes

- No finding was skipped.
- IN-01 through IN-05 were out of the requested scope and were not changed,
  except that the WR-03 test now matches the bullet form (IN-03's observation)
  as a side effect.
- `REVIEW-FIX.md` is intentionally left uncommitted for the orchestrator.

---

_Fixed: 2026-10-26T11:45:27Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
