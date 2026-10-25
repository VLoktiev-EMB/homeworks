---
phase: 05-generated-views-and-documentation-site
plan: "06"
subsystem: docs
tags: [katex, mkdocs-material, vendoring, provenance, sha256, stdlib-tests]

requires:
  - phase: 04-metadata-contract-and-scaffolding
    provides: "the stdlib-only scripts/tests/ suite and the D-14 rule that no test imports PyYAML or jsonschema"
provides:
  - "docs/assets/vendor/katex/0.19.0/ — the 24 pinned distribution files, render-math.js, PROVENANCE.txt and FILES.sha256"
  - "KatexVendoringTests, KatexVendoringDiscriminationTests and RenderMathScriptTests in scripts/tests/test_docs_pins.py"
  - "a byte-integrity gate that catches a missing vendored asset MkDocs reports no warning for"
affects: [05-08-site-configuration, 05-09-site-build-and-publication]

actuals:
  tokens: 79425
  tasks: 2
  commits: 2

tech-stack:
  added:
    - "KaTeX 0.19.0 (vendored as static files, never installed into a dependency graph)"
  patterns:
    - "sha256sum -c ledger in FILES.sha256, recomputed with hashlib.sha256 in a stdlib test"
    - "discrimination tests that mutate a temp copy so a green helper cannot be a false positive"
    - "ASCII-only authored browser script as a deliberate, testable policy"

key-files:
  created:
    - "docs/assets/vendor/katex/0.19.0/ (27 files: 24 distribution, render-math.js, PROVENANCE.txt, FILES.sha256)"
    - "scripts/tests/test_docs_pins.py"
  modified:
    - ".pre-commit-config.yaml"

key-decisions:
  - "The vendored tree is excluded from trailing-whitespace and end-of-file-fixer: upstream minified JavaScript has no final newline, and normalizing it would break the ledger."
  - "Task 2's 'names no external host' is implemented as no external asset host (no CDN token and no src=); the source URL in the comment is required by Task 1."
  - "PROVENANCE.txt records the tarball URL and one-time SHA-256 so authenticity is auditable independently of the ledger the copy generated."

patterns-established:
  - "A committed checksum ledger plus a discrimination suite is the pattern for any future vendored third-party tree."
  - "Vendored bytes are never normalized by repository hooks; a hook must exclude the tree rather than edit it."

requirements-completed: [META-08]

coverage:
  - id: D1
    description: "The vendor directory holds exactly the 24 KaTeX distribution files plus render-math.js, PROVENANCE.txt and FILES.sha256, and every digest matches."
    requirement: META-08
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_docs_pins.KatexVendoringTests"
        status: pass
    human_judgment: false
  - id: D2
    description: "The checksum gate fails for a flipped byte, a deleted face, an unlisted file, a fonts/ subdirectory and a CRLF ledger, and passes on the real tree."
    requirement: META-08
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_docs_pins.KatexVendoringDiscriminationTests"
        status: pass
    human_judgment: false
  - id: D3
    description: "render-math.js is ASCII, subscribes to document$, calls renderMathInElement, declares all four delimiter pairs and references no external asset host."
    requirement: META-08
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_docs_pins.RenderMathScriptTests"
        status: pass
    human_judgment: false
  - id: D4
    description: "PROVENANCE.txt records the npm tarball URL, the one-time tarball SHA-256, the retrieval date and the MIT licence."
    requirement: META-08
    verification:
      - kind: unit
        ref: "scripts.tests.test_docs_pins.KatexVendoringTests#test_provenance_records_the_authentic_tarball"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 06: KaTeX Vendoring and Checksum Gate Summary

**KaTeX 0.19.0 vendored as 24 pinned static files with a provenance record, a sorted SHA-256 ledger, and a stdlib test proven to fail on a flipped byte, a missing font, an unlisted file, a `fonts/` subdirectory and a CRLF checkout.**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-10-26T18:23:55Z (worktree creation)
- **Completed:** 2026-10-26T18:26:05Z
- **Tasks:** 2
- **Files modified:** 29

## Accomplishments
- Vendored exactly the 24 distribution files from the pinned `katex@0.19.0` npm tarball, plus the authored `render-math.js`, `PROVENANCE.txt` and `FILES.sha256` — 27 files, no `.woff`/`.ttf` fallbacks, no `katex.js`/`.mjs`, no extra `contrib/`.
- Recorded the tarball URL, one-time SHA-256 (`d8e49f2f…d1ee`), retrieval date and MIT licence, so source authenticity is auditable independently of the ledger.
- Added a sorted `sha256sum -c` ledger over the 24 files and a stdlib test that recomputes every digest with `hashlib.sha256`.
- Proved the gate discriminates: each mutation case fails for the named reason, a CRLF ledger parses to the same 24 paths, and the real tree is clean.
- Pinned the browser integration surface: `document$.subscribe`, `renderMathInElement`, all four delimiter pairs, ASCII-only content, no CDN host.

## Task Commits

1. **Task 1: Vendor the pinned KaTeX tree and prove every byte against a committed checksum ledger** - `e73582e` (feat)
2. **Task 2: Prove the checksum gate discriminates and pin the browser integration points** - `9e2dbdd` (test)

**Plan metadata:** committed with this SUMMARY (docs).

## Files Created/Modified
- `docs/assets/vendor/katex/0.19.0/LICENSE` - KaTeX MIT licence (Khan Academy and contributors)
- `docs/assets/vendor/katex/0.19.0/katex.min.css` - distribution stylesheet; resolves `url(fonts/<name>.woff2)`
- `docs/assets/vendor/katex/0.19.0/katex.min.js` - distribution renderer, byte-exact from npm
- `docs/assets/vendor/katex/0.19.0/contrib/auto-render.min.js` - defines the `renderMathInElement` global
- `docs/assets/vendor/katex/0.19.0/fonts/KaTeX_*.woff2` - 20 faces beside the CSS
- `docs/assets/vendor/katex/0.19.0/render-math.js` - ASCII script re-rendering math after Material's body swap
- `docs/assets/vendor/katex/0.19.0/FILES.sha256` - 24-entry sorted `sha256sum -c` ledger
- `docs/assets/vendor/katex/0.19.0/PROVENANCE.txt` - tarball URL, one-time SHA-256, date, licence
- `scripts/tests/test_docs_pins.py` - `read_ledger`, `verify_tree`, and the three test classes
- `.pre-commit-config.yaml` - excluded the vendored tree from the two text-normalizing hooks

## Decisions Made
- **Hook exclusion over byte rewriting.** The upstream minified JavaScript has no final newline; normalizing it would change the bytes and invalidate the ledger. The vendored tree is excluded from `trailing-whitespace` and `end-of-file-fixer` instead, preserving the "never hand-edit a vendored file" prohibition.
- **"No external host" means no external asset host.** Task 1 requires the source URL in a leading comment; Task 2's assertion therefore bans CDN tokens (`cdn.`, `unpkg.com`, `jsdelivr`) and `src=`, not provenance commentary.
- **`PinConsistencyTests` stays out of this plan.** Per the plan, the pin-consistency class arrives with the site configuration in 05-08; this module deliberately starts as the vendoring and provenance gate.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Excluded the vendored tree from the text-normalizing pre-commit hooks**
- **Found during:** Task 1 (first commit attempt)
- **Issue:** `end-of-file-fixer` appended a final newline to `katex.min.js` and `contrib/auto-render.min.js`, changing their bytes and breaking the checksum ledger. The upstream files legitimately carry no final newline, so this was a hook-induced edit of a vendored file.
- **Fix:** Restored the exact upstream bytes from the extracted tarball and added `exclude: ^docs/assets/vendor/` to `trailing-whitespace` and `end-of-file-fixer` in `.pre-commit-config.yaml`.
- **Files modified:** `.pre-commit-config.yaml`
- **Verification:** the pre-commit run is green, `KatexVendoringTests` digests match, and the ledger still records the upstream bytes.
- **Committed in:** `e73582e` (Task 1 commit)
- **Scope note:** the plan forbade `.gitignore` and `.gitattributes` changes; this changes neither, and no rule was relaxed for authored content.

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary for correctness — without it the committed bytes would not be the pinned ones and the integrity test would either fail or have to be weakened.

## Issues Encountered
- The repository's `git` command is wrapped; full-path `/usr/bin/git` was used for staging and committing. No functional impact.

## User Setup Required
None - no external service configuration required. The one-time tarball download was a local operation; the committed tree needs no network at build time.

## Known Stubs
None.

## Threat Flags
None beyond the plan's threat register. T-5-17 and T-5-18 mitigations are implemented and tested: exact allowlist, ledger, provenance, CRLF-safe reader, `fonts/` subdirectory refusal, discrimination suite, ASCII-only authored script with fixed delimiters.

## Next Phase Readiness
- 05-08 can now reference the vendored paths in the generated `mkdocs.yml` and extend this module with `PinConsistencyTests`.
- The vendor tree is complete and byte-verified; a missing `extra_css`/`extra_javascript` target can no longer pass silently.

## Self-Check: PASSED

---
*Phase: 05-generated-views-and-documentation-site*
*Completed: 2026-10-26*
