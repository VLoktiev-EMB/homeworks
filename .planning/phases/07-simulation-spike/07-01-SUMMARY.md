---
phase: 07-simulation-spike
plan: 01
subsystem: build-tooling
tags: [platformio, scons, esptool, wokwi-cli, unittest, firmware-merge]

requires:
  - phase: 04.2-tracer-homework-1-3
    provides: the project-local esptool 5 merge post action and the homework build wiring
  - phase: 06-developer-experience-and-quality-layering
    provides: the stdlib-only test suite and the ruff per-file-ignore policy
provides:
  - shared merge post action at scripts/pio/merge_firmware.py with a pure command builder
  - nine-case unit test pinning the merge argv and both esptool package failures
  - executed three-valued path probe for the documented Wokwi command
affects: [08-ci-and-simulation-gate, 10-report-and-evidence-checker]

actuals:
  tokens: 4625
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - guarded SCons import so a build post action is importable by a unit test
    - pure argv builder extracted from an SCons post action
    - executed CLI path probe with a negative control and a non-vacuity assertion

key-files:
  created:
    - scripts/pio/merge_firmware.py
    - scripts/tests/test_merge_firmware.py
    - scripts/tests/test_simulation_paths.py
  modified:
    - homeworks/1_3-police-flasher/platformio.ini
    - pyproject.toml
  deleted:
    - homeworks/1_3-police-flasher/merge_firmware.py

key-decisions:
  - "Promote the merge action to scripts/pio and wire it with the relative post: path, deleting the project-local copy in the same change (D-12)."
  - "Guard Import('env') with try/except NameError so the module imports without SCons; this is the deliberate divergence from scripts/pio/compiledb.py."
  - "Check both package membership and get_package_dir() for None, so an unpacked tool-esptool fails with a named remedy instead of a TypeError (Pitfall 8)."
  - "Prove the documented Wokwi command by execution with WOKWI_CLI_SERVER at a closed local port, never by prose matching (D-13)."

patterns-established:
  - "Guarded SCons globals: import-safe post action, registration behind `if env is not None`."
  - "Pure command builder: argv assembly tested in process with a four-surface stub env."
  - "Three-valued CLI probe: positive, negative, and a non-vacuity assertion on the doubled path."

requirements-completed: [SIM-02]

coverage:
  - id: D1
    description: "The shared post action produces firmware.merged.bin from the project directory through the relative post: entry, and the per-homework copy is deleted from disk and git."
    requirement: SIM-02
    verification:
      - kind: integration
        ref: "pio run -d homeworks/1_3-police-flasher -t clean && pio run -d homeworks/1_3-police-flasher"
        status: pass
      - kind: automated
        ref: "test -f homeworks/1_3-police-flasher/.pio/build/esp32s3_arduino/firmware.merged.bin"
        status: pass
      - kind: automated
        ref: "git ls-files --error-unmatch homeworks/1_3-police-flasher/merge_firmware.py (expected to fail: untracked)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The merge command assembly is pinned by nine named unit cases without a live SCons environment."
    requirement: SIM-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_merge_firmware.py#MergeCommandTests (9 cases)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The documented Wokwi command resolves project-relative option values and a repository-root spelling fails at the doubled path."
    requirement: SIM-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_simulation_paths.py#SimulationPathTests (3 cases)"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-10-26
status: complete
plan_head_before: 1da08981f6bc42fa967f5151991e1dc3976dd624
plan_head_after: 536b71bed676af8cbaaca83fa64b532645a850f3
---

# Phase 7 Plan 1: Shared Merge Post Action and Wokwi Path Probe Summary

**The Wokwi merge action now lives in `scripts/pio/merge_firmware.py` and is covered by a pure-function argv test plus an executed path probe for the documented command.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-10-26T16:02:00+02:00 (approx)
- **Completed:** 2026-10-26T16:14:56+02:00
- **Tasks:** 3
- **Files modified:** 5 (3 created, 2 modified, 1 deleted)

## Accomplishments

- Promoted `merge_firmware.py` into the shared `scripts/pio` tree with a guarded SCons import, a pure `build_merge_command`, and named esptool failure modes.
- Repointed the homework `post:` entry and removed the project-local copy with `git rm`; the stale ruff F821 ignore is gone.
- A clean build produced `.pio/build/esp32s3_arduino/firmware.merged.bin` and printed `Merging firmware images into`, and `-t compiledb` still writes the project database.
- Nine named unit cases pin argv order, both offset renderings, quoting, the output target, board fallbacks, both package failures, and the Windows binary name.
- Three executed cases prove the documented Wokwi command reaches the connection stage, while a repository-root spelling fails at the doubled path.

## Task Commits

Each task was committed atomically:

1. **Task 1: The shared post action produces the merged image end to end** - `60a4aac` (feat)
2. **Task 2: Pin the merge command assembly with named unit cases** - `cbb7cf5` (test)
3. **Task 3: Prove the documented Wokwi command's path resolution without a network** - `536b71b` (test)

**Plan metadata:** committed separately after this SUMMARY.

## Files Created/Modified

- `scripts/pio/merge_firmware.py` - Shared SCons post action: `_quote`, `esptool_directory`, `esptool_binary`, `build_merge_command`, `merge_firmware`, guarded `env`.
- `scripts/tests/test_merge_firmware.py` - `MergeCommandTests` with the nine named cases and a four-surface stub env.
- `scripts/tests/test_simulation_paths.py` - `SimulationPathTests`: positive, negative, and non-vacuity probes.
- `homeworks/1_3-police-flasher/platformio.ini` - `post:../../scripts/pio/merge_firmware.py` beside the unchanged `pre:` compiledb entry.
- `pyproject.toml` - Removed `"homeworks/*/merge_firmware.py" = ["F821"]` and narrowed the comment to one site.
- `homeworks/1_3-police-flasher/merge_firmware.py` - Deleted via `git rm`.

## Decisions Made

- Followed D-12: the move and the deletion landed in one change, so two sources never coexisted.
- Kept `env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", merge_firmware)` byte-identical; `post:` is load order, the merge is the post action (Pitfall 7).
- Kept the `_quote` claim honest: double quotes provide argument atomicity for repository-controlled paths, not general metacharacter sanitization.
- The path probe asserts on `Error connecting to ws://127.0.0.1:1` and the doubled path, never on the errno, so it is sandbox-neutral (`EPERM` inside, `ECONNREFUSED` outside).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The plan's verification `git grep -n 'homeworks/1_3-police-flasher/merge_firmware.py'` matches historical `.planning/` artifacts (Phases 04.2, 06, 07 planning records). Those are published historical records and are not rewritten. Restricted to live files (`-- ':!.planning'`) the search returns no match, which is the intended contract.
- One harmless PlatformIO network-update probe was denied inside the command sandbox during the clean build; the build itself completed normally.

## Known Stubs

None.

## Threat Flags

None beyond the plan's threat model. T-07-01 (dummy token, exactly four child-environment names) and T-07-02 (`_quote` atomicity, tested) are both mitigated in the delivered code.

## Next Phase Readiness

- Plan 2 (owner-run Wokwi session) can rely on the shared post action producing the merged image and on the proven path rule.
- Phase 8 consumes the measured command surface; no `scripts/simulate.py` gate or wrapper was introduced (D-14).
- The `scripts/pio/` CI fan-out widening is intended per `scripts/affected.py` (T-5-12), not a defect.

## Self-Check: PASSED

- Created files exist: `scripts/pio/merge_firmware.py`, `scripts/tests/test_merge_firmware.py`, `scripts/tests/test_simulation_paths.py`, this SUMMARY.
- Task commits are ancestors of HEAD: `60a4aac`, `cbb7cf5`, `536b71b`.
