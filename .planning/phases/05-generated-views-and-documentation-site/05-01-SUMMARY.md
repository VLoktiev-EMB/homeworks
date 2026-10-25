---
phase: 05-generated-views-and-documentation-site
plan: 01
subsystem: testing
tags: [python, stdlib, unittest, platformio, pyyaml, mkdocs, refactor]

# Dependency graph
requires:
  - phase: 04-metadata-contract-and-scaffolding
    provides: "the metadata contract, the stdlib-only test rule (04/D-14), the closed {{...}} placeholder vocabulary (04/D-25, 04/D-33) and the architecture checker's platformio.ini readers"
provides:
  - "scripts/metadata/errors.py — the one CheckError class shared by the scaffold, the checkers and the generators"
  - "scripts/metadata/render.py — render(text, mapping, display) and read_text(source, display), one non-recursive pass"
  - "scripts/metadata/paths.py — HOMEWORK_ID, resolve_root, relative_path, derive_parts, stdlib-only"
  - "scripts/metadata/yaml_loader.py — StrictSafeLoader, PyYAML-only"
  - "scripts/metadata/platformio.py — option, extends_targets, dep_names, load_ini, preload_extra_configs"
  - "temp_root.write_synthetic_root — the two-homework, three-library fixture with a top-level tests/ consumer"
  - "requirements-docs.txt — the three exact docs-stack pins"
affects: [05-02, 05-03, 05-04, 05-05, 05-06, 05-07, 05-08]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
actuals:
  tokens: 14900
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added:
    - "mkdocs==1.6.1 (pinned, not installed by this plan)"
    - "mkdocs-material==9.7.7 (pinned, not installed by this plan)"
    - "pymdown-extensions==12.3 (pinned, not installed by this plan)"
  patterns:
    - "stdlib-only extraction with re-exports from the PyYAML/jsonschema module"
    - "one non-recursive closed-map placeholder pass, never a template language"
    - "extra_configs resolved relative to the containing project directory"
    - "string-assembled synthetic fixture, never a copy of the authored tree"

key-files:
  created:
    - scripts/metadata/errors.py
    - scripts/metadata/render.py
    - scripts/metadata/paths.py
    - scripts/metadata/yaml_loader.py
    - scripts/metadata/platformio.py
    - scripts/tests/test_platformio_readers.py
    - requirements-docs.txt
  modified:
    - scripts/metadata/contract.py
    - scripts/new_homework
    - scripts/check_architecture.py
    - scripts/tests/test_new_homework.py
    - scripts/tests/temp_root.py
    - scripts/tests/test_homework_metadata.py

key-decisions:
  - "The four path/identity helpers and StrictSafeLoader leave contract.py so a PyYAML-only environment can import them without jsonschema (T-5-28)."
  - "contract.py re-exports the moved names instead of redefining them, so every existing call site and `except CheckError` keeps working."
  - "preload_extra_configs resolves each extra_configs entry against the containing project directory, cuts inline `;`/`#` comments, splits commas then whitespace, and refuses a quoted entry."
  - "The synthetic fixture deliberately copies nothing but platformio.shared.ini, the schema, templates/views and the board profile; it does not symlink lib/ as build_root does."
  - "The two fixture homework consumers are disjoint (common vs port) while the tests/ project consumes common, port and host, so a lib/common change must reach 1_3-alpha and tests but not 1_4-beta."

patterns-established:
  - "Extraction pattern: move the body verbatim, bind the name through a re-export, and prove object identity in a subprocess."
  - "Module-boundary pattern: import the stdlib-only modules in process, AST-parse the sources for non-stdlib roots, and shell out only where the validation stack is legitimate."

requirements-completed: [META-05, META-06, META-08]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "The renderer, path helpers, strict YAML loader and platformio.ini readers each have one implementation, importable without the validation stack."
    requirement: META-05
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_new_homework.ModuleBoundaryTests"
        status: pass
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_platformio_readers"
        status: pass
    human_judgment: false
  - id: D2
    description: "scripts/new_homework renders through the shared module and keeps its exit-2 contract (unknown placeholder, ${...}, golden tree, idempotency)."
    requirement: META-05
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_new_homework.RendererContractTests"
        status: pass
      - kind: integration
        ref: "python3 -m unittest discover -s scripts/tests (104 tests, OK)"
        status: pass
    human_judgment: false
  - id: D3
    description: "scripts/check_architecture.py consumes the shared readers, re-exports CheckError, and still exits 0 with unchanged output."
    requirement: META-06
    verification:
      - kind: e2e
        ref: "python3 scripts/check_architecture.py (PASS: dependency rule satisfied)"
        status: pass
    human_judgment: false
  - id: D4
    description: "write_synthetic_root and requirements-docs.txt are in place for every later plan, including the top-level tests/ consumer and the zero-homework mode."
    requirement: META-08
    verification:
      - kind: other
        ref: "inline fixture assertions from 05-01-PLAN.md task 3 (fixture OK; homeworks=False gives an empty homeworks/)"
        status: pass
      - kind: e2e
        ref: "uv run scripts/check_metadata.py --dir <fixture> (PASS: metadata contract satisfied)"
        status: pass
    human_judgment: false

# Metrics
duration: 16min
completed: 2026-10-25
plan_head_before: 78f1e7c5ae520b471ebd9699b2b9eb98c7f94f39
plan_head_after: b08a8889da5bf685d3156ed4d6667718c81ae63c
status: complete
---

# Phase 5 Plan 1: Shared Renderer, PlatformIO Readers and Wave 0 Fixtures Summary

**The `{{name}}` renderer and the `platformio.ini` readers each collapsed to one stdlib-only implementation, and the synthetic two-homework fixture plus the three docs pins landed for every later plan.**

## Performance

- **Duration:** ~16 min
- **Started:** 2026-10-25T22:12:00Z
- **Completed:** 2026-10-25T22:28:00Z
- **Tasks:** 3
- **Files modified:** 13 (7 created, 6 modified)

## Accomplishments
- `scripts/metadata/render.py`, `paths.py`, `yaml_loader.py` and `errors.py` now hold the renderer, the identity/path helpers, the strict YAML loader and the single `CheckError`; `contract.py` re-exports all of them as the same objects.
- `scripts/new_homework` renders only through the shared module, and `RendererContractTests` pins the load-bearing property that a mapping value containing `{{...}}` is emitted verbatim (T-5-01).
- `scripts/metadata/platformio.py` owns `option`, `extends_targets`, `dep_names`, `load_ini` and the new `preload_extra_configs`; `scripts/check_architecture.py` consumes them and still exits 0 with unchanged output.
- `temp_root.write_synthetic_root` writes two metadata-valid homeworks, three leaf libraries, the top-level `tests/` consumer, a marker-bounded `docs/index.md`, a decisions index and a board profile — and `homeworks=False` gives the zero-homework mode.
- `requirements-docs.txt` pins exactly `mkdocs==1.6.1`, `mkdocs-material==9.7.7` and `pymdown-extensions==12.3`.
- The suite grew from 81 to 104 tests, all green; a PyYAML-only environment can now import every generator dependency without jsonschema.

## Task Commits

Each task was committed atomically:

1. **Task 1: Move the `{{name}}` renderer into a shared module and prove the scaffold still renders end to end** - `6bdf7d1` (refactor)
2. **Task 2: Move the `platformio.ini` readers into a shared module and point the architecture checker at it** - `dbc5041` (refactor)
3. **Task 3: Add the synthetic fixture builder and the docs pin file** - `b08a888` (test)

**Plan metadata:** committed by the executor after this file (docs: complete plan).

## Files Created/Modified

- `scripts/metadata/errors.py` - the one `CheckError` class, stdlib-only.
- `scripts/metadata/render.py` - `render(text, mapping, display)`, `read_text(source, display)`, `PLACEHOLDER`, `DOLLAR_BRACE`.
- `scripts/metadata/paths.py` - `HOMEWORK_ID`, `resolve_root`, `relative_path`, `derive_parts`, stdlib-only.
- `scripts/metadata/yaml_loader.py` - `StrictSafeLoader`, PyYAML-only.
- `scripts/metadata/platformio.py` - `option`, `extends_targets`, `dep_names`, `load_ini`, `preload_extra_configs`.
- `scripts/metadata/contract.py` - the moved names are now re-exports; no function body changed.
- `scripts/new_homework` - renders through `scripts.metadata.render`; local `_render`, `_read_text` and the two regexes are gone.
- `scripts/check_architecture.py` - `sys.path` bootstrap, shared readers, `CheckError` re-export.
- `scripts/tests/test_new_homework.py` - `RendererContractTests` and `ModuleBoundaryTests`.
- `scripts/tests/test_platformio_readers.py` - `ExtraConfigsTests` and `ReaderRuleTests`.
- `scripts/tests/temp_root.py` - `write_synthetic_root` and its two private writers; `build_root`, `render_tree`, `repository_root` and `_copy` unchanged.
- `requirements-docs.txt` - the three docs-stack pins.

## Decisions Made
- Kept `PLATFORMIO_CORE` and `StrictBaseLoader` in `contract.py`: only the safe loader and the pure path helpers are shared with the generators.
- `preload_extra_configs` returns the constructed `Path(project_dir) / entry` values in entry order (not `resolve()`d), so callers see exactly the entry PlatformIO would read and no symlink is followed at this layer.
- The fixture copies `templates/board-profile/profile.yaml` into `boards/esp32-s3-devkitc-1.yaml` rather than retyping the six fields, so the fixture cannot drift from the template.
- Task 1's boundary test shipped over `errors`/`render`/`paths` and added `platformio` in task 2, because the module does not exist until then (see deviations).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The canonical-id test read a literal the extraction moved**
- **Found during:** Task 1 (renderer extraction)
- **Issue:** `test_homework_metadata.CanonicalIdTest` reads `scripts/metadata/contract.py` and requires the `HOMEWORK_ID = re.compile(r"...")` literal there. Moving the pattern to `paths.py` made the test fail, and the plan forbids keeping a second copy in `contract.py`.
- **Fix:** Pointed the module-level `CONTRACT` constant at `scripts/metadata/paths.py` (the new owner) and corrected the "not found in" message. The assertion itself is unchanged: schema, the canonical literal and `AGENTS.md` must still agree.
- **Files modified:** `scripts/tests/test_homework_metadata.py`
- **Verification:** full suite green (89 tests at that commit, 104 after task 2); the assertion still compares the same three literals.
- **Committed in:** `6bdf7d1` (Task 1 commit)

**2. [Rule 3 - Blocking] `ModuleBoundaryTests` named `platformio` before that module existed**
- **Found during:** Task 1 (renderer extraction)
- **Issue:** The plan's task-1 action has the boundary test import `scripts.metadata.platformio`, but `platformio.py` is created in task 2; importing it in task 1 would fail the task's own verify.
- **Fix:** Task 1 shipped `ModuleBoundaryTests` over `errors`/`render`/`paths` plus the `yaml_loader` source check; task 2 added `platformio` to `STDLIB_ONLY_MODULES`, the in-process import and the subprocess identity program.
- **Files modified:** `scripts/tests/test_new_homework.py`
- **Verification:** the boundary class passes at both commits (8 tests).
- **Committed in:** `6bdf7d1` and `dbc5041`

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking)
**Impact on plan:** Both changes are mechanical consequences of moving code between modules. No behaviour, assertion strength or scope changed.

## Issues Encountered
- The plan's task-3 verify constructs `preload_extra_configs` paths with `..` segments; the reader intentionally does not call `resolve()` (that would follow symlinks), so the tests normalize both sides instead. No functional impact.
- `templates/views/` does not exist yet, so `write_synthetic_root` skips copying it today; the guard makes it copy the real templates as soon as 05-03 creates them.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- 05-02, 05-03 and 05-07 can import `StrictSafeLoader` from `scripts.metadata.yaml_loader` and the pure helpers from `paths.py` without jsonschema.
- 05-04 can import `load_ini`, `option`, `dep_names` and `preload_extra_configs` from `scripts.metadata.platformio` for the fanout graph and the inherited `framework`.
- 05-03, 05-04, 05-05 and 05-07 build on `write_synthetic_root`; 05-05 gets its zero-homework case from `homeworks=False`.
- `requirements-docs.txt` is in place; its cross-check against the generated `mkdocs.yml` and the vendored KaTeX version is 05-08's `PinConsistencyTests`.
- No blockers.

## Self-Check: PASSED

---
*Phase: 05-generated-views-and-documentation-site*
*Completed: 2026-10-25*
