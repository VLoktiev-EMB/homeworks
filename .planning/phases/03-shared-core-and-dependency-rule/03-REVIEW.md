---
phase: 03-shared-core-and-dependency-rule
reviewed: 2026-10-23T22:52:39Z
depth: standard
files_reviewed: 64
files_reviewed_list:
  - .pre-commit-config.yaml
  - AGENTS.md
  - docs/decisions/0008-common-depends-on-port.md
  - docs/decisions/README.md
  - lib/arduino/include/arduino/gpio.h
  - lib/arduino/include/arduino/log.h
  - lib/arduino/include/arduino/time.h
  - lib/arduino/library.json
  - lib/arduino/src/gpio.c
  - lib/arduino/src/log.c
  - lib/arduino/src/time.c
  - lib/common/include/common/crc.h
  - lib/common/include/common/hex.h
  - lib/common/include/common/ring_buffer.h
  - lib/common/include/common/timing.h
  - lib/common/library.json
  - lib/common/src/crc.c
  - lib/common/src/hex.c
  - lib/common/src/ring_buffer.c
  - lib/common/src/timing.c
  - lib/espidf/include/espidf/gpio.h
  - lib/espidf/include/espidf/log.h
  - lib/espidf/include/espidf/time.h
  - lib/espidf/library.json
  - lib/espidf/src/gpio.c
  - lib/espidf/src/log.c
  - lib/espidf/src/time.c
  - lib/host/include/host/fake_gpio.h
  - lib/host/include/host/fake_i2c.h
  - lib/host/include/host/fake_log.h
  - lib/host/include/host/fake_spi.h
  - lib/host/include/host/fake_time.h
  - lib/host/library.json
  - lib/host/src/fake_gpio.c
  - lib/host/src/fake_i2c.c
  - lib/host/src/fake_log.c
  - lib/host/src/fake_spi.c
  - lib/host/src/fake_time.c
  - lib/port/include/port/gpio.h
  - lib/port/include/port/i2c.h
  - lib/port/include/port/log.h
  - lib/port/include/port/spi.h
  - lib/port/include/port/status.h
  - lib/port/include/port/time.h
  - lib/port/library.json
  - partitions/default_16MB.csv
  - platformio.shared.ini
  - scripts/architecture/allowlist.json
  - scripts/check_architecture.py
  - scripts/tests/test_architecture_headers.py
  - scripts/tests/test_check_architecture.py
  - scripts/tests/test_gitignore.py
  - scripts/tests/test_native_determinism.py
  - scripts/tests/test_native_purity.py
  - scripts/tests/test_pio_scripts.py
  - tests/platformio.ini
  - tests/src/main.c
  - tests/test/test_common_crc/test_crc.c
  - tests/test/test_common_hex/test_hex.c
  - tests/test/test_common_ring_buffer/test_ring_buffer.c
  - tests/test/test_common_timing/test_timing.c
  - tests/test/test_host_fake_time/test_fake_time.c
  - tests/test/test_host_fakes/test_host_fakes.c
  - tests/test/test_port_contracts/test_contracts.c
findings:
  critical: 1
  warning: 10
  info: 7
  total: 18
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-10-23T22:52:39Z
**Depth:** standard
**Files Reviewed:** 64
**Status:** issues_found

## Summary

The shared core (`common`, `port`) and the host doubles are in good shape: the CRC, hex,
ring-buffer and timing implementations are small, allocation-free, and their NULL/wrap
semantics are documented and pinned by tests. Every `common` and `host` source
syntax-checks clean under `-std=c11 -Wall -Wextra -Wpedantic`; the shipped checker exits 0
on the real tree; the checker's own 37 Python tests pass; and the full native Unity suite
runs 73 cases with no failures. The port headers are self-sufficient, ASCII-only and
framework-free.

The defects concentrate in the machinery that is supposed to *prove* the architecture rule
and in the adapter layer that nothing in this phase compiles:

- The `platformio.ini` dependency reader parses the `name=` alias and throws away the
  `symlink://` target, so a project can satisfy the closure rule with one library name
  while linking a different one — the gate reports PASS for a configuration the ADR
  forbids (verified against the shipped checker).
- The same reader's env-name heuristic and its "extends target contains `native`" shortcut
  let a target environment be classified as native, so `lib/host` can slip into a firmware
  build (verified).
- `lib/arduino` and `lib/espidf` are not compiled or exercised by any test in this phase
  (`tests/platformio.ini` links only `common`, `port`, `host`), and two of their paths
  diverge from the behavior the fakes implement.
- `AGENTS.md`, the canonical rulebook, still describes `lib/` as planned and still claims
  the local gate covers only "hygiene, large files, secrets".

Line numbers are from the working tree at the reviewed commit range.

## Critical Issues

### CR-01: `lib_deps` alias discards the symlink target, so a forbidden dependency passes the architecture gate

**File:** `scripts/check_architecture.py:460-479` (`_dep_names`)
**Issue:** The entry is split on `=` *before* the `symlink://` form is examined, so the
alias becomes the dependency name and the target path is discarded:

```python
if "=" in entry:
    entry = entry.split("=", 1)[0].strip()
if entry.startswith("symlink://"):
    entry = entry.rstrip("/").rsplit("/", 1)[-1]
```

Two verified consequences against the shipped checker:

1. **False PASS — the gate is defeated.** A homework environment declaring
   `port=symlink://../../lib/arduino` plus `common=symlink://../../lib/common` is read as
   depending on `port`. It therefore satisfies the one-adapter rule (zero adapters
   detected) and the `CLOSURE_REQUIRES_PORT` rule, while it actually links the Arduino
   adapter and never links `port` at all. The run prints
   `PASS config: 1 homework environments satisfy the closure rules` and exits 0.
2. **False FAIL.** A legitimate alias such as `hw=symlink://../../lib/arduino` (or
   `contracts=symlink://../../lib/port`) is read as a library named `hw`, so a correct
   project is rejected with `must also list 'port'`.

This is the gate ADR-0008 names as its Confirmation, so a silent false PASS contradicts the
record's central claim.
**Fix:** Derive the name from the target, never from the alias; if the alias is kept, use it
only as an assertion that can be checked.

```python
def _dep_names(value):
    """Turn a `lib_deps` value into the set of library names it names."""
    names = set()
    for raw_line in value.replace("\r", "\n").splitlines():
        entry = raw_line.split(";", 1)[0].strip()
        if not entry:
            continue
        alias = ""
        if "=" in entry:
            alias, entry = (part.strip() for part in entry.split("=", 1))
        if entry.startswith("symlink://"):
            # The target path is the identity; a bare alias is not.
            entry = entry.rstrip("/").rsplit("/", 1)[-1]
        entry = entry.split("@", 1)[0].strip()
        if not entry:
            continue
        names.add(entry)
        if alias and alias != entry:
            names.add(alias)  # keep the mismatch visible to the config rules
    return names
```

## Warnings

### WR-01: Test-looking environment names skip every config rule

**File:** `scripts/check_architecture.py:132`, `scripts/check_architecture.py:510-511`
**Issue:** `TEST_ENV_NAME` is matched against the *name* only, and a match `continue`s before
the one-adapter, closure and host-native checks. Verified: an environment named
`[env:integration_test]` (`platform = espressif32`, two adapters, plus `host`) is skipped
entirely, and the run reports `PASS config: 0 homework environments satisfy the closure
rules`. Any firmware environment whose name happens to contain `test` escapes all three
rules, and a project can simply choose such a name.
**Fix:** Decide the exemption from evidence, not the name — e.g. skip only when the env sets
`test_framework` or `test_build_src = false` or `platform = native`, or require an explicit
opt-out key. At minimum, still apply the one-adapter and host-native rules to skipped envs.

### WR-02: The "exactly one adapter" rule is implemented as "at most one adapter"

**File:** `scripts/check_architecture.py:518-529`
**Issue:** ADR-0008 (`docs/decisions/0008-common-depends-on-port.md:49-54`) states "a
homework depends on `common`, `port` and exactly one adapter". The code only rejects
`len(adapters) > 1`. Verified: a firmware environment with `platform = espressif32`,
`framework = arduino`, `lib_deps = port=symlink://../../lib/port` and
`common=symlink://../../lib/common`, and no adapter, passes with
`PASS config: 1 homework environments satisfy the closure rules` — nothing in the project
implements the ports for that target.
**Fix:** For a non-native environment, reject zero adapters as well:

```python
if not native and len(adapters) != 1:
    found = ", ".join(sorted(adapters)) or "none"
    violations.append(
        _violation("config", relative, 0, "config",
                   f"[env:{name}] must name exactly one adapter (found {found})")
    )
```

### WR-03: The `native` heuristic short-circuits the `extends` chain and misclassifies a target env

**File:** `scripts/check_architecture.py:432-440`
**Issue:** When a key is absent, `_option` walks the `extends` targets and applies
`if key == "platform" and "native" in target.lower(): return "native"` *inside the loop*,
so the first target whose name contains `native` wins even when a later target carries a
real `platform`. Verified: `[env:hw] extends = base_native_helpers, esp32s3_arduino` with
`host=symlink://../../lib/host` passes, although `esp32s3_arduino` declares
`platform = espressif32@8.0.0`. The `host`-must-be-native rule is therefore bypassable by
ordering, and any section named `*_native_*` is treated as a host build regardless of what
it declares.
**Fix:** Consult the name heuristic only after the whole chain has been searched, or drop
it and require an explicit `platform = native`:

```python
for target in _extends_targets(parser, section):
    for candidate in ("env:" + target, target):
        value = _option(parser, candidate, key, seen)
        if value:
            return value
if key == "platform" and "native" in section.lower():
    return "native"
return ""
```

### WR-04: The GPIO double accepts pin modes and levels that both real adapters reject

**File:** `lib/host/src/fake_gpio.c:25`, `lib/host/src/fake_gpio.c:41`
**Issue:** `host_fake_set_mode` stores `mode` and `host_fake_write` stores `level` without
validating either. `arduino_set_mode` (`lib/arduino/src/gpio.c:19-21`) and `espidf_set_mode`
(`lib/espidf/src/gpio.c:41-43`) return `PORT_ERR_INVALID_ARG` for an unknown mode, and
`espidf_write` (`lib/espidf/src/gpio.c:55-57`) does the same for an unknown level; the
port-contract test's own double also rejects an invalid level
(`tests/test/test_port_contracts/test_contracts.c:47-49`). Code that passes a cast enum
value therefore passes against the fake and fails on target — the double hides exactly the
class of bug it exists to catch.
**Fix:** Reject values outside the documented enumerators before consuming the forced
status:

```c
if (mode != PORT_GPIO_INPUT && mode != PORT_GPIO_OUTPUT &&
    mode != PORT_GPIO_INPUT_PULLUP) {
    return PORT_ERR_INVALID_ARG;
}
```

and likewise `level != PORT_GPIO_LOW && level != PORT_GPIO_HIGH` in `host_fake_write`.

### WR-05: ESP-IDF logging silently filters records the Arduino adapter emits

**File:** `lib/espidf/src/log.c:30`
**Issue:** `esp_log_write` "checks the level and tag level. If logging is allowed then it
outputs it as is." (installed header
`components/log/include/esp_log_write.h:44`, ESP-IDF 5.5.3). With the fixed tag `"port"` at
the default tag level (`ESP_LOG_INFO`), every `PORT_LOG_DEBUG` record is dropped, and a
`CONFIG_LOG_MAXIMUM_LEVEL` setting can drop `INFO` too. The Arduino adapter deliberately
emits unconditionally (`lib/arduino/src/log.c:25-27` uses `log_printf`, bypassing the
level-gated macros), so identical consumer code produces different output on the two
adapters. Neither `lib/port/include/port/log.h` nor
`lib/espidf/include/espidf/log.h:11-13` discloses the filtering; the latter claims only a
one-to-one mapping.
**Fix:** Make the guarantee explicit and equal — either call
`esp_log_level_set("port", ESP_LOG_VERBOSE)` before returning the contract, or document in
`port/log.h` that a sink may filter and that `write` is best-effort — and state the chosen
behavior in `espidf/log.h`.

### WR-06: The ESP-IDF GPIO adapter rejects the wrong pin range and reports invalid arguments as I/O errors

**File:** `lib/espidf/src/gpio.c:20`, `lib/espidf/src/gpio.c:8-13`
**Issue:** The guard is `pin >= 64`, but the target's valid range is 0..48
(`SOC_GPIO_PIN_COUNT 49` in the installed ESP32-S3 `soc_caps.h:177`). Pins 49..63 pass the
adapter's own check and reach `gpio_config`/`gpio_set_level`, which answer
`ESP_ERR_INVALID_ARG`; `map_esp_err` then collapses *every* non-OK code to `PORT_ERR_IO`, so
a caller error is reported as a bus failure, and this adapter can never produce
`PORT_ERR_INVALID_ARG`, `PORT_ERR_TIMEOUT` or `PORT_ERR_NOT_SUPPORTED`. The same collapse
hides `ESP_ERR_INVALID_STATE` (pin already claimed by another peripheral).
**Fix:** Reject the actually invalid range and preserve the distinction:

```c
if (pin >= SOC_GPIO_PIN_COUNT) {
    return PORT_ERR_INVALID_ARG;
}
...
static port_status_t map_esp_err(esp_err_t err) {
    switch (err) {
        case ESP_OK:                return PORT_OK;
        case ESP_ERR_INVALID_ARG:   return PORT_ERR_INVALID_ARG;
        case ESP_ERR_TIMEOUT:       return PORT_ERR_TIMEOUT;
        case ESP_ERR_NOT_SUPPORTED: return PORT_ERR_NOT_SUPPORTED;
        default:                    return PORT_ERR_IO;
    }
}
```

(`SOC_GPIO_PIN_COUNT` needs `soc/soc_caps.h`, which the adapter may include as a framework
header.)

### WR-07: `port_time_now_ms` dereferences an unchecked contract, unlike its sibling helper

**File:** `lib/port/include/port/time.h:25-27`
**Issue:** `port_time_now_ms` calls `time->now_ms(time->ctx)` with no guard, while
`port_log_write` two headers away guards both `log` and `log->write`. The project treats a
NULL contract as a supported case elsewhere: `common_debounce_update` checks
`time == NULL || time->now_ms == NULL` itself (`lib/common/src/timing.c:22-24`), and the
time fake's callback dereferences `ctx` without a check either
(`lib/host/src/fake_time.c:5-9`). Any caller that zero-initialises a `port_time_t` — or that
passes a NULL fake to `host_fake_time_port` — faults instead of seeing a defined result,
and no test covers the case.
**Fix:** Mirror the log helper and document the choice:

```c
static inline uint32_t port_time_now_ms(const port_time_t *time) {
    if (time == NULL || time->now_ms == NULL) {
        return 0u; /* no clock: a fixed instant, never a fault */
    }
    return time->now_ms(time->ctx);
}
```

### WR-08: `common_debounce_t` has no initializer and no documented initial value

**File:** `lib/common/include/common/timing.h:29-33`
**Issue:** `common_debounce_t` is the only stateful type in `common` without an init
function, and the header never states that it must be zero-initialised. A stack instance
with an indeterminate `candidate_since_ms` either promotes on its first call or suppresses
the first real transition for up to 2^32 ms; the tests work only because each one
hand-writes `{false, false, 0u}` (`tests/test/test_common_timing/test_timing.c:11-16`).
`common_ring_buffer_t` in the same library spells its zero-init semantics out and offers
`common_ring_buffer_init`, so the omission is inconsistent as well as unsafe.
**Fix:** Add and document:

```c
void common_debounce_init(common_debounce_t *state, bool initial_level);
```

plus one contract line: "a zero-initialised struct is a debounce released at level false
with no pending change".

### WR-09: The bus contracts do not define NULL buffer semantics, and the two in-repo implementations disagree

**File:** `lib/port/include/port/spi.h:21`, `lib/port/include/port/i2c.h:22-25`
**Issue:** Neither header says whether `tx`/`rx`/`data` may be NULL. The shipped double
rejects a transfer with `tx == NULL && length > 0` (`lib/host/src/fake_spi.c:20-22`), while
the port-contract test's double accepts the same call and synthesises zeros into `rx`
(`tests/test/test_port_contracts/test_contracts.c:151-160`). `host_fake_i2c_read`
(`lib/host/src/fake_i2c.c:42-45`) rejects `data == NULL` only when `length > 0`, and
`write_read` additionally requires `rx_length <= tx_length` — a model constraint not
expressed in `port/i2c.h`. A consumer written against one implementation fails on the
other.
**Fix:** State the rule in both port headers ("`rx` may be NULL to discard incoming bytes;
`tx` must be non-NULL when `length > 0`", or the converse) and make both doubles implement
the same rule.

### WR-10: `AGENTS.md` still describes the shipped tree as planned and the local gate as three checks

**File:** `AGENTS.md:34-52`, `AGENTS.md:29`
**Issue:** This phase commits `lib/`, `tests/`, `partitions/` and `platformio.shared.ini`,
yet "Repository layout — Present today" lists none of them, and "Planned, each with the
phase that introduces it" still says `lib/ — shared portable libraries: common, port, and
thin adapters (Phase 3)`. The same file is the canonical rulebook, so a reader is told the
libraries do not exist while a pre-commit hook enforces rules over them. Step 7 still
describes `pre-commit run --all-files` as "hygiene, large files, secrets", omitting
`check-architecture` (new in this phase) and `no-generated-files` (already missing before
this phase). `scripts/tests/test_agents_md.py` pins neither paragraph, so nothing catches
the drift.
**Fix:** Move `lib/`, `tests/`, `partitions/` and `platformio.shared.ini` into "Present
today", delete the `lib/` line from "Planned", and extend step 7's purpose to name the
architecture and generated-file gates. Consider a test asserting that each path named under
"Present today" exists, so the section cannot rot again.

## Info

### IN-01: `consume_forced_status` is copied verbatim into three fakes

**File:** `lib/host/src/fake_gpio.c:5-12`, `lib/host/src/fake_i2c.c:5-12`,
`lib/host/src/fake_spi.c:5-12`
**Issue:** The same nine-line helper is triplicated; a change to the one-shot semantics has
to be made three times.
**Fix:** Move it into one private header under `lib/host/src/` (not under `include/`) and
include that from the three translation units.

### IN-02: Unused `<stdint.h>` in the ESP-IDF log adapter

**File:** `lib/espidf/src/log.c:1`
**Issue:** Nothing in the file uses a fixed-width type; `port_log_level_t` and
`esp_log_level_t` supply the types.
**Fix:** Drop the include.

### IN-03: `test_check_architecture.py` cannot be executed directly

**File:** `scripts/tests/test_check_architecture.py:25`
**Issue:** `from scripts import check_architecture` requires the repository root on
`sys.path`, which only holds under `python3 -m unittest`. Running
`python3 scripts/tests/test_check_architecture.py` fails with
`ModuleNotFoundError: No module named 'scripts'` (verified); every sibling module in
`scripts/tests/` imports only stdlib and runs either way.
**Fix:** Add `sys.path.insert(0, str(Path(__file__).resolve().parents[2]))` before that
import, as the sibling suites already resolve `REPO_ROOT` from `__file__`.

### IN-04: The config group passes vacuously when no homework environment exists

**File:** `scripts/check_architecture.py:482-487`, `scripts/check_architecture.py:671-675`
**Issue:** `check_platformio` returns `(violations, 0)` when `homeworks/` is absent, and the
report prints `PASS config: 0 homework environments satisfy the closure rules`. The include
scan deliberately treats an empty tree as an environment error (exit 2) so success cannot
be claimed without evidence; the config group has no equivalent guard, so a deleted or
renamed project directory stays invisible. Expected today (no homework exists yet), but the
asymmetry should close before homeworks land.
**Fix:** Report `SKIP config: no homework environments` instead of `PASS`, or require at
least one environment once any `homeworks/*/` directory exists.

### IN-05: Nothing pins the `check-architecture` hook registration

**File:** `.pre-commit-config.yaml:55-60`
**Issue:** The ADR's Confirmation relies on this hook, but no test asserts that the hook id,
`entry`, `files` pattern or `pass_filenames: false` survive; all 37 Python tests pass with
the hook deleted. `scripts/tests/test_agents_md.py` only checks that the literal string
`pre-commit run --all-files` appears in `AGENTS.md`.
**Fix:** Add a test that parses `.pre-commit-config.yaml` and asserts the local hook ids
`no-generated-files` and `check-architecture`, their entries, and that the `files` pattern
still covers `lib/`, `homeworks/`, `scripts/architecture/` and the checker itself.

### IN-06: The blocking scan covers `lib/common` but not `lib/port`

**File:** `scripts/check_architecture.py:397-402`
**Issue:** ADR-0008 calls `port` a leaf that owns no state; a `delay(`, `millis(` or
`esp_timer_get_time(` in a `port` header would not be reported. The docstring acknowledges
this ("that is a review reading, not a scan"), so the gap is documented rather than hidden.
**Fix:** Extend the `relative.startswith("lib/common/")` filter to the pure owners
(`("lib/common/", "lib/port/")`); no port header contains a token today, so this costs
nothing.

### IN-07: The ADR index gives no signal that ADR-0008 supersedes a sentence of ADR-0002

**File:** `docs/decisions/README.md:25`, `docs/decisions/README.md:13-14`
**Issue:** The index still shows `0002 … accepted` with no annotation, while ADR-0008
states that it supersedes the "dependency rule" sentence of ADR-0002. The index's numbering
rules describe only the whole-record `superseded by ADR-NNNN` case, so a reader scanning
the table cannot see the partial supersession.
**Fix:** Annotate the 0002 row, e.g. `accepted (dependency-rule sentence superseded by
ADR-0008)`, and add that partial-supersession form to the numbering rules.

---

_Reviewed: 2026-10-23T22:52:39Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
