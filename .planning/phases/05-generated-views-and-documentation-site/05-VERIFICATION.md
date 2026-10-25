---
phase: 05-generated-views-and-documentation-site
verified: 2026-10-25T23:12:15Z
status: human_needed
score: 124/125 must-haves verified
covered_files: [".github/workflows/docs.yml",".github/workflows/generated-views.yml",".gitignore",".planning/phases/05-generated-views-and-documentation-site/05-01-PLAN.md",".planning/phases/05-generated-views-and-documentation-site/05-01-SUMMARY.md",".planning/phases/05-generated-views-and-documentation-site/05-02-PLAN.md",".planning/phases/05-generated-views-and-documentation-site/05-02-SUMMARY.md",".planning/phases/05-generated-views-and-documentation-site/05-03-PLAN.md",".planning/phases/05-generated-views-and-documentation-site/05-03-SUMMARY.md",".planning/phases/05-generated-views-and-documentation-site/05-04-PLAN.md",".planning/phases/05-generated-views-and-documentation-site/05-04-SUMMARY.md",".planning/phases/05-generated-views-and-documentation-site/05-05-PLAN.md",".planning/phases/05-generated-views-and-documentation-site/05-05-SUMMARY.md",".planning/phases/05-generated-views-and-documentation-site/05-06-PLAN.md",".planning/phases/05-generated-views-and-documentation-site/05-06-SUMMARY.md",".planning/phases/05-generated-views-and-documentation-site/05-07-PLAN.md",".planning/phases/05-generated-views-and-documentation-site/05-07-SUMMARY.md",".planning/phases/05-generated-views-and-documentation-site/05-08-PLAN.md",".planning/phases/05-generated-views-and-documentation-site/05-08-SUMMARY.md",".planning/phases/05-generated-views-and-documentation-site/05-09-PLAN.md",".planning/phases/05-generated-views-and-documentation-site/05-09-SUMMARY.md",".pre-commit-config.yaml","AGENTS.md","README.md","boards/esp32-s3-devkitc-1.yaml","docs/assets/vendor/katex/0.19.0/FILES.sha256","docs/assets/vendor/katex/0.19.0/LICENSE","docs/assets/vendor/katex/0.19.0/PROVENANCE.txt","docs/assets/vendor/katex/0.19.0/contrib/auto-render.min.js","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_AMS-Regular.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Caligraphic-Bold.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Caligraphic-Regular.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Fraktur-Bold.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Fraktur-Regular.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Main-Bold.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Main-BoldItalic.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Main-Italic.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Main-Regular.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Math-BoldItalic.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Math-Italic.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_SansSerif-Bold.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_SansSerif-Italic.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_SansSerif-Regular.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Script-Regular.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Size1-Regular.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Size2-Regular.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Size3-Regular.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Size4-Regular.woff2","docs/assets/vendor/katex/0.19.0/fonts/KaTeX_Typewriter-Regular.woff2","docs/assets/vendor/katex/0.19.0/katex.min.css","docs/assets/vendor/katex/0.19.0/katex.min.js","docs/assets/vendor/katex/0.19.0/render-math.js","docs/boards/esp32-s3-devkitc-1.md","docs/homeworks/1_3-police-flasher.md","docs/index.md","generated.manifest","homeworks.code-workspace","mkdocs.yml","platformio.shared.ini","requirements-docs.txt","schema/board-profile.schema.json","scripts/affected.py","scripts/check_architecture.py","scripts/check_metadata.py","scripts/ci/check_lfs_pointers.sh","scripts/gen_views.py","scripts/metadata/board_profile.py","scripts/metadata/contract.py","scripts/metadata/errors.py","scripts/metadata/paths.py","scripts/metadata/platformio.py","scripts/metadata/render.py","scripts/metadata/yaml_loader.py","scripts/new_homework","scripts/tests/temp_root.py","scripts/tests/test_affected.py","scripts/tests/test_ci_workflows.py","scripts/tests/test_docs_pins.py","scripts/tests/test_gen_views.py","scripts/tests/test_homework_metadata.py","scripts/tests/test_new_homework.py","scripts/tests/test_platformio_readers.py","templates/views/board-page.md.tmpl","templates/views/homework-page.md.tmpl","templates/views/homeworks-table.md.tmpl","templates/views/mkdocs.yml.tmpl","templates/views/shared-ini.ini.tmpl","templates/views/workspace.json.tmpl"]
covered_digest: "v3:sha256:6bfb5f00cd3abcaa95d2d39bd5d27275855b466da90a381db6f4d0867c811c3a"
behavior_unverified: 1
overrides_applied: 0
deferred: # Items addressed in later phases — not actionable gaps
  - truth: "A CI build matrix is generated from `homework.yaml` (roadmap success criterion 1, META-05)"
    addressed_in: "Phase 8"
    evidence: "Phase 8 success criterion 1: 'a `changes` job that computes the affected matrix'; 05-CONTEXT D-26 states 'Phase 5 generates no CI matrix ... converting them into a matrix is Phase 8'."
behavior_unverified_items: # Emitted regardless of overall status
  - truth: "GitHub Pages deploys the built site (roadmap success criterion 4, META-08)"
    test: "Merge to `main` (or dispatch the `docs` workflow), open the Pages URL, and confirm the home page, the 1.3 homework page and the board page render with KaTeX fonts."
    expected: "The `build` job completes, `upload-pages-artifact` and `deploy-pages` succeed, and https://vloktiev-emb.github.io/homeworks/ serves the generated pages."
    why_human: "The Pages source setting and the `github-pages` environment are repository settings; `deploy-pages` cannot run on a feature branch, so the deploy path is wired but its runtime behaviour cannot be exercised pre-merge."
human_verification:
  - test: "Deploy the site: merge the phase branch, or run the `docs` workflow with `workflow_dispatch` after setting Settings -> Pages -> Build and deployment -> Source = GitHub Actions, then open https://vloktiev-emb.github.io/homeworks/"
    expected: "The workflow's `build and deploy` job is green; the home page shows the six-column generated table, the Homeworks/Boards/Decisions navigation resolves, and a math-bearing page renders through the vendored KaTeX fonts."
    why_human: "GitHub Pages source selection and the `github-pages` environment are repository-level settings; `deploy-pages` is unavailable to feature-branch runs, so no pre-merge command can prove the deployment."
  - test: "Review the 23 judgment-tier `must_haves.prohibitions` across the nine plans (no CDN assets, no report-body copying, no writes under `docs/decisions/`, no arbitrary pin selection, no matrix under-approximation, no PR write permissions / `gh-pages` publication)."
    expected: "A human confirms each must-NOT held; the mechanical checks below found no violation, but the plans mark them `verification: judgment`."
    why_human: "ADR-550 routes judgment-tier prohibitions to an explicit human checkpoint rather than an automatic pass."
---

# Phase 5: Generated Views and Documentation Site Verification Report

**Phase Goal:** Every repeated view of the repository is generated from `homework.yaml`, and the documentation site builds and deploys from that tree. **Friction-log justification:** The Phase 4.2 log must contain at least one entry for generated views or the docs site; otherwise the automation is not built.
**Verified:** 2026-10-25T23:12:15Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

The nine plans declare 124 `must_haves.truths`. All 124 are VERIFIED. The only extra must-have is the roadmap's deploy clause, which is present and wired but whose runtime behaviour is not exercised (125 total, 124 verified, 1 present-behavior-unverified). Roadmap criteria 1–3 are already restated by plan truths and are therefore not double-counted.

| # | Truth group | Status | Evidence |
|---|-------------|--------|----------|
| 1 | **05-01 (13 truths)** — shared renderer, stdlib-only `paths.py`, PyYAML-only `yaml_loader.py`, shared `platformio.ini` readers, one `CheckError`, Wave-0 fixture, exact docs pins | ✓ VERIFIED | All eight artifacts exist. `resolve_root`/`relative_path`/`derive_parts`/`HOMEWORK_ID`/`StrictSafeLoader`/`CheckError` are identity-equal across `contract.py`, `paths.py`, `yaml_loader.py`, `platformio.py`, `check_architecture.py` (printed `True`). Importing the four modules adds neither `jsonschema` nor `scripts.metadata.contract` to `sys.modules`. `check_architecture.py` exits 0. `requirements-docs.txt` pins mkdocs 1.6.1 / mkdocs-material 9.7.7 / pymdown-extensions 12.3. Full suite 279 tests OK. |
| 2 | **05-02 (11 truths)** — board-profile schema, one real profile, checker extension, symlink refusal, family positionals, read-only | ✓ VERIFIED | `uv run scripts/check_metadata.py` exits 0 and prints `boards/esp32-s3-devkitc-1.yaml: OK — board profile contract satisfied`. `BoardProfileTests` (id/stem, unknown key, missing key, psram enum, non-https URL, duplicate frameworks, duplicate psram/pinout_url, symlinked directory/document, missing `boards/`, positional families, exit 2) all pass. `check-metadata` hook regex contains `boards/`. |
| 3 | **05-03 (18 truths)** — generator spine, marker region, manifest, four drift classes, atomic writes, strict loader, escaping, allowlist, numeric order, `.gitignore` fix | ✓ VERIFIED | `uv run scripts/gen_views.py --all --check` exits 0 with 8 `UNCHANGED` records. Appending a byte to `mkdocs.yml` makes `gen_views.py nav --check` exit 1 with `mkdocs.yml: MODIFIED`, then exit 0 after restore. `generated.manifest` is version 1, 7 sorted entries, never lists itself, carries `mode`/`sha256`/`bytes`/markers. `.gitignore` has `!generated.manifest`. `--help` states the non-serialization warning. `TracerTests`, `IdempotencyTests`, `ManifestTests`, `DriftTests`, `WholeFileRecoveryTests`, `MarkerTests`, `EscapeTests`, `AllowlistTests`, `SymlinkInputTests`, `RealTreeSmokeTest` pass (temp-file cleanup asserted). |
| 4 | **05-04 (16 truths)** — `affected.py` JSON matrix, fanout, no-build-impact set, fail-safe widening, framework resolution, native/simulate rules, path format, safety | ✓ VERIFIED | `--paths-from` with `lib/common/src/ring.c` emits build `{1_3-police-flasher: esp32s3_arduino, native; tests: native}` and simulate `{1_3-police-flasher: esp32s3_arduino}`. `docs/index.md` only yields `{"build": [], "simulate": []}`. An unknown path and a `../` path both widen to every project. `--format paths` prints `build <project> <env> <framework>`. `FanoutTests`, `NoBuildImpactTests`, `FrameworkTests`, `PathsFromTests`, `EndToEndTests`, `FixtureGuardTests` pass. |
| 5 | **05-05 (15 truths)** — generated workspace and shared INI, fixed roots, ASCII paths, tab format, pin derivation/refusal, Core pin | ✓ VERIFIED | `homeworks.code-workspace` contains `repo`, `docs`, `lib`, `scripts` plus `homeworks/1_3-police-flasher`, tab-indented, with the original `extensions` block. `platformio.shared.ini` keeps the three sections and byte-identical SCons comment, pins `PlatformIO Core: 6.2.0` and `espressif32@8.0.0`, and names no homework id. `contract.read_shared_core_pin('.')` returns `6.2.0`. `WorkspaceTests`/`SharedIniTests` (including zero-homework exit 2 naming `shared-ini`) pass. |
| 6 | **05-06 (12 truths)** — vendored KaTeX 0.19.0, provenance, SHA-256 ledger, CRLF handling, subdirectory detection, render hook, no CDN | ✓ VERIFIED | Vendor tree is exactly 27 files = 24 distribution files + `render-math.js` + `PROVENANCE.txt` + `FILES.sha256`; ledger has 24 sorted sha256sum-format lines. `PROVENANCE.txt` records npm tarball URL, tarball digest, retrieval date and MIT licence. `render-math.js` subscribes to `document$` and declares `$$`, `$`, `\(`/`\)`, `\[`/`\]`. `KatexVendoringTests` and `KatexVendoringDiscriminationTests` (flipped byte, deleted face, unlisted file, fonts subdirectory, removed fonts dir, CRLF ledger) pass. |
| 7 | **05-07 (14 truths)** — generated homework/board pages, site home, metadata card, absolute report links, no `../` leakage, escaping, no `docs/decisions/` writes | ✓ VERIFIED | `docs/homeworks/1_3-police-flasher.md` carries the generated header, the eight-field D-02 card, `wokwi (pending)`, and absolute GitHub blob links. `docs/boards/esp32-s3-devkitc-1.md` renders the board table and exactly `../homeworks/1_3-police-flasher.md`. `docs/index.md` uses the same six-column header inside its marker region. `git diff 752ecac..HEAD -- docs/decisions` is empty (12 authored files untouched). `DocsPagesTests`, `BoardPageTests`, `ReportPathTests`, `SymlinkInputTests` pass. |
| 8 | **05-08 (12 truths)** — generated `mkdocs.yml`, four-section nav, label extraction, ASCII targets, strict build, pin consistency | ✓ VERIFIED | `mkdocs.yml` declares `site_name: Homeworks`, the Pages `site_url`, `theme.name: material` with no `custom_dir`, `plugins: [search]`, the validation block, the extensions list and the three vendored KaTeX assets. Nav has exactly Home/Homeworks/Boards/Decisions and 15 leaves for the 15 Markdown files under `docs/`; every entry uses an unquoted separator colon. `uv run --python 3.13 --with-requirements requirements-docs.txt mkdocs build --strict` exits 0 and writes pages plus the vendor tree into `site/`; installed versions are mkdocs 1.6.1, mkdocs-material 9.7.7, pymdown-extensions 12.3. `PinConsistencyTests` and `NavTests` pass. |
| 9 | **05-09 (13 truths)** — drift hook, CI drift job, docs deploy workflow, LFS guard, SHA pins, AGENTS corrections, Pages checklist | ✓ VERIFIED | `gen-views-check` runs `python scripts/gen_views.py --all --check`, `pass_filenames: false`, only `PyYAML==6.0.3`, and the documented `files:` regex. `pre-commit run --all-files` exits 0 with all nine hooks passing, including `generated views are in sync`. `generated-views.yml`: PR + dispatch, `contents: read`, one matrix-free job. `docs.yml`: push to `main` + dispatch, `contents: read`/`pages: write`/`id-token: write`, `github-pages` environment, checkout `lfs: false`, strict build step, LFS guard, configure/upload/deploy Pages. All `uses:` are 40-hex SHAs. `AGENTS.md` names `boards/`, `templates/views/`, `mkdocs.yml`, `requirements-docs.txt`, `docs/`, `generated.manifest`, and schedules `docs/standards/` for Phase 10 on both lines. `LfsPointerGuardTests` pass. |
| 10 | **Friction-log justification** — the Phase 4.2 log contains at least one entry for generated views or the docs site | ✓ VERIFIED | `04.2-FRICTION-LOG.md` F-18 is an entry about adding the workspace folder, and the "Top automation candidates" table has the Phase 5 row "Generate the root README row, the workspace folder, and the shared-ini decision from `homework.yaml`, with a `--check` drift mode" with evidence F-01, F-14, F-18. |
| 11 | **Roadmap SC4 deploy clause** — GitHub Pages deploys the artifact | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | `docs.yml` wires `configure-pages`, `upload-pages-artifact` and `deploy-pages` with OIDC permissions; the deploy runtime cannot be exercised before merge — see Human Verification. |

**Score:** 124/125 truths verified (1 present, behavior-unverified)
**Plan truths:** 124/124 verified.

### Roadmap Success Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | README index, MkDocs navigation, workspace, shared INI and CI matrix regenerate; `--check` fails on drift | ✓ VERIFIED (CI-matrix clause deferred) | Four views regenerate and `--check` exits 1 on drift. The CI matrix is explicitly Phase 8 work (05-CONTEXT D-26; Phase 8 SC1); see Deferred Items. |
| 2 | `affected.py` maps a `lib/**` diff to every consumer in the build and simulation matrix | ✓ VERIFIED | `lib/common` diff selects the homework's Arduino and native environments plus the top-level `tests` native environment in `build`, and the Arduino environment in `simulate`. |
| 3 | `homeworks.code-workspace` contains `repo`, `docs`, `lib`, `scripts` and every homework, ASCII paths | ✓ VERIFIED | Workspace file inspected; homework path is `homeworks/1_3-police-flasher`, display name `1.3 Police Flasher`. |
| 4 | `mkdocs build --strict` succeeds with Material 9.7.7, Zensical-compatible config, vendored KaTeX; Pages deploys the artifact | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED (build verified, deploy not exercised) | Strict build exits 0 with Material 9.7.7 and vendored KaTeX; deploy path is wired but runtime-unverified. |

### Deferred Items

Items not yet met but explicitly addressed in later milestone phases.

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | CI build matrix generated from `homework.yaml` | Phase 8 | Phase 8 success criterion 1: "a `changes` job that computes the affected matrix"; 05-CONTEXT D-26: "Phase 5 generates no CI matrix ... converting them into a matrix is Phase 8". |
| 2 | Friction-log candidates F-04 (`lib/pattern` manifest) and F-05/F-18 (test scaffold + inner `.gitignore`) | Phase 9 / backlog | 05-CONTEXT D-25: "deferred to backlog / Phase 9. They produce project content, not views of `homework.yaml`." |
| 3 | Authored `docs/standards/` pages | Phase 10 | 05-CONTEXT D-12; `AGENTS.md` now schedules them for Phase 10 on both lines. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/gen_views.py` | PEP 723 generator, five views + `--all`/`--check` | ✓ VERIFIED | 1698 lines; `--help` lists `readme`, `workspace`, `shared-ini`, `docs`, `nav`; imported and exercised. |
| `scripts/affected.py` | Diff-to-matrix mapper | ✓ VERIFIED | 554 lines; JSON and paths formats exercised on real and unknown/traversal inputs. |
| `scripts/metadata/{errors,render,paths,yaml_loader,platformio,board_profile}.py` | Shared stdlib/PyYAML-only helpers | ✓ VERIFIED | All exist, bounded import graph proven. |
| `scripts/tests/temp_root.py` | Two-homework/three-library fixture | ✓ VERIFIED | 384 lines; `homeworks=False` and zero-homework cases exercised by tests. |
| `templates/views/*.tmpl` | Six reviewed writers | ✓ VERIFIED | `homeworks-table`, `workspace.json`, `shared-ini.ini`, `homework-page`, `board-page`, `mkdocs.yml`. |
| `generated.manifest` | Committed ownership ledger | ✓ VERIFIED | 7 entries, version 1, sorted, hashes/bytes/modes. |
| `README.md`, `docs/index.md` | Marker-bounded generated regions | ✓ VERIFIED | Six-column table present in both; prose outside markers authored. |
| `homeworks.code-workspace`, `platformio.shared.ini`, `mkdocs.yml` | Whole generated views | ✓ VERIFIED | Contents match D-15/D-16/D-06; `--check` clean. |
| `docs/homeworks/<id>.md`, `docs/boards/<id>.md` | Generated pages | ✓ VERIFIED | One each; generated headers, cards, links verified. |
| `docs/assets/vendor/katex/0.19.0/` | 24 vendored files + ledger + provenance + script | ✓ VERIFIED | 27 files total; digests verified. |
| `boards/esp32-s3-devkitc-1.yaml` + `schema/board-profile.schema.json` | Board profile contract | ✓ VERIFIED | Validated by `check_metadata.py`. |
| `.github/workflows/{generated-views,docs}.yml` | Drift and deploy workflows | ✓ VERIFIED | Read-only drift job; OIDC Pages build+deploy; 40-hex pins. |
| `.pre-commit-config.yaml` | `gen-views-check` hook | ✓ VERIFIED | Check-only hook; `pre-commit run --all-files` exit 0. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `scripts/new_homework` | `scripts/metadata/render.py` | shared `render`/`read_text` | ✓ WIRED | Imports the extracted module; exit-code contract covered by `test_new_homework.py`. |
| `scripts/metadata/contract.py` | `scripts/metadata/paths.py`, `yaml_loader.py` | re-exports | ✓ WIRED | Identity checks printed `True` for all five names. |
| `scripts/gen_views.py`, `scripts/affected.py` | `paths.py`, `platformio.py`, `render.py`, `yaml_loader.py` | imports | ✓ WIRED | Neither imports `contract.py`; import-isolation subprocess test passes. |
| `scripts/check_architecture.py` | `scripts/metadata/platformio.py` | `load_ini`/`option`/`dep_names` | ✓ WIRED | `CheckError` identity true; architecture check exits 0. |
| `scripts/check_metadata.py` | `scripts/metadata/board_profile.py` | board validation | ✓ WIRED | Board OK record printed; `BoardProfileTests` pass. |
| `scripts/gen_views.py` | `generated.manifest` | ownership ledger | ✓ WIRED | 7 entries consumed by `--check`; drift detected on a one-byte edit. |
| `scripts/gen_views.py` | `templates/views/*` | reviewed templates | ✓ WIRED | All six templates exist and are the only writers; symlink refusal tested. |
| `docs/index.md` | `homeworks/<id>/homework.yaml` | shared table template | ✓ WIRED | Index and README share the six-column header; index rows are absolute. |
| `docs/boards/<id>.md` | `boards/<id>.yaml` | projection | ✓ WIRED | Board table and homework list generated from the profile. |
| `docs/homeworks/<id>.md` | `homeworks/<id>/report.md` | absolute GitHub blob URL | ✓ WIRED | Link verified; report body not copied. |
| `mkdocs.yml` | `docs/` tree | nav + extra_css/js | ✓ WIRED | 15 nav leaves for 15 Markdown files; strict build resolves all targets. |
| `.pre-commit-config.yaml` | `scripts/gen_views.py` | `--all --check` | ✓ WIRED | Hook passed on the real tree; manual perturbation fails the same command. |
| `.github/workflows/generated-views.yml` | `generated.manifest` | `--all --check` | ✓ WIRED | Job runs the identical command read-only. |
| `.github/workflows/docs.yml` | `requirements-docs.txt`, `site/` | install, strict build, artifact upload | ✓ WIRED | Steps present; local strict build matches the workflow command. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `README.md` region | `{{homework_rows}}` | `homeworks/*/homework.yaml` via `_load_homeworks` | Yes — 1.3 row with real metadata | ✓ FLOWING |
| `docs/index.md` region | `{{homework_rows}}` | same loader, absolute link style | Yes | ✓ FLOWING |
| `docs/homeworks/*.md` | page fields | `homework.yaml` | Yes — board/framework/status/toolchain/simulation | ✓ FLOWING |
| `docs/boards/*.md` | board fields + homework list | `boards/*.yaml` + homework metadata | Yes | ✓ FLOWING |
| `mkdocs.yml` nav | nav fragments | `docs/**/*.md` headings + homework/board ids | Yes — 15 entries | ✓ FLOWING |
| `homeworks.code-workspace` | folders | homework ids | Yes | ✓ FLOWING |
| `platformio.shared.ini` | pins | distinct `toolchain.*` pair | Yes — 6.2.0 / espressif32@8.0.0 | ✓ FLOWING |
| `scripts/affected.py` output | build/simulate | `platformio.ini` + `homework.yaml` + `library.json` | Yes — observed fanout | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Generated-view check on the real tree | `uv run scripts/gen_views.py --all --check` | exit 0, 8 `UNCHANGED` records | ✓ PASS |
| Drift is non-zero | append a byte to `mkdocs.yml`; `gen_views.py nav --check` | exit 1, `mkdocs.yml: MODIFIED`; exit 0 after restore | ✓ PASS |
| `lib/**` fanout | `affected.py --paths-from` with `lib/common/src/ring.c` | 3 build entries (incl. `tests` native), 1 simulate | ✓ PASS |
| No-build-impact path | `affected.py --paths-from` with `docs/index.md` | `{"build": [], "simulate": []}` | ✓ PASS |
| Fail-safe widening | `affected.py --paths-from` with `weird/unknown.txt` and `../outside.txt` | every project selected | ✓ PASS |
| Strict site build | `uv run --python 3.13 --with-requirements requirements-docs.txt mkdocs build --strict` | exit 0; `site/` contains homeworks, boards, vendor | ✓ PASS |
| Metadata + board contract | `uv run scripts/check_metadata.py` | exit 0, board OK record | ✓ PASS |
| Architecture/dependency rule | `python3 scripts/check_architecture.py` | exit 0 | ✓ PASS |
| Python suite | `python3 -m unittest discover -s scripts/tests` | 279 tests, OK (22.0 s) | ✓ PASS |
| Local gate | `pre-commit run --all-files` | exit 0, all nine hooks passed | ✓ PASS |

### Probe Execution

No phase-declared probe scripts and no `scripts/*/tests/probe-*.sh` exist; this phase is a generator/docs phase, so Step 7c is not applicable. (`scripts/review_smoke_test.sh` is a review-tooling script, not a phase probe.)

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| META-05 | 05-01, 05-03, 05-07, 05-09 | README index, MkDocs nav, workspace, shared INI and CI matrix generated with `--check`; CI fails on drift | ✓ SATISFIED (CI-matrix clause deferred to Phase 8 per D-26) | Four views regenerate; `--check` exits 1 on drift; `generated-views.yml` runs the check on PR; manifest committed. |
| META-06 | 05-01, 05-04 | `scripts/affected.py` maps a git diff to build/simulation matrices with `lib/**` fanout | ✓ SATISFIED | Fanout, no-build-impact, widening and path formats exercised; `EndToEndTests` uses a real temporary git repo. |
| META-07 | 05-05 | Committed multi-root workspace with `repo`, `docs`, `lib`, `scripts`, every homework; ASCII paths | ✓ SATISFIED | Workspace content and tab formatting verified. |
| META-08 | 05-01, 05-06, 05-07, 05-08, 05-09 | MkDocs Material 9.7.7 strict site, Zensical-compatible, vendored KaTeX, Pages deploy via artifact upload | ⚠️ SATISFIED with one human item | Build and vendoring verified; deploy path wired but runtime deploy not exercised. |

No orphaned requirements: REQUIREMENTS.md maps exactly META-05–08 to Phase 5, and all four appear in plan frontmatter.

### Anti-Patterns Found

No blocking anti-pattern was found. The 70 changed implementation files contain no `TBD`/`FIXME`/`XXX` markers, so the debt-marker gate does not fire. The 24 code-review findings are accounted for by ID in `05-REVIEW-DISPOSITION.md` (2 critical, 14 warning, 8 info; `unparsed: 24` is explained by the `####` vs `###` heading mismatch). CR-01, CR-02, WR-02 and WR-03 are fixed and their regression tests pass. The 20 remaining `open` findings are latent robustness issues, not phase-goal violations:

| File | Finding | Severity | Impact |
|------|---------|----------|--------|
| `scripts/gen_views.py` | WR-01 — `_escape_cell` does not escape backslashes, so a title containing `\` before `|`/`[` can defeat the escape | ⚠️ Warning | Affects only attacker-authored metadata in this same public repo; the phase must-have (pipe/newline/HTML) is met. |
| `scripts/check_metadata.py` | WR-04 — absolute board positionals are misclassified when the caller's root spelling differs from the resolved root | ⚠️ Warning | Edge invocation only; the documented relative invocation and all plan tests pass. Does not widen the other family to "all". |
| `scripts/affected.py` | WR-10 — a selected project with `platformio.ini` but no `[env:]` silently contributes no matrix entry | ⚠️ Warning | No current project is in that state; latent under-approximation. |
| `.github/workflows/generated-views.yml`, `docs.yml` | WR-13 — no PR job builds the site, and the stdlib docs/KaTeX tests never run in CI | ⚠️ Warning | The docs workflow builds strictly on `main`; PR-time gating is Phase 8's CI scope. The KaTeX ledger is enforced locally. |
| `scripts/check_architecture.py`, `_write_atomic`, `new_homework`, `check_lfs_pointers.sh` | WR-05…WR-09, WR-11, WR-12, WR-14 and IN-01…IN-08 | ℹ️ Info | Recorded and deliberately deferred; none contradicts a phase must-have. |

### Human Verification Required

#### 1. GitHub Pages deployment

**Test:** Set `Settings -> Pages -> Build and deployment -> Source` to `GitHub Actions`, merge the phase branch (or dispatch the `docs` workflow from `main`), and open https://vloktiev-emb.github.io/homeworks/.
**Expected:** The `build and deploy` job is green; the home page shows the generated six-column table; Homeworks/Boards/Decisions navigation resolves; a math-bearing page renders through the vendored KaTeX fonts.
**Why human:** The Pages source setting and the `github-pages` environment are repository settings, and `deploy-pages` cannot run on a feature branch. `05-SECURITY.md` marks T-5-26 "closed — first deploy verified after merge", but that is a planning claim, not evidence this verification can reproduce.

#### 2. Judgment-tier prohibitions

**Test:** Confirm the 23 `must_haves.prohibitions` across the nine plans.
**Expected:** No CDN asset, no report-body copy, no write under `docs/decisions/`, no arbitrary pin selection, no matrix under-approximation, no PR write permission or `gh-pages` publication, no second copy of the shared readers, no `format` keyword in the board schema, no per-homework shared-INI entry or editor files.
**Why human:** They are declared `verification: judgment`; the mechanical checks found no violation, but ADR-550 requires an explicit human disposition.

### Gaps Summary

No gaps block the phase goal. All 124 plan-level must-have truths are verified in the codebase, and the Phase 4.2 friction log contains the required generated-views entry (F-18 plus the Phase 5 automation-candidate row). Two items are honest boundaries rather than failures:

1. **Deploy runtime is unproven pre-merge.** The `docs` workflow wires the full OIDC Pages path and the strict build is green locally, but `deploy-pages` needs repository settings and a `main` push. This is the human verification item.
2. **The CI matrix is deferred to Phase 8** by decision D-26 and by Phase 8's own success criterion; it is recorded under Deferred Items, not as a gap.

The 20 open review findings are latent robustness concerns. None undermines a must-have: the most phase-relevant one (WR-13) means the site build is proven on `main` and locally rather than on pull requests, which is the documented Phase 5/Phase 8 split.

---

_Verified: 2026-10-25T23:12:15Z_
_Verifier: Claude (gsd-verifier)_
