---
phase: 05-generated-views-and-documentation-site
reviewed: 2026-10-25T22:59:41Z
depth: standard
files_reviewed: 43
files_reviewed_list:
  - .github/workflows/docs.yml
  - .github/workflows/generated-views.yml
  - .gitignore
  - .pre-commit-config.yaml
  - AGENTS.md
  - README.md
  - boards/esp32-s3-devkitc-1.yaml
  - docs/boards/esp32-s3-devkitc-1.md
  - docs/homeworks/1_3-police-flasher.md
  - docs/index.md
  - generated.manifest
  - homeworks.code-workspace
  - mkdocs.yml
  - platformio.shared.ini
  - requirements-docs.txt
  - schema/board-profile.schema.json
  - scripts/affected.py
  - scripts/check_architecture.py
  - scripts/check_metadata.py
  - scripts/ci/check_lfs_pointers.sh
  - scripts/gen_views.py
  - scripts/metadata/board_profile.py
  - scripts/metadata/contract.py
  - scripts/metadata/errors.py
  - scripts/metadata/paths.py
  - scripts/metadata/platformio.py
  - scripts/metadata/render.py
  - scripts/metadata/yaml_loader.py
  - scripts/new_homework
  - scripts/tests/temp_root.py
  - scripts/tests/test_affected.py
  - scripts/tests/test_ci_workflows.py
  - scripts/tests/test_docs_pins.py
  - scripts/tests/test_gen_views.py
  - scripts/tests/test_homework_metadata.py
  - scripts/tests/test_new_homework.py
  - scripts/tests/test_platformio_readers.py
  - templates/views/board-page.md.tmpl
  - templates/views/homework-page.md.tmpl
  - templates/views/homeworks-table.md.tmpl
  - templates/views/mkdocs.yml.tmpl
  - templates/views/shared-ini.ini.tmpl
  - templates/views/workspace.json.tmpl
findings:
  critical: 2
  warning: 14
  info: 8
  total: 24
status: issues_found
---

# Phase 5: Code Review Report

**Reviewed:** 2026-10-25T22:59:41Z
**Depth:** standard
**Files Reviewed:** 43
**Status:** issues_found

## Summary

The phase is materially sound: the 27 vendored KaTeX files were excluded as directed, the
committed `generated.manifest` digests were independently recomputed and match every owned
byte, `uv run scripts/gen_views.py --all --check` on the real tree reports eight UNCHANGED
records and exits 0, and the committed `mkdocs.yml` parses. The generator's plan/apply
classifier, target allowlist, component-level symlink walk, atomic writes and the
`paths.py`/`yaml_loader.py` import split hold up.

The defects below are in the edges the implementation itself claims to defend: metadata that
reaches the generated Markdown without HTML escaping (the published site renders raw HTML),
symlinked inputs the generator follows even though it refuses symlinks everywhere else, and
several false-positive/exit-code/CI-gate gaps in the supporting checks. Findings marked
"verified" were reproduced against a disposable fixture root or against Python-Markdown
3.9; the real tree was never modified.

## Narrative Findings (AI reviewer)

### Critical Issues

#### CR-01: Metadata reaches the published site as raw HTML — stored XSS via `title`, and unvalidated `report.path` breaks the link destination

**File:** `scripts/gen_views.py:149-160` (also `257-281`, `765-773`, `789-808`, `939-951`)
**Issue:** `_escape_cell` neutralizes control characters, `|`, `[` and `]` only. It never
escapes `<`, `>` or `&`, and `report.path` is interpolated into a Markdown link destination
without any escaping or validation. `schema/homework.schema.json` puts no character
restriction on `title` (`minLength: 1` only), and the only CI job that reads
`homework.yaml` (`generated-views.yml`) installs PyYAML only — it never runs
`check_metadata.py`. A title of `<img src=x onerror=alert(1)>` is therefore emitted verbatim
into `docs/homeworks/<id>.md`, `docs/index.md` and `README.md`. MkDocs/Python-Markdown 3.x
has no safe mode; rendering the generated Markdown with the `tables` extension (verified)
produces:

```html
<td><img src=x onerror=alert(1)></td>
```

so the published GitHub Pages site executes attacker-controlled script (stored XSS). The
same applies to `frameworks`/`soc`/`psram` on the board page (`_render_board_page` checks
only that `frameworks` is a list of non-empty strings). `report.path` (schema-constrained but
not validated here) is placed inside `[report](...)` and `- [Report](...)`; a value
containing `)` or `]` closes the destination/label early.

**Fix:**
```python
def _escape_cell(value):
    text = "" if value is None else str(value)
    text = _CONTROL.sub(" ", text).strip()
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return text.replace("\\", "\\\\").replace("|", "\\|") \
               .replace("[", "\\[").replace("]", "\\]")
```
Also validate `report.path` against the schema pattern (or percent-encode it) before building
a URL, and add a `title` pattern (`^[^<>]*$`) to the schema as defense in depth. Running the
metadata checker in the same CI job helps but must not be the only defense (the generator's
own T-5-33 rule).

#### CR-02: The generator follows symlinked `homework.yaml` and view templates, unlike every other input it guards

**File:** `scripts/gen_views.py:203` and `scripts/gen_views.py:532` (same read at `611`,
`692`, `787`, `930`, `976`, `1128`)
**Issue:** `gen_views` refuses a symlinked `homeworks/` directory, a symlinked homework
directory, `boards/`, each board file, `docs/decisions/`, each decision file and every target
component — but it reads `homeworks/<id>/homework.yaml` through `render.read_text`, which
follows a symlink, and it reads every `templates/views/*.tmpl` the same way. Verified in a
disposable root:

- `homeworks/1_3-alpha/homework.yaml -> <external>.yaml` (title `LEAKED-TITLE`) rendered
  `| 1.3 | [1.3 LEAKED-TITLE](homeworks/1_3-alpha/) | ... |` and exited 0.
- `templates/views/homeworks-table.md.tmpl -> <external file>` wrote that file's bytes into
  the README region and exited 0.

Git stores symlink targets verbatim, including absolute paths. A pull request can therefore
make the documented local repair `uv run scripts/gen_views.py --all` read an arbitrary local
file (YAML/UTF-8) and copy it into a generated, committable artifact. `scripts/new_homework`
already lstat-checks its template entries (T-04-03), so this is an inconsistency in the
generator, not a design choice.

**Fix:** lstat the file and raise `CheckError` before reading it (or give `read_text` a
`refuse_symlink=True` argument used by every generator call site), matching
`_load_boards` and `_decision_nav_entries`.

### Warnings

#### WR-01: `_escape_cell` does not escape backslashes, so its own escaping can be defeated

**File:** `scripts/gen_views.py:149-160`
**Issue:** Because `\` is left untouched, a metadata value containing a literal backslash
immediately before a pipe or a structural bracket defeats the escape. Verified: a title
containing `\|` produces the cell text `\\|`; Python-Markdown renders that as an escaped
backslash followed by a column separator, splitting the cell into two (`x \` + `y`). A title
ending in `\` turns the structural `]` of the link label into `\]`, so the label never
closes and the link is broken. The docstring claims a pipe or bracket "cannot break the
card", which is not true for this input class.
**Fix:** escape the backslash first, before `|`, `[` and `]` (see CR-01's snippet).

#### WR-02: `_nav_label` is not a YAML double-quoted-scalar encoder — a title/heading with `\` or a newline emits an invalid `mkdocs.yml`

**File:** `scripts/gen_views.py:1009-1017` (used at `1052` and `1112`)
**Issue:** The label is placed inside a double-quoted YAML scalar, where `\` starts an escape
sequence and a newline ends the scalar. `_nav_label` only replaces `"` with `'`. Verified: a
homework title `Alpha \q` produced

```yaml
    - "1.3 Alpha \q": homeworks/1_3-alpha.md
```

`PyYAML` then fails with `found unknown escape character 'q'`. `gen_views.py` exited 0 and
committed the broken config; `nav --check` cannot catch it because it compares bytes, not
YAML validity. A YAML block-scalar title (`title: |`) or a decision heading containing a
newline/control character produces a multi-line entry. The unquoted nav *path* has the same
weakness for a decision filename containing `: ` or ` #`.
**Fix:** use `json.dumps(label)` (a JSON string is a valid YAML double-quoted scalar) and
`json.dumps(path)`, or escape `\`, `"`, control characters and newlines explicitly.

#### WR-03: A deleted generated whole file is unrecoverable — `DELETED` blocks every run and the manifest keeps listing it

**File:** `scripts/gen_views.py:1242-1258` (and `BLOCKING_STATUSES` at `120`)
**Issue:** When a manifest-listed whole-file target is absent, `_classify_produced` returns
`DELETED` with no payload. `main` treats `DELETED` as blocking and returns 1 before `_apply`,
while `new_entries` still includes the produced entry, so the manifest is reported UNCHANGED
and keeps the absent path. Verified against a fixture: after `gen_views --all`, deleting
`docs/homeworks/1_3-alpha.md` makes every subsequent `--all` print
`docs/homeworks/1_3-alpha.md: DELETED — manifest-listed file is absent on disk`, exit 1, and
never recreate the file; `--all --check` exits 1 forever. This contradicts `AGENTS.md:49`
("the fix is `uv run scripts/gen_views.py --all`, never a hand edit"), which cannot repair
this failure mode. Only hand-editing or deleting the committed manifest recovers.
**Fix:** for a whole-file target that a selected view still produces, absent-on-disk must be
`CREATE` with the rendered payload. `ORPHAN`/`DELETE` already covers a path that no selected
view produces, so `DELETED` is redundant; remove it or reserve it for an explicitly retired
target.

#### WR-04: Board positionals are misclassified whenever the root spelling differs from the resolved root

**File:** `scripts/check_metadata.py:214-236` (and `_relative_lexical` at `197-211`)
**Issue:** `_partition_paths` compares `boards = root / "boards"` (where `root` is the
canonical, resolved root) against `Path(os.path.abspath(candidate)).parents` (which does not
resolve symlinks). Whenever the caller's spelling differs from the resolved spelling — macOS
`/var` vs `/private/var`, or any symlinked workspace/alias — an absolute board positional is
not recognized as a board path and falls through to the homework family. Verified:

```
$ check_metadata.py --dir <tmp>/real boards/esp32-s3-devkitc-1.yaml
boards/esp32-s3-devkitc-1.yaml: OK — board profile contract satisfied

$ check_metadata.py --dir <tmp>/real <tmp>/real/boards/esp32-s3-devkitc-1.yaml
boards: ERROR — directory contains neither homework.yaml nor task.md
```

The same mismatch makes `_relative_lexical` degrade a refused symlinked board document's
record to a bare filename (losing the `boards/` prefix) in strict mode. The homework family
is unaffected because it is the fallback.
**Fix:** reconcile only the ancestor prefix through `resolve()` (the pattern already used by
`contract._homework_directory`, T-04-29/30): split the lexical parts, verify the ancestor of
`boards/<file>` resolves to `(root / "boards").resolve()`, and keep the final filename
lexical so a symlinked document is still classified as a board path.

#### WR-05: The architecture gate never loads `extra_configs`, so an inherited `platform = native` is "unset" and produces false violations

**File:** `scripts/check_architecture.py:438-454` (`check_platformio`)
**Issue:** `load_ini(ini, relative)` is called without `preload_extra_configs`, unlike
`affected._project_record`. `option(..., "platform")` therefore cannot see a platform
inherited from `../../platformio.shared.ini` unless the `extends` target happens to start
with `native`. Verified with a fixture where `[shared_native] platform = native` lives in
the extra config and `[env:integration_test] extends = shared_native` lists `host`:

```
violations WITHOUT preload: [{'area': 'config', ... "[env:integration_test] lists 'host' in a non-native environment (platform = unset)"}]
platform WITH preload: 'native'
```

With the preload the environment is native and the test-environment exemption applies. This
is a false positive that blocks a valid host build, and a divergence from the mapper that
D-23 says must not exist.
**Fix:** call `preload_extra_configs(parser, project, relative)` immediately after
`load_ini`, then add `platformio.shared.ini` to the hook's `files` pattern (see WR-06) so an
edit to the shared pin re-runs the gate.

#### WR-06: The `check-architecture` pre-commit hook does not trigger on the shared INI reader it now depends on

**File:** `.pre-commit-config.yaml:62-67`
**Issue:** The hook's `files` regex is
`^(lib/|homeworks/|scripts/architecture/|scripts/check_architecture\.py)`. Since 05-01 moved
`option`, `dep_names`, `load_ini` and `extends_targets` into
`scripts/metadata/platformio.py`, a commit that edits only that file skips the architecture
gate on a normal `git commit`. (`pre-commit run --all-files` masks the gap because it runs
every hook, which is why the current tree appears green.) A change to the reader can
therefore silently change the dependency verdict.
**Fix:** extend the regex with `scripts/metadata/` (and `platformio\.shared\.ini$` once
WR-05 is fixed). The two sibling hooks already name `scripts/metadata/`.

#### WR-07: The LFS-pointer guard exits 0 when it could not scan the tree

**File:** `scripts/ci/check_lfs_pointers.sh:30-38`
**Issue:** `find` runs in a process substitution and its status is discarded, and `grep`'s
status is only tested as "matched / did not match" (`if grep -qF`), so exit 2 (I/O error) is
treated as "no pointer". Verified: a pointer file inside a `chmod 000` subdirectory is not
found; `find` prints `Permission denied` and the guard exits 0, while the same tree with the
directory readable exits 1. A guard whose purpose is to prove absence must fail when it
cannot read part of the tree.
**Fix:** materialise the file list (or use `set -o pipefail` with a pipeline) and treat a
non-zero `find` as exit 2; in the loop, distinguish `grep` exit 1 (no match) from exit >1
(error → exit 2).

#### WR-08: An empty `platform =` in the shared INI is reported as homework content violations instead of an environment error

**File:** `scripts/metadata/contract.py:378-388`
**Issue:** `read_shared_platform_pin` uses `has_option`, so `platform =` (empty) is present;
both sections then "agree" on `""`, `len(set(pins.values())) == 1`, and the function returns
`""`. `validate_homework_text` compares each homework's real pin against `""` and emits an
`ERROR` record per homework (exit 1), although the module docstring promises that a missing
pin is a repository-environment failure (exit 2). The exit-code split is a CI contract.
**Fix:** strip the value and raise `CheckError` when it is empty.

#### WR-09: `new_homework` parses `template.yaml` with `yaml.safe_load`, silently keeping the last duplicate key

**File:** `scripts/new_homework:133`
**Issue:** Every other metadata reader uses `StrictSafeLoader` (T-04-20/D-33), but the
template manifest uses `yaml.safe_load`. A duplicated `framework:` (a realistic bad-merge
shape) silently selects the last value and scaffolds a homework with the wrong framework;
nothing in the plan reports it.
**Fix:** `yaml.load(text, Loader=StrictSafeLoader)` and wrap `yaml.YAMLError` as today.

#### WR-10: A complete project with no `[env:]` section silently contributes nothing to the build matrix

**File:** `scripts/affected.py:279-302` (`_project_record`)
**Issue:** A `platformio.ini` with only `[platformio]` (or no `env:` sections) yields
`envs: []`, `incomplete: False`. If a diff selects that project, `_entries` emits no `build`
or `simulate` entry and `main` returns 0, so CI builds nothing for a project the matrix
claims to cover. `_has_homework_content` already treats a project without an INI as a
content problem; the zero-environment case is silent.
**Fix:** report an error record (exit 1) when a complete, selected project resolves zero
environments, naming the INI.

#### WR-11: `_pinout_link` validates only `|`, `<` and `>`; other Markdown-breaking characters still pass

**File:** `scripts/gen_views.py:906-921`
**Issue:** `pinout_url` is only checked against `^https://[^\s]+$` plus `|<>`. The schema
pattern permits `(`, `)`, `[`, `]` and `\`. An unmatched `)` closes the Markdown destination
early, leaking the remainder into the cell as text; `[`/`]` can open or close a link/label.
This is the same failure class T-5-19 claims to close.
**Fix:** percent-encode (or refuse) `()[]\` in the URL before emitting `[Official pinout](…)`.

#### WR-12: `_write_atomic` replaces every generated file with a 0600-mode temp file

**File:** `scripts/gen_views.py:495-506` and `scripts/new_homework:392-403`
**Issue:** `tempfile.mkstemp` creates the temporary file with mode 0600, and `os.replace`
discards the destination's mode. Verified: a `README.md` at 0644 becomes 0600 after a
write-mode `gen_views readme` run. Every regeneration (the documented repair path) silently
strips group/other read permission from the committed generated files; scaffolded homework
files are created owner-only as well.
**Fix:** `os.chmod(temporary, 0o666 & ~current_umask)` before `os.replace`, or copy the
existing target's mode when it exists.

#### WR-13: No pull request proves the site builds, and the Python test suite never runs in CI

**File:** `.github/workflows/generated-views.yml:39-44` and `.github/workflows/docs.yml:8-11,55-60`
**Issue:** `generated-views.yml` runs only `python scripts/gen_views.py --all --check`.
`docs.yml` runs `mkdocs build --strict` only on `push` to `main`; the other workflows run
PlatformIO/`gitleaks` only. Consequences: (a) WR-02's invalid `mkdocs.yml` merges green and
fails only after merge; (b) `scripts/tests/test_docs_pins.py` — described in its own
docstring as the only mechanism that can catch a missing/flipped KaTeX byte, because
`mkdocs build --strict` passes silently on a missing asset — never executes in CI, so a
corrupted vendor tree can be published; (c) the nav-coverage check in that module is also
local-only.
**Fix:** add a read-only job (or step) to the PR workflow that installs
`requirements-docs.txt`, runs `mkdocs build --strict`, and runs the stdlib-only tests
(`python -m unittest scripts.tests.test_docs_pins scripts.tests.test_ci_workflows
scripts.tests.test_platformio_readers`).

#### WR-14: Blocking-token detection is a raw substring match, so unrelated identifiers are flagged

**File:** `scripts/check_architecture.py:409-410` (`scan_blocking`)
**Issue:** `if token in line` means `device_sleep(`, `get_millis(` and `my_delay(` all match
`sleep(`, `millis(` and `delay(`. A non-blocking function whose name merely ends in one of
the tokens is reported as a violation and blocks the change.
**Fix:** anchor each token at an identifier boundary, e.g.
`re.search(r"(?<![A-Za-z0-9_])" + re.escape(token), line)`.

### Info

#### IN-01: Dead module constants in `gen_views.py`

**File:** `scripts/gen_views.py:86,122-123`
**Issue:** `SITE_URL`, `TABLE_HEADER` and `TABLE_SEPARATOR` are never referenced. The table
header/separator actually live in `templates/views/homeworks-table.md.tmpl`, and the tests
define their own copies. The unused constants invite a future edit that changes nothing.
**Fix:** remove them, or use them to assert that the reviewed template still starts with the
expected six-column header.

#### IN-02: The Core-pin reader is dead production code and the scaffold pin is a hardcoded duplicate

**File:** `scripts/metadata/contract.py:83,391-416`; `scripts/new_homework:214`
**Issue:** `read_shared_core_pin` is called only by tests; `validate_homework_text` never
cross-checks `toolchain.platformio` against the generated `; PlatformIO Core:` header, and
the scaffold writes the hardcoded `PLATFORMIO_CORE = "6.2.0"`. The "one pin, declared in
three places" invariant is enforced only indirectly through the shared-ini pair check.
**Fix:** wire `read_shared_core_pin` into `validate_homework_text` (now that the shared INI is
generated) or delete it; drive the scaffold's pin from `platformio.shared.ini`.

#### IN-03: Manifest entries with an unknown `owner` are never cleaned up

**File:** `scripts/gen_views.py:362-417` (`_validate_entry`) and `1494-1524`
**Issue:** `_validate_entry` accepts any non-empty `owner`; `_build_plan` preserves entries
whose owner is not among the selected views, and no view can ever be selected for an unknown
owner. A renamed/removed view (or a typo) leaves its targets in the manifest forever with
stale digests, and `--all --check` reports UNCHANGED.
**Fix:** require `owner in VIEWS` in `_validate_entry`, or treat an unknown owner as an
`ORPHAN` during `--all`.

#### IN-04: A stray file listed in the manifest under another owner escapes both the orphan scan and the produced set

**File:** `scripts/gen_views.py:1388-1395` (`_scan_orphans`)
**Issue:** `listed` is built from *every* manifest entry regardless of owner, while the
orphan pass only considers entries whose owner is selected. A stray page the manifest lists
under a different owner is skipped by the directory scan and is not produced by the selected
view, so it persists with no record at all.
**Fix:** build `listed` from entries whose `owner` is in `selected_owners`, or include the
mismatch as an `ORPHAN`.

#### IN-05: `check_metadata` follows symlinked homework directories/documents while the rest of the tooling refuses them

**File:** `scripts/check_metadata.py:78-91,158-194`
**Issue:** `_directories` uses `is_dir()`/`is_file()` and `_read_document` uses
`read_text()`; a symlinked `homeworks/` or `homeworks/<id>/homework.yaml` is followed and
validated. The board family (`_board_documents`) refuses symlinked documents, `gen_views`
refuses symlinked homework directories, and CR-02 flags the generator's file-level gap.
Since the checker is read-only the impact is low, but the posture should be consistent and
documented.
**Fix:** lstat the directory and the two contract files, or explicitly document that the
checker intentionally validates a symlink's target.

#### IN-06: The scaffold hardcodes a board id without checking the profile exists

**File:** `scripts/new_homework:90,206-216`
**Issue:** `BOARD = "esp32-s3-devkitc-1"` is unconditional, and nothing verifies that
`boards/esp32-s3-devkitc-1.yaml` exists or that the profile is valid. A scaffolded homework
can reference a board with no profile; `gen_views` will still render its page (it does not
run the schema).
**Fix:** verify the board profile exists (and, ideally, read the id from a single validated
source) before writing the candidate.

#### IN-07: `load_allowlist` ignores unknown keys in an allowlist entry

**File:** `scripts/check_architecture.py:525-544`
**Issue:** The validator checks `path`, `rule` and `reason` and silently drops every other
key. A typo (`"rules"` instead of `"rule"`) makes the entry stale rather than reporting a
schema error, and extra keys pass unnoticed; `gen_views._validate_entry` rejects extra keys,
so the two validators disagree.
**Fix:** reject `set(entry) - {"path", "rule", "reason"}` as an environment error.

#### IN-08: `AGENTS.md` does not describe the new local gate or run the Python test suite

**File:** `AGENTS.md:22-23,47-49,65-73`
**Issue:** The quick-start table still describes `pre-commit run --all-files` as running
"hygiene, large files, secrets, the dependency rule, and the metadata contract"; it now also
runs `gen-views-check`. The quick-start, the Definition of Done and the routing table never
run `scripts/tests/` (the Python suite that owns the KaTeX integrity, nav-coverage, generator
and mapper tests), so those gates are local-only (see WR-13). The layout paragraph's claim
that the fix for drift is always `gen_views --all` is false for the `DELETED` case (WR-03).
**Fix:** add `gen-views-check` to the step-3 description, add the test suite to the
quick-start/DoD (and CI), and qualify the drift-repair sentence.

---

_Reviewed: 2026-10-25T22:59:41Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
