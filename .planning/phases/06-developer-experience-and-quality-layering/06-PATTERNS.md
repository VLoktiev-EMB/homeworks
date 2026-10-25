# Phase 6: Developer Experience and Quality Layering - Pattern Map

**Mapped:** 2026-10-26
**Files analyzed:** 28 (17 new, 11 modified/integration)
**Analogs found:** 22 / 28

Sources of scope: `06-CONTEXT.md` D-01..D-23 (incl. D-07a/D-08a/D-19a) and
`06-RESEARCH.md` §Recommended Project Structure, §Phase Requirements → Test Map,
§Wave 0 Gaps.

## File Classification

| New/Modified File | Action | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|--------|------|-----------|----------------|---------------|
| `.clang-format` | new | config | transform (source text) | none (new format; RESEARCH §Code Examples) | none |
| `.clang-tidy` | new | config | transform (static analysis) | none (RESEARCH §Code Examples) | none |
| `.markdownlint-cli2.jsonc` | new | config | transform | none (RESEARCH §Code Examples) | none |
| `.yamllint.yaml` | new | config | transform | none (RESEARCH §Code Examples) | none |
| `pyproject.toml` | new | config | transform | none (RESEARCH §Code Examples) | none |
| `.vscode/settings.json` | new | config | request-response (editor config) | `templates/views/workspace.json.tmpl` (same JSON object, other scope) | role-match |
| `scripts/clangd-wrapper.sh` | new | utility | request-response (exec passthrough) | `scripts/tag_homework.sh` + `scripts/ci/check_lfs_pointers.sh` | role-match |
| `scripts/clang-tidy-db` | new | utility (gate) | file-I/O | `scripts/check_architecture.py` + `scripts/ci/check_lfs_pointers.sh` | exact |
| `scripts/tests/test_tooling_config.py` | new | test | batch (config invariants) | `scripts/tests/test_ci_workflows.py` + `scripts/tests/test_docs_pins.py` | exact |
| `templates/homework-arduino/.clangd` | new | config (template source) | transform | `templates/homework-arduino/sdkconfig.defaults`-style static file | role-match |
| `templates/homework-espidf/.clangd` | new | config (template source) | transform | same | role-match |
| `scripts/tests/fixtures/golden/homework-arduino/.clangd` | new | fixture | batch | existing golden tree files | exact |
| `scripts/tests/fixtures/golden/homework-espidf/.clangd` | new | fixture | batch | existing golden tree files | exact |
| `homeworks/1_3-police-flasher/.clangd` | new | config | transform | same template file | exact |
| `docs/standards/vscode.md` | new | docs | prose | `docs/decisions/README.md` + `AGENTS.md` | role-match |
| `docs/decisions/0012-*.md` | new | docs (ADR) | prose | `docs/decisions/0010-python-dependency-policy.md` | exact |
| `docs/decisions/0013-*.md` | new | docs (ADR) | prose | `docs/decisions/0011-squash-merge-commit-message.md` | exact |
| `.pre-commit-config.yaml` | modify | config (hook runner) | event-driven (git stages) | itself | exact |
| `templates/views/mkdocs.yml.tmpl` | modify | template (nav) | transform | itself | exact |
| `templates/views/workspace.json.tmpl` | modify | template (workspace) | transform | itself | exact |
| `scripts/gen_views.py` | modify | service (generator) | transform | itself (`_render_workspace`) | exact |
| `AGENTS.md` | modify | docs (rulebook) | prose | itself | exact |
| `docs/decisions/README.md` | modify | docs (index) | prose | itself | exact |
| `mkdocs.yml` | regenerate | generated | transform | itself (owner `nav`) | exact |
| `homeworks.code-workspace` | regenerate | generated | transform | itself (owner `workspace`) | exact |
| `generated.manifest` | regenerate | generated | transform | itself | exact |
| 60 tracked C/C++ files under `lib/`, `homeworks/`, `tests/`, `templates/homework-*/`, goldens | modify (mechanical) | source | transform (format) | `lib/common/src/hex.c` (already D-02-shaped) | role-match |
| `lib/common/src/hex.c` | modify | source | transform (bitwise) | itself, lines 47-50 | exact |
| `scripts/affected.py` (+ `scripts/tests/test_affected.py`) | optional modify | config (diff mapping) | batch | itself, lines 93-99 | exact |

## Pattern Assignments

### `.clang-format` (config, transform)

**Analog:** none in the tree — first formatter config. Use RESEARCH §Code Examples
verbatim (D-02), and note the resolved-value caveat: `--dump-config` reports
`SortIncludes: {Enabled: true, IgnoreCase: false}`, `AllowShortFunctionsOnASingleLine:
{Empty: true}`, `AlignConsecutiveAssignments: {Enabled: false}`, `ReflowComments: Never`.
D-05's test should assert resolved values by shelling out, not only source text.

### `.clang-tidy` (config, static analysis)

**Analog:** none — RESEARCH §Code Examples, narrowed by D-07a. Keep `WarningsAsErrors: ""`
(warnings-first) and include `-portability-avoid-pragma-once`.

### `.markdownlint-cli2.jsonc`, `.yamllint.yaml`, `pyproject.toml` (config)

**Analog:** none. Use RESEARCH excerpts; they are measured against this tree (MD013/MD060
off; yamllint `line-length: {max: 120}`, `document-start: disable`; ruff
`line-length = 100`, `target-version = "py313"`, per-file `F821` ignores for
`scripts/pio/*.py` and `homeworks/*/merge_firmware.py`).

### `.vscode/settings.json` (config, editor)

**Analog:** `templates/views/workspace.json.tmpl` — same object, different scope (D-19a).

`.gitignore` already un-ignores it, so no ignore change:
```gitignore
# .gitignore:94-99
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json
!.vscode/*.code-snippets
```

### `templates/views/workspace.json.tmpl` (template, transform) — CRITICAL CONSTRAINT

**Analog:** itself.

```json
// templates/views/workspace.json.tmpl:1-14
{
	"folders": [
{{workspace_folders}}
	],
	"extensions": {
		"recommendations": [
			"platformio.platformio-ide"
		],
		"unwantedRecommendations": [
			"ms-vscode.cpptools-extension-pack",
			"pioarduino.pioarduino-ide"
		]
	}
}
```

`scripts/gen_views.py` renders this template through the shared closed renderer:
```python
# scripts/gen_views.py:640-650
def _render_workspace(root, homeworks):
    """Return the produced entry for the whole `homeworks.code-workspace`."""
    display = "homeworks.code-workspace"
    template_display = "templates/views/workspace.json.tmpl"
    template = read_regular_text(root / template_display, template_display)
    rendered = render(
        template,
        {"workspace_folders": _workspace_folders(homeworks)},
        template_display,
    )
```

**The renderer rejects `${...}` outright:**
```python
# scripts/metadata/render.py:28-42
PLACEHOLDER = re.compile(r"\{\{([^{}]*)\}\}")
DOLLAR_BRACE = re.compile(r"\$\{[^}]*\}")

def render(text, mapping, display):
    """Substitute the closed map; an unknown token or `${...}` stops the run."""
    if DOLLAR_BRACE.search(text):
        raise CheckError(
            f"{display}: dollar-brace interpolation '${{...}}' is not allowed"
        )
```

**Consequence the planner must encode:** D-19a's `clangd.path` value
`${env:HOME}/.local/bin/clangd-wrapper` cannot appear literally in this template — the
generator exits 2. Add a closed placeholder (e.g. `{{clangd_wrapper_path}}`) to the template
and a matching key in `_render_workspace`'s mapping whose **value** is the literal
`${env:HOME}/.local/bin/clangd-wrapper`. `re.sub` does not rescan mapping values
(`render.py:32-52`), so the emitted JSON is correct. This makes `scripts/gen_views.py` a
required modified file, not an incidental one.

### `scripts/clangd-wrapper.sh` (utility, exec passthrough)

**Analog:** `scripts/tag_homework.sh` for the shell header/preflight contract and
`scripts/ci/check_lfs_pointers.sh` for the 0/1/2 exit vocabulary.

```bash
# scripts/tag_homework.sh:19-31
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "FAIL arguments: usage: scripts/tag_homework.sh <id>" >&2
  exit 2
fi
```

```bash
# scripts/ci/check_lfs_pointers.sh:21-28
set -eu

target="${1:-.}"

if [ ! -d "$target" ]; then
  echo "check_lfs_pointers: not a directory: $target" >&2
  exit 2
fi
```

Copy the posture: `set -eu`/`set -euo pipefail`, a comment block naming exit codes,
`FAIL ...: reason` on stderr, exit 2 for "environment unusable", exit 1 for "found a
violation". D-17's resolution order (`$ESP_CLANGD` → `command -v esp-clangd` → newest
`~/.espressif/tools/esp-clangd/esp-*/esp-clangd/bin/clangd`), then
`exec "$CLANGD" --query-driver="$PIO_PACKAGES/toolchain-*/bin/*,$PIO_PACKAGES/tool-*/bin/*" "$@"`.
Never `**`. Mode 100755. RESEARCH §Pattern 3 is the shape; the error message must name the
installation source and point at `docs/standards/vscode.md`.

### `scripts/clang-tidy-db` (utility gate, file-I/O)

**Analog:** `scripts/check_architecture.py` — same 0/1/2 contract, same `--dir` override,
same `PASS/FAIL` reporting.

```python
# scripts/check_architecture.py:635-659
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
```

Behaviour (RESEARCH §Pitfall 3, D-09): absent or stale `tests/compile_commands.json`
(mtime older than `tests/platformio.ini`, `platformio.shared.ini`, or described sources)
→ exit 1 and print exactly `pio run -d tests -e native -t compiledb`. Never generate the
database, never write `.pio/`, never skip silently. Give it its own stdlib unit test with a
temp root (same shape as `scripts/tests/test_ci_workflows.py` running a guard against a
`TemporaryDirectory`).

### `scripts/tests/test_tooling_config.py` (test, batch)

**Analog:** `scripts/tests/test_ci_workflows.py` (text/behaviour split, stdlib only) plus
`scripts/tests/test_docs_pins.py` (config invariants read from committed bytes).

```python
# scripts/tests/test_ci_workflows.py:14-45
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
...
class LfsPointerGuardTests(unittest.TestCase):
    """The guard's exit status, not the workflow's spelling of it."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def run_guard(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(GUARD), *args],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
```

```python
# scripts/tests/test_docs_pins.py:37-59
REPO_ROOT = Path(__file__).resolve().parents[2]
...
PIN_LINES = frozenset(
    {"mkdocs==1.6.1", "mkdocs-material==9.7.7", "pymdown-extensions==12.3"}
)
```

Use this structure for the five test classes RESEARCH §Phase Requirements → Test Map names:
`ClangFormatConfigTests` (shell out to clang-format `--dump-config` via the pre-commit env),
`ClangTidyConfigTests` (text), `ClangdWrapperTests` (subprocess with a fake `$ESP_CLANGD` and
a temp `HOME`), `EditorContractTests` (`json.loads` both files, compare settings objects),
`HookLayeringTests` (text: `default_stages`, `stages: [pre-push]`, the five hook ids).
Constraint 04/D-14: never import `yaml`/`jsonschema`.

### `.clangd` template + golden + real tree (config/fixture)

**Analog:** the committed golden fixtures and `scripts/tests/test_new_homework.py`.

```python
# scripts/tests/test_new_homework.py:33-49
GOLDEN_ROOT = REPO_ROOT / "scripts" / "tests" / "fixtures" / "golden"
...
TEMPLATES = ("arduino", "espidf")

# FOUND-01: the eight paths a scaffolded homework must contain.
EIGHT_PATHS = (
    "platformio.ini",
    "src/main.cpp",
    "include/.gitkeep",
    "test/test_homework/test_homework.c",
    "assets/.gitkeep",
    "README.md",
    "task.md",
    "homework.yaml",
)
```

```python
# scripts/tests/test_new_homework.py:68-74
def snapshot(directory: Path) -> dict:
    """Return every file under *directory* as `relative path -> bytes`."""
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob("*"), key=lambda item: item.as_posix())
        if path.is_file()
    }
```

```python
# scripts/tests/test_new_homework.py:187-198
class GoldenTreeTests(ScaffoldTestBase):
    """D-37: a committed expected tree, reported as a unified diff."""

    def test_arduino_tree_matches_its_golden(self) -> None:
        result = self.scaffold(self.root)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assert_golden(self.root, "arduino")
```

`rglob` includes dotfiles, so `.clangd` is covered by the equality test once both goldens
carry it. Regenerate fixtures, never hand-copy:

```python
# scripts/tests/temp_root.py:353-384
def render_tree(source, target, mapping, skip=()):
    """Render every regular file under *source* into *target*.
    ...
    *skip* names source-relative POSIX paths that are
    not rendered (the scaffold skips ``template.yaml``).
    """
```

**Scaffold needs no code change:** `_template_files` walks with `os.walk`, which includes
dotfiles, and only skips `template.yaml`.

```python
# scripts/new_homework:147-176
def _template_files(template_dir):
    ...
    for current, dirnames, filenames in os.walk(template_dir, followlinks=False):
        ...
        for name in sorted(filenames):
            ...
            if relative == Path(MANIFEST_NAME):
                continue
            entries.append((relative, candidate))
```

Content comes from RESEARCH §Code Examples `.clangd` — `CompilationDatabase: .`,
`BuiltinHeaders: QueryDriver`, the `Remove:` GCC-only flags, `Diagnostics.Suppress`.
One byte-identical file in `templates/homework-{arduino,espidf}/.clangd`, both goldens, and
`homeworks/1_3-police-flasher/.clangd`. Do **not** add it to `template.yaml`.

### `.pre-commit-config.yaml` (config, event-driven)

**Analog:** itself.

```yaml
# .pre-commit-config.yaml:1-2
minimum_pre_commit_version: '4.7.0'
default_install_hook_types: [pre-commit]
```

```yaml
# .pre-commit-config.yaml:43-55 — local hook shape
  - repo: local
    hooks:
      - id: no-generated-files
        name: generated files are never committed
        language: system
        entry: >-
          bash -c '...'
        pass_filenames: false
        always_run: true
```

```yaml
# .pre-commit-config.yaml:110-116 — check-only, pass_filenames: false
      - id: gen-views-check
        name: generated views are in sync
        language: python
        additional_dependencies: ["PyYAML==6.0.3"]
        entry: python scripts/gen_views.py --all --check
        files: ^(README\.md$|docs/|templates/views/|boards/|schema/|homeworks/|scripts/gen_views\.py$|scripts/metadata/|generated\.manifest$|mkdocs\.yml$|platformio\.shared\.ini$|homeworks\.code-workspace$)
        pass_filenames: false
```

Apply the target shape from RESEARCH §Code Examples exactly, including the four measured
corrections: `default_install_hook_types: [pre-commit, pre-push]`,
`default_stages: [pre-commit]`, `entry: clang-format --dry-run --Werror` (the mirror defaults
to `-i`), `types_or: [c, c++]`, `ruff-check` (not `ruff`), and the local `clang-tidy-db`
guard placed **above** the `cpp-linter-hooks` repo. Existing gitleaks/hygiene/metadata/views
hooks stay untouched; every added hook is check-only (05/D-21).

### `templates/views/mkdocs.yml.tmpl` (template, nav)

**Analog:** itself.

```yaml
# templates/views/mkdocs.yml.tmpl:18-35
nav:
  - "Home": index.md
  - "Homeworks":
{{homework_nav_entries}}
  - "Boards":
{{board_nav_entries}}
  - "Decisions":
      - "Decision record index": decisions/README.md
{{decision_nav_entries}}
validation:
  nav:
    omitted_files: warn
    absolute_links: warn
```

Insert a static `Standards` section with `standards/vscode.md` (D-22). `validation.nav.omitted_files:
warn` plus `mkdocs build --strict` makes this mandatory; `PinConsistencyTests` also enforces
it against the real tree:

```python
# scripts/tests/test_docs_pins.py:472
def test_nav_lists_every_markdown_file_under_docs(self) -> None:
```

Never hand-edit `mkdocs.yml`; regenerate with `uv run scripts/gen_views.py --all`.

### `docs/standards/vscode.md` (docs, prose)

**Analog:** `docs/decisions/README.md` (the only authored, nav-indexed page besides ADRs) and
`AGENTS.md` (task-oriented prose with tables and code fences). Carry
`# ` heading, short sections, fenced commands, and the one required symlink step:

```bash
ln -sf "$PWD/scripts/clangd-wrapper.sh" "$HOME/.local/bin/clangd-wrapper"
```

macOS and Linux paths; Windows only as a WSL note (D-20). Must mention the clang-tidy
native-test-TU gap (D-08a) explicitly.

### `docs/decisions/0012-*.md`, `0013-*.md` (docs, ADR)

**Analog:** `docs/decisions/0010-python-dependency-policy.md` (frontmatter + sections) and
`0011-squash-merge-commit-message.md` (same skeleton).

```markdown
---
status: accepted
date: 2026-10-24
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---
```

Section order (all ADRs): `## Context and Problem Statement`, `## Decision Drivers`,
`## Considered Options`, `## Decision Outcome`, `## Pros and Cons of the Options`,
`## More Information`. ADR 0012 = formatting approximation (AStyle ≠ clang-format);
ADR 0013 = esp-clangd + multi-root contract, including `BuiltinHeaders: QueryDriver`, the
`--query-driver` execution warning, and the test-TU gap.

### `docs/decisions/README.md` (docs index, prose)

**Analog:** itself.

```markdown
# docs/decisions/README.md:12-14
| Date | Decision | Why | Change cost | Status | Record |
|------|----------|-----|-------------|--------|--------|
| 2026-10-23 | Monorepo with independent PlatformIO projects | per-project isolation, one CI surface, one metadata contract | high — moving a published homework path breaks tags and links | accepted | [0001](0001-monorepo-with-independent-projects.md) |
```

Add two rows dated `2026-10-26`, each linking `[0012](0012-...md)` / `[0013](0013-...md)`,
`Status` `accepted`.

### `AGENTS.md` (docs rulebook, prose)

**Analog:** itself.

```markdown
# AGENTS.md:75-78
## Rules

Every rule carries two dimensions: severity (`[MUST]` or `[SHOULD]`) and where a violation is
caught (`[ENFORCED: pre-commit]`, `[ENFORCED: CI]`, or `[ENFORCED: review]`). No `[MAY]`, no `[INFO]`.
```

Extend the parenthetical to four points (add `[ENFORCED: pre-push]`), insert a
`### Quality tooling` section after `### Secrets` (line 149) / before
`### Assets and generated files` (line 162) using the existing bullet form:

```markdown
# AGENTS.md:149-156
### Secrets

- **[MUST]** **[ENFORCED: pre-commit]** gitleaks must pass. ...
- **[MUST]** **[ENFORCED: review]** A real secret triggers, in this order: ...
```

Add a Routing-table row (table starts line 204) pointing at `docs/standards/vscode.md`.

### `mkdocs.yml`, `homeworks.code-workspace`, `generated.manifest` (generated)

**Analog:** themselves; never hand-edited. `generated.manifest` records `owner`/`mode`/`sha256`/
`bytes` per generated path (`generated.manifest:36-49` for workspace/nav). Regenerate with
`uv run scripts/gen_views.py --all`; the `gen-views-check` hook and `--check` fail on drift.

### 60 tracked C/C++ files (mechanical reformat)

**Analog:** `lib/common/src/hex.c` is already in the D-02 shape (4-space indent, 120 columns,
function brace on its own line) and is the visual reference for the pass:

```c
// lib/common/src/hex.c:20-22
bool common_hex_encode(const uint8_t *data, size_t length, char *out, size_t out_size,
                       size_t *out_length) {
```

Run `clang-format -i` (via the pinned hook env / `pre-commit run clang-format`
with the entry temporarily un-overridden, or the wheel) across `lib/`, `homeworks/`,
`tests/`, `templates/homework-*/`, goldens. This is whitespace-only, one commit, no hand
edits. `types_or: [c, c++]` keeps templates and goldens in scope (RESEARCH Pitfall 10).

### `lib/common/src/hex.c` (source, bitwise fix)

**Analog:** itself, the signed-bitwise sites.

```c
// lib/common/src/hex.c:47-50
    for (index = 0u; index < length; index++) {
        out[index * 2u] = HEX_DIGITS[(data[index] >> 4) & 0x0Fu];
        out[index * 2u + 1u] = HEX_DIGITS[data[index] & 0x0Fu];
    }
```

Fix the seven `bugprone-signed-bitwise` findings by casting the integer promotions to
`unsigned int` before shifting/masking; keep behaviour and the existing comment style.
`WarningsAsErrors` stays empty (D-07a).

### `scripts/affected.py` + `scripts/tests/test_affected.py` (optional)

**Analog:** itself.

```python
# scripts/affected.py:93-99
NO_BUILD_IMPACT = (
    ".planning/",
    ...
    "templates/views/",
```

Root `.clang-*`, `.markdownlint-cli2.jsonc`, `.yamllint.yaml`, `pyproject.toml`, and
`.vscode/` are currently unrecognised and therefore widen the build matrix to every project.
If the planner wants them inert, add them to `NO_BUILD_IMPACT` and to
`NO_BUILD_IMPACT_PATHS` in `scripts/tests/test_affected.py:236-251`. Not required by
TOOL-01..04 and not a CI change; treat as an optional cleanup.

## Shared Patterns

### Check-only hooks (05/D-21)
**Source:** `.pre-commit-config.yaml:91-116`
**Apply to:** every new pre-commit hook.
Hooks report and exit non-zero; they never rewrite, never `git add`. Override the mirror's
`-i` entry; do not use `ruff-format`.

### Deterministic exit vocabulary (04/D-23)
**Source:** `scripts/check_architecture.py:14-19,635-659`; `scripts/ci/check_lfs_pointers.sh:12-15`
**Apply to:** `scripts/clang-tidy-db`, `scripts/clangd-wrapper.sh`.
`0` pass, `1` violation, `2` usage/environment error; human output `PATH: STATUS — reason`;
`--json` where a script enumerates records (04/D-23).

### Stdlib-only tests (04/D-14)
**Source:** `scripts/tests/test_ci_workflows.py:10-12`, `scripts/tests/test_docs_pins.py:9-12`
**Apply to:** `scripts/tests/test_tooling_config.py`.
Never import `yaml` or `jsonschema`; read committed bytes or shell out to `uv run`.

### Closed `{{placeholder}}` rendering, `${...}` forbidden (04/D-25, D-33)
**Source:** `scripts/metadata/render.py:28-52`
**Apply to:** both homework templates and `templates/views/*.tmpl`.
Any `${...}` in a template stops the run with exit 2. Express `clangd.path` through a mapping
value, not template text.

### Generator owns generated files; manifest records the hash (05/D-13)
**Source:** `generated.manifest`, `scripts/gen_views.py:640-650`, `.pre-commit-config.yaml:110-116`
**Apply to:** `mkdocs.yml`, `homeworks.code-workspace`, `generated.manifest`.
Fix drift with `uv run scripts/gen_views.py --all`, never an edit.

### Golden-tree drift guard
**Source:** `scripts/tests/test_new_homework.py:68-74,187-198`; `scripts/tests/temp_root.py:353-384`
**Apply to:** the three `.clangd` locations.
Template, golden, and the real homework change in one coherent commit.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `.clang-format` | config | transform | First formatter config; use RESEARCH §Code Examples |
| `.clang-tidy` | config | static analysis | First analyzer config; use RESEARCH §Code Examples narrowed by D-07a |
| `.markdownlint-cli2.jsonc` | config | transform | No Markdown linter exists yet |
| `.yamllint.yaml` | config | transform | No YAML linter exists yet |
| `pyproject.toml` | config | transform | No root `pyproject.toml` exists (RESEARCH Pitfall 9: `[tool.ruff]` only) |
| `docs/standards/` | docs | prose | Directory does not exist yet; nearest prose analogs are the ADRs and `AGENTS.md` |

## Integration Risks Discovered During Mapping

1. **`render.py` rejects `${env:HOME}`.** D-19a's literal path cannot live in
   `templates/views/workspace.json.tmpl`. Add a `{{clangd_wrapper_path}}` placeholder plus a
   mapping entry in `_render_workspace`, and keep the literal `${env:HOME}/...` in the
   committed `.vscode/settings.json` (the drift test compares parsed values, not text).
2. **`.vscode/settings.json` is already un-ignored** (`.gitignore:94-99`); no ignore change.
3. **`scripts/new_homework` needs no change** for `.clangd`: `os.walk` includes dotfiles.
4. **Root config files widen the build matrix** via `scripts/affected.py`; optional
   `NO_BUILD_IMPACT` addition (see above).
5. **`scripts/affected.py` is not a quality file** — any edit there is orthogonal to the
   phase and should be its own commit if taken.

## Metadata

**Analog search scope:** repo root configs, `scripts/`, `scripts/tests/`, `scripts/ci/`,
`scripts/pio/`, `templates/`, `templates/views/`, `docs/decisions/`, `lib/`, `tests/`,
`.github/workflows/`
**Files scanned:** 24 analogs read; all named analog paths confirmed with
`git ls-files` (no gitignored mirrors).
**Pattern extraction date:** 2026-10-26
