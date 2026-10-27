# Phase 9: Agent Workflow and Skills - Pattern Map

**Mapped:** 2026-10-26
**Files analyzed:** 40 (21 canonical skill files, 4 mirror/generator artifacts, 2 test files, 8 integration edits, 5 generated mirror placeholders)
**Analogs found:** 36 / 40

All analog paths below are git-tracked source. Verified with `git ls-files` in the
repository root; no `.gsd/capabilities/**` mirror is referenced.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/gen_skills.py` | generator / CLI | file-I/O transform (plan → classify → atomic write) | `scripts/gen_views.py` | role-match (near-exact) |
| `generated.skills.manifest` | generated data artifact | file-I/O (digest ledger) | `generated.manifest` | exact |
| `.agents/skills/**` (28 generated files) | generated artifact | file-I/O transform (frontmatter projection) | `.claude/skills/**` (source) + `generated.manifest` entry shape | role-match |
| `scripts/tests/test_gen_skills.py` | test | subprocess/CRUD over a fixture root | `scripts/tests/test_gen_views.py` | exact |
| `scripts/tests/temp_root.py` (modify) | test support utility | file-I/O fixture builder | its own `write_synthetic_root` | exact |
| `.claude/skills/new-homework/SKILL.md` | skill definition (Markdown + YAML frontmatter) | request-response (conversation contract) | `templates/task/task.md` (frontmatter) + `docs/standards/vscode.md` (prose) | partial |
| `.claude/skills/new-homework/references/question-bank.md` | reference prose | event-driven (conditional branch graph) | `docs/standards/vscode.md` | role-match (prose) |
| `.claude/skills/hw-build/SKILL.md` | skill definition | request-response (bounded retry loop) | `docs/standards/vscode.md` | partial |
| `.claude/skills/hw-build/references/repair-loop.md` | reference prose | batch (bounded loop) | `.claude/skills/new-homework/references/question-bank.md` (sibling, same phase) | role-match |
| `.claude/skills/hw-flash/SKILL.md` | skill definition | request-response with human gate | `docs/standards/vscode.md` | partial |
| `.claude/skills/{hw-report,schematic,simulate,course-index}/SKILL.md` | skill definition (stub) | request-response | `templates/task/task.md` (frontmatter) | partial |
| `.claude/skills/*/CHANGELOG.md`, `LESSONS.md` (14 files) | dated record | append-only log | `docs/decisions/README.md` (dated table rows) | role-match |
| `.claude/skills/_shared/guardrails.md` | shared policy prose | — | `AGENTS.md` §Rules (severity + enforcement annotations) | role-match |
| `.pre-commit-config.yaml` (modify) | config | check-only gate | its own `gen-views-check` block, lines 188-200 | exact |
| `.gitignore` (modify) | config | — | lines 262-265 (`*.manifest` + negation) and lines 22-31 (scoped ignore block) | exact |
| `AGENTS.md` (modify) | config / rulebook | — | lines 70-71 and line 272 (routing table) | exact |
| `.claude/CLAUDE.md` (regenerate only) | generated adapter | — | generator-owned `GSD:skills-*` block, lines 12-17 | exact |
| `docs/standards/vscode.md` (modify) | documentation | — | its own "Hooks you will meet" section, lines 152-188 | exact |
| `scripts/affected.py` (modify, optional) | config / policy tuple | — | `NO_BUILD_IMPACT`, lines 95-105 | exact |
| `scripts/tests/test_tooling_config.py` (modify, optional) | test | — | `test_..._pre_commit_hooks...`, lines 1245-1260 | exact |
| `.planning/phases/09-*/09-DRY-RUN.md` | evidence transcript | — | no analog (phase artifact; `.planning/` is authored, not generated) | none |

## Pattern Assignments

### `scripts/gen_skills.py` (generator, file-I/O transform)

**Analog:** `scripts/gen_views.py` (1134 lines, tracked)

This generator must copy the whole spine from `gen_views.py`: PEP 723 header, exit
vocabulary, plan-then-apply classification, symlink refusal, atomic writes, sorted
`PATH: STATUS — reason` emission, manifest bookkeeping. The one deliberate deviation
is that the frontmatter transform is the new work (see "No Analog Found"); everything
else is reused verbatim.

**Entry header** (lines 1-5) — keep the `uv run --script` shape, drop the PyYAML pin
because this generator is stdlib-only (RESEARCH §Standard Stack):

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
```

**Module docstring contract** (lines 6-55) — the docstring is the interface. Reproduce
the Usage block and the exit-code table, adapting owner names:

```text
Usage:
  uv run scripts/gen_skills.py [--check] [--json] [--dir PATH]

Exit codes (the vocabulary shared with `check_metadata.py`, D-23):
  0  every record is CREATE or UNCHANGED (write mode), or every record is
     UNCHANGED (check mode)
  1  a content problem on an owned file (ERROR), a stale path the manifest
     lists but no canonical file produces (ORPHAN), or, in check mode, any drift
  2  usage or environment error (bad arguments, a symlink on a target path, an
     unreadable or malformed manifest, an unknown frontmatter field, an
     unclosed frontmatter fence, a skill directory name outside the slug
     pattern, an OS-level write failure)

`--check` never writes: it classifies, emits the records and returns.
```

**Constants** (lines 84-113) — one header, one ledger, one blocking set:

```python
GENERATED_HEADER = (
    "<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->"
)
MANIFEST_PATH = "generated.skills.manifest"
BLOCKING_STATUSES = ("ERROR", "ORPHAN")
```

The mirror header is Markdown, not HTML: the constant above is the literal first line
of every generated `SKILL.md`, and `_classify_orphan` reads that first line before
deleting anything.

**Symlink refusal** (lines 315-350) — copy `_component_conflict` verbatim. It walks
each prefix with `os.lstat`, refuses a symlink at the final component and at any
intermediate component, and treats a missing component as "rest is safe to create".
This is the mitigation for the "symlink swap" threat in RESEARCH §Security Domain.

**Manifest validation** (lines 368-423) — copy `_validate_entry`'s three habits:

```python
    extra = set(entry) - allowed
    if extra:
        raise CheckError(
            f"{MANIFEST_PATH} entry for {entry['path']} has unknown keys: "
            + ", ".join(sorted(extra))
        )
```

plus the `_SHA256_HEX` regex check (line 132), the `isinstance(size, bool)` guard
(line 390, a bool is an int in Python), and the refusal to list the manifest itself
(lines 395-396).

**Target containment** (lines 353-365) — replace the single-segment `ALLOWED_FILES`
allowlist with a prefix allowlist. Both canonical and mirror targets must resolve
under `.agents/skills/`, and a skill name must match `^[a-z0-9]+(?:-[a-z0-9]+)*$`
before it becomes a path component (RESEARCH §Security Domain, V5):

```python
def _allowed_target(relative):
    """Refuse any target outside `.agents/skills/` (exit 2)."""
    path = Path(relative)
    parts = path.parts
    if (
        not parts
        or path.is_absolute()
        or ".." in parts
        or parts[:2] != (".agents", "skills")
        or not _SKILL_NAME.match(parts[2])
    ):
        raise CheckError(f"{path.as_posix()} is outside the skills mirror")
```

**Manifest entry + serialization** (lines 475-498) — reuse the exact shape, adding the
`source` key required by RESEARCH Code Example 3:

```python
def _manifest_entry(*, path, owner, source, data):
    entry = {
        "path": Path(path).as_posix(),
        "owner": owner,
        "source": Path(source).as_posix(),
        "mode": "whole",
    }
    entry["sha256"] = hashlib.sha256(data).hexdigest()
    entry["bytes"] = len(data)
    return entry


def _manifest_bytes(entries):
    ordered = sorted(entries, key=lambda item: item["path"])
    payload = {"version": 1, "entries": ordered}
    return (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
```

**Atomic write** (lines 501-512) — copy verbatim, only the temp-file prefix changes:

```python
def _write_atomic(target, data):
    descriptor, temporary = tempfile.mkstemp(
        dir=target.parent, prefix=".gen_skills-"
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
        os.replace(temporary, target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
```

**Emission** (lines 515-531) — copy `_emit` verbatim. `--json` yields
`[{path, status, reason}]` sorted by path; text mode yields
`f"{item['path']}: {item['status']} — {item['reason']}"`. The em dash is part of the
established format.

**Classification** (lines 742-875) — the mirror has only whole-file targets, so keep
the whole-file half and drop the region branch:

```python
    if not target.exists():
        status = "DELETED" if (listed and check) else "CREATE"
    elif not target.is_file():
        status = "ERROR"
    elif target.read_bytes() == data:
        status = "UNCHANGED"
    else:
        status = "MODIFIED"
```

**Orphan handling** (lines 878-941) — keep both rules: check mode reports `ORPHAN`
and writes nothing; write mode deletes only a file whose first line is
`GENERATED_HEADER`. A mirror file missing the header blocks the run.

**Planning and apply** (lines 944-1067) — keep `_build_plan` returning
`(records, writes, deletes, manifest_write)` and let `_apply` be the only writer.
`--check` returns before `_apply` (line 1119-1120); write mode refuses to apply when
any record is in `BLOCKING_STATUSES` (lines 1122-1123).

**Entry point** (lines 1070-1130) — copy the argparse shape and the `CheckError` →
stderr `ERROR:` → exit 2 boundary. Arguments are `--check`, `--json`, `--dir`; there
is no positional argument because one run owns the whole mirror:

```python
    try:
        root = resolve_root(args.dir)
        records, writes, deletes, manifest_write = _build_plan(root, args.check)
        ordered = _emit(records, args.json)
    except CheckError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
```

**Shared helpers to import, not re-implement** (lines 71-80):

```python
from scripts.metadata.errors import CheckError
from scripts.metadata.paths import resolve_root
from scripts.metadata.render import read_regular_text
```

`read_regular_text` already refuses a non-regular file; reuse it for every canonical
read. Do not import `scripts.metadata.contract` — it pulls `jsonschema`, and the hook
environment carries no dependency at all (the boundary that `ModuleBoundaryTests`
enforces for `gen_views.py`; see `scripts/tests/test_gen_views.py:263-277`).

---

### `generated.skills.manifest` (generated data artifact, digest ledger)

**Analog:** `generated.manifest`

Copy the `{"version": 1, "entries": [...]}` object, entries sorted by `path`, no
self-listing. Add `source` to each entry:

```json
{
  "path": ".agents/skills/new-homework/SKILL.md",
  "owner": "skills",
  "source": ".claude/skills/new-homework/SKILL.md",
  "mode": "whole",
  "sha256": "<64 lowercase hex>",
  "bytes": 1234
}
```

`_shared/guardrails.md` is a manifest entry too, with `owner: "skills"` and a source
under `.claude/skills/_shared/`; it is a file, not a skill (RESEARCH Pitfall 7).

---

### `.agents/skills/**` (generated mirror, frontmatter projection)

**Analog:** the canonical tree it projects, plus the entry shape above.

Every mirror file is a whole-file target. The transform is specified in RESEARCH Code
Example 2 and is *not* modelled on any existing repository file — see "No Analog
Found". Two invariants are testable and must be stated in the generator docstring:

1. Non-`SKILL.md` files (`CHANGELOG.md`, `LESSONS.md`, `references/*.md`,
   `_shared/*.md`) are byte-copied with the generated header inserted as the first
   line.
2. `SKILL.md` output is `---`, the surviving frontmatter lines verbatim, `---`, the
   generated marker, the optional invocation banner, one blank line, the untouched
   body. Never `yaml.safe_dump` (RESEARCH Pitfall 2).

The banner is mandatory whenever `disable-model-invocation: true` was dropped:

```markdown
> **Invocation:** explicit only — run `/new-homework`. Do not invoke this skill automatically.
```

---

### `scripts/tests/test_gen_skills.py` (test, subprocess over a fixture root)

**Analog:** `scripts/tests/test_gen_views.py` (994 lines, tracked)

**Module docstring and imports** (lines 1-26) — stdlib only, plus the fixture builder:

```python
"""Integration tests for scripts/gen_skills.py.

Every test drives the real generator through `uv run` against a disposable
repository root built by `scripts.tests.temp_root`, so no test module imports
PyYAML (04/D-14).
"""

from scripts.tests import temp_root

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = "scripts/gen_skills.py"
```

**Runner helper** (lines 53-66) — copy the shape, including the `uv` presence check
and the `timeout`:

```python
def run_gen_skills(*args: str, timeout: int = 180) -> subprocess.CompletedProcess:
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

**Snapshot helper** (lines 119-125) — copy `snapshot` verbatim; every "must not write"
assertion compares a before/after dict of `relative path -> bytes`.

**Module warm-up** (lines 140-146) — copy `setUpModule` so the first asserted run is
not the one paying uv's environment build.

**Test base** (lines 149-186) — copy the disposable-root pattern, swapping the fixture
builder:

```python
class SkillsTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="gen-skills-")
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)
        self.root = temp_root.write_skills_root(self.workspace / "root")

    def generate(self, *args: str) -> subprocess.CompletedProcess:
        return run_gen_skills(*args, "--dir", str(self.root))

    def assert_usage_error(self, result) -> None:
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stdout, "a usage error must print no record")
        self.assertIn("ERROR:", result.stderr)
```

**Per-concern test classes** (lines 189-475) — mirror the split. The drift tests are the
template for the three failure classes:

```python
    def test_an_edited_mirror_byte_is_modified_drift(self) -> None:
        mirror = self.root / ".agents/skills/alpha/SKILL.md"
        mirror.write_text(
            mirror.read_text(encoding="utf-8").replace("alpha", "edited"),
            encoding="utf-8",
        )
        before = snapshot(self.root)

        result = self.generate("--check")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(".agents/skills/alpha/SKILL.md: MODIFIED", result.stdout)
        self.assertEqual(before, snapshot(self.root), "--check must not write")
```

Tests the RESEARCH validation map requires (do not add a real-tree content test —
D-18 forbids it):

- strip Claude-only keys, keep the body byte-for-byte, inject the banner;
- an unknown frontmatter key exits 2 with no record;
- an unclosed fence exits 2;
- `--check` reports MODIFIED / DELETED / ORPHAN and writes nothing;
- two full runs are byte-identical;
- manifest entries are sorted, digest-correct, and never list the manifest;
- `_shared/` mirrors as files, not as a skill;
- a symlink at any component exits 2;
- one real-tree smoke: `run_gen_skills("--check")` against `REPO_ROOT` returns 0.

---

### `scripts/tests/temp_root.py` (modify: add `write_skills_root`)

**Analog:** its own `write_synthetic_root` (lines 90-202)

**Module docstring** (lines 1-17) — extend the second paragraph, keeping the
"stdlib-only, read-only with respect to the repository" contract. The new builder is
string assembly, never a copy of `.claude/skills/`, so the tests never depend on the
authored skills:

```python
def write_skills_root(base, *, source_root=None):
    """Write a small canonical skill tree at *base* and return it.

    The tree carries two skills, one reference file per skill, one `_shared`
    file, and one stub, all by string assembly, so the generator suite never
    depends on the authored `.claude/skills/` tree.
    """
    root = Path(base)
    root.mkdir(parents=True, exist_ok=True)
    ...
```

Follow the sibling's conventions: return the root, take an optional `source_root`
(never resolve git when it is absent), and create every parent with
`mkdir(parents=True, exist_ok=True)`. Keep the file PyYAML-free: write frontmatter as
plain text lines, exactly as `_write_synthetic_homework` writes `homework.yaml`
(lines 214-252).

---

### `.claude/skills/*/SKILL.md` (skill definition, request-response)

**Analog:** `templates/task/task.md` for the frontmatter fence; `docs/standards/vscode.md`
for the prose register. No existing `SKILL.md` exists in the repository.

**Frontmatter** — the implemented-skill form from RESEARCH Code Example 1:

```markdown
---
name: new-homework
description: Scaffolds a new PlatformIO homework through the repository's only supported path, then guides the user block by block from intake to report. Use when starting a new assignment, creating a homeworks directory, or asking for the guided homework workflow.
disable-model-invocation: true
metadata:
  version: "0.1"
  status: active
---
```

Rules the planner must carry into every task:

- `name` equals the directory name (`new-homework`, `hw-build`, `hw-flash`,
  `hw-report`, `schematic`, `simulate`, `course-index`).
- `version` is quoted (`"0.1"`), because `metadata` is string-to-string
  (RESEARCH Pitfall 6).
- `status` is `active` or `stub`; the four stubs use `stub`.
- Only `course-index` omits `disable-model-invocation` (D-03).
- `description` is English, one sentence of capability plus one of when-to-use.

**Body shape** — follow the register of `docs/standards/vscode.md`: an H1, short
paragraphs, imperative verbs, fenced commands with the repository-relative form
(`uv run scripts/new_homework <id> --template <name>`). Keep each body under 500 lines
and push detail into `references/` (progressive disclosure; RESEARCH §State of the
Art).

**Mandatory body fragments** shared by every implemented skill:

```markdown
Speak to the user in Ukrainian; write every repository file in English.
Read `../_shared/guardrails.md` before the first write.
```

Path validation before any command interpolation (RESEARCH Pitfall 9), using the
canonical regex from `scripts/metadata/paths.py:27`:

```text
Validate the homework id against ^[0-9]+_[0-9]+-[a-z0-9-]+$ before use and pass
it as one argv element, never through a shell string.
```

**Stub body** (D-19, RESEARCH Code Example 7) — the banner names the gap and the
manual command:

```markdown
# Simulate (stub)

> **Stub (v0.1).** This skill does not run a simulation, read serial output, or write a
> measurement-ledger row. Until it is promoted, run the documented command yourself:
> `wokwi-cli homeworks/<id> --diagram-file assets/diagram.json --scenario scenario.yaml`
> after `pio run -d homeworks/<id>`. A run consumes the Wokwi free-plan quota; simulation
> is never a build and never bench evidence.
```

---

### `.claude/skills/*/references/*.md` (reference prose, branch graph)

**Analog:** `docs/standards/vscode.md`

**Question bank ordering** (D-11/D-12) — `mode` first, then `board`, `framework`,
`language`, `specification`, `simulation`, `tests`, `deliverables`. Use H2 sections with
explicit branch sentences ("If the board is not `esp32-s3-devkitc-1`, ask for the
PlatformIO board id and record it."), never a table that reads as a form. Cover the
eight topics; coverage is review-enforced.

**Repair loop reference** (`hw-build/references/repair-loop.md`) — state the counter as
per-run, not per-error:

```text
attempt = 0
while attempt < 2:
    run pio run -d homeworks/<id>
    if exit 0: break
    diagnose the first actionable error
    make the smallest fix
    attempt += 1
if still failing: explain cause + both attempted fixes + evidence; ask for direction
```

Include the native run (`pio test -d homeworks/<id> -e native`) with the same cap, and
the F-05 note that both host fakes are reset in `setUp` and the idle button seeded HIGH.

---

### `.claude/skills/*/CHANGELOG.md` and `LESSONS.md` (dated record, append-only)

**Analog:** `docs/decisions/README.md` — dated, one-line, reason-bearing entries
(lines 11-32).

Shape to reuse (D-16/D-17, discretion grant on entry structure):

```markdown
# Changelog

## 2026-10-26 — guided dry run, 9_1-dry-run
- Added the scaffold block pause wording.
```

Each entry is dated and names the run it came from; the skill drafts it after a
completed run and writes it only after `[Записати | Не зараз]`. `LESSONS.md` uses the
same heading form and states the observation plus the rule it implies.

---

### `.claude/skills/_shared/guardrails.md` (shared policy prose)

**Analog:** `AGENTS.md` §Rules — the repository's only severity-annotated policy prose.

Reuse the annotation discipline, not the C++ rules:

```markdown
- **[MUST]** **[ENFORCED: review]** Never run `pio run -t upload` without a literal
  affirmative from the user. An empty answer, a refusal, or any other text is a stop.
```

Six sections (RESEARCH Pattern 8): flashing, commit/PR, specification versus best
practice, ambiguity, secrets, evidence. State the two non-negotiables literally:
never pre-approve `upload` in `allowed-tools`, and never record a token — only
`simulation_token_present: true|false`.

---

### `.pre-commit-config.yaml` (modify: add `gen-skills-check`)

**Analog:** the `gen-views-check` block, lines 188-200.

Copy the fields exactly, change the id, entry and `files`, and keep
`additional_dependencies` absent because the generator is stdlib-only:

```yaml
      - id: gen-skills-check
        name: generated skills mirror is in sync
        language: python
        entry: python scripts/gen_skills.py --check
        files: >-
          (?x)^(\.claude/skills/|\.agents/skills/
          |scripts/gen_skills\.py$|generated\.skills\.manifest$)
        pass_filenames: false
        stages: [pre-commit]
```

Two sibling edits in the same file:

1. `markdownlint-cli2` `exclude` (line 98) becomes
   `exclude: ^(\.planning/|\.claude/|\.agents/)` — the mirror is generated, not
   authored (RESEARCH Pitfall 4). Extend the comment at lines 87-91 to say so.
2. `no-generated-files` `entry` pathspec (lines 123-128) gains `.skill-state` so a
   `git add -f` cannot commit checkpoint state (RESEARCH Pitfall 5).

The comment block above `gen-views-check` (lines 169-187) is the documentary
precedent: explain check-only, the repair command (`uv run scripts/gen_skills.py`),
and why `files` names the generator as well as its inputs.

---

### `.gitignore` (modify)

**Analog:** lines 262-265.

The blanket `*.manifest` rule hides a second manifest, so add the negation beside the
existing one:

```gitignore
*.manifest
# D-17: `generated.manifest` is the committed ownership ledger for the
# generated views. The blanket PyInstaller rule above would otherwise hide it.
!generated.manifest
# Phase 9: the skills mirror ledger; same blanket rule, same negation.
!generated.skills.manifest
```

For `.skill-state/`, follow the scoped-block style of lines 22-31 (a comment naming
the decision, the pattern, then the order-sensitive negation where one is needed):

```gitignore
# Per-homework skill checkpoints (D-13). Untracked by design: machine-specific,
# deletable, and never a repository artifact.
.skill-state/
```

---

### `AGENTS.md` (modify)

**Analog:** lines 70-71 and line 272.

Replace the "Planned:" sentence with the live layout and the two commands:

```markdown
`.claude/skills/` — the canonical project skills; `.agents/skills/` — the generated
mirror, drift-checked by `uv run scripts/gen_skills.py --check` and the
`gen-skills-check` hook.
```

Update the routing-table row at line 272 the same way; it currently says
"(planned, Phase 9)".

---

### `.claude/CLAUDE.md` (regenerate, never hand-edit)

**Analog:** the generator-owned block at lines 12-17.

The `GSD:skills-start` / `GSD:skills-end` region is owned by
`~/.claude/gsd-core/bin/lib/profile-output.cjs` (RESEARCH §Sources). The planner must
schedule a regeneration step, not an Edit inside the markers. The regeneration
discovers `.claude/skills` and `.agents/skills` and lists each skill by name, so it is
a post-skill-tree step, and its diff is reviewed like any generated output.

---

### `docs/standards/vscode.md` (modify)

**Analog:** its own "Hooks you will meet" section, lines 152-188.

Three surgical edits, matching the existing bullet register:

1. line 154: "13 hooks" → the new count (14 on commit).
2. one bullet after `gen-views-check` (line 182):

```markdown
- `gen-skills-check` — the committed `.agents/skills/` mirror is out of sync with
  `.claude/skills/`. Run `uv run scripts/gen_skills.py`, review the diff, and commit
  the regenerated mirror.
```

3. the troubleshooting table, if it names the generator commands — add the same repair
   command beside `gen-views-check`'s.

---

### `scripts/affected.py` (modify, optional but recommended)

**Analog:** `NO_BUILD_IMPACT`, lines 95-105.

A skills-only change currently falls through to the widen-all rule and rebuilds every
project. Add two entries:

```python
    ".claude/",
    ".agents/",
```

`generated.skills.manifest` needs no entry only if `.claude/` and `.agents/` cover it —
they do not (it is a root file), so add `"generated.skills.manifest"` beside
`"generated.manifest"` at line 104. `.skill-state/` is untracked and never appears in a
diff, so it needs no entry.

---

### `scripts/tests/test_tooling_config.py` (modify, optional)

**Analog:** the stage-enumeration test at lines 1245-1260.

Add `"gen-skills-check"` to the tuple of pre-commit hook ids. It will not fail without
the edit (the test asserts only that the listed ids exist and declare the stage), but
leaving it out means the new hook escapes the stage assertion.

## Shared Patterns

### Exit vocabulary and record format
**Source:** `scripts/gen_views.py:43-54`, `scripts/new_homework:17-26`
**Apply to:** `scripts/gen_skills.py`; every command the skills document
```text
0  clean;  1  content drift or a blocked plan;  2  usage or environment error
PATH: STATUS — reason          (text mode, sorted by path)
[{path, status, reason}]       (--json mode, sorted by path)
```

### Check-only gates never write
**Source:** `.pre-commit-config.yaml:169-187` (05/D-21)
**Apply to:** `gen-skills-check`, and the skills' own use of `--dry-run`
The hook runs `--check`; the repair command is printed in the comment, never executed
by the hook. A skill that scaffolds also never repairs: it accepts `UNCHANGED`.

### Generated files are committed and drift-checked
**Source:** `generated.manifest`, `scripts/gen_views.py:84-108`
**Apply to:** `.agents/skills/**` and `generated.skills.manifest`
A hand edit is never the fix; the first line of every generated file names the repair
command; the generator deletes only a file that carries that line.

### Atomic writes and symlink refusal
**Source:** `scripts/gen_views.py:315-350`, `501-512`
**Apply to:** every mirror write and the manifest write
`lstat` every component; `mkstemp` in the target directory; `os.replace`.

### Stdlib-only tests that shell out
**Source:** `scripts/tests/test_gen_views.py:1-26`, `53-66`; `scripts/tests/temp_root.py:1-17`
**Apply to:** `test_gen_skills.py` and `write_skills_root`
No `import yaml`, no `import jsonschema`; drive the real generator through `uv run`
against a disposable root built by `temp_root`.

### Bounded automation
**Source:** `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md` (F-01, F-04, F-05),
RESEARCH Pattern 6
**Apply to:** `hw-build`, `new-homework`
Two repairs per run; accept `CREATE` or `UNCHANGED` from the scaffold; name
`UV_CACHE_DIR`; a homework-local `lib/pattern` manifest omits `frameworks`/`platforms`
and never enters `lib_deps`.

## No Analog Found

| File / concern | Role | Data Flow | Reason |
|----------------|------|-----------|--------|
| The `SKILL.md` frontmatter projection (line scanner, Claude-only key drop, banner injection) | transform logic | file-I/O | No existing file in this repository parses YAML frontmatter. Use RESEARCH Code Examples 1-2; the only repository invariant to keep is the unknown-key refusal style of `_validate_entry` (`scripts/gen_views.py:415-420`). |
| The seven skill bodies as an interaction contract (pause menus, one-concept-per-turn, checkpoint state) | skill prose | request-response / event-driven | No agent instruction files exist yet; the content is design, verified by the D-22 dry run, not by a code analog. |
| `.skill-state/<id>.json` schema | state record | file-I/O | The repository has no untracked JSON state precedent. Use RESEARCH Code Examples 4-5; the closest mechanical analog is the atomic `json.dump` write style, and `git rev-parse` must run with `check=False` (Pitfall 8). |
| `.planning/phases/09-*/09-DRY-RUN.md` transcript | evidence | — | Phase artifacts have no generator; authored Markdown outside the lint surface. |

## Metadata

**Analog search scope:** `scripts/`, `scripts/tests/`, `scripts/metadata/`, `templates/`,
`docs/standards/`, `docs/decisions/`, `.pre-commit-config.yaml`, `.gitignore`,
`AGENTS.md`, `.claude/`, `homeworks/1_3-police-flasher/`
**Files scanned:** 16 read in full or in targeted ranges; all analog paths verified with
`git ls-files`
**Pattern extraction date:** 2026-10-26
