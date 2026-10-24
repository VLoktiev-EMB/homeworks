---
phase: 04-metadata-contract-and-scaffolding
reviewed: 2026-10-24T22:42:44Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - scripts/metadata/contract.py
  - scripts/tests/test_homework_metadata.py
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
---

# Phase 04: Code Review Report (incremental — plan 04-09 delta)

**Reviewed:** 2026-10-24T22:42:44Z
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

> **Scope.** This report reviews only the plan-04-09 gap-closure delta
> (`131a673`, `9e33238`, `9312ec3`, plus the `c54ad8c` plan-metadata commit)
> against `d6fa103`, the commit that holds the prior full-phase review. That
> prior review is dispositioned in `04-REVIEW-DISPOSITION.md`; its findings are
> not re-litigated here. WR-10 of that review (root-spelling skip) is **closed**
> by this delta, and WR-08 (allowlist test without Cyrillic) is **closed** by
> the strengthened test. WR-07 (TOCTOU), WR-11 (`relative_path` resolves),
> WR-09, WR-12–WR-14 and the Info items remain open and are outside this delta.

## Summary

The delta rewrites `_homework_directory` from a lexical prefix comparison to a
structural guard plus ancestor-only resolution, and adds three CLI-driven
`IdentityTests` regressions plus a strengthened WR-08 assertion. The core claim
holds: a mismatched `id` is now rejected for an explicit absolute positional
under a differing root spelling, a matching `id` is still accepted under that
spelling, and the symlinked-`homeworks` protection still fires beneath it. I
re-ran the delivered gates on this machine rather than trusting the SUMMARY:

- `python3 -m unittest scripts.tests.test_homework_metadata
  scripts.tests.test_new_homework.ErrorTests.test_mismatched_rendered_id_is_error`
  → `Ran 61 tests ... OK`.
- Direct CLI probes on disposable roots for: canonical spelling, `/tmp` vs
  `/private/tmp` spelling, alias root, symlinked `homeworks` base, symlinked
  base under an alias root, and the matching-`id` control. All behave as the
  plan's must-have truths state.

The new helper is materially better than what it replaced and I found no
regression against the symlinked-base protection. It is, however, not the
"cannot be silently disabled" guarantee its own docstring now asserts. Three
spellings/shapes still make the helper return `None`, and both callers treat
`None` as "identity not applicable" rather than as an error: a case-only
spelling of the `homeworks` component (reachable on the default macOS
filesystem, where this repository is developed), any explicitly named document
that is not exactly `<root>/homeworks/<dir>/homework.yaml` (for example
`homeworks/<sub>/<dir>` or a directory outside the root), and a symlinked
`homeworks/<dir>` whose link name — not its real directory — is what the
identity check compares. The first is the same *class* of defect as the row-10
gap this delta closes, one path component over; the other two are pre-existing
but are now documented as a lexical guarantee that they do not actually provide.

No BLOCKER (critical) finding: the default scan used by the pre-commit hook and
by CI constructs paths from `<resolved root>/homeworks` and cannot reach any of
the three holes without a caller-supplied positional path.

## Warnings

### WR-01: A case-only spelling of the `homeworks` component still silently skips the `id` invariant — WARNING

**File:** `scripts/metadata/contract.py:598-600`

**Issue:** The guard compares `parts[-3]` to the literal `"homeworks"` with
Python's case-sensitive `==`. On the default APFS filesystem (this repository's
development platform) `HomeWorks` and `homeworks` name the same directory, so
the document is read and validated while `_homework_directory` returns `None`
and the `id`-equals-directory rule is skipped. This is the same failure mode as
the closed row-10/WR-10 gap — a caller-chosen spelling that silently disables
the invariant — reached through a different component: WR-10 fixed the ancestor
prefix, but the `homeworks` component itself is still compared textually.

**Reproduced** (fixture root with `homeworks/1_3-good/homework.yaml` whose `id`
is `1_3-other`):

```text
$ uv run scripts/check_metadata.py --dir <root> <root>/homeworks/1_3-good/homework.yaml
homeworks/1_3-good/homework.yaml: ERROR — id: '1_3-other' does not match the containing directory '1_3-good'
EXIT=1

$ uv run scripts/check_metadata.py --dir <root> <root>/HomeWorks/1_3-good/homework.yaml
HomeWorks/1_3-good/homework.yaml: OK — metadata contract satisfied
PASS: metadata contract satisfied
EXIT=0

$ uv run scripts/check_metadata.py --dir <root> HomeWorks/1_3-good
... PASS: metadata contract satisfied
EXIT=0
```

Both are the identical file; only the spelling of the component changed. Note
that the module docstring at `contract.py:590-593` claims "the id-equals-
directory rule cannot be silently disabled", which this contradicts.

**Fix:** establish that the component *names* `<root>/homeworks` instead of
comparing its letters, without touching the tail:

```python
ancestor = Path(*parts[:-3])
if ancestor != Path(root) and ancestor.resolve() != Path(root).resolve():
    return None
homeworks_component = ancestor / parts[-3]
if homeworks_component.exists():
    if not os.path.samefile(homeworks_component, Path(root) / "homeworks"):
        return None
elif parts[-3] != "homeworks":      # scaffold target not created yet
    return None
return parts[-2]
```

`os.path.samefile` follows the link only for the `homeworks` component, which
is exactly the pre-04-08 behaviour that erased the tail from the *comparison
input*; the returned name stays lexical, so the symlinked-base protection is
unchanged (verified: `homeworks -> outside` still yields the identity ERROR).
The `exists()` branch is needed because `validate_candidate` runs before the
scaffold creates `homeworks/`. Because the plan's prohibition forbids resolving
the `homeworks` component, adopting this needs an explicit plan amendment
rather than a silent edit. A test must pin the `HomeWorks` spelling (it needs a
case-insensitive filesystem, so guard it with a skip when the spelling does not
resolve).

### WR-02: `None` conflates "not a homework document" with "identity not checked", so a nested or out-of-root positional validates with no `id` check — WARNING

**File:** `scripts/metadata/contract.py:598-604`; caller `scripts/check_metadata.py:147-182` (`_directories`)

**Issue:** The helper returns `None` for every path whose last three components
are not exactly `homeworks/<dir>/homework.yaml`. Both callers interpret `None`
as "the rule does not apply" (`validate_homework_text:652-659`,
`validate_candidate:354-371`). `_directories` accepts *any* existing directory
as a positional, so a document reached as `homeworks/<sub>/<dir>` or from
outside the root is schema-validated and reported `OK` while the identity
invariant is skipped. The CLI's own help says a positional may name a homework
directory; it does not say the identity rule will be dropped when it does not.

**Reproduced** (`homeworks/sub/1_3-good/homework.yaml` with `id: 1_3-other`):

```text
$ uv run scripts/check_metadata.py --dir <root> <root>/homeworks/sub/1_3-good
homeworks/sub/1_3-good/homework.yaml: OK — metadata contract satisfied
homeworks/sub/1_3-good/task.md: OK — task provenance contract satisfied
PASS: metadata contract satisfied
EXIT=0
```

The default scan does not reach this shape (it only descends one level and
reports `homeworks/sub` as an ERROR), so this is a positional-only hole; it is
pre-existing, not introduced by the delta.

**Fix:** stop treating `None` as silently acceptable for a document the run was
explicitly asked to check. The cheapest place is `_directories`: after
normalising a positional to its directory, require that it sit directly under
the `homeworks` base and exit 2 otherwise.

```python
homeworks = root / "homeworks"
...
if candidate.parent.resolve() != homeworks.resolve():
    raise CheckError(
        f"{raw}: not a direct homeworks/<id> directory; refusing to check it "
        "without the id-equals-directory invariant"
    )
```

This comparison resolves only the *directory* components to decide whether the
positional is in scope; it does not feed the identity comparison, whose tail
stays lexical. Add a regression for `homeworks/<sub>/<dir>` expecting exit 2.

### WR-03: A symlinked `homeworks/<dir>` is trusted lexically, so the "containing directory" is the link name and content outside the repository is validated — WARNING

**File:** `scripts/metadata/contract.py:598-604` (the lexical `parts[-2]` return); scan entry point `scripts/check_metadata.py:168-177`

**Issue:** Because only the ancestor prefix is resolved, a directory entry that
is itself a symlink contributes its link name to the identity comparison. A
tree of `homeworks/1_3-link -> <any directory>`, where that directory's
`homework.yaml` says `id: 1_3-link`, is accepted even though the real containing
directory has a different name and may live outside the repository. The
checker then validates and reports that external content as a repository
document. This is the direct cost of the lexical tail the delta now documents as
protection: the invariant holds for the *link*, not for the directory that
actually contains the file. Related to the still-open WR-11, which explains the
degraded record path.

**Reproduced:**

```text
homeworks/1_3-link -> /tmp/claude-501/probe04b/outside-whatever
outside-whatever/homework.yaml: id: 1_3-link

$ uv run scripts/check_metadata.py --dir <root>
homework.yaml: OK — metadata contract satisfied
task.md: OK — task contract satisfied
PASS: metadata contract satisfied
EXIT=0
```

The record path degrades to a bare `homework.yaml` / `task.md`, so the report
neither names the repository path nor reveals that the content came from
outside the root.

**Fix:** refuse to *validate* a symlinked `homeworks/<dir>` entry, while still
allowing a symlinked `homeworks` base (row 59 / T-04-27). `lstat` on the final
component distinguishes the two:

```python
# in check_metadata.py::_directories, for both scan modes
if stat.S_ISLNK(os.lstat(path).st_mode):
    raise CheckError(f"{display}: homework directory is a symlink; refusing to follow it")
```

A symlinked base still passes this check because `lstat` inspects only the final
component (`root/homeworks/<dir>`), and the pre-existing
`test_id_mismatch_survives_a_symlinked_homeworks_base` (which symlinks
`homeworks` itself) is unaffected. Add a regression with a symlinked
`homeworks/<dir>` expecting exit 2.

## Info

### IN-01: `_homework_directory` is CWD-sensitive and its docstring does not state the absolute-path precondition — INFO

**File:** `scripts/metadata/contract.py:598`

**Issue:** `os.path.abspath(path)` resolves a relative `path` against the
process working directory. Both current callers pass absolute paths
(`check_metadata.py` builds them from the resolved root; `new_homework` builds
them from `target_dir`), so this is latent. A future caller passing a relative
document path while the CWD is not the root gets `ancestor.resolve() !=
Path(root).resolve()` and therefore `None` — the invariant is skipped, not
failed. That is the same silent-skip contract as WR-02, reached through
CWD state.

**Fix:** state the precondition in the docstring and assert it at the top,
e.g. `if not Path(path).is_absolute(): raise check-error/return error` instead
of returning `None`; or normalise `path` against `root` explicitly rather than
against the CWD.

### IN-02: The three new identity tests duplicate the alias-fixture setup three times — INFO

**File:** `scripts/tests/test_homework_metadata.py:689-752`

**Issue:** The `mkdtemp` + `addCleanup(shutil.rmtree, ...)` + `symlink_to` block
is repeated verbatim in `test_id_mismatch_holds_when_the_root_is_spelled_
differently` (691-694), `test_matching_id_is_accepted_when_the_root_is_spelled_
differently` (718-721) and `test_id_mismatch_survives_a_symlinked_base_under_a_
differently_spelled_root` (733-737). A change to the spelling fixture (prefix,
cleanup policy, target) must be made in three places.

**Fix:** extract a `FixtureBase._alias_root()` helper returning the alias path
with cleanup already registered, and call it from all three tests.

---

_Reviewed: 2026-10-24T22:42:44Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
