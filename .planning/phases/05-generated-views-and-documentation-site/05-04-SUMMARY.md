---
phase: 05-generated-views-and-documentation-site
plan: 04
subsystem: tooling
tags: [python, cli, platformio, git-diff, ci-matrix, unittest, pyyaml]

# Dependency graph
requires:
  - phase: 05-generated-views-and-documentation-site
    plan: 01
    provides: "scripts/metadata/platformio.py (option, extends_targets, dep_names, load_ini, preload_extra_configs), paths.py, yaml_loader.py and temp_root.write_synthetic_root"
  - phase: 03-shared-library-core
    provides: "the platformio.ini `extends`/`lib_deps` semantics the architecture gate already enforces"
provides:
  - "scripts/affected.py — the PEP 723 diff mapper: --paths-from, --base, --format {json,paths}, --dir; constants NO_BUILD_IMPACT, WIDEN_ALL, SIMULATE_OFF"
  - "the JSON contract {\"build\": [{project, env, framework}], \"simulate\": [...]} Phase 8 feeds to strategy.matrix"
  - "a project set that includes the top-level tests/ consumer alongside every homeworks/*/ project"
  - "scripts/tests/test_affected.py — TracerTests, FanoutTests, NoBuildImpactTests, PathsFromTests, FrameworkTests, FixtureGuardTests, EndToEndTests"
affects: [05-09, phase-08-ci-matrix]

actuals:
  tokens: 9600
  tasks: 3
  commits: 3

tech-stack:
  added:
    - "PyYAML==6.0.3 (already the repository pin; the mapper's PEP 723 header names it and nothing else)"
  patterns:
    - "one fanout table applied in order: no-build-impact, specific rules, fail-safe widen"
    - "segment-based path matching so lib/common and lib/commonplace stay distinct"
    - "containment-only refusal of absolute, Windows-absolute and `..`-bearing paths; a refusal widens, never reads or echoes"
    - "dependency graph derived only from lib_deps plus library.json, walked with a seen set"
    - "fixtures invoked through `uv run` subprocesses; no test imports PyYAML"

key-files:
  created:
    - scripts/affected.py
    - scripts/tests/test_affected.py
  modified: []

key-decisions:
  - "A change under homeworks/<id>/ selects exactly that project; an empty project directory is skipped, while a directory holding homework.yaml or a source file but no platformio.ini exits 1 with the directory named."
  - "NO_BUILD_IMPACT names generated.manifest, mkdocs.yml, requirements-docs.txt, homeworks.code-workspace, templates/views/ and boards/ explicitly, so a views-only pull request rebuilds nothing while an unknown path still widens."
  - "The project set includes the top-level tests/ consumer, because it consumes common, port and host; it appears in build only, once because it is native and once because it declares no simulation."
  - "An unsafe diff path (absolute, Windows-absolute or containing `..`) widens to every project and is never read or echoed."
  - "framework falls back to native when the resolved platform is native; a non-native environment with no resolvable framework is a CheckError (exit 2) rather than an empty string."
  - "A malformed circular library.json dependency chain terminates through a seen set, proven by a fixture where common and port depend on each other."

patterns-established:
  - "The diff mapper reads platformio.ini only through scripts/metadata/platformio.py, so the architecture gate and the CI matrix cannot disagree."
  - "Content problem (exit 1) versus environment problem (exit 2) is decided by whether the selected project can be built at all; diagnostics go to stderr and stdout carries only the payload."

requirements-completed: [META-06]

coverage:
  - id: D1
    description: "A single changed homework file maps end to end to its build and simulation entries, with each entry carrying project, env and framework sorted by (project, env)."
    requirement: META-06
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_affected.TracerTests"
        status: pass
    human_judgment: false
  - id: D2
    description: "A lib/<name> change reaches exactly its consumers, including the top-level tests/ project; shared and unrecognised paths widen to every project."
    requirement: META-06
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_affected.FanoutTests"
        status: pass
    human_judgment: false
  - id: D3
    description: "The twelve NO_BUILD_IMPACT entries and a views-only diff yield empty build and simulate arrays, while a mixed diff still selects its homework."
    requirement: META-06
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_affected.NoBuildImpactTests"
        status: pass
    human_judgment: false
  - id: D4
    description: "Unsafe path spellings (absolute, parent segment) widen instead of being read, and neither spelling is echoed; newline and NUL path files behave alike."
    requirement: META-06
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_affected.PathsFromTests"
        status: pass
    human_judgment: false
  - id: D5
    description: "framework resolves to arduino, espidf and native through extra_configs plus extends; native environments and simulation.tool: none projects stay out of simulate."
    requirement: META-06
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_affected.FrameworkTests"
        status: pass
    human_judgment: false
  - id: D6
    description: "A duplicated simulation key exits 2, a project without platformio.ini exits 1, an empty homework directory is skipped, and a cyclic library.json chain terminates."
    requirement: META-06
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_affected.FixtureGuardTests"
        status: pass
    human_judgment: false
  - id: D7
    description: "A real git init repository, a real commit and a real diff produce the expected matrix in both working-tree and --base modes, with lib/common reaching 1_3-alpha and tests."
    requirement: META-06
    verification:
      - kind: integration
        ref: "python3 -m unittest scripts.tests.test_affected.EndToEndTests"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-10-25
plan_head_before: db9fd74ef264b0c8f8003f42ab4e10dba9e784bc
plan_head_after: dd472df970be9190301623dfd22023aea7175bda
status: complete
---

# Phase 5 Plan 4: Diff-to-Matrix Mapper Summary

**`scripts/affected.py` turns a git diff into the sorted build and simulation matrix Phase 8 feeds to `strategy.matrix`, with `lib/**` fanout to exactly its consumers (including the top-level `tests/` project), an explicit no-build-impact set so a views-only pull request rebuilds nothing, and a fail-safe widen for every unrecognised or unsafe path.**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-10-25T22:30:37Z
- **Completed:** 2026-10-25T22:33:25Z
- **Tasks:** 3
- **Files modified:** 2 (both created)

## Accomplishments
- `scripts/affected.py` prints one JSON object `{"build": [...], "simulate": [...]}` on stdout and nothing else, with each entry `{project, env, framework}` sorted by `(project, env)`; `--format paths` prints the documented line format with the build block first.
- The fanout table is complete and tested: a `homeworks/<id>/` change selects that project, a `lib/<name>/` change selects every consumer transitively through `library.json`, five shared paths widen to every project, and every unrecognised or unsafe path widens rather than being dropped.
- The project set includes the top-level `tests/` project when `tests/platformio.ini` exists, so a `lib/common`, `lib/port` or `lib/host` change reaches the shared native suite; `tests` appears in `build` only.
- `NO_BUILD_IMPACT` is explicit, documented in the module docstring and tested entry by entry; a views-only diff (`generated.manifest`, `mkdocs.yml`, a generated `docs/` page) yields two empty arrays.
- `framework` resolves through `[platformio] extra_configs` and `extends` to `arduino`, `espidf` and `native`, proven against the fixture and against the real `1_3-police-flasher` INI.
- Metadata is parsed with `StrictSafeLoader`; a circular `library.json` chain terminates; a project without `platformio.ini` exits 1 with the directory named; an empty directory is skipped.
- Two runs over the same input are byte-identical, and the suite grew from 144 to 168 tests, all green.

## Task Commits

Each task was committed atomically:

1. **Task 1: Map one changed homework file to its build and simulation entries end to end** - `83e97c9` (feat)
2. **Task 2: Implement the full fanout table and prove the fail-safe widening** - `494e9e7` (test)
3. **Task 3: Prove framework inheritance and run the mapper against a real git repository** - `dd472df` (test)

**Plan metadata:** committed with this SUMMARY (docs).

## Files Created/Modified

- `scripts/affected.py` — the PEP 723 diff mapper. Module constants `NO_BUILD_IMPACT`, `WIDEN_ALL`, `SIMULATE_OFF`; helpers `_changed_paths`, `_projects`, `_consumers`, `_fan_out`, `_entries`, `_render`, `main`; CLI flags `--dir`, `--paths-from`, `--base`, `--format {json,paths}`.
- `scripts/tests/test_affected.py` — `TracerTests`, `FanoutTests`, `NoBuildImpactTests`, `PathsFromTests`, `FrameworkTests`, `FixtureGuardTests`, `EndToEndTests`.

## Decisions Made

- **A real project without `platformio.ini` is a content problem, an empty directory is not.** `_has_homework_content` treats `homework.yaml` or a source suffix as project content; a directory with neither is still scaffolding and is skipped, so the matrix reports `{"build": [], "simulate": []}` instead of failing.
- **A symlinked or missing `homeworks/<id>` directory widens.** Only a real directory that the project set already knows can narrow the selection; anything else takes the fail-safe.
- **`lib/<name>` with no registered consumer widens.** This covers both a genuinely unconsumed library and a prefix-adjacent name such as `lib/commonplace`, so an under-approximation is impossible.
- **`tests/` is not a narrowable project path.** A change under `tests/` is an unrecognised shared input and widens, which is a safe over-approximation; the plan names only `homeworks/<id>/` as a narrowing rule.
- **Task 2 committed tests only.** Task 1 already implemented `_consumers` and `_fan_out` (its action lists the whole skeleton), so task 2's "complete" step had nothing left to change and its commit is the proof.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The plan lists `scripts/affected.py` under tasks 2 and 3, but the task-1 skeleton was already complete and correct: tasks 2 and 3 changed only the test module. No behaviour or scope changed; each task's verify passed at its own commit.
- The repository's `git` is wrapped by a command-condensing launcher, so `/usr/bin/git` was used for staging and committing inside the worktree. No functional impact.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None.

## Threat Flags

None beyond the plan's threat register. T-5-11 (containment refusal), T-5-12 (explicit `NO_BUILD_IMPACT` plus fail-safe widen), T-5-13 (`lib_deps` + `library.json`, alias-aware, `seen`-bounded walk) and T-5-32 (`tests/` in the project set; view inputs explicitly no-impact) are implemented and each has a passing test.

## Next Phase Readiness
- Phase 8 can consume `uv run scripts/affected.py --base <rev>` unchanged: stdout is one JSON object and every diagnostic is on stderr.
- 05-09's CI workflow wiring can invoke the same command; the mapper's only dependency is the repository's existing `PyYAML==6.0.3` pin.
- The real-tree run confirms the intended matrix today: `lib/common` + `lib/host` select `homeworks/1_3-police-flasher` (both environments) and `tests`, with `esp32s3_arduino` alone in `simulate`.

## Self-Check: PASSED

---
*Phase: 05-generated-views-and-documentation-site*
*Completed: 2026-10-25*
