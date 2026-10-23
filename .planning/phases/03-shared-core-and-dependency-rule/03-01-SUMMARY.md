---
phase: 03-shared-core-and-dependency-rule
plan: 01
subsystem: testing
tags: [platformio, unity, native, ports-and-adapters, c11, fake-clock, timing]

# Dependency graph
requires:
  - phase: 02-toolchain-truth
    provides: "platformio.shared.ini [native_unity], symlink:// library layout, PlatformIO Core 6.2.0"
provides:
  - "Host-only tests/ PlatformIO project linking common, port and host with Unity pinned at 2.6.1"
  - "Consumer-owned port_time_t contract and port_status_t vocabulary"
  - "Framework-free common/timing module (elapsed, expiry, debounce)"
  - "Deterministic caller-owned host fake clock"
  - "Two native Unity suites: 15 timing cases and 4 fake-clock cases"
affects: [03-02, 03-03, 03-04, 03-05, 03-06, 03-07, 03-09]

actuals:
  tokens: 3941
  tasks: 3
  commits: 3
  plan_head_before: 2f2d4035fa354d13a9ebd3452cf259697d1f2091
  plan_head_after: de2b23a11f577eae2bfd1e80523201dee526e85b

tech-stack:
  added: ["Unity 2.6.1 (PlatformIO registry, pinned to an exact version)"]
  patterns:
    - "Consumer-owned vtable struct with an opaque void *ctx"
    - "Factory returns the port struct by value, positional initialization"
    - "Time is injected, never read, inside lib/common"
    - "Wraparound-safe unsigned/signed 32-bit difference arithmetic"
    - "Caller-owned allocation-free test doubles in lib/host"

key-files:
  created:
    - tests/platformio.ini
    - tests/src/main.c
    - tests/test/test_common_timing/test_timing.c
    - tests/test/test_host_fake_time/test_fake_time.c
    - lib/port/include/port/status.h
    - lib/port/include/port/time.h
    - lib/common/include/common/timing.h
    - lib/common/src/timing.c
    - lib/host/include/host/fake_time.h
    - lib/host/src/fake_time.c
  modified:
    - tests/test/test_common_timing/test_timing.c (extended from 7 to 15 cases in Task 2)

key-decisions:
  - "common depends on port; port is header-only and owns no global mutable state"
  - "common_debounce_t keeps three fields (stable, candidate, candidate_since_ms) so a transition beginning at time zero is distinguishable from no pending transition"
  - "Expiry uses the sign of the 32-bit difference, so the documented horizon is 2^31 - 1 ms (~24.85 days), not 49.7 days"
  - "test_dir is a project-level option and lives in [platformio]; placing it in [env:native] is ignored by PlatformIO"
  - "tests/src/main.c exists only to populate the compiledb database; test_build_src = false keeps it out of every Unity app"

patterns-established:
  - "Header shell: #pragma once first, extern \"C\" guard last, C standard headers only"
  - "Every Unity suite defines setUp and tearDown, even when empty"
  - "Fakes return the same port type the real adapters return, so signature drift is a compile error"

requirements-completed: [ARCH-01, ARCH-02, ARCH-03, ARCH-06]

coverage:
  - id: D1
    description: "Host-only tests/ PlatformIO project builds common, port and host and runs two Unity suites without a target toolchain"
    requirement: ARCH-06
    verification:
      - kind: integration
        ref: "pio test -d tests -e native"
        status: pass
    human_judgment: false
  - id: D2
    description: "port_time_t consumer-owned clock contract and port_status_t error vocabulary, header-only and framework-free"
    requirement: ARCH-01
    verification:
      - kind: automated
        ref: "python3 -c header assertion over lib/port/include/port/{status,time}.h"
        status: pass
    human_judgment: false
  - id: D3
    description: "common/timing computes elapsed, expiry and debounce from injected time with wraparound-safe arithmetic and NULL guards"
    requirement: ARCH-02
    verification:
      - kind: unit
        ref: "tests/test/test_common_timing/test_timing.c#15 cases"
        status: pass
    human_judgment: false
  - id: D4
    description: "host fake clock resets, advances, wraps and keeps two instances independent without global state"
    requirement: ARCH-03
    verification:
      - kind: unit
        ref: "tests/test/test_host_fake_time/test_fake_time.c#4 cases"
        status: pass
    human_judgment: false
  - id: D5
    description: "Compilation database contains the shared translation units, proving the shared sources compile natively"
    requirement: ARCH-06
    verification:
      - kind: integration
        ref: "pio run -d tests -e native -t compiledb"
        status: pass
    human_judgment: false
  - id: D6
    description: "Unity is pinned at exactly 2.6.1 and the installed manifest reports that version"
    requirement: ARCH-06
    verification:
      - kind: automated
        ref: "tests/.pio/libdeps/native/Unity/library.json#version"
        status: pass
    human_judgment: false

duration: 2 min
completed: 2026-10-24
status: complete
---

# Phase 03 Plan 01: Native Ports-and-Adapters Slice Summary

**A consumer-owned `port_time_t` contract, a framework-free `common/timing` module and a deterministic host fake clock, proven by 19 Unity cases in a host-only PlatformIO project with Unity pinned at 2.6.1.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-10-23T22:23:37Z
- **Completed:** 2026-10-23T22:25:49Z
- **Tasks:** 3
- **Files modified:** 10 (10 created; one extended in a second task)

## Accomplishments

- `pio test -d tests -e native` exits 0 with 19 passing cases: 15 in `test_common_timing` and 4 in `test_host_fake_time`.
- `common -> port` compiles and links on the host with no target toolchain; `port` is header-only and has no `src/`.
- The debounce helper is driven end to end by `host_fake_time_port`, so timing behaviour is deterministic and independent of the wall clock.
- `pio run -d tests -e native -t compiledb` produces a 7-entry database containing `lib/common/src/timing.c`, `lib/host/src/fake_time.c` and the project's `src/main.c`.
- The installed Unity manifest reports exactly `2.6.1`; no unpinned `^2.6.1` install line appears in the build log.

## Task Commits

1. **Task 1: End-to-end slice — port time contract, common timing, host fake clock, green Unity suite** — `7591a19` (feat)
2. **Task 2: Complete the timing contract — expiry horizon, debounce boundaries, NULL safety** — `4b47588` (test)
3. **Task 3: Fake-clock isolation suite — reset, advance, wraparound, multiple instances** — `de2b23a` (test)

## Exact `tests/platformio.ini`

```ini
; tests/platformio.ini — the shared-library native suite.
; extra_configs and extra_scripts resolve relative to THIS project directory,
; so both paths are one level up, not two.
[platformio]
default_envs = native
extra_configs = ../platformio.shared.ini
; Project-level option: PlatformIO ignores test_dir inside an [env:] section.
test_dir = test

[env:native]
extends = native_unity
test_framework = unity
; Written explicitly: the PlatformIO default is not a repository contract, and a
; future default change must not link tests/src/main.c into every Unity app.
test_build_src = false
; extends replaces list options wholesale; repeat the parent's flags and add -Werror.
build_flags =
    -std=c11
    -Wall
    -Wextra
    -Werror
; The inherited native_unity value points at ../../scripts/..., which resolves two
; levels above the repository from here. Override it so the hook stays inside the repo.
extra_scripts = pre:../scripts/pio/compiledb.py
lib_deps =
    common=symlink://../lib/common
    port=symlink://../lib/port
    host=symlink://../lib/host
    throwtheswitch/Unity@2.6.1
```

## Unity install evidence

First run (cold cache) printed:

```
Library Manager: Installing throwtheswitch/Unity @ 2.6.1
Library Manager: Unity@2.6.1 has been installed!
```

`tests/.pio/libdeps/native/Unity/library.json` reports `"version": "2.6.1"` and
`"license": "MIT"` with the official `ThrowTheSwitch/Unity.git` repository.

## `-Werror` disposition (assumption A9)

No fallback was needed. `-Werror` stayed in the four-line `build_flags` list and every
suite compiled clean; no warning originated inside Unity 2.6.1 or the host headers.
Observed warning text: none.

## `common_debounce_t` field layout

```c
typedef struct common_debounce {
    bool stable;
    bool candidate;
    uint32_t candidate_since_ms;
} common_debounce_t;
```

Three fields are deliberate: a two-field `stable` / `last_change_ms` pair cannot
distinguish "no pending change" from "a change that began at time zero", so the next
transition would latch immediately. `candidate` names the level being observed and
`candidate_since_ms` records when that candidacy began.

## Documented expiry horizon

`common_timer_expired` decides on the sign of the 32-bit difference `now - deadline`.
That detects at most `2^31 - 1` ms — about **24.85 days** — into the future. A deadline
farther away wraps to a negative difference and therefore reads as already expired. The
header records this explicitly and does not describe the horizon as 49.7 days.

## Files Created/Modified

- `tests/platformio.ini` — host-only project: `[platformio]` (`default_envs`, `extra_configs`, `test_dir`) and one `[env:native]` extending `native_unity`
- `tests/src/main.c` — compiledb-only probe; never linked into a Unity app
- `tests/test/test_common_timing/test_timing.c` — 15 cases for elapsed, expiry, debounce boundaries and NULL safety
- `tests/test/test_host_fake_time/test_fake_time.c` — 4 cases for reset, advance, wraparound and instance isolation
- `lib/port/include/port/status.h` — `port_status_t` with `PORT_OK` and four error values
- `lib/port/include/port/time.h` — `port_time_t`, `void *ctx`, `static inline port_time_now_ms`
- `lib/common/include/common/timing.h` — `common_debounce_t` and the three helper declarations
- `lib/common/src/timing.c` — wraparound-safe arithmetic; no clock, sleep or delay call
- `lib/host/include/host/fake_time.h` — caller-owned `host_fake_time_t` and factory
- `lib/host/src/fake_time.c` — reset, advance and the private `now_ms` callback

## Decisions Made

- Wrote the tracer slice for keeps, so Task 2's contract work (signed-difference expiry,
  NULL guards, horizon comment) was already present in the Task 1 source; Task 2 added the
  branch tests that make every path observable.
- Kept `tests/` a subdirectory and added no root `platformio.ini` and no `lib_extra_dirs`,
  so the LDF cannot auto-discover an adapter into the native build.
- Pinned Unity explicitly rather than relying on `test_framework = unity`'s `^2.6.1` range.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `test_dir` placed in `[env:native]` is ignored by PlatformIO**
- **Found during:** Task 1 (first `pio test` run)
- **Issue:** the plan specified `test_dir = test` inside `[env:native]`. PlatformIO printed
  `Warning! Ignore unknown configuration option 'test_dir' in section [env:native]` and
  silently kept its default (`test`, the same value).
- **Fix:** moved the option to `[platformio]`, where PlatformIO accepts it. The value is
  unchanged and the warning is gone.
- **Files modified:** `tests/platformio.ini`
- **Verification:** re-ran the suite; `config-warning=absent`, 19/19 pass
- **Committed in:** `7591a19` (part of Task 1 commit)

**2. [Rule 1 - Plan verify command defect] The compiledb assertion assumed absolute entry paths**
- **Found during:** Task 1 verification
- **Issue:** the plan's `<automated>` check required an entry ending with `tests/src/main.c`.
  PlatformIO writes project sources as a project-relative `src/main.c` and records the
  absolute project directory in the entry's `directory` field. The literal check therefore
  reported `missing=['tests/src/main.c']` while the database was correct.
- **Fix:** no code change. Ran the equivalent assertion that resolves
  `directory + "/" + file` before matching; the intent (all three translation units present)
  is unchanged.
- **Files modified:** none (verification only)
- **Verification:** `entries=7 missing=[]`; the database contains
  `lib/common/src/timing.c`, `lib/host/src/fake_time.c` and `<tests>/src/main.c`
- **Committed in:** n/a (verification-only; evidence in this summary)

---

**Total deviations:** 2 auto-fixed (2 bugs, one of them in the plan's verify command)
**Impact on plan:** Neither changes behaviour. The config option now sits where PlatformIO
reads it, and the compiledb check proves the same contract while accounting for the
documented path representation.

## Issues Encountered

None beyond the two deviations above.

## Known Stubs

None. `tests/src/main.c` intentionally performs no work; it is a compilation probe, and
`test_build_src = false` keeps it out of every test binary.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The `tests/` project, the `port_time_t` contract and the fake clock are ready for the
  remaining Phase 3 plans to expand from this slice.
- The Phase 2 stub headers and sources (`lib/port/include/port.h`, `lib/common/include/common.h`,
  `lib/host/include/host.h` and their `.c` files) remain untouched as planned; plan 03-07 retires them.
- Repositories' Python suite still passes: 122 tests OK after the new native project was added.

---
*Phase: 03-shared-core-and-dependency-rule*
*Completed: 2026-10-24*

## Self-Check: PASSED

- All 10 declared files exist on disk.
- All three task commits (`7591a19`, `4b47588`, `de2b23a`) are ancestors of HEAD.
- `pio test -d tests -e native`: 19/19 passed.
- `python3 -m unittest discover -s scripts/tests -v`: 122 tests OK.
- Self-check verdict: PASSED.
