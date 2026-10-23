---
phase: "1"
slug: "repository-foundation-and-policy-gate"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-23"
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` (no pytest installed; adding one is Phase 6 scope) |
| **Config file** | none — Wave 0 creates `scripts/tests/` |
| **Quick run command** | `python3 -m unittest discover -s scripts/tests -v` |
| **Full suite command** | `python3 -m unittest discover -s scripts/tests -v && python3 scripts/check_pr_templates.py && python3 scripts/check_policy.py --check && pre-commit run --all-files` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m unittest discover -s scripts/tests -v`
- **After every plan wave:** Run the full suite command
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

Derived from the final plan frontmatter: the Plan and Wave columns are regenerated from each
PLAN.md's `plan` / `wave` / `requirements` fields, and the plans are authoritative. Each row's
plan is the one whose tasks actually implement that requirement; regenerate this table if a
plan's frontmatter changes.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-01-* | 01 | 1 | FOUND-03 | T-1-01 | `bypass_actors` stays `[]`; live rules equal committed projection | integration | `python3 scripts/check_policy.py --check` | ❌ W0 | ⬜ pending |
| 1-01-* | 01 | 1 | FOUND-04 | T-1-01 | squash-only merges, `delete_branch_on_merge: true` asserted | integration | `python3 scripts/check_policy.py --check` | ❌ W0 | ⬜ pending |
| 1-02-* | 02 | 2 | FOUND-07 | T-1-02 | `.gitignore` covers `.pio/`, `.env`, `compile_commands.json`, `site/`, `.planning/research/.cache/` | unit | `python3 -m unittest scripts.tests.test_gitignore` | ❌ W0 | ⬜ pending |
| 1-02-* | 02 | 2 | FOUND-08 | T-1-09 | `.gitattributes` routes every LFS extension to `filter: lfs`; docs images and videos are **not** LFS-routed | integration | `git check-attr filter -- *.pdf *.step *.stl *.fzz *.zip *.bin *.elf *.vcd docs/assets/x.png report/video.mp4` | ✅ | ⬜ pending |
| 1-03-* | 03 | 2 | FOUND-07 | T-1-02 | gitleaks blocks a staged fake secret; `--redact` keeps it out of logs | integration | `pre-commit run gitleaks --all-files` (non-zero on the planted canary) | ✅ manual, once | ⬜ pending |
| 1-03-* | 03 | 2 | FOUND-07 | T-1-08 | the full-history workflow pins `fetch-depth: 0`, the all-refs log options, and `--redact` | unit | `python3 -m unittest scripts.tests.test_security_workflow` | ❌ W0 | ⬜ pending |
| 1-04-* | 04 | 2 | FOUND-06 | T-1-03 | `LICENSE`, `NOTICE`, `LICENSES/*`, `REUSE.toml` present; split declared | integration | `reuse lint` (local once; CI in Phase 8) | ❌ W0 | ⬜ pending |
| 1-04-* | 04 | 2 | FOUND-06 | T-1-03 | no PII: public handle only in `LICENSE` / `NOTICE` / `REUSE.toml` | unit | `python3 -m unittest scripts.tests.test_license_hygiene` | ❌ W0 | ⬜ pending |
| 1-05-* | 05 | 2 | FOUND-05 | T-1-10 | three templates exist; shared header identical across all three | unit | `python3 -m unittest scripts.tests.test_check_pr_templates` | ❌ W0 | ⬜ pending |
| 1-05-* | 05 | 2 | FOUND-05 | T-1-10 | no default `pull_request_template.md` at any of the three paths | unit | same | ❌ W0 | ⬜ pending |
| 1-07-* | 07 | 2 | TOOL-07 | T-1-12 | five ADRs, MADR frontmatter, sequential numbering, index agrees | unit | `python3 -m unittest scripts.tests.test_adrs` | ❌ W0 | ⬜ pending |
| 1-08-* | 08 | 2 | FOUND-04 | T-1-07 | `tag_homework.sh` refuses an existing `hw/<id>` tag; no force flags in source | unit | `python3 -m unittest scripts.tests.test_tag_homework` | ❌ W0 | ⬜ pending |
| 1-06-* | 06 | 3 | FOUND-10 | T-1-13 | `AGENTS.md` exists, ≤ 300 lines, carries `[MUST]`/`[ENFORCED: …]` vocabulary; `.claude/CLAUDE.md` imports `@AGENTS.md` and does not restate rules | unit | `python3 -m unittest scripts.tests.test_agents_md` | ❌ W0 | ⬜ pending |
| 1-06-* | 06 | 3 | FOUND-02 | — | homework ID convention documented in `AGENTS.md` and test-proven (empty and separator-less rejected, canonical form accepted) | unit | `python3 -m unittest scripts.tests.test_homework_id` | ❌ W0 | ⬜ pending |
| 1-06-* | 06 | 3 | FOUND-02 | — | the same convention is enforced mechanically by the Phase 4 schema (not Phase 1) | manual | — documented only | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `scripts/tests/__init__.py` — make the directory importable as a package
- [ ] `scripts/tests/test_check_pr_templates.py` — marker equality, absence of a default template, per-type DoD present
- [ ] `scripts/tests/test_check_policy.py` — normalization and diff logic against a fixture (no network)
- [ ] `scripts/tests/test_agents_md.py` — line ceiling, import presence, tag vocabulary
- [ ] `scripts/tests/test_adrs.py` — frontmatter keys, sequential numbers, index agreement
- [ ] `scripts/tests/test_gitignore.py` — pattern presence for build output, secrets, generated files
- [ ] `scripts/tests/test_license_hygiene.py` — handle-only copyright lines, no real name or institution
- [ ] `scripts/tests/fixtures/ruleset-live.json` — a captured live GET payload for offline diff tests
- [ ] `pre-commit` upgraded 4.6.0 → 4.7.0 (the pinned `minimum_pre_commit_version` refuses to run otherwise)
- [ ] `git-lfs` installed (LFS attributes are inert without the binary)
- [ ] `gitleaks` available (Homebrew 8.30.1, or the `language: golang` hook builds it)
- [ ] Framework install: none — `unittest` is stdlib

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| A direct push to `main` is rejected end-to-end | FOUND-03 | Requires an actual rejected `git push` against the live remote; deliberately not automated to avoid CI writing to the default branch | On a scratch clone: `git checkout main && git commit --allow-empty -m test && git push origin main` → rejected with a ruleset-protected-branch error; discard the commit |
| A staged secret is blocked before commit | FOUND-07 | Requires an interactive `git add` + hook run with a synthetic credential | Plant `AKIAIOSFODNN7EXAMPLE` in a scratch file, `git add`, `pre-commit run gitleaks --all-files` → non-zero, secret redacted in output |
| Secret scanning / push protection are actually enabled | FOUND-03 | Live org setting; enabling is a one-time API/UI action with billing implications | `gh api repos/VLoktiev-EMB/homeworks --jq '.security_and_analysis'` → all `status: "enabled"` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
