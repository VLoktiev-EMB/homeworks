---
phase: 01-repository-foundation-and-policy-gate
reviewed: 2026-10-23T17:27:00Z
depth: standard
files_reviewed: 38
files_reviewed_list:
  - .claude/CLAUDE.md
  - .gitattributes
  - .github/PULL_REQUEST_TEMPLATE/docs.md
  - .github/PULL_REQUEST_TEMPLATE/homework.md
  - .github/PULL_REQUEST_TEMPLATE/infra.md
  - .github/workflows/security.yml
  - .gitignore
  - .pre-commit-config.yaml
  - AGENTS.md
  - LICENSE
  - LICENSES/CC-BY-4.0.txt
  - LICENSES/MIT.txt
  - NOTICE
  - README.md
  - REUSE.toml
  - docs/decisions/0001-monorepo-with-independent-projects.md
  - docs/decisions/0002-ports-and-adapters-no-universal-hal.md
  - docs/decisions/0003-git-policy-and-protected-main.md
  - docs/decisions/0004-license-and-attribution.md
  - docs/decisions/0005-asset-and-lfs-policy.md
  - docs/decisions/README.md
  - docs/decisions/template.md
  - policy/repository.json
  - policy/ruleset-main.json
  - scripts/check_policy.py
  - scripts/check_pr_templates.py
  - scripts/tag_homework.sh
  - scripts/tests/__init__.py
  - scripts/tests/fixtures/ruleset-live.json
  - scripts/tests/test_adrs.py
  - scripts/tests/test_agents_md.py
  - scripts/tests/test_check_policy.py
  - scripts/tests/test_check_pr_templates.py
  - scripts/tests/test_gitignore.py
  - scripts/tests/test_homework_id.py
  - scripts/tests/test_license_hygiene.py
  - scripts/tests/test_security_workflow.py
  - scripts/tests/test_tag_homework.py
findings:
  critical: 0
  warning: 6
  info: 7
  total: 13
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-10-23T17:27:00Z
**Depth:** standard
**Files Reviewed:** 38
**Status:** issues_found

## Summary

The full phase 01 delta (48 commits after `ccf4224`) was reviewed: two Python checkers,
the tagging bash script, policy-as-code, the secret gate, the license declaration, the
ADRs, the PR templates, the rulebook, and the test suite. The review was not read-only
inspection: the test suite was executed (99 tests, OK), `reuse lint`/`reuse spdx` were run
to verify the actual license split, `gitleaks git --redact --verbose --log-opts="--all"`
was executed against the real history (no leaks found), and two suspected defects were
confirmed with targeted experiments in throwaway git repositories.

Overall: the policy core is correct and fail-closed. `check_policy.py` detects drift in
every direction that was probed (missing rule, extra rule, disabled enforcement, widened
conditions), and the projection does not skip fields that are absent from live. Two
guards, however, have real fail-open gaps: the PR-template checker does not see every path
GitHub uses for a default template, and `tag_homework.sh` verifies the homework in the
working tree but tags an entirely different commit. In addition, some
`[ENFORCED: ...]` tags in AGENTS.md claim mechanisms the repository does not have.

No critical (BLOCKER) defects were found.

## Warnings

### WR-01: The PR-template checker misses a default template in the root `PULL_REQUEST_TEMPLATE/`

**File:** `scripts/check_pr_templates.py:40-49`, `scripts/check_pr_templates.py:182-191`
**Issue:** `DEFAULT_TEMPLATE_PATHS` lists eight paths, but GitHub supports a
`PULL_REQUEST_TEMPLATE/` directory in `.github/` as well as in the repository root and in
`docs/`, and uses a `default.md` file inside that directory as the default template. The
paths `PULL_REQUEST_TEMPLATE/default.md` and `docs/PULL_REQUEST_TEMPLATE/default.md` (and
any other casing, when the CI filesystem is case-sensitive) are not checked. Verified
experimentally: in a temporary tree containing a copy of the three templates plus an added
root-level `PULL_REQUEST_TEMPLATE/default.md`, the script printed
`PASS default-template: no default PR template at any fallback path` and exited with code
0. The invariant "chooser cannot be suppressed" (claimed in 01-05-SUMMARY) therefore does
not actually hold: a contributor can add a default template and the checker will not
notice, while GitHub silently stops showing the template chooser.
**Fix:** enumerate every documented location instead of a hand-picked list, and compare
names case-insensitively; better, scan the three supported directories rather than a fixed
list:

```python
SUPPORTED_DIRS = ("", "docs", ".github")
for base in SUPPORTED_DIRS:
    directory = root / base / "PULL_REQUEST_TEMPLATE"
    if directory.is_dir():
        for child in directory.iterdir():
            if child.name.lower() == "default.md":
                present.append(child.relative_to(root).as_posix())
```

and add the corresponding negative fixtures to `test_stray_default_template_exits_1`.

### WR-02: `tag_homework.sh` checks the homework in the working tree but tags `origin/<default>`

**File:** `scripts/tag_homework.sh:104-110`, `scripts/tag_homework.sh:161-180`
**Issue:** Precondition 2 checks `-d "$REPO_ROOT/homeworks/$id"`, that is, the *current
working tree* (possibly the `hw/<id>` branch), while the tag is created at
`refs/remotes/origin/$DEFAULT_BRANCH`. These are different commits. Verified
experimentally: in a temporary repository, `origin/main` does not contain
`homeworks/9_9-ghost-homework` while the `hw/9_9-ghost-homework` branch does; the script
printed `PASS homework: ... exists`, created and pushed the tag, and
`git cat-file -e hw/9_9-ghost-homework:homeworks/9_9-ghost-homework/README.md` failed. In
real mode this is partly masked by the merged-PR check, but that check does not require the
PR to have been merged into the default branch, so the tag can point at a commit without
the homework. Because the tag is a public and immutable artifact (ADR-0003), the mistake
becomes a permanent dangling reference.
**Fix:** after computing `base`, verify the contents of that exact commit and require the
merged PR to target the default branch:

```bash
if ! git -C "$REPO_ROOT" cat-file -e "$base:homeworks/$id"; then
  echo "FAIL homework: homeworks/$id is absent from $DEFAULT_BRANCH ($base)" >&2
  exit 1
fi
```

and add `--base "$DEFAULT_BRANCH"` to `gh pr list` (once the default branch is resolved;
the order of the preconditions will have to change).

### WR-03: `[ENFORCED: pre-commit]` for generated files has no enforcement mechanism

**File:** `AGENTS.md:153-155`
**Issue:** The rule "Generated files are never committed: `compile_commands.json`, `site/`,
`.pio/`" is tagged `[MUST] [ENFORCED: pre-commit]`, but `.pre-commit-config.yaml` contains
only gitleaks, trailing-whitespace, end-of-file-fixer, check-merge-conflict, and
check-added-large-files. None of these inspects tracked paths; `.gitignore` only prevents
an accidental `git add .`, and `git add -f compile_commands.json` passes every hook. The
rulebook is the canonical artifact of this phase, and its enforcement tags are by
definition machine-matchable and verifiable, so a false tag is worse than none.
**Fix:** either change the tag to `[ENFORCED: review]`, or add a real hook, for example a
local `repo: local` with `entry: bash -c 'git ls-files -ci --exclude-standard
compile_commands.json site .pio | grep . && exit 1 || exit 0'`.

### WR-04: `[ENFORCED: CI]` for the license split before Phase 8

**File:** `AGENTS.md:159-161`
**Issue:** The MIT/CC-BY-4.0 rule carries the `[ENFORCED: CI]` tag even though the same
sentence says `reuse lint` "joins the pull-request pipeline in Phase 8", and the only
workflow in the repository is `security.yml` (gitleaks). Today no CI job checks the license
split, so the tag describes a future state rather than the current one.
**Fix:** use `[ENFORCED: review]` until Phase 8, or add a `reuse lint` job to
`security.yml` so the tag becomes true. The same applies to the wording on lines 84-87:
`check_policy.py --check` is not part of CI today; only a human or an agent runs it.

### WR-05: The gitleaks binary in CI is executed without an integrity check

**File:** `.github/workflows/security.yml:17-28`
**Issue:** `curl -sSfL .../gitleaks_8.30.1_linux_x64.tar.gz | tar -xz` downloads and
immediately unpacks the archive, after which the binary is installed into
`/usr/local/bin` and executed. There is neither a SHA-256 nor a signature, nor
`--proto '=https'`; a compromised release artifact or a CDN-level substitution runs with
the CI job's privileges. The pinned version narrows the surface but does not prove
integrity. Additionally, `actions/checkout@v7` is a mutable major tag, not an immutable
SHA.
**Fix:** pin the digest and verify it before unpacking, and pin `checkout` to a commit SHA:

```yaml
echo "<sha256>  $RUNNER_TEMP/gitleaks.tar.gz" | sha256sum -c -
```

### WR-06: `READ_ONLY` is never applied, and the "strips read-only keys" test cannot fail

**File:** `scripts/check_policy.py:36-48`, `scripts/tests/test_check_policy.py:87-96`
**Issue:** The `READ_ONLY` constant is not used anywhere: `project()` builds its result by
iterating only the keys of `desired`, so server-side fields cannot reach the projection
regardless of the contents of `READ_ONLY`. The corresponding test asserts
`assertNotIn(key, projected)` for keys that `committed_ruleset()` does not contain, so the
check is true by construction — even if `READ_ONLY` were removed or broken. This is dead
code plus a test that creates false confidence that server fields are verified.
**Fix:** either remove `READ_ONLY` and the corresponding assertion, or make it real:
explicitly drop read-only keys from the live body before projecting, test against a
synthetic `live` that *does* contain those keys, and additionally assert that `policy/`
itself contains no read-only fields (which would prevent a failed `--apply`).

## Info

### IN-01: The success path of `tag_homework.sh` has no test coverage

**File:** `scripts/tests/test_tag_homework.py:97-180`
**Issue:** All four tests end before the tag is created (`TAG_HOMEWORK_SKIP_REMOTE=1` plus
the absence of an `origin` in the fixture). The branch `git fetch` → `resolve_default_branch`
→ `git tag` → `git push` never executes; 01-08-SUMMARY acknowledges this. That is exactly
where defect WR-02 and the dependency on `origin/HEAD` live.
**Fix:** add a fixture with a local bare remote (`git init --bare`), several commits, and
an assertion that the tag was created at `origin/main` and pushed exactly once.

### IN-02: `section_order` can miss a missing MADR section

**File:** `scripts/tests/test_adrs.py:112-115`, `scripts/tests/test_adrs.py:216-225`
**Issue:** `lines.index(heading)` takes the first occurrence, and the assertion is limited
to `len(indices) == len(MADR_SECTIONS)`. If one heading is duplicated and another is
missing, the count still matches and the test passes.
**Fix:** assert that each heading is unique (`text.count(heading) == 1`) and compare
positions computed in a single pass.

### IN-03: The "no configured git identity" check can fail spuriously

**File:** `scripts/tests/test_license_hygiene.py:198-210`
**Issue:** `assertNotIn(value, text)` for `git config user.name` trips on any short name
(for example `A` or `MIT`) that happens to occur in the `LICENSE`/`NOTICE` text. The
canonical command `python3 -m unittest discover -s scripts/tests` then fails for a reason
unrelated to a PII leak.
**Fix:** check only `user.email` (which is unique), or require a minimum value length / a
whole-word match with boundaries.

### IN-04: The `language: golang` hook pulls an unpinned Go toolchain

**File:** `.pre-commit-config.yaml:5-8`
**Issue:** The upstream gitleaks definition uses `language: golang`; when `go` is not on
`PATH`, pre-commit downloads the *latest* Go version from `go.dev`/`dl.google.com` while
installing the hook. That contradicts the pinned-toolchain posture
(PlatformIO/espressif32/clang-format) and makes the first `pre-commit run` network-dependent
and drifting over time.
**Fix:** either document this as a known property, or use `id: gitleaks-system` with an
already installed 8.30.1 binary (brew/CI), or `language: docker_image`.

### IN-05: "Next number: 0006 (reserved …)" contradicts the numbering rule

**File:** `docs/decisions/README.md:10-16`, `docs/decisions/README.md:30`
**Issue:** The index states that numbers are assigned sequentially *on acceptance* and
that the next number is "highest existing + 1", but then "reserves" 0006 for a Phase 2
decision. Reservation is not provided for by the rules and creates a conflict if Phase 2
accepts a different decision first.
**Fix:** replace it with "Next free number: 0006".

### IN-06: The ASCII character class is broader than the ID pattern

**File:** `AGENTS.md:100-107`
**Issue:** The ID rule is `^[0-9]+_[0-9]+-[a-z0-9-]+$`, while the next rule allows the
class `[a-z0-9_.-]` for "IDs and paths". The ID `1_3-a.b` satisfies the ASCII rule but not
the ID pattern; a reader implementing both rules gets different results.
**Fix:** separate them: an exact regex for IDs, `[a-z0-9_.-]` for paths.

### IN-07: The `--check` projection cannot see fields absent from the committed file

**File:** `scripts/check_policy.py:144-162`, `docs/decisions/0003-git-policy-and-protected-main.md:122-127`
**Issue:** Verified: changing live `require_extra_approval_for_unattributed_changes` from
`true` to `false` still makes `--check` return 0, because the field is not declared in
`policy/ruleset-main.json`. ADR-0003 documents this explicitly as an unverified assumption,
so it is not an implementation defect, but it is a genuine fail-open gap in the drift
checker: a weakening of protection made outside the declared subset is not detected.
**Fix:** after the first `--apply`, record the actual values of
`require_extra_approval_for_unattributed_changes`, `required_reviewers`, and
`dismissal_restriction` in the committed file (or explicitly forbid them), so `--check`
compares them too.

---

_Reviewed: 2026-10-23T17:27:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
