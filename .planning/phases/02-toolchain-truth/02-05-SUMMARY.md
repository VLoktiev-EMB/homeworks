---
phase: 02-toolchain-truth
plan: 05
subsystem: infra
tags: [adr, madr, symlink-libs, platformio, espressif32, esp32s3, n16r8, psram, compiledb, esptool, phase-gate]

# Dependency graph
requires:
  - phase: 02-toolchain-truth
    plan: 01
    provides: "platformio.shared.ini, five symlink-resolved libraries, the native slice and the compiledb SCons hook"
  - phase: 02-toolchain-truth
    plan: 02
    provides: "Scoped .gitignore rules and the extended no-generated-files hook for ESP-IDF build outputs"
  - phase: 02-toolchain-truth
    plan: 03
    provides: "The Arduino N16R8 environment, the preprocessed CONFIG_SPIRAM proof and the esptool reading pattern"
  - phase: 02-toolchain-truth
    plan: 04
    provides: "The ESP-IDF N16R8 environment, sdkconfig.json evidence and both criterion-2 artifacts"
provides:
  - "Permanent ADR-0007 recording symlink:// plus library.json over lib_extra_dirs and copying"
  - "A status index that agrees with ADR-0007 and advances the next number to 0008"
  - "One end-to-end phase gate: three green builds, three ordered CDB checks, both image headers, the preprocessed PSRAM macro, both pins, and the Phase 1 repository invariants"
affects: [03-shared-core, 05-metadata-generators, 08-ci, 10-report-evidence]

actuals:
  tokens: 1975
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "A permanent decision record is validated structurally by an existing test, not by review alone"
    - "The phase gate is a fixed command order because the single compilation database is overwritten per environment (P8)"
    - "Criterion 2 is re-proven from artifacts — sdkconfig.json and both image headers — never from the build banner or the board name (P10, P11)"

key-files:
  created:
    - docs/decisions/0007-symlink-shared-libraries.md
  modified:
    - docs/decisions/README.md

key-decisions:
  - "The ADR records the single version source in library.json and the LDF's explicit-dependency behaviour, because a second version site or a directory scan would silently drift"
  - "The gate runs the Arduino preprocessor check before the ESP-IDF compiledb step, because one database path is overwritten by every run (P8)"
  - "Token coverage is asserted as count == record count (64/64 and 1074/1074), not against the research baselines, because record totals are environment-dependent"

patterns-established:
  - "Phase gate order: build native -> arduino -> espidf, then assert each CDB immediately after its own compiledb"
  - "A negative claim (no script writes the shared config) is proven by a bounded source audit over scripts/ that allows mentions and fails only on creation or mutation constructs"

requirements-completed: [FOUND-09, ARCH-04]

coverage:
  - id: D1
    description: "ADR-0007 records the symlink:// plus library.json choice over lib_extra_dirs and copying, and the index agrees on number, title, status and date"
    requirement: ARCH-04
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_adrs -v -> 18 tests OK"
        status: pass
      - kind: integration
        ref: "grep -c '| 0007 |' docs/decisions/README.md -> 1; grep -qx 'Next number: **0008**.' -> exit 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "All three environments build green in the D-19 order: native, esp32s3_arduino, esp32s3_espidf"
    requirement: FOUND-09
    verification:
      - kind: integration
        ref: "pio run -e native -> SUCCESS 0.33 s; -e esp32s3_arduino -> SUCCESS 7.77 s; -e esp32s3_espidf -> SUCCESS 24.58 s"
        status: pass
    human_judgment: false
  - id: D3
    description: "Each compilation database is asserted immediately after its own compiledb run and contains the shared sources plus src/main.cpp"
    requirement: ARCH-04
    verification:
      - kind: integration
        ref: "native CDB -> entries=4 missing=[]"
        status: pass
      - kind: integration
        ref: "Arduino CDB -> entries=64 missing=[] counts={'qio_opi/include': 64, 'ARDUINO_PARTITION_default_16MB': 64, 'BOARD_HAS_PSRAM': 64}"
        status: pass
      - kind: integration
        ref: "ESP-IDF CDB -> entries=1074 missing=[] DESP_PLATFORM=1074"
        status: pass
    human_judgment: false
  - id: D4
    description: "The Arduino entry point preprocesses to CONFIG_SPIRAM 1 while the Arduino database is still in place"
    requirement: FOUND-09
    verification:
      - kind: integration
        ref: "preprocess src/main.cpp from its CDB command with -E -dM -> rc=0 CONFIG_SPIRAM=True"
        status: pass
    human_judgment: false
  - id: D5
    description: "Criterion 2 is re-proven from artifacts: 16 MB flash and octal PSRAM in sdkconfig.json, and Flash size: 16MB in both image headers with the esptool banner"
    requirement: FOUND-09
    verification:
      - kind: integration
        ref: "python3 assertion on .pio/build/esp32s3_espidf/config/sdkconfig.json -> 16MB + octal PSRAM OK"
        status: pass
      - kind: integration
        ref: "esptool image-info (Arduino) -> line 1 'Using tool-esptool@2.50400.0 package', line 10 'Flash size: 16MB'"
        status: pass
      - kind: integration
        ref: "esptool image-info (ESP-IDF) -> line 1 'Using tool-esptool@2.50400.0 package', line 10 'Flash size: 16MB'"
        status: pass
    human_judgment: false
  - id: D6
    description: "Both toolchain pins are re-proven at the final gate"
    requirement: FOUND-09
    verification:
      - kind: integration
        ref: "pio --version -> 'PlatformIO Core, version 6.2.0'; pio pkg show platformio/espressif32 -> 'Platform . 8.0.0 . Public . Published on Mon Oct 19 10:06:19 2026'"
        status: pass
    human_judgment: false
  - id: D7
    description: "Repository invariants hold: the script suite, the policy drift check, the PR-template check and pre-commit are all green"
    requirement: FOUND-09
    verification:
      - kind: integration
        ref: "python3 -m unittest discover -s scripts/tests -> Ran 122 tests, OK"
        status: pass
      - kind: integration
        ref: "python3 scripts/check_policy.py --check -> PASS: live GitHub state matches the committed policy"
        status: pass
      - kind: integration
        ref: "python3 scripts/check_pr_templates.py -> PASS: PR template contract satisfied"
        status: pass
      - kind: integration
        ref: "pre-commit run --all-files -> all hooks Passed (secrets, whitespace, end-of-files, merge conflicts, large files, generated files)"
        status: pass
    human_judgment: false
  - id: D8
    description: "No generated artifact is tracked, platformio.shared.ini is tracked, and no script creates or mutates the shared config"
    requirement: FOUND-09
    verification:
      - kind: integration
        ref: "git ls-files -ci --exclude-standard over the six declared generated pathspecs -> empty; git ls-files --error-unmatch platformio.shared.ini -> tracked"
        status: pass
      - kind: integration
        ref: "bounded scripts/ audit -> mentions=6 write-like=[]"
        status: pass
    human_judgment: false
  - id: D9
    description: "The shared config is a hand-authored addition, and every file this phase commits is in English"
    verification: []
    human_judgment: true
    rationale: "Whether an addition is hand-authored is a claim about history that no command asserts; the reviewer reads the adding commit and the prose. The English requirement is likewise a judgment over the committed text."

# Metrics
duration: 2 min
completed: 2026-10-23
status: complete
plan_head_before: d0c0c7697fb3c4a011c5384c4dc4ce63b28a32fe
plan_head_after: f7de8c9ea4c78120bace378c84b0372e682741ef
commits: 1
---

# Phase 02 Plan 05: ADR-0007 and the Closing Phase Gate Summary

**ADR-0007 records `symlink://` plus `library.json` as permanent decision 0007 with an agreeing index, and the phase closes on one end-to-end gate: three green builds (0.33 s / 7.77 s / 24.58 s), three ordered CDB checks (4 / 64 / 1074 records), `CONFIG_SPIRAM 1`, `Flash size: 16MB` in both image headers, both pins, and 122 green repository tests.**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-10-23T19:58:05Z
- **Completed:** 2026-10-23T19:59:50Z
- **Tasks:** 2/2 (Task 2 is evidence-only and changed no tracked file)
- **Files modified:** 2 (`docs/decisions/0007-symlink-shared-libraries.md` created, `docs/decisions/README.md` modified)

## Accomplishments

- `docs/decisions/0007-symlink-shared-libraries.md` is a MADR 4.0 record: five frontmatter keys, the eight sections in the enforced order, `Chosen option: "..."` opening the Decision Outcome, and exactly three considered options, each with a `###` pros-and-cons subsection.
- The record states the chosen spelling `lib_deps = <name>=symlink://../../lib/<name>` with a `library.json` per library, that the version lives only in `library.json` (D-12), and that the LDF no longer scans the whole `lib/`, so a foreign adapter cannot enter a build.
- `docs/decisions/README.md` gains `| 0007 | Symlinked shared libraries via lib_deps and library.json | accepted | 2026-10-23 |` and the single line `Next number: **0008**.`
- The phase gate re-proved criterion 2 from artifacts for both frameworks and confirmed the three environments, the CDB composition and the Phase 1 repository invariants.

## Measured evidence (final gate)

**Toolchain pins (FOUND-09):**

```text
$ pio --version
PlatformIO Core, version 6.2.0

$ pio pkg show platformio/espressif32
platformio/espressif32
Platform • 8.0.0 • Public • Published on Mon Oct 19 10:06:19 2026
```

The `pio pkg show` README fetch was denied by the network sandbox (`185.199.110.153:80`); the version metadata is unaffected, and the denial is not a registry failure.

**Builds, in the D-19 order (cold in this worktree):**

```text
native           SUCCESS   00:00:00.327   (Found 3 compatible libraries: common, port, host)
esp32s3_arduino  SUCCESS   00:00:07.771
esp32s3_espidf   SUCCESS   00:00:24.578
```

The research baselines were 0.34 s, 5.70 s and 24.73 s warm; the measured totals match within the expected cold-start spread.

**Compilation databases — each asserted immediately after its own `compiledb` (P8):**

```text
native:          entries=4     missing=[]
arduino:         entries=64    missing=[]  counts={'qio_opi/include': 64, 'ARDUINO_PARTITION_default_16MB': 64, 'BOARD_HAS_PSRAM': 64}
esp32s3_espidf:  entries=1074  missing=[]  DESP_PLATFORM=1074
```

Required sources present in every database: `lib/common/src/common.c`, `lib/port/src/port.c`, the matching adapter source, and `src/main.cpp`. Every Arduino token count equals the record count (64/64), and `-DESP_PLATFORM` covers all 1074 ESP-IDF records.

**Preprocessed Arduino entry point (P5, D-22), run before the ESP-IDF database replaced it:**

```text
rc=0 CONFIG_SPIRAM=True
```

**Effective Kconfig (`sdkconfig.json`), the criterion-2 proof:**

```text
ESPTOOLPY_FLASHSIZE='16MB' ESPTOOLPY_FLASHSIZE_16MB=True SPIRAM=True SPIRAM_MODE_OCT=True SPIRAM_MODE_QUAD=False
```

**Image headers (P11 — matched by content, never by line position):**

```text
Arduino:  line 1  Using tool-esptool@2.50400.0 package
          line 10 Flash size: 16MB      (Flash freq: 80m, Flash mode: DIO)
ESP-IDF:  line 1  Using tool-esptool@2.50400.0 package
          line 10 Flash size: 16MB      (image also reports ESP-IDF: 6.1.0)
```

`Flash mode: DIO` is expected PlatformIO behaviour for this platform and is not a defect.

**Repository invariants:**

```text
python3 -m unittest discover -s scripts/tests   -> Ran 122 tests in 3.074s, OK
python3 scripts/check_policy.py --check         -> PASS: live GitHub state matches the committed policy
python3 scripts/check_pr_templates.py           -> PASS: PR template contract satisfied
pre-commit run --all-files                      -> all hooks Passed
```

**Generated-file hygiene (D-18, D-23, T-02-14):**

```text
$ git ls-files -ci --exclude-standard -- compile_commands.json site .pio \
      'homeworks/*/CMakeLists.txt' 'homeworks/*/src/CMakeLists.txt' 'homeworks/*/sdkconfig.*'
(empty)

$ git ls-files --error-unmatch platformio.shared.ini
platformio.shared.ini
```

**Bounded D-03 source audit:**

```text
mentions=6 write-like=[]
```

Six lines under `scripts/` name `platformio.shared.ini`; none contains an open-for-write, a text or bytes write, a stream write, a copy/move, or a replace/rename/touch. Mentions alone are allowed — `scripts/tests/test_pio_scripts.py` legitimately asserts the contract.

**Hand-authored history (human-check):** `git rev-list HEAD -- platformio.shared.ini` returns `0e63ce9` (add, plan 02-01 Task 1) and `a4e7ff7` (modify, plan 02-01 Task 2). Commit `0e63ce9` is `feat(02-01): add shared PlatformIO config, five libraries and native smoke project`; the file arrives with the 21 authored source files and no generator. **Consumption proven; generation deferred to Phase 5.**

**Prose language:** every file this plan commits — the ADR and the index row — is English; the prior plans' committed prose (the smoke-project README and all five PLAN.md files) is English as well, per AGENTS.md.

**Three reproduced failure modes this design prevents** (recorded from the phase research, where each was observed):

| Failure | Observed message | Design that prevents it |
|---------|------------------|-------------------------|
| A `.c` entry point under the Arduino core 3.3.12 | `undefined reference to '_Z5setupv'` | `src/main.cpp` with the `#ifdef ARDUINO` branch (D-15 amended) |
| A public header without the linkage guard | `undefined reference to '_Z14common_versionv'` | `#ifdef __cplusplus / extern "C"` guards in every `lib/*/include/*.h` |
| `app_main` without its linkage specification | `undefined reference to 'app_main'` | `extern "C" void app_main(void)` under `#elif defined(ESP_PLATFORM)` |

## Task Commits

1. **Task 1: ADR-0007 for symlink:// and the status-index update** — `f7de8c9` (docs)
2. **Task 2: Phase gate — three builds, three CDB checks, both image checks, the PSRAM macro, pins, tests and pre-commit** — no commit (its `<files>` is "None tracked"; it reads gitignored build output only)

**Plan metadata:** committed separately as `docs(02-05): complete phase gate plan` (this file).

Commit count for this plan is **1**, measured as `git rev-list --count d0c0c76..f7de8c9`.

## Files Created/Modified

- `docs/decisions/0007-symlink-shared-libraries.md` — MADR 4.0 record for the symlinked-library decision; frontmatter `status: accepted`, `date: 2026-10-23`, title `Symlinked shared libraries via lib_deps and library.json`
- `docs/decisions/README.md` — a `0007` status row and the line `Next number: **0008**.`

## Decisions Made

- The ADR's Confirmation section cites only evidence this phase produced — the three green builds, the CDB coverage, the preprocessed macro and both image headers, plus `scripts/tests/test_pio_scripts.py` — and does not claim the Phase 3 architecture checker exists.
- The gate executes the Arduino preprocessor proof between the Arduino and ESP-IDF `compiledb` runs, because the single database path is overwritten by each run (P8).
- Token coverage is asserted as equality with the record count rather than against the research totals, so the check stays valid on any machine.
- Requirement marking in `.planning/REQUIREMENTS.md` is deliberately left to the orchestrator, because this plan runs in a parallel worktree and shared planning artifacts are written centrally after the wave.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected a MADR heading level in the new ADR**
- **Found during:** Task 1 verification
- **Issue:** The first draft wrote `### Pros and Cons of the Options` instead of `## Pros and Cons of the Options`; `scripts/tests/test_adrs.py` reported `7 != 8 : 0007-symlink-shared-libraries.md is missing a MADR section`.
- **Fix:** Restored the required `##` level and re-ran the suite.
- **Files modified:** `docs/decisions/0007-symlink-shared-libraries.md`
- **Verification:** `python3 -m unittest scripts.tests.test_adrs -v` -> 18 tests, OK.
- **Committed in:** `f7de8c9` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** A heading typo inside the file being authored; no scope change and no file outside the task's declared file list.

## Issues Encountered

- `pio pkg show platformio/espressif32` printed the version metadata and then had its README fetch denied by the network sandbox. The version assertion is unaffected; the research file already records that this denial is not a registry failure.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. The five library accessors remain deliberate linkage fixtures whose version is declared once in `library.json` (D-12); no placeholder, empty-data path or unwired component was introduced by this plan.

## Threat Flags

None — no new network endpoint, auth path, file-access pattern or schema at a trust boundary was added. The threat-register mitigations T-02-12 (Confirmation cites only reproducible artifacts), T-02-13 (pins re-proven at the gate) and T-02-14 (`git ls-files -ci` over every declared generated pathspec) are implemented by this plan. The phase installed no package beyond the already-approved pinned platform and its dependencies (T-02-SC).

## Next Phase Readiness

- **Criteria status:** criterion 1 (three green environments), criterion 2 (16 MB flash plus octal PSRAM, proven from `sdkconfig.json` and both image headers) and criterion 4 (shared sources in both ESP compilation databases) are proven; criterion 3 is satisfied for **consumption only** — generation of `platformio.shared.ini` is Phase 5 (META-05, D-03).
- **ADR-0007 is permanent:** Phase 5 and later must cite `0007`, and the next record takes `0008`.
- **For Phase 3 (D-07):** deleting `homeworks/0_0-toolchain-smoke/` must also remove the two scoped CMake ignore patterns from plan 02-02; the ADR and its manifest contract survive that deletion.
- **For Phase 8 (TOOL-05):** the gate commands in this plan are the exact checks CI should re-run unchanged.
- The phase is ready for `/gsd-verify-work`.

---

*Phase: 02-toolchain-truth*
*Completed: 2026-10-23*

## Self-Check: PASSED

- `docs/decisions/0007-symlink-shared-libraries.md` and this SUMMARY exist on disk.
- Commit `f7de8c9` is an ancestor of HEAD; `commits: 1` measured as `git rev-list --count d0c0c76..f7de8c9`.
- Re-run at close-out: `test_adrs` 18 tests OK, index row and next-number line present, three builds green (0.33 s / 7.77 s / 24.58 s), CDB 4/64/1074 with all required sources and all-record token coverage, `CONFIG_SPIRAM=True`, both images `Flash size: 16MB` with the esptool banner, `sdkconfig.json` five-key assertion OK, 122 repository tests OK, policy and PR-template checks PASS, pre-commit all Passed, `git ls-files -ci` empty, `platformio.shared.ini` tracked, D-03 audit `mentions=6 write-like=[]`.
