# Phase 1: Repository Foundation and Policy Gate - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-23
**Phase:** 1-Repository Foundation and Policy Gate
**Areas discussed:** Rulebook split, Git policy as code, Licensing & identity, ADR set &
numbering, Ignore & attribute coverage, Secret-scanning policy, PR template contract,
Public README now

---

## Rulebook split

| Option | Description | Selected |
|--------|-------------|----------|
| Thin CLAUDE.md + docs | ~30-line adapter with `@AGENTS.md`; rules to AGENTS.md; stack material to `docs/standards/` | ✓ |
| Thin CLAUDE.md, defer docs | Same adapter, but stack material stays only in `.planning/research/` | |
| Keep CLAUDE.md as project doc | Keep the 772-line project/stack overview and import AGENTS.md | |

**User's choice:** Thin CLAUDE.md + docs
**Notes:** Drops ~700 lines from every session's context; the material becomes publishable in Phase 5.

| Option | Description | Selected |
|--------|-------------|----------|
| Hard 200-line cap | Root AGENTS.md under 200 lines; nest only when a rule differs | |
| ~300-line ceiling | REQUIREMENTS as written; room for tags, examples, routing table | ✓ |
| No fixed cap | Optimize for completeness now | |

**User's choice:** ~300-line ceiling
**Notes:** Best-practice guidance (<200) was rejected in favor of the recorded requirement.

| Option | Description | Selected |
|--------|-------------|----------|
| Severity + mechanism | `[MUST]`/`[SHOULD]` plus `[ENFORCED: pre-commit | CI | review]` | ✓ |
| Flat enforcement tags | One dimension: `[ENFORCED:CI]`, `[HUMAN]`, `[ADVISORY]` | |
| Table-driven, no inline tags | "Rule | Enforcement | Check" tables only | |

**User's choice:** Severity + mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Rules + commands + routing | Rules, canonical commands, layout, routing table; depth behind links | ✓ |
| Everything agent-facing inline | Report structure and quality gates inline too | |
| Rules + routing, commands linked | Even commands are referenced, not written out | |

**User's choice:** Rules + commands + routing

| Option | Description | Selected |
|--------|-------------|----------|
| Root only, nest when needed | No nested file now; allow `lib/AGENTS.md` when the dependency rule differs | ✓ |
| Root + lib/AGENTS.md now | Create the dependency-rule stub in Phase 1 | |
| Root + per-homework | One rulebook per homework | |

**User's choice:** Root only, nest when needed

| Option | Description | Selected |
|--------|-------------|----------|
| Portable rule + Claude adapter | AGENTS.md states the workflow rule; CLAUDE.md keeps command mechanics | ✓ |
| GSD entry points in AGENTS.md | Rulebook lists the `/gsd-*` commands | |
| Orthogonal, no cross-reference | No file references the other | |

**User's choice:** Portable rule + Claude adapter
**Notes:** User corrected the premise: **Antigravity can run `/gsd-*` commands**, so GSD is not Claude-only. Rule recorded as a portable MUST in AGENTS.md; AGENTS.md wins conflicts.

---

## Git policy as code

| Option | Description | Selected |
|--------|-------------|----------|
| Ruleset JSON + check/apply script | Commit the ruleset; `--check` diffs live vs committed; `--apply` re-applies; CI in Phase 8 | ✓ |
| Ruleset as code + CI verify now | Same plus a PR workflow running `--check` | |
| Documentation only | Record settings and the `gh api` command in `docs/standards/git.md` | |

**User's choice:** Ruleset JSON + check/apply script

| Option | Description | Selected |
|--------|-------------|----------|
| Keep 0 approvals, documented trigger | Solo self-merge allowed; raise to 1 when a second maintainer joins | ✓ |
| 1 approval + admin bypass | Stronger gate, weaker audit story | |
| 1 approval, no bypass | Blocks work until a second reviewer exists | |

**User's choice:** Keep 0 approvals, documented trigger

| Option | Description | Selected |
|--------|-------------|----------|
| Type prefixes matching templates | `hw/<id>`, `infra/<slug>`, `docs/<slug>` select the template | ✓ (hybrid) |
| Conventional-commit prefixes | `feat/`, `fix/`, `chore/`, `docs/` | |
| No branch convention | Only commit messages governed | |

**User's choice:** Anchor-only hybrid — `hw/<id>` → homework, `docs/<slug>` → docs, all other prefixes free-form and defaulting to infra; full mapping revisited after the pilot.
**Notes:** User asked whether `feat`/`chore` could coexist; accepted that they can, but the complete mapping is unknowable before real branches exist.

| Option | Description | Selected |
|--------|-------------|----------|
| Validated tag script | `scripts/tag_homework.sh` verifies merged PR and unused tag | ✓ |
| Manual, documented only | Document `git tag hw/<id>` and push | |
| Auto-tag workflow now | Actions workflow tags on merged `hw/<id>` PRs | |

**User's choice:** Validated tag script

| Option | Description | Selected |
|--------|-------------|----------|
| Ruleset + security settings | Also assert push protection, secret scanning, auto-delete-branches | ✓ |
| Ruleset only, settings documented | Settings recorded as manual setup steps | |
| No settings coverage | Rely on gitleaks alone | |

**User's choice:** Ruleset + security settings

---

## Licensing & identity

| Option | Description | Selected |
|--------|-------------|----------|
| MIT code + CC-BY-4.0 content | GitHub OSPO mixed-repository pattern | ✓ |
| Uniform MIT | One license for code and prose | |
| MIT code + CC-BY-SA content | Share-alike for reports/docs | |

**User's choice:** MIT code + CC-BY-4.0 content

| Option | Description | Selected |
|--------|-------------|----------|
| Public handle everywhere | Handle in LICENSE, NOTICE, and report metadata; no real name or institution | ✓ |
| Real name + institution | Conventional academic metadata; permanent public PII | |
| Handle in code, name in reports | Split identity by artifact type | |

**User's choice:** Public handle everywhere

| Option | Description | Selected |
|--------|-------------|----------|
| NOTICE + .reuse/dep5 globs | Split declared once by path; `reuse lint` verifies; no per-file headers | ✓ (delegated) |
| NOTICE only, directory convention | Documented split, no automated check | |
| Per-file SPDX headers | Header on every file | |

**User's choice:** Delegated — "i don't care about license tbh".
**Notes:** Claude discretion: `.reuse/dep5` globs, `NOTICE` with third-party and trademark sections, `reuse lint` deferred to Phase 8. Later confirmed the MIT + CC-BY-4.0 boundary after being shown the all-rights-reserved consequence of shipping unlicensed.

---

## ADR set & numbering

| Option | Description | Selected |
|--------|-------------|----------|
| Five policy ADRs | 0001 monorepo, 0002 ports-and-adapters, 0003 Git policy, 0004 license, 0005 assets/LFS | ✓ |
| Minimal three ADRs | Monorepo, ports-and-adapters, Git policy only | |
| Research-listed three | Includes `0003` symlink vs `lib_extra_dirs` | |

**User's choice:** Five policy ADRs

| Option | Description | Selected |
|--------|-------------|----------|
| Sequential on acceptance + index | Never reused; `docs/decisions/README.md` index | ✓ |
| Topic-reserved numbers | Pre-reserve numbers by topic; folder accumulates gaps | |
| Date-based IDs | `YYYYMMDD-slug` filenames | |

**User's choice:** Sequential on acceptance + index
**Notes:** Consequence accepted: the symlink ADR becomes `0006` in Phase 2.

| Option | Description | Selected |
|--------|-------------|----------|
| MADR 4.0 full | Frontmatter, drivers, options, pros/cons, outcome, confirmation, consequences | ✓ |
| MADR 4.0 minimal | Context, outcome, consequences only | |
| Nygard classic | Title/Status/Context/Decision/Consequences | |

**User's choice:** MADR 4.0 full

---

## Ignore & attribute coverage

| Option | Description | Selected |
|--------|-------------|----------|
| Pre-declare narrow LFS set | `.pdf .step .stl .fzz .zip .bin .elf .vcd` day one + size guard | ✓ |
| Size guard only, LFS later | LFS patterns added on first occurrence | |
| Decide per first occurrence | Highest risk of an unrecoverable mistake | |

**User's choice:** Pre-declare narrow LFS set

| Option | Description | Selected |
|--------|-------------|----------|
| Build, generated, secrets, OS, video | `.pio/`, `compile_commands.json`, `site/`, caches, secrets, `.DS_Store`, video containers | ✓ |
| Baseline + all editor state | Also ignore `.vscode/` and `.idea/` entirely | |
| Minimal | Only `.pio/` and secrets | |

**User's choice:** Build, generated, secrets, OS, video

---

## Secret-scanning policy

| Option | Description | Selected |
|--------|-------------|----------|
| Defaults + reviewed allowlist | gitleaks defaults; `.gitleaks.toml` only for verified false positives, reviewed in PRs | ✓ |
| Defaults, no allowlist | No config file; placeholders must be reworded | |
| Curated rule subset | Hand-picked rules; blind spots | |

**User's choice:** Defaults + reviewed allowlist

| Option | Description | Selected |
|--------|-------------|----------|
| Rotate → assess → document | Rotate first, then assess, forward-fix, document; never rewrite history | ✓ |
| Assess first, rotate if real | Triage before rotating | |
| Document only | Record and continue | |

**User's choice:** Rotate → assess → document

**Claude's discretion:** full-history `gitleaks git` scan runs on every pull request; revisit only if measured history size makes it a CI bottleneck.

---

## PR template contract

| Option | Description | Selected |
|--------|-------------|----------|
| Type + traceability + checks | Type, requirement/phase ID, ADR/issue link, checks line with run link | ✓ |
| Minimal header | Type and one-line summary | |
| Rich header with evidence table | Evidence table on every PR | |

**User's choice:** Type + traceability + checks

| Option | Description | Selected |
|--------|-------------|----------|
| Differentiated per type | Separate homework, infra, docs checklists | ✓ |
| Universal DoD + type extras | One shared checklist plus extras | |
| DoD cites AGENTS.md rules | Every checkbox references a rule ID | |

**User's choice:** Differentiated per type

**Claude's discretion:** shared header delimited by HTML comment markers and compared by `scripts/check_pr_templates.py`; local in Phase 1, CI in Phase 8.

---

## Public README now

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal foundation README | Purpose, license statement, policy links, early-phase status; kept current | ✓ |
| Wait for Phase 5 | Leave the 11-byte placeholder | |
| Full public README now | Full structure, setup, roadmap, contributing | |

**User's choice:** Minimal foundation README, "but keep it updated further"
**Notes:** Treated as a living document; Phase 5 adds the generated index section in place.

---

## Claude's Discretion

- Licensing declaration mechanics (`.reuse/dep5`, `reuse lint` in Phase 8) after the user delegated the topic; the license boundary itself was explicitly confirmed.
- PR-template shared-header drift mechanism (delimited block + check script).
- Full-history secret-scan cadence (every PR).
- Minimal `.pre-commit-config.yaml` (gitleaks, whitespace/EOF, large-file guard) in Phase 1 rather than a throwaway shell hook; Phase 6 extends it.
- One `security.yml` workflow for the full-history gitleaks scan; the rest of CI stays in Phase 8.

## Deferred Ideas

- Full branch-prefix-to-template mapping after the pilot.
- Ruleset `--check`, `reuse lint`, and the PR-template drift check in Phase 8 CI.
- Required approvals rise from 0 to 1 when a second maintainer joins.
- `lib/AGENTS.md` only when the Phase 3 dependency rule differs from the root.
- README refreshed at each phase boundary and milestone.
- The symlink ADR becomes `0006` in Phase 2, not `0003`.
