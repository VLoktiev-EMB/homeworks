# Phase 10: Report and Evidence System - Pattern Map

**Mapped:** 2026-10-27
**Files analyzed:** 23 (9 new, 13 modified, 1 generated)
**Analogs found:** 20 / 23 (3 have no close analog: the Markdown parser, the table
parser, and the vocabulary module — each has a structural sketch in RESEARCH.md instead)

**Tracked-source gate:** every analog below is git-tracked source. Verified with
`git ls-files` for all of them; `scripts/report/` does not exist yet
(`git ls-files --error-unmatch scripts/report` → pathspec error), so no mirrored or
gitignored path is named.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/report/__init__.py` | package marker | — | `scripts/metadata/__init__.py` | exact |
| `scripts/report/vocabulary.py` | config / constants module | transform (static) | `scripts/metadata/paths.py` (literal-constant convention only) | partial |
| `scripts/report/markdown.py` | parser / utility | streaming transform | none — RESEARCH Pattern 2 sketch | none |
| `scripts/report/tables.py` | parser / utility | transform | none — RESEARCH "Cell normalization" sketch | none |
| `scripts/report/contract.py` | service (rule engine) | batch transform | `scripts/metadata/contract.py` | role-match |
| `scripts/check_report.py` | CLI entry script | file-I/O + batch | `scripts/check_metadata.py` | exact |
| `scripts/tests/test_report.py` | test | batch | `scripts/tests/test_homework_metadata.py` | exact |
| `templates/report/report.md` (rewrite) | template | — | `homeworks/1_3-police-flasher/report.md` (shape) + `templates/task/task.md` (placeholder convention) | role-match |
| `docs/standards/report.md` | doc | — | `docs/standards/vscode.md` | role-match |
| `docs/standards/electrical-calculations.md` | doc | — | `docs/standards/vscode.md` | role-match |
| `scripts/new_homework` | service (scaffold) | file-I/O + transform | itself — its `task.md` path (`:205-242`, `:386-397`) | exact (self) |
| `templates/homework-arduino/homework.yaml` | config | — | `templates/homework-espidf/homework.yaml` | exact (twin) |
| `templates/homework-espidf/homework.yaml` | config | — | `templates/homework-arduino/homework.yaml` | exact (twin) |
| `.pre-commit-config.yaml` | config | — | its own `check-metadata` block (`:171-178`) | exact (self) |
| `scripts/tests/test_new_homework.py` | test | — | itself — `SHARED_PATHS` / `assert_matches_live_template` / `ModuleBoundaryTests` | exact (self) |
| `scripts/tests/test_tooling_config.py` | test | — | itself — `:1240-1266` hook tuple | exact (self) |
| `homeworks/1_3-police-flasher/report.md` | doc / data | — | itself (retrofit) | exact (self) |
| `AGENTS.md` | doc | — | itself — quick-start `:17-25`, Rules `:100+` | exact (self) |
| `.github/pull_request_template.md` | doc | — | itself — Definition of Done | exact (self) |
| `docs/decisions/README.md` | doc | — | itself — the decision table | exact (self) |
| `.claude/skills/hw-report/SKILL.md` | doc | — | itself — stub block | exact (self) |
| `.claude/skills/hw-report/CHANGELOG.md` | doc | — | itself — dated entries | exact (self) |
| `.agents/skills/hw-report/**` | generated mirror | — | produced by `scripts/gen_skills.py` | GENERATED — never hand-edit |

---

## Pattern Assignments

### `scripts/check_report.py` (CLI entry, file-I/O + batch)

**Analog:** `scripts/check_metadata.py`

This is the single most important copy in the phase: D-04 says the CLI is a mirror, not a
redesign.

**Shebang, PEP 723 header, path bootstrap** (`check_metadata.py:1-5`, `:51`). Copy the shape
but declare **PyYAML only**; the report checker must not drag jsonschema in:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3"]
# ///
```

```python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
```

**Import block** (`check_metadata.py:53-65`). `check_metadata.py` may import the validation
stack because it declares both pins; the report checker declares **PyYAML only**, so it must
import from the leaf modules instead. `contract.py:50-51` imports `yaml` and
`Draft202012Validator` at module scope, so importing `scripts.metadata.contract` here would
drag jsonschema into the hook environment and break `python3 -m unittest discover`.

Existing shape to mirror (`check_metadata.py:53-65`):

```python
from scripts.metadata.contract import (  # noqa: E402
    CheckError, load_schema, relative_path, resolve_root,
    validate_candidate, validate_homework_text, validate_task_text,
)
```

What `scripts/check_report.py` imports instead:

```python
from scripts.metadata.errors import CheckError  # noqa: E402
from scripts.metadata.paths import relative_path, resolve_root  # noqa: E402
from scripts.metadata.yaml_loader import StrictSafeLoader  # noqa: E402
from scripts.report.contract import validate_report  # noqa: E402
```

Never `scripts.metadata.contract`. `load_schema` and the `validate_*` helpers are
deliberately absent: the report checker reads metadata values and never re-validates the
schema.

**Record helper** (`check_metadata.py:68-75`) — copy, then extend with `rule`:

```python
def _record(root, path, status, reason, line=0):
    """Render one record with a repository-relative POSIX path."""
    return {
        "path": relative_path(root, path),
        "status": status,
        "reason": reason,
        "line": line,
    }
```

**Document read** (`check_metadata.py:78-91`) — the content-vs-environment split that makes
exit 1 vs exit 2 meaningful:

```python
def _read_document(root, path):
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError as exc:
        return None, _record(root, path, "ERROR", f"document is not valid UTF-8: {exc}")
    except OSError as exc:
        raise CheckError(f"cannot read {path}: {exc}") from exc
```

**Positional handling** (`check_metadata.py:158-194`). Copy `_directories` semantics: a
positional that is a file reduces to its parent; a non-directory raises `CheckError`
(exit 2); no positionals means every direct child of `homeworks/`. For the report checker the
file case must also accept `report.md` — the reduction `candidate.parent` already does that,
because a report path is directly inside its homework directory.

**Argparse** (`check_metadata.py:308-331`) — three flags exactly: `--dir`, `--json`, variadic
`paths`.

**Output, sort, exit codes** (`check_metadata.py:350-377`):

```python
    except CheckError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    records.sort(key=lambda item: item["path"])
    violations = sum(1 for record in records if record["status"] == "ERROR")

    if args.json:
        payload = [
            {"path": record["path"], "status": record["status"], "reason": record["reason"]}
            for record in records
        ]
        print(json.dumps(payload, indent=2))
        return 1 if violations else 0

    for record in records:
        print(f"{record['path']}: {record['status']} — {record['reason']}")

    print()
    if violations:
        print(f"FAIL: {violations} metadata violation(s)")
        return 1
    print("PASS: metadata contract satisfied")
    return 0
```

**Deliberate deviations the planner must pin (RESEARCH Pattern 1, A3):**
1. Sort by `(path, line, rule)`, not by `path` alone (`check_metadata.py:354`).
2. Carry `rule` and `line` in **both** text and JSON. `check_metadata.py:357-367` drops
   `line` from the JSON payload — do **not** copy that; D-04 requires a line per ERROR.
3. Text line becomes `f"{path}:{line}: {status} [{rule}] — {reason}"`.

**No-analog risk:** none; this file is a near-copy with three named deltas.

---

### `scripts/report/__init__.py` (package marker)

**Analog:** `scripts/metadata/__init__.py`

One-line module docstring, no imports:

```python
"""Shared metadata contract for the homework checker and the scaffold."""
```

The report package's docstring names `scripts/report/` as the stdlib-only structural half.
`scripts/` itself has no `__init__.py`; namespace packages make the import work (RESEARCH
Wave 0).

---

### `scripts/report/vocabulary.py` (constants, transform)

**Analog:** `scripts/metadata/paths.py` — only for the "one literal, module-level constant,
comment naming the owning decision" convention (`paths.py:23-27`):

```python
from scripts.metadata.errors import CheckError

# The canonical homework-identifier literal. The schema's `id.pattern`, the
# backticked span in `AGENTS.md` and this constant must stay byte-identical.
HOMEWORK_ID = re.compile(r"^[0-9]+_[0-9]+-[a-z0-9-]+$")
```

**Match quality: partial.** No constants module exists yet; this file is genuinely new. Use
the RESEARCH Pattern 3 sketch as the shape (`10-RESEARCH.md:577-592`), with the literals
locked by D-06/D-07/D-08/D-10/D-34:

```python
REPORT_HEADINGS = (
    "1. Title and Metadata", "2. Objective", "3. Assumptions", "4. Theory",
    "5. Hardware and Wiring", "6. Methodology", "7. Results", "8. Analysis",
    "9. Conclusions", "10. References",
)
LEDGER_HEADER = (
    "ID", "Quantity", "Value", "Label", "Instrument", "Method",
    "Uncertainty", "Implementation commit",
)
NOT_APPLICABLE = "_Not applicable — "
EVIDENCE_LABELS = frozenset(
    {"measured", "calculated", "simulated", "datasheet", "not measured",
     "measured (observed)"}
)
```

Also host here: the report size bound (RESEARCH A4 — pick a value larger than 64 KiB or no
cap; see "Do not copy" below), the rule-id registry, and the `REPORT-01…REPORT-08`
requirement ids. Keep it stdlib-only (no imports needed).

---

### `scripts/report/markdown.py` (parser, streaming transform)

**Analog: none.** No Markdown parser exists in the tree. Use RESEARCH Pattern 2 verbatim
(`10-RESEARCH.md:542-560`):

```python
FENCE = re.compile(r"^\s*(```|~~~)")

def scan(lines):
    """Yield headings and table blocks; skip every line inside a fence."""
    in_fence = False
    for number, line in enumerate(lines, start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = ATX.match(line)          # ^(#{1,6})\s+(.*?)\s*#*\s*$
        if heading:
            yield ("heading", number, heading.group(1), heading.group(2))
            continue
        if line.lstrip().startswith("|"):
            yield ("row", number, line)
```

Load-bearing invariants from RESEARCH Pitfalls 1, 4, 6, 7:
- Enumerate the original lines once (`enumerate(lines, start=1)`); the fence state decides
  classification, never numbering.
- Build a section tree (heading → children → body line range) so every subsection
  requirement resolves against its parent section.
- Reference entries are collected **only** inside `## 10. References`; citation tokens only
  from sections 1–9 plus `## Decision Appendix`. `report.md:370` is a wrapped continuation
  line that begins `[1] `.

Import style: follow `scripts/metadata/render.py:18-24` — `from __future__ import
annotations`, stdlib only, and `from scripts.metadata.errors import CheckError` if the parser
needs a hard failure.

---

### `scripts/report/tables.py` (parser, transform)

**Analog: none.** Use the RESEARCH cell-normalization block (`10-RESEARCH.md:1356-1372`) and
Pitfall 5:

```python
_WHITESPACE = re.compile(r"\s+")

def normalize_cell(value):
    """Strip inline-code markers, unescape pipes, collapse whitespace."""
    text = value.replace("\\|", "|").replace("`", "")
    return _WHITESPACE.sub(" ", text).strip()

def normalize_platform(value):
    text = normalize_cell(value)
    if text.startswith("platformio/"):
        text = text[len("platformio/"):]
    return _WHITESPACE.sub(" ", text.replace("@", " ")).strip()
```

Split on unescaped `|` only, keep the escape in the cell until after the split, then unescape.
`report.md` today contains zero escaped pipes, so a naive split ships silently — add the
fixture even though the retrofit needs no edit (RESEARCH, "Retrofit Audit" closing note).

---

### `scripts/report/contract.py` (rule engine, batch transform)

**Analog:** `scripts/metadata/contract.py`

**Inner record factory** (`contract.py:201-207`) — the per-document record shape:

```python
    def record(status_value, reason, line=0):
        return {
            "path": display,
            "status": status_value,
            "reason": reason,
            "line": line,
        }
```

**Documented record contract** (`contract.py:487-502`):

```python
def validate_homework_text(text, *, root, path):
    """... Each record is `{"path", "status", "reason", "line"}` where `status` is
    `OK` or `ERROR`. Content problems ... are ERROR records and therefore exit 1;
    environment problems raise `CheckError` and exit 2.
    """
```

**Display path** (`contract.py:507`): `display = relative_path(root, path)`; every rule
record is emitted against that one display value.

**Lexical-first containment** (`contract.py:463-487` `_homework_directory`) — the posture for
artifact/link resolution (D-13/D-38):

```python
    parts = Path(os.path.abspath(path)).parts
    ...
    ancestor = Path(*parts[:-3])
    if ancestor != Path(root) and ancestor.resolve() != Path(root).resolve():
        return None
```

and the RESEARCH `resolve_artifact` sketch (`10-RESEARCH.md:1379-1394`) as the token-level
form. `os.path.abspath` normalizes `.`/`..` without following a symlink; a resolved
`relative_to()` is defence in depth only. This matters on macOS because
`resolve_root()` returns the resolved temp path (`/private/var/...`) while fixtures spell
`/var/...` (Pitfall 10).

**Dedupe** (`contract.py:304` `_dedupe`) — the precedent for collapsing repeated records so
one defect yields one line.

**Boundary rule (hard):** this module is stdlib-only. It must not import `yaml`,
`jsonschema`, or `scripts.metadata.contract` (RESEARCH Pattern 4 / Pitfall 9;
enforced by `scripts/tests/test_new_homework.py:676-716`). It may import
`scripts.metadata.errors`, `scripts.metadata.paths`.

**Do-not-copy items** are listed in the final section.

---

### `scripts/tests/test_report.py` (test, batch)

**Analog:** `scripts/tests/test_homework_metadata.py`

**Module docstring contract** (`test_homework_metadata.py:1-8`) — copy the intent verbatim:

```python
"""Prove the homework metadata contract end to end.

The checker is invoked as a subprocess (`uv run scripts/check_metadata.py`)
because the validator imports PyYAML and jsonschema, and D-14 keeps this suite
dependency-free: no test module may import either library. Every fixture is a
temporary root ...
"""
```

**Subprocess runner** (`test_homework_metadata.py:121-129`):

```python
def run_checker(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", str(SCRIPT), *args],
        cwd=str(cwd), capture_output=True, text=True, timeout=120, check=False,
    )
```

Rename to `run_report_checker`, and add `--help` warm-up in `setUpModule`
(`test_homework_metadata.py:147-155`) so uv's first-run install line cannot break a
determinism assertion.

**Fixture base** (`test_homework_metadata.py:199-253`):

```python
class FixtureBase(unittest.TestCase):
    """A temporary root with the schema and the shared configuration copied in."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="metadata-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        shutil.copytree(REPO_ROOT / "schema", self.root / "schema")
        shutil.copy2(REPO_ROOT / "platformio.shared.ini", self.root / "platformio.shared.ini")
    ...
    def assert_accepted(self, result):
        self.assertEqual(0, result.returncode, combined(result))
        self.assertIn(": OK — ", result.stdout)

    def assert_rejected(self, result, fragment=None):
        self.assertEqual(1, result.returncode, combined(result))
        self.assertIn(": ERROR — ", result.stdout)
        if fragment:
            self.assertIn(fragment, result.stdout)

    def assert_environment_error(self, result, fragment=None):
        self.assertEqual(2, result.returncode, combined(result))
        self.assertIn("ERROR:", result.stderr)
```

Add a `write_report(text=..., homework_yaml=...)` sibling to `write_homework` (same file,
`:220-243`). For the report suite the temp root needs `schema/` only if the checker reads
`homework.yaml` values; it must **not** re-validate the schema, so `schema/` copying is
optional but harmless.

**Fixture text by string assembly** (`test_homework_metadata.py:64-121`, the
`SCALAR_CHUNKS` / `DEFS_CHUNKS` / `document()` builder). Use the same pattern for report
fixtures: no `yaml` import, no stored golden `report.md`.

**Scaffold fixtures** reuse `scripts/tests/temp_root.py:77-99` `build_root(...)`; it already
copies `templates/`, `schema/`, `partitions/`, `scripts/pio/` and links `lib/`.

**Real-tree regression** (RESEARCH "Test Harness Conventions"): one test that
`uv run scripts/check_report.py` exits 0 and every real `report.md` yields exactly one `OK`
record.

**Import-boundary guard:** extend `ModuleBoundaryTests` (`test_new_homework.py:676-716`):

```python
    STDLIB_ONLY_MODULES = ("render", "paths", "platformio")
    PYYAML_ONLY_MODULES = ("yaml_loader",)

    def test_source_imports_are_stdlib_or_scripts(self) -> None:
        for name in self.STDLIB_ONLY_MODULES:
            with self.subTest(module=name):
                roots = _import_roots(METADATA_DIR / f"{name}.py")
                self.assertEqual(set(), roots - sys.stdlib_module_names - {"scripts"})
```

Add `scripts/report/{markdown,tables,vocabulary,contract}.py` to the stdlib-only set. The
helper is `_import_roots` at `test_new_homework.py:763-775` (AST-based, never imports the
module under test).

---

### `templates/report/report.md` (template, rewrite)

**Analog 1 (shape):** `homeworks/1_3-police-flasher/report.md`; **Analog 2 (placeholder
convention):** `templates/task/task.md`.

Current template is six lines and is replaced wholesale (`templates/report/report.md:1-6`).
The worked example supplies every literal the template must contain:

- H1 + preamble (`report.md:1-7`):

```markdown
# {{title}}

A two-LED police beacon on the ESP32-S3-DevKitC-1 with a third LED, four run-time
patterns, three run-time speeds, and a single-GPIO half-bridge profile.

## 1. Title and Metadata
```

- Section-1 `Field | Value` table (`report.md:8-20`) with the nine compared rows and the
  commit row. Pin the `Field | Value` header in `vocabulary.py` (RESEARCH Open Question 2).

```markdown
| Field | Value |
|-------|-------|
| Homework ID | `1_3-police-flasher` |
| Title | Police Flasher |
| Framework | Arduino |
| PlatformIO Core | 6.2.0 |
| Platform | `platformio/espressif32` 8.0.0 |
| Homework status | `in-progress` |
| Report status | `draft` |
| Implementation commit | `9e1238d` |
```

- Six table headers at `report.md:46-47`, `:143-144`, `:155-156`, `:176-177`, `:293-294`,
  `:335-336` (assumptions, BOM, pin map, calculations, ledger, traceability).
- Safety bullet shape (`report.md:185-199`): every bullet begins `- **` and names a hazard.
- Ledger row shape, including the `not measured:` reason prefix (`report.md:301`):

```markdown
| L-01 | Supply voltage at `3V3.1` | not measured: bench equipment offline during automated tracer run | not measured | multimeter | DC volts across `3V3.1` and `GND.1`, procedure 1 in the methodology | not applicable: no reading was taken | `9e1238d` |
```

- `Status:` paragraph (`report.md:430`) and the three `Industry note:` paragraphs
  (`report.md:389`, `:395`, `:402`).
- IEEE reference entries (`report.md:440-458`), one per blank-line-separated paragraph.

**Placeholder convention** (`templates/task/task.md:1-15`): literal `TODO` sentinels, closed
`{{name}}` tokens, no `${...}`:

```markdown
---
source_url: TODO
...
---

# {{title}}

## Task

TODO: English paraphrase of the assignment. Never the original internal material.
```

Only the six closed placeholders of D-21 are legal: `{{homework_id}}`, `{{title}}`,
`{{board}}`, `{{framework}}`, `{{platformio_version}}`, `{{platform_version}}` — exactly the
`_mapping` keys at `scripts/new_homework:232-242`. `${...}` is refused by
`scripts/metadata/render.py:39-42`.

**Hard constraint:** the template is not checked as a report (D-23); a stdlib test asserts
containment of every heading and header literal both ways.

---

### `docs/standards/report.md` and `docs/standards/electrical-calculations.md` (docs)

**Analog:** `docs/standards/vscode.md`.

Format conventions to copy from `docs/standards/vscode.md:1-40`:
- One `# ` H1, then short `## ` sections in a task order ("Before you start", "Install …").
- Prose is English, second person, one sentence per line-ish wrapped at ~100 columns.
- Commands are fenced `bash` blocks; inline paths are backticked.
- No frontmatter, no emoji.
- Linted by `markdownlint-cli2` (`.markdownlint-cli2.jsonc`), so keep one H1 and blank lines
  around headings, fenced blocks, and lists.

`report.md` additionally needs the D-25/D-43 rule-id → remediation table; model the table on
the decisions table shape (below) — `Rule | Meaning | Fix` with three columns.

---

### `scripts/new_homework` (scaffold, file-I/O + transform)

**Analog:** itself — the `task.md` composition path. This is a fixed four-point edit
(RESEARCH Pattern 5).

**Constants** (`new_homework:84-87`):

```python
MANIFEST_NAME = "template.yaml"
HOMEWORK_YAML = "homework.yaml"
TASK_MD = "task.md"
TASK_TEMPLATE = Path("templates") / "task" / TASK_MD
```

**Candidate append** (`new_homework:205-229`) — copy the symlink/missing/duplicate checks:

```python
    candidates = _template_files(template_dir)
    task_template = root / TASK_TEMPLATE
    if task_template.is_symlink():
        raise CheckError("templates/task/task.md is a symlink; refusing to follow it")
    if not task_template.is_file():
        raise CheckError("missing templates/task/task.md")
    candidates.append((Path(TASK_MD), task_template))

    seen = set()
    for relative, _ in candidates:
        if relative in seen:
            raise CheckError(f"two template entries map to the target path {relative.as_posix()}")
        seen.add(relative)
    return sorted(candidates, key=lambda item: item[0].as_posix())
```

**Render loop** (`new_homework:385-393`):

```python
        text = read_text(source, display)
        output = render(text, mapping, display)
        data = output.encode("utf-8")
```

**Required-set check** (`new_homework:395-397`):

```python
    for required in (HOMEWORK_YAML, TASK_MD):
        if required not in rendered:
            raise CheckError(f"the candidate set provides no {required}")
```

**Refactor hazard (RESEARCH Code Examples note):** the existing strings
`"templates/task/task.md is a symlink; refusing to follow it"` and
`"missing templates/task/task.md"` are asserted by tests. Generalising to a loop changes
them; move the assertions with the change rather than keeping dead literals.

---

### `templates/homework-arduino/homework.yaml` and `templates/homework-espidf/homework.yaml`

**Analog:** each other (byte-identical except `framework` and `language`). Current tail
(`templates/homework-arduino/homework.yaml:13-17`):

```yaml
tests:
  framework: unity
  native: true
  coverage: false
```

Append (D-22, matching `schema/homework.schema.json:80-91`):

```yaml
report:
  path: report.md
  status: placeholder
```

Live precedent for the block: `homeworks/1_3-police-flasher/homework.yaml:1-27`
(`report.path: report.md`, `report.status: draft`).

---

### `.pre-commit-config.yaml` (config)

**Analog:** the `check-metadata` block (`.pre-commit-config.yaml:171-178`):

```yaml
      - id: check-metadata
        name: homework metadata contract
        language: python
        additional_dependencies: ["PyYAML==6.0.3", "jsonschema==4.26.0"]
        entry: python scripts/check_metadata.py
        files: ^(homeworks/|boards/|schema/|scripts/(check_metadata\.py|new_homework$|gen_views\.py$|metadata/))
        pass_filenames: false
        stages: [pre-commit]
```

Copy with three deltas (D-05): `additional_dependencies: ["PyYAML==6.0.3"]` only, a
report-specific `files` pattern, and the `(?x)` folded form for the long pattern — the
established trick at `.pre-commit-config.yaml:204-209`:

```yaml
        files: >-
          (?x)^(homeworks/.*/(report\.md|homework\.yaml|assets/diagram\.json)$
          |templates/report/|docs/standards/(report|electrical-calculations)\.md$
          |scripts/(check_report\.py|report/))
```

Also copy the block-comment convention: the neighbouring hooks explain why the dependency set
is exactly what it is (`gen-views-check`, `:184-200`). Write the same paragraph for
`check-report`, naming the PyYAML-only boundary.

---

### `scripts/tests/test_new_homework.py` (test, modify)

**Hand-maintained path inventory** (`test_new_homework.py:40-57`):

```python
# FOUND-01: the seven shared paths plus the framework-specific entry point.
SHARED_PATHS = (
    "platformio.ini", "include/.gitkeep", "test/test_homework/test_homework.c",
    "assets/.gitkeep", "README.md", "task.md", "homework.yaml",
)

def eight_paths(template: str) -> tuple:
    """Return the eight FOUND-01 paths for *template*."""
    return (ENTRY_POINTS[template],) + SHARED_PATHS
```

Add `"report.md"` and rename `eight_paths` → `declared_paths` (RESEARCH Pitfall 13).

**Live-template parity** (`test_new_homework.py:140-177`):

```python
        expected = authored_template_files(template_dir)
        expected["task.md"] = REPO_ROOT / "templates" / "task" / "task.md"
        actual = snapshot_tree(target)

        self.assertEqual(sorted(expected), sorted(actual), "the scaffolded file set differs")
```

Add `expected["report.md"] = REPO_ROOT / "templates" / "report" / "report.md"`.

**Do not** add a stored golden `report.md`: `authored_template_files`
(`test_new_homework.py:60-88`) asserts against the live template on purpose (quick task
`261026-x78`).

---

### `scripts/tests/test_tooling_config.py` (test, modify)

**Hook tuple** (`test_tooling_config.py:1240-1266`):

```python
        for hook_id in (
            "gitleaks", "trailing-whitespace", ..., "check-metadata",
            "gen-views-check", "gen-skills-check",
        ):
            with self.subTest(hook=hook_id):
                block = _hook_block(text, hook_id)
                self.assertNotEqual("", block, hook_id)
                self.assertIn("stages: [pre-commit]", block)
                self.assertNotIn("stages: [pre-push]", block)
```

Add `"check-report"`, **and** add the closed-set assertion from RESEARCH Pitfall 12: every
`- id:` in the config appears in either the fast tuple or the push tuple
(`("clang-tidy-db", "clang-tidy")`, `:1268-1276`).

---

### `homeworks/1_3-police-flasher/report.md` (retrofit, doc/data)

**Analog:** itself. D-44's three edits, verified against the file:

1. Pin-map header, `report.md:155` — `| Signal | ESP32-S3 pin | Connects to | Notes |` →
   `| Signal | Pin | Connects to | Notes |`.
2. Add `### Next Steps` under `## 9. Conclusions`. Section 9 currently ends at the `Status:`
   paragraph (`report.md:430-437`) and `## 10. References` starts at `:439`; insert between
   them. Source the items from the `Status:` paragraph itself so no new claim is introduced
   (RESEARCH Open Question 4).
3. Three traceability rows appended as `T-18`, `T-19`, `T-20` (`:327-360` table) for
   `REPORT-01`, `REPORT-05`, `REPORT-08`. Follow the existing row grammar exactly:

```markdown
| T-07 | Bill of materials (REPORT-02) | BOM in section 5 | manual cross-check against the diagram part ids | 7 of 7 diagram ids have a BOM row | verified |
```

The new rows must carry resolvable artifacts and a non-`pending` status (RESEARCH A5), or
D-13/D-19 make the retrofit cosmetic.

Everything else passes — see the research retrofit audit table for the field-by-field
evidence.

---

### `AGENTS.md`, `.github/pull_request_template.md`, `docs/decisions/README.md`, `hw-report` skill

**`AGENTS.md`:**
- quick-start table (`:17-25`) — add a row `uv run scripts/check_report.py` beside step 4.
- Definition of Done (`:90-99`) — rewrite clause 4 from "guidance, not a merge gate" to the
  checked contract.
- Rules (`:100+`) — add a tight `### Reports and evidence` block. Copy the bullet grammar
  from `:153-157`:

```markdown
- **[MUST]** **[ENFORCED: pre-commit]** Every homework carries `homework.yaml` and `task.md`,
  validated by `scripts/check_metadata.py` against `schema/homework.schema.json`.
```

- Delete the `Planned: report structure under \`docs/standards/\` (Phase 10).` line at
  `AGENTS.md:81` (Pitfall 15 — the file is already ~303 lines).
- Routing table gains a row pointing at `docs/standards/report.md`.

**`.github/pull_request_template.md`** — Definition of Done bullet list; replace
`- [ ] The report contains the sections that apply to the assignment` with the checker
command, and add the four-item self-audit list (D-26).

**`docs/decisions/README.md`** — one row in the table (`:10-11` header), same six columns:

```markdown
| 2026-10-27 | Standalone checked report contract | one deterministic gate; prose quality stays review | high — every report and the hook follow the contract | accepted | — |
```

`Record` is `—` because D-30 forbids an ADR file.

**`.claude/skills/hw-report/SKILL.md`** — keep `metadata.status: stub`, keep
`disable-model-invocation: true`, and rewrite only the blockquote + fallback to name
`docs/standards/report.md` and `scripts/check_report.py` (D-27). Then:

```bash
uv run scripts/gen_skills.py
```

because `.agents/skills/` is generated and `gen-skills-check` is the drift gate
(`.pre-commit-config.yaml:229-239`). Add one dated `CHANGELOG.md` entry — the repository's
skill convention is one entry per change.

---

## Shared Patterns

### Record and exit-code vocabulary
**Source:** `scripts/check_metadata.py:68-91`, `:350-377`; `scripts/metadata/contract.py:201-207`
**Apply to:** `scripts/check_report.py`, `scripts/report/contract.py`
Exit 0 (`PASS`), 1 (content `ERROR` records), 2 (`CheckError` on stderr, no stdout records).
Never invent a second vocabulary.

### Path helpers
**Source:** `scripts/metadata/paths.py:30-60`
**Apply to:** `scripts/check_report.py`, `scripts/report/contract.py`, `scripts/new_homework`
```python
def resolve_root(explicit):
    if explicit:
        return Path(explicit).resolve()
    proc = subprocess.run(["git", "rev-parse", "--show-toplevel"], ...)
```
Never `Path.cwd()`; never a hand-rolled containment check.

### Strict YAML
**Source:** `scripts/metadata/yaml_loader.py:21-50`
**Apply to:** `scripts/check_report.py` only (the single PyYAML-aware module)
`StrictSafeLoader` rejects a duplicated key that `yaml.safe_load` would silently overwrite —
relevant because `report:` could be written twice.

### Closed template rendering
**Source:** `scripts/metadata/render.py:32-52`, `:65-83`
**Apply to:** `templates/report/report.md`, `scripts/new_homework`
One non-recursive `{{name}}` pass over the six-key map; `${...}` is refused; a template read
uses `read_text` / `read_regular_text` (symlink-refusing).

### Lexical containment before resolution
**Source:** `scripts/metadata/contract.py:463-487`; `scripts/check_metadata.py:197-211`
**Apply to:** artifact existence (D-13), internal links (D-38), BOM/diagram checks
`os.path.abspath` first (normalizes `.`/`..` without following a symlink), then a resolved
`relative_to()` as defence in depth. A token escaping both roots is an `ERROR`, never a
silent `False`.

### Stdlib-only module ladder
**Source:** `scripts/tests/test_new_homework.py:676-716`, `:763-775`
**Apply to:** every `scripts/report/*` module
`python3 -m unittest discover scripts/tests` runs with no third-party package installed, so
`scripts/report/*.py` may import stdlib + `scripts.metadata.{errors,paths}` only.

### Hook is check-only
**Source:** `.pre-commit-config.yaml:179-200` (the `gen-views-check` comment block)
**Apply to:** the new `check-report` hook
Never regenerate, never stage, never autofix. A failure names the repair command.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `scripts/report/markdown.py` | parser | streaming | No Markdown parser in the tree; the contract needs only ATX headings + pipe tables, which no existing module extracts. Use RESEARCH Pattern 2. |
| `scripts/report/tables.py` | parser | transform | No pipe-table parser exists; `report.md` is read as prose everywhere else. Use the RESEARCH normalization sketch. |
| `scripts/report/vocabulary.py` | constants | static | The repository has no shared-constants module; `paths.py:27` only models the one-literal convention. Use RESEARCH Pattern 3 with the D-07/D-08/D-10 literals. |

---

## Patterns That Must NOT Be Copied

| Do not copy | Source | Why |
|---|---|---|
| `MAX_INPUT_BYTES = 64 * 1024` | `scripts/metadata/contract.py:80` | The live report is 42,344 bytes / 496 lines — only ~1.5× headroom. A realistic expanded report would fail for a reason the standard never states (Pitfall 14, A4). Put a report-specific (larger or absent) bound in `vocabulary.py`. |
| JSON payload that drops `line` | `scripts/check_metadata.py:357-367` | D-04 requires a line number per ERROR; omit it from JSON and the machine contract loses the specificity the standard promises. |
| Sort by `path` only | `scripts/check_metadata.py:354` | Two errors on one report must print in reading order; sort by `(path, line, rule)`. |
| Importing `scripts.metadata.contract` from a stdlib module | `scripts/metadata/contract.py:50-51` | It pulls `yaml` **and** `jsonschema` at module scope; a `scripts/report/*` import would fail test discovery under plain `python3` (Pitfall 9). |
| Re-validating the metadata schema in the report checker | `scripts/check_metadata.py:335-336` (`load_schema`) | Duplicates work, drags jsonschema into the hook, and turns one metadata defect into two reports. Read values, do not validate the document. |
| Line-anchored `[N]` / `##` regex sweep | — | `report.md:370` starts a wrapped continuation line with `[1] `; section 6 has two fenced blocks at `:206-208` and `:217-219`; a naive scan reports seven references for six and mis-numbers every line after a fence (Pitfalls 1, 4). |
| Document-wide evidence-vocabulary scan | — | Prose at `report.md:250-255` and `:293-299` legitimately discusses `observed` and `not measured`; scope the rules to ledger `Label`/`Value` cells (Pitfall 3, D-10). |
| "Section 7 children are exactly [Ledger, Matrix]" | — | `### Interpreting the Forward-Voltage Row` sits between them (`report.md:316`); require presence, not exclusivity. Order applies only to the ten `##` headings (Pitfall 6, D-09). |
| `Path.resolve()` on a fixture root or an artifact token | — | `resolve_root()` canonicalises `/var` → `/private/var` on macOS; a resolve-first containment check fails every fixture, and a blind resolve follows a symlink out of the repo (Pitfall 10). |
| Adding `check-report` to the hook tuple only | `test_tooling_config.py:1240-1266` | Without the closed-set assertion the suite stays green while the new hook is never inspected (Pitfall 12). |
| Extending the scaffold without extending `SHARED_PATHS` | `test_new_homework.py:41-57` | Green tests that no longer assert the new path — the vacuity trap (Pitfall 13). |
| A stored golden `report.md` fixture | — | Reverses `261026-x78`; assert against the live template instead. |
| A prose/doc-sync test about the standard's wording | — | Pruned in `261026-ky7`; the only permitted text assertion is the narrow rule-id presence check (RESEARCH Open Question 3). |
| `git cat-file` reachability or external link fetching | — | Deferred by D-11/D-38; makes the hook non-deterministic and slow (Pitfall 17). |

---

## Metadata

**Analog search scope:** `scripts/`, `scripts/metadata/`, `scripts/tests/`,
`templates/`, `homeworks/1_3-police-flasher/`, `docs/standards/`, `docs/decisions/`,
`.pre-commit-config.yaml`, `.github/`, `.claude/skills/hw-report/`, `AGENTS.md`
**Files read for extraction:** 22 (all listed as analogs above; all git-tracked)
**Pattern extraction date:** 2026-10-27
