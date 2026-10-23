---
phase: 01-repository-foundation-and-policy-gate
verified: 2026-10-23T17:36:56Z
status: human_needed
score: 22/28 must-haves verified
covered_files:
  - .claude/CLAUDE.md
  - .gitattributes
  - .github/PULL_REQUEST_TEMPLATE/docs.md
  - .github/PULL_REQUEST_TEMPLATE/homework.md
  - .github/PULL_REQUEST_TEMPLATE/infra.md
  - .github/workflows/security.yml
  - .gitignore
  - .planning/phases/01-repository-foundation-and-policy-gate/01-01-PLAN.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-01-SUMMARY.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-02-PLAN.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-02-SUMMARY.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-03-PLAN.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-03-SUMMARY.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-04-PLAN.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-04-SUMMARY.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-05-PLAN.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-05-SUMMARY.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-06-PLAN.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-06-SUMMARY.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-07-PLAN.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-07-SUMMARY.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-08-PLAN.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-08-SUMMARY.md
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
covered_digest: "v3:sha256:e5722254bc02935fa4faebe9a1251f7905f04b49c71de78ad8d660a5f62c2a92"
behavior_unverified: 6
overrides_applied: 0
behavior_unverified_items:
  - truth: "A direct push to the default branch is rejected by the live ruleset."
    test: "On a scratch clone, commit on main and run git push origin main."
    expected: "GitHub rejects the push with a ruleset/protected-branch error; the commit is discarded."
    why_human: "The ruleset configuration is verified live, but no push has been attempted; rejection is server-side runtime behavior."
  - truth: "Two concurrent pushes to the default branch cannot both succeed, and two pull requests touching the same region cannot both merge untouched."
    test: "Observe the direct-push probe and a second pull request rebased onto main after the first merges."
    expected: "The non-fast-forward and required-linear-history rules reject the loser until it updates its base."
    why_human: "Enforcement happens in GitHub's server; no repository command can observe it without mutating the live branch."
  - truth: "A squash merge produces exactly one commit on the default branch per pull request."
    test: "Merge the Phase 1 pull request with squash and inspect git log --oneline origin/main."
    expected: "Exactly one new commit appears for the pull request."
    why_human: "No pull request has been merged yet; the result exists only in the live commit graph."
  - truth: "check_policy.py --apply is idempotent: a second run changes nothing."
    test: "Run python3 scripts/check_policy.py --apply twice, then python3 scripts/check_policy.py --check."
    expected: "The second apply reports no diff, --check exits 0, and git status is unchanged."
    why_human: "Only one apply run has happened; a second run mutates live GitHub settings and was deliberately left to the owner."
  - truth: "The gitleaks and reuse CI jobs execute successfully on a GitHub runner."
    test: "Open the Phase 1 pull request and watch the security workflow."
    expected: "Both jobs pass; the gitleaks job scans the full history with --redact and the reuse job reports compliance."
    why_human: "Neither job has ever run on GitHub Actions; only the equivalent commands were executed locally."
  - truth: "tag_homework.sh creates and pushes a tag after a real merged pull request on GitHub."
    test: "After a homework pull request is merged, run scripts/tag_homework.sh <id> against the real origin."
    expected: "Every precondition passes, the tag appears at origin/main, and it is pushed exactly once."
    why_human: "The success path is proven against a local bare remote; the gh pr list gate has never queried the live repository."
human_verification:
  - test: "Direct-push probe (VALIDATION manual row, FOUND-03)"
    expected: "git push origin main on a scratch clone is rejected with a ruleset/protected-branch error; discard the commit."
    why_human: "Requires a real rejected push against the live remote."
  - test: "check_policy.py --apply idempotence (FOUND-03/FOUND-04)"
    expected: "A second --apply produces no diff, --check still exits 0, and git status is unchanged."
    why_human: "Only one apply has run; repeating it mutates live GitHub state."
  - test: "Real-GitHub tag creation (FOUND-04)"
    expected: "scripts/tag_homework.sh <id> passes its merged-PR gate via gh and pushes hw/<id> once at origin/main."
    why_human: "The gh path has only been exercised against a local bare remote."
  - test: "First CI execution of .github/workflows/security.yml (FOUND-07 and FOUND-06)"
    expected: "The gitleaks full-history job and the reuse lint job both pass on a GitHub runner."
    why_human: "The workflow has never run on GitHub Actions."
  - test: "Squash-merge and linear-history behavior (backstop truths)"
    expected: "The Phase 1 pull request squash-merges into exactly one commit on main; a second same-region pull request must update its base before merging."
    why_human: "These are GitHub server-side behaviors visible only in the live commit graph."
  - test: "Judgment-tier prohibitions review"
    expected: "No internal course material or original assignment text is present; no document describes a direct-push or force-push workflow."
    why_human: "Both prohibitions are reviewer judgment, not machine-checkable."
  - test: "Accepted free-plan limitation (informational)"
    expected: "ADR-0003's revisit trigger for secret_scanning_validity_checks and secret_scanning_non_provider_patterns is reviewed when the org plan changes."
    why_human: "The two toggles cannot be enabled on the current free plan; the disposition is documented."
---

# Phase 1: Repository Foundation and Policy Gate Verification Report

**Phase Goal:** A public repository whose history, licensing, asset, and contribution rules are safe by construction and cannot be repaired later.
**Verified:** 2026-10-23T17:36:56Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

The goal was judged against the repository itself, not against the eight SUMMARY files. Every claim below was re-derived from the working tree, the git index, and live GitHub state. All commands were run in this session; none of the evidence is copied from a SUMMARY.

### Observable Truths

| #   | Truth   | Status     | Evidence       |
| --- | ------- | ---------- | -------------- |
| 1 | `policy/ruleset-main.json` protects the default branch through `~DEFAULT_BRANCH`, is active, has an empty `bypass_actors`, and carries creation, deletion, non-fast-forward, required-linear-history, pull-request (squash-only), and status-check rules | ✓ VERIFIED | Live `gh api repos/VLoktiev-EMB/homeworks/rulesets/25632456` returns `bypass_actors: []`, `include: ["~DEFAULT_BRANCH"]`, `enforcement: active`, and exactly those six rule types; `check_policy.py --check` exits 0 |
| 2 | A direct push to `main` is actually rejected | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Configuration is live and bypass-free, but no push has been attempted (see Human Verification) |
| 3 | Two concurrent pushes to `main`, and two pull requests touching the same region, cannot both land (backstop) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | `non_fast_forward` and `required_linear_history` are live; the runtime consequence is unobserved |
| 4 | A squash merge produces exactly one commit per pull request (backstop) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | `allowed_merge_methods: ["squash"]` and `required_linear_history` are live; no merge has occurred yet |
| 5 | `check_policy.py --check` is read-only, normalizes rules by type, and uses exit codes 0/1/2 | ✓ VERIFIED | `test_check_mode_never_mutates`, `test_reordered_rules_report_no_drift`, `test_non_empty_bypass_actors_reports_drift`, `test_gh_failure_returns_exit_2_without_traceback`, `test_check_and_apply_are_mutually_exclusive`; live run exits 0 |
| 6 | Live GitHub state matches the committed policy | ✓ VERIFIED | `python3 scripts/check_policy.py --check` → exit 0 with all repository-setting lines PASS against the live repository |
| 7 | `check_policy.py --apply` is idempotent | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Apply path exists (`PUT` ruleset, `PATCH` repository, then re-read); only one run has happened |
| 8 | A staged secret is blocked before commit and redacted | ✓ VERIFIED | `pre-commit run --all-files` runs the pinned gitleaks hook (all six hooks Passed); an independent probe with a generated RSA key exited 1 with `RuleID: private-key` and the key value absent from output |
| 9 | The CI scan covers every ref with `fetch-depth: 0`, `--log-opts="--all"`, `--redact`, a pinned gitleaks rev, a pinned action SHA, and a verified archive digest | ✓ VERIFIED | Workflow read directly; the token contract suite passes; the same command run locally scanned 73 commits with no leaks |
| 10 | The CI workflow executes on a GitHub runner | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | `.github/workflows/security.yml` has never run on GitHub Actions |
| 11 | `.gitignore` covers build output, generated files, Python caches, secrets (with `.env.example` kept), OS/editor junk, videos, and the research cache | ✓ VERIFIED | Independent `git check-ignore` sweep: 23 positive paths ignored, `.env.example` and five tracked paths visible |
| 12 | The research cache is untracked | ✓ VERIFIED | `git ls-files .planning/research/.cache/` → 0 paths |
| 13 | LFS routes exactly the eight declared extensions; docs images and videos stay non-LFS | ✓ VERIFIED | `git check-attr filter` → `lfs` for pdf/step/stl/fzz/zip/bin/elf/vcd; `unspecified` for png/jpg/jpeg/webp/svg and mp4 |
| 14 | The large-file guard is LFS-aware with no exclusion list | ✓ VERIFIED | Installed `check_added_large_files.py` filters `filter=lfs` files; `.pre-commit-config.yaml` sets only `--maxkb=1024` |
| 15 | Three PR templates share a byte-identical header and carry distinct Definitions of Done | ✓ VERIFIED | Header slice is 342 bytes and identical across all three; DoD rows are 6/4/3; no required AI-disclosure row (prohibited) |
| 16 | No default PR template exists at any supported path, and the checker scans all of them case-insensitively | ✓ VERIFIED | `check_pr_templates.py` PASS; independent scan of root/`docs`/`.github` file and `PULL_REQUEST_TEMPLATE/default.md` shapes finds nothing; negative fixtures cover `DEFAULT.md` |
| 17 | `check_pr_templates.py` is read-only and idempotent | ✓ VERIFIED | Two consecutive runs exit 0 and leave `git status` unchanged |
| 18 | `LICENSE` is MIT with one handle-only copyright line; `NOTICE` carries attribution and trademark sections; no PII | ✓ VERIFIED | Files read; `Copyright (c) 2026 VLoktiev-EMB` present exactly once; neither `git config user.name` nor `user.email` occurs in LICENSE/NOTICE/REUSE.toml; 15 hygiene tests pass |
| 19 | The MIT/CC-BY-4.0 split is declared once in `REUSE.toml`, `reuse lint` is clean, and no `.reuse/dep5` exists | ✓ VERIFIED | `reuse --no-multiprocessing lint` → 72/72 files with license and copyright, 0 unused licenses, compliant; `.reuse/` is absent |
| 20 | `LICENSES/MIT.txt` and `LICENSES/CC-BY-4.0.txt` exist with canonical texts | ✓ VERIFIED | Both files present (18 and 156 lines); CC-BY text carries the canonical heading |
| 21 | Five sequential MADR ADRs exist with a matching status index, MADR 4.0 order, and the required notes | ✓ VERIFIED | 0001–0005 present; index statuses/dates match frontmatter; `test_adrs` 18 tests pass; ADR-0003 records tag mutability, the approvals trigger, and `.planning/` publicity; ADR-0004 records the REUSE.toml substitution, the PR-template MIT boundary, and the stale SIM-02 reference |
| 22 | `AGENTS.md` is the canonical rulebook within its ceiling, with both dimensions on every rule, routing, and precedence | ✓ VERIFIED | 198 lines (ceiling 300); all five vocabulary tokens present; an independent scan found no rule bullet missing `[MUST]`/`[SHOULD]` or an `[ENFORCED: …]` tag; routing targets exist or are marked planned; precedence sentence present |
| 23 | `.claude/CLAUDE.md` imports `@AGENTS.md` without restating rules and preserves generator blocks | ✓ VERIFIED | `@AGENTS.md` is line 1; no enforcement token appears outside the three GSD blocks; all three blocks intact |
| 24 | `README.md` states the license split, links the policy surfaces, and shows early-phase status | ✓ VERIFIED | Links to AGENTS.md, docs/decisions/README.md, LICENSE, NOTICE, LICENSES/; explicit MIT vs CC-BY-4.0 split and "Phase 1 of 11" status |
| 25 | The homework-ID convention is documented and test-proven | ✓ VERIFIED | `test_homework_id` extracts the single anchored pattern from `AGENTS.md` and rejects `""`, `police-flasher`, mixed case, dotted, and non-ASCII forms while accepting canonical IDs |
| 26 | `tag_homework.sh` refuses an existing tag, aggregates its preconditions, never forces, and succeeds on a local bare remote | ✓ VERIFIED | 4 refusal tests plus `test_tag_is_created_at_the_default_branch_commit` (tag at `origin/main`, pushed once) and a source-level no-force assertion; script contains no force flag |
| 27 | `tag_homework.sh` succeeds against real GitHub | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Only the local bare-remote path has executed; `gh pr list` has never queried the live repository |
| 28 | Prohibitions: no required AI disclosure (test-tier); no internal course material or bypass workflow (judgment-tier) | ✓ VERIFIED | `test_no_required_row_demands_ai_disclosure` passes; the tree contains no homework/task material and no direct-push or force-push workflow is documented |

**Score:** 22/28 truths verified (6 present, behavior-unverified)

### Deferred Items

None. The six behavior-unverified truths need observation of live GitHub behavior, not later-phase work.

### Required Artifacts

| Artifact | Expected    | Status | Details |
| -------- | ----------- | ------ | ------- |
| `policy/ruleset-main.json` | Committed writable ruleset subset | ✓ VERIFIED | Exists, substantive, consumed by `check_policy.py`, matched against live state |
| `policy/repository.json` | Merge and achievable security settings | ✓ VERIFIED | Exists; every declared key PASSes against live |
| `scripts/check_policy.py` | Read-only/apply drift checker | ✓ VERIFIED | 351 lines, wired into AGENTS.md, live run exits 0, tests exercise drift and error paths |
| `scripts/check_pr_templates.py` | Marker-slice drift checker | ✓ VERIFIED | Read-only, wired into AGENTS.md and templates; PASS against the real tree |
| `scripts/tag_homework.sh` | Precondition-gated tagger | ✓ VERIFIED | Mode 755; wired into AGENTS.md; tests cover refusal and success paths offline |
| `.gitignore` | Ignore coverage | ✓ VERIFIED | Independently exercised through `git check-ignore` |
| `.gitattributes` | LFS routing and text/binary treatment | ✓ VERIFIED | Independently exercised through `git check-attr` |
| `.pre-commit-config.yaml` | Pinned hooks plus generated-files guard | ✓ VERIFIED | Full-tree run: six hooks Passed |
| `.github/workflows/security.yml` | Full-history scan and reuse lint | ✓ VERIFIED (presence + wiring) | Both jobs read directly; never executed on a runner |
| `.github/PULL_REQUEST_TEMPLATE/{homework,infra,docs}.md` | Three type-specific templates | ✓ VERIFIED | Shared header identical; distinct DoDs |
| `AGENTS.md`, `.claude/CLAUDE.md`, `README.md` | Rulebook, adapter, front door | ✓ VERIFIED | Line-1 import, 198-line ceiling, precise license statement |
| `LICENSE`, `NOTICE`, `LICENSES/*`, `REUSE.toml` | License boundary | ✓ VERIFIED | `reuse lint` compliant; no PII against the configured identity |
| `docs/decisions/` | Five MADRs, template, index | ✓ VERIFIED | Sequential and index-consistent |
| `scripts/tests/` | Suite | ✓ VERIFIED | 109 tests pass; 1,915 lines across nine modules and one fixture |

### Key Link Verification

| From | To  | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `scripts/check_policy.py` | live ruleset 25632456 | `gh api` GET + normalized projection | ✓ WIRED | Live run exits 0; drift tests cover missing/extra/weakened rules |
| `scripts/check_policy.py --apply` | live repository settings | `PUT` ruleset, `PATCH` repository, re-read | ✓ WIRED (idempotence unobserved) | Code path present; one apply has run |
| `.gitattributes` | pre-commit size guard | `filter=lfs` recognized by the hook | ✓ WIRED | Hook source filters LFS files before the size test |
| `.pre-commit-config.yaml` gitleaks hook | `.github/workflows/security.yml` | both pinned 8.30.1 with `--redact`, staged vs full history | ✓ WIRED | Both halves read; local full-history equivalent ran clean |
| `REUSE.toml` | `LICENSES/*.txt` | SPDX identifiers resolve to required filenames | ✓ WIRED | `reuse lint` 0 unused licenses |
| `README.md` | `LICENSE` / `NOTICE` | explicit links and split statement | ✓ WIRED | Both links resolve in the tree |
| `scripts/check_pr_templates.py` | three templates | marker byte slice | ✓ WIRED | PASS on the real tree; negative fixtures fail |
| `.claude/CLAUDE.md` | `AGENTS.md` | line-1 `@AGENTS.md` import | ✓ WIRED | Import is the first substantive line; no restated rules |
| `AGENTS.md` routing table | scripts and `docs/decisions/README.md` | task→artifact routes | ✓ WIRED | Every named file exists; planned paths marked |
| `docs/decisions/README.md` | ADR files | status index | ✓ WIRED | Index matches frontmatter; test enforces it |
| `scripts/tag_homework.sh` | `origin` tags | local `rev-parse` + `ls-remote` + `gh pr list` | ✓ WIRED (live gh path unobserved) | Local bare-remote test creates the tag at `origin/main` and pushes once |

### Data-Flow Trace (Level 4)

This phase produces configuration, policy, and checkers rather than rendered UI; the relevant flow is policy JSON → live API → normalized projection → exit code.

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `scripts/check_policy.py` | live ruleset / repository settings | `gh api` against `VLoktiev-EMB/homeworks` | Yes — live run exits 0 and prints per-setting PASS lines | ✓ FLOWING |
| `scripts/check_pr_templates.py` | template bytes | real repository tree via `git rev-parse --show-toplevel` | Yes — PASS on the real tree | ✓ FLOWING |
| `scripts/tag_homework.sh` | tag target | `refs/remotes/origin/<default>` resolved from `origin/HEAD` | Yes — bare-remote test tags the `origin/main` commit | ✓ FLOWING (local remote) |
| `.gitignore` / `.gitattributes` | path decisions | git's own ignore/attribute engine | Yes — exercised with `git check-ignore` / `git check-attr` | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Full suite | `python3 -m unittest discover -s scripts/tests` | 109 tests, OK | ✓ PASS |
| Python lint | `ruff check scripts/` | No issues found | ✓ PASS |
| PR template contract | `python3 scripts/check_pr_templates.py` (twice) | PASS, no tree change | ✓ PASS |
| Live policy drift | `python3 scripts/check_policy.py --check` | PASS, exit 0 | ✓ PASS |
| License split | `reuse --no-multiprocessing lint` | Compliant, 72/72 files | ✓ PASS |
| Local gate | `pre-commit run --all-files` | Six hooks Passed | ✓ PASS |
| Full-history secret scan | `gitleaks git --redact --verbose --log-opts="--all"` | 73 commits, no leaks | ✓ PASS |
| Secret detection canary | generated RSA key staged in a throwaway repo, `gitleaks git --pre-commit --redact --staged --verbose` | exit 1, `private-key`, secret withheld | ✓ PASS |
| Ignore coverage | `git check-ignore` over 23 positive and 6 negative paths | all as expected | ✓ PASS |
| LFS routing | `git check-attr filter` over 14 paths | 8 LFS, 6 unspecified | ✓ PASS |
| Commit convention | `git log origin/main..HEAD` subject scan | 81/81 Conventional Commits | ✓ PASS |

### Probe Execution

Not applicable — this phase declares no `scripts/*/tests/probe-*.sh` and its plans name no probes.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| FOUND-02 | 01-06 | Homework IDs follow `module_lesson-name` and stay stable | ✓ SATISFIED | Pattern documented in AGENTS.md and applied by `test_homework_id`; publication stability is documented (Phase 4 enforces the schema) |
| FOUND-03 | 01-01, 01-08 | `main` protected; every change through branch + PR; no force-push or history rewrite | ✓ SATISFIED (runtime probe pending) | Live active ruleset, empty bypass, six rules; `check_policy --check` exit 0; direct-push rejection is a human check |
| FOUND-04 | 01-01, 01-08 | Conventional Commits; squash merges; `hw/<id>` tag after merge; branch deleted | ✓ SATISFIED (real-GitHub tag pending) | 81/81 commits conventional; squash-only ruleset live; `delete_branch_on_merge: true`; tag script tested against a bare remote |
| FOUND-05 | 01-05 | Three PR templates with shared header and type-specific DoD | ✓ SATISFIED | Templates and checker verified; no default template anywhere |
| FOUND-06 | 01-04, 01-06 | MIT, NOTICE, third-party attribution; no internal material or PII | ✓ SATISFIED | `reuse lint` compliant; handle-only identity; no course material present |
| FOUND-07 | 01-02, 01-03 | gitleaks locally and over full history in CI; ignore/attribute coverage | ✓ SATISFIED (CI execution pending) | Local gate proven by canary and full-tree run; workflow wired and contract-tested; CI job not yet executed |
| FOUND-08 | 01-02 | LFS only for large non-diffable binaries; site assets normal; videos linked | ✓ SATISFIED | `git check-attr` sweep matches the policy exactly |
| FOUND-10 | 01-06 | AGENTS.md canonical rulebook; `.claude/CLAUDE.md` imports it | ✓ SATISFIED | 198 lines, full vocabulary, thin adapter, contract tests |
| TOOL-07 | 01-07 | Infrastructure decisions recorded as MADR ADRs | ✓ SATISFIED | Five accepted MADRs, template, and index, all tested |

No orphaned requirements: every Phase 1 ID in REQUIREMENTS.md (`FOUND-02`–`FOUND-08`, `FOUND-10`, `TOOL-07`) is claimed by at least one plan.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `docs/decisions/README.md` | 30 | "Next number: 0006 (reserved …)" contradicts the sequential-on-acceptance rule (review IN-05) | ℹ️ Info | Documentation-only; no number is actually reserved in code |
| `scripts/check_policy.py` | 146-170 | Projection cannot detect a weakening of server fields the committed file does not declare (review IN-07) | ℹ️ Info | Documented in ADR-0003 as an unverified assumption; ruleset core still fail-closed |
| `scripts/tests/test_adrs.py` | 112-115 | Section-order check can miss one missing heading if another is duplicated (review IN-02) | ℹ️ Info | Test-quality only; the real ADRs have the correct order |
| `.pre-commit-config.yaml` | 5-8 | `language: golang` may download an unpinned Go toolchain on a fresh machine (review IN-04) | ℹ️ Info | Environment-dependence only; the hook rev itself is pinned |
| `AGENTS.md` | 101-108 | ID regex and the broader path character class are stated side by side (review IN-06) | ℹ️ Info | A reader could conflate them; the tested ID regex is unambiguous |
| `.planning/phases/01-.../01-VALIDATION.md` | whole file | Still `status: draft`, all rows pending, `nyquist_compliant: false` | ℹ️ Info | Process tracking artifact not updated after execution; does not affect the repository rules |
| `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` | tracking tables | Phase 1 requirement checkboxes and plan status remain unchecked/pending | ℹ️ Info | Tracking drift only; the implementation exists |

No `TBD`, `FIXME`, or `XXX` debt markers were found in any file changed by this phase (the only `XXX` hit was an `mktemp` template in a pre-existing script). No stub or orphaned artifact was found.

The six review warnings (WR-01 to WR-06) are all fixed in the tree, as the disposition claims: directory-based default-template detection with `DEFAULT.md` fixtures, tag-target content verification and `--base` on the merged-PR gate, a real `no-generated-files` hook, a `reuse` CI job, a SHA-pinned checkout with a verified gitleaks digest, and a wired `READ_ONLY` filter with a non-vacuous test.

### Human Verification Required

### 1. Direct-push probe (FOUND-03)

**Test:** On a scratch clone of the public repository, `git checkout main`, `git commit --allow-empty -m test`, `git push origin main`.
**Expected:** GitHub rejects the push with a ruleset/protected-branch error; discard the commit.
**Why human:** Requires an actual rejected push against the live remote; deliberately not automated.

### 2. `check_policy.py --apply` idempotence

**Test:** Run `python3 scripts/check_policy.py --apply` a second time, then `python3 scripts/check_policy.py --check` and `git status --porcelain`.
**Expected:** No diff on the second apply, `--check` exits 0, and the working tree is unchanged.
**Why human:** Only one apply has run; repeating it mutates live GitHub settings.

### 3. Real-GitHub tag creation (FOUND-04)

**Test:** After a homework pull request is merged, run `scripts/tag_homework.sh <id>` against the real origin.
**Expected:** All preconditions pass, including the `gh pr list --base <default> --head hw/<id>` gate; the tag is created at `origin/main` and pushed exactly once.
**Why human:** The script's `gh` path has only been exercised against a local bare remote.

### 4. First CI execution of the security workflow

**Test:** Open the Phase 1 pull request and watch `.github/workflows/security.yml`.
**Expected:** The gitleaks full-history job passes with redacted output and the reuse job reports compliance.
**Why human:** Neither job has ever run on a GitHub runner.

### 5. Squash-merge and linear-history behavior (backstop truths)

**Test:** Squash-merge the Phase 1 pull request, then inspect `git log --oneline origin/main`; for the conflict case, open a second pull request touching the same region after the first merges.
**Expected:** Exactly one new commit per pull request; the second pull request must update its base before merging.
**Why human:** Server-side GitHub behavior, visible only in the live commit graph.

### 6. Judgment-tier prohibitions review

**Test:** Review the tree for internal course material or original assignment text, and review AGENTS.md, README.md, and the ADRs for any documented direct-push or force-push workflow.
**Expected:** None present; assignments would appear only as attributed English paraphrase.
**Why human:** Reviewer judgment; not machine-checkable.

### 7. Accepted free-plan limitation (informational)

**Test:** When the organization plan changes, revisit ADR-0003's trigger for `secret_scanning_validity_checks` and `secret_scanning_non_provider_patterns`.
**Expected:** Both toggles enabled in `policy/repository.json` and applied.
**Why human:** The two toggles are unachievable on the current free plan; secret scanning and push protection are already enabled and verified live.

### Gaps Summary

No gap blocks the phase goal. The repository's history, licensing, asset, and contribution rules are present, wired, and independently exercised:

- history: the live ruleset is active with an empty bypass list and every write-blocking rule; `check_policy.py --check` exits 0 against GitHub, and all 81 phase commits follow Conventional Commits;
- licensing: MIT plus CC-BY-4.0 are declared once, `reuse lint` is clean, and no configured identity appears in the legal files;
- assets: LFS routing covers exactly the eight declared extensions, while site images and videos stay normal objects and videos are ignored;
- contribution: three templates share a byte-identical header with distinct DoDs and no default template, the rulebook is canonical at 198 lines with the adapter importing it, and the tag script fails closed.

The remaining uncertainty is runtime confirmation of server-side and CI behavior, which this environment cannot produce: the direct-push probe, the second `--apply`, a real-GitHub tag, the first workflow run, and the squash-merge/linear-history observations. These are reported for human verification, not as implementation failures. The review's six warnings are fixed; its seven remaining findings are informational (one documentation contradiction, one documented fail-open in the drift subset, and five test/tooling-quality notes).

---

_Verified: 2026-10-23T17:36:56Z_
_Verifier: Claude (gsd-verifier)_
