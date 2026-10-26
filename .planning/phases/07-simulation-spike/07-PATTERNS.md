# Phase 7: Simulation Spike - Pattern Map

**Mapped:** 2026-10-26
**Files analyzed:** 16 (11 hand-edited, 3 generated, 1 moved, 1 deleted)
**Analogs found:** 14 / 16 (the two remaining are generated outputs with no hand-write pattern)

Scope sources: `07-CONTEXT.md` §decisions D-08…D-14, §code_context, and
`07-RESEARCH.md` §Recommended Project Structure, §Measurement Protocol, §Code Examples.
Every analog below is git-tracked source (verified with `git ls-files`); no
`.gsd/capabilities/**` mirror path is named.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `docs/decisions/0014-simulator-selection.md` | decision record (ADR) | static document | `docs/decisions/0013-clangd-multi-root-contract.md` | exact |
| `docs/decisions/README.md` (one row) | decision index | static document | same file, rows 14–29 | exact |
| `scripts/pio/merge_firmware.py` (moved, rewritten) | build tool (SCons post action) | command assembly → `env.Execute` | `homeworks/1_3-police-flasher/merge_firmware.py` + `scripts/pio/compiledb.py` | exact (move) / role-match (new home) |
| `scripts/tests/test_merge_firmware.py` | test (unit, pure function) | transform | `scripts/tests/test_platformio_readers.py` | exact |
| `scripts/tests/test_simulation_paths.py` | test (subprocess, tool-gated) | request-response via CLI | `scripts/tests/test_tooling_config.py::ClangdGuideCommandTests` | exact |
| `homeworks/1_3-police-flasher/platformio.ini` (one line) | config | build wiring | same file, lines 18–22 | exact |
| `homeworks/1_3-police-flasher/homework.yaml` (one value) | config (metadata) | static document | same file, lines 14–17 | exact |
| `homeworks/1_3-police-flasher/report.md` (§7/§9 sentences) | document (authored prose) | static document | same file, lines 283–286 and 415–418 | exact |
| `homeworks/1_3-police-flasher/README.md` (§Simulation) | document (authored prose) | static document | same file, lines 39–45 | exact |
| `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md` | phase evidence record | static document + measurement tables | `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md` | role-match |
| `pyproject.toml` (one ignore line removed) | config (lint policy) | static document | same file, lines 18–22 | exact |
| `docs/homeworks/1_3-police-flasher.md` | **generated** | renderer output | `scripts/gen_views.py` (`_decision_nav_entries`, `_nav_label`) | generated |
| `mkdocs.yml` | **generated** | renderer output | `scripts/gen_views.py` nav section | generated |
| `README.md` (homework table region) | **generated** | renderer output | `generated.manifest` `readme` region entry | generated |
| `generated.manifest` | **generated** | digest ledger | same file | generated |
| `homeworks/1_3-police-flasher/merge_firmware.py` | **deleted** | — | the moved source above | exact |
| (not a file) timestamp wrapper | — | — | — | deliberately inline: RESEARCH §Pattern 2, "not committed as a tool" |

## Pattern Assignments

### `docs/decisions/0014-simulator-selection.md` (decision record, static)

**Analog:** `docs/decisions/0013-clangd-multi-root-contract.md`

**MADR frontmatter** (lines 1–7) — the exact five keys, in this order, `decision-makers` as a
flow list, `consulted`/`informed` empty:

```markdown
---
status: accepted
date: 2026-10-26
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---
```

**Title** (line 9) — one `# ` ATX heading. `gen_views.py::_decision_label` reads this heading
as the nav label, so it must exist and must be the first heading after the frontmatter:

```markdown
# clangd and the multi-root editor contract
```

**Section order** (headings at their observed line numbers): `## Context and Problem
Statement` (11), `## Decision Drivers` (22, bullet list), `## Considered Options` (38, bullet
list), `## Decision Outcome` (46, opens `Chosen option: "…", because …`), topic `###`
subsections inside the outcome (64, 76, 92), `### Consequences` (102), `### Confirmation`
(115), `## Pros and Cons of the Options` (129, one `###` per option with `* Good, because` /
`* Bad, because` / `* Neutral, because`), `## More Information` (174).

**Decision Outcome opening** (lines 46–51):

```markdown
## Decision Outcome

Chosen option: "one discovered esp-clangd behind `scripts/clangd-wrapper.sh`, per-project
`.clangd`, and the editor contract emitted in the generated workspace `settings` object",
because it is the only combination that reaches all five roots, discovers both versioned
directories at run time, and keeps each project's database local.
```

**Consequences bullets** (lines 104–113) — the Good/Bad/Neutral vocabulary, one sentence each,
each naming its cost rather than a benefit restated:

```markdown
* Good, because one server and one index serve every root, and each project's database is
  found by nearest ancestor from its own `.clangd`.
* Bad, because the setup needs one filesystem step, the `~/.local/bin` symlink, before the
  committed `clangd.path` resolves.
* Neutral, because esp-clangd is Espressif's build of clangd; the standard headers it supplies
  are the ones the target build uses.
```

**Confirmation** (lines 115–127) — the commandable-evidence section; for ADR-0014 this is
where the link to `07-SPIKE-EVIDENCE.md` and the two new test module invocations belong:

```markdown
### Confirmation

* `python3 -m unittest scripts.tests.test_tooling_config.ClangdWrapperTests -v` runs the real
  wrapper with a temporary `HOME`, proves the resolution order, the exit-2 diagnostics, and the
  exact two forwarded globs.
```

**Prose width:** ~100 columns, hard-wrapped, no MD013 enforcement (`.markdownlint-cli2.jsonc`
disables MD013/MD060; MD024 is `siblings_only`).

---

### `docs/decisions/README.md` (decision index, static)

**Analog:** itself.

**Table header and the two row shapes to copy** (lines 12–13, 25, 28):

```markdown
| Date | Decision | Why | Change cost | Status | Record |
|------|----------|-----|-------------|--------|--------|
| 2026-10-25 | Ceremony trim: proportion process to frequency | recurring cost, not appearance, decides what stays | low — ceremony can be restored | accepted | — |
| 2026-10-26 | esp-clangd and the multi-root editor contract | one server for five roots, a bounded driver allowlist, one documented machine step | moderate — the path is consumed by every homework and the onboarding guide | accepted | [0013](0013-clangd-multi-root-contract.md) |
```

Rules carried by those rows: `Date` is `YYYY-MM-DD`; `Change cost` starts with the D-09-style
word (`low` / `moderate` / `high` / `irreversible`) followed by `— <consequence>`; `Status` is
`accepted` for a live decision; `Record` is `—` when the row is the whole record, and a
relative link `[00NN](00NN-slug.md)` only when an ADR file exists. ADR-0014 qualifies (D-09),
so the new row carries the link. Rows are appended in date order, after line 29. The paragraph
at lines 1–10 ("The table is the index and the default record…") is **not** edited.

---

### `scripts/pio/merge_firmware.py` (build tool, command assembly)

**Analogs:** `homeworks/1_3-police-flasher/merge_firmware.py` (the code being moved) and
`scripts/pio/compiledb.py` (the shared-script *shape*).

**Shared-script shape from `scripts/pio/compiledb.py`** (whole file, 23 lines) — module
docstring that names the wiring and the reason, `from __future__ import annotations`, stdlib
imports only, and `Import("env")` as the last statement:

```python
"""Point PlatformIO's compilation database at the project directory.
...
``platformio.shared.ini`` wires this file as a ``pre:`` extra script, so it runs
before the build graph is constructed and the override reaches the ``compiledb``
target. ...
"""

from __future__ import annotations

import os

Import("env")

env.Replace(
    COMPILATIONDB_PATH=os.path.join(env.subst("$PROJECT_DIR"), "compile_commands.json")
)
```

**Current merge logic to preserve** (`homeworks/1_3-police-flasher/merge_firmware.py`):

- docstring lines 1–9: the F-09 rationale — `tool-esptool`, esptool 5, `merge-bin`,
  `--flash-mode`, `--flash-size`, "writes only `$BUILD_DIR/firmware.merged.bin`".
- lines 13, 16–18: `Import("env")` then the argument atomizer:

```python
def _quote(value):
    """Quote one argument so a build path containing spaces stays atomic."""
    return f'"{value}"'
```

- lines 21–47: the image list and the argv; offsets from `FLASH_EXTRA_IMAGES` first, the
  application last; `hex()` for integer offsets, pass-through for strings:

```python
    images = [
        (offset, env.subst(path))
        for offset, path in env.get("FLASH_EXTRA_IMAGES", [])
    ]
    images.append((env.subst("$ESP32_APP_OFFSET"), str(target[0])))

    command = [
        _quote(esptool),
        "--chip",
        board.get("build.mcu", "esp32"),
        "merge-bin",
        "-o",
        _quote(merged),
        "--flash-mode",
        board.get("build.flash_mode", "dio"),
        "--flash-size",
        board.get("upload.flash_size", "4MB"),
    ]
```

- lines 49–54: the single `env.Execute(env.VerboseAction(...))` and the
  `env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", merge_firmware)` registration. Keep the
  `AddPostAction` target string byte-identical — Pitfall 7: `post:` is load order, the actual
  merge is the post action.

**Differences the promotion must introduce** (from RESEARCH §Code Examples and Pitfalls 8–9):

1. SCons globals guarded so the module is importable by a test —
   `try: Import("env") / except NameError: env = None` (the target shape is quoted at
   RESEARCH 696–719). `compiledb.py` does **not** need this guard because nothing imports it;
   the promoted merge script does, and this is the one deliberate divergence from the
   `scripts/pio/compiledb.py` shape.
2. Extract `build_merge_command(env, esptool, build_dir, target_path)` as a pure function so
   `test_merge_firmware.py` needs no SCons — the "Don't Hand-Roll" row "Firmware-image test".
3. Replace the bare `join(env.PioPlatform().get_package_dir("tool-esptool"), "esptool")` with
   a load-time membership guard (`"tool-esptool" in env.PioPlatform().packages`) and a named
   `SystemExit` message (Pitfall 8), and resolve the directory inside the post action.
4. Do **not** parse `package.json`'s version (Pitfall 9: `2.50400.0` vs esptool `5.4.0`).

**Import resolution for the test:** `scripts/pio/` has **no `__init__.py`**; `scripts.pio`
resolves as a PEP 420 namespace package from the repository root (verified:
`find_spec('scripts.pio.compiledb')` → `scripts/pio/compiledb.py`). So
`from scripts.pio.merge_firmware import build_merge_command` works under
`python3 -m unittest discover -s scripts/tests -t .`, provided step 1 above is done.

---

### `scripts/tests/test_merge_firmware.py` (unit test, pure function)

**Analog:** `scripts/tests/test_platformio_readers.py` (283 lines, exact shape: in-process
import of a `scripts.*` module, no PyYAML, no shell-out).

**Module docstring** (lines 1–9) — names the rule it protects, the decision id, and what the
cases pin:

```python
"""Unit tests for the shared `platformio.ini` readers.

`scripts.metadata.platformio` is stdlib-only, so this module imports it in
process and never reads PyYAML (04/D-14). The cases pin the two relative
`extra_configs` depths the repository really uses, ...
"""
```

**Imports** (lines 11–24) — `from __future__ import annotations`, stdlib only, then the module
under test; no `sys.path` surgery:

```python
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.metadata.errors import CheckError
from scripts.metadata.platformio import (
    dep_names,
    extends_targets,
    load_ini,
    ...
)
```

**Base class with disposable state** (lines 40–62) — used here for a stub `env` per test:

```python
class ReaderTestBase(unittest.TestCase):
    """One disposable project tree per test."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="platformio-readers-")
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def write(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path
```

**Assertion style** (lines 84–87, 193–195, 207–209) — `assertEqual(expected, actual, message)`
with the expected value first, and a `with self.assertRaises(...) as raised:` +
`assertIn(fragment, str(raised.exception))` pair for the failure message. The missing-package
case must assert the *named* remedy, mirroring line 195's `self.assertIn("quoted", …)`.

**Main guard** (lines 282–283):

```python
if __name__ == "__main__":
    unittest.main()
```

**Stub `env` shape for this file** (derived from the four SCons methods the script actually
uses — `subst`, `get`, `BoardConfig().get`, `PioPlatform().packages`; RESEARCH "Don't
Hand-Roll": "a stub is ten lines"). The stub must return a mapping for `FLASH_EXTRA_IMAGES` and
`$ESP32_APP_OFFSET`, a `BoardConfig()` with `build.mcu` / `build.flash_mode` /
`upload.flash_size`, and a `PioPlatform()` whose `packages` is a dict to exercise both the
present and absent `tool-esptool` paths.

**Alternative loader if the in-process import is rejected:** `test_tooling_config.py` lines
1120–1128, `importlib.machinery.SourceFileLoader` + `spec_from_loader` + `exec_module` — the
established precedent for loading a single script file that is not a clean module. Prefer the
plain import; this is the fallback.

---

### `scripts/tests/test_simulation_paths.py` (subprocess test, tool-gated)

**Analog:** `scripts/tests/test_tooling_config.py::ClangdGuideCommandTests` (lines 1362–1410) —
the exact positive/negative/non-vacuity precedent: a documented invocation is *executed*, a
missing tool skips with a named remedy, and nothing is matched as prose.

**Class docstring and skip-with-remedy** (lines 1362–1385) — the shape to copy verbatim in
intent:

```python
class ClangdGuideCommandTests(unittest.TestCase):
    """G-06-1: the guide's documented command is executed, not matched.

    The ``--check=`` token is extracted from the onboarding guide and handed to
    the real wrapper from the checkout root, so a broken command fails on its
    observed exit status rather than surviving because the prose still carries
    a matching substring. An absent server skips with a named remedy instead of
    passing silently.
    """
    ...
        if not HOMEWORK_DATABASE.is_file():
            self.skipTest(
                "homeworks/1_3-police-flasher/compile_commands.json is absent; "
                "generate it with `pio run -d homeworks/1_3-police-flasher "
                "-t compiledb`"
            )
```

For Phase 7 the gate is `shutil.which("wokwi-cli") is None` →
`self.skipTest("wokwi-cli is not installed; install 0.28.1 with `curl -L https://wokwi.com/ci/install.sh | sh -s 0.28.1`")`.
The repo's other skip convention raises rather than skips for a *required* tool
(`test_affected.py` lines 33–36: `uv` absent → `AssertionError`); `wokwi-cli` is optional on a
developer machine, so **skip** is correct here and `uv` is the precedent for "required".

**Subprocess invocation** (lines 1387–1410) — `cwd=str(REPO_ROOT)`, `capture_output=True`,
`text=True`, an explicit `timeout=`, `check=False`, then assert on the combined output:

```python
                result = subprocess.run(
                    [bash, str(WRAPPER), invocation],
                    cwd=str(REPO_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )
                combined = result.stdout + result.stderr
                ...
                self.assertEqual(0, result.returncode, combined)
                self.assertIn("All checks completed, 0 errors", combined)
```

**Environment helper** — build the child environment explicitly rather than mutating
`os.environ`; `test_tooling_config.py` lines 222–236 show the pattern (`child = {"HOME": …,
"PATH": …}` plus an override dict, passed as `env=child`). For this module the override is:

```python
{"WOKWI_CLI_TOKEN": "dummy", "WOKWI_CLI_SERVER": "ws://127.0.0.1:1"}
```

**The three assertions** (RESEARCH §Pattern 3; the commands are verified in RESEARCH
§Code Examples):

```text
positive:    correct relative option values  -> stderr contains "Error connecting to ws://127.0.0.1:1"
negative:    repo-root option values         -> stderr contains "diagram.json not found"
non-vacuity: the negative stderr names the doubled path
             "homeworks/1_3-police-flasher/homeworks/1_3-police-flasher/assets/diagram.json"
```

Design notes that make the test trustworthy, all from the verified probes:

- Assert on `"Error connecting to"` **plus** the override URL, never on the errno
  (`EPERM` in-sandbox, `ECONNREFUSED` outside).
- `--elf <tmp file>` sets both firmware and ELF, so no build artifact is needed. Keep `--elf`
  present in **both** cases so the only variable is the option spelling — this is the
  controlled-variable refinement over the two blocks printed in RESEARCH §Code Examples
  (the negative block there omits `--elf`, which is correct for the CLI but adds a second
  difference to the experiment).
- Create the fixture with `Path.write_bytes(b"")` in `setUp` via
  `tempfile.TemporaryDirectory` + `addCleanup` (the `ReaderTestBase` shape above), not
  `: > "$TMPDIR/…"`, so the test owns its lifetime.
- `--timeout 15000` in milliseconds (Pitfall 2); a bare `15` would abort in 15 ms.
- Option values are the project-relative `scenario.yaml` and `assets/diagram.json`; the
  positional argument is `homeworks/1_3-police-flasher` (Pitfall 4).
- `WOKWI_CLI_SERVER` is undocumented and exists at the installed commit's `constants.ts`. If a
  future CLI drops it, the test fails loudly — acceptable, and better than a network
  dependency (RESEARCH §Code Examples note).
- No `REPO_ROOT`-relative `mkdocs.yml`/prose assertion anywhere: D-13 forbids a doc-sync test,
  and those were pruned in quick task `261026-ky7`.

**`REPO_ROOT` constant** (`test_tooling_config.py` line 32, `test_docs_pins.py` line 37):

```python
REPO_ROOT = Path(__file__).resolve().parents[2]
```

---

### `homeworks/1_3-police-flasher/platformio.ini` (config, one line)

**Analog:** itself. Lines 18–22 are the contract; only the `post:` value changes:

```ini
; extends replaces list options wholesale: repeating the inherited compiledb
; entry is required or the target build stops producing compile_commands.json.
extra_scripts =
    pre:../../scripts/pio/compiledb.py
    post:merge_firmware.py
```

becomes `post:../../scripts/pio/merge_firmware.py`. Keep the `pre:` line byte-identical
(Pitfall 6: `extends` replaces `extra_scripts` wholesale) and keep the two-line comment above
it. The relative spelling `../../scripts/pio/…` is the same depth as the existing
`pre:` entry and the existing `extra_configs`, so it survives `pio run -d <project>`
(RESEARCH: `GetExtraScripts` resolves under `fs.cd($PROJECT_DIR)`).

---

### `homeworks/1_3-police-flasher/homework.yaml` (metadata, one value)

**Analog:** itself, lines 14–17:

```yaml
simulation:
  tool: wokwi
  diagram: assets/diagram.json
  status: pending
```

Change only `status` to `verified`, and only after the executed, evidenced run (D-10). No key
is added or removed: the schema is `additionalProperties: false` (D-10, Pitfall "a new field is
a schema change"), and `verified` is already legal. The first line
`# yaml-language-server: $schema=../../schema/homework.schema.json` stays.

---

### `homeworks/1_3-police-flasher/report.md` (authored prose, minimal correction)

**Analog:** itself.

**§7 simulation paragraph to correct** (lines 283–286):

```markdown
**Simulation.** The canonical diagram passed `wokwi-cli lint --offline`; the scenario has not
been executed because `WOKWI_CLI_TOKEN` is absent. The expected alternating timing is therefore
`simulated`, not observed, and Phase 7 owns the execution and the simulator decision.
```

**§9 evidence paragraph to correct** (lines 415–418):

```markdown
The evidence does not support any claim about the bench, the serial port, or the simulator.
...
The Wokwi scenario has not been executed, so the expected timing is `simulated`, not observed.
```

Both become present-tense-true by adding one sentence that points at
`07-SPIKE-EVIDENCE.md` and ADR-0014 (RESEARCH Open Question 1: "a correction of a
present-tense falsehood, not the README expansion D-15 defers"). Preserve the five-label
vocabulary the ledger defines (line ~291: `measured`, `calculated`, `simulated`, `datasheet`,
`not measured`, plus `measured (observed)`) and do not upgrade `simulated` to `measured` —
simulation is not bench evidence (PITFALLS C10, AF-11). Do not restructure any section; this is
a two-sentence amendment, not the Phase 11 rewrite.

---

### `homeworks/1_3-police-flasher/README.md` (authored prose, minimal correction)

**Analog:** itself, lines 39–45:

```markdown
`wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json` validates the
wiring without one. The run is deferred to Phase 7, so `simulation.status` in
`homework.yaml` stays `pending`.
```

Replace the last two sentences with a pointer to the evidence file; keep the command block
(lines ~31–35) and the dummy-token paragraph unchanged (RESEARCH Open Question 2). The command
block is the *documented command* the F-19 test executes, in project-relative form:

```sh
cd homeworks/1_3-police-flasher
pio run
wokwi-cli . --diagram-file assets/diagram.json --scenario scenario.yaml
```

---

### `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md` (evidence record)

**Analog:** `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md` (role-match: the
repository's only existing phase evidence record).

**Header block** (lines 1–6) — one paragraph stating what the document is, the decision id it
serves, and where the conclusion lives:

```markdown
# Phase 4.2 Friction Log — Tracer Homework 1.3

This log records where delivering the real homework `1_3-police-flasher` hurt, while the
work was fresh. It is the primary output of Phase 4.2: Phases 5 through 10 automate only
what this log proves painful (D-20). Each entry is a step of the delivery cycle, not a
bug report; the homework itself is the instrument that produced the evidence.
```

**"How to read" section** (lines 8–22) — states the fixed field vocabulary *before* the data,
so a reviewer knows what each column means. For Phase 7 the equivalent is the five labels
(`measured`, `calculated`, `datasheet`, `simulated`, `not measured`) plus the qualifier
`calculated (upper bound)`, and the D-08 statement that raw data lives here while the ADR
carries only the conclusion.

**One entry as a two-column field table** (lines 26–38) — the unit of the record; each field
is one table row, and the field set is stable across entries:

```markdown
### F-01 — Scaffold the homework from the template

| Field | Value |
|-------|-------|
| Step | Scaffold with `scripts/new_homework` |
| What hurt | ... |
| Frequency | ... |
| Cheap fix | ... |
| Automation candidate | ... |
| What worked | ... |
| Minutes spent | 0.14 min for the first target build (8.21 s), 0.81 s for the first native run; ... |
| Command | `UV_CACHE_DIR="$TMPDIR/uv-cache" uv run scripts/new_homework 1_3-police-flasher --template arduino` |
```

Phase 7's field set for a run entry (D-08, RESEARCH §Step 0/§Step 2): `Run` (1 cold / 2 warm /
3 repeat), `Command`, `Wall clock`, `Simulator cold or warm` (from the timestamp wrapper),
`Exit code` (with the 0 / 42 / 1 mapping), `Serial log` (`pattern ready` present?), `Simulated
minutes` (dashboard delta or the 15 000 ms bound), `Label` (one of the five). Keep the em-dash
in the `###` heading and the value-first `measured`/`calculated` wording; every number carries
a label, and "token supplied by the repository owner; value not recorded" is the only token
sentence permitted (D-02).

Also record, per RESEARCH: `wokwi-cli 0.28.1 (7cf4ffaebfd8)`, the Velxio `RepoDigests` digest
(the tag is mutable), the container name and named volumes, and the Docker run command as
given.

---

### `pyproject.toml` (lint policy, one line removed)

**Analog:** itself, lines 15–22:

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.ruff.lint.per-file-ignores]
# SCons injects both globals into these scripts; importing them would break the
# build, so the F821 finding is a false positive at exactly these two sites.
"scripts/pio/*.py" = ["F821"]
"homeworks/*/merge_firmware.py" = ["F821"]
```

Delete the last pattern only (Pitfall 11). The comment above says "exactly these two sites"
and must be revised to one site in the same edit — leaving it stale would re-create the very
drift the file is written to avoid. `scripts/pio/*.py = ["F821"]` already covers the new
location.

---

## Generated Outputs (never hand-edited)

Three committed files change as a *consequence* of the status flip and the new ADR. They are
produced by `scripts/gen_views.py`; the only sanctioned action is
`uv run scripts/gen_views.py --all` followed by `--check` (RESEARCH Pitfall 10).

| File | Why it changes | Current state |
|------|----------------|---------------|
| `docs/homeworks/1_3-police-flasher.md` | renders the `simulation` block | line 14: `\| Simulation \| wokwi (pending) \|` |
| `mkdocs.yml` | nav is a directory scan of `docs/decisions/` | lines 26–40, labels from `_decision_label` |
| `README.md` | homework table region | `generated.manifest` `readme`/`region` entry |
| `generated.manifest` | digests + byte counts of the above | `docs/homeworks/1_3-police-flasher.md` entry, `mkdocs.yml` entry |

**Nav-label rule the ADR must satisfy** (`scripts/gen_views.py::_decision_label`,
lines ~1060–1084): the label is the first `# ` heading **after** the frontmatter block; if
there is no heading, it falls back to the filename with the numeric prefix stripped and
hyphens replaced. So a frontmatter-only `# `-less file gets a filename-derived label, and an
ADR that puts its title above the frontmatter gets `status: accepted` as its nav label.

**Nav coverage test that will gate the ADR**
(`scripts/tests/test_docs_pins.py::PinConsistencyTests::test_nav_lists_every_markdown_file_under_docs`,
lines 472–482):

```python
        missing = sorted(docs - set(targets))
        extra = sorted(set(targets) - docs)
        self.assertEqual([], missing, f"the nav omits: {missing}")
        self.assertEqual(
            [], extra, f"the nav names paths that are not files under docs/: {extra}"
        )
```

It reads `mkdocs.yml` with a line regex (`NAV_LINE`, line 53:
`re.compile(r'^\s+- "[^"]+": (\S+\.md)$')`) and no PyYAML. A nav entry whose label breaks the
quoted-scalar shape fails `test_no_nav_entry_is_a_single_quoted_scalar` (lines 484–494), and
`_nav_label` handles that by rendering `"` as `'` — so keep the ADR heading free of double
quotes.

`docs/decisions/README.md` is **not** generated: `_decision_nav_entries` skips it
("`README.md` is the directory index and is emitted by the template itself").

---

## Shared Patterns

### Stdlib-only tests, no PyYAML, no jsonschema
**Source:** `scripts/tests/test_affected.py` lines 1–5 and `scripts/tests/test_docs_pins.py`
lines 9–12; decision 04/D-14.
**Apply to:** `test_merge_firmware.py`, `test_simulation_paths.py`.

```python
No test imports PyYAML or jsonschema: every case invokes the mapper through
`uv run` (D-28), and fixtures are built by string assembly in
`scripts.tests.temp_root.write_synthetic_root` (D-29).
```

Neither new module should need `uv` (both are pure Python / direct subprocess), so prefer the
in-process form and keep the suite fast. If a test does shell out to `uv`, warm it in
`setUpModule` first (`test_affected.py` lines 47–58) so the first-run install line cannot
pollute an stderr assertion.

### Skip-with-a-named-remedy for an optional external tool
**Source:** `scripts/tests/test_tooling_config.py` lines 1380–1408.
**Apply to:** `test_simulation_paths.py` (any test that needs `wokwi-cli`).

Every `skipTest` names the missing artifact *and* the command that produces it. No bare
`skipTest()`, and never a silent pass when the tool is absent.

### Required-tool absence is an error, not a skip
**Source:** `scripts/tests/test_affected.py` lines 33–36.
**Apply to:** nothing in this phase directly; noted so the two skip conventions are not mixed
up. `uv` is required by the suite; `wokwi-cli` is optional on a developer machine.

### SCons globals guarded at import
**Source:** the divergence between `scripts/pio/compiledb.py` line 19 (`Import("env")` bare,
because nothing imports it) and RESEARCH §Code Examples (`try: Import("env") / except
NameError: env = None`, because a test imports it).
**Apply to:** `scripts/pio/merge_firmware.py`. This is the one place the promoted script must
differ from the established `scripts/pio/` shape, and the reason belongs in the module
docstring.

### Deterministic module docstrings that name the decision
**Source:** every file above; e.g. `test_tooling_config.py` line 3 ("D-05 makes success
criterion 1 machine-checked"), `test_platformio_readers.py` line 4 ("04/D-14"),
`pyproject.toml` line 1 ("D-13: the one ruff policy").
**Apply to:** both new test modules, the promoted script, and ADR-0014. Each names the decision
id it implements and the failure mode it prevents — the docstring is the review surface.

### `REPO_ROOT` from `__file__`, never `cwd`
**Source:** `scripts/tests/test_tooling_config.py` line 32, `test_docs_pins.py` line 37,
`test_affected.py` line 25.
**Apply to:** both new test modules (`Path(__file__).resolve().parents[2]`).

### Generated files are produced, never edited
**Source:** `docs/homeworks/1_3-police-flasher.md` line 1
(`<!-- GENERATED — do not edit. Run: uv run scripts/gen_views.py --all -->`) and AGENTS.md
"the fix is `uv run scripts/gen_views.py --all`, never a hand edit".
**Apply to:** all four files in the Generated Outputs table.

### Commit granularity
**Source:** AGENTS.md "Every change is one atomic commit"; D-12 requires the move and the
deletion in the same change; D-13's path test and the promotion are separable (CONTEXT
"Claude's Discretion": "the exact commit split between the evidence/ADR work and the
`merge_firmware.py` promotion").
**Apply to:** at minimum two commits — (1) promotion + `platformio.ini` + `pyproject.toml` +
`test_merge_firmware.py` + deletion; (2) evidence + ADR + `README.md` row + status flip +
prose corrections + `test_simulation_paths.py` + one `gen_views.py --all`. Conventional
Commits, scope `7` or `07`.

## No Analog Found

| File | Role | Data flow | Reason |
|------|------|-----------|--------|
| `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md` | evidence record | measurement tables | Only a `role-match` analog exists (`04.2-FRICTION-LOG.md` is a friction log, not a run ledger). The *field set* must come from RESEARCH §Step 0/§Step 2 and D-08; only the document skeleton is copied. The planner should not invent a schema beyond those fields. |
| (not a file) timestamp wrapper | measurement harness | streaming stdout | Deliberately uncommitted (RESEARCH §Pattern 2: "Recorded inline in the evidence file; not committed as a tool"; D-14 forbids a gate). Copy the nine-line wrapper from RESEARCH 296–306 into the evidence file as a fenced block. |

No file in this phase requires a pattern from outside the repository except the ADR's
*content* (quota, fidelity limits, licence text), which comes from RESEARCH §Step 4/§Step 5.

## Metadata

**Analog search scope:** `docs/decisions/`, `scripts/pio/`, `scripts/tests/`, `scripts/`,
`homeworks/1_3-police-flasher/`, `.planning/phases/04.2-tracer-homework-1-3/`, repository root
config (`pyproject.toml`, `mkdocs.yml`, `generated.manifest`, `.markdownlint-cli2.jsonc`).
**Files scanned:** 12 read in full or in targeted ranges; 4 additional files inspected by
grep.
**Tracking check:** every named analog verified with `git ls-files` (non-empty output).
**Pattern extraction date:** 2026-10-26.
