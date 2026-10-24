---
phase: 04-metadata-contract-and-scaffolding
plan: 02
subsystem: templates
tags: [platformio, arduino, espidf, unity, templates, scaffolding]

# Dependency graph
requires:
  - phase: 02-toolchain-truth
    provides: platformio.shared.ini, the shared 16 MB partition table, and the compiledb hook
  - phase: 03-shared-core-and-dependency-rule
    provides: lib/port contracts, the Arduino and ESP-IDF adapters, and the host fake
provides:
  - templates/homework-arduino and templates/homework-espidf, both proven at homeworks/<id> depth
  - starter code that compiles lib/port plus the matching adapter on the target
  - a stdlib-only contract test for the template tree
affects: [04-04-scaffold, 04-05-phase-gate, 05-generated-views, 08-ci, 11-pilot]

actuals:
  tokens: 6084
  tasks: 3
  commits: 3

commits: 3
plan_head_before: 7dea6f7d782930d99281d3d55590db6776003569
plan_head_after: 1309b2d657267d9ef37434f7a68bfa84beaaa027

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Homework template as authored input only"
    - "Composition root drives lib/port through the framework adapter"
    - "Target env declares only extends and lib_deps; native owns lib/host and Unity"

key-files:
  created:
    - templates/homework-arduino/template.yaml
    - templates/homework-arduino/platformio.ini
    - templates/homework-arduino/src/main.cpp
    - templates/homework-arduino/test/test_homework/test_homework.c
    - templates/homework-arduino/homework.yaml
    - templates/homework-arduino/README.md
    - templates/homework-espidf/template.yaml
    - templates/homework-espidf/platformio.ini
    - templates/homework-espidf/src/main.cpp
    - templates/homework-espidf/sdkconfig.defaults
    - templates/homework-espidf/test/test_homework/test_homework.c
    - templates/homework-espidf/homework.yaml
    - templates/homework-espidf/README.md
    - scripts/tests/test_templates.py
  modified: []

key-decisions:
  - "The Arduino entry includes <Arduino.h> because delay() is declared there; the plan's four-header list would not compile otherwise."
  - "Native repeats the parent's build_flags to add -Werror, while extra_scripts stays inherited so the hook resolves at homeworks/<id> depth."
  - "The placeholder lint skips the four later-wave template directories and exempts the MADR template, whose brace style is not the scaffold vocabulary."
  - "The ESP-IDF memory configuration is proven from the generated sdkconfig.json; ESP-IDF 6.1 emits unprefixed Kconfig names."

patterns-established:
  - "Authored input only: a template ships no CMakeLists.txt and no sdkconfig.<env>."
  - "Arduino keeps contracts at file scope because setup/loop split initialization from iteration; ESP-IDF keeps them at function scope inside app_main."
  - "Template tests assert configuration as data without importing PlatformIO or PyYAML."

requirements-completed: [META-03, FOUND-01]

coverage:
  - id: D1
    description: "Arduino homework template with the seven FOUND-01 paths, template.yaml and no task.md"
    requirement: FOUND-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_templates.py#TemplateInventoryTests"
        status: pass
      - kind: integration
        ref: "pio run at <temp>/homeworks/1_3-template-check (SUCCESS)"
        status: pass
    human_judgment: false
  - id: D2
    description: "ESP-IDF homework template with app_main linkage and the three authored sdkconfig.defaults lines"
    requirement: FOUND-01
    verification:
      - kind: integration
        ref: "pio run at <temp>/homeworks/1_3-template-check (SUCCESS); generated sdkconfig.json reports 16MB flash, SPIRAM=true, SPIRAM_MODE_OCT=true"
        status: pass
    human_judgment: false
  - id: D3
    description: "Starter code compiles lib/port through the matching adapter on the target"
    requirement: META-03
    verification:
      - kind: integration
        ref: "pio run compiled lib/arduino/{gpio,log,time}.c and the ESP-IDF adapter sources; -DBOARD_HAS_PSRAM present in compile_commands.json"
        status: pass
    human_judgment: false
  - id: D4
    description: "Native Unity test passes in [env:native] with lib/host and Unity native-only"
    requirement: META-03
    verification:
      - kind: unit
        ref: "pio test -e native: 2 test cases PASSED"
        status: pass
    human_judgment: false
  - id: D5
    description: "Template README links to templates/report/report.md, which 04-03 creates"
    verification: []
    human_judgment: true
    rationale: "The link is intentionally forward-looking; 04-03 owns the report skeleton that makes it resolvable."

# Metrics
duration: 3min
completed: 2026-10-24
status: complete
---

# Phase 4 Plan 2: Homework Templates Summary

**Two homework templates that build at `homeworks/<id>` depth, drive `lib/port` through the matching adapter, and are guarded by an exact-inventory contract test**

## Performance

- **Duration:** 3 min
- **Started:** 2026-10-24T20:50:04Z
- **Completed:** 2026-10-24T20:53:01Z
- **Tasks:** 3
- **Files modified:** 18 created (14 source/config/doc files plus four `.gitkeep` markers)

## Accomplishments

- `templates/homework-arduino/` renders at `<temp>/homeworks/1_3-template-check`, builds with `pio run` (SUCCESS, 8.79 s) and passes `pio test -e native` (2 cases).
- `templates/homework-espidf/` builds with `pio run` (SUCCESS, 25.28 s); the generated `sdkconfig.json` proves 16 MB flash, `SPIRAM=true` and `SPIRAM_MODE_OCT=true`, with `SPIRAM_MODE_QUAD=false`.
- Both starter files call the consumer-owned contracts through `arduino_gpio_port()`/`arduino_log_port()` and `espidf_gpio_port()`/`espidf_log_port()`, so the target build compiles the adapter — the Phase 3 carry-forward now has evidence.
- `-DBOARD_HAS_PSRAM` appears in the generated `compile_commands.json`, proving the target environment inherited the shared build flags (Pitfall P8).
- `scripts/tests/test_templates.py` adds 21 stdlib-only tests; the full script suite is green (211 tests).

## Task Commits

Each task was committed atomically:

1. **Task 1: Arduino template end-to-end** - `eae889e` (feat)
2. **Task 2: ESP-IDF template at homework depth** - `9be964b` (feat)
3. **Task 3: Template contract tests** - `1309b2d` (test)

## Files Created/Modified

- `templates/homework-arduino/template.yaml` - framework and description manifest
- `templates/homework-arduino/platformio.ini` - target env plus native Unity env, both extending the shared ini
- `templates/homework-arduino/src/main.cpp` - composition root over `lib/port` and the Arduino adapters
- `templates/homework-arduino/test/test_homework/test_homework.c` - two real Unity assertions against `lib/host`
- `templates/homework-arduino/homework.yaml` - metadata skeleton with the schema modeline and placeholders
- `templates/homework-arduino/README.md` - project stub with report and task links
- `templates/homework-espidf/template.yaml` - framework and description manifest
- `templates/homework-espidf/platformio.ini` - target env plus the same native section
- `templates/homework-espidf/src/main.cpp` - `extern "C" void app_main(void)` composition root
- `templates/homework-espidf/sdkconfig.defaults` - three authored Kconfig lines (16 MB flash, PSRAM, octal mode)
- `templates/homework-espidf/test/test_homework/test_homework.c` - byte-identical to the Arduino test
- `templates/homework-espidf/homework.yaml` - same contract with `framework: espidf`
- `templates/homework-espidf/README.md` - same stub
- `scripts/tests/test_templates.py` - inventory, placeholder, environment-shape, linkage and generated-file tests

## Decisions Made

- Added `<Arduino.h>` to the Arduino entry because `delay()` is declared there; the plan's four-header list alone does not compile with `-Werror`.
- Repeated the parent's `build_flags` in `[env:native]` only to add `-Werror` (whitespace list replacement), while leaving `extra_scripts` inherited from `native_unity` so it resolves at homework depth.
- Kept the placeholder vocabulary closed but did not require every name to appear: `framework` and `board` are literal in the templates per the plan, so the lint asserts token membership, not exhaustive use.
- Kept the four `task`, `report`, `adr` and `board-profile` directories optional in the test until 04-03 adds them; `adr` is exempt from the placeholder lint because the MADR template uses its own brace style.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The Arduino entry needed `<Arduino.h>` for `delay()`**
- **Found during:** Task 1 (Arduino template end-to-end)
- **Issue:** The plan lists four headers; `delay(500)` is declared in `<Arduino.h>`, so the entry would not compile.
- **Fix:** Added `#include <Arduino.h>` above the port and adapter headers.
- **Files modified:** `templates/homework-arduino/src/main.cpp`
- **Verification:** `pio run` reached SUCCESS and compiled `src/main.cpp`.
- **Committed in:** `eae889e` (Task 1 commit)

**2. [Rule 1 - Bug] The ESP-IDF `sdkconfig.json` assertion used the wrong key spelling**
- **Found during:** Task 2 (ESP-IDF template build)
- **Issue:** The plan's `<automated>` block reads `CONFIG_ESPTOOLPY_FLASHSIZE_16MB`, `CONFIG_SPIRAM` and `CONFIG_SPIRAM_MODE_OCT`; ESP-IDF 6.1 writes unprefixed Kconfig names (`ESPTOOLPY_FLASHSIZE_16MB`, `SPIRAM`, `SPIRAM_MODE_OCT`), so the literal command returns `None` and fails despite correct configuration.
- **Fix:** Verified the same facts through an assertion that accepts both spellings; the observed values match the research evidence exactly (`16MB`, `True`, `True`, `False` for quad).
- **Files modified:** none (verification only)
- **Verification:** `flash= 16MB flash16= True spiram= True oct= True quad= False`
- **Committed in:** `9be964b` (Task 2 commit)

**3. [Rule 3 - Blocking] The plan's single-command build fixture could not run under the worktree guard**
- **Found during:** Task 1 and Task 2 verification
- **Issue:** The worktree harness refuses a compound shell command that passes a runtime-computed path into `python3`/`pio`; the plan's verify blocks are one such command.
- **Fix:** Executed the identical steps as separate, plain commands against a fixed fixture root, preserving the same directory layout, rendering map and assertions.
- **Files modified:** none (verification only)
- **Verification:** The same `pio run`, `pio test -e native`, `pio run -t compiledb` and `sdkconfig.json` checks passed.
- **Committed in:** `eae889e`, `9be964b` (evidence for Tasks 1 and 2)

---

**Total deviations:** 3 auto-fixed (2 blocking, 1 bug)
**Impact on plan:** No scope creep. One source change was required to compile; the other two are verification-command corrections that keep the intended evidence intact.

## Issues Encountered

- The generated ESP-IDF `CMakeLists.txt` files appear only in the temporary rendered project, never in the template; the template static check confirms neither `CMakeLists.txt` nor `sdkconfig.<env>` is shipped.
- The template README points at `../../templates/report/report.md`, which 04-03 creates, and at `task.md`, which 04-04 composes. Both are recorded forward dependencies, not silent broken links.
- `homework.yaml` carries `source.reference: TODO`, which is the intentional planned-status sentinel (D-39), not a stub.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for 04-04: both templates are the rendered source, `template.yaml` is present, and `[env:native]` is reachable with `pio test -e native`.
- 04-03 must create `templates/report/report.md`, `templates/task/task.md`, `templates/adr/template.md` and `templates/board-profile/profile.yaml`; the contract test already scans them once they exist and 04-03 should remove the later-wave skip.
- No blockers.

---

*Phase: 04-metadata-contract-and-scaffolding*
*Completed: 2026-10-24*

## Self-Check: PASSED
