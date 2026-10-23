---
phase: 01-repository-foundation-and-policy-gate
verified: 2026-10-23T18:23:19Z
status: human_needed
score: 41/42 must-haves verified
covered_files:
  - .claude/CLAUDE.md
  - .gitattributes
  - .github/PULL_REQUEST_TEMPLATE/docs.md
  - .github/PULL_REQUEST_TEMPLATE/homework.md
  - .github/PULL_REQUEST_TEMPLATE/infra.md
  - .github/workflows/security.yml
  - .gitignore
  - .planning/REQUIREMENTS.md
  - .planning/ROADMAP.md
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
  - docs/decisions/0006-public-commit-identity.md
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
covered_digest: "v3:sha256:7cba657e87bf6da5f299d81cd5f34ea97dd2aaef8e3368ec0f1606318177c726"
behavior_unverified: 1
overrides_applied: 1
overrides:
  - must_have: "Published history uses the public handle only: no real name, institution, or email address appears in commit metadata (AGENTS.md MUST; FOUND-06; phase goal 'history safe by construction and cannot be repaired later')."
    reason: "External constraint, not an implementation defect. GitHub writes the merging account's public profile display name into server-side squash-merge commits, ignoring the handle identity present in the branch commits. The three published commits (57ff7ba, e2dd499, 69c2434) cannot be rewritten: the live ruleset rejects force-pushes and AGENTS.md forbids history rewrites. ADR-0006 (docs/decisions/0006-public-commit-identity.md) records the decision to accept the public account's display name as the repository's commit identity; 01-SECURITY.md records threat T-1-15 (accept) and accepted risk R-1-02, with threats_open: 0. The address is a handle-based GitHub noreply address (23013718+4oc3p@users.noreply.github.com); no institution or private contact data is present. The local git identity is already the handle (user.name = 4oc3p)."
    accepted_by: "VLoktiev-EMB"
    accepted_at: "2026-10-23"
re_verification:
  previous_status: gaps_found
  previous_score: 40/42
  gaps_closed:
    - "Published commit metadata carries the public account display name: reclassified from an open blocker to PASSED (override) because the irreparable exposure is now recorded as ADR-0006 and accepted risk R-1-02 in 01-SECURITY.md (threat T-1-15, status closed, threats_open: 0). No compliant remediation exists; history rewriting is forbidden by the live ruleset and AGENTS.md."
  gaps_remaining: []
  regressions: []
deferred:
  - truth: "scripts/tag_homework.sh succeeds against the real origin: its ls-remote tag refusal and its gh merged-pull-request gate both query live GitHub."
    addressed_in: "Phase 11"
    evidence: "PILOT-01 delivers homework 1.3; its merged homework pull request is the first point at which the gh pr list --state merged --base <default> --head hw/<id> gate can return a result. UAT test 3 records this as an explicit Deferred Follow-Up ('verify on the first homework PR (Phase 11)'), not as an unverified gap."
advisory: []
behavior_unverified_items:
  - truth: "Two pull requests touching the same region cannot both merge untouched; the required-linear-history rule forces the second to update its base first."
    reason: "insufficient_spec"
    test: "Create a second pull request that edits the same region as an already-merged pull request and observe its mergeability before updating its base."
    expected: "GitHub reports a conflict or a required base update and refuses the merge until the branch is updated."
    why_human: "The plan tags this truth verification: backstop. UAT test 5 records the squash-merge half as pass but states explicitly that 'the second-PR base-update behaviour was not exercised (no second PR touching the same region yet)'. PR #2 touched documentation only, so it did not exercise the clause either. No held-out or property-based test exercises it, and the verifier did not directly observe it; presence of the live ruleset is not explicit evidence for a non-inferable truth."
human_verification:
  - test: "Create a second pull request that edits the same lines as an already-merged pull request, then inspect its mergeability before updating its base."
    expected: "GitHub reports a conflict or a required base update and refuses the merge until the branch is updated."
    why_human: "GitHub-side enforcement; cannot be reproduced offline and no test exercises it. UAT test 5 records the limitation explicitly."
---

# Phase 1: Repository Foundation and Policy Gate Verification Report

**Phase Goal:** A public repository whose history, licensing, asset, and contribution rules are safe by construction and cannot be repaired later.
**Verified:** 2026-10-23T18:23:19Z
**Status:** human_needed
**Re-verification:** Yes — after the Phase 1 merge, the post-merge docs commit, the completed UAT, and the ADR-0006 acceptance of the commit-identity exposure. Every claim below was re-derived from the working tree, the git object store, the live GitHub API, and fresh local runs; SUMMARY.md claims were not used as evidence.

## Goal Achievement

The repository's policy, licensing, asset, and contribution machinery is present, wired, and exercised. The one goal-level finding from the previous pass — the public account's display name in published commit metadata — is now classified as an accepted, ADR-recorded risk rather than an open defect: the exposure is irreparable under the repository's own no-rewrite rule, so the only compliant disposition is acceptance. One behavioral clause remains unexercised (the same-region pull-request backstop), which routes the phase to human verification rather than a clean pass.

### Observable Truths

| #   | Truth   | Status     | Evidence       |
| --- | ------- | ---------- | -------------- |
| 1 | `policy/ruleset-main.json` targets `~DEFAULT_BRANCH` (not literal `refs/heads/main`), is active, has empty `bypass_actors`, and carries creation, deletion, non-fast-forward, required-linear-history, pull-request (squash-only), and status-check rules | ✓ VERIFIED | Live `gh api repos/VLoktiev-EMB/homeworks/rulesets/25632456`: `bypass_actors: []`, `include: ["~DEFAULT_BRANCH"]`, `enforcement: active`, six rule types, `allowed_merge_methods: ["squash"]`; committed JSON matches |
| 2 | Empty `bypass_actors` is enforced; a non-empty value reports drift and exits 1 | ✓ VERIFIED | Committed JSON has `bypass_actors: []`; `test_non_empty_bypass_actors_reports_drift` passes in the 110-test suite |
| 3 | `check_policy.py --check` normalizes rules by sorting on type; a reordered fixture reports no drift | ✓ VERIFIED | `test_reordered_rules_report_no_drift`, `test_rule_removed_from_live_reports_drift`, `test_reduced_approval_count_reports_drift` all pass |
| 4 | `check_policy.py --check` is read-only and uses exit 0/1/2 | ✓ VERIFIED | `READ_ONLY` wired into `project()`; `test_check_mode_never_mutates` asserts no `-X`/POST/PUT/PATCH call; `test_gh_failure_returns_exit_2_without_traceback`; `--check` against live GitHub exits 0 |
| 5 | Live GitHub state matches committed policy after an accepted apply: squash-only into the default branch, branch deletion on merge, and the security toggles the plan allows | ✓ VERIFIED | `python3 scripts/check_policy.py --check` exits 0 with per-setting PASS lines; ruleset enforces squash-only. The plan's literal "merge-commit and rebase-merge disabled / all four toggles" clause was superseded by the documented scope correction (repo-level merge/rebase stay enabled, AGENTS.md) and the free-plan opt-out for the two extra secret-scanning toggles (ADR-0003, COVERAGE.md) |
| 6 | Two concurrent pushes to `main` cannot both succeed (backstop) | ✓ VERIFIED | Live `non_fast_forward` + `creation` rules; UAT test 1 records a scratch-clone `git push origin HEAD:main` rejected; remote heads are `main` only |
| 7 | A squash merge produces exactly one commit on `main` per pull request (backstop) | ✓ VERIFIED | `git log origin/main`: 57ff7ba → e2dd499 (PR #1) → 69c2434 (PR #2), one commit per PR; PR #1 head branch deleted |
| 8 | Two PRs touching the same region cannot both merge untouched (backstop) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | `required_linear_history` is live, but UAT test 5 states the second-PR base-update behaviour was not exercised; PR #2 (docs-only) did not exercise it either; no test or direct observation — see Behavior-Unverified Item |
| 9 | `.gitignore` covers build output, generated files, Python caches, secrets (with `.env.example` kept), OS/editor junk, videos, and the research cache | ✓ VERIFIED | `git check-ignore` sweep: `.pio/x`, `compile_commands.json`, `site/index.html`, `secrets.txt`, `key.pem`, `id_rsa`, `video.mp4`, `.planning/research/.cache/x.json` ignored; `.env.example`, `README.md` visible; `test_gitignore.py` 11 tests pass |
| 10 | The research cache is ignored and untracked | ✓ VERIFIED | `.planning/research/.cache/` matches `.gitignore`; `git ls-files .planning/research/.cache/` returns 0 paths |
| 11 | LFS routes exactly the eight declared extensions; docs images and videos remain non-LFS | ✓ VERIFIED | `git check-attr filter`: lfs for pdf/step/stl/fzz/zip/bin/elf/vcd; unspecified for png/jpg/jpeg/webp/svg/mp4 |
| 12 | The large-file guard is LFS-aware with no exclusion list | ✓ VERIFIED | Installed `check_added_large_files.py` calls `filter_lfs_files()` via `git check-attr filter`; `.pre-commit-config.yaml` sets only `--maxkb=1024`; hook passes on the full tree |
| 13 | A staged secret is blocked before commit and redacted | ✓ VERIFIED | Fresh canary this pass: generated RSA key staged in a throwaway repo; `gitleaks git --pre-commit --redact --staged --verbose` exits 1 with `RuleID: private-key`, `Finding: REDACTED`, and zero raw-key lines in output |
| 14 | The hook and CI scan cannot mutate history and both pass `--redact` | ✓ VERIFIED | Workflow contains no `git push`/`git commit`/write API call; `test_never_writes_back_to_the_repository` and `test_redacts_detected_secrets` pass |
| 15 | The full-history scan covers every ref (`fetch-depth: 0`, `--log-opts="--all"`) | ✓ VERIFIED | Workflow read directly; `test_checks_out_full_history` and `test_scans_every_ref` pass; local scan covered 88 commits; CI job green |
| 16 | gitleaks uses default rules; no `.gitleaks.toml` exists | ✓ VERIFIED | `.gitleaks.toml` absent; no allowlist is committed |
| 17 | `REUSE.toml` declares the MIT/CC-BY-4.0 split once and `reuse lint` is clean; PR templates stay on the MIT catch-all | ✓ VERIFIED | `reuse --no-multiprocessing lint` → 75/75 files compliant; `reuse spdx` shows homework template MIT, README/AGENTS CC-BY-4.0; `.reuse/dep5` absent |
| 18 | `LICENSE` is MIT with one handle-only copyright line; `NOTICE` carries attribution and trademark sections | ✓ VERIFIED | `Copyright (c) 2026 VLoktiev-EMB` is the only copyright line; NOTICE has MADR attribution, other-third-party, and trademark sections; 15 hygiene tests pass |
| 19 | `LICENSES/MIT.txt` and `LICENSES/CC-BY-4.0.txt` exist with canonical texts | ✓ VERIFIED | Both files present; CC-BY text carries the canonical heading; `reuse lint` resolves both |
| 20 | `REUSE.toml` replaces `.reuse/dep5`; the two formats never coexist | ✓ VERIFIED | `.reuse/` absent; `test_reuse_toml_exists_and_dep5_does_not` passes |
| 21 | Each PR template has rows under every required Definition-of-Done heading; the checker fails on an empty section | ✓ VERIFIED | `check_pr_templates.py` PASS; `test_empty_dod_section_exits_1` and `test_required_dod_items_present_per_type` pass |
| 22 | The shared header is byte-identical across the three templates; the checker compares only that slice | ✓ VERIFIED | SHA-256 of the three header slices is identical; `test_header_mismatch_exits_1_and_names_file` passes |
| 23 | `check_pr_templates.py` is read-only and idempotent | ✓ VERIFIED | Two consecutive runs exit 0 with `git status --porcelain` unchanged; `test_second_run_is_identical_and_read_only` passes |
| 24 | No default PR template exists at any fallback path | ✓ VERIFIED | `find` returns only `.github/PULL_REQUEST_TEMPLATE/`; checker PASS; `test_stray_default_template_exits_1` covers a stray default |
| 25 | Empty, null, and separator-less homework IDs are rejected; the documented regex is applied | ✓ VERIFIED | `test_homework_id.py`: exactly one anchored pattern, canonical IDs match, `""`/`police-flasher`/mixed-case/dotted/non-ASCII rejected |
| 26 | Homework IDs and paths are ASCII-only | ✓ VERIFIED | `^[0-9]+_[0-9]+-[a-z0-9-]+$` documented; non-ASCII probe rejected; ASCII path rule documented in AGENTS.md |
| 27 | `AGENTS.md` stays under 300 lines and `.claude/CLAUDE.md` imports it without restating rules | ✓ VERIFIED | AGENTS.md 198 lines; `.claude/CLAUDE.md` line 1 is `@AGENTS.md`; 12 adapter/ceiling/vocabulary tests pass |
| 28 | Every AGENTS.md rule carries severity and enforcement; routing targets exist or are marked planned | ✓ VERIFIED | 20 `[MUST]`, 4 `[SHOULD]`, 21 `[ENFORCED: …]`; `test_carries_the_full_enforcement_vocabulary` and `test_planned_paths_are_marked_planned` pass |
| 29 | GSD is a portable MUST, the precedence sentence exists, and generator blocks are preserved verbatim | ✓ VERIFIED | AGENTS.md change-workflow rule and precedence section present; `test_preserves_every_generator_block` passes |
| 30 | `README.md` states the license split, links the policy surfaces, and shows early-phase status | ✓ VERIFIED | Links to AGENTS.md, decisions index, LICENSE, NOTICE, LICENSES/; explicit MIT vs CC-BY-4.0 split and "Phase 1 of 11" |
| 31 | Five sequential MADR ADRs exist with a matching status index | ✓ VERIFIED | 0001–0005 plus the closeout ADR 0006 and the index; `test_numbers_are_contiguous_from_one`, `test_index_has_a_row_for_every_record`, `test_index_titles_match_record_titles` pass. The plan's parenthetical "Phase 2 continues at 0006" is superseded by ADR-0006 (numbering stays sequential; next is 0007) |
| 32 | Every ADR follows MADR 4.0 full section order | ✓ VERIFIED | `test_every_record_has_all_sections_in_madr_order` and `test_decision_outcome_opens_with_the_chosen_option` pass, including ADR-0006 |
| 33 | ADR-0004 records the REUSE.toml substitution and the stale SIM-02 reference | ✓ VERIFIED | ADR-0004 §Consequences/More Information records `.reuse/dep5` deprecation, the substitution, and the stale SIM-02 pointer; `test_adr_0004_records_the_license_substitutions` passes |
| 34 | ADR-0003 records tag mutability, the approvals trigger, and `.planning/` publicity | ✓ VERIFIED | ADR-0003 records all three accepted gaps; `test_adr_0003_records_the_git_policy_audit_gaps` passes |
| 35 | `tag_homework.sh` refuses an existing tag locally or on origin and never force-updates | ✓ VERIFIED | 5 refusal/creation tests pass (offline bare remote); source has no force flag; the live `ls-remote` branch is code-present but its live behaviour is deferred with UAT test 3 |
| 36 | `tag_homework.sh` checks preconditions in order, prints one PASS/FAIL line each, and returns a single aggregate exit code | ✓ VERIFIED | Source order 1–5 verified by reading; `test_missing_homework_directory_is_refused` and `test_homework_absent_from_the_tag_target_is_refused` pass; live `gh` gate deferred with UAT test 3 |
| 37 | The tag script never rewrites or moves a tag; no force flag appears | ✓ VERIFIED | `test_source_has_no_forced_tag_or_push`; no `--force`/`--force-with-lease`; push is a single `refs/tags/$TAG` |
| 38 | Published history uses the public handle only: no real name, institution, or email in commit metadata (AGENTS.md MUST; FOUND-06; phase goal) | PASSED (override) | Factually re-confirmed: all three commits carry `Volodymyr Loktiev <23013718+4oc3p@users.noreply.github.com>` and the GitHub API returns `name: "Volodymyr Loktiev"` for account `4oc3p`. Reclassified because ADR-0006 accepts the public account display name as the commit identity and 01-SECURITY.md records T-1-15 (accept) and R-1-02 with `threats_open: 0`. Override: external constraint, irreparable, accepted by VLoktiev-EMB on 2026-10-23 |

**Prohibitions**

| # | Prohibition | Status | Evidence |
| --- | ----------- | ------ | -------- |
| P1 | Published legal artifacts and commit trailers contain no real name, institution, or PII (test-tier) | ✓ VERIFIED | LICENSE/NOTICE/REUSE.toml carry only `VLoktiev-EMB`; no commit trailers exist; `test_published_files_contain_no_configured_git_identity` passes. The commit-metadata surface is the documented override above, not an undetected failure |
| P2 | No PR template requires AI-assistance disclosure (test-tier) | ✓ VERIFIED | `test_no_required_row_demands_ai_disclosure` passes; no template row demands it |
| P3 | No internal course material or original assignment text is committed (judgment-tier) | ✓ VERIFIED | UAT test 6 records pass; the tree contains only infrastructure and paraphrased planning material |
| P4 | No document endorses a direct-push or force-push workflow (judgment-tier) | ✓ VERIFIED | UAT test 6 records pass; AGENTS.md forbids both; no alternative tag/push path is documented |

**Score:** 41/42 must-haves verified (1 present, behavior-unverified; 1 override)

### Deferred Items

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | Real-origin behaviour of `scripts/tag_homework.sh` (remote tag lookup and `gh` merged-PR gate) | Phase 11 | PILOT-01 delivers homework 1.3; its merged homework PR is the first point where the gate can run. UAT test 3 is recorded as an explicit Deferred Follow-Up. |

### Advisory (New Scope, Unevidenced)

None. Every finding in this report is backed by a reproducible command, a live API response, or a recorded UAT result. The absence of an automated commit-identity guard is documented in ADR-0006 §Confirmation as a deliberate, accepted state (any future guard must allow the public account display name), not an unevidenced defect.

### Required Artifacts

All 38 artifacts declared across the eight plans pass the artifact verifier (`all_passed: true`, 38/38: 6 + 3 + 3 + 6 + 5 + 5 + 8 + 2). ADR-0006 is an additional closeout artifact outside the declared set and is present, substantive, and indexed.

| Artifact | Expected    | Status | Details |
| -------- | ----------- | ------ | ------- |
| `policy/ruleset-main.json`, `policy/repository.json` | Committed policy subset | ✓ VERIFIED | Exists, substantive, matches live state (`--check` exit 0) |
| `scripts/check_policy.py` | Read-only/apply drift checker | ✓ VERIFIED | `READ_ONLY` projection wired; exit codes tested; live run exits 0 |
| `scripts/check_pr_templates.py` | Marker-slice drift checker | ✓ VERIFIED | Read-only; PASS on the real tree; negative fixtures fail |
| `scripts/tag_homework.sh` | Precondition-gated tagger | ✓ VERIFIED | Mode 755; fails closed on every local precondition; live network path deferred |
| `.gitignore`, `.gitattributes` | Ignore and LFS routing | ✓ VERIFIED | Exercised independently with `git check-ignore` / `git check-attr` |
| `.pre-commit-config.yaml` | Pinned hooks plus generated-files guard | ✓ VERIFIED | Six hooks pass on the full tree |
| `.github/workflows/security.yml` | Full-history scan and reuse lint | ✓ VERIFIED | Both jobs green on runs 39998933792, 40000049776, 40000212188, 40000791067, 40000898555 |
| `.github/PULL_REQUEST_TEMPLATE/{homework,infra,docs}.md` | Three type-specific templates | ✓ VERIFIED | Header byte-identical; distinct DoDs; no default template |
| `AGENTS.md`, `.claude/CLAUDE.md`, `README.md` | Rulebook, adapter, front door | ✓ VERIFIED | 198 lines; line-1 import; precise license statement |
| `LICENSE`, `NOTICE`, `LICENSES/*`, `REUSE.toml` | License boundary | ✓ VERIFIED | `reuse lint` 75/75; handle-only copyright |
| `docs/decisions/` (0001–0006, template, index) | Five planned MADRs plus the accepted-risk record | ✓ VERIFIED | Sequential, index-consistent; ADR-0006 present and indexed |
| `scripts/tests/` | Suite | ✓ VERIFIED | 110 tests pass |

### Key Link Verification

`gsd_run` `verify key-links` resolves 7 of 12 links by pattern and flags 5 as "Source file not found" because those plans put prose in the `from` field (for example `scripts/check_policy.py --apply` or `AGENTS.md routing table`). Manual tracing confirms every one is wired.

| From | To  | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `scripts/check_policy.py` | live ruleset 25632456 | `gh api` GET + normalized projection | ✓ WIRED | Live run exits 0; drift tests cover missing/extra/weakened rules |
| `scripts/check_policy.py --apply` | live repository settings | `PUT` ruleset, `PATCH` repository, re-read | ✓ WIRED | Apply path present; UAT test 2 confirms idempotence |
| `.gitattributes` | pre-commit size guard | `filter=lfs` recognized by the hook | ✓ WIRED | Installed hook calls `filter_lfs_files()` via `git check-attr` |
| `.pre-commit-config.yaml` gitleaks hook | `.github/workflows/security.yml` | both pinned 8.30.1 with `--redact`, staged vs full history | ✓ WIRED | Local canary blocks and redacts; CI job green |
| `REUSE.toml` | `LICENSES/*.txt` | SPDX identifiers resolve to required filenames | ✓ WIRED | `reuse lint` reports 0 unused licenses |
| `README.md` | `LICENSE` / `NOTICE` | explicit links and split statement | ✓ WIRED | Both links resolve in the tree |
| `scripts/check_pr_templates.py` | three templates | maker byte slice | ✓ WIRED | PASS on the real tree; negative fixtures fail |
| `.claude/CLAUDE.md` | `AGENTS.md` | line-1 `@AGENTS.md` import | ✓ WIRED | Import is the first substantive line; no restated rules |
| `AGENTS.md` routing table | scripts and `docs/decisions/README.md` | task→artifact routes | ✓ WIRED | Every named file exists; planned paths marked |
| `docs/decisions/README.md` | ADR files | status index | ✓ WIRED | Index matches frontmatter; test enforces it |
| `scripts/tag_homework.sh` | `origin` tags | `rev-parse` + `ls-remote` + `gh pr list` | ✓ WIRED (live gh path deferred) | Local bare-remote test creates the tag at `origin/main` and pushes once |
| `AGENTS.md` tag rule | `scripts/tag_homework.sh` | rulebook routes tag creation through the script | ✓ WIRED | Rule and script agree; no alternative tag path documented |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `scripts/check_policy.py` | live ruleset / repository settings | `gh api` against `VLoktiev-EMB/homeworks` | Yes — live run exits 0 with per-setting PASS lines | ✓ FLOWING |
| `scripts/check_pr_templates.py` | template bytes | real repository tree | Yes — PASS on the real tree | ✓ FLOWING |
| `scripts/tag_homework.sh` | tag target | `refs/remotes/origin/<default>` | Yes — bare-remote test tags the `origin/main` commit | ✓ FLOWING (local remote; live path deferred) |
| `.gitignore` / `.gitattributes` | path decisions | git's ignore/attribute engine | Yes — exercised with `git check-ignore` / `git check-attr` | ✓ FLOWING |
| gitleaks hook / workflow | staged and historical content | git object store | Yes — canary blocks a private key; 88-commit scan is clean; CI green | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Full suite | `python3 -m unittest discover -s scripts/tests` | 110 tests, OK | ✓ PASS |
| PR template contract | `python3 scripts/check_pr_templates.py` | PASS, exit 0 | ✓ PASS |
| Live policy drift | `python3 scripts/check_policy.py --check` | PASS, exit 0 | ✓ PASS |
| License split | `reuse --no-multiprocessing lint` | Compliant, 75/75 files | ✓ PASS |
| Local gate | `pre-commit run --all-files` | Six hooks Passed | ✓ PASS |
| Full-history secret scan | `gitleaks git --redact --log-opts="--all"` | 88 commits, no leaks | ✓ PASS |
| Secret detection canary | generated RSA key staged in a throwaway repo, `gitleaks git --pre-commit --redact --staged` | exit 1, `private-key`, `REDACTED`, 0 raw-key lines | ✓ PASS |
| Ignore coverage | `git check-ignore` over positive and negative paths | all as expected | ✓ PASS |
| LFS routing | `git check-attr filter` over 14 paths | 8 LFS, 6 unspecified | ✓ PASS |
| CI execution | `gh run list` / `gh run view` | every security run success | ✓ PASS |
| Merged history | `gh pr view 1,2` + `git log origin/main` | PR #1 → e2dd499, PR #2 → 69c2434; one commit each; branch deleted | ✓ PASS |
| Live ruleset | `gh api repos/.../rulesets/25632456` | active, bypass [], six rules, squash-only | ✓ PASS |
| Commit identity | `git log --format='%an <%ae>' origin/main` + `gh api users/4oc3p` | display name matches the profile name; noreply address | PASSED (override) |

### Probe Execution

Not applicable — this phase declares no `scripts/*/tests/probe-*.sh` and its plans name no probes.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| FOUND-02 | 01-06 | Homework IDs follow `module_lesson-name` and stay stable | ✓ SATISFIED | Pattern documented and applied by `test_homework_id`; ASCII rule documented |
| FOUND-03 | 01-01, 01-08 | `main` protected; every change via branch + PR; no force-push or history rewrite | ✓ SATISFIED | Live active ruleset with empty bypass and six rules; `--check` exit 0; direct-push rejection recorded (UAT test 1) |
| FOUND-04 | 01-01, 01-08 | Conventional Commits; squash merges; `hw/<id>` tag after merge; branch deleted | ✓ SATISFIED (live tag path deferred) | Squash-only rule live; PR #1/#2 subjects conventional; one commit per PR; branch deleted. The real-tag check is a recorded Phase 11 deferral |
| FOUND-05 | 01-05 | Three PR templates with shared header and type-specific DoD | ✓ SATISFIED | Templates and checker verified; no default template |
| FOUND-06 | 01-04, 01-06 | MIT, NOTICE, third-party attribution; no internal material or PII | ✓ SATISFIED (override on the commit-metadata surface) | Licensing half verified: MIT/CC-BY split, NOTICE, `reuse lint` 75/75. The PII half: legal files carry only the handle; the commit display name is accepted by ADR-0006 / R-1-02 |
| FOUND-07 | 01-02, 01-03 | gitleaks locally and over full history in CI; ignore/attribute coverage | ✓ SATISFIED | Local canary blocks and redacts; 88-commit scan clean; every CI job green |
| FOUND-08 | 01-02 | LFS only for large non-diffable binaries; site assets normal; videos linked | ✓ SATISFIED | `git check-attr` sweep matches the policy exactly |
| FOUND-10 | 01-06 | AGENTS.md canonical rulebook; `.claude/CLAUDE.md` imports it | ✓ SATISFIED | 198 lines, full vocabulary, thin adapter, contract tests |
| TOOL-07 | 01-07 | Infrastructure decisions recorded as MADR ADRs | ✓ SATISFIED | Five planned MADRs plus ADR-0006, template, and index, all tested |

No orphaned requirements: every Phase 1 ID in REQUIREMENTS.md (`FOUND-02`–`FOUND-08`, `FOUND-10`, `TOOL-07`) is claimed by at least one plan.

### Decision Coverage

All trackable CONTEXT.md decisions are honored by shipped artifacts: 27/27 (no `not_honored` entries).

### Test Quality Audit

| Test File | Linked Req | Active | Skipped | Circular | Assertion Level | Verdict |
|-----------|-----------|--------|---------|----------|-----------------|---------|
| `test_check_policy.py` | FOUND-03/04 | 13 | 0 | No | Behavioral (projection, drift, mutation-free) | ✓ |
| `test_gitignore.py` | FOUND-07/08 | 11 | 0 | No | Value (real `git check-ignore`/`check-attr`) | ✓ |
| `test_security_workflow.py` | FOUND-07 | 18 | 0 | No | Value (token/contract assertions) | ✓ |
| `test_check_pr_templates.py` | FOUND-05 | 11 | 0 | No | Value + negative fixtures | ✓ |
| `test_license_hygiene.py` | FOUND-06 | 15 | 0 | No | Value (SPDX, identity) | ✓ — scoped to files, not commit metadata; the commit surface is ADR-0006's accepted risk |
| `test_agents_md.py` | FOUND-10 | 12 | 0 | No | Value | ✓ |
| `test_homework_id.py` | FOUND-02 | 6 | 0 | No | Value (two-sided regex probes) | ✓ |
| `test_adrs.py` | TOOL-07 | 18 | 0 | No | Value | ✓ |
| `test_tag_homework.py` | FOUND-04 | 6 | 0 | No | Behavioral (real script, local remote) | ✓ — remote path offline-only |

**Disabled tests on requirements:** 0.
**Circular patterns detected:** 0 (the `write_text` calls create temp fixtures, not expected values from the system under test).
**Insufficient assertions:** 0.

### Anti-Patterns Found

No `TBD`, `FIXME`, or `XXX` debt marker exists in any file changed by this phase. (The `XXXXXX` token in `scripts/review_smoke_test.sh` is an `mktemp` template, not a debt marker.) No stub or orphaned artifact was found.

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| git history | author field | Public account display name in three published commits | ℹ️ Info (accepted) | Recorded as ADR-0006 and accepted risk R-1-02; irreparable under the no-rewrite rule. Not a blocker |
| `01-UAT.md` | test 5 | Squash-merge passed, but the same-region clause was explicitly not exercised | ⚠️ Warning | Truth 8 remains insufficient_spec (behavior-unverified) |
| `docs/decisions/README.md` | "Next number: 0007 (reserved …)" | Pre-reserving a number diverges from sequential-on-acceptance | ℹ️ Info | Documentation-only; no number is reserved in code |
| `scripts/check_policy.py` | projection | Cannot detect weakening of server fields the committed file does not declare | ℹ️ Info | Documented in ADR-0003 as an unverified assumption; ruleset core still fails closed |
| `scripts/tests/test_adrs.py` | section-order check | Can miss one missing heading if another is duplicated | ℹ️ Info | Test-quality only; the real ADRs have the correct order |
| `.pre-commit-config.yaml` | gitleaks repo | `language: golang` may download an unpinned Go toolchain on a fresh machine | ℹ️ Info | Environment-dependence only; hook rev is pinned |
| `AGENTS.md` | branch scopes | `infra`, `state`, `config` are not phase-plan or homework IDs | ℹ️ Info | A reader could conflate the two rules; both are review-enforced |
| `01-VALIDATION.md` | whole file | Still `status: draft`, `nyquist_compliant: false` | ℹ️ Info | Process tracking artifact not updated; does not affect repository rules |
| `.planning/REQUIREMENTS.md` | Phase 1 checkboxes | Requirement checkboxes and traceability remain `Pending` | ℹ️ Info | Tracking drift only; the implementation exists |
| `homeworks.code-workspace`, `scripts/review_smoke_test.sh`, `.planning/intel/API-SURFACE.md` | whole files | Committed in the Phase 1 squash but declared in no plan; the workspace is a Phase 5 stub | ℹ️ Info | No effect on the Phase 1 goal |
| `docs/decisions/0006-public-commit-identity.md` | Confirmation | No automated commit-identity guard exists | ℹ️ Info | Deliberate per ADR-0006; any future guard must allow the public account display name |

`01-SECURITY.md` now records 16 threats with `threats_open: 0` (ASVS L1). T-1-15 closes the previously missing commit-metadata surface; the former T-1-13 file-content gap is therefore covered by a dedicated accepted threat rather than an unstated assumption. `COVERAGE.md` records 18 GitHub REST capabilities (7 INTEGRATE, 11 reasoned OPT-OUT) for the surface used by `check_policy.py`; its claims match the script.

### Behavior-Unverified Item (Human Check Recommended)

**Truth:** Two pull requests touching the same region cannot both merge untouched; the required-linear-history rule forces the second to update its base first.

**Reason:** `insufficient_spec` (the plan tags this truth `verification: backstop`).

**Test:** Create a second pull request that edits the same region as an already-merged pull request and inspect its mergeability before updating its base.
**Expected:** GitHub reports a conflict or a required base update and refuses the merge until the branch is updated.
**Why human:** UAT test 5 records the squash-merge half as pass but states explicitly that the second-PR base-update behaviour was not exercised. PR #2 was documentation-only and did not exercise it. No held-out/property-based test covers it, and presence of the live ruleset is not explicit evidence for a non-inferable truth.

### Human Verification Required

1. **Same-region second pull request**

   **Test:** Create a second pull request that edits the same lines as an already-merged pull request, then inspect its mergeability before updating its base.
   **Expected:** GitHub reports a conflict or a required base update and refuses the merge until the branch is updated.
   **Why human:** GitHub-side enforcement; cannot be reproduced offline and no test exercises it.

### Gaps Summary

No gaps remain. The previous pass's single gap — published commit metadata carrying the public account's display name — is reclassified as `PASSED (override)`.

**Why the accepted risk is sufficient.** The finding was never an implementation defect: the local identity was already the handle (`user.name = 4oc3p`, handle-based noreply address), and GitHub wrote the profile display name server-side during web/squash-merge. The three published commits cannot be rewritten — the active ruleset rejects force-pushes and `AGENTS.md` forbids history rewrites — so no compliant action can remove the name. `ADR-0006` records the decision to accept the public account display name as the repository's commit identity, and `01-SECURITY.md` records it as threat `T-1-15` with disposition `accept` and accepted risk `R-1-02`, with `threats_open: 0`. Under the secure-phase classification contract an explicitly accepted, ADR-recorded risk is closed. The verifier therefore applies the override mechanism rather than re-reporting the same irreparable item as an open blocker; the residual divergence from the literal `AGENTS.md` wording is itself recorded in ADR-0006 §Consequences.

The remaining open item is not a gap but an evidence gap: the same-region pull-request backstop (truth 8) has no test or direct observation. It drives `status: human_needed` and is listed under Human Verification above. The real-tag path of `scripts/tag_homework.sh` is a recorded Phase 11 deferral (UAT test 3), not an unverified gap.

Everything else in the phase is in place and exercised:

- **policy:** live active ruleset with empty bypass and six rules; `check_policy.py --check` exits 0; a direct push was rejected (UAT test 1); two PRs each produced exactly one commit on `main`;
- **secrets:** a staged RSA key is blocked and redacted locally (fresh canary this pass); the full-history CI scan is green over 88 commits;
- **licensing:** MIT plus CC-BY-4.0 declared once, `reuse lint` 75/75, CI enforces it, no configured identity appears in the legal files;
- **assets:** LFS routing covers exactly the eight declared extensions, images and videos stay normal objects, videos are ignored;
- **contribution:** three templates share a byte-identical header with distinct DoDs and no default template; the rulebook is canonical at 198 lines with the adapter importing it; the tag script fails closed locally, with the live-origin check deferred to Phase 11.

---
_Verified: 2026-10-23T18:23:19Z_
_Verifier: Claude (gsd-verifier)_
