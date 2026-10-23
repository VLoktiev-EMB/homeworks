---
phase: 01-repository-foundation-and-policy-gate
plan: 02
subsystem: infra
tags: [gitignore, gitattributes, git-lfs, ignore-patterns, git-check-ignore, git-check-attr, python-unittest]

# Dependency graph
requires:
  - phase: 01-01
    provides: "scripts/tests/ package and the python3 -m unittest discovery convention; git-lfs 3.8.1 installed"
provides:
  - ".gitignore — category-grouped coverage for build output, generated files, Python caches, secrets, OS/editor junk, video containers, and .planning/research/.cache/"
  - ".gitattributes — LFS routing for the eight D-20 extensions plus explicit text/binary treatment for site assets"
  - "scripts/tests/test_gitignore.py — 10 tests that ask git check-ignore / git check-attr rather than reading the files as text"
  - "research cache untracked (5 JSONs removed from the index, still on disk)"
affects: [01-03, phase-08-ci, every later plan that adds an asset or a generated file]

actuals:
  tokens: 3624
  tasks: 2
  commits: 2
  plan_head_before: 76110a09422d192d0b0317b313f02b1d33855c42
  plan_head_after: d3cffb89b2def4a9527220ce2b7b4dc22c1b717f

tech-stack:
  added: []
  patterns:
    - "Gitignore/attribute assertions ask git (check-ignore, check-attr) instead of grepping the config file, so a pattern that looks right but does not match still fails"
    - "An ignore rule and the `git rm --cached` that activates it land in the same commit; either half alone is inert"
    - "Route by extension only: eight LFS extensions, everything else under the pre-commit size guard. No exclusion regexes."

key-files:
  created:
    - .gitignore
    - .gitattributes
    - scripts/tests/test_gitignore.py
  modified: []

key-decisions:
  - "LFS routing is declared before any binary exists, because .gitattributes can be edited later but the blobs it would have caught cannot be removed from a public history (D-12/D-18)."
  - "Page-served assets stay normal git objects: GitHub Pages cannot serve LFS, so routing png/jpg/jpeg/webp/svg to LFS would break the site build."
  - "No exclusion list for check-added-large-files. LFS-tracked files are filtered by that hook before the size test, so routing — not a wider threshold — is what lets a legitimate large binary through (RESEARCH Pitfall 4)."
  - "The research cache is ignored but .planning/ stays tracked: the plan record is the project's audit trail, the retrieval cache is an input."
  - "The `.md` text assertion accepts git's `auto` as well as `set`; the authoritative .gitattributes carries no `*.md` rule, only the global `* text=auto eol=lf`, and git reports that as `auto`."

patterns-established:
  - "Throwaway pathnames: git check-ignore and git check-attr resolve patterns without the file existing, so the suite never creates fixture artifacts."

requirements-completed: [FOUND-07, FOUND-08]

coverage:
  - id: D1
    description: ".gitignore covers every D-21 category: build output, generated files, Python caches, secrets (with the .env.example carve-out), OS/editor junk, video containers"
    requirement: FOUND-07
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_gitignore -v#TestGitignorePatterns.test_ignored_categories"
        status: pass
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_gitignore -v#TestGitignorePatterns.test_visible_paths_are_not_ignored"
        status: pass
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_gitignore -v#TestGitignorePatterns.test_env_example_is_the_only_secret_carve_out"
        status: pass
    human_judgment: false
  - id: D2
    description: ".planning/research/.cache/ ignored and the five cached JSONs removed from the index in the same commit; the files remain on disk"
    requirement: FOUND-07
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_gitignore#TestGitignorePatterns.test_research_cache_has_no_tracked_files"
        status: pass
      - kind: integration
        ref: "git ls-files .planning/research/.cache/ — empty"
        status: pass
      - kind: manual_procedural
        ref: "ls .planning/research/.cache/ — 5 files still present after git rm --cached"
        status: pass
    human_judgment: false
  - id: D3
    description: "LFS routing for exactly the eight D-20 extensions; page-served images and video containers are not LFS-routed; raster images are binary and svg is LF text"
    requirement: FOUND-08
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_gitignore -v#TestLfsRouting (6 tests)"
        status: pass
      - kind: integration
        ref: "git check-attr filter -- artifact.{pdf,step,stl,fzz,zip,bin,elf,vcd} — all `filter: lfs`"
        status: pass
      - kind: integration
        ref: "git check-attr filter -- docs/assets/sample.{png,jpg,jpeg,webp,svg} report/{video.mp4,clip.mov} — all `unspecified`"
        status: pass
    human_judgment: false

duration: ~2min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 02: Day-One Hygiene Surface Summary

**`.gitignore` and `.gitattributes` committed before the first asset: secrets, build output, and video containers excluded; eight binary extensions routed to LFS while page-served images stay normal git objects — with git itself, not a grep, proving both contracts.**

## Performance

- **Duration:** ~2 min (start timestamp captured after context loading)
- **Started:** 2026-10-23T17:13:28Z
- **Completed:** 2026-10-23T17:14:53Z
- **Tasks:** 2 of 2 complete
- **Files modified:** 3 created, 5 index entries removed

## Accomplishments

- `.gitignore` covers all seven D-21 categories in the research's exact order and
  wording, including the `!.env.example` negation that keeps the one legitimate env
  file visible.
- `.planning/research/.cache/` ignored **and** its five tracked JSONs untracked in the
  same commit — the ignore rule alone would have been inert while the index still held
  them.
- `.gitattributes` routes exactly the eight D-20 extensions through
  `filter=lfs diff=lfs merge=lfs -text`, marks raster images binary, and declares svg
  as LF text so the docs site keeps working without LFS.
- `scripts/tests/test_gitignore.py` (10 tests) turns pattern drift into a failing
  build. It asks `git check-ignore` and `git check-attr` — reading the files as text
  would only prove a string is present, not that it matches.
- Negative cases are asserted as deliberately as positive ones: `.env.example`,
  `README.md`, the smoke-test script, `.planning/ROADMAP.md`, and a homework README must
  stay visible, because an over-broad pattern is as damaging as a missing one.

## Task Commits

1. **Task 1: .gitignore + untrack the research cache** — `a4ce83c` (feat)
2. **Task 2: .gitattributes — LFS routing declared day one** — `d3cffb8` (feat)

Both tasks ran test-first: the failure counts before the config existed were 27 and 14
respectively (RED), then 4/4 and 10/10 green.

## Verified routing table

`git check-attr filter -- <path>` against the committed `.gitattributes`:

| Extension | filter | Rationale |
|---|---|---|
| `.pdf` `.step` `.stl` `.fzz` `.zip` `.bin` `.elf` `.vcd` | `lfs` | large, non-diffable (D-20) |
| `.png` `.jpg` `.jpeg` `.webp` | `unspecified` | page-served; Pages cannot serve LFS |
| `.svg` | `unspecified` | text, diffable, page-served |
| `.mp4` `.mov` `.avi` `.webm` `.mkv` | `unspecified` | gitignored entirely, never added |

Text/eol treatment: `.png` `.jpg` `.jpeg` `.webp` → `text: unset` (binary macro);
`.svg` → `text: set`, `eol: lf`; `.md` → `text: auto`, `eol: lf` via `* text=auto eol=lf`.

## Research cache files untracked

Five paths, removed from the index only (`git rm --cached`), all still present on disk:

```
.planning/research/.cache/3f321a7b83ea11224c423b79561a9ad0c96b271db7a956499e3755d4b151fec7.json
.planning/research/.cache/54282e06705083d5c1be66f752d19050407bce4630eda69bd1dfc048eae37176.json
.planning/research/.cache/7d54e3949b6767eb4bdd4abfb306c2382ce58dc89c72c13d9b3bd0a1b11b0226.json
.planning/research/.cache/8004c5b5daef53f79feab40c119bea2a53cc292200032da66a7a1f89763d476e.json
.planning/research/.cache/fd2ee07b47abd8ac418b23568b605e1342158c512112650d093e90b7c5f948dc.json
```

`01-PATTERNS.md` predicted six; the tree held five at execution time.

## Files Created/Modified

- `.gitignore` — D-21 coverage plus `.planning/research/.cache/`, in seven commented groups
- `.gitattributes` — `* text=auto eol=lf`, eight LFS routes, site-asset block
- `scripts/tests/test_gitignore.py` — 10 tests: `TestGitignorePatterns` (4) and `TestLfsRouting` (6)

## Decisions Made

- **No exclusion list for `check-added-large-files`.** `grep -rn
  'check-added-large-files\|exclude' .gitattributes .gitignore` returns nothing. The
  hook filters LFS-tracked files before measuring size, so routing is the mechanism that
  admits a legitimate large binary — widening the threshold or naming exceptions would
  defeat both guards at once.
- **Ignore the cache, keep the record.** `.planning/` stays tracked per Open Question 3;
  ADR-0003 (plan 01-07) must record that the planning tree is permanently public, since
  the decision cannot be undone after the first push.
- **Test through git, not through text.** `check-ignore`/`check-attr` cost one subprocess
  per case (~0.5 s for the whole module) and catch the failure mode a text assertion
  cannot: a pattern that is present but does not match.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Pre-commit git hook exists but its config file does not yet**
- **Found during:** Task 1 (first commit)
- **Issue:** `git commit` exited 1 with "No .pre-commit-config.yaml file was found".
  The hook was installed during plan 01-01's Wave-0 bootstrap, while
  `.pre-commit-config.yaml` itself is plan 01-03's deliverable — 01-03 runs in the same
  wave, so creating it here would both exceed scope and guarantee a merge conflict.
- **Fix:** committed with `PRE_COMMIT_ALLOW_NO_CONFIG=1`, the override git's own error
  message names for exactly this state. Not `--no-verify`: no hooks were skipped,
  because there are none to run yet.
- **Files modified:** none
- **Verification:** both commits report "`.pre-commit-config.yaml` config file not
  found. Skipping `pre-commit`."
- **Committed in:** `a4ce83c`, `d3cffb8`

**2. [Rule 1 - Bug] `.md` text-attribute assertion contradicted the authoritative file**
- **Found during:** Task 2 (TDD red phase)
- **Issue:** The plan's `<behavior>` says `.md` paths report `text` **set**. The
  `.gitattributes` the plan designates authoritative has no `*.md` rule — only the
  global `* text=auto eol=lf` — so git correctly reports `text: auto`. Asserting `set`
  would have forced a redundant rule and made the test disagree with the file it exists
  to protect.
- **Fix:** the assertion accepts `{"auto", "set"}` for `.md` and still asserts
  `eol: lf` strictly; `.svg` keeps the strict `text: set` assertion because it *is*
  declared explicitly.
- **Files modified:** `scripts/tests/test_gitignore.py`
- **Verification:** `TestLfsRouting.test_markdown_is_lf_text` passes; the comment above
  the assertion records why.
- **Committed in:** `d3cffb8` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug)
**Impact on plan:** Neither changed the shipped configuration. The first was an
environment/tooling ordering artifact from the parallel wave; the second corrected a
plan statement that contradicted its own authoritative source.

## Issues Encountered

- `git` on `PATH` is an `rtk` wrapper that the worktree-isolation guard cannot verify
  when it appears in a compound command; `/usr/bin/git` was used for status, add, and
  commit throughout, and plain `git` only for `rm --cached`.
- Writes to the shared `.git` directory are refused by the isolation guard, so the
  standard plan-commit ledger file could not be placed at
  `$(git rev-parse --git-dir)/gsd-plan-head-before-01-02`. The commit count and both
  head SHAs were measured directly with
  `git rev-list --count 76110a09..HEAD` (2) and two `rev-parse` calls instead; the
  values recorded in `actuals` are measured, not narrated.

## Known Stubs

None.

## Threat Flags

None — the changed files stay inside the plan's threat model. T-1-09 (LFS quota
exhaustion) is mitigated exactly as designed: only the eight declared extensions reach
LFS, and everything else stays under the 1024 kB pre-commit guard that plan 01-03 adds.
T-1-SC did not apply — nothing was installed.

## Next Phase Readiness

- Plan 01-03 can add `.pre-commit-config.yaml` with `check-added-large-files` and
  **must not** introduce an exclusion regex: LFS routing is what makes a large binary
  pass, and the absence of an exclusion list is deliberate.
- The `PRE_COMMIT_ALLOW_NO_CONFIG=1` workaround becomes unnecessary the moment that
  config file lands.
- Plan 01-07 (ADR-0003) should record: the planning tree is public by decision, and its
  retrieval cache is the only part excluded.

## Self-Check: PASSED

- `.gitignore`, `.gitattributes`, `scripts/tests/test_gitignore.py` all exist on disk.
- Commits `a4ce83c` and `d3cffb8` are ancestors of HEAD (`d3cffb8`).
- `python3 -m unittest scripts.tests.test_gitignore -v` — 10 tests, OK.
- `python3 -m unittest discover -s scripts/tests -v` — 20 tests, OK.
- `git ls-files .planning/research/.cache/` — empty.
- `git check-attr filter` — eight `lfs`, five images and two video probes `unspecified`.

---
*Phase: 01-repository-foundation-and-policy-gate*
*Completed: 2026-10-23*
