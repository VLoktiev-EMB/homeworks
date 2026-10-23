# Phase 3: Shared Core and Dependency Rule - Pattern Map

**Mapped:** 2026-10-24
**Files analyzed:** 40 (28 new, 12 modified, 3 deletions/relocations)
**Analogs found:** 36 / 40

Every analog path below is git-tracked source (verified with `git ls-files -- <path>`).
No `.gsd/capabilities/**` or other gitignored mirror tree is cited.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `lib/port/include/port/status.h` | contract header | request-response | `lib/port/include/port.h` | exact (shape) |
| `lib/port/include/port/time.h` | contract header | request-response | `lib/port/include/port.h` + RESEARCH Pattern 1 | role-match |
| `lib/port/include/port/gpio.h` | contract header | request-response | `lib/port/include/port.h` | role-match |
| `lib/port/include/port/i2c.h` | contract header | file-I/O (bus) | `lib/port/include/port.h` | role-match |
| `lib/port/include/port/spi.h` | contract header | file-I/O (bus) | `lib/port/include/port.h` | role-match |
| `lib/port/include/port/log.h` | contract header | streaming | `lib/port/include/port.h` | role-match |
| `lib/port/library.json` (modify) | config | — | `lib/common/library.json` | exact |
| `lib/port/include/port.h`, `lib/port/src/port.c` (delete) | — | — | — | n/a |
| `lib/common/include/common/{ring_buffer,timing,crc,hex}.h` | library header | transform | `lib/common/include/common.h` | role-match |
| `lib/common/src/{ring_buffer,timing,crc,hex}.c` | library source | transform | `lib/common/src/common.c` | role-match |
| `lib/common/include/common.h`, `src/common.c` (delete) | — | — | — | n/a |
| `lib/common/library.json` (modify) | config | — | `lib/common/library.json` | exact (self) |
| `lib/host/include/host/fake_*.h` (5) | test-double header | request-response | `lib/host/include/host.h` | role-match |
| `lib/host/src/fake_*.c` (5) | test-double source | request-response | `lib/host/src/host.c` | role-match |
| `lib/host/library.json` (modify) | config | — | `lib/common/library.json` | exact |
| `lib/arduino/include/arduino/{time,gpio,log}.h` | adapter header | request-response | `lib/arduino/include/arduino_adapter.h` | exact (shape) |
| `lib/arduino/src/{time,gpio,log}.c` | adapter source | request-response | `lib/arduino/src/arduino_adapter.c` | exact |
| `lib/arduino/library.json` (modify) | config | — | `lib/common/library.json` | exact |
| `lib/espidf/include/espidf/{time,gpio,log}.h` | adapter header | request-response | `lib/espidf/include/espidf_adapter.h` | exact (shape) |
| `lib/espidf/src/{time,gpio,log}.c` | adapter source | request-response | `lib/espidf/src/espidf_adapter.c` | exact |
| `lib/espidf/library.json` (modify) | config | — | `lib/common/library.json` | exact |
| `tests/platformio.ini` | config | — | `homeworks/0_0-toolchain-smoke/platformio.ini` | exact |
| `tests/test/test_common_*/test_*.c` (4) | C unit test | transform | RESEARCH Unity skeleton | no analog (new) |
| `tests/test/test_port_contracts/test_contracts.c` | C unit test | request-response | RESEARCH Pattern 1 | no analog (new) |
| `tests/test/test_host_fakes/test_host_fakes.c` | C unit test | request-response | RESEARCH Unity skeleton | no analog (new) |
| `scripts/check_architecture.py` | checker | batch (file scan) | `scripts/check_pr_templates.py` | exact |
| `scripts/architecture/allowlist.json` | config data | — | `policy/*.json` (read by checker) | role-match |
| `scripts/tests/test_check_architecture.py` | Python test | batch | `scripts/tests/test_check_pr_templates.py` | exact |
| `scripts/tests/test_architecture_headers.py` | Python test | batch | `scripts/tests/test_pio_scripts.py` | role-match |
| `scripts/tests/test_native_determinism.py` | Python test | batch (subprocess) | `scripts/tests/test_pio_scripts.py` | partial |
| `scripts/tests/test_native_purity.py` | Python test | batch (subprocess) | `scripts/tests/test_pio_scripts.py` | partial |
| `.pre-commit-config.yaml` (modify) | config | — | `.pre-commit-config.yaml:36-48` | exact (self) |
| `partitions/default_16MB.csv` (move) | data | — | moved from smoke project | exact |
| `platformio.shared.ini` (modify) | config | — | `platformio.shared.ini:10,24` | exact (self) |
| `docs/decisions/0008-*.md` | ADR | — | `docs/decisions/0007-symlink-shared-libraries.md` | exact |
| `docs/decisions/README.md` (modify) | doc index | — | same file, table rows 24-32 | exact (self) |
| `scripts/tests/test_pio_scripts.py` (modify) | Python test | batch | `scripts/tests/test_gitignore.py` | role-match |
| `scripts/tests/test_gitignore.py` (modify) | Python test | batch | same file, `VISIBLE`/`IGNORED` tables | exact (self) |
| `homeworks/0_0-toolchain-smoke/` (delete) | — | — | — | n/a |
| `AGENTS.md` (modify, step 3 command) | doc | — | `AGENTS.md` quick-start table | exact (self) |

---

## Pattern Assignments

### `lib/port/include/port/*.h` (contract headers, header-only)

**Analog:** `lib/port/include/port.h` (Phase 2 stub) — the exact guard shape every new header must keep.

**Header shell pattern** (`lib/port/include/port.h:1-11`):

```c
#pragma once

#ifdef __cplusplus
extern "C" {
#endif

const char *port_version(void);

#ifdef __cplusplus
}
#endif
```

Keep `#pragma once` first, `extern "C"` immediately after, declarations in between, and the closing brace as the last three lines. This is the shape `test_architecture_headers.py` asserts and the Phase 2 D-15 rule requires.

**Core contract pattern** (RESEARCH.md lines 369-389, verified to compile under `-std=c11 -pedantic` and `-std=c++17 -pedantic`):

```c
/* lib/port/include/port/time.h */
#pragma once
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

typedef struct port_time {
    uint32_t (*now_ms)(void *ctx);
    void *ctx;
} port_time_t;

static inline uint32_t port_time_now_ms(const port_time_t *time) {
    return time->now_ms(time->ctx);
}

#ifdef __cplusplus
}
#endif
```

**Status vocabulary** (`status.h`, RESEARCH lines 404-411) — every failing operation returns it; time reads and logging do not:

```c
typedef enum port_status_t {
    PORT_OK = 0,
    PORT_ERR_TIMEOUT,
    PORT_ERR_IO,
    PORT_ERR_INVALID_ARG,
    PORT_ERR_NOT_SUPPORTED
} port_status_t;
```

**Import rule:** `port` includes only C standard headers. No `common/`, no adapter header, no framework header. The `#include <stdint.h>` line above is the maximum allowed.

**Do not copy** `lib/port/src/port.c` — it is deleted (D-04/D-05: the version string moves out and the library becomes header-only).

---

### `lib/common/{include/common,src}/*.{h,c}` (library, transform)

**Analog headers:** `lib/common/include/common.h` — same shell as above.
**Analog source:** `lib/common/src/common.c:1-3`:

```c
#include "common.h"

const char *common_version(void) { return "0.1.0"; }
```

This shows the two house conventions to carry forward: (1) the module's own header is included **quoted**, after any system headers; (2) no trailing whitespace, two-space C indentation as in the adapter sources. Delete the `*_version` function — the version lives only in `library.json` (D-04/WR-03).

**Time-injection pattern** (RESEARCH Pattern 3, lines 420-433). `common` never calls a clock; it accepts one:

```c
/* lib/common/include/common/timing.h */
#include <stdbool.h>
#include <stdint.h>

#include "port/time.h"

typedef struct common_debounce {
    bool stable;
    uint32_t last_change_ms;
} common_debounce_t;

uint32_t common_elapsed_ms(uint32_t now_ms, uint32_t since_ms);
bool common_timer_expired(uint32_t now_ms, uint32_t deadline_ms);
bool common_debounce_update(common_debounce_t *state, const port_time_t *time,
                            bool raw_input, uint32_t stable_ms);
```

Wraparound uses unsigned subtraction; never `>` on absolute timestamps.

**Forbidden tokens** in `lib/common/**` (mechanical denylist, RESEARCH line 825-826): `millis(`, `esp_timer_get_time(`, `delay(`, `delayMicroseconds(`, `vTaskDelay`, `sleep(`, `usleep(`, `HAL_Delay(`, `xTaskGetTickCount(`.

**Delete** `lib/common/include/common.h` and `lib/common/src/common.c`; the four module pairs replace them.

---

### `lib/host/{include/host,src}/fake_*.{h,c}` (test doubles)

**Analog:** `lib/host/include/host.h` (header shell) and `lib/host/src/host.c` (source shell) — the same layout as `common`, with the additional constraint that `host` may include **only** `port` and C standard headers.

**Fake factory shape** — follows the adapter factory convention so a signature drift is a compile error (RESEARCH ARCH-03, Pitfall C12):

```c
/* lib/host/include/host/fake_time.h */
#pragma once
#include <stdint.h>
#include "port/time.h"
#ifdef __cplusplus
extern "C" {
#endif

typedef struct host_fake_time {
    uint32_t now_ms;
} host_fake_time_t;

void host_fake_time_reset(host_fake_time_t *fake);
void host_fake_time_advance(host_fake_time_t *fake, uint32_t delta_ms);
port_time_t host_fake_time_port(host_fake_time_t *fake);

#ifdef __cplusplus
}
#endif
```

Each fake returns the **same vtable type** the real adapter returns (`port_time_t`, `port_gpio_t`, `port_i2c_t`, `port_spi_t`, `port_log_t`). Fakes are bounded and allocation-free: 64-pin GPIO array and 32 captured log lines (assumption A2).

---

### `lib/arduino/src/*.c` and `lib/espidf/src/*.c` (framework adapters)

**Analog source:** `lib/arduino/src/arduino_adapter.c:1-7`:

```c
#include <Arduino.h>

#include "arduino_adapter.h"

const char *arduino_adapter_version(void) {
  (void)millis();
  return "0.1.0";
}
```

Carry forward exactly: framework header first in angle brackets, blank line, then the project header in quotes; two-space indent. The `(void)ctx;` suppression pattern is the same idiom.

**Analog (ESP-IDF):** `lib/espidf/src/espidf_adapter.c:1-7` — `#include <esp_err.h>` then `"espidf_adapter.h"`.

**Adapter factory pattern** (RESEARCH lines 774-804) — pure C, positional aggregate initialization, **never** a designated initializer in C++ callers (Pitfall 4):

```c
/* lib/arduino/src/time.c */
#include <Arduino.h>
#include "arduino/time.h"

static uint32_t arduino_now_ms(void *ctx) {
    (void)ctx;
    return (uint32_t)millis();
}

port_time_t arduino_time_port(void) {
    port_time_t port = { arduino_now_ms, NULL };
    return port;
}
```

ESP-IDF equivalent uses `esp_timer_get_time() / 1000`; GPIO uses `gpio_config`/`gpio_set_level`/`gpio_get_level`; logging uses `ESP_LOGI` or `log_printf("%s\n", msg)` unconditionally (Pitfall 5 — `log_i`/`log_d` compile to nothing at the default `CORE_DEBUG_LEVEL`).

**Header rule (D-10):** the adapter header declares only `port_*` types and the factory name. No `Arduino.h`, no `esp_*.h` in `include/`.

---

### `lib/*/library.json` (five manifest modifications)

**Analog:** `lib/common/library.json:1-8` (byte-identical across all five today):

```json
{
  "name": "common",
  "version": "0.1.0",
  "build": {
    "srcDir": "src",
    "includeDir": "include"
  }
}
```

Changes: `"version": "0.2.0"` in all five (D-04); drop `"srcDir": "src"` **for `port` only**, because it becomes header-only and has no `src/` (RESEARCH Open Question 3). Keep `srcDir` for the other four. Never add a `dependencies` key (D-03).

---

### `tests/platformio.ini` (PlatformIO project config)

**Analog:** `homeworks/0_0-toolchain-smoke/platformio.ini:1-10` — the working composition of `extra_configs`, `extends`, and `symlink://` lib_deps that this file replaces:

```ini
[platformio]
default_envs = native
extra_configs = ../../platformio.shared.ini

[env:native]
extends = native_unity
lib_deps =
    common=symlink://../../lib/common
    port=symlink://../../lib/port
    host=symlink://../../lib/host
```

**Differences forced by depth and D-13/D-14** (RESEARCH §Code Examples, verified end to end):

```ini
[platformio]
default_envs = native
extra_configs = ../platformio.shared.ini

[env:native]
extends = native_unity
test_framework = unity
build_flags =
    -std=c11
    -Wall
    -Wextra
    -Werror
extra_scripts = pre:../scripts/pio/compiledb.py
lib_deps =
    common=symlink://../lib/common
    port=symlink://../lib/port
    host=symlink://../lib/host
    throwtheswitch/Unity@2.6.1
test_dir = test
```

`extra_scripts` must be overridden: the inherited value `pre:../../scripts/pio/compiledb.py` resolves relative to the **project** directory and would point outside the repository (Pitfall 1). `build_flags` must be repeated, because `extends` does not merge lists (Pitfall 3). Unity must be pinned explicitly (Pitfall 9). Do not add a root `platformio.ini` (Pitfall 10).

---

### `tests/test/test_*/test_*.c` (Unity suites)

**Analog:** none in the repository — this is the first Unity suite. Use RESEARCH lines 736-769 verbatim as the skeleton:

```c
#include <unity.h>

#include "common/timing.h"
#include "host/fake_time.h"

static host_fake_time_t fake;

void setUp(void) { host_fake_time_reset(&fake); }
void tearDown(void) {}

static void test_elapsed_handles_wraparound(void) {
    TEST_ASSERT_EQUAL_UINT32(32u, common_elapsed_ms(0x00000010u, 0xFFFFFFF0u));
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_elapsed_handles_wraparound);
    return UNITY_END();
}
```

Non-negotiable: every file defines `setUp` **and** `tearDown`, even empty (Pitfall 12); `main` returns `UNITY_END()`; `static` test functions; one `test/test_<area>/` directory per module.

---

### `scripts/check_architecture.py` (checker, file-scan)

**Analog:** `scripts/check_pr_templates.py` — the closest sibling in the checker family (deterministic, `--dir` seam, three exit codes, read-only). Mirror its structure section by section.

**Module docstring / contract block** (`check_pr_templates.py:1-22`) — restate usage, the `0/1/2` exit-code contract, and why the check is textual rather than compiler-based (RESEARCH Pattern 4):

```python
#!/usr/bin/env python3
"""Verify the shared-library dependency rule.

Usage:
  python3 scripts/check_architecture.py [--dir PATH]

Exit codes (a CI contract from Phase 8 onward):
  0  every scanned include and every lib_deps entry is allowed
  1  violation (forbidden edge, path escape, blocking token, stale allowlist entry)
  2  usage or environment error (bad arguments, missing lib/, malformed allowlist)
"""
```

**Imports** (`check_pr_templates.py:24-31`):

```python
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
```

Add `configparser` (for the `lib_deps` rule) and `os` only if `os.walk(followlinks=False)` is used.

**Environment-error class** (`check_pr_templates.py:55-56`) — the family convention for exit code 2:

```python
class CheckError(Exception):
    """A usage or environment problem, reported with exit code 2."""
```

**Root resolution** (`check_pr_templates.py:59-76`) — copy `resolve_root` verbatim; it is the `--dir` test seam every fixture test depends on:

```python
def resolve_root(explicit):
    """Return the repository root, explicit or resolved through git."""
    if explicit:
        return Path(explicit).resolve()
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=False,
        )
    except OSError as exc:
        raise CheckError(f"cannot execute git: {exc}") from exc
    root = proc.stdout.strip()
    if proc.returncode != 0 or not root:
        detail = proc.stderr.strip() or "git rev-parse failed"
        raise CheckError(f"cannot locate the repository root: {detail}")
    return Path(root).resolve()
```

**Pass/fail reporting** (`check_pr_templates.py:120-142, 219-237`) — one `PASS <area>: <sentence>` or `FAIL <area>: <sentence>` line per rule group, indented details beneath, `failures` counted as an integer and returned:

```python
def run_check(root):
    """Print the report and return the number of failed checks."""
    ...
    if problems:
        print("FAIL includes: forbidden dependency edge")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print(f"PASS includes: {count} files match the dependency matrix")
    return 0
```

**Main / exit-code mapping** (`check_pr_templates.py:240-268`) — copy verbatim, swapping the description and the closing sentence:

```python
def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify the shared-library dependency rule.")
    parser.add_argument("--dir", metavar="PATH", help="repository root to check")
    args = parser.parse_args(argv)
    try:
        root = resolve_root(args.dir)
        failures = run_check(root)
    except CheckError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if failures:
        print()
        print("FAIL: dependency rule violated")
        return 1
    print()
    print("PASS: dependency rule satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Core scan** (RESEARCH lines 810-844) — the classifier, matrix, and denylist as **module-level data**, not inline `if` chains:

```python
INCLUDE = re.compile(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]')
EDGES = {
    "port": frozenset(),
    "common": frozenset({"port"}),
    "arduino": frozenset({"port"}),
    "espidf": frozenset({"port"}),
    "host": frozenset({"port"}),
}
BLOCKING = ("delay(", "delayMicroseconds(", "vTaskDelay", "sleep(", "usleep(",
            "HAL_Delay(", "millis(", "esp_timer_get_time(", "xTaskGetTickCount(")

def owner_of(relative_path: Path) -> str:
    parts = relative_path.parts
    if parts[0] == "lib":
        return parts[1]
    return "homeworks/" + parts[1]

def classify(name: str) -> tuple[str, str]:
    if name.startswith(("./", "../")):
        return "escape", name
    first = name.split("/", 1)[0]
    if first in EDGES:
        return "project", first
    return "external", name
```

**Safety rules** (RESEARCH §Security Domain): strip comments before matching; `os.walk(..., followlinks=False)`; resolve `--dir` and check containment; byte-cap the allowlist; `json.loads` + schema validation; exit 2 when `lib/` is missing (never exit 0 on an empty tree); `configparser.ConfigParser(interpolation=None)` when parsing `platformio.ini`; `subprocess.run([...])` list arguments only.

---

### `scripts/architecture/allowlist.json` (config data)

**Analog:** `policy/ruleset-main.json` / `policy/repository.json` — committed JSON parsed by a checker with a strict schema and exit 2 on malformed input (see `check_policy._load_json`, `scripts/check_policy.py:67-73`).

Shape (RESEARCH §Recommended Project Structure line 347):

```json
{"version": 1, "entries": []}
```

Empty by default (A7). Each future entry carries a `path`, a `rule`, and a `reason`; an entry that matches no violation is a stale-allowlist failure (exit 1).

---

### `scripts/tests/test_check_architecture.py` (Python test, fixture trees)

**Analog:** `scripts/tests/test_check_pr_templates.py` — the closest match: a real-tree class plus one negative fixture class that copies a tree and mutates one property.

**Runner seam** (`test_check_pr_templates.py:32-44`):

```python
def run_checker(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(cwd), capture_output=True, text=True, timeout=60, check=False,
    )

def combined(result: subprocess.CompletedProcess) -> str:
    return result.stdout + result.stderr
```

**Real-tree class** (`test_check_pr_templates.py:58-64`):

```python
class RealTreeTests(unittest.TestCase):
    def test_real_tree_passes(self):
        result = run_checker()
        self.assertEqual(0, result.returncode, combined(result))
        self.assertIn("PASS: dependency rule satisfied", result.stdout)
```

**Read-only idempotence** (`test_check_pr_templates.py:104-116`) — copy verbatim; it is the guarantee that the checker never mutates the tree:

```python
def test_second_run_is_identical_and_read_only(self):
    before = git_status()
    first = run_checker()
    second = run_checker()
    after = git_status()
    self.assertEqual(0, first.returncode, combined(first))
    self.assertEqual(0, second.returncode, combined(second))
    self.assertEqual(
        (first.returncode, first.stdout, first.stderr),
        (second.returncode, second.stdout, second.stderr),
    )
    self.assertEqual(before, after, "the checker modified the working tree")
```

**Negative fixture pattern** (`test_check_pr_templates.py:122-141`):

```python
def make_tree(self) -> Path:
    tmp = tempfile.TemporaryDirectory()
    self.addCleanup(tmp.cleanup)
    root = Path(tmp.name)
    # build the minimal lib/ tree under root
    return root

def test_framework_include_in_common_exits_1(self):
    root = self.make_tree()
    (root / "lib" / "common" / "src" / "x.c").write_text(
        '#include <Arduino.h>\n', encoding="utf-8"
    )
    result = run_checker("--dir", str(root))
    self.assertEqual(1, result.returncode, combined(result))
    self.assertIn("FAIL includes", result.stdout)
    self.assertIn("x.c", result.stdout)
```

Required fixture cases (RESEARCH §Wave 0 Gaps): framework include in `common`; adapter include in `common`; `port → common`; adapter → `common`; `host` → framework; path escape `../`; blocking token in `common`; allowlisted violation passes; stale allowlist entry fails; malformed allowlist exits 2; multi-adapter homework env fails; `host` in a target env fails. Missing `lib/` exits 2.

---

### `scripts/tests/test_architecture_headers.py` (Python test, static scan)

**Analog:** `scripts/tests/test_pio_scripts.py` — the established "assert source files as data" style for artefacts that cannot be imported or executed.

**Root + config helpers** (`test_pio_scripts.py:24-35, 100-103`):

```python
def _repo_root() -> Path:
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(completed.stdout.strip())

REPO_ROOT = _repo_root()
```

**Constants-as-contract** (`test_pio_scripts.py:41-57`):

```python
LIB_NAMES = ("common", "port", "arduino", "espidf", "host")
HOOK_PATH = "pre:../../scripts/pio/compiledb.py"
FORBIDDEN_SCRIPT_TOKENS = ("COMPILATIONDB_INCLUDE_TOOLCHAIN",)
```

Apply the same shape: list the five contract headers, assert `#pragma once` on line 1, assert `extern "C" {` … `}` bracket the declarations, assert no `#include` outside the C standard set for `port`/`common`/`host`, and assert each header is the sole file in its module contract (no whole-driver names such as `port_get_handle`).

---

### `scripts/tests/test_native_determinism.py` (Python test, subprocess)

**Analog:** `scripts/tests/test_pio_scripts.py` — only partial: it shells out and parses config, but has no repeated-run comparison.

Copy from it: `_repo_root()`, `subprocess.run([...], capture_output=True, text=True, timeout=..., check=False)`, and per-assertion `subTest`. Then add the normalization from RESEARCH lines 848-864:

```python
TEST_LINE = re.compile(
    r"^test/(?P<suite>test_[^/]+)/[^:]+:\d+: "
    r"(?P<name>\w+)(?:: .*?)?\t\[(?P<status>PASSED|FAILED|IGNORED)\]$"
)

def digest(stdout: str) -> str:
    rows = []
    for line in stdout.splitlines():
        match = TEST_LINE.match(line)          # per-line anchor; NOT findall(text)
        if match:
            rows.append((match["suite"], match["name"], match["status"]))
    lines = [f"{suite}/{name}: {status}" for suite, name, status in rows]
    for status in ("PASSED", "FAILED", "IGNORED"):
        lines.append(f"{status.lower()}={sum(1 for row in rows if row[2] == status)}")
    return "\n".join(lines)
```

Run `pio test -d tests -e native` 20 times with a 300 s per-run timeout; assert exit code on every run; compare digests only. Skip with an explicit message when `pio` is absent — never silently pass.

---

### `scripts/tests/test_native_purity.py` (Python test, subprocess)

**Analog:** `scripts/tests/test_pio_scripts.py` (`CompiledbScriptTests`, lines 106-131) — the closest subprocess/config-contract test.

Run `pio run -d tests -e native -t compiledb`, read `tests/compile_commands.json`, and assert every `command` names only the host compiler and no framework `-I` path. Add the negative case: a temporary copy of the tree with a framework include in `common` must make `pio run` fail (RESEARCH ARCH-05/06 validation row).

---

### `.pre-commit-config.yaml` (hook registration)

**Analog:** the local repo block at `.pre-commit-config.yaml:36-48` — add one more hook to the **same** `- repo: local` list:

```yaml
      - id: check-architecture
        name: shared-library dependency rule
        language: system
        entry: python3 scripts/check_architecture.py
        files: ^(lib|homeworks)/
        pass_filenames: false
```

Keep `files:` so an unrelated commit does not pay the scan cost; keep `pass_filenames: false` because the checker walks the tree itself.

---

### `platformio.shared.ini` (partitions path) and `partitions/default_16MB.csv` (move)

**Analog:** `platformio.shared.ini:10` and `:24` — `board_build.partitions = default_16MB.csv`, resolved relative to each project directory.

Change both to the permanent location:

```ini
board_build.partitions = ../../partitions/default_16MB.csv
```

Do **not** touch the comment block at `:27-30` or the `-std=c11` flag at `:34`. Move the CSV with `git mv homeworks/0_0-toolchain-smoke/default_16MB.csv partitions/default_16MB.csv` in the same change that updates the two references (RESEARCH §Runtime State Inventory: move, never copy).

---

### `docs/decisions/0008-*.md` (ADR) and `docs/decisions/README.md`

**Analog:** `docs/decisions/0007-symlink-shared-libraries.md` — the immediately preceding record; copy its skeleton exactly.

**Frontmatter** (`0007-symlink-shared-libraries.md:1-7`):

```markdown
---
status: accepted
date: 2026-10-24
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# <Title in sentence case>
```

**Eight-section MADR 4.0 order** — required verbatim by `scripts/tests/test_adrs.py:36-45`:

`## Context and Problem Statement`, `## Decision Drivers`, `## Considered Options`, `## Decision Outcome`, `### Consequences`, `### Confirmation`, `## Pros and Cons of the Options`, `## More Information`.

Open the Decision Outcome with `Chosen option: "<option text>", because …` (asserted by `test_adrs.py`). Confirmation must cite the mechanical proof: `scripts/check_architecture.py`, `tests/` native suite, the pre-commit hook.

**Index row** (`docs/decisions/README.md:24-32`):

```markdown
| 0008 | Common depends on port; ports are consumer-owned | accepted | 2026-10-24 |
```

and change the footer to `Next number: **0009**.` in the same change (D-02, D-27).

---

### `scripts/tests/test_pio_scripts.py` (refactor off the smoke project)

**Problem line:** `test_pio_scripts.py:38`

```python
PROJECT_INI = REPO_ROOT / "homeworks" / "0_0-toolchain-smoke" / "platformio.ini"
```

**Analog for the replacement:** `scripts/tests/test_gitignore.py` shows the house approach for "assert against data that need not exist" — `git check-ignore` resolves patterns against a pathname, so the fixture never needs a real file (lines 1-12). Apply the same idea: point `PROJECT_INI` at `REPO_ROOT / "tests" / "platformio.ini"` (which will exist) or synthesize the ini text in a `tempfile.TemporaryDirectory()` and feed `_read_config`.

**Targets to update:**
- `PROJECT_INI` → `tests/platformio.ini` (line 38); drop `PROJECT_SRC`/`main.cpp` assertions or retarget them to `tests/` (there is no `src/` there).
- `D14_KEYS["board_build.partitions"]` at line 66 → `"../../partitions/default_16MB.csv"`.
- `LIB_SOURCES` at lines 45-51 → the new module file names (`ring_buffer.c`, `timing.c`, `crc.c`, `hex.c`, `fake_time.c`, …); `port` has **no** source, so remove its entry.
- `test_library_manifests_agree_with_directories` (lines 186-194): version `0.2.0`; assert `includeDir` for all five and `srcDir` only where a `src/` exists.
- `test_entry_point_is_cpp_and_library_sources_are_c` (lines 196-203): delete the smoke-project assertions; keep a library-source-is-`.c` check over `lib/*/src/**`.

**New test for D-18** (RESEARCH validation table): parse `platformio.shared.ini` with `_read_config`, read both `board_build.partitions` values, resolve each relative to a `homeworks/<id>/` style depth, and assert the file exists.

**Style to keep** (`test_pio_scripts.py:59-71`): constants at module scope, one `unittest.TestCase` class per contract area, `subTest` per parameter, no network, no execution of repository scripts.

---

### `scripts/tests/test_gitignore.py` (retarget stale fixture paths)

**Analog:** the file's own `IGNORED` / `VISIBLE` tables (`test_gitignore.py:62-141`). Replace every `homeworks/0_0-toolchain-smoke/...` fixture string with a neutral, non-existent homework id:

| Line | Old | New |
|------|-----|-----|
| 86 | `homeworks/0_0-toolchain-smoke/CMakeLists.txt` | `homeworks/1_1-example/CMakeLists.txt` |
| 87 | `.../src/CMakeLists.txt` | `homeworks/1_1-example/src/CMakeLists.txt` |
| 88 | `.../sdkconfig.esp32s3_espidf` | `homeworks/1_1-example/sdkconfig.esp32s3_espidf` |
| 136 | `.../sdkconfig.defaults` (VISIBLE) | `homeworks/1_1-example/sdkconfig.defaults` |
| 171, 175, 184 | same three paths in the paired test | same replacements |

The rationale comments ("D-23, P6", "D-23, P7") stay; only the path strings change. `git check-ignore` resolves against patterns, so the tests keep passing with the directory absent.

---

### `homeworks/0_0-toolchain-smoke/` (deletion) and `AGENTS.md` (command fix)

Delete in a **dedicated commit** (D-19) using `git rm -r`, then remove the leftover ignored tree with a plain filesystem delete (RESEARCH §Runtime State Inventory: `.pio/` survives `git rm`).

`AGENTS.md:25` currently documents `pio test -e native`, which fails at the root with `NotPlatformIOProjectError` (Pitfall 7). Change the step 3 command to `pio test -d tests -e native`. Keep the table row's shape and the trailing description style used by every other row.

---

## Shared Patterns

### Header shell (`#pragma once` + `extern "C"`)
**Source:** `lib/port/include/port.h:1-11`
**Apply to:** every new public header in `lib/port`, `lib/common`, `lib/host`, `lib/arduino`, `lib/espidf`.
Open with `#pragma once`; wrap declarations in `#ifdef __cplusplus / extern "C" {` … `}`. The closing block is the last content in the file. No exceptions.

### Factory returned by value
**Source:** RESEARCH §Code Examples lines 774-804, following `lib/arduino/src/arduino_adapter.c`
**Apply to:** every adapter and every host fake.
Adapters and fakes export `port_<contract>_t <owner>_<contract>_port(void)` or `port_<contract>_t host_fake_<contract>_port(host_fake_<contract>_t *)`, initializing positionally (`{ fn, ctx }`). Never a designated initializer (Pitfall 4).

### Error vocabulary
**Source:** RESEARCH Pattern 2 lines 404-411
**Apply to:** all five contracts.
Only `port_status_t`; never `errno`. Time reads and log writes are the documented exceptions (A1).

### Root resolution and exit codes
**Source:** `scripts/check_pr_templates.py:55-76, 240-268`
**Apply to:** `check_architecture.py` and every Python test that shells out.
`--dir` optional; default `git rev-parse --show-toplevel`; `CheckError` → exit 2; violations → exit 1; clean → exit 0. Tests import the module (`from scripts import check_architecture`) when they need unit seams and invoke it via `subprocess` when they assert the process contract — both styles exist in the family (`test_check_policy.py:19` vs `test_check_pr_templates.py:33`).

### Fixture-tree testing
**Source:** `scripts/tests/test_check_pr_templates.py:122-141`
**Apply to:** `test_check_architecture.py`, `test_pio_scripts.py` replacements.
`tempfile.TemporaryDirectory()` + `self.addCleanup(tmp.cleanup)`; build the minimum valid tree; mutate exactly one property per test; assert exit code, the `FAIL <area>` line, and the offending file name.

### Version single-source
**Source:** `lib/common/library.json:3` and D-04/WR-03
**Apply to:** all five manifests and all five source deletions.
`0.2.0` appears in `library.json` only. No `*_version()` function, no `@version` in any `lib_deps` line.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `tests/test/test_common_*/test_*.c` (4 files) | C unit test | transform | No Unity suite exists yet; use the RESEARCH skeleton and Unity 2.6.1 conventions |
| `tests/test/test_port_contracts/test_contracts.c` | C unit test | request-response | Same — first C test in the repository |
| `tests/test/test_host_fakes/test_host_fakes.c` | C unit test | request-response | Same |
| `scripts/tests/test_native_determinism.py` | Python test | batch (subprocess) | Partial analog only (`test_pio_scripts.py`); the 20-run normalized digest has no precedent |
| `scripts/tests/test_native_purity.py` | Python test | batch (subprocess) | Partial analog only; no test currently reads `compile_commands.json` |

For these, the planner should use RESEARCH.md §Code Examples and the Unity skeleton rather than searching further.

## Metadata

**Analog search scope:** `lib/`, `scripts/`, `scripts/tests/`, `.pre-commit-config.yaml`, `platformio.shared.ini`, `homeworks/0_0-toolchain-smoke/`, `docs/decisions/`
**Files scanned:** 22 (5 Phase 2 library pairs, 2 checkers, 5 Python tests, 1 SCons hook, 1 pre-commit config, 1 shared ini, 1 smoke project, 2 ADRs)
**Tracked-source gate:** every cited path confirmed with `git ls-files -- <path>`
**Pattern extraction date:** 2026-10-24
