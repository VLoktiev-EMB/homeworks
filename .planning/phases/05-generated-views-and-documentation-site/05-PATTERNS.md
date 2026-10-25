# Phase 5: Generated Views and Documentation Site - Pattern Map

**Mapped:** 2026-10-25
**Files analyzed:** 34 (17 new code/config, 9 generated artifacts, 4 modified, 4 tests)
**Analogs found:** 31 / 34 (3 vendored-asset files have no analog)

Scope source: `05-CONTEXT.md` (D-01…D-30) and `05-RESEARCH.md` (§Recommended Project Structure,
§Pattern 1–4, §Validation Architecture). Every analog path below is git-tracked source
(`git ls-files -- <path>` verified); no `.gsd/` capability mirror is named.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/gen_views.py` | utility (CLI entry point) | batch / transform | `scripts/new_homework` | exact |
| `scripts/affected.py` | utility (CLI entry point) | transform (diff → matrix) | `scripts/check_architecture.py` | role-match |
| `scripts/metadata/render.py` | utility (shared library) | transform | `scripts/new_homework` `_render` | exact |
| `scripts/metadata/platformio.py` | utility (shared library) | parse / transform | `scripts/check_architecture.py` `_option`/`_dep_names` | exact |
| `scripts/metadata/board_profile.py` | utility (validator) | request-response (record list) | `scripts/metadata/contract.py` | role-match |
| `scripts/check_metadata.py` (modify) | utility (validator entry point) | request-response | itself + `contract.py` | exact |
| `schema/board-profile.schema.json` | config (data contract) | — | `schema/homework.schema.json` | exact |
| `boards/esp32-s3-devkitc-1.yaml` | config (data) | — | `templates/board-profile/profile.yaml` | exact |
| `templates/views/readme.md.tmpl` | config (template) | transform | `templates/homework-arduino/README.md` | role-match |
| `templates/views/mkdocs.yml.tmpl` | config (template) | transform | `platformio.shared.ini` (whole-file owner) | role-match |
| `templates/views/workspace.json.tmpl` | config (template) | transform | `homeworks.code-workspace` | role-match |
| `templates/views/shared-ini.ini.tmpl` | config (template) | transform | `platformio.shared.ini` | exact |
| `templates/views/homework-page.md.tmpl` | config (template) | transform | `templates/report/report.md` | partial |
| `templates/views/board-page.md.tmpl` | config (template) | transform | `templates/report/report.md` | partial |
| `generated.manifest` | config (generated data) | CRUD (ledger) | `scripts/architecture/allowlist.json` | role-match |
| `mkdocs.yml` | config (generated) | transform | `platformio.shared.ini` (generated whole) | role-match |
| `homeworks.code-workspace` (replace) | config (generated) | transform | itself (current bytes) | exact |
| `platformio.shared.ini` (replace) | config (generated) | transform | itself (current bytes) | exact |
| `README.md` (marker region) | config (generated region) | transform | itself (table at lines 15-17) | exact |
| `requirements-docs.txt` | config (pins) | — | PEP 723 headers + `.pre-commit-config.yaml` pins | role-match |
| `docs/index.md` | config (authored + marker) | transform | `README.md` | exact |
| `docs/homeworks/<id>.md` × N | config (generated page) | transform | `templates/report/report.md` | partial |
| `docs/boards/<id>.md` × N | config (generated page) | transform | `templates/report/report.md` | partial |
| `docs/assets/vendor/katex/0.19.0/{katex.min.js,katex.min.css,contrib/,fonts/,LICENSE}` | config (vendored asset) | — | — | none |
| `docs/assets/vendor/katex/0.19.0/render-math.js` | utility (browser script) | event-driven (`document$`) | — | none |
| `docs/assets/vendor/katex/0.19.0/FILES.sha256` | config (checksum ledger) | — | `scripts/architecture/allowlist.json` (ledger shape only) | partial |
| `.pre-commit-config.yaml` (modify) | config (gate) | — | itself, `check-metadata` hook | exact |
| `.github/workflows/generated-views.yml` | config (CI) | event-driven | `.github/workflows/homework.yml` | exact |
| `.github/workflows/docs.yml` | config (CI) | event-driven | `.github/workflows/homework.yml` | exact |
| `AGENTS.md` (modify lines 39, 192) | config (docs) | — | itself | exact |
| `scripts/tests/temp_root.py` (modify) | test (fixture harness) | file-I/O | itself | exact |
| `scripts/tests/test_gen_views.py` | test | subprocess / batch | `scripts/tests/test_new_homework.py` | exact |
| `scripts/tests/test_affected.py` | test | subprocess / transform | `scripts/tests/test_new_homework.py` + `test_homework_metadata.py` | exact |
| `scripts/tests/test_docs_pins.py` | test | file-I/O | `scripts/tests/test_homework_metadata.py` | exact |

---

## Pattern Assignments

### `scripts/gen_views.py` (utility, batch/transform)

**Analog:** `scripts/new_homework` — the repository's production plan-then-apply renderer. Copy
its skeleton wholesale; change only the candidate source (`templates/views/` + metadata) and the
CLI surface.

**PEP 723 header + module docstring** (lines 1-5; keep `requires-python` and pin style, drop
`jsonschema` — the generator reads metadata, it does not validate it):

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3"]
# ///
```

**Import bootstrap + shared-module contract** (lines 69-79). Every entry script in this repo
inserts the repository root before importing `scripts.metadata.*`; `gen_views.py` and
`affected.py` must do the same:

```python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.metadata.contract import (  # noqa: E402
    CheckError,
    resolve_root,
)
from scripts.metadata.render import render  # noqa: E402
```

**Closed placeholder vocabulary** (lines 83-86) — this moves to `render.py`, but the two
constants and their comment stay the contract:

```python
# D-25/D-33: a closed placeholder vocabulary, and `${...}` is never allowed
# because PlatformIO, CMake and SCons own that syntax.
PLACEHOLDER = re.compile(r"\{\{([^{}]*)\}\}")
DOLLAR_BRACE = re.compile(r"\$\{[^}]*\}")
```

**Core plan-then-apply algorithm** (lines 39-42 docstring, realized in `_build_plan` 385-421 and
`main` 504-536). The shape `gen_views.py` must reproduce exactly:

```python
try:
    root = resolve_root(args.dir)
    <load metadata once>
    records, payloads = _build_plan(root, <subcommand>)
    ordered = _emit(records, args.json)       # prints PATH: STATUS — reason
except CheckError as exc:
    print(f"ERROR: {exc}", file=sys.stderr)
    return 2

blocked = any(item["status"] in CONFLICT_STATUSES for item in ordered)
if args.check or blocked:
    return 1 if blocked else 0

try:
    _write_all(payloads, ordered)
except OSError as exc:
    print(f"ERROR: write failed: {exc}", file=sys.stderr)
    return 2
return 0
```

**Classification without following a symlink** (lines 251-321). `gen_views.py` gains a fourth
status (`MODIFIED`, `DELETED`, `ORPHAN`) instead of `CONFLICT`, but the `lstat` component walk is
the security control (ASVS V12) and must be reused verbatim:

```python
def _component_conflict(base, relative):
    consumed = Path("homeworks")          # gen_views: Path(".") — root-relative
    parts = relative.parts
    for index, part in enumerate(parts):
        consumed = consumed / part
        current = base / Path(*parts[: index + 1])
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise CheckError(f"cannot inspect {consumed.as_posix()}: {exc}") from exc
        if index == len(parts) - 1:
            if stat.S_ISLNK(mode):
                return ("CONFLICT", "target is a symlink; refusing to follow or overwrite it")
            return None
        if stat.S_ISLNK(mode):
            return ("CONFLICT", f"intermediate path {consumed.as_posix()} is a symlink; refusing to follow it")
        if not stat.S_ISDIR(mode):
            return ("CONFLICT", f"intermediate path {consumed.as_posix()} exists and is not a directory")
    return None
```

**Atomic write** (lines 424-436) — reuse unchanged; the temp file must live in the target's own
directory:

```python
def _write_atomic(target, data):
    descriptor, temporary = tempfile.mkstemp(dir=target.parent, prefix=".new_homework-")
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
        os.replace(temporary, target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
```

**Record emission** (lines 450-468) — `PATH: STATUS — reason` on stdout, one sorted JSON array
under `--json`. `gen_views.py` sorts by `path` only (the manifest is a ledger, not a plan):

```python
ordered = sorted(records, key=lambda item: (item["path"], item["status"], item["reason"]))
...
print(f"{item['path']}: {item['status']} — {item['reason']}")
```

**Do not copy:** `_contained_target` (lines 324-382) is `homeworks/<id>`-specific. The equivalent
for `gen_views.py` is a static allowed-root set: every target path must be one of `README.md`,
`docs/**`, `mkdocs.yml`, `homeworks.code-workspace`, `platformio.shared.ini` — reject anything
else as a usage error (exit 2) before classifying.

**Marker-region ownership (new logic, no analog).** D-14/D-09 require `_region(text, begin, end)`:
refuse zero or multiply-present begin markers, refuse an end marker preceding the begin marker,
and hash the region *including both markers* (RESEARCH §Pattern 4). Report an ambiguous marker
layout as a `CheckError` (exit 2) — it is an environment problem, not drift.

---

### `scripts/affected.py` (utility, transform)

**Analogs:** `scripts/check_architecture.py` for the INI/`extends`/`lib_deps` machinery, and
`scripts/check_metadata.py` for the entry-point, `--json` and exit-code shape.

**CLI + exit-code shape** (`check_metadata.py` lines 182-237): `argparse`, `--dir`, `--json`,
try/except `CheckError` → 2, records sorted before printing. `affected.py` adds `--format
{json,paths}` and `--paths-from PATH` (RESEARCH §Git diff input).

**`_option` — `extends` resolution, copy verbatim** (`check_architecture.py` lines 419-444). This
is the code RESEARCH says must move to `scripts/metadata/platformio.py`; `affected.py` imports it
from there rather than redefining it:

```python
def _option(parser, section, key, seen=frozenset()):
    if section in seen or not parser.has_section(section):
        return ""
    if parser.has_option(section, key):
        value = parser.get(section, key).strip()
        if value:
            return value
    seen = seen | {section}
    for target in _extends_targets(parser, section):
        for candidate in ("env:" + target, target):
            value = _option(parser, candidate, key, seen)
            if value:
                return value
        # `native` as a PREFIX, not a substring
        if key == "platform" and re.match(r"native(?:$|_)", target.lower()):
            return "native"
    return ""
```

**`_dep_names` — `name=symlink://` alias rule** (lines 464-489). The alias is **not** the library;
the spec on the right decides (CR-01). Copy it, do not re-derive:

```python
for raw_line in value.replace("\r", "\n").splitlines():
    entry = raw_line.split(";", 1)[0].strip()
    if not entry:
        continue
    if "=" in entry:
        entry = entry.split("=", 1)[1].strip()
    if entry.startswith("symlink://"):
        entry = entry.rstrip("/").rsplit("/", 1)[-1]
    entry = entry.split("@", 1)[0].strip()
    if entry:
        names.add(entry)
```

**INI loading with `interpolation=None`** (`check_architecture.py` 507-514; same idiom as
`contract.py:441`). Pitfall 7 — never split on `=` by hand:

```python
parser = configparser.ConfigParser(interpolation=None)
try:
    with ini.open(encoding="utf-8") as handle:
        parser.read_file(handle)
except (OSError, UnicodeDecodeError) as exc:
    raise CheckError(f"cannot read {relative}: {exc}") from exc
except configparser.Error as exc:
    raise CheckError(f"{relative} is not valid INI: {exc}") from exc
```

**New in this file — `extra_configs` preload (Pitfall 8).** `check_architecture.py` never needs
the shared file because every env repeats `lib_deps`; `affected.py` needs it for `framework`:

```python
[platformio]
extra_configs = ../../platformio.shared.ini
```

Read `[platformio] extra_configs` first, resolve each entry **relative to the project directory**,
`parser.read()` them, then walk `extends`. Warning sign: `"framework": ""`.

**JSON output contract** (RESEARCH §`affected.py` output). Sorted by `(project, env)`; diagnostics
on stderr only so Phase 8 can pipe stdout into `fromJson`:

```json
{"build": [{"project": "homeworks/1_3-police-flasher", "env": "esp32s3_arduino", "framework": "arduino"}],
 "simulate": [{"project": "homeworks/1_3-police-flasher", "env": "esp32s3_arduino", "framework": "arduino"}]}
```

**Git input** — `git diff --name-only -z` plus `git merge-base` (RESEARCH §Git diff input); the
`-z` form survives spaces. `_read_sources`'s containment idiom (lines 263-310: skip symlinks,
`resolve()` then `relative_to(root)` or `CheckError`) is the pattern for any path read from the
diff — never trust a diff path to stay inside the repository.

---

### `scripts/metadata/render.py` (utility, transform) — D-19 extraction

**Analog:** `scripts/new_homework` `_render` (lines 223-238), already duplicated once in
`scripts/tests/temp_root.py:99-111`. Extract once; delete the duplicate bodies.

```python
def render(text, mapping, display):
    """Substitute the closed map; an unknown token or `${...}` stops the run."""
    if DOLLAR_BRACE.search(text):
        raise CheckError(f"{display}: dollar-brace interpolation '${{...}}' is not allowed")

    def replace(match):
        token = match.group(1)
        if token not in mapping:
            raise CheckError(f"{display}: unknown placeholder " + "{{" + token + "}}")
        return mapping[token]

    return PLACEHOLDER.sub(replace, text)
```

**Non-negotiable property** (RESEARCH §Pattern 3): the substitution is one non-recursive pass. A
metadata value containing `{{...}}` must never trigger a second substitution. `re.sub` already
guarantees this; add a regression test rather than changing the implementation.

**Also move** `_read_text` (lines 241-248) — UTF-8 decode failure is `CheckError` (exit 2).

`temp_root.render_tree` (lines 85-116) keeps its `KeyError` contract for golden-fixture
generation; it must **not** start importing `scripts.metadata` (it is imported by tests before
the root exists).

---

### `scripts/metadata/platformio.py` (utility, parse/transform) — recommended extraction

**Analog:** `scripts/check_architecture.py` lines 419-489 (`_option`, `_extends_targets`,
`_dep_names`) plus the parser load at 507-514 and the native rule at 442-443.

Public surface to move (keep names so `check_architecture.py`'s call sites at 521-522 change only
their import line):

| Symbol | Source lines | Contract |
|--------|--------------|----------|
| `option(parser, section, key, seen=frozenset())` | 419-444 | inherited lookup through `extends`; `native` prefix rule |
| `extends_targets(parser, section)` | 447-461 | tolerates `env:` prefix, commas, repeats |
| `dep_names(value)` | 464-489 | alias-aware, `symlink://` last-segment, `@version` strip |
| `load_ini(path)` | 507-514 | `ConfigParser(interpolation=None)`, `CheckError` on failure |

`check_architecture.py` keeps `CheckError` where it is; `platformio.py` must import it from
`contract.py` (or define its own and re-export) — do **not** create a third copy of the class.
The extraction is only correct if `check_architecture.py`'s existing tests stay green with no
behavioural change; that is the gate for the refactor commit.

---

### `scripts/metadata/board_profile.py` (utility, validator) — D-27

**Analog:** `scripts/metadata/contract.py` `load_schema` (465-482) and `validate_homework_text`
(523-579). Same record shape `{"path", "status", "reason", "line"}`; same split between content
problems (exit 1, ERROR record) and environment problems (`CheckError`, exit 2).

```python
def load_schema(root):
    path = Path(root) / SCHEMA_PATH
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CheckError(f"cannot read schema {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise CheckError(f"cannot decode schema {path}: {exc}") from exc
    try:
        schema = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CheckError(f"cannot parse schema {path}: {exc}") from exc
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise CheckError(f"schema {path} is invalid: {exc.message}") from exc
    return schema
```

**Board-profile specifics.** `boards/<id>.yaml` must satisfy the same invariants the homework
schema enforces: `additionalProperties: false` at every level, no `format` keyword (anchored
`pattern` instead — `test_homework_metadata.SchemaShapeTest.test_schema_contains_no_format_keyword`
is the precedent), `id` must equal the file stem (mirror `_homework_directory` for the identity
check). `frameworks` is an array — validate as `{"type": "array", "uniqueItems": true, "items":
{"enum": ["arduino", "espidf"]}}`.

---

### `scripts/check_metadata.py` (modify — add `boards/`)

**Analog:** itself. Add a `_board_directory` walk in the same shape as `_directories` (144-179)
and reuse `_record` (54-61). Keep `load_schema` for both schemas in one `try` so a broken board
schema is exit 2, and keep `records.sort(key=lambda item: item["path"])` so the two document
families interleave deterministically.

The read-only contract (docstring lines 28-32) is unchanged: never write, never read the clock,
two runs byte-identical. Board validation is additive; it must not renumber or reorder existing
homework records.

---

### `schema/board-profile.schema.json` (config)

**Analog:** `schema/homework.schema.json`. Copy the envelope exactly (lines 1-16): draft
2020-12, `"additionalProperties": false`, explicit `required`, `$defs` for nested objects.

Field set, from `templates/board-profile/profile.yaml` (`id`, `soc`, `flash_mb`, `psram`,
`frameworks`, `pinout_url`):

```json
"id": { "type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$" },
"soc": { "type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$" },
"flash_mb": { "type": "integer", "minimum": 1 },
"psram": { "enum": ["none", "quad", "octal"] },
"pinout_url": { "type": "string", "pattern": "^https://[^\\s]+$" }
```

The two `pattern` shapes are lifted from `homework.schema.json:21` (`board`) and `:19` (`id`).
`pinout_url` uses a pattern, never `"format": "uri"` — the reason is written in the test
comment: "`format: uri` accepts 'not a url' without a checker".

---

### `boards/esp32-s3-devkitc-1.yaml` (config/data)

**Analog:** `templates/board-profile/profile.yaml`, copied verbatim — the values are already the
real board's (16 MB flash, octal PSRAM, both frameworks). Only the location changes (D-04).
`templates/board-profile/profile.yaml` stays as the template and is **not** rendered by
`gen_views.py`.

---

### `templates/views/*.tmpl` (config/templates)

**Analog:** `templates/homework-arduino/*` for the placeholder idiom (closed `{{name}}`
vocabulary, no loops), `platformio.shared.ini` for the whole-file-owned text target, and
`homeworks.code-workspace` for the JSON target's exact formatting.

**Placeholder idiom** (`templates/homework-arduino/homework.yaml` lines 3-4, 12-13):

```
id: "{{homework_id}}"
title: "{{title}}"
```

**Fragment placeholders (D-20).** Pre-rendered strings, never loop syntax:
`{{homework_rows}}`, `{{homework_nav_entries}}`, `{{board_nav_entries}}`,
`{{decision_nav_entries}}`, `{{workspace_folders}}`, `{{decision_entries}}`,
`{{board_homework_list}}`.

**`mkdocs.yml.tmpl` must carry** the skeleton from RESEARCH §`mkdocs.yml` skeleton verbatim
(theme features, palette, `plugins: [search]`, `validation:`, all `markdown_extensions`,
`extra_css`/`extra_javascript`), because D-06 makes this one reviewed template the only owner.
Two hard constraints encoded in it:

- nav entries are `- "Title": path` with the colon **unquoted** (Pitfall 1);
- every outbound homework link is `{{repository_url}}/…`, a module constant, never `../../`
  (Pitfall 3) and never `git remote` (RESEARCH §Anti-Patterns; precedent `BOARD` constant at
  `scripts/new_homework:94`).

**`shared-ini.ini.tmpl` must carry** the five-line SCons comment above `[native_unity]` verbatim
(`platformio.shared.ini` lines 27-30):

```
# The C standard flag is safe next to a C++ entry point: SCons routes `-std=`
# into the C-only flag list by language (SCons 4.11.1 `Environment.py`
# lines 1176-1181), so it reaches the `.c` library sources and never the
# `.cpp` entry point. Do not move it into a per-project override.
[native_unity]
```

Only the two pin values are placeholders: `platform = {{platform_pin}}` in both ESP sections and
`platformio` where a Core pin is named. No per-homework entry is ever added (04.2/D-17).

**`workspace.json.tmpl`** must reproduce the editor's own formatting — tab indent (the current
file is tab-indented, `homeworks.code-workspace` lines 1-19), `extensions` block verbatim
(`recommendations: [platformio.platformio-ide]`, the two `unwantedRecommendations`), and
`{"name": …, "path": …}` folders in the order `repo → "."`, `docs → "docs"`, `lib → "lib"`,
`scripts → "scripts"`, then every homework. Serialize the fragment with
`json.dumps(..., indent="\t", ensure_ascii=False)` + `\n` (RESEARCH §Don't Hand-Roll) so a VS Code
re-save is byte-identical.

---

### `generated.manifest` (config/generated data)

**Analog:** `scripts/architecture/allowlist.json` — a committed, versioned JSON ledger with an
explicit `{"version": 1, "entries": [...]}` envelope validated by a checker that exits 2 on a
malformed file. Its validator (`check_architecture.load_allowlist`, lines 574-620) is the exact
shape to copy for reading the manifest back:

```python
version = data.get("version")
if isinstance(version, bool) or not isinstance(version, int) or version != 1:
    raise CheckError(f"{path} must declare version 1")
entries = data.get("entries")
if not isinstance(entries, list):
    raise CheckError(f"{path} must declare an entries list")
```

Entry shape (RESEARCH §Pattern 4; `owner` = subcommand name so a single-subcommand run rewrites
only its own entries):

```json
{"path": "README.md", "owner": "readme", "mode": "region",
 "marker_begin": "<!-- BEGIN GENERATED: homeworks -->",
 "marker_end": "<!-- END GENERATED -->", "sha256": "…", "bytes": 1234}
```

Rules: entries sorted by `path`; two-space indent; one trailing newline; no timestamps; the
manifest never lists itself (recompute and byte-compare instead). Use `hashlib.sha256` — never a
hand-rolled digest (ASVS V6).

---

### `README.md` (modify — marker region)

**Analog:** itself. Lines 13-17:

```markdown
## Homeworks

| ID | Project | Status | Report |
|----|---------|--------|--------|
| 1.3 | [1.3 Police Flasher](homeworks/1_3-police-flasher/) | in progress | [report](homeworks/1_3-police-flasher/report.md) |
```

Wrap exactly this table in `<!-- BEGIN GENERATED: homeworks -->` / `<!-- END GENERATED -->`
(D-14) and replace it with the six-column D-11 table. Everything else — lines 1-11, 19-36 —
stays byte-identical except the stale intro paragraph at lines 9-11 ("Phase 4.2"), which is
edited by hand in the same commit (RESEARCH §Existing artifacts).

**Cell escaping (ASVS V5):** a metadata `title` containing `|` breaks the table and `md_in_html`
passes raw HTML through. Escape `\|`, and strip control characters and newlines from every
single-line field before it enters a cell.

---

### `docs/index.md` (new — authored prose + same marker region)

**Analog:** `README.md` — the authored-prose-outside / generated-table-inside split (D-09).
Same begin/end markers and the identical six-column table renderer, so one code path produces
both (CONTEXT §Integration Points). Authored prose is the site's "Home"; the generator owns only
the marker region.

---

### `docs/homeworks/<id>.md`, `docs/boards/<id>.md` (generated pages)

**Analog:** `templates/report/report.md` — a one-heading Markdown page with `{{title}}` as its
only placeholder (`# {{title}}` at line 1). The generated pages follow that minimal shape plus
the D-03 header:

```markdown
<!-- GENERATED — do not edit. Run `uv run scripts/gen_views.py --all`. -->

# {{title}}
```

Then the D-02 metadata card (id, title, board, framework, language, status, toolchain,
simulation status) as a Markdown table or definition list, and **absolute** links to
`{{repository_url}}/blob/main/homeworks/<id>/report.md` and `.../README.md`. Never copy the report
body (D-02) and never emit a `../../` link (Pitfall 3).

---

### `.pre-commit-config.yaml` (modify — check-only drift hook)

**Analog:** itself, `check-metadata` hook (lines 62-77). Copy the shape, change the entry, the
`files` regex and the dependency list (only `PyYAML==6.0.3`, no `jsonschema`):

```yaml
      - id: gen-views-check
        name: generated views are in sync
        language: python
        additional_dependencies: ["PyYAML==6.0.3"]
        entry: python scripts/gen_views.py --all --check
        files: ^(README\.md|docs/|templates/views/|boards/|schema/|homeworks/|scripts/gen_views\.py$|scripts/metadata/|generated\.manifest$|mkdocs\.yml$|platformio\.shared\.ini$|homeworks\.code-workspace$)
        pass_filenames: false
```

**Hard rule (D-21):** `--check` only. The hook must never regenerate or stage; the failure
message must name `uv run scripts/gen_views.py --all`. Also add `gen_views.py` to the
`check-metadata` hook's `files:` regex (its rendering can change metadata-derived output), the
same defense-in-depth reasoning written at lines 68-70 for `scripts/new_homework`.

---

### `.github/workflows/generated-views.yml` and `.github/workflows/docs.yml` (new CI)

**Analog:** `.github/workflows/homework.yml`. Copy: pinned action SHAs with the `# vX.Y.Z`
comment and the rationale comment at lines 20-21, `permissions: contents: read` (line 7-8),
`concurrency:` group (10-12), `runs-on: ubuntu-24.04`, `timeout-minutes:`.

```yaml
      # Pinned to the v7.0.1 commit, not the mutable `v7` major tag: a tag can
      # be repointed at other code between runs, a commit SHA cannot.
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false
```

- `generated-views.yml`: `on: pull_request`, one job, one step `uv run scripts/gen_views.py --all
  --check`. No matrix (D-21/D-26).
- `docs.yml`: `on: push: branches: [main]` + `workflow_dispatch`; `permissions: contents: read,
  pages: write, id-token: write`; `environment: github-pages`; steps = build with
  `uv run --python 3.13 --with-requirements requirements-docs.txt mkdocs build --strict`, the
  LFS-pointer guard (fail if `site/` contains `git-lfs.github.com/spec/v1`, Pitfall 12), then
  `upload-pages-artifact` + `deploy-pages` at the SHAs resolved in RESEARCH §Local probes
  (`configure-pages@v6 → 45bfe019…`, `upload-pages-artifact@v5 → fc324d35…`,
  `deploy-pages@v5 → 368f8252…`). Checkout **without** LFS.
- `setup-python` pin is already available at `homework.yml:31`.

---

### `scripts/tests/temp_root.py` (modify — fixture coverage)

**Analog:** itself. `COPIED_PATHS` (lines 26-32) currently copies `platformio.shared.ini`,
`partitions`, `schema`, `templates`, `scripts/pio`. The generator tests need `boards/`,
`docs/`, `templates/views/` and root files (`README.md`, `mkdocs.yml`,
`homeworks.code-workspace`, `generated.manifest`, `requirements-docs.txt`) — but a *synthetic*
root (D-29: two homeworks, two libraries, one consumer each) is the better fit for
`test_gen_views.py`.

Recommended: keep `build_root` for the metadata/scaffold suites unchanged, and add a second
builder in the same module (a `write_synthetic_root(base, ...)` helper) rather than widening
`COPIED_PATHS` for every test — copying the real `docs/` tree would couple the unit tests to
authored content. Reuse `repository_root()` (lines 35-48) and `_copy` (51-57) as-is.

---

### `scripts/tests/test_gen_views.py` (new test)

**Analog:** `scripts/tests/test_new_homework.py`. Copy the harness shape, not the assertions.

**Subprocess-only invocation** (lines 47-60) — D-28: no test imports `yaml`.

```python
def run_scaffold(*args: str, timeout: int = 180) -> subprocess.CompletedProcess:
    """Invoke `uv run scripts/new_homework` from the repository root."""
    if shutil.which("uv") is None:
        raise AssertionError(
            "uv is a required repository tool; install it before running this suite"
        )
    return subprocess.run(
        ["uv", "run", SCRIPT, *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
```

**Byte snapshot helper** (lines 63-69) — this is how "authored files are untouched" is proven:

```python
def snapshot(directory: Path) -> dict:
    """Return every file under *directory* as `relative path -> bytes`."""
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob("*"), key=lambda item: item.as_posix())
        if path.is_file()
    }
```

**Test base + assertion vocabulary** (lines 72-103): one `tempfile.TemporaryDirectory` per test,
`self.addCleanup(self._tmp.cleanup)`, an `assert_usage_error` that pins **both** exit 2 and an
empty stdout ("a usage error must print no plan").

**Idempotency assertions** (lines 196-217): second run is all `UNCHANGED`, and no `": CREATE"`,
`": CONFLICT"`, `": ERROR"` in stdout; two runs byte-identical via `snapshot`.

Required classes (RESEARCH §Phase Requirements → Test Map): `IdempotencyTests`, `DriftTests`
(modified / deleted / orphan / manifest-in-sync), `ManifestTests`, `WorkspaceTests`,
`SharedIniTests` (two disagreeing pins → exit 1 naming both, Pitfall 6), `RealTreeSmokeTest`
(`--check --dir <repo>` exits 0 and writes nothing).

**Real-tree smoke helper** — follow `test_homework_metadata.py`'s `git_status()` (lines ~134-141)
to prove no write happened:

```python
def git_status() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, check=True, timeout=60,
    ).stdout
```

Also copy `setUpModule` (lines ~144-152): warm `uv` with `--help` before the first asserted run so
the first-run install line cannot pollute an stderr comparison.

---

### `scripts/tests/test_affected.py` (new test)

**Analogs:** `test_new_homework.py` (subprocess, temp root) for the unit cases, and
`test_homework_metadata.py` `FixtureBase` (lines 190-246) for building a small metadata tree by
**string assembly, never with `yaml`**.

**Fixture tree** — D-29: two homeworks, two libraries, one consumer each. Each fixture homework
needs `platformio.ini` with `[platformio] extra_configs = ../../platformio.shared.ini` and
`[env:<name>] extends = <shared section>` plus `lib_deps = <name>=symlink://../../lib/<name>`,
copied from `homeworks/1_3-police-flasher/platformio.ini:4-16`. Each fixture library needs a
`library.json` shaped like `lib/common/library.json`.

**Unit cases** (`--paths-from` avoids the git dependency, RESEARCH §Git diff input):

```bash
printf 'lib/common/src/x.c\0homeworks/1_3-police-flasher/src/main.cpp\0' > paths.txt
uv run scripts/affected.py --paths-from paths.txt
```

Required classes: `FanoutTests` (lib → consumers; `platformio.shared.ini`/`partitions/`/`schema/`/
`scripts/pio/`/`affected.py` → every project; unknown shared path → every project; `NO_BUILD_IMPACT`
set → empty arrays), `FrameworkTests` (`arduino`, `espidf`, `native` via `extra_configs` + `extends`,
Pitfall 8), `EndToEndTests` (real `git init`, real commit, real `git diff --name-only -z`).

---

### `scripts/tests/test_docs_pins.py` (new test — replaces the deleted `test_metadata_deps.py`)

**Analog:** `test_homework_metadata.py` `SchemaShapeTest` (lines 247-268) — a read-only class that
parses committed data directly with `json`/`re`, no subprocess.

**Pin consistency.** Cross-check three sources and assert one truth:
`requirements-docs.txt` (`mkdocs==1.6.1`, `mkdocs-material==9.7.7`, `pymdown-extensions==12.3`),
the version strings named in `mkdocs.yml`, and the KaTeX directory name
(`docs/assets/vendor/katex/0.19.0/`). Note D-30 says "12.3.0" but the published artefact is
`12.3` — assert the artefact string (RESEARCH §Standard Stack).

**KaTeX vendoring (the only mechanism that catches a missing asset — Pitfall 4).** Iterate
`FILES.sha256` in `sha256sum -c` format and assert, with `hashlib.sha256`, that all 24 files
exist and match; a missing `extra_css` target produces **no MkDocs warning**.

---

## Shared Patterns

### Determinism and no clock
**Source:** `scripts/new_homework` docstring lines 52-53; `scripts/check_metadata.py` lines 28-32.
**Apply to:** every generator, `affected.py`, and every test.
> "The scaffold never invokes PlatformIO (D-22) and never reads the clock (Pitfall P10); a second
> run is byte-identical."

No `datetime.now`, no `git remote` lookup at generation time (fixture roots have no remote), no
network, no `pio` invocation from a generator.

### Exit-code vocabulary (0 / 1 / 2)
**Source:** `scripts/new_homework` docstring lines 17-26; `scripts/check_metadata.py` lines 17-26.
**Apply to:** `gen_views.py`, `affected.py`, the extended `check_metadata.py`.
Content/drift problem → 1 with a `PATH: STATUS — reason` record; usage or environment problem →
2 with `ERROR: …` on **stderr** and nothing on stdout.

### Record shape
**Source:** `scripts/check_metadata.py` `_record` (lines 54-61).
**Apply to:** all validators and generators.
```python
{"path": relative_path(root, path), "status": status, "reason": reason, "line": line}
```
Paths are repository-relative POSIX in output (`relative_path`, `contract.py:398-408`); an
out-of-root path degrades to its final component so no absolute path leaks (ASVS V5).

### Symlink-safe writes
**Source:** `scripts/new_homework` `_component_conflict` (251-295) and `_write_atomic` (424-436).
**Apply to:** every file `gen_views.py` writes. Never resolve a path before inspecting it with
`lstat`; write through a temp file in the target directory and `os.replace`.

### Single schema, single validator per document family
**Source:** `scripts/metadata/contract.py`; D-12/D-27.
**Apply to:** `boards/*.yaml`. `check_metadata.py` remains the only validator; per-family rules
live in `scripts/metadata/`, never in the entry script.

### Placeholder substitution, one pass, closed vocabulary
**Source:** `scripts/new_homework` lines 83-86, 223-238; D-19/D-20/D-33.
**Apply to:** `render.py`, every template under `templates/views/`, `gen_views.py`.
Unknown token → error; `${...}` → error; no loops; no re-scan of output.

### Test suite stays dependency-free
**Source:** `test_homework_metadata.py` docstring lines 1-18; D-14.
**Apply to:** all three new test modules.
> "no test module may import either library" (PyYAML, jsonschema)

Tests shell out to `uv run`; fixtures are built by string assembly; real-tree read-only
assertions use `git status --porcelain`.

### Escaping before Markdown
**Source:** ASVS V5 row in RESEARCH §Security Domain; D-11.
**Apply to:** README rows, site home table, homework/board pages, nav labels.
Escape `\|` in table cells; strip control characters and newlines from single-line fields; never
emit raw HTML from a metadata value. Nav entries are `- "Title": path` with an unquoted separator
colon (Pitfall 1).

---

## No Analog Found

Files with no close match in the codebase (planner should use RESEARCH.md patterns instead):

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `docs/assets/vendor/katex/0.19.0/{katex.min.js,katex.min.css,contrib/auto-render.min.js,fonts/*.woff2,LICENSE}` | vendored asset (23 files, ~600 KB) | — | The repository has no vendored third-party asset tree; the file list and sizes are in RESEARCH §KaTeX, the integrity check is `FILES.sha256` |
| `docs/assets/vendor/katex/0.19.0/render-math.js` | browser script | event-driven (`document$`) | No JavaScript exists in the repository; source is the Material math reference snippet in RESEARCH |
| `docs/assets/vendor/katex/0.19.0/FILES.sha256` | checksum ledger | — | Only `scripts/architecture/allowlist.json` shares the "committed ledger" idea; the `sha256sum -c` line format is new |
| `mkdocs.yml`, `docs/index.md`, `docs/homeworks/*.md`, `docs/boards/*.md` | site config/pages | transform | No MkDocs config or generated page exists yet; the skeleton is verified in RESEARCH and the ownership rules come from D-06/D-09/D-02 |
| `requirements-docs.txt` | pin file | — | No requirements file exists; the pin discipline is borrowed from the PEP 723 headers and the pre-commit `additional_dependencies`, not from a file analog |

## Notable gaps in the codebase (record, do not invent)

- `scripts/tests/test_metadata_deps.py` does **not** exist — it was deleted in `597bd7a`
  (RESEARCH §Summary). D-30's "extend" means **create** `test_docs_pins.py`.
- No `lib/<name>/library.json` declares `dependencies` (`lib/common/library.json`,
  `lib/port/library.json` carry only `name`, `version`, `build`). Treat a missing key as "leaf"
  and rely on the fail-safe widening rule (Pitfall 9).
- `scripts/tests/` has 81 tests today; keep the new modules inside that runtime budget by using
  `--paths-from` for `affected.py` units.

## Metadata

**Analog search scope:** `scripts/`, `templates/`, `schema/`, `docs/`, `.github/`, `.pre-commit-config.yaml`, root `README.md` / `platformio.shared.ini` / `homeworks.code-workspace` / `AGENTS.md`
**Files scanned:** 22 (all git-tracked; mirror paths excluded)
**Test baseline:** `python3 -m unittest discover -s scripts/tests` → 81 tests, OK
**Pattern extraction date:** 2026-10-25
