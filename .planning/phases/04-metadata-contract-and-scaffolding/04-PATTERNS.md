# Phase 4: Metadata Contract and Scaffolding - Pattern Map

**Mapped:** 2026-10-24
**Files analyzed:** 41 (25 new source/config/doc files under `schema/`, `scripts/`, `templates/`; 10 new test/fixture paths; 6 modified or removed paths)
**Analogs found:** 31 / 41

Every analog path below is git-TRACKED source, verified with `git ls-files -- <path>`. No path
in this file points at a gitignored mirror (`homeworks/*/CMakeLists.txt`, `sdkconfig.<env>`,
`.pio/`, `site/`, `compile_commands.json` are deliberately absent from the analog list).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `schema/homework.schema.json` | config (machine contract) | transform | `policy/ruleset-main.json` + `scripts/check_policy.py` | role-match |
| `scripts/metadata/__init__.py` | utility (package marker) | — | `scripts/tests/__init__.py` | exact |
| `scripts/metadata/contract.py` | service (shared library) | transform | `scripts/check_architecture.py` | role-match |
| `scripts/metadata/allowlist.json` | config (committed data) | transform | `scripts/architecture/allowlist.json` | exact |
| `scripts/check_metadata.py` | controller (CLI checker) | batch (scan all homeworks) | `scripts/check_architecture.py` | exact |
| `scripts/new_homework` | controller (CLI generator) | file-I/O | `scripts/tag_homework.sh` + `scripts/check_architecture.py` | role-match (hybrid) |
| `templates/homework-arduino/template.yaml` | config (template manifest) | transform | none (D-19 introduces it) | none |
| `templates/homework-arduino/platformio.ini` | config | transform | `tests/platformio.ini` | exact |
| `templates/homework-arduino/src/main.cpp` | component (firmware entry) | event-driven | `tests/src/main.c` + `lib/port/include/port/gpio.h` | partial |
| `templates/homework-arduino/include/.gitkeep` | placeholder | — | none | none |
| `templates/homework-arduino/test/test_homework/test_homework.c` | test (Unity target test) | batch | `tests/test/test_common_crc/test_crc.c` | exact |
| `templates/homework-arduino/assets/.gitkeep` | placeholder | — | none | none |
| `templates/homework-arduino/README.md` | doc (project stub) | transform | `README.md` (root) | partial |
| `templates/homework-arduino/homework.yaml` | config (metadata document) | transform | none (new contract) | none |
| `templates/homework-espidf/template.yaml` | config | transform | none | none |
| `templates/homework-espidf/platformio.ini` | config | transform | `tests/platformio.ini` + `platformio.shared.ini` | role-match |
| `templates/homework-espidf/src/main.cpp` | component (firmware entry) | event-driven | `tests/src/main.c` + `lib/espidf/include/espidf/gpio.h` | partial |
| `templates/homework-espidf/sdkconfig.defaults` | config (Kconfig fragment) | transform | none (authored Kconfig) | none |
| `templates/homework-espidf/include/.gitkeep` | placeholder | — | none | none |
| `templates/homework-espidf/test/test_homework/test_homework.c` | test | batch | `tests/test/test_common_crc/test_crc.c` | exact |
| `templates/homework-espidf/assets/.gitkeep` | placeholder | — | none | none |
| `templates/homework-espidf/README.md` | doc | transform | `README.md` (root) | partial |
| `templates/homework-espidf/homework.yaml` | config | transform | none | none |
| `templates/task/task.md` | doc (provenance skeleton) | transform | `docs/decisions/0008-common-depends-on-port.md` frontmatter | partial |
| `templates/report/report.md` | doc (bare skeleton) | transform | none (Phase 10 owns the contract) | none |
| `templates/adr/template.md` | doc (moved) | transform | `docs/decisions/template.md` | exact (verbatim move) |
| `templates/board-profile/profile.yaml` | config (profile) | transform | `lib/port/library.json` (manifest shape only) | partial |
| `scripts/tests/test_homework_metadata.py` | test | request-response (subprocess) | `scripts/tests/test_check_architecture.py` | exact |
| `scripts/tests/test_new_homework.py` | test | file-I/O | `scripts/tests/test_check_architecture.py` + `test_tag_homework.py` | role-match |
| `scripts/tests/test_templates.py` | test | transform | `scripts/tests/test_pio_scripts.py` + `test_homework_id.py` | role-match |
| `scripts/tests/test_metadata_deps.py` | test | transform | `scripts/tests/test_agents_md.py` | role-match |
| `scripts/tests/test_adrs.py` (modified) | test | transform | itself | exact |
| `scripts/tests/fixtures/golden/homework-arduino/**` | fixture | — | `scripts/tests/fixtures/ruleset-live.json` (fixtures dir) | partial |
| `scripts/tests/fixtures/golden/homework-espidf/**` | fixture | — | same | partial |
| `.pre-commit-config.yaml` (modified) | config (hook) | event-driven | itself | exact |
| `AGENTS.md` (modified) | doc (rulebook) | — | itself | exact |
| `REUSE.toml` (modified) | config (license) | — | itself | exact |
| `docs/decisions/README.md` (modified) | doc (index) | — | itself | exact |
| `docs/decisions/0009-homework-metadata-contract.md` | doc (ADR) | transform | `docs/decisions/0008-common-depends-on-port.md` | exact |
| `docs/decisions/0010-python-dependency-policy.md` | doc (ADR) | transform | `docs/decisions/0008-common-depends-on-port.md` | exact |
| `docs/decisions/template.md` (removed) | doc | — | moves to `templates/adr/template.md` | exact |

---

## Pattern Assignments

### `schema/homework.schema.json` (config, transform)

**Analog:** `policy/ruleset-main.json` (committed machine contract) + `scripts/check_policy.py`
(the checker that consumes it). The repository pattern is "committed data, deterministic
checker", not "schema embedded in code".

**Committed-contract pattern** — `scripts/check_policy.py:32-35`:
```python
REPO_ROOT = Path(__file__).resolve().parent.parent
POLICY_DIR = REPO_ROOT / "policy"
RULESET_FILE = POLICY_DIR / "ruleset-main.json"
REPOSITORY_FILE = POLICY_DIR / "repository.json"
```
Phase 4 mirrors this exactly: one module constant `SCHEMA_PATH = Path("schema") /
"homework.schema.json"`, resolved against the root, never a literal in two places (D-10).

**Content:** do not invent the schema body. RESEARCH.md lines 720-785 contain the
probe-validated 2020-12 skeleton (required core, `$defs`, `additionalProperties: false` at
every level, anchored `pattern`s for URL/path/version, no `format` keyword). Copy it
verbatim, then add the D-08 nested blocks and nothing else.

**House style:** the file is data in this repository — no SPDX header (REUSE.toml
`**` catch-all, lines 19-22), two-space JSON indentation, keys in the order the document
declares them.

---

### `scripts/metadata/contract.py` (service, transform)

**Analog:** `scripts/check_architecture.py`. This is the single most important analog in the
phase: it is the repository's existing "policy as data + rules as code + allowlist" module,
and D-12 requires the new module to be the same seam for two callers.

**Module docstring pattern** — `scripts/check_architecture.py:1-57`:
```python
#!/usr/bin/env python3
"""Verify the shared-library dependency rule.

... one paragraph of WHY ...

Usage:
  python3 scripts/check_architecture.py [--dir PATH]

Exit codes (a CI contract from Phase 8 onward):
  0  ...
  1  ...
  2  usage or environment error ...
"""
```
Every deterministic check in this repository opens with that three-line exit-code block. The
metadata contract module keeps it and names Phase 8 as the consumer (D-11).

**Error type** — `scripts/check_architecture.py:140-161`:
```python
class CheckError(Exception):
    """A usage or environment problem, reported with exit code 2."""


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
Copy this pair verbatim into the shared module (with the module name in the docstring), so
`check_metadata.py` and `new_homework` share one root-resolution and one error vocabulary.

**Allowlist load and stale-entry rule** — `scripts/check_architecture.py:574-641`. Copy the
shape and adapt the key:
```python
def load_allowlist(root):
    """Read and validate the allowlist; any failure is an environment error."""
    path = root / ALLOWLIST_PATH
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise CheckError(f"cannot read allowlist {path}: {exc}") from exc
    if len(raw) > ALLOWLIST_MAX_BYTES:
        raise CheckError(f"allowlist {path} is {len(raw)} bytes; the cap is {ALLOWLIST_MAX_BYTES}")
    ...
    for index, entry in enumerate(entries):
        where = f"allowlist entry {index}"
        if not isinstance(entry, dict):
            raise CheckError(f"{where} must be an object")
        entry_path = entry.get("path")
        if not isinstance(entry_path, str) or not entry_path.strip():
            raise CheckError(f"{where} must carry a non-empty path")
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise CheckError(f"{where} must carry a non-empty reason")
        validated.append({"path": entry_path.strip(), "reason": reason.strip()})
    return validated
```
```python
def apply_allowlist(violations, entries):
    """Drop covered violations; return `(remaining, stale_entries)`."""
    remaining = []
    matched = [False] * len(entries)
    for violation in violations:
        for index, entry in enumerate(entries):
            if matched[index]:
                continue
            if entry["path"] == violation["path"]:
                matched[index] = True
                break
        else:
            remaining.append(violation)
    stale = [entry for entry, used in zip(entries, matched) if not used]
    return remaining, stale
```
Differences required by CONTEXT: the metadata allowlist drops the `rule` key (one rule:
Cyrillic, D-16/RESEARCH Pattern 3) and the docstring's `(path, rule)` paragraph becomes
`(path)`. The 64 KiB cap stays.

**ID pattern** — one literal, sourced from the same place as the existing test.
`scripts/tests/test_homework_id.py:25-29`:
```python
BACKTICKED = re.compile(r"`([^`\n]+)`")
EXPECTED_PATTERN = r"^[0-9]+_[0-9]+-[a-z0-9-]+$"

MATCHING_IDS = ("1_3-police-flasher", "2_1-blink", "11_4-ring-buffer")
REJECTED_IDS = ("", "police-flasher", "1_3_Police-Flasher", "x.y", "1_3-policía")
```
`contract.py` holds `HOMEWORK_ID = re.compile(r"^[0-9]+_[0-9]+-[a-z0-9-]+$")` plus the D-02
derivation helper (`module`, `lesson`, `slug`). Do not re-type the pattern into the checker,
the scaffold, or the schema-only test — AGENTS.md plus `test_homework_id.py` plus
`contract.py` must be proven to agree by one assertion (RESEARCH anti-pattern, line 508).

**Validation API shape (new, no analog):** RESEARCH Pattern 1 requires the module to validate
*strings in memory*, not only paths, because the scaffold validates rendered bytes before the
first write. Expose one function taking `homework_yaml_text` and `task_md_text` and returning
records; the path-based checker is a thin reader around it.

**YAML loaders (RESEARCH Pattern 4, P2):** `SafeLoader` for `homework.yaml`, `BaseLoader` for
`task.md` frontmatter. The excerpt to encode:
```python
yaml.load(block, Loader=yaml.BaseLoader)   # -> {'retrieved': '2026-10-24T20:01:00Z'}
yaml.safe_load(text)                       # for homework.yaml; ambiguous scalars must be quoted
```

**Provenance primitives** — RESEARCH.md lines 897-907 (probe-verified; copy, do not
re-derive):
```python
CYRILLIC = re.compile(r"[Ѐ-ԯᲀ-᲏ⷠ-ⷿꙀ-ꚟ]")
SPDX_LIKE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]*$")

def valid_iso8601(value: str) -> bool:
    try:
        parsed = datetime.datetime.fromisoformat(value)
    except ValueError:
        return False
    return parsed.tzinfo is not None
```
Never use JSON Schema `format: uri` / `format: date-time` (Pitfall P1 — silently inert).

---

### `scripts/metadata/allowlist.json` (config, transform)

**Analog:** `scripts/architecture/allowlist.json:1` — byte-for-byte shape:
```json
{"version": 1, "entries": []}
```
Keep it one line, empty at acceptance, and deny-by-default. An entry is
`{"path": "homeworks/<id>/task.md", "reason": "..."}`; a stale entry fails the run (exit 1),
matching `_report_group`'s `allowlist` group below.

---

### `scripts/check_metadata.py` (controller, batch)

**Analog:** `scripts/check_architecture.py` (the entire file) and
`scripts/check_pr_templates.py` (the report/main split).

**Entry-point skeleton** — `scripts/check_architecture.py:711-739`:
```python
def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Verify the shared-library dependency rule."
    )
    parser.add_argument(
        "--dir",
        metavar="PATH",
        help="repository root to check (default: git rev-parse --show-toplevel)",
    )
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
This is the mandated exit-code contract (D-11). Add `[PATH...]` positionals and `--json`;
nothing else in `main` changes shape.

**Per-record reporting** — `scripts/check_architecture.py:644-656`, adapted to D-23's
`PATH: STATUS — reason`:
```python
def _report_group(name, violations, pass_sentence):
    """Print one PASS/FAIL group; return 1 when the group failed."""
    if not violations:
        print(f"PASS {name}: {pass_sentence}")
        return 0
    print(f"FAIL {name}: {len(violations)} violation(s)")
    for violation in violations:
        if violation["line"]:
            location = f"{violation['path']}:{violation['line']}"
        else:
            location = violation["path"]
        print(f"  {location}: {violation['rule']}: {violation['message']}")
    return 1
```
Keep the `PATH` component repository-relative POSIX (Security: never leak an absolute path),
and keep the summary lines (`FAIL: ...` / `PASS: ...`) — the tests assert on them.

**Read-only determinism** — `scripts/tests/test_check_architecture.py:78-90` is the test
that proves it; the implementation obligation is: sort every path, no timestamps, no writes.

**PEP 723 preamble + import bootstrap** — RESEARCH.md lines 798-817 (Pitfall P11):
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3", "jsonschema==4.26.0"]
# ///

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.metadata.contract import ...  # noqa: E402
```
The same two version pins must appear verbatim in `.pre-commit-config.yaml`
`additional_dependencies` (D-13); `test_metadata_deps.py` parses both as text.

---

### `scripts/new_homework` (controller, file-I/O)

**Analogs:** `scripts/tag_homework.sh` for the CLI/precondition/exit-code posture, and
`scripts/check_architecture.py` for the argparse + `--dir` + `CheckError` mechanics.

**CLI posture** — `scripts/tag_homework.sh:1-31` and `:41-69`, `:88-109`:
```bash
#!/usr/bin/env bash
# tag_homework.sh <id> - create and push the hw/<id> tag for a merged homework PR.
#
# WHY: ...
#
# USAGE: scripts/tag_homework.sh <id>
#
# EXIT CODES: 0 ...  1 ...  2 usage error
```
```bash
if [ "$#" -ne 1 ]; then
  echo "FAIL arguments: expected exactly one <id>, got $#" >&2
  usage >&2
  exit 2
fi
...
if [[ "$id" =~ $ID_PATTERN ]]; then
  echo "PASS id: '$id' matches the module_lesson-name shape"
else
  echo "FAIL id: '$id' does not match ... (example: 1_3-police-flasher)" >&2
  usage >&2
  exit 2
fi
```
Translate, do not transplant bash: `new_homework` is Python (extensionless, PEP 723 shebang,
D-13/D-18), `argparse` with `id` positional plus `--template`, `--dry-run`, `--json`, `--dir`.
A malformed ID or unknown template is exit 2 *before* any plan output; the pattern is the
shared module's constant.

**Plan-then-write** (RESEARCH Pattern 2 — the production algorithm, not a special case):
compute every rendered `{path: bytes}` in memory → classify each target
(`CREATE` / `UNCHANGED` / `CONFLICT`) → validate the full candidate through
`scripts.metadata.contract` → print the plan → stop if `--dry-run` or any `CONFLICT`. The
`--dry-run` parity that D-21 demands is then true by construction; do not implement two code
paths.

**Atomic write and containment** — RESEARCH.md lines 837-855 (verified shape):
```python
def write_atomic(target: Path, text: str) -> None:
    """Write *text* so a crash never leaves a partial file (D-24)."""
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, prefix=".new_homework-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(tmp_name, target)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def contained(root: Path, homework_id: str) -> Path:
    base = (root / "homeworks").resolve()
    target = (base / homework_id).resolve()
    target.relative_to(base)  # ValueError if the id escaped the tree
    return target
```

**Placeholder renderer** (D-25/D-33, RESEARCH Pattern 5): a closed map
(`homework_id`, `title`, `framework`, `board`, `platformio_version`, `platform_version`);
`{{unknown}}` or any `${...}` → exit 2. Skip symlinked template entries (Security table).

**Output vocabulary** (D-23): reuse the report style above —
`PATH: CREATE — reason`, `PATH: UNCHANGED — reason`, `PATH: CONFLICT — reason`,
`PATH: OK — reason`, `PATH: ERROR — reason`; English, sorted paths, repo-relative POSIX.

---

### `templates/homework-arduino/platformio.ini` (config, transform)

**Analog:** `tests/platformio.ini` (lines 1-29) — the only working project ini in the tree.

**Header/`[platformio]` pattern** — `tests/platformio.ini:1-15`:
```ini
; tests/platformio.ini — the shared-library native suite.
; extra_configs and extra_scripts resolve relative to THIS project directory,
; so both paths are one level up, not two.
[platformio]
default_envs = native
extra_configs = ../platformio.shared.ini
; Project-level option: PlatformIO ignores test_dir inside an [env:] section.
test_dir = test
```
For a scaffolded homework the paths are one level deeper, so `extra_configs` is
`../../platformio.shared.ini` and the hook is `pre:../../scripts/pio/compiledb.py`
(already the shared-ini value, `platformio.shared.ini:16,25,37`). `default_envs` must name
only the target env (D-28): `esp32s3_arduino` (or `esp32s3_espidf`).

**`[env:*]` shape — `extends` only, never repeat inherited lists** —
`tests/platformio.ini:10-29`:
```ini
[env:native]
extends = native_unity
test_framework = unity
; Written explicitly: the PlatformIO default is not a repository contract ...
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
Consequences for the templates (D-28/D-29, Pitfall P8):
- target `[env:esp32s3_arduino]` / `[env:esp32s3_espidf]` declare **only** `extends` and
  `lib_deps`; the `build_flags` list (including `-DBOARD_HAS_PSRAM`) is inherited.
- `[env:native]` extends `native_unity`; repeat its flags only if you add `-Werror`
  (wholesale list replacement), and override `extra_scripts` to the two-level path.
- `lib_deps` for target envs: `common`, `port`, one adapter — all `symlink://../../lib/<name>`,
  no versions (versions live only in `library.json`, AGENTS.md routing rule).
- `lib/host` and `throwtheswitch/Unity` appear **only** in `[env:native]`.

**Shared sections used by the templates** — `platformio.shared.ini:1-37`:
```ini
[esp32s3_arduino]
platform = espressif32@8.0.0
board = esp32-s3-devkitc-1
framework = arduino
board_build.arduino.memory_type = qio_opi
...
board_build.partitions = ../../partitions/default_16MB.csv
```
`toolchain.platform` in `homework.yaml` must equal the `platform` pin here (D-07); the
checker cross-checks it. `toolchain.platformio` has no source in the ini — use the module
constant (Open Question 2).

---

### `templates/homework-*/src/main.cpp` (component, event-driven)

**Analog:** `tests/src/main.c` (the only committed entry point) plus the port/adapter
headers. There is no existing firmware `main.cpp` — the Phase 2 smoke project was removed
(ADR-0007), so this is a partial match by design.

**Composition-root pattern** — `tests/src/main.c:1-23`:
```c
/* Compiled only by `pio run -t compiledb`; this file is never linked into a
   Unity app because tests/platformio.ini sets test_build_src = false. ... */
#include "common/timing.h"
#include "host/fake_time.h"
#include "port/status.h"
#include "port/time.h"

int main(void) {
    host_fake_time_t fake;
    port_time_t clock;
    ...
    clock = host_fake_time_port(&fake);
    ...
}
```
Mirror the shape: construct the adapter's port struct once, pass it to `common`, never store
it in a global (ADR-0008). Starter code uses `port/gpio.h` + `port/log.h`.

**Contract API to call** — `lib/port/include/port/gpio.h:40-45`:
```c
typedef struct port_gpio {
    port_status_t (*set_mode)(void *ctx, uint8_t pin, port_gpio_mode_t mode);
    port_status_t (*write)(void *ctx, uint8_t pin, port_gpio_level_t level);
    port_status_t (*read)(void *ctx, uint8_t pin, port_gpio_level_t *level);
    void *ctx;
} port_gpio_t;
```
Factories: `arduino_gpio_port()` (`lib/arduino/include/arduino/gpio.h:14`),
`espidf_gpio_port()` (`lib/espidf/include/espidf/gpio.h:15`), and the matching
`*_log_port()` returning `port_log_t` (`lib/arduino/include/arduino/log.h:14`,
`lib/espidf/include/espidf/log.h:14`). Logging call is the inline helper
`lib/port/include/port/log.h:35-40`:
```c
static inline void port_log_write(const port_log_t *log, port_log_level_t level,
                                  const char *message) {
    if (log != NULL && log->write != NULL) {
        log->write(log->ctx, level, message);
    }
}
```

**Entry-point linkage (Pitfall P9):** Arduino template defines `void setup(void)` and
`void loop(void)` (C++ mangled by the core); ESP-IDF template defines
`extern "C" void app_main(void)`. The file is `.cpp`, so all included C headers keep their
`extern "C"` guards (already present in every `lib/*/include` header). A test must assert both
tokens.

---

### `templates/homework-{arduino,espidf}/test/test_homework/test_homework.c` (test, batch)

**Analog:** `tests/test/test_common_crc/test_crc.c` — exact Unity shape.

**Full pattern** — `tests/test/test_common_crc/test_crc.c:1-18, 49-57`:
```c
#include <stddef.h>
#include <stdint.h>

#include <unity.h>

#include "common/crc.h"

/* The standard check vector of the CRC-16/CCITT-FALSE catalogue entry. */
static const uint8_t CHECK_VECTOR[] = {'1', '2', '3', '4', '5', '6', '7', '8', '9'};
#define CHECK_VECTOR_LENGTH (sizeof(CHECK_VECTOR))

void setUp(void) {}

void tearDown(void) {}

static void test_crc16_check_value(void) {
    TEST_ASSERT_EQUAL_HEX16(0x29B1u, common_crc16(CHECK_VECTOR, CHECK_VECTOR_LENGTH));
}
...
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_crc16_check_value);
    ...
    return UNITY_END();
}
```
The scaffolded test must be a *real* assertion (D-29), not a placeholder. Use
`lib/host`'s fake as the test double — `lib/host/library.json` exists and is in
`[env:native] lib_deps`; never reference `lib/host` from a target env.

---

### `templates/task/task.md` (doc, transform)

**Analog:** `docs/decisions/0008-common-depends-on-port.md` frontmatter — the only committed
YAML frontmatter block in the repository (partial match: provenance keys differ).

**Frontmatter shape** — `docs/decisions/0008-common-depends-on-port.md:1-9`:
```markdown
---
status: accepted
date: 2026-10-24
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# Common depends on port; ports are consumer-owned
```
Provenance skeleton instead carries exactly four keys (D-15):
```markdown
---
source_url: TODO
retrieved: TODO
attribution: TODO
license: TODO
---

# {{title}}

## Task

TODO: English paraphrase of the assignment. Never the original internal material.

## Acceptance criteria

- TODO
```
Quote-free scalars: `TODO` is literal (D-39); the checker accepts it only while
`homework.yaml` says `status: planned`, and rejects it at `in-progress` and beyond. Never
render a timestamp (Pitfall P10).

`templates/task/task.md` is composed by the scaffold into every homework (Open Question 6);
no homework template carries its own copy.

---

### `templates/adr/template.md` (doc, moved)

**Analog:** `docs/decisions/template.md` — the exact file being moved (D-26). Move verbatim;
do not edit its braces (`{proposed | rejected | ...}` are MADR placeholders, not the scaffold's
`{{...}}` vocabulary). Two consumers must be updated in the same change (Pitfall P12):
`scripts/tests/test_adrs.py:24-26`:
```python
DECISIONS_DIR = Path(__file__).resolve().parents[2] / "docs" / "decisions"
INDEX_FILE = DECISIONS_DIR / "README.md"
TEMPLATE_FILE = DECISIONS_DIR / "template.md"
```
and the assertion message at `test_adrs.py:134-136`; and `docs/decisions/README.md:5-6`.

---

### `docs/decisions/0009-...md` and `0010-...md` (doc, ADR)

**Analog:** `docs/decisions/0008-common-depends-on-port.md` — exact.

**Frontmatter + section order** — copy `0008` lines 1-7 and the eight `##`/`###` headings
(`test_adrs.py:36-45` asserts them): Context and Problem Statement, Decision Drivers,
Considered Options, Decision Outcome + Consequences + Confirmation, Pros and Cons of the
Options, More Information.

**Decision Outcome opening** — `0008:43-47`:
```markdown
## Decision Outcome

Chosen option: "`common` depends on `port`, with consumer-owned contracts", because only
this direction lets the pure logic call an injected operation while `port` remains a leaf
that adapters, test doubles and the host fake can implement independently.
```
The `Chosen option: "..." because ...` sentence is machine-checked; keep that exact opening.
Confirmation sections must name the phase's actual gate commands and must not claim CI runs
them (Phase 8 owns CI), mirroring `0008:87-96`.

**Index rows** — `docs/decisions/README.md:20-33`:
```markdown
| 0008 | Common depends on port; ports are consumer-owned | accepted | 2026-10-24 |

Next number: **0009**.
```
Add rows 0009/0010 and advance "Next number" to **0011** in the same change.

---

### `AGENTS.md` (doc, modified)

**Analog:** itself. Apply D-34 and fix the stale layout (Pitfall P13).

**Layout section to edit** — `AGENTS.md:32-52`:
```markdown
## Repository layout

Present today:

- `AGENTS.md` — this rulebook; `README.md` — the public front door.
...
Planned, each with the phase that introduces it:

- `homeworks/<id>/` — one independent PlatformIO project per assignment (Phase 2 onward).
- `lib/` — shared portable libraries: `common`, `port`, and thin adapters (Phase 3).
- `templates/` — the scaffolding source for a new homework (Phase 4).
- `docs/standards/` — report structure and formatting rationale (planned, Phase 5).
- `.claude/skills/` or `.agents/skills/` — versioned agent skills (planned, Phase 9).
```
Move `homeworks/`, `lib/`, `schema/`, `templates/` into "Present today"; leave
`docs/standards/` and the skills path planned. Add the schema contract, the new quick-start
row (`uv run scripts/check_metadata.py`), the two routing rows ("create a homework",
"validate metadata"), and the new hook to the pre-commit description. The hard ceiling is 300
lines (`scripts/tests/test_agents_md.py:24-25`), and the enforcement vocabulary
(`[MUST]`/`[SHOULD]`/`[ENFORCED: ...]`, lines 27-34) must stay complete.

---

### `.pre-commit-config.yaml` (config, modified)

**Analog:** itself; the local-hook block is the pattern — `.pre-commit-config.yaml:36-61`:
```yaml
  - repo: local
    hooks:
      - id: no-generated-files
        name: generated files are never committed
        language: system
        ...
      - id: check-architecture
        name: shared-library dependency rule
        language: system
        entry: python3 scripts/check_architecture.py
        files: ^(lib/|homeworks/|scripts/architecture/|scripts/check_architecture\.py)
        pass_filenames: false
```
Add the `check-metadata` hook in `repo: local` with `language: python`,
`additional_dependencies: ["PyYAML==6.0.3", "jsonschema==4.26.0"]`,
`entry: python scripts/check_metadata.py`, and `files:` naming `homeworks/`, `schema/`, the
checker, and `scripts/metadata/` — **excluding `templates/`** (unrendered `{{...}}` is not
valid metadata). RESEARCH.md lines 821-829 has the exact block.

---

### `REUSE.toml` (config, modified)

**Analog:** itself — `REUSE.toml:15-28`:
```toml
version = 1

# Catch-all: original code, scripts, configuration, and every path that no
# more specific annotation below claims.
[[annotations]]
path = "**"
SPDX-FileCopyrightText = "2026 VLoktiev-EMB"
SPDX-License-Identifier = "MIT"

# Documentation, homework reports, and planning artifacts.
[[annotations]]
path = ["*.md", "docs/**", "homeworks/**/*.md", ".planning/**"]
SPDX-FileCopyrightText = "2026 VLoktiev-EMB"
SPDX-License-Identifier = "CC-BY-4.0"
```
D-36 adds `templates/**/*.md` to the CC-BY-4.0 list (or a new annotation after it) and leaves
`templates/**/*.ini`, `templates/**/*.json`, `schema/**` on the MIT catch-all. Order matters —
last match wins (comment lines 8-10). `test_license_hygiene.py` and `reuse lint` are the gate.

---

### `scripts/tests/test_homework_metadata.py` (test, request-response)

**Analog:** `scripts/tests/test_check_architecture.py` — exact.

**Subprocess helper + real-tree class** — `test_check_architecture.py:16-90`:
```python
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import check_architecture

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_architecture.py"

...
def run_checker(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(cwd), capture_output=True, text=True, timeout=60, check=False,
    )


def combined(result):
    return result.stdout + result.stderr
```
```python
class RealTreeTests(unittest.TestCase):
    def test_real_tree_passes(self):
        result = run_checker()
        self.assertEqual(0, result.returncode, combined(result))
        self.assertIn("PASS includes:", result.stdout)

    def test_second_run_is_identical_and_read_only(self):
        before = git_status()
        first = run_checker()
        second = run_checker()
        after = git_status()
        self.assertEqual((first.returncode, first.stdout, first.stderr),
                         (second.returncode, second.stdout, second.stderr))
        self.assertEqual(before, after, "the checker modified the working tree")
```
One class for the real (empty) tree, one `FixtureBase` per rule family: build a temp
`homeworks/<id>/` with one mutated property, assert exit 1 and the exact record. Note D-14:
tests must not import `yaml`/`jsonschema`, so the checker is invoked as a subprocess (use
`sys.executable` when it also runs under pre-commit's env, or `uv run scripts/check_metadata.py`
where the dependency pins are under test — Open Question 5).

Coverage matrix: RESEARCH.md lines 1060-1077 (`test_unknown_top_level_key_is_error`,
`test_unknown_nested_key_is_error` with `subTest` per `$defs`, `test_provenance_shapes`,
`test_cyrillic_gate_and_allowlist`, `test_cross_validation`).

---

### `scripts/tests/test_new_homework.py` (test, file-I/O)

**Analogs:** `test_check_architecture.py` (subprocess + `--dir` fixture) and
`test_tag_homework.py` (disposable tree per test, single aggregate assertion on exit codes).

**Fixture setup pattern** — `test_tag_homework.py:30-55, 58-85`:
```python
SCRIPT = REPO_ROOT / "scripts" / "tag_homework.sh"
...
class TagHomeworkTest(unittest.TestCase):
    """Runs the real script with cwd set to a disposable repository."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="tag-homework-")
        self.addCleanup(self._tmp.cleanup)
        base = Path(self._tmp.name)
        ...
```
Phase 4's helper instead copies `templates/`, `schema/`, `platformio.shared.ini`, and
`partitions/` into the temp root and symlinks `lib/` (RESEARCH temp-root fixture, lines
865-877). Use `tempfile.TemporaryDirectory(prefix="new-homework-")` + `addCleanup`, and pass
`--dir <tmp>` — never create a real `homeworks/` directory (context boundary).

**Golden-tree diff** — reuse `difflib.unified_diff` exactly as
`scripts/check_pr_templates.py:111-117`:
```python
def _print_diff(name, reference_name, actual, expected):
    left = actual.decode("utf-8", errors="replace").splitlines()
    right = expected.decode("utf-8", errors="replace").splitlines()
    for line in difflib.unified_diff(
        left, right, fromfile=name, tofile=reference_name, lineterm=""
    ):
        print(f"  {line}")
```
Assert the eight FOUND-01 paths, `UNCHANGED` on rerun, `CONFLICT` + zero writes on a modified
target, and `--dry-run` output equality against a real run.

---

### `scripts/tests/test_templates.py` (test, transform)

**Analogs:** `scripts/tests/test_pio_scripts.py` (config asserted as data, no PlatformIO
import) and `test_homework_id.py` (inventory and two-sided probes).

**Repo-root + exact inventory pattern** — `test_pio_scripts.py:28-64`:
```python
def _repo_root() -> Path:
    """Resolve the repository root so the suite runs from any working directory."""
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(completed.stdout.strip())


REPO_ROOT = _repo_root()
SCRIPT = REPO_ROOT / "scripts" / "pio" / "compiledb.py"
SHARED_INI = REPO_ROOT / "platformio.shared.ini"
...
LIB_SOURCES = {
    "common": ("ring_buffer.c", "timing.c", "crc.c", "hex.c"),
    ...
}
```
Apply the same style: a `TEMPLATE_DIRS` tuple, an exact file inventory per template (so a
missing template file fails), a regex that finds every `{{...}}` token and asserts membership
in the closed map, and `assertNotIn("${", text)` over every template file. The ADR-move test
belongs here or in the updated `test_adrs.py`.

---

### `scripts/tests/test_metadata_deps.py` (test, transform)

**Analog:** `scripts/tests/test_agents_md.py` — reading repository files as text with `re`,
no third-party import.

**Text-as-data pattern** — `test_agents_md.py:20-43`:
```python
REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS = REPO_ROOT / "AGENTS.md"
...
LINE_CEILING = 300

ENFORCEMENT_TOKENS = (...)
CANONICAL_COMMANDS = (
    "scripts/tag_homework.sh",
    "scripts/check_policy.py --check",
    ...
)
```
Phase 4 reads the PEP 723 `dependencies = [...]` lines from both entry scripts and the
`additional_dependencies:` list from `.pre-commit-config.yaml`, and asserts set equality of
`name==version` tokens (D-13). Also assert the hook's `language: python`,
`pass_filenames: false`, and that `files:` does not match `templates/`.

---

### `scripts/tests/fixtures/golden/homework-{arduino,espidf}/**`

**Analog:** `scripts/tests/fixtures/ruleset-live.json` — the existing committed-fixture
convention (single JSON under `scripts/tests/fixtures/`). A directory tree is new; keep the
same location and naming discipline. Contents are generated once from a real `--dir` run and
must never contain a date (Pitfall P10). Commit the rendered `homework.yaml` with
`{{homework_id}}` resolved for the chosen fixture id so the golden diff is stable.

---

## Shared Patterns

### Exit codes and single aggregate result
**Source:** `scripts/check_architecture.py:14-19, 140-161, 711-735`; `scripts/tag_homework.sh:24-27, 179-183`
**Apply to:** `scripts/check_metadata.py`, `scripts/new_homework`, their tests
```text
0  clean / all preconditions passed
1  violation (or conflict) / a gate failed
2  usage or environment error
```
Never `sys.exit` deep in the logic: raise `CheckError` (exit 2) or accumulate failures and
return the count. `--dry-run` reports the same codes as a real run (D-21).

### Root resolution and the `--dir` test seam
**Source:** `scripts/check_architecture.py:144-161` (also `check_pr_templates.py:59-76`)
**Apply to:** both entry scripts and every test that needs a fixture root
Use `git rev-parse --show-toplevel`, explicit `--dir` first. This is what lets Phase 4 test
the scaffold without a real homework directory.

### Committed data plus a deterministic read-only checker
**Source:** `policy/` + `scripts/check_policy.py`; `scripts/architecture/allowlist.json` + `check_architecture.py`
**Apply to:** `schema/`, `scripts/metadata/allowlist.json`, `templates/`, golden trees
The rule lives in committed data, the code only applies it; two runs are byte-identical; no
timestamps and no writes.

### Allowlist with a stale-entry failure
**Source:** `scripts/check_architecture.py:574-641, 693-707`
**Apply to:** `scripts/metadata/allowlist.json` consumption
Entry = path + non-empty reason (no `rule` key here). Unmatched entry is exit 1.

### Atomic, contained, all-or-nothing writes
**Source:** RESEARCH.md lines 837-855
**Apply to:** `scripts/new_homework` only
`tempfile.mkstemp(dir=target.parent)` + `os.replace`; `resolve()` + `relative_to()`;
validate the whole candidate before the first `mkdir`.

### Closed placeholder vocabulary
**Source:** D-25/D-33 and RESEARCH Pattern 5
**Apply to:** every file under `templates/` except `templates/adr/template.md`
`{{name}}` only from the fixed map; any `${...}` is exit 2. The MADR template's `{braces}`
are its own placeholder style and are exempt because the scaffold never renders that file.

### Library versions live only in `library.json`
**Source:** `lib/*/library.json` (AGENTS.md, Routing table)
**Apply to:** every scaffolded `platformio.ini`
`lib_deps` carries `common=symlink://...`, `port=...`, `<adapter>=...` with no version; the
only pinned external is `throwtheswitch/Unity@2.6.1` in `[env:native]`, matching
`tests/platformio.ini:29`.

### ADR discipline
**Source:** `docs/decisions/0008-common-depends-on-port.md` + `docs/decisions/README.md:20-33`
**Apply to:** 0009, 0010, the moved template, and every touched doc
Five frontmatter keys, eight sections in fixed order, `Chosen option: "..." because ...`
opening, index row plus the advanced "Next number".

### Test style
**Source:** `scripts/tests/test_check_architecture.py`, `test_tag_homework.py`,
`test_pio_scripts.py`, `test_agents_md.py`
**Apply to:** all four new test modules
Stdlib `unittest` only (D-14); no `yaml`/`jsonschema` import; module docstring stating what
the file protects and the covered cases; subprocess for CLI behaviour; exact-inventory or
two-sided probes for patterns; `TemporaryDirectory` + `addCleanup` for fixtures.

---

## No Analog Found

Files with no close match; the planner should use RESEARCH.md (or the D-xx decision text)
rather than an existing file. Ten files, grouped into seven rows.

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `templates/homework-{arduino,espidf}/template.yaml` | config | transform | D-19 introduces the per-template manifest; no template registry or manifest exists in the tree |
| `templates/homework-{arduino,espidf}/homework.yaml` | config | transform | The metadata contract is created by this phase; only `policy/*.json` and `lib/*/library.json` are committed machine documents, and neither shares its shape |
| `templates/homework-espidf/sdkconfig.defaults` | config | transform | No Kconfig fragment is tracked; the three lines come from the Phase 2 verification and `sdkconfig.*` is otherwise gitignored |
| `templates/report/report.md` | doc | transform | The 10-section report contract is Phase 10; the file is a bare skeleton only |
| `templates/homework-{arduino,espidf}/include/.gitkeep` | placeholder | — | No `.gitkeep` is tracked anywhere in the repository |
| `templates/homework-{arduino,espidf}/assets/.gitkeep` | placeholder | — | Same |
| `templates/homework-{arduino,espidf}/README.md` | doc | transform | Only a root `README.md` exists; no per-project README precedent |

Also note the **partial** matches that must not be over-trusted: `tests/src/main.c` is a
compile-only stub, not a firmware entry point, and `docs/decisions/0008...md` supplies the
frontmatter *syntax* for `task.md` but not its keys or the `TODO` sentinel rule (D-39).

## Metadata

**Analog search scope:** repository root — `scripts/`, `scripts/tests/`, `scripts/architecture/`,
`docs/decisions/`, `lib/*/include/`, `lib/*/library.json`, `tests/`, `platformio.shared.ini`,
`.pre-commit-config.yaml`, `REUSE.toml`, `AGENTS.md`, `.gitignore`, `policy/`
**Files scanned:** 18 analog files read in full or in targeted ranges; 194 tracked paths listed
**Pattern extraction date:** 2026-10-24
**Tracked-path check:** every named analog appears in `git ls-files`; `schema/`, `templates/`,
`homeworks/`, and `scripts/metadata/` are absent from the index today, confirming they are new.
