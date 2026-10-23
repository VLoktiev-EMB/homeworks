---
phase: 03-shared-core-and-dependency-rule
plan: 07
subsystem: build-configuration
tags: [partition-table, platformio, library-manifest, test-refactor, cleanup, conventional-commits]

# Dependency graph
requires:
  - phase: 03-shared-core-and-dependency-rule
    plan: 01
    provides: "lib/port contract headers, lib/common modules and the host-only tests/ project"
  - phase: 03-shared-core-and-dependency-rule
    plan: 03
    provides: "GPIO and logging port contracts with the final enum vocabulary"
  - phase: 03-shared-core-and-dependency-rule
    plan: 04
    provides: "lib/host deterministic fakes for all five contracts"
  - phase: 03-shared-core-and-dependency-rule
    plan: 05
    provides: "cross-fake contract suite and capturing log sink"
  - phase: 03-shared-core-and-dependency-rule
    plan: 06
    provides: "Arduino and ESP-IDF time, GPIO and logging adapters"
  - phase: 02-toolchain-truth
    provides: "the tracked default_16MB.csv and the smoke project the suite used to hard-read"
provides:
  - "partitions/default_16MB.csv as the permanent home of the 16 MB partition table"
  - "platformio.shared.ini resolving ../../partitions/default_16MB.csv from every project depth"
  - "A test suite with no reference to the deleted smoke project"
  - "Five library manifests at 0.2.0 with port declared header-only"
  - "An exact per-library source inventory and a green native suite"
affects: [03-08, 03-09, 04, 05, 06, 08, 11]

# Actuals (#2632) — chars/4 over the realized plan diff (19861 chars), not a harness count.
actuals:
  tokens: 4965
  tasks: 3
  commits: 3
  plan_head_before: bbeb0a2510d54db349fb9328e8dfa21a818a8387
  plan_head_after: 5cb1571

tech-stack:
  added: []
  patterns:
    - "Board data files live at repository root and are addressed by a project-relative path"
    - "Tests assert a path exists and separately assert the relative value normalizes to it"
    - "Manifest version is the single version site; no source returns a version string"
    - "A header-only library declares includeDir only and has no src directory"
    - "A directory retirement is its own commit with an assertable fixed subject"

key-files:
  created:
    - partitions/default_16MB.csv
  modified:
    - platformio.shared.ini
    - scripts/tests/test_pio_scripts.py
    - scripts/tests/test_gitignore.py
    - lib/common/library.json
    - lib/port/library.json
    - lib/arduino/library.json
    - lib/espidf/library.json
    - lib/host/library.json
  deleted:
    - homeworks/0_0-toolchain-smoke/README.md
    - homeworks/0_0-toolchain-smoke/platformio.ini
    - homeworks/0_0-toolchain-smoke/sdkconfig.defaults
    - homeworks/0_0-toolchain-smoke/src/main.cpp
    - lib/port/include/port.h
    - lib/port/src/port.c
    - lib/common/include/common.h
    - lib/common/src/common.c
    - lib/host/include/host.h
    - lib/host/src/host.c
    - lib/arduino/include/arduino_adapter.h
    - lib/arduino/src/arduino_adapter.c
    - lib/espidf/include/espidf_adapter.h
    - lib/espidf/src/espidf_adapter.c

key-decisions:
  - "The partition table moves with git mv, recorded as a 100% rename, so no checkout holds two copies or zero copies (D-18)"
  - "Both ESP sections carry board_build.partitions = ../../partitions/default_16MB.csv; a test asserts the root file exists and a second asserts the value normalizes from a homework-depth anchor to exactly that file"
  - "Task 1 kept presence-only source assertions; the exact set equality and the header-only emptiness assertion landed in Task 2, after the stubs were deleted, so every commit was green on the tree it described"
  - "The project fixture is tests/platformio.ini, and the suite pins its depth-correct hook override pre:../scripts/pio/compiledb.py and test_build_src = false"
  - "All five manifests are at 0.2.0; port drops srcDir and its src directory, the other four keep both build keys; no manifest gains a dependencies key (D-03, D-04, D-05)"
  - "The smoke project is deleted in its own commit with the exact subject chore(03): remove the temporary toolchain smoke project (D-19)"
  - "ADR-0007 is untouched: its mention of the smoke project is historical evidence, and its final paragraph already schedules the Phase 3 deletion (D-19)"

patterns-established:
  - "A moved data file is asserted twice: existence at the new path and normalization of every consumer's relative value onto it"
  - "Ignore-rule fixtures use neutral homework ids so deleting a directory cannot leave misleading test strings"
  - "Library inventory tests assert exact per-library source sets and that every source is a .c file"

requirements-completed: [ARCH-01, ARCH-02, ARCH-03, ARCH-06]

coverage:
  - id: D1
    description: "The 16 MB partition table lives at partitions/default_16MB.csv and both ESP sections resolve ../../partitions/default_16MB.csv onto it from a homework-depth path"
    verification:
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_partition_table_lives_at_repository_root"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_shared_partitions_value_resolves_to_the_root_file"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_shared_partitions_value_has_no_absolute_path"
        status: pass
    human_judgment: false
  - id: D2
    description: "The repository suite no longer reads the smoke project: the fixture is tests/platformio.ini and the ignore fixtures name homeworks/1_1-example"
    requirement: ARCH-06
    verification:
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_project_declares_the_depth_correct_hook_override"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_gitignore.py#test_sdkconfig_defaults_is_visible_and_env_output_is_not"
        status: pass
      - kind: unit
        ref: "python3 -m unittest discover -s scripts/tests -v"
        status: pass
    human_judgment: false
  - id: D3
    description: "lib/port is header-only: manifest 0.2.0 with includeDir only, no srcDir, no src directory and an empty source inventory"
    requirement: ARCH-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_library_manifests_agree_with_directories"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_header_only_library_has_no_sources"
        status: pass
    human_judgment: false
  - id: D4
    description: "lib/common ships exactly ring_buffer.c, timing.c, crc.c and hex.c with a 0.2.0 manifest carrying both build keys"
    requirement: ARCH-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_library_sources_match_the_inventory_exactly"
        status: pass
      - kind: integration
        ref: "pio test -d tests -e native#test_common_ring_buffer, test_common_timing, test_common_crc, test_common_hex"
        status: pass
    human_judgment: false
  - id: D5
    description: "lib/arduino, lib/espidf and lib/host keep srcDir, ship the expected adapter and fake modules, and declare 0.2.0"
    requirement: ARCH-03
    verification:
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_library_sources_match_the_inventory_exactly"
        status: pass
      - kind: integration
        ref: "pio test -d tests -e native#test_host_fakes, test_host_fake_time"
        status: pass
    human_judgment: false
  - id: D6
    description: "The Phase 2 stub header/source pairs are gone and no library source carries a version string or version function"
    requirement: ARCH-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_every_library_source_is_c"
        status: pass
      - kind: unit
        ref: "python3 -c check for 0.1.0 and _version( under lib/*/src/*"
        status: pass
    human_judgment: false
  - id: D7
    description: "homeworks/0_0-toolchain-smoke is absent from the working tree and the index, and the removal is its own commit"
    verification:
      - kind: unit
        ref: "git ls-files -- homeworks (empty) and test ! -e homeworks/0_0-toolchain-smoke"
        status: pass
      - kind: unit
        ref: "git log -1 --format=%s == chore(03): remove the temporary toolchain smoke project"
        status: pass
    human_judgment: false
  - id: D8
    description: "The partition-file move is a rename, not a copy followed by a deletion, and no unrelated change rode along in the deletion commit"
    verification: []
    human_judgment: true
    rationale: "A suite cannot distinguish a rename from an identical delete plus add after the fact, and it cannot prove that no unrelated file rode along; both are review judgements the plan records as deferred concerns."

duration: 4 min
completed: 2026-10-24
status: complete
---

# Phase 03 Plan 07: Phase 2 Carry-Forward Close-Out Summary

**The 16 MB partition table now lives at `partitions/default_16MB.csv`, the suite reads `tests/platformio.ini` instead of the smoke project, five manifests declare `0.2.0` with `port` header-only, and the smoke project is retired in a dedicated `chore(03)` commit.**

## Performance

- **Duration:** ~4 min (first plan commit 22:37:01Z to completion 22:38:03Z)
- **Started:** 2026-10-23T22:34:00Z (approximate session start)
- **Completed:** 2026-10-23T22:38:03Z
- **Tasks:** 3
- **Files modified:** 23 paths in the plan diff (133 insertions, 184 deletions)

## Accomplishments

- `partitions/default_16MB.csv` exists as the permanent, repository-level partition table; both ESP sections in `platformio.shared.ini` carry `board_build.partitions = ../../partitions/default_16MB.csv`.
- `scripts/tests/test_pio_scripts.py` is retargeted to `tests/platformio.ini`, pins the depth-correct hook override and `test_build_src = false`, and asserts both the root partition file and the normalization of the relative value onto it.
- `scripts/tests/test_gitignore.py` uses neutral `homeworks/1_1-example/...` fixtures, keeping every pattern assertion without naming a directory that no longer exists.
- All ten Phase 2 stub files (one header and one source per library) are deleted; the five manifests read `0.2.0`, `port` is header-only with no `srcDir`, and no source carries a version string.
- `homeworks/0_0-toolchain-smoke/` is gone from the working tree and the index, removed by its own commit with the exact required subject.
- Both gates pass on the final tree: `python3 -m unittest discover -s scripts/tests -v` (130 tests, OK) and `pio test -d tests -e native` (73 test cases, 73 succeeded).

## Task Commits

Each task was committed atomically:

1. **Task 1: Permanent partition table and a test harness that no longer reads the smoke project** — `47a9ea4` (chore)
2. **Task 2: Retire the five stub header/source pairs, bump the manifests, and tighten the inventory** — `f1112b4` (refactor)
3. **Task 3: Delete the temporary smoke project in a dedicated commit** — `5cb1571` (chore)
4. **Plan metadata** — `docs(03-07): complete 03-07 phase-2 carry-forward close-out plan` (recorded after this SUMMARY; not part of the measured three commits)

_Note: Task 3's subject is exactly `chore(03): remove the temporary toolchain smoke project`, as its verify asserts._

## Evidence Recorded by the Plan

### Partition-table move

`git status --short` at Task 1 staging showed a rename, not a copy plus delete:

```text
R  homeworks/0_0-toolchain-smoke/default_16MB.csv -> partitions/default_16MB.csv
```

The commit summary confirms `rename {homeworks/0_0-toolchain-smoke => partitions}/default_16MB.csv (100%)`.

Both new `board_build.partitions` values:

```text
[esp32s3_arduino]  ../../partitions/default_16MB.csv
[esp32s3_espidf]   ../../partitions/default_16MB.csv
```

The automated resolution check printed both values and resolved both to
`<repo>/partitions/default_16MB.csv` with `exists=True`.

### Final `LIB_SOURCES` mapping

```python
LIB_SOURCES = {
    "common": ("ring_buffer.c", "timing.c", "crc.c", "hex.c"),
    "port": (),
    "arduino": ("time.c", "gpio.c", "log.c"),
    "espidf": ("time.c", "gpio.c", "log.c"),
    "host": ("fake_time.c", "fake_gpio.c", "fake_i2c.c", "fake_spi.c", "fake_log.c"),
}
HEADER_ONLY_LIBRARIES = ("port",)
```

### Manifest contents after Task 2

```json
{ "name": "common",  "version": "0.2.0", "build": { "srcDir": "src", "includeDir": "include" } }
{ "name": "arduino", "version": "0.2.0", "build": { "srcDir": "src", "includeDir": "include" } }
{ "name": "espidf",  "version": "0.2.0", "build": { "srcDir": "src", "includeDir": "include" } }
{ "name": "host",    "version": "0.2.0", "build": { "srcDir": "src", "includeDir": "include" } }
{ "name": "port",    "version": "0.2.0", "build": { "includeDir": "include" } }
```

(shown collapsed; each file is written with two-space indentation and a trailing newline, key order
`name`, `version`, `build`.)

### Deleted stubs

`lib/port/include/port.h`, `lib/port/src/port.c`, `lib/common/include/common.h`,
`lib/common/src/common.c`, `lib/host/include/host.h`, `lib/host/src/host.c`,
`lib/arduino/include/arduino_adapter.h`, `lib/arduino/src/arduino_adapter.c`,
`lib/espidf/include/espidf_adapter.h`, `lib/espidf/src/espidf_adapter.c`.

After the deletion, `lib/port/src` was removed from the filesystem as well.

### Deletion commit

- Subject: `chore(03): remove the temporary toolchain smoke project`
- Hash: `5cb1571`
- Tree and index: `test ! -e homeworks/0_0-toolchain-smoke` passed; `git ls-files -- homeworks` printed nothing.

### Suite results

| Gate | Result |
|------|--------|
| `python3 -m unittest discover -s scripts/tests -v` | 130 tests, OK |
| `pio test -d tests -e native` | 73 test cases, 73 succeeded |
| `python3 -c` manifest/stub/version check | `bad=[] stubs=[] vers=[] empty_port_src=True` |
| `python3 -c` smoke-reference scan over `scripts`, `platformio.shared.ini`, `AGENTS.md`, `README.md` | `hits=[]` |

## Files Created/Modified

- `partitions/default_16MB.csv` — the moved 16 MB partition table (`0x10000` app offset preserved)
- `platformio.shared.ini` — both ESP sections point at `../../partitions/default_16MB.csv`; everything else byte-identical
- `scripts/tests/test_pio_scripts.py` — project fixture retargeted, partitions tests added, manifest/source contract tightened
- `scripts/tests/test_gitignore.py` — neutral `homeworks/1_1-example/...` fixtures
- `lib/{common,port,arduino,espidf,host}/library.json` — version `0.2.0`; `port` without `srcDir`
- Deleted: the ten Phase 2 stub files and `homeworks/0_0-toolchain-smoke/**`

## Decisions Made

- **Ordering is the contract.** Task 1 could only add presence assertions because the stubs were still on disk; Task 2 deleted the stubs and added exact set equality in the same commit; Task 3 removed the project after both test modules had stopped naming it. Every commit was green on its own tree.
- **The synthetic anchor is load-bearing but never asserted to exist.** `homeworks/1_1-example` exists only to normalize `../../partitions/default_16MB.csv`; the test asserts the resolved path equals the root file and never calls `exists()` on the anchor.
- **`port` is the only header-only library.** Its manifest keeps `includeDir` and drops `srcDir`; a separate test asserts both the empty inventory and the absent-or-empty `src/` directory.
- **No manifest gained a `dependencies` key.** A dedicated test enforces D-03 so a future edit cannot quietly reintroduce registry resolution.

## Deviations from Plan

None - plan executed exactly as written.

Task 3 removed no ignored build output because this worktree never ran a build of the smoke
project; the only entries present were the five tracked files, four of which remained after the
Task 1 rename and were removed by `git rm -r`.

## Issues Encountered

- The repository's condensing shell wrapper (`rtk`) refused several compound commands that embed
  `git` in command substitution or `git -C`. The same commands were run as plain `/usr/bin/git`
  invocations inside the worktree; no repository content was affected.
- `pio test -d tests -e native` printed a sandbox `network-outbound` notice for a GitHub address
  while PlatformIO probed for updates. The process still exited 0 with all 73 test cases green, so
  no retry was needed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `partitions/default_16MB.csv` is the only copy of the table, and both ESP sections resolve to it.
- The suite has no dependency on `homeworks/`, so plan 03-08's checker and plan 03-09's determinism
  proof can run against a tree whose `homeworks/` directory is empty.
- Open and deliberately not closed here: WR-04 (broad `.gitignore` patterns) remains a recorded risk
  for Phase 6 or Phase 8, and the post-Phase-3 target-compile gate for adapters now has no smoke
  project to compile against; the Phase 4 template build and Phase 8 CI own that gap.

---
*Phase: 03-shared-core-and-dependency-rule*
*Completed: 2026-10-24*

## Self-Check: PASSED

- `partitions/default_16MB.csv` exists; `03-07-SUMMARY.md` exists.
- Commits `47a9ea4`, `f1112b4` and `5cb1571` are ancestors of HEAD.
- `homeworks/0_0-toolchain-smoke` is absent and `git ls-files -- homeworks` is empty.
