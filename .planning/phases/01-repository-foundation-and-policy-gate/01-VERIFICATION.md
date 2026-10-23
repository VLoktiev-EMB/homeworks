---
phase: 01-repository-foundation-and-policy-gate
verified: 2026-10-23T18:01:31Z
status: human_needed
score: 25/28 must-haves verified
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
  - .planning/phases/01-repository-foundation-and-policy-gate/01-SECURITY.md
  - .planning/phases/01-repository-foundation-and-policy-gate/01-UAT.md
  - .planning/phases/01-repository-foundation-and-policy-gate/COVERAGE.md
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
covered_digest: "v3:sha256:8bbbb668b23a8996125f2bb44c55b6582957cec4d581f30c6780e782ab4a3daf"
behavior_unverified: 3
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 22/28
  gaps_closed:
    - "A direct push to main is actually rejected (UAT test 1: pass)"
    - "check_policy.py --apply is idempotent (UAT test 2: pass)"
    - "The gitleaks and reuse CI jobs execute successfully on a GitHub runner (run 39998933792: both jobs pass)"
  gaps_remaining: []
  regressions: []
behavior_unverified_items:
  - truth: "Two concurrent pushes to main cannot both succeed, and two pull requests touching the same region cannot both merge untouched."
    test: "After PR #1 squash-merges, open a second pull request touching the same region and observe that it must update its base before it can merge."
    expected: "The non-fast-forward and required-linear-history rules reject the loser until its base is updated."
    why_human: "Enforcement happens in GitHub's server; no repository command can observe it without mutating the live branch."
  - truth: "A squash merge produces exactly one commit on the default branch per pull request."
    test: "Squash-merge PR #1 and inspect git log --oneline origin/main."
    expected: "Exactly one new commit appears for the pull request, with the pull-request title as its subject."
    why_human: "PR #1 is open and unmerged; the result exists only in the live commit graph."
  - truth: "tag_homework.sh creates and pushes a tag after a real merged pull request on GitHub."
    test: "After a homework pull request is merged, run scripts/tag_homework.sh <id> against the real origin."
    expected: "Every precondition passes, the tag appears at origin/main, and it is pushed exactly once."
    why_human: "The success path is proven against a local bare remote; the gh pr list gate has never queried the live repository."
human_verification:
  - test: "Squash-merge and linear-history behavior (UAT test 5, still blocked)"
    expected: "PR #1 squash-merges into exactly one commit on main; a later same-region pull request must update its base before merging."
    why_human: "GitHub server-side behavior visible only in the live commit graph; PR #1 is still open."
  - test: "Real-GitHub tag creation (UAT test 3, still blocked)"
    expected: "scripts/tag_homework.sh <id> passes its merged-PR gate via gh and pushes hw/<id> once at origin/main."
    why_human: "No homework pull request has been merged; the gh path has only been exercised against a local bare remote."
  - test: "Conventional Commits compliance of the merge commit (FOUND-04)"
    expected: "Before merging, retitle PR #1 to a Conventional Commits subject (for example feat(01): add repository foundation and policy gate) so the squash commit on main complies with AGENTS.md. The branch also contains one wip: checkpoint commit (cb571fd) that a squash merge will collapse and that will not reach main."
    why_human: "The squash commit message is chosen at merge time from the PR title; the current title Phase 1: Repository foundation and policy gate is not type(scope): summary."
---

# Phase 1: Repository Foundation and Policy Gate Verification Report

**Phase Goal:** A public repository whose history, licensing, asset, and contribution rules are safe by construction and cannot be repaired later.
**Verified:** 2026-10-23T18:01:31Z
**Status:** human_needed
**Re-verification:** Yes — the previous report was marked `stale` because covered inputs changed; this run re-derived every claim from the working tree, the live GitHub API, and a fresh CI run.

## Goal Achievement

The goal was judged against the repository itself, not against the eight SUMMARY files. Every claim below was re-derived from the working tree, the git index, the live GitHub repository, and the GitHub Actions run log. This re-verification also re-checked the three inputs the previous report did not cover: `01-SECURITY.md`, `COVERAGE.md`, and `01-UAT.md`.

### Observable Truths

| #   | Truth   | Status     | Evidence       |
| --- | ------- | ---------- | -------------- |
| 1 | `policy/ruleset-main.json` protects the default branch through `~DEFAULT_BRANCH`, is active, has an empty `bypass_actors`, and carries creation, deletion, non-fast-forward, required-linear-history, pull-request (squash-only), and status-check rules | ✓ VERIFIED | Live `gh api repos/VLoktiev-EMB/homeworks/rulesets/25632456` returns `bypass_actors: []`, `include: ["~DEFAULT_BRANCH"]`, `enforcement: active`, and exactly those six rule types; `pull_request.allowed_merge_methods: ["squash"]` |
| 2 | A direct push to `main` is actually rejected | ✓ VERIFIED | UAT test 1 records `result: pass`: a scratch-clone `git push origin HEAD:main` was rejected by the ruleset; the live ruleset is active, bypass-free, and targets `~DEFAULT_BRANCH` |
| 3 | Two concurrent pushes to `main`, and two pull requests touching the same region, cannot both land (backstop) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | `non_fast_forward` and `required_linear_history` are live; the runtime consequence is unobserved (see Human Verification) |
| 4 | A squash merge produces exactly one commit per pull request (backstop) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | `allowed_merge_methods: ["squash"]` and `required_linear_history` are live; PR #1 is open and no merge has occurred |
| 5 | `check_policy.py --check` is read-only, normalizes rules by type, and uses exit codes 0/1/2 | ✓ VERIFIED | `test_projection_drops_every_read_only_field`, `test_reordered_rules_report_no_drift`, `test_non_empty_bypass_actors_reports_drift`, `test_gh_failure_returns_exit_2_without_traceback`, `test_check_and_apply_are_mutually_exclusive`; full suite 110 tests OK; live run exits 0 |
| 6 | Live GitHub state matches the committed policy | ✓ VERIFIED | `python3 scripts/check_policy.py --check` → exit 0; ruleset projection PASS and all seven repository-setting lines PASS against the live repository |
| 7 | `check_policy.py --apply` is idempotent | ✓ VERIFIED | UAT test 2 records `result: pass`: a second `--apply` produced no diff, `--check` still exits 0, and `git status --porcelain` was unchanged |
| 8 | A staged secret is blocked before commit and redacted | ✓ VERIFIED | Fresh canary in this session: a generated RSA private key staged in a throwaway repo makes `gitleaks git --pre-commit --redact --staged` exit 1 with `RuleID: private-key` and `Finding: REDACTED`; the key material is absent from output; `pre-commit run --all-files` passes all six hooks |
| 9 | The CI scan covers every ref with `fetch-depth: 0`, `--log-opts="--all"`, `--redact`, a pinned gitleaks rev, a pinned action SHA, and a verified archive digest | ✓ VERIFIED | Workflow read directly; 18-test token contract suite passes; local full-history run scanned 82 commits with no leaks; the same job passes on the runner (run 39998933792) |
| 10 | The CI workflow executes on a GitHub runner | ✓ VERIFIED | `gh run view 39998933792` → `reuse lint (license split)` pass 10s and `gitleaks (full history)` pass 4s; a later run 39999067143 is also green |
| 11 | `.gitignore` covers build output, generated files, Python caches, secrets (with `.env.example` kept), OS/editor junk, videos, and the research cache | ✓ VERIFIED | Independent `git check-ignore` sweep: `.pio/`, `compile_commands.json`, `site/`, `secrets.txt`, `*.pem`, `*.key`, `id_rsa`, `*.mp4`, `.planning/research/.cache/`, `build/lib/` ignored; `.env.example`, `lib/**`, `homeworks/**`, `.planning/STATE.md`, `.claude/CLAUDE.md` visible; `test_gitignore.py` 11 tests pass |
| 12 | The research cache is untracked | ✓ VERIFIED | `git ls-files .planning/research/.cache/` → 0 paths |
| 13 | LFS routes exactly the eight declared extensions; docs images and videos stay non-LFS | ✓ VERIFIED | `git check-attr filter` → `lfs` for pdf/step/stl/fzz/zip/bin/elf/vcd; `unspecified` for png/jpg/jpeg/webp/svg and mp4 |
| 14 | The large-file guard is LFS-aware with no exclusion list | ✓ VERIFIED | Installed `check_added_large_files.py` calls `filter_lfs_files` via `git check-attr filter` and skips `lfs` entries; `.pre-commit-config.yaml` sets only `--maxkb=1024` |
| 15 | Three PR templates share a byte-identical header and carry distinct Definitions of Done | ✓ VERIFIED | `check_pr_templates.py` PASS on header, markers, and DoD; header slice identical across all three; DoD rows differ per type; no required AI-disclosure row |
| 16 | No default PR template exists at any supported path, and the checker scans all of them case-insensitively | ✓ VERIFIED | Checker PASS; repository-wide `find` returns only the `.github/PULL_REQUEST_TEMPLATE/` directory; negative fixtures cover `default.md`/`DEFAULT.md` |
| 17 | `check_pr_templates.py` is read-only and idempotent | ✓ VERIFIED | Two consecutive runs exit 0 and `git status --porcelain` remains empty; `test_second_run_is_identical_and_read_only` |
| 18 | `LICENSE` is MIT with one handle-only copyright line; `NOTICE` carries attribution and trademark sections; no PII | ✓ VERIFIED | Files read; `Copyright (c) 2026 VLoktiev-EMB` is the only copyright line; the configured git identity (`4oc3p`) does not occur in LICENSE/NOTICE/REUSE.toml; 15 hygiene tests pass; a repository-wide email sweep finds only test fixtures and `git@github.com` remote forms |
| 19 | The MIT/CC-BY-4.0 split is declared once in `REUSE.toml`, `reuse lint` is clean, no `.reuse/dep5` exists, and PR templates stay on the MIT catch-all | ✓ VERIFIED | `reuse --no-multiprocessing lint` → 74/74 files with license and copyright, compliant; `.reuse/` absent; `reuse spdx` shows `.github/PULL_REQUEST_TEMPLATE/homework.md` → MIT and `README.md` → CC-BY-4.0 |
| 20 | `LICENSES/MIT.txt` and `LICENSES/CC-BY-4.0.txt` exist with canonical texts | ✓ VERIFIED | Both files present (18 and 156 lines); CC-BY text carries the canonical heading |
| 21 | Five sequential MADR ADRs exist with a matching status index, MADR 4.0 order, and the required notes | ✓ VERIFIED | 0001–0005 present; index statuses/dates match frontmatter; `test_adrs` 18 tests pass; ADR-0003 records tag mutability, the approvals trigger, and `.planning/` publicity; ADR-0004 records the REUSE.toml substitution, the PR-template MIT boundary, and the stale SIM-02 reference |
| 22 | `AGENTS.md` is the canonical rulebook within its ceiling, with both dimensions on every rule, routing, and precedence | ✓ VERIFIED | 198 lines (ceiling 300); 20 `[MUST]`, 4 `[SHOULD]`, 24 `[ENFORCED: …]` tokens; no rule bullet missing a tag; every routing target exists or is marked planned; precedence sentence present |
| 23 | `.claude/CLAUDE.md` imports `@AGENTS.md` without restating rules and preserves generator blocks | ✓ VERIFIED | `@AGENTS.md` is line 1; three generator block pairs intact; 12 adapter/ceiling/vocabulary tests pass |
| 24 | `README.md` states the license split, links the policy surfaces, and shows early-phase status | ✓ VERIFIED | Links to AGENTS.md, docs/decisions/README.md, LICENSE, NOTICE, LICENSES/; explicit MIT vs CC-BY-4.0 split and "Phase 1 of 11" status |
| 25 | The homework-ID convention is documented, ASCII-only, and test-proven | ✓ VERIFIED | `test_homework_id` extracts the single anchored pattern from `AGENTS.md` and rejects `""`, `police-flasher`, mixed case, dotted, and non-ASCII forms while accepting canonical IDs; the ASCII-only path rule is documented |
| 26 | `tag_homework.sh` refuses an existing tag, aggregates its preconditions, never forces, and succeeds on a local bare remote | ✓ VERIFIED | 4 refusal tests plus `test_tag_is_created_at_the_default_branch_commit` (tag at `origin/main`, pushed once) and a source-level no-force assertion; script is mode 755 and contains no force flag |
| 27 | `tag_homework.sh` succeeds against real GitHub | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Only the local bare-remote path has executed; `gh pr list` has never queried the live repository (UAT test 3 remains blocked) |
| 28 | Prohibitions: no required AI disclosure (test-tier); no internal course material or bypass workflow (judgment-tier) | ✓ VERIFIED | `test_no_required_row_demands_ai_disclosure` passes; the tree contains no homework or assignment material and no documented direct-push or force-push path; UAT test 6 records `result: pass` |

**Score:** 25/28 truths verified (3 present, behavior-unverified)

### Deferred Items

None. The three behavior-unverified truths need observation of live GitHub behavior at merge time, not later-phase implementation work.

### Advisory (New Scope, Unevidenced)

None. Every re-verification finding below is backed by a reproducible command or a live API response.

### Required Artifacts

All 38 artifacts declared across the eight plans pass the artifact verifier (`all_passed: true`, 38/38).

| Artifact | Expected    | Status | Details |
| -------- | ----------- | ------ | ------- |
| `policy/ruleset-main.json`, `policy/repository.json` | Committed policy subset | ✓ VERIFIED | Exists, substantive, matched against live state (`--check` exit 0) |
| `scripts/check_policy.py` | Read-only/apply drift checker | ✓ VERIFIED | 350 lines, `READ_ONLY` wired into projection, exit codes 0/1/2 tested, live run exits 0 |
| `scripts/check_pr_templates.py` | Marker-slice drift checker | ✓ VERIFIED | 268 lines, read-only, PASS on the real tree, negative fixtures fail |
| `scripts/tag_homework.sh` | Precondition-gated tagger | ✓ VERIFIED | 199 lines, mode 755, fails closed on every network and tag precondition |
| `.gitignore`, `.gitattributes` | Ignore and LFS routing | ✓ VERIFIED | Independently exercised with `git check-ignore` / `git check-attr` |
| `.pre-commit-config.yaml` | Pinned hooks plus generated-files guard | ✓ VERIFIED | Six hooks pass on the full tree; gitleaks 8.30.1, pre-commit-hooks v6.0.0 |
| `.github/workflows/security.yml` | Full-history scan and reuse lint | ✓ VERIFIED | Both jobs green on GitHub run 39998933792 |
| `.github/PULL_REQUEST_TEMPLATE/{homework,infra,docs}.md` | Three type-specific templates | ✓ VERIFIED | Shared header identical; distinct DoDs; no default template |
| `AGENTS.md`, `.claude/CLAUDE.md`, `README.md` | Rulebook, adapter, front door | ✓ VERIFIED | 198-line ceiling, line-1 import, precise license statement |
| `LICENSE`, `NOTICE`, `LICENSES/*`, `REUSE.toml` | License boundary | ✓ VERIFIED | `reuse lint` compliant; no PII against the configured identity |
| `docs/decisions/` | Five MADRs, template, index | ✓ VERIFIED | Sequential and index-consistent |
| `scripts/tests/` | Suite | ✓ VERIFIED | 110 tests pass; nine test modules plus one fixture |

### Key Link Verification

`gsd_run query verify.key-links` flagged five links as "Source file not found" because those plans put prose in the `from` field (for example `scripts/check_policy.py --apply` or `AGENTS.md routing table`). Manual tracing confirms every link is wired; the table records the traced result.

| From | To  | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `scripts/check_policy.py` | live ruleset 25632456 | `gh api` GET + normalized projection | ✓ WIRED | Live run exits 0; drift tests cover missing/extra/weakened rules |
| `scripts/check_policy.py --apply` | live repository settings | `PUT` ruleset, `PATCH` repository, re-read | ✓ WIRED | Apply path present; UAT test 2 confirms idempotence |
| `.gitattributes` | pre-commit size guard | `filter=lfs` recognized by the hook | ✓ WIRED | Installed hook filters LFS files before the size test |
| `.pre-commit-config.yaml` gitleaks hook | `.github/workflows/security.yml` | both pinned 8.30.1 with `--redact`, staged vs full history | ✓ WIRED | Local canary blocks and redacts; CI job green |
| `REUSE.toml` | `LICENSES/*.txt` | SPDX identifiers resolve to required filenames | ✓ WIRED | `reuse lint` reports 0 unused licenses |
| `README.md` | `LICENSE` / `NOTICE` | explicit links and split statement | ✓ WIRED | Both links resolve in the tree |
| `scripts/check_pr_templates.py` | three templates | marker byte slice | ✓ WIRED | PASS on the real tree; negative fixtures fail |
| `.claude/CLAUDE.md` | `AGENTS.md` | line-1 `@AGENTS.md` import | ✓ WIRED | Import is the first substantive line; no restated rules |
| `AGENTS.md` routing table | scripts and `docs/decisions/README.md` | task→artifact routes | ✓ WIRED | Every named file exists; planned paths marked |
| `docs/decisions/README.md` | ADR files | status index | ✓ WIRED | Index matches frontmatter; test enforces it |
| `scripts/tag_homework.sh` | `origin` tags | `rev-parse` + `ls-remote` + `gh pr list` | ✓ WIRED (live gh path unobserved) | Local bare-remote test creates the tag at `origin/main` and pushes once |
| `AGENTS.md` tag rule | `scripts/tag_homework.sh` | rulebook routes tag creation through the script | ✓ WIRED | Rule and script agree; no alternative tag path documented |

### Data-Flow Trace (Level 4)

This phase produces configuration, policy, and checkers rather than rendered UI; the relevant flow is policy JSON → live API → normalized projection → exit code.

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `scripts/check_policy.py` | live ruleset / repository settings | `gh api` against `VLoktiev-EMB/homeworks` | Yes — live run exits 0 with per-setting PASS lines | ✓ FLOWING |
| `scripts/check_pr_templates.py` | template bytes | real repository tree via `git rev-parse --show-toplevel` | Yes — PASS on the real tree | ✓ FLOWING |
| `scripts/tag_homework.sh` | tag target | `refs/remotes/origin/<default>` resolved from `origin/HEAD` | Yes — bare-remote test tags the `origin/main` commit | ✓ FLOWING (local remote) |
| `.gitignore` / `.gitattributes` | path decisions | git's own ignore/attribute engine | Yes — exercised with `git check-ignore` / `git check-attr` | ✓ FLOWING |
| gitleaks hook / workflow | staged and historical content | git object store at pre-commit and on the runner | Yes — canary blocks a private key; CI scan of 82 commits is clean | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Full suite | `python3 -m unittest discover -s scripts/tests` | 110 tests, OK | ✓ PASS |
| PR template contract | `python3 scripts/check_pr_templates.py` (twice) | PASS, no tree change | ✓ PASS |
| Live policy drift | `python3 scripts/check_policy.py --check` | PASS, exit 0 | ✓ PASS |
| License split | `reuse --no-multiprocessing lint` | Compliant, 74/74 files | ✓ PASS |
| Local gate | `pre-commit run --all-files` | Six hooks Passed | ✓ PASS |
| Full-history secret scan | `gitleaks git --redact --log-opts="--all"` | 82 commits, no leaks | ✓ PASS |
| Secret detection canary | generated RSA key staged in a throwaway repo, `gitleaks git --pre-commit --redact --staged` | exit 1, `private-key`, `REDACTED`, key absent | ✓ PASS |
| Ignore coverage | `git check-ignore` over 13 positive and 6 negative paths | all as expected | ✓ PASS |
| LFS routing | `git check-attr filter` over 14 paths | 8 LFS, 6 unspecified | ✓ PASS |
| SPDX split | `reuse --no-multiprocessing spdx` | PR templates MIT; README and docs CC-BY-4.0 | ✓ PASS |
| CI execution | `gh run view 39998933792` | gitleaks pass 4s; reuse lint pass 10s | ✓ PASS |
| PR state | `gh pr view 1` | OPEN, MERGEABLE, CLEAN, branch → `main` | ✓ PASS |
| Live ruleset | `gh api repos/.../rulesets/25632456` | active, bypass [], six rules, squash-only | ✓ PASS |
| Commit convention | `git log --format=%s origin/main..HEAD` | 89/90 Conventional Commits; 1 `wip:` commit (cb571fd) | ✗ FAIL (warning; see Anti-Patterns) |

### Probe Execution

Not applicable — this phase declares no `scripts/*/tests/probe-*.sh` and its plans name no probes.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| FOUND-02 | 01-06 | Homework IDs follow `module_lesson-name` and stay stable | ✓ SATISFIED | Pattern documented in AGENTS.md and applied by `test_homework_id`; ASCII rule documented; publication stability is documented, and Phase 4's schema will enforce it |
| FOUND-03 | 01-01, 01-08 | `main` protected; every change through branch + PR; no force-push or history rewrite | ✓ SATISFIED | Live active ruleset with empty bypass and six rules; `check_policy --check` exit 0; direct-push rejection recorded as UAT test 1 pass; concurrent-push backstop remains behavior-unverified |
| FOUND-04 | 01-01, 01-08 | Conventional Commits; squash merges; `hw/<id>` tag after merge; branch deleted | ? NEEDS HUMAN | Squash-only rule live (89/90 branch commits conventional); real-GitHub tag creation blocked on a merged homework PR; the one `wip:` branch commit and the non-conventional PR #1 title must not reach `main` (see Human Verification) |
| FOUND-05 | 01-05 | Three PR templates with shared header and type-specific DoD | ✓ SATISFIED | Templates and checker verified; no default template anywhere |
| FOUND-06 | 01-04, 01-06 | MIT, NOTICE, third-party attribution; no internal material or PII | ✓ SATISFIED | `reuse lint` compliant; handle-only identity; no course material present |
| FOUND-07 | 01-02, 01-03 | gitleaks locally and over full history in CI; ignore/attribute coverage | ✓ SATISFIED | Local canary blocks and redacts; full-history scan clean; both CI jobs green on run 39998933792 |
| FOUND-08 | 01-02 | LFS only for large non-diffable binaries; site assets normal; videos linked | ✓ SATISFIED | `git check-attr` sweep matches the policy exactly |
| FOUND-10 | 01-06 | AGENTS.md canonical rulebook; `.claude/CLAUDE.md` imports it | ✓ SATISFIED | 198 lines, full vocabulary, thin adapter, contract tests |
| TOOL-07 | 01-07 | Infrastructure decisions recorded as MADR ADRs | ✓ SATISFIED | Five accepted MADRs, template, and index, all tested |

No orphaned requirements: every Phase 1 ID in REQUIREMENTS.md (`FOUND-02`–`FOUND-08`, `FOUND-10`, `TOOL-07`) is claimed by at least one plan.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| commit `cb571fd` | subject | `wip:` is not one of the permitted Conventional Commits types | ⚠️ Warning | One of 90 branch commits violates the AGENTS.md MUST rule; a squash merge will collapse it, so it cannot reach `main`, but the branch is published and must not be rebased |
| PR #1 | title | `Phase 1: Repository foundation and policy gate` is not `type(scope): summary` | ⚠️ Warning | GitHub uses the PR title for the default squash commit message; without a retitle, the merged commit on `main` would violate FOUND-04 |
| `docs/decisions/README.md` | 30 | "Next number: 0006 (reserved …)" contradicts the sequential-on-acceptance rule | ℹ️ Info | Documentation-only; no number is actually reserved in code |
| `scripts/check_policy.py` | 146-170 | Projection cannot detect a weakening of server fields the committed file does not declare | ℹ️ Info | Documented in ADR-0003 as an unverified assumption; ruleset core still fails closed |
| `scripts/tests/test_adrs.py` | 112-115 | Section-order check can miss one missing heading if another is duplicated | ℹ️ Info | Test-quality only; the real ADRs have the correct order |
| `.pre-commit-config.yaml` | 5-8 | `language: golang` may download an unpinned Go toolchain on a fresh machine | ℹ️ Info | Environment-dependence only; the hook rev itself is pinned |
| `AGENTS.md` | 101-108 | ID regex and path character class sit side by side; branch commits also use scopes (`infra`, `state`, `config`) that are not phase-plan or homework IDs | ℹ️ Info | A reader could conflate the patterns; both rules are review-enforced |
| `01-VALIDATION.md` | whole file | Still `status: draft`, `nyquist_compliant: false` | ℹ️ Info | Process tracking artifact not updated after execution; does not affect the repository rules |
| `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` | tracking tables | Phase 1 requirement checkboxes and plan status remain unchecked/pending | ℹ️ Info | Tracking drift only; the implementation exists |

No `TBD`, `FIXME`, or `XXX` debt marker exists in any file changed by this phase. No stub or orphaned artifact was found. `01-SECURITY.md` records 15 threats, all closed, `threats_open: 0` (ASVS L1). `COVERAGE.md` records 18 GitHub REST capabilities (7 INTEGRATE, 11 reasoned OPT-OUT) for the surface used by `check_policy.py`. Both were read and spot-checked against the live API and the scripts; their claims hold.

### Human Verification Required

### 1. Squash-merge and linear-history behavior (UAT test 5, blocked)

**Test:** Squash-merge PR #1, then inspect `git log --oneline origin/main`; for the conflict case, open a second pull request touching the same region after the first merges.
**Expected:** Exactly one new commit per pull request; the second pull request must update its base before merging.
**Why human:** Server-side GitHub behavior, visible only in the live commit graph.

### 2. Real-GitHub tag creation (UAT test 3, blocked)

**Test:** After a homework pull request is merged, run `scripts/tag_homework.sh <id>` against the real origin.
**Expected:** All preconditions pass, including the `gh pr list --state merged --base <default> --head hw/<id>` gate; the tag is created at `origin/main` and pushed exactly once.
**Why human:** No homework pull request exists yet; the script's `gh` path has only been exercised against a local bare remote.

### 3. Conventional Commits compliance of the merge commit (FOUND-04)

**Test:** Before merging, retitle PR #1 to a Conventional Commits subject, for example `feat(01): add repository foundation and policy gate`.
**Expected:** The squash commit on `main` follows `type(scope): summary`. The branch's `wip:` checkpoint commit `cb571fd` is collapsed by the squash and does not reach `main`; the branch must not be rebased to alter it.
**Why human:** The squash commit message is chosen from the PR title at merge time; the current title is not conventional.

### Gaps Summary

No gap blocks the phase goal. The repository's history, licensing, asset, and contribution rules are present, wired, and independently exercised:

- **history:** the live ruleset is active with an empty bypass list and every write-blocking rule; `check_policy.py --check` exits 0 against GitHub; a direct push was rejected (UAT test 1); 89 of 90 branch commits follow Conventional Commits;
- **licensing:** MIT plus CC-BY-4.0 are declared once, `reuse lint` is clean at 74/74, CI enforces it, and no configured identity appears in the legal files;
- **assets:** LFS routing covers exactly the eight declared extensions, while site images and videos stay normal objects and videos are ignored;
- **contribution:** three templates share a byte-identical header with distinct DoDs and no default template, the rulebook is canonical at 198 lines with the adapter importing it, and the tag script fails closed.

Compared with the previous report, three of the six behavior-unverified truths are now resolved by direct observation: the rejected direct push, the idempotent second `--apply`, and the first green CI run (gitleaks 4s, reuse 10s). Three remain human-dependent because they require actually merging PR #1 and creating a tag after a real homework merge. The previous report's claim that "81/81 commits follow Conventional Commits" was inaccurate — the `wip:` checkpoint commit was already present and is reported here as a warning, together with the PR-title action needed to keep the squash commit conventional.

---

_Verified: 2026-10-23T18:01:31Z_
_Verifier: Claude (gsd-verifier)_
