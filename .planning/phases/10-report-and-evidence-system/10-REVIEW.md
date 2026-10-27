---
phase: 10-report-and-evidence-system
reviewed: 2026-10-27T16:04:06Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - scripts/metadata/yaml_loader.py
  - scripts/check_report.py
  - scripts/report/contract.py
  - scripts/report/vocabulary.py
  - scripts/tests/test_report.py
  - scripts/tests/test_homework_metadata.py
  - docs/standards/report.md
findings:
  critical: 3
  warning: 4
  info: 3
  total: 10
status: issues_found
---

# Phase 10: Code Review Report (gap-closure re-review)

**Reviewed:** 2026-10-27T16:04:06Z
**Depth:** standard
**Files Reviewed:** 7
**Base:** `344186819035cbd053f139cd6f3a06de2208fdf4`
**Status:** issues_found

## Summary

This re-review judges the G-10-1 gap closure on its own merits, not on the plan or summary
claims. I ran the two checkers against the real tree, ran every new test on the current tree,
re-ran the new tests against an extracted copy of the base commit, and drove hostile documents
through both CLIs.

What the change actually achieves:

- **CR-01 (deep `homework.yaml`)** is closed for `StrictSafeLoader`. The `compose_node` bound
  fires on flow and block style alike (`ComposerError: nesting depth exceeds 64`, a
  `yaml.YAMLError`), and `check_report.py` additionally catches `RecursionError`. The guard is
  not bypassable through aliases (an alias does not recurse; recursive anchors construct
  lazily) or merge keys (a merge key fails earlier with a `ConstructorError`, so the
  `flatten_mapping` chain never runs). `MAX_DEPTH = 64` is safe and generous: it permits 63
  nested containers below the document root, the deepest shipped block is about four, and both
  checkers pass on the real tree.
- **CR-02 (deep `assets/diagram.json`)** is closed. `parse_diagram` catches
  `(ValueError, RecursionError)`, the deep payload becomes `RPT-207`, and the `--json` array is
  parseable.
- **CR-03 (`report.path` containment)** is closed for the vectors it tests: absolute values,
  `..` components, intermediate symlinks, final-component symlinks (`RPT-002`, unchanged) and
  absent documents all behave as documented. Windows-style separators are not a bypass: on
  POSIX a backslash is a literal filename, and on Windows `Path` splits on it, `..` is detected,
  and a drive-relative `C:foo` is caught by the lexical containment check.
- **The `RPT-001` record itself does not leak a host path.** Every refusal reason names a
  failure class only, and the record path is the repository-relative `homework.yaml`.

What it does not achieve, and what I could reproduce:

1. A `report.path` containing an embedded NUL — reachable through a YAML escape such as
   `path: "report\0.md"` — still produces an unhandled `ValueError`, a traceback and an empty
   `--json` stdout. This is the same hostile-document class G-10-1 exists to close.
2. The second YAML loader in the same repository, `StrictBaseLoader` (task.md frontmatter), was
   not given the depth bound. A ~2 KB `task.md` still crashes `check_metadata.py` with a
   `RecursionError` traceback, so the `yaml_loader.py` docstring's claim that every caller's
   `except yaml.YAMLError` suffices is false.
3. A committed symlink at `homeworks/<id>/homework.yaml` is followed, so untrusted repository
   content chooses an arbitrary host file to read; the value is echoed into stdout through
   `RPT-003`.
4. A content-controlled overlong path component turns a content problem into exit 2 and echoes
   the absolute candidate path to stderr; a symlinked `assets/` parent is followed; and the
   containment/read sequence remains a check-then-use.

Finding ids continue the phase ledger (`10-REVIEW-DISPOSITION.md`) to avoid colliding with the
prior CR-01..CR-03 / WR-01..WR-10 / IN-01..IN-09 entries. Prior open warnings were not
re-audited; only findings touched by, or directly adjacent to, this diff are listed.

## Critical Issues

### CR-04: An embedded NUL or lone surrogate in `report.path` still crashes the checker with a `ValueError` traceback

**File:** `scripts/check_report.py:200` (and `:216`, `:219`, `:233-241`, `:306`); `scripts/metadata/paths.py:56-58`

**Issue:** `_contained_report_path` only reasons about absolute paths, `..`, symlinks and
lexical containment. YAML double-quoted scalars can carry a NUL (`\0`, `\x00`) or a lone
surrogate (`\uD800`), and `Path`, `os.path.abspath` and `relative_to` accept those strings
without touching the filesystem. The first filesystem call does not:

- `path: "a\0b/report.md"` enters the parent walk and `os.lstat(current)` raises
  `ValueError: embedded null byte`. The walk catches only `FileNotFoundError` and `OSError`, so
  it escapes to `main`, which catches only `CheckError`.
- `path: "report\0.md"` has no parent component. On Python 3.13 `is_symlink()`/`is_file()`
  swallow the `ValueError` and return `False`, so the code reaches the "absent" branch and dies
  in `_record` → `relative_path` → `Path.resolve()`; on Python 3.11 it dies earlier in
  `is_symlink()`. Either way the result is the same.
- `path: "re\uD800port.md"` raises `UnicodeEncodeError` inside `os.path.realpath`
  (`UnicodeEncodeError` is a `ValueError` subclass).

Reproduced on Python 3.11 and 3.13: `exit=1`, **0 bytes on stdout**, a traceback on stderr,
and no `RPT-*` record at all. That is exactly the failure mode CR-01/CR-02 were supposed to
remove, and it violates the module docstring's "a content problem stays at exit 1 with
records" contract. It also makes behaviour version-dependent because `Path.is_file()` /
`is_symlink()` gained a `ValueError` guard in 3.13.

**Fix:** Refuse, with an `RPT-001` reason, any `report.path` the filesystem layer cannot even
represent, and make the fallible calls defensive:

```python
path = Path(value)
if "\0" in value or any(0xD800 <= ord(ch) <= 0xDFFF for ch in value):
    return None, "report.path contains a character no path may contain; it is refused"
...
try:
    mode = os.lstat(current).st_mode
except FileNotFoundError:
    return candidate, None
except (OSError, ValueError) as exc:      # ENAMETOOLONG/ELOOP and undecodable names
    return None, f"report.path cannot be inspected ({type(exc).__name__}); it is refused"
```

Also wrap the `realpath`/`resolve` calls, and make `relative_path` (`paths.py:56-60`) fall back
to a lexical name rather than calling `Path.resolve()` on a path that may be unusable. Add a
regression test for both NUL positions and for a surrogate.

### CR-05: The depth guard was not applied to `StrictBaseLoader`, so a hostile `task.md` still crashes `check_metadata.py`

**File:** `scripts/metadata/yaml_loader.py:9-14` and `:42-64`; `scripts/metadata/contract.py:103-129` and `:178-181`

**Issue:** `yaml_loader.py` states that the bound exists so that "every caller's existing
`except yaml.YAMLError` renders a content error instead of a traceback". That is true only for
`StrictSafeLoader` callers. `task.md` frontmatter is parsed by a second, independent loader,
`StrictBaseLoader` (`contract.py:103`), which has no `compose_node` bound, and
`parse_task_frontmatter` catches only `yaml.YAMLError` (`contract.py:180`). A frontmatter block
containing `title: [[[…]]]` (about 2 KB, well inside the 64 KiB cap) therefore raises
`RecursionError`, which nothing catches.

Reproduced end to end with `uv run scripts/check_metadata.py --dir <fixture> --json`:
**0 bytes on stdout**, exit 1, traceback ending at
`contract.py:179 parse_task_frontmatter` → `RecursionError`. `check_metadata.py` is a
documented Definition-of-Done gate, and its `--json` surface is the CI contract.

**Fix:** Extract the depth guard into a mixin and apply it to both loaders, for example:

```python
class _DepthBound:
    MAX_DEPTH = 64
    def __init__(self, stream):
        super().__init__(stream)
        self._node_depth = 0
    def compose_node(self, parent, index): ...   # as in StrictSafeLoader

class StrictSafeLoader(_DepthBound, yaml.SafeLoader): ...
class StrictBaseLoader(_DepthBound, yaml.BaseLoader): ...   # in contract.py
```

As defence in depth, add `RecursionError` to the `parse_task_frontmatter` handler (and to
`validate_homework_text`/`validate_board_text`). Extend `HostileNestingTests` in
`scripts/tests/test_homework_metadata.py:895` with a deep-frontmatter fixture; today the class
only writes deep `homework.yaml`, which is why this gap looks closed.

### CR-06: A symlinked `homework.yaml` is followed, letting untrusted content read an arbitrary host file and echo its values

**File:** `scripts/check_report.py:131-139` (`homework.read_text`); same pattern in `scripts/check_metadata.py:85`; prior ledger entry IN-04

**Issue:** The report document and the diagram go through `read_regular_text`, which refuses a
symlink on the final component. `_read_metadata` does not: `homework.is_file()` follows the
link and `homework.read_text` opens the target. A pull request can commit
`homeworks/<id>/homework.yaml` as a symlink to any absolute path the CI user can read, and the
checker will parse it as that homework's metadata. `scripts/gen_views.py:215-218` already
refuses a symlinked `homeworks/<id>`, so the repository's own posture is the opposite.

Reproduced: with `homework.yaml -> /tmp/…/outside.yaml`, `check_report.py` exited 0 and
accepted a placeholder declaration taken from the outside file. When the outside file declared
`status: LEAKME-SECRET`, the checker printed
`outside.yaml:0: ERROR [RPT-003] — unknown homework status 'LEAKME-SECRET'` — a concrete value
echo from a file outside the checked root. (`check_metadata.py`'s schema messages additionally
echo instance values, e.g. an `enum` failure names the offending value.) The prior review
recorded this as IN-04; the demonstrated read-through plus value echo is a security-relevant
containment gap, not a style inconsistency.

**Fix:** Read `homework.yaml` through `read_regular_text(homework, display)`, or `os.lstat` it
and refuse `S_ISLNK` before opening; return an `RPT-001` record instead of raising, so a
symlinked document is a content problem, not exit 2. Mirror the same refusal for `task.md` in
`check_metadata.py`, and add a test asserting that a symlinked metadata file is refused and its
target is never read.

## Warnings

### WR-11: A content-controlled overlong path becomes exit 2 and echoes the absolute candidate path

**File:** `scripts/check_report.py:213-220`

**Issue:** The parent walk converts every `OSError` into `CheckError`, which `main` renders on
stderr and exits 2. A `report.path` with a 300-byte component (untrusted `homework.yaml`
content) raises `ENAMETOOLONG`; reproduced:

```
ERROR: cannot inspect the declared report path: [Errno 63] File name too long:
'/private/tmp/rvw10/long.yYfgT4/homeworks/1_3-good/aaaa…'
exit=2, stdout empty
```

Two contracts break at once: "Only the environment exits 2" (this is content), and
`relative_path`'s guarantee that an absolute root is never echoed. The message interpolates
`exc`, which contains the full path. `ELOOP` is the same class.

**Fix:** Classify by `errno`: `ENAMETOOLONG`/`ELOOP` (and other failures that are a function of
the declared name) are `RPT-001` refusals with a class-only reason; keep genuine permission or
I/O failures as `CheckError`. Never put `str(exc)` into a message that reaches output — use
`exc.strerror` or the exception type name.

### WR-12: `assets/diagram.json` is read through a symlinked parent directory

**File:** `scripts/check_report.py:99-118`; `scripts/metadata/render.py:65-83`

**Issue:** `_read_diagram` reads `directory / "assets" / "diagram.json"` with
`read_regular_text`, which calls `os.lstat` on the **final component only**. A committed
`assets` symlink is an intermediate component and is therefore followed. Reproduced:
`assets -> /tmp/…/outassets` with an outside `diagram.json`; `read_regular_text` returned the
outside payload. `report.path` now gets a parent-component walk; the diagram path, which is
equally content-adjacent (a pull request can create the symlink), does not.

**Fix:** Run the fixed path through the same parent-component validation as
`_contained_report_path` (the path is constant, so a simple "every existing component must be a
real directory" walk suffices), and return `Diagram(error=…)` instead of reading through a
symlinked `assets/`.

### WR-13: Containment is check-then-use; the final open is not anchored to the inspected inode

**File:** `scripts/check_report.py:289-310`; `scripts/metadata/render.py:73-83`

**Issue:** `_contained_report_path` lstat-walks the parents, `_validate_directory` then calls
`is_symlink()` and `is_file()`, and `read_regular_text` calls `os.lstat` again before
`source.read_text(source)`. Every decision is made on a path, not on an open descriptor; a
final component (or a parent) replaced between the last `lstat` and `open` is followed. The
same window exists between the parent walk and `read_text`. The realistic threat model is a
static CI checkout, so likelihood is low, but the helper advertises containment.

**Fix:** Open with `os.open(path, os.O_RDONLY | os.O_NOFOLLOW)`, verify `os.fstat(fd)` is
`S_ISREG`, and read from the descriptor; for parents, open each directory with
`O_DIRECTORY | O_NOFOLLOW` and use `dir_fd`/`openat`. At minimum, document that the guarantee
assumes the tree is not mutated concurrently.

### WR-14: `test_hostile_inputs_are_deterministic` is vacuous for the defect it claims to cover, and the two reproduced crashes have no test

**File:** `scripts/tests/test_report.py:718-731`; `scripts/tests/test_homework_metadata.py:895-903`

**Issue:** I extracted the base commit tree, overlaid the new test files, and ran the new test
classes. Every targeted test failed as it should **except**
`test_hostile_inputs_are_deterministic`, which passed for all three fixtures against the
pre-fix code. Pre-fix, the deep-metadata and deep-diagram cases leave stdout **empty**, so
`first.stdout == second.stdout` holds while both runs are tracebacks; the test never asserts
the contract its class docstring promises ("parseable, non-empty `--json` array … no
traceback"). The other four pre-fix passes are legitimate regression/positive controls.

The same base-tree run shows the blind spots: there is no test for a NUL/surrogate
`report.path` (CR-04) and none for deep `task.md` frontmatter (CR-05), so both crashes survive
a green suite.

**Fix:** In the determinism test, assert `self.assertNotIn("Traceback", combined(first))`,
`json.loads(first.stdout)` is non-empty, and the expected rule per fixture
(`RPT-001`/`RPT-207`/`RPT-001`). Add the two missing hostile fixtures.

## Info

### IN-10: `report.path: .` is refused for the wrong stated reason

**File:** `scripts/check_report.py:233-241`

**Issue:** `Path(".").parts` is empty, so the walk is skipped and the realpath check runs on
`candidate.parent`, which is the homework directory's *parent*; the value is refused as
"resolves outside the homework directory". Refusing a directory as a document is correct, but
the reason mis-describes it.

**Fix:** Special-case an empty relative path and a value that resolves to a directory with
"report.path does not name a document".

### IN-11: `StrictSafeLoader` rejects standard YAML merge keys

**File:** `scripts/metadata/yaml_loader.py:66-86`

**Issue:** The duplicate-key loop constructs the `<<` key node before `flatten_mapping` runs.
The merge tag has no constructor, so `{<<: *anchor}` fails with
`ConstructorError: could not determine a constructor for the tag 'tag:yaml.org,2002:merge'`.
This is pre-existing (not caused by the depth guard) and it fails closed — it is actually why
merge-key chains cannot bypass the depth bound — but a legitimate document using merges is
reported as invalid YAML with a message that does not mention merges. No shipped document uses
them; document the restriction, or skip the merge tag in the duplicate-key loop and let
`flatten_mapping` handle it.

### IN-12: Duplicated hostile fixtures and JSON-contract tests

**File:** `scripts/tests/test_report.py:88` and `:92`; `scripts/tests/test_homework_metadata.py:105`; `scripts/tests/test_report.py:647` vs `:701`

**Issue:** `DEEP_YAML` is defined twice with the same literal, and
`HostileMetadataTests.test_deeply_nested_metadata_keeps_the_json_contract` largely duplicates
`HostileDocumentContractTests.test_deep_metadata_keeps_the_contract`. Low cost, but it invites
the two copies to drift.

**Fix:** Move the payload literals into one test helper module and keep a single JSON-contract
assertion per hostile fixture.

---

_Reviewed: 2026-10-27T16:04:06Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
