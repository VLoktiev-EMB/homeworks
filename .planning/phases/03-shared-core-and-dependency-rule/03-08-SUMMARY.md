---
phase: 03-shared-core-and-dependency-rule
plan: 08
subsystem: enforcement
tags: [dependency-rule, architecture-checker, allowlist, pre-commit, header-contract, python-unittest]

# Dependency graph
requires:
  - phase: 03-shared-core-and-dependency-rule
    plan: 01
    provides: "lib/port contract headers, lib/common modules and the host-only tests/ project"
  - phase: 03-shared-core-and-dependency-rule
    plan: 03
    provides: "GPIO and logging contracts and the final status/log vocabulary the headers expose"
  - phase: 03-shared-core-and-dependency-rule
    plan: 04
    provides: "lib/host fake headers for all five contracts"
  - phase: 03-shared-core-and-dependency-rule
    plan: 05
    provides: "the cross-fake contract suite and the capturing log sink header"
  - phase: 03-shared-core-and-dependency-rule
    plan: 06
    provides: "Arduino and ESP-IDF adapter sources and headers"
  - phase: 03-shared-core-and-dependency-rule
    plan: 07
    provides: "the final 21-header tree and a manifest/source inventory the header suite pins"
provides:
  - "scripts/check_architecture.py: a deny-by-default textual dependency checker with exit codes 0/1/2"
  - "A classifier that treats every .. segment and every absolute include name as a path escape"
  - "Per-owner external-header allowlists and a blocking denylist for lib/common only"
  - "scripts/architecture/allowlist.json: an empty, schema-versioned allowlist with a non-empty-reason rule"
  - "A 37-case fixture matrix and a 21-header public contract suite"
  - "A local pre-commit hook that gates code, the checker and the allowlist"
affects: [03-09, 04, 05, 06, 08, 11]

# Actuals (#2632) — chars/4 over the realized plan diff (57983 chars), not a harness count.
actuals:
  tokens: 14496
  tasks: 3
  commits: 5
  plan_head_before: ddea02efdcd678ab17c3ef9bd7ecfb1603a25a3a
  plan_head_after: 63460cd93999d079a792e61abbaa88e728e081e7

tech-stack:
  added: []
  patterns:
    - "Policy as committed data plus a deterministic stdlib-only checker with 0/1/2 exit codes"
    - "A classifier that rejects any .. segment and any absolute form before the first segment is read"
    - "A comment stripper as an offset-preserving state machine, so line numbers survive and string literals are not misread"
    - "Deny-by-default allowlist keyed by (path, rule), with a non-empty reason and stale-entry failure"
    - "Static assertions over public headers as data: inventory constant, guard order, include set, banned type names"

key-files:
  created:
    - scripts/check_architecture.py
    - scripts/architecture/allowlist.json
    - scripts/tests/test_check_architecture.py
    - scripts/tests/test_architecture_headers.py
  modified:
    - .pre-commit-config.yaml
    - lib/port/include/port/log.h

key-decisions:
  - "The classifier rejects an include when any path segment is `..`, not only a leading one; `common/../arduino/...` is an escape, never a self-edge (review bypass fix)"
  - "Absolute include names are escapes: a leading `/`, a Windows drive letter and a UNC prefix are all rejected before the first segment is consulted"
  - "External headers are allowed per owner, tightly: port gets stddef/stdint, common adds stdbool, host adds string; stdlib.h and stdio.h are absent everywhere so allocation or formatted output cannot ride a broad set"
  - "The blocking denylist applies to lib/common/** only; the two adapters legitimately call framework clocks"
  - "Comments are stripped by a state machine over //, /* */, string and character literals, with removed characters replaced by spaces so line numbers still match"
  - "The allowlist matches on the pair (path, rule); one entry covers one rule for one path, an unmatched entry fails as stale (exit 1) and a schema failure (including an empty reason) is exit 2"
  - "A missing lib/ and a scan that finds zero source files are exit 2, so an empty tree can never report success"
  - "platformio.ini is parsed with ConfigParser(interpolation=None); a missing lib_deps key is inherited through extends only when the child does not set it, matching PlatformIO's wholesale list semantics"
  - "A test-only environment (a name matching tests/test_ or a leading native) is skipped because tests/** is out of scope (D-15)"

patterns-established:
  - "A checker reads the tree read-only and proves idempotence by comparing two runs plus git status"
  - "Every negative fixture mutates exactly one property of one shared fixture tree, whose clean baseline is asserted first"
  - "A header inventory is a deliberate constant: adding a public header requires updating the test in the same change"

requirements-completed: [ARCH-01, ARCH-02, ARCH-03, ARCH-05, ARCH-07]

coverage:
  - id: D1
    description: "The dependency rule is a failing textual check over lib/ and homeworks/, with any .. segment and any absolute include name classified as a path escape"
    requirement: ARCH-05
    verification:
      - kind: unit
        ref: "scripts/tests/test_check_architecture.py#IncludeRuleTests"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_check_architecture.py#CliContractTests.test_classify_treats_every_dotdot_segment_as_an_escape"
        status: pass
      - kind: integration
        ref: "python3 scripts/check_architecture.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "The allowlist is deny-by-default and schema-versioned; a stale entry fails with exit 1 and a malformed file, an unknown rule or an empty reason fails with exit 2"
    requirement: ARCH-05
    verification:
      - kind: unit
        ref: "scripts/tests/test_check_architecture.py#AllowlistTests"
        status: pass
    human_judgment: false
  - id: D3
    description: "platformio.ini enforces the port closure, at most one adapter per environment and no host in a non-native environment, including a multi-line lib_deps block"
    requirement: ARCH-05
    verification:
      - kind: unit
        ref: "scripts/tests/test_check_architecture.py#ConfigRuleTests"
        status: pass
    human_judgment: false
  - id: D4
    description: "The 21 public headers are ASCII, start with #pragma once, carry a complete extern \"C\" guard, include only their per-library allowance and name no framework type"
    requirement: ARCH-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_architecture_headers.py#HeaderInventoryTests"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_architecture_headers.py#HeaderShapeTests"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_architecture_headers.py#HeaderIncludeSetTests"
        status: pass
    human_judgment: false
  - id: D5
    description: "The checker runs as a local pre-commit hook whose files pattern also covers the checker and scripts/architecture/ "
    requirement: ARCH-05
    verification:
      - kind: integration
        ref: "pre-commit run check-architecture --all-files"
        status: pass
    human_judgment: false
  - id: D6
    description: "The checker never writes to the tree: two consecutive runs produce identical stdout, stderr and exit code, and git status is unchanged"
    verification:
      - kind: unit
        ref: "scripts/tests/test_check_architecture.py#RealTreeTests.test_second_run_is_identical_and_read_only"
        status: pass
    human_judgment: false
  - id: D7
    description: "The allowlist stays empty in this phase; whether a future entry's reason justifies an exception remains a review judgement"
    human_judgment: true
    rationale: "The schema can prove a reason is present; only a reviewer can judge whether the reason describes a real exception rather than a permanent bypass (D-15)."

duration: 3 min
completed: 2026-10-24
status: complete
---

# Phase 03 Plan 08: Dependency-Rule Enforcement Summary

**A stdlib-only checker now rejects every forbidden `#include` — including embedded `..` path arithmetic and absolute names — plus every `lib_deps` closure violation, and runs from a local pre-commit hook; a 21-header contract suite pins the public surface.**

## Performance

- **Duration:** 3 min (22:39:18Z to 22:42:46Z)
- **Started:** 2026-10-23T22:39:18Z
- **Completed:** 2026-10-23T22:42:46Z
- **Tasks:** 3
- **Files modified:** 6 paths (1462 insertions, 2 deletions; 57983 diff characters)

## Accomplishments

- `scripts/check_architecture.py` scans `lib/**` and `homeworks/**` for `#include` directives and fails on a path escape, a forbidden project edge, an external header outside the owner's tight set, a blocking token in `lib/common`, or a cross-homework include.
- The classifier cannot be walked around with path arithmetic: any `..` segment anywhere is an escape, and `/`, `C:/` and `\\server\...` forms are escapes too. `common/../arduino/include/arduino/time.h` is rejected as `escape`, not accepted as a `common` self-edge.
- `scripts/architecture/allowlist.json` is `{"version": 1, "entries": []}`; the loader caps the file at 64 KiB, validates every entry, requires a non-empty reason, and fails as stale when an entry matches nothing.
- `platformio.ini` is parsed with `interpolation=None` and checked for the `port` closure, one adapter per environment, and no `host` in a non-native environment; a multi-line `lib_deps` block is handled as one value.
- `scripts/tests/test_check_architecture.py` proves 37 cases, including the two escape fixtures the review demanded, the tight external set, a `//` inside a string literal, a commented-out include and an empty allowlist reason.
- `scripts/tests/test_architecture_headers.py` pins the 21-header inventory and checks ASCII, `#pragma once`, the `extern "C"` guard order, the per-library include set and banned framework type names.
- `.pre-commit-config.yaml` gains the `check-architecture` local hook, whose `files` pattern covers `lib/`, `homeworks/`, `scripts/architecture/` and the checker itself.

## The Rule Tables as Implemented

### Project edges (`EDGES`)

| Owner | Allowed project edges |
|-------|------------------------|
| `port` | none (self-include allowed) |
| `common` | `port` |
| `arduino` | `port` |
| `espidf` | `port` |
| `host` | `port` |
| `homeworks/<id>` | `port`, `common`, `arduino`, `espidf`, `host`, with at most one adapter enforced from `platformio.ini` |

A library always may include its own headers; `target == owner` is allowed before the matrix is consulted.

### External headers (`EXTERNAL_OK`)

| Owner | Allowed external headers |
|-------|--------------------------|
| `port` | `stddef.h`, `stdint.h` |
| `common` | `stdbool.h`, `stddef.h`, `stdint.h` |
| `host` | `stdbool.h`, `stddef.h`, `stdint.h`, `string.h` |
| `arduino` | any external header (`None`); project edges still checked |
| `espidf` | any external header (`None`); project edges still checked |

`stdio.h`, `stdlib.h` and `limits.h` are accepted nowhere, so a future allocation or formatted write cannot pass by riding a broad C-standard set.

### Blocking tokens (`lib/common/**` only)

```python
("delay(", "delayMicroseconds(", "vTaskDelay", "sleep(", "usleep(",
 "HAL_Delay(", "millis(", "esp_timer_get_time(", "xTaskGetTickCount(")
```

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | clean tree, no stale allowlist entry |
| `1` | violation or stale allowlist entry |
| `2` | usage/environment error: missing `lib/`, zero scanned files, unreadable or malformed allowlist |

## Exact PASS Output on the Real Tree

```text
PASS includes: 36 source files and 70 includes match the dependency matrix
PASS blocking: no blocking token in lib/common
PASS config: 0 homework environments satisfy the closure rules
PASS allowlist: 0 entries, none stale

PASS: dependency rule satisfied
```

`homeworks/` does not exist yet, so the config group reports zero environments; absence is not an error, and the rule is exercised entirely by the fixture trees.

## The Two Escape Fixtures

| Include written in a `common` source | Result |
|--------------------------------------|--------|
| `#include "../common/crc.h"` | exit 1, `escape` |
| `#include "common/../arduino/include/arduino/time.h"` | exit 1, `escape` — and specifically **not** `forbidden project edge` |
| `#include "/tmp/anything.h"` | exit 1, `escape` |
| `#include "C:/tools/anything.h"` | exit 1, `escape` |

The embedded-`..` test asserts the absence of an edge message, so a future classifier that regresses to first-segment matching fails loudly.

## Fixture Cases and Exit Codes

| Group | Case | Exit |
|-------|------|------|
| Baseline | minimal fixture tree | 0 |
| Baseline | module including its own header | 0 |
| Includes | framework include in `common` | 1 (`external`) |
| Includes | adapter include in `common` | 1 (`edge common -> arduino`) |
| Includes | `port` including `common` | 1 (`edge port -> common`) |
| Includes | adapter including `common` | 1 (`edge arduino -> common`) |
| Includes | `host` including a framework header | 1 (`external`) |
| Includes | leading `../` escape | 1 (`escape`) |
| Includes | embedded `..` escape | 1 (`escape`, no edge) |
| Includes | absolute `/tmp` include | 1 (`escape`) |
| Includes | Windows absolute include | 1 (`escape`) |
| Includes | `<stdlib.h>` in `common` | 1 (`external`) |
| Includes | cross-homework include | 1 (`cross-homework`) |
| Blocking | `millis(` in `lib/common` | 1 (`blocking`) |
| Blocking | blocking token inside a comment | 0 |
| Blocking | commented-out include | 0 |
| Blocking | `//` inside a string, then a real `millis(` | 1 (`blocking`; the stripper does not hide it) |
| Allowlist | covered violation | 0 |
| Allowlist | stale entry | 1 (`allowlist`) |
| Allowlist | empty reason | 2 |
| Allowlist | unknown rule | 2 |
| Allowlist | malformed JSON | 2 |
| Allowlist | missing `lib/` | 2 |
| Config | `arduino` + `espidf` in one environment | 1 |
| Config | `host` with `platform = espressif32` | 1 |
| Config | `common` without `port` | 1 |
| Config | multi-line `lib_deps` with one adapter + `port` + `common` | 0 |
| Config | native environment listing `host` | 0 |
| CLI | `--help` | 0 |
| CLI | unknown argument | 2 |

The module also unit-tests `strip_comments` directly, the classifier's escape set, the docstring's `(path, rule)` contract and `interpolation=None` in the parser.

## Header Inventory (21 files)

| Library | Headers |
|---------|---------|
| `port` | `status.h`, `time.h`, `gpio.h`, `i2c.h`, `spi.h`, `log.h` |
| `common` | `timing.h`, `ring_buffer.h`, `crc.h`, `hex.h` |
| `host` | `fake_time.h`, `fake_gpio.h`, `fake_i2c.h`, `fake_spi.h`, `fake_log.h` |
| `arduino` | `time.h`, `gpio.h`, `log.h` |
| `espidf` | `time.h`, `gpio.h`, `log.h` |

Allowed public includes per library: `port` -> `port/` + `stddef.h`/`stdint.h`; `common` -> `common/`, `port/` + `stdbool.h`/`stddef.h`/`stdint.h`; `host` -> `host/`, `port/` + those three plus `string.h`; `arduino` -> `arduino/`, `port/`; `espidf` -> `espidf/`, `port/`.

## Hook Output

```text
shared-library dependency rule...........................................Passed
```

`pre-commit run check-architecture --all-files` exits 0, and a commit that stages only `lib/` files runs the hook for real rather than skipping it.

## Task Commits

Each task was committed atomically:

1. **Task 1: dependency checker with the hardened classifier and an empty allowlist** — `04943ee` (feat)
2. **Task 2: dependency-rule fixture matrix** — `53fbb44` (test)
3. **Task 3a: register the local hook** — `1a86c75` (chore)
4. **Task 3b: keep the port log header ASCII-only** — `e0f9e1a` (fix, deviation Rule 1)
5. **Task 3c: 21-header public contract suite** — `63460cd` (test)

**Plan metadata:** committed separately after this SUMMARY.

## Files Created/Modified

- `scripts/check_architecture.py` — the checker: `CheckError`, `resolve_root`, `INCLUDE`, `PROJECT_NAMES`, `EDGES`, `EXTERNAL_OK`, `BLOCKING`, `RULES`, `SCAN_ROOTS`, `SOURCE_SUFFIXES`, `owner_of`, `classify`, `strip_comments`, `_read_sources`, `scan_includes`, `scan_blocking`, `_option`, `_extends_targets`, `_dep_names`, `check_platformio`, `load_allowlist`, `apply_allowlist`, `run_check`, `main`
- `scripts/architecture/allowlist.json` — `{"version": 1, "entries": []}`
- `scripts/tests/test_check_architecture.py` — real-tree, baseline, include, blocking, allowlist, config and CLI classes (37 tests)
- `scripts/tests/test_architecture_headers.py` — inventory, shape and include-set classes (7 tests)
- `.pre-commit-config.yaml` — the `check-architecture` local hook
- `lib/port/include/port/log.h` — two em dashes replaced with ASCII hyphens

## Decisions Made

- **The classifier rejects before it classifies.** Absolute forms and any `..` segment are decided before the first segment is read, so `common/../arduino/...` can never be mistaken for a self-edge.
- **One checker owns both the source and the configuration rules.** The include scan and the `platformio.ini` closure share `owner_of`, the classifier and the allowlist, so a future rule change has one place to land.
- **The allowlist key is `(path, rule)`, not `path`.** An entry waives one rule for one file; a second rule on the same file needs its own reason.
- **Test-only environments are skipped by name.** A `tests`/`native`-style environment is out of D-15's scope, so the config rules never read it; the fixture suite exercises the rules on firmware-shaped environments instead.
- **The header inventory is a constant.** The suite cannot distinguish "new header" from "forgot the constant", so it deliberately forces both edits into one change.

## Deviations from Plan

### Execution-order deviation

**1. The configuration rules landed in Task 1 rather than Task 2**

- **Found during:** Task 1 implementation
- **Issue:** The checker was written as one coherent module, so `check_platformio` and its helpers were present in the Task 1 commit; Task 2's step 1 therefore had nothing to add.
- **Fix:** Task 2 delivered the whole fixture matrix, including every configuration case; no code was reverted.
- **Impact:** None on the artifacts. Each commit is green on the tree it describes; the only difference is which commit first contains the config code. It is untested until `53fbb44`, which is the commit the plan assigns the tests to.

### Auto-fixed Issues

**1. [Rule 1 - Bug] `lib/port/include/port/log.h` contained non-ASCII bytes**

- **Found during:** Task 3 (`test_each_header_is_ascii_and_starts_with_pragma_once`)
- **Issue:** Two em dashes (U+2014) in the contract comment made the header non-ASCII, violating the plan's explicit ASCII-only truth for every public header.
- **Fix:** Replaced both with ASCII hyphens; no code or behaviour changed.
- **Files modified:** `lib/port/include/port/log.h`
- **Verification:** `python3 -m unittest scripts.tests.test_architecture_headers -v` — 7 tests OK; the header suite now reports all 21 files ASCII-clean.
- **Committed in:** `e0f9e1a` (its own `fix(03-08)` commit, so the header edit is not buried in a test commit)

**2. [Rule 1 - Bug] The extern-guard assertion looked for the wrong `#endif`**

- **Found during:** Task 3, first run of the header suite
- **Issue:** The first `#endif` after `extern "C" {` closes the *opening* `#ifdef` block, not the scope, so a correct header failed as "not closed before #endif".
- **Fix:** Locate the second `#ifdef __cplusplus`, then require `}` before its `#endif`.
- **Files modified:** `scripts/tests/test_architecture_headers.py`
- **Verification:** All 21 headers pass the guard-order assertion.
- **Committed in:** `63460cd` (part of the Task 3 test commit)

---

**Total deviations:** 2 auto-fixed (2 Rule 1), 1 execution-order deviation.
**Impact on plan:** Both fixes were required for the plan's own acceptance criteria; neither changes scope. The header edit is the only production-code change outside the plan's file list, and it is a comment-only ASCII correction.

## Issues Encountered

- `gsd_run` is not installed in this execution environment, so the requirements-tracking step (`requirements.ready-ids` / `requirements.mark-complete`) could not run. `REQUIREMENTS.md` is untouched; marking belongs to the orchestrator after the wave, and the shared-ID gate would block most IDs until plan 03-09 has a SUMMARY anyway.
- The repository's condensing shell wrapper refused a few compound `cd ... && git ...` forms and one `git status --short` invocation; the same commands ran as plain `/usr/bin/git` calls inside the worktree. No repository content was affected.
- `pre-commit` refuses to commit while `.pre-commit-config.yaml` itself is unstaged, so the hook registration was committed before the two Task 3 content commits. Each commit is independently green.

## Known Stubs

None. The checker parses `platformio.ini` from data; it does not pretend to enforce anything it cannot see. The textual scan's blind spots (a macro that expands to `#include`, a generated header) are documented in the module docstring rather than left implicit, and the native compile gate owns transitive purity.

## Threat Flags

None. The change implements the mitigations already registered in the plan's threat model (T-03-41 through T-03-44): `followlinks=False` with resolved containment, exit 2 on an empty or missing tree, a capped and schema-checked allowlist, and a fixed hook entry with `pass_filenames: false`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The dependency rule is enforceable today: `python3 scripts/check_architecture.py` exits 0 on the real tree, and the local hook blocks a forbidden include at commit time.
- Plan 03-09 can rely on the checker as an existing gate; it owns ARCH-06's determinism and purity proofs and does not need to touch this plan's files.
- The `homeworks/` configuration rules are proven only by fixtures; the first real homework (Phase 11) will exercise them on a live `platformio.ini`.
- Open, deliberate limits: the scan is textual (macro-generated includes are invisible, recorded in the docstring), and the legitimacy of a future allowlist reason stays a review judgement.

---
*Phase: 03-shared-core-and-dependency-rule*
*Completed: 2026-10-24*

## Self-Check: PASSED

- `scripts/check_architecture.py`, `scripts/architecture/allowlist.json`, `scripts/tests/test_check_architecture.py`, `scripts/tests/test_architecture_headers.py`, `.pre-commit-config.yaml` and `lib/port/include/port/log.h` exist on disk.
- Commits `04943ee`, `53fbb44`, `1a86c75`, `e0f9e1a` and `63460cd` are ancestors of HEAD.
- `python3 scripts/check_architecture.py`: exit 0, final PASS sentence.
- `python3 -m unittest scripts.tests.test_check_architecture scripts.tests.test_architecture_headers -v`: 44 tests OK.
- `pre-commit run check-architecture --all-files`: Passed.
- `python3 -m unittest discover -s scripts/tests -v`: 174 tests OK.
- Self-check verdict: PASSED.
