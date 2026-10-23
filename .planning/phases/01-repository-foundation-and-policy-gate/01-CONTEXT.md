# Phase 1: Repository Foundation and Policy Gate - Context

**Gathered:** 2026-10-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver the irreversible, pre-publication policy foundation of the public repository:
the agent rulebook, the reproducible Git policy, the license and attribution boundary,
secret and asset hygiene, the three pull-request templates, the first MADR decision
records, and a minimal public README.

This is a policy-and-artifact phase, not a build phase. No PlatformIO project, shared
library, schema, generator, or CI matrix is created here — those belong to Phases 2–8.
What ships here must be verifiable: a full-history secret scan, a policy definition that
can be re-applied, and PR templates whose shared header can be drift-checked.

Verified starting state (2026-10-23): the remote `VLoktiev-EMB/homeworks` is public; a
repository ruleset named `main` is already active (no bypass actors, 0 required
approvals, squash-only, linear history, deletion and force-push blocked); classic branch
protection is not used. No `AGENTS.md`, `LICENSE`, `NOTICE`, `docs/`, `.github/`,
`.gitignore`, or `.gitattributes` exists. `.claude/CLAUDE.md` is 772 lines. The working
branch is `infra/initialize-project`.

</domain>

<decisions>
## Implementation Decisions

### Rulebook and Agent Instructions

- **D-01:** `.claude/CLAUDE.md` is reduced to a thin adapter (~30 lines): an `@AGENTS.md`
  import plus the Claude-specific GSD block. All rules move to `AGENTS.md`; durable
  stack/reference material moves to `docs/standards/` and becomes publishable in Phase 5.
  The current 772-line content is not kept in the adapter file.
- **D-02:** `AGENTS.md` has a **~300-line ceiling** — REQUIREMENTS wins over the <200-line
  best-practice guidance, because the rulebook must carry enforcement tags, short
  examples, a routing table, and canonical commands.
- **D-03:** Enforcement is marked with two composable dimensions: severity
  (`[MUST]` / `[SHOULD]`) and mechanism (`[ENFORCED: pre-commit | CI | review]`) —
  **Reversibility:** costly — the tag vocabulary will be cited by standards documents and
  checked by scripts, so changing it later touches every rule and every checker.
- **D-04:** `AGENTS.md` contains rules, canonical commands, repository layout, and a
  routing table pointing to skills, scripts, and `docs/standards/`. Depth (report
  structure, formatting rationale, git rationale) lives behind the link.
- **D-05:** Root `AGENTS.md` only in this phase. A nested `lib/AGENTS.md` is allowed later
  only when the Phase 3 dependency rule genuinely differs from the root rulebook.
  Nearest-file precedence is documented as a rule, not as a current structure.
- **D-06:** The GSD workflow is a **portable MUST in `AGENTS.md`** — every change goes
  through the GSD workflow and deterministic scripts. The correction recorded during
  discussion: Antigravity can also run `/gsd-*` commands, so GSD is not a Claude-only
  adapter. `.claude/CLAUDE.md` keeps the command-level mechanics below the import.
  On conflict, `AGENTS.md` wins.

### Git Policy and Enforcement

- **D-07:** The live `main` ruleset is stored as code: a ruleset JSON under `policy/`
  plus a script with `--check` (diff live versus committed via `gh api`) and `--apply`
  (re-apply). CI wiring is deferred to Phase 8.
- **D-08:** The policy check also asserts GitHub repository security settings: secret
  scanning, secret-scanning push protection, and auto-delete-branches for merged PRs.
  These remain read-only checks; the settings themselves are changed via UI or `gh`.
- **D-09:** Keep **0 required approvals**, no bypass actors, squash-only merges. The
  policy documentation records the trigger: raise to 1 approval when a second maintainer
  joins.
- **D-10:** Branch naming is **anchor-only**: `hw/<id>` maps to the homework template,
  `docs/<slug>` maps to the docs template; every other prefix is free-form and defaults
  to the infra template. The full prefix-to-template mapping is revisited after the pilot.
- **D-11:** `scripts/tag_homework.sh <id>` verifies the PR is merged and the homework
  exists, checks that the tag is unused, then creates and pushes `hw/<id>`.
- **D-12:** Direct pushes to `main`, force-push, and published-history rewriting are
  forbidden; the existing ruleset already enforces this — **Reversibility:** one-way —
  anything that reaches public history (a secret, PII, instructor material) cannot be
  scrubbed without the rewriting the policy forbids.

### Licensing, Attribution, and Public Identity

- **D-13:** **MIT for code; CC-BY-4.0 for docs and homework reports**, following the
  GitHub OSPO mixed-repository pattern — **Reversibility:** one-way — a published license
  grant is irrevocable, and the repository is already public.
- **D-14:** The **public handle or org** (e.g. `VLoktiev-EMB`) is used everywhere: the
  `LICENSE` copyright line, `NOTICE`, and report author metadata. No real name, no
  institution — **Reversibility:** one-way — PII published into history cannot be
  removed under the no-rewrite policy.
- **D-15:** The license split is declared once in `.reuse/dep5` path globs — no per-file
  SPDX headers in reports or YAML. `NOTICE` carries third-party-attribution and trademark
  sections. `reuse lint` is wired into CI with Phase 8.
- **D-16:** Phase 1 ships a minimal foundation README: purpose, the MIT/CC-BY-4.0
  statement linking `LICENSE` and `NOTICE`, links to `AGENTS.md` and `docs/decisions/`,
  and an explicit early-phase status. The README is **kept current as phases ship**;
  Phase 5 adds the generated homework index section in place rather than replacing the
  document.

### Secrets and Asset Hygiene

- **D-17:** gitleaks runs with its **default rules**; a `.gitleaks.toml` is added only
  for verified false positives (documentation placeholders such as `changeme`), and every
  allowlist entry is reviewed in a pull request.
- **D-18:** A real secret triggers: **rotate first**, assess exposure, remove it with a
  forward fix, document the incident. History is never rewritten, so rotation is the only
  real mitigation.
- **D-19:** The full-history scan (`gitleaks git`) runs on **every pull request**;
  revisit only if measured history size makes it a CI bottleneck.
- **D-20:** LFS patterns are **pre-declared day one** in `.gitattributes` for
  `.pdf .step .stl .fzz .zip .bin .elf .vcd`, backed by a pre-commit size guard.
- **D-21:** `.gitignore` covers build output (`.pio/`), generated files
  (`compile_commands.json`, `site/`), Python caches, secrets (`.env`, `secrets.*`),
  OS junk (`.DS_Store`), and video containers (`.mp4 .mov .avi .webm .mkv`) — videos are
  linked, never committed. Editor state stays out except the committed workspace.

### Pull Request Contracts

- **D-22:** The shared header carries: PR type selection, requirement/phase ID, related
  ADR or issue link, and a checks line confirming meta, build, native tests, and gitleaks
  passed with a run link.
- **D-23:** The Definition of Done is **differentiated per type**:
  - homework — builds, native tests, report sections, evidence provenance, regenerated
    index/workspace, simulation if applicable;
  - infra — ADR recorded, policy check passes, no new secrets, docs updated;
  - docs — links valid, markdownlint clean, no duplicated source material.
- **D-24:** The shared header is delimited by HTML comment markers in all three files and
  compared by `scripts/check_pr_templates.py`; the check runs locally in Phase 1 and joins
  CI in Phase 8. There is no default `PULL_REQUEST_TEMPLATE.md`.

### Architecture Decision Records

- **D-25:** Phase 1 records five ADRs: `0001` monorepo, `0002` ports-and-adapters / no
  universal HAL, `0003` Git policy and protected `main`, `0004` license and attribution,
  `0005` asset and LFS policy.
- **D-26:** ADRs use the **MADR 4.0 full** template: frontmatter, context and problem
  statement, decision drivers, considered options, pros/cons, decision outcome with
  confirmation, consequences.
- **D-27:** Numbers are assigned **sequentially on acceptance and never reused**, with
  `docs/decisions/README.md` as the status index — **Reversibility:** costly — ADR numbers
  become permanent cross-references; the consequence is that the symlink decision becomes
  `0006` in Phase 2, not the `0003` the research list assumed.

### Claude's Discretion

The user delegated the following; these are locked at the level stated and need no
re-confirmation downstream:

- Licensing declaration mechanics: `.reuse/dep5` over per-file headers; `reuse lint`
  deferred to Phase 8 (user: "i don't care about license tbh", then confirmed the
  MIT + CC-BY-4.0 boundary).
- PR-template drift mechanism: delimited shared header plus `check_pr_templates.py`.
- Secret-scan cadence: full history on every PR.
- A minimal `.pre-commit-config.yaml` (gitleaks, trailing whitespace/EOF, large-file
  guard) is installed in this phase rather than a throwaway shell hook; Phase 6 extends it.
- One `security.yml` workflow is added for the full-history gitleaks scan; the rest of CI
  stays in Phase 8.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning artifacts
- `.planning/PROJECT.md` — core value, constraints, and the locked Key Decisions table.
- `.planning/REQUIREMENTS.md` §Repository Foundation and Policy — FOUND-02 through
  FOUND-08, FOUND-10; §Tooling and Quality — TOOL-07.
- `.planning/ROADMAP.md` §Phase 1 — goal, requirements, and the five success criteria.
- `.planning/STATE.md` — current position and blockers.
- `.planning/research/SUMMARY.md` — the conflicts table that changes PROJECT.md before
  scaffolding; ADR and policy implications.
- `.planning/research/ARCHITECTURE.md` — recommended repository structure, documentation
  layering (AGENTS.md canonical, `.claude/CLAUDE.md` imports it), ADR list.
- `.planning/research/PITFALLS.md` — secrets exposure, PII, LFS bloat, branch hygiene;
  "declare `.gitattributes` binary extensions on day one".
- `.planning/research/FEATURES.md` — TS-18 license/copyright hygiene, TS-19 secret/PII
  hygiene, TS-20 asset/LFS policy, TS-24 auditable Git workflow.
- `.planning/research/STACK.md` — pinned tool versions (pre-commit 4.7.0, gitleaks 8.30.1,
  markdownlint-cli2 0.24.0, yamllint 1.38.0).

### External standards
- `https://agents.md/` — the cross-tool `AGENTS.md` convention; nested-file precedence.
- `https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets`
  — the rule types used by the committed ruleset JSON.
- `https://learn.github.com/well-architected/governance/recommendations/managing-repositories-at-scale/rulesets-best-practices`
  — minimal baseline, scoped bypass actors, audit guidance.
- `https://github.com/github/github-ospo/blob/main/policies/licensing.md` — MIT for code,
  CC-BY-4.0 for documentation/media.
- `https://github.com/adr/madr` — MADR 4.0 template and status conventions.

### Live external configuration
- GitHub repository `VLoktiev-EMB/homeworks`, ruleset `main` (id `25632456`) — active,
  target `~DEFAULT_BRANCH`, rules: deletion, non-fast-forward, required linear history,
  pull request with 0 approvals and squash-only merges, empty required-status-check list,
  no bypass actors. This is the live counterpart the committed JSON must match.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/` exists and already contains `review_smoke_test.sh` — new deterministic
  scripts (`tag_homework.sh`, `check_pr_templates.py`, the policy script) belong here.
- The committed `homeworks.code-workspace` (currently untracked) already provides the
  multi-root editor surface; Phase 5 will generate it, so Phase 1 must not hand-edit it.
- `.claude/` contains only `CLAUDE.md` today; the GSD tooling lives outside the repo at
  `~/.claude/gsd-core/`.

### Established Patterns
- Commits follow Conventional Commits already (`docs:`, `chore:`), and work proceeds on
  `infra/initialize-project` — consistent with the anchor-only branch rule.
- Planning state is tracked under `.planning/` by the GSD workflow; repository artifacts
  are English while user-facing discussion follows the user's language (Ukrainian).
- No code, library, schema, docs tree, or CI workflow exists yet — Phase 1 creates the
  policy surface only.

### Integration Points
- `.github/PULL_REQUEST_TEMPLATE/{homework,infra,docs}.md` — the three templates; no
  root `PULL_REQUEST_TEMPLATE.md`.
- `.github/workflows/security.yml` — the single Phase 1 workflow (full-history gitleaks).
- `.pre-commit-config.yaml` at the repository root — minimal Phase 1 hooks.
- `policy/` — new directory holding the ruleset JSON consumed by the check/apply script.
- `docs/decisions/` — new tree: five ADRs, a MADR template, and `README.md` index.
- `.claude/CLAUDE.md` — rewritten as a thin `@AGENTS.md` adapter.

</code_context>

<specifics>
## Specific Ideas

- The user's correction during discussion: **Antigravity can run `/gsd-*` commands**, so
  the GSD workflow rule belongs in the portable rulebook, not only in the Claude adapter.
- The user wants the **README kept updated further**, not frozen until Phase 5.
- On licensing the user said "i don't care about license tbh", then explicitly chose
  **A — keep MIT + CC-BY-4.0** when shown the legal consequence of shipping unlicensed.
- The discussion happened in Ukrainian; the planning artifacts stay in English per the
  project language constraint.

</specifics>

<deferred>
## Deferred Ideas

- Full branch-prefix-to-template mapping — revisit after the pilot, once real `feat/` and
  `chore/` branches exist.
- Ruleset `--check`, `reuse lint`, and the PR-template drift check join CI in Phase 8.
- Required approvals rise from 0 to 1 when a second maintainer joins (documented trigger).
- `lib/AGENTS.md` only when the Phase 3 dependency rule genuinely differs from the root.
- README refreshed at each phase boundary and milestone; Phase 5 adds the generated
  homework index section in place.
- Consequence to carry into Phase 2: the `symlink://` versus `lib_extra_dirs` ADR becomes
  `0006`, not `0003`, because numbering is sequential and permanent.

</deferred>

---

*Phase: 1-Repository Foundation and Policy Gate*
*Context gathered: 2026-10-23*
