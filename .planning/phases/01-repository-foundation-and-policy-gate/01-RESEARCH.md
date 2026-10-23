# Phase 1: Repository Foundation and Policy Gate - Research

**Researched:** 2026-10-23
**Domain:** Repository governance — GitHub rulesets, secret scanning, licensing metadata, agent rulebooks, PR contracts
**Confidence:** HIGH on live-repo facts and file formats; MEDIUM on two contested artifacts (see Open Questions)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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

### Deferred Ideas (OUT OF SCOPE)

- Full branch-prefix-to-template mapping — revisit after the pilot, once real `feat/` and
  `chore/` branches exist.
- Ruleset `--check`, `reuse lint`, and the PR-template drift check join CI in Phase 8.
- Required approvals rise from 0 to 1 when a second maintainer joins (documented trigger).
- `lib/AGENTS.md` only when the Phase 3 dependency rule genuinely differs from the root.
- README refreshed at each phase boundary and milestone; Phase 5 adds the generated
  homework index section in place.
- Consequence to carry into Phase 2: the `symlink://` versus `lib_extra_dirs` ADR becomes
  `0006`, not `0003`, because numbering is sequential and permanent.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FOUND-02 | Homework IDs follow `module_lesson-name` and stay stable | Documented as an anchor rule in `AGENTS.md`; enforcement belongs to the Phase 4 JSON Schema (`additionalProperties: false` + `pattern`), so Phase 1 only states the rule. |
| FOUND-03 | `main` protected; every change via branch + PR; no force-push or history rewrite | Live ruleset verified (six rules, no bypass actors). `policy/ruleset-main.json` + `scripts/check_policy.py --check` make it assertable; `GET /rules/branches/main` verifies effective rules. |
| FOUND-04 | Conventional Commits; squash merge; `hw/<id>` tag after merge; source branch deleted | Ruleset already forces `allowed_merge_methods: ["squash"]` and `delete_branch_on_merge: true`; Conventional Commits spec quoted for the rulebook; `scripts/tag_homework.sh` preconditions specified; branch rulesets do not constrain tags, so tag push is safe. |
| FOUND-05 | Three PR templates with shared header and type-specific DoD | Path precedence and chooser behaviour confirmed; no default template required for the chooser to appear; marker delimiters and `check_pr_templates.py` design specified. |
| FOUND-06 | MIT for code, `NOTICE`, third-party attribution, no PII | OSPO rule quoted ("Code → use MIT", "Not code → use CC-BY"); `LICENSES/MIT.txt` + `LICENSES/CC-BY-4.0.txt` required by REUSE; public-handle-only rule sourced from D-14. |
| FOUND-07 | gitleaks in pre-commit and full history in CI; `.gitignore`/`.gitattributes` coverage | gitleaks 8.30.1 verified; hook `entry` read from the upstream `.pre-commit-hooks.yaml`; `gitleaks git --log-opts=--all` + `fetch-depth: 0` workflow given; `.gitignore` skeleton covers every D-21 category. |
| FOUND-08 | LFS only for large non-diffable binaries; site assets normal; videos linked | Exact `filter=lfs diff=lfs merge=lfs -text` tuple verified; `check-added-large-files` skips LFS-tracked files via `git check-attr` (source read), so the size guard and LFS coexist without exclusion rules. |
| FOUND-10 | `AGENTS.md` canonical (~300 lines), enforcement tags, examples, quick-start; `.claude/CLAUDE.md` imports it | agents.md convention confirms no mandatory structure and states the nearest-file precedence rule verbatim; tag vocabulary `[MUST]/[SHOULD]` + `[ENFORCED: …]` defined; the convention is silent on CLAUDE.md, so the import is a Claude Code feature and must be documented as such. |
| TOOL-07 | Infrastructure decisions recorded as MADR ADRs under `docs/decisions/` | MADR 4.0.0 template read verbatim — exact frontmatter keys, section order, status enum; numbering is sequential and permanent (D-27), which conflicts with SIM-02's "ADR-0004" reference (Open Question 2). |
</phase_requirements>

## Summary

This phase ships policy artifacts, not code. The valuable research is therefore exact file
formats, exact API schemas, and the places where the locked decisions in `01-CONTEXT.md`
collide with what the tools actually accept today.

Four findings change planning:

1. **Secret scanning and push protection are currently OFF on the live repository.** D-08
   assumes the policy check asserts them; as committed today, that check fails on its first
   run. Phase 1 must enable them (or the check must ship as a known-red gate).
2. **`.reuse/dep5` is deprecated.** REUSE Specification 3.3 says "The DEP5 file is
   deprecated", and `reuse-tool` has supported the replacement `REUSE.toml` since v4.0.0.
   The local tool version is 6.2.0. D-15 names `dep5`; the discretionary block in CONTEXT.md
   only locks "no per-file SPDX headers". `REUSE.toml` is the recommended substitution.
3. **Branch rulesets do not apply to tags at all**, so `git push origin hw/<id>` is
   unaffected by the `main` ruleset. No ruleset rule needs relaxing for D-11.
4. **The live ruleset's GET response is not a valid PUT body.** It returns read-only fields
   and at least one `pull_request` parameter that the documented request schema does not
   list. A `--check` that diffs raw GET output against a committed file will always differ;
   the comparison must be normalized against the committed subset.

**Primary recommendation:** Ship `policy/ruleset-main.json` containing only writable fields
plus a stdlib-Python `--check`/`--apply` script that compares a normalized subset of the
live ruleset, and gate the phase on that script exiting 0.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| Branch protection, merge policy, bypass actors | GitHub server (ruleset API) | Local policy file (`policy/*.json`) as source of truth | Rules are enforced by GitHub at push/merge time; the repo only records intent and detects drift. |
| Secret detection | Developer workstation (pre-commit hook) | CI (full-history scan) | Pre-commit stops the commit; CI catches a bypassed local hook. Neither alone covers both directions. |
| License declaration | Repository files (`REUSE.toml`, `LICENSE`, `LICENSES/`, `NOTICE`) | CI lint (`reuse lint`, Phase 8) | Licensing is static metadata; only a lint step turns it into an enforced claim. |
| Agent rulebook | `AGENTS.md` at repo root | `.claude/CLAUDE.md` thin import | The portable rulebook is the contract; tool adapters must not fork the rules. |
| PR contract | `.github/PULL_REQUEST_TEMPLATE/*.md` | `scripts/check_pr_templates.py` | GitHub renders the template; the script is the only way shared-header drift is detectable pre-merge. |
| Decision records | `docs/decisions/*.md` (MADR) | `docs/decisions/README.md` index | ADRs are human-reviewed prose; the index is the machine-readable status surface. |
| Asset policy | `.gitattributes` (LFS routing) | `.gitignore`, pre-commit size guard | Git decides LFS at add time; hooks only nudge. |

## Standard Stack

### Core

| Tool | Version | Purpose | Why Standard |
|---|---|---|---|
| GitHub repository rulesets | live API v2026-03-10 | Branch protection as code | Native, no bypass actors by default, importable as JSON. |
| `gitleaks` | **8.30.1** [VERIFIED: GitHub releases; Homebrew formula 8.30.1] | Secret detection, local + CI | Default rules cover 300+ provider formats; `git`/`dir`/`stdin` modes. |
| `pre-commit` | **4.7.0** [VERIFIED: PyPI] | Hook runner | Pinned hook revs, per-stage selection, first-class `pre-push`. |
| `pre-commit-hooks` | **v6.0.0** [VERIFIED: GitHub releases] | Whitespace, EOF, large-file, conflict-marker guards | Canonical companion repo; LFS-aware size guard. |
| `reuse` | **6.2.0** [VERIFIED: PyPI] | License metadata lint | Reference implementation of REUSE 3.3. |
| `git-lfs` | 3.8.1 [CITED: Homebrew formula] | Large non-diffable binaries | Only mechanism GitHub Pages cannot serve — hence the policy split in FOUND-08. |

### Supporting

| Tool | Version | Purpose | When to Use |
|---|---|---|---|
| `gh` CLI | 2.103.0 (installed) | `gh api` for ruleset read/apply, repo settings | Every policy operation; no raw `curl` token juggling. |
| Python | 3.13.13 (installed) | `check_pr_templates.py`, policy script, unit tests | Stdlib only — no third-party deps in Phase 1. |
| Go | 1.27.1 (installed) | Builds the `gitleaks` pre-commit hook when `language: golang` | Only if you pick the `golang` hook over `gitleaks-system`. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| `gitleaks/gitleaks-action@v3` | Install the gitleaks CLI in a `run:` step | **The action requires `GITLEAKS_LICENSE` for organization-owned repos.** `VLoktiev-EMB` is an org [CITED: github.com/gitleaks/gitleaks-action]. CLI install avoids a secret and a third-party action. |
| `pre-commit` `gitleaks` hook (`language: golang`) | `gitleaks-system` hook + Homebrew gitleaks | `golang` needs no system install but builds from source on first run (slow, needs Go); `gitleaks-system` is instant but adds a manual install step. Pick `golang` for reproducibility, `system` for speed. |
| `REUSE.toml` | `.reuse/dep5` | DEP5 still works but is deprecated in REUSE 3.3 and slated for removal; the two are mutually exclusive. |
| `reuse lint` | Per-file SPDX headers | Locked out by D-15 and hopeless at 30+ reports. |
| Ruleset JSON via `gh api` | Terraform / `gh` ruleset UI | No Terraform state file in a teaching repo; UI does not diff. |
| `actions/checkout` default shallow clone | `fetch-depth: 0` | Full-history scan is impossible on a shallow clone. D-19 requires full history. |

**Installation:**

```bash
brew install gitleaks git-lfs
uv tool install 'pre-commit==4.7.0' 'reuse==6.2.0'   # or: pipx install ...
pre-commit install
git lfs install
```

## Package Legitimacy Audit

The seam lookup (`gsd_run query package-legitimacy check --ecosystem pypi pre-commit reuse`)
returned `SUS` with **all signals null** (`exists: null`, `weeklyDownloads: null`,
`repoUrl: null`) and an accompanying certificate-copy error. That is an inconclusive
lookup, not a verdict — no observation was made. Verdicts below come from direct PyPI and
GitHub API reads instead.

| Package | Registry | Age | Source Repo | License | Verdict | Disposition |
|---|---|---|---|---|---|---|
| pre-commit 4.7.0 | PyPI | since 2014 [VERIFIED: github.com/pre-commit/pre-commit created 2014-03-13, 15,655 stars] | github.com/pre-commit/pre-commit | MIT | OK | Approved |
| pre-commit-hooks v6.0.0 | GitHub | since 2014 (6,725 stars) | github.com/pre-commit/pre-commit-hooks | MIT | OK | Approved |
| reuse 6.2.0 | PyPI | since 2019 [VERIFIED: github.com/fsfe/reuse-tool created 2019-04-12] | fsfe/reuse-tool | Apache-2.0 / CC0 / CC-BY-SA-4.0 | OK | Approved |
| gitleaks 8.30.1 | GitHub / Homebrew | since 2018 (30,265 stars) | github.com/gitleaks/gitleaks | MIT | OK | Approved |
| git-lfs 3.8.1 | Homebrew | since 2013 (14,557 stars) | github.com/git-lfs/git-lfs | NOASSERTION (GPL-ish + MIT parts) | OK | Approved — install-time tool only, not redistributed |
| gitleaks-action v3 | GitHub | since 2020 (667 stars) | github.com/gitleaks/gitleaks-action | NOASSERTION | **Not adopted** | Requires org license key; replaced by direct CLI install |

**Packages removed due to SLOP verdict:** none.
**Packages flagged as suspicious:** none.

## Architecture Patterns

### System Architecture Diagram

```
Developer workstation                          GitHub
─────────────────────                          ────────────────────────────────
git commit
  └─> pre-commit  ──> gitleaks (staged, redacted) ──┐
      ├─ trailing-whitespace / end-of-file-fixer    │ block?  ── yes ──> commit aborts
      └─ check-added-large-files (LFS-aware)        │
                                                    v
git push origin <branch>
  └─> GitHub ruleset "main" (target=branch, ref=~DEFAULT_BRANCH)
        ├─ creation          → only main itself is create-protected
        ├─ deletion          → branch delete blocked
        ├─ non_fast_forward  → force-push blocked
        ├─ required_linear_history → merge commits rejected
        ├─ pull_request      → must be a PR, squash-only, 0 approvals
        └─ required_status_checks → (empty in Phase 1; filled Phase 8)
              │
              v
        pull_request event
              └─> .github/workflows/security.yml
                    checkout fetch-depth: 0
                    └─> gitleaks git --log-opts=--all  ──> leak? ──> job fails ──> merge blocked
              │
              v
        merge (squash) → delete_branch_on_merge=true removes source branch
              │
              v
        scripts/tag_homework.sh <id> → verify merged + homework exists + tag unused → push hw/<id>
                                       (branch rulesets do not apply to tags)

Drift detection (local + Phase 8 CI):
  policy/ruleset-main.json  ──┐
  policy/repository.json    ──┤──> scripts/check_policy.py --check ──> gh api GET ──> normalize ──> diff
  live GitHub state         ──┘                                                     exit 1 on mismatch
```

### Recommended Project Structure

```
./
├── AGENTS.md                          # canonical rulebook (~300 lines max)
├── LICENSE                            # MIT, public handle only
├── NOTICE                             # third-party attribution + trademark
├── LICENSES/
│   ├── MIT.txt
│   └── CC-BY-4.0.txt
├── REUSE.toml                         # (or .reuse/dep5 — see Conflicts C1)
├── .gitignore
├── .gitattributes
├── .pre-commit-config.yaml
├── .gitleaks.toml                     # only when a verified false positive exists
├── .claude/CLAUDE.md                  # ~30 lines: @AGENTS.md + GSD mechanics
├── .github/
│   ├── PULL_REQUEST_TEMPLATE/
│   │   ├── homework.md
│   │   ├── infra.md
│   │   └── docs.md
│   └── workflows/security.yml
├── docs/
│   └── decisions/
│       ├── README.md                  # status index
│       ├── template.md                # MADR 4.0 template
│       ├── 0001-record-architecture-decisions.md
│       ├── 0002-ports-and-adapters-no-universal-hal.md
│       ├── 0003-git-policy-and-protected-main.md
│       ├── 0004-license-and-attribution.md
│       └── 0005-asset-and-lfs-policy.md
├── policy/
│   ├── ruleset-main.json
│   └── repository.json
└── scripts/
    ├── check_policy.py
    ├── check_pr_templates.py
    ├── tag_homework.sh
    └── tests/
        ├── test_check_policy.py
        └── test_check_pr_templates.py
```

### Pattern 1: Ruleset as a normalized subset, not a verbatim export

**What:** Commit only the fields `POST`/`PUT` accepts. Compare a *projection* of the live
ruleset restricted to those keys, ignoring list order.

**When to use:** Always, for the `--check` path.

**Why:** The live GET returns `id`, `node_id`, `source_type`, `source`, `created_at`,
`updated_at`, `_links`, `current_user_can_bypass` [VERIFIED: live response for ruleset
25632456], plus `pull_request.parameters.require_extra_approval_for_unattributed_changes`
which is absent from the documented request-body schema [CITED:
docs.github.com/en/rest/repos/rules]. A verbatim diff never converges.

**Example:**

```python
READ_ONLY = {"id", "node_id", "source_type", "source", "created_at", "updated_at",
             "_links", "current_user_can_bypass"}

def project(live: dict, desired: dict) -> dict:
    """Keep only the keys the committed file declares, recursively."""
    out = {}
    for k, v in desired.items():
        if k not in live:
            continue
        if isinstance(v, dict) and isinstance(live[k], dict):
            out[k] = project(live[k], v)
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            out[k] = sorted(
                (project(item, tmpl) for item, tmpl in zip(live[k], v)),
                key=lambda d: d.get("type", ""),
            )
        else:
            out[k] = live[k]
    return out
```

### Pattern 2: Two-dimensional enforcement tags in `AGENTS.md`

**What:** Every rule carries severity and mechanism, e.g.
`**[MUST]** **[ENFORCED: pre-commit]**` or `**[SHOULD]** **[ENFORCED: review]**`.

**When to use:** Throughout `AGENTS.md`. Never write a bare rule.

**Why:** D-03 locks this vocabulary, and future scripts will grep it. Keep the tokens
literal and machine-matchable: `[MUST]`, `[SHOULD]`, `[ENFORCED: pre-commit]`,
`[ENFORCED: CI]`, `[ENFORCED: review]`. Do not introduce `[MAY]` or `[INFO]` — no checker
will know what to do with them.

### Pattern 3: Delimited shared PR header

**What:** Each of the three templates carries an identical byte range between
`<!-- pr-header:start -->` and `<!-- pr-header:end -->`.

**When to use:** All three templates; `check_pr_templates.py` compares that slice only.

**Why:** A full-file equality check is impossible because the Definition of Done differs
by design (D-23). The markers make the shared contract testable without freezing the
per-type content.

**Example:**

```markdown
<!-- pr-header:start -->
## Pull request

- **Type:** `homework` | `infra` | `docs`
- **Phase / requirement:** `<e.g. FOUND-03, Phase 1>`
- **ADR / issue:** `<docs/decisions/0003-... or #123>`

Verification (paste run links):
- [ ] `meta` checks passed — `<link>`
- [ ] build passed — `<link>`
- [ ] native tests passed — `<link>`
- [ ] `gitleaks` passed — `<link>`
<!-- pr-header:end -->
```

### Anti-Patterns to Avoid

- **Committing a raw `gh api` export.** It carries read-only fields and will not re-import.
- **Diffing rules array by index.** Rule order is not part of the contract; sort by `type`.
- **Adding a default `pull_request_template.md`.** It suppresses the chooser and silently
  becomes the template for every PR, defeating D-24.
- **Per-file SPDX headers in reports.** They collide with markdownlint and report
  readability; D-15 rules them out.
- **`check-json` in pre-commit.** `homeworks.code-workspace` is JSONC; the hook will fail on
  comments the moment Phase 5 generates it.
- **Trusting `.gitignore` to keep secrets out.** It stops accidental `git add`; only
  gitleaks and push protection stop a deliberate one.
- **Rewriting history to remove a leaked secret.** D-12/D-18 make this the one forbidden
  remediation; rotate instead.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Secret pattern matching | Custom regex list | gitleaks 8.30.1 default rules | 300+ provider formats, entropy checks, allowlist ergonomics; a hand list is stale on day one. |
| LFS routing | Manual `git lfs track` in a script | `.gitattributes` patterns committed | Tracked rules must reach clones and forks; a script run once does not. |
| License metadata | Hand-written per-file header audit | REUSE (`REUSE.toml` + `LICENSES/`) | Handles globs, precedence, and `.license` companions; `reuse lint` is the single pass/fail. |
| Ruleset drift detection | Eyeballing the Settings UI | `gh api` GET + normalized diff | UI does not diff, does not version, and cannot run in CI. |
| PR template drift detection | Reviewer discipline | `check_pr_templates.py` marker comparison | Reviewers stop noticing by the third PR. |
| Branch-name-to-template mapping | `.github/` automation | Documented anchor rule + reviewer | GitHub has no native branch→template router; a workflow for this is Phase 8 scope at the earliest. |
| Tag creation safety | Manual `git tag && git push` | `scripts/tag_homework.sh` | Verifies merged, existence, and unused-tag preconditions that a human forgets. |

**Key insight:** Every item here is a place where a hand-rolled substitute is *correct on the
day it is written and wrong six months later*. The policy phase exists to install the tool,
not to write a smaller version of it.

## Common Pitfalls

### Pitfall 1: Branch rulesets are silently irrelevant to tags

**What goes wrong:** Someone reads `non_fast_forward` + `deletion` on the `main` ruleset and
concludes tags are protected, then a stray `git push --force origin hw/1_3` succeeds — or,
inversely, assumes tags need a ruleset exception.
**Why it happens:** GitHub separates `target: branch` from `target: tag`; a branch ruleset
never evaluates against a tag ref [CITED: available-rules-for-rulesets].
**How to avoid:** State explicitly in ADR-0003 that `hw/<id>` tags are unprotected and that
`tag_homework.sh` is the only guard. If tag immutability matters later, add a tag ruleset.
**Warning signs:** A policy doc claiming "force-push is blocked" without naming the ref type.

### Pitfall 2: The ruleset GET body is not a PUT body

**What goes wrong:** `--apply` posts the stored export and GitHub rejects it with 422, or
silently drops a parameter.
**Why it happens:** GET returns server-assigned and derived fields; at least one
`pull_request` parameter in the live response is undocumented in the request schema.
**How to avoid:** Store the writable subset; never round-trip GET output. Test `--apply`
against a throwaway ruleset before running it on `main`.
**Warning signs:** `--check` reporting drift immediately after a successful `--apply`.

### Pitfall 3: Enabling secret scanning does not enable push protection

**What goes wrong:** The policy check passes for scanning but the developer can still push a
secret, because push protection is a separate toggle.
**Why it happens:** `security_and_analysis` exposes `secret_scanning`,
`secret_scanning_push_protection`, `secret_scanning_validity_checks`, and
`secret_scanning_non_provider_patterns` as four independent statuses [VERIFIED: live GET
`/repos/VLoktiev-EMB/homeworks`].
**How to avoid:** Assert each status separately in `policy/repository.json`.
**Warning signs:** A check that reads one boolean named `security`.

### Pitfall 4: `check-added-large-files` measures the working tree, not the blob

**What goes wrong:** A 900 MB PDF already routed to LFS still fails the hook, or the author
widens `--maxkb` until the guard is meaningless.
**Why it happens:** The hook calls `os.stat(filename).st_size` on the working-tree path.
**How to avoid:** Know that it removes LFS-tracked files first via
`git check-attr filter` before sizing [VERIFIED:
pre-commit-hooks/pre_commit_hooks/check_added_large_files.py:13-31,43]; LFS routing is what
makes a large file pass, not a larger threshold.
**Warning signs:** `--maxkb` creeping upward across PRs.

### Pitfall 5: `gitleaks git` needs real history

**What goes wrong:** CI reports "no leaks" on a repository whose full history contains one.
**Why it happens:** `actions/checkout` defaults to a shallow clone; `gitleaks git` inspects
patches from `git log -p` and only sees what was fetched.
**How to avoid:** `fetch-depth: 0`, and pass `--log-opts="--all"` so non-default refs are
included.
**Warning signs:** The scan finishes in under two seconds on a repository with hundreds of
commits.

### Pitfall 6: `reuse lint` covers more than you think

**What goes wrong:** The lint fails on `.planning/**`, `scripts/**`, and `policy/*.json` —
files nobody thought of as "licensed content".
**Why it happens:** Covered files are *all* project files except a short exclusion list
(`LICENSES/`, root `LICENSE`/`COPYING`/`LICENCE`, VCS/ignored files, `REUSE.toml`,
`.reuse/`, symlinks, zero-byte files).
**How to avoid:** Write the annotation globs to cover *everything*, ending with a
catch-all, and run `reuse lint` before wiring CI in Phase 8.
**Warning signs:** A lint failure list that grows after every new script.

### Pitfall 7: The org requirement on `gitleaks-action`

**What goes wrong:** CI fails on the first PR with a license error.
**Why it happens:** The action's license is "required for organizations, not required for
user accounts" [CITED: github.com/gitleaks/gitleaks-action].
**How to avoid:** Do not use the action; install the pinned CLI binary in a `run:` step.

### Pitfall 8: `homeworks.code-workspace` is JSONC

**What goes wrong:** `check-json` fails the moment Phase 5 writes comments or trailing
commas into the generated workspace file.
**How to avoid:** Do not add a JSON validator in Phase 1; validate generated JSON inside the
generator (Phase 5) where it is produced.

## Code Examples

### Ruleset JSON — committed form (writable fields only)

```json
{
  "name": "main",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {
    "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] }
  },
  "rules": [
    { "type": "creation" },
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_linear_history" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": ["squash"]
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": false,
        "do_not_enforce_on_create": false,
        "required_status_checks": []
      }
    }
  ]
}
```

Source: field set verified against the live ruleset for `VLoktiev-EMB/homeworks`
(id `25632456`) and the documented request schema [CITED: docs.github.com/en/rest/repos/rules].
`~DEFAULT_BRANCH` is a documented special include token that selects the repository's
default branch.

### Repository settings file

```json
{
  "delete_branch_on_merge": true,
  "allow_squash_merge": true,
  "allow_merge_commit": false,
  "allow_rebase_merge": false,
  "allow_auto_merge": false,
  "security_and_analysis": {
    "secret_scanning": { "status": "enabled" },
    "secret_scanning_push_protection": { "status": "enabled" }
  }
}
```

Current live values that this file must change: `allow_merge_commit: true`,
`allow_rebase_merge: true`, `secret_scanning: disabled`,
`secret_scanning_push_protection: disabled` [VERIFIED: `gh api
repos/VLoktiev-EMB/homeworks`]. `delete_branch_on_merge` is already `true`.

Enable with:

```bash
gh api -X PATCH repos/VLoktiev-EMB/homeworks \
  -f 'security_and_analysis[secret_scanning][status]=enabled' \
  -f 'security_and_analysis[secret_scanning_push_protection][status]=enabled'
```

### `.pre-commit-config.yaml`

```yaml
minimum_pre_commit_version: '4.7.0'
default_install_hook_types: [pre-commit]

repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks          # entry: gitleaks git --pre-commit --redact --staged --verbose

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: check-added-large-files
        args: [--maxkb=1024]
```

Hook `entry`, `pass_filenames: false`, and `language: golang` for `id: gitleaks` are
[VERIFIED: gitleaks/.pre-commit-hooks.yaml]. `stages` values are the literal Git hook names
(`pre-commit`, `pre-push`, …) plus `manual` — there is no `push` [CITED: pre-commit.com].
Phase 6 will add `stages: [pre-push]` entries; do not add them now.

### `.github/workflows/security.yml`

```yaml
name: security

on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  gitleaks:
    name: gitleaks (full history)
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
      - name: Install gitleaks
        env:
          GITLEAKS_VERSION: 8.30.1
        run: |
          set -euo pipefail
          curl -sSfL \
            "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz" \
            | tar -xz -C "$RUNNER_TEMP" gitleaks
          install -m 0755 "$RUNNER_TEMP/gitleaks" /usr/local/bin/gitleaks
      - name: Scan full history
        run: gitleaks git --redact --verbose --log-opts="--all"
```

`fetch-depth: 0` is required for a full-history scan; `--redact` keeps a detected secret out
of the build log. No `GITLEAKS_LICENSE` is needed because the action is not used.

### `.gitattributes`

```gitattributes
* text=auto eol=lf

# Git LFS — large, non-diffable binaries only (D-20)
*.pdf   filter=lfs diff=lfs merge=lfs -text
*.step  filter=lfs diff=lfs merge=lfs -text
*.stl   filter=lfs diff=lfs merge=lfs -text
*.fzz   filter=lfs diff=lfs merge=lfs -text
*.zip   filter=lfs diff=lfs merge=lfs -text
*.bin   filter=lfs diff=lfs merge=lfs -text
*.elf   filter=lfs diff=lfs merge=lfs -text
*.vcd   filter=lfs diff=lfs merge=lfs -text

# Binary but small and page-served — normal git objects (FOUND-08)
*.png  binary
*.jpg  binary
*.jpeg binary
*.webp binary
*.svg  text eol=lf
```

The `filter=lfs diff=lfs merge=lfs -text` tuple is the documented attribute set
[CITED: docs.github.com/en/repositories/working-with-files/managing-large-files/configuring-git-large-file-storage].
`-text` disables CRLF normalization on binary content.

### `.gitignore` (initial coverage)

```gitignore
# Build output
.pio/
.pioenvs/
.piolibdeps/
platformio.sublime-project
platformio.sublime-workspace

# Generated
compile_commands.json
site/
*.log

# Python
__pycache__/
*.py[cod]
.venv/
.pytest_cache/
.ruff_cache/

# Secrets
.env
.env.*
!.env.example
secrets.*
*.pem
*.key

# OS / editor
.DS_Store
Thumbs.db
*.swp
.idea/

# Video (linked, never committed — D-21)
*.mp4
*.mov
*.avi
*.webm
*.mkv

# Internal research cache (planning artifacts stay tracked)
.planning/research/.cache/
```

### Policy check script — shape

```python
#!/usr/bin/env python3
"""Assert that live GitHub policy matches the committed policy files.

Usage:
  scripts/check_policy.py --check    # exit 1 on drift (default)
  scripts/check_policy.py --apply    # push committed policy to GitHub
"""
import argparse, json, subprocess, sys, difflib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
READ_ONLY = {"id", "node_id", "source_type", "source", "created_at", "updated_at",
             "_links", "current_user_can_bypass"}

def gh(*args: str) -> object:
    out = subprocess.run(["gh", "api", *args], capture_output=True, text=True, check=True)
    return json.loads(out.stdout) if out.stdout.strip() else None

def slug() -> str:
    url = subprocess.run(["git", "remote", "get-url", "origin"],
                         capture_output=True, text=True, check=True).stdout.strip()
    # git@github.com:OWNER/REPO.git  |  https://github.com/OWNER/REPO.git
    tail = url.split("github.com", 1)[1].lstrip(":/").removesuffix(".git")
    return tail

def normalise(live: dict, desired: dict) -> dict:
    """Project the live object onto the keys the desired file declares."""
    ...

def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", default=True)
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    ...
```

Design constraints for this script:

- **Resolve the repository from `origin`**, never hard-code `VLoktiev-EMB/homeworks`.
- **`--check` is read-only**; it must never call `POST`, `PUT`, or `PATCH`.
- **`--apply` re-reads the ruleset after writing** and re-runs the check, so a partial
  application cannot report success.
- **Exit codes:** `0` match, `1` drift, `2` usage/environment error. CI in Phase 8 keys off
  these.
- **Output:** a `difflib.unified_diff` of the normalized objects, plus one line per
  repository setting.
- **Idempotence:** running `--apply` twice must produce no second change and no API error.

### MADR 4.0 template — exact section order

Verbatim from
`github.com/adr/madr/blob/develop/template/adr-template.md` [VERIFIED: raw file, MADR
release `4.0.0`, published 2024-09-17]:

- YAML frontmatter delimited by `---` … `---`, keys: `status`, `date`, `decision-makers`,
  `consulted`, `informed`
- `# {short title, representative of solved problem and found solution}`
- `## Context and Problem Statement`
- `## Decision Drivers`
- `## Considered Options`
- `## Decision Outcome` — body starts `Chosen option: "{title}", because …`
- `### Consequences`
- `### Confirmation`
- `## Pros and Cons of the Options` — one `### {title}` subsection per option, bullets
  labelled `Good, because …`, `Neutral, because …`, `Bad, because …`
- `## More Information`

Status values, quoted from the template: `"{proposed | rejected | accepted | deprecated | …
| superseded by ADR-0123}"`.

### `AGENTS.md` — what the convention actually requires

[CITED: agents.md] The file is ordinary Markdown at the repository root; **no headings or
fields are mandatory**. Nested files are permitted for monorepos, and the precedence rule
is stated verbatim as:

> "The closest AGENTS.md to the edited file wins; explicit user chat prompts override
> everything."

and

> "Agents automatically read the nearest file in the directory tree"

The page names Codex, Jules, Factory, Aider, goose, opencode, Zed, Warp, VS Code, Cursor,
Gemini CLI, Copilot Coding Agent, Windsurf, and Augment as readers. **It does not mention
`CLAUDE.md` at all**, so the `@AGENTS.md` import in `.claude/CLAUDE.md` is a Claude Code
feature, not part of the agents.md convention.

Given no mandatory structure, D-02's ~300-line ceiling and D-04's routing-table design are
entirely compatible. Recommended section order (D-04):

1. Project in one paragraph
2. Agent quick-start (canonical commands, in order)
3. Repository layout
4. Rules, each tagged `[MUST]`/`[SHOULD]` + `[ENFORCED: …]`
5. Routing table → skills, scripts, `docs/standards/`
6. Nearest-file precedence rule (documented, not yet used — D-05)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| Classic branch protection | Repository rulesets | Rulesets GA 2023 | Rulesets are exportable/importable JSON, support bypass actors explicitly, and expose `GET /rules/branches/{branch}`. Classic protection is not used here. |
| `.reuse/dep5` | `REUSE.toml` | reuse-tool 4.0.0 (2024-07-03); deprecated in REUSE 3.3 | DEP5 still parses but is scheduled for removal; the two formats are mutually exclusive. |
| `gitleaks protect` / `gitleaks detect` | `gitleaks git` / `gitleaks dir` / `gitleaks stdin` | gitleaks v8.19+ | Old subcommand names are gone; every tutorial older than ~2024 shows the wrong ones. |
| pre-commit `push` stage | `stages: [pre-push]` | pre-commit 3.x | `push` is not a valid stage name. |
| `pre_commit_dummy_stage` / `pre-commit install -t push` | `default_install_hook_types` | pre-commit 2.18+ | One declarative key replaces per-hook flags. |
| `actions/checkout@v3` | `@v7` | 2025–2026 | Node runtime bumps; the project's STACK pins v7.0.1. |
| `gitleaks-action@v2` | `@v3` | 2026 | v2 runs Node 20; v3 runs Node 24. |

**Deprecated / outdated:**
- `.reuse/dep5` — deprecated in REUSE 3.3.
- `gitleaks protect` / `gitleaks detect` — removed; use `gitleaks git` / `gitleaks dir`.
- pre-commit `stages: [push]` — never existed; use `pre-push`.
- Classic branch protection — superseded by rulesets, which are not used in this repo.
- `mkdocs gh-deploy` — out of scope here, but already ruled out by STACK.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | GitHub accepts `"~DEFAULT_BRANCH"` in the `conditions.ref_name.include` array on `POST`/`PUT`, not only in `GET` | Standard Stack / Code Examples | `--apply` returns 422; substitute `["main"]`, which is functionally equivalent but loses default-branch portability. |
| A2 | The undocumented `require_extra_approval_for_unattributed_changes` parameter is either accepted or safely omitted on `PUT` | Pitfall 2 | `PUT` may reset it to a default; verify with a throwaway ruleset before touching `main`. |
| A3 | Secret scanning and push protection can be enabled on this public org-owned repo via `PATCH /repos` without a paid plan | Code Examples | If refused, the policy check must ship as a documented known-red assertion, and D-08 needs revisiting. |
| A4 | The authenticated `gh` account (`4oc3p`) holds admin on `VLoktiev-EMB/homeworks` | Standard Stack | `--apply` and the `PATCH` fail with 403; enablement becomes a manual UI step. |
| A5 | `reuse` 6.2.0 accepts `MIT` and `CC-BY-4.0` as SPDX identifiers and requires `LICENSES/MIT.txt` + `LICENSES/CC-BY-4.0.txt` | Standard Stack | `reuse lint` fails on missing license files; the filenames are specified by REUSE 3.3, only the version behaviour is assumed. |
| A6 | Tracking `.planning/**` in a public repository is acceptable | Open Questions | Internal planning notes become permanently public; `.gitignore` cannot remove them retroactively under D-12. |
| A7 | The `golang`-language gitleaks pre-commit hook builds successfully with Go 1.27.1 on macOS arm64 | Standard Stack | Falls back to `gitleaks-system` + Homebrew; costs one extra install step in the onboarding doc. |

## Open Questions

1. **`REUSE.toml` versus `.reuse/dep5`**
   - What we know: D-15 names `.reuse/dep5`; the discretionary block only locks "no per-file
     headers". REUSE 3.3 deprecates DEP5; reuse-tool 6.2.0 supports `REUSE.toml` and ships
     `reuse convert-dep5`.
   - What's unclear: whether the user cares that the artifact filename changes.
   - Recommendation: use `REUSE.toml`, note the substitution in ADR-0004, and let the
     planner surface it as a one-line confirmation rather than a blocking question.

2. **ADR number `0004` is double-booked**
   - What we know: D-25 assigns `0004` to "license and attribution". `REQUIREMENTS.md`
     SIM-02 (Phase 7) says the simulation-spike result "is recorded in ADR-0004".
   - What's unclear: nothing technically — D-27 makes numbering sequential and permanent.
   - Recommendation: keep `0004` = license and attribution; add a note in ADR-0004's
     `## More Information` that SIM-02's reference is stale, and correct the wording when
     Phase 7 is planned.

3. **Should `.planning/` stay in the public repository?**
   - What we know: it is tracked today (20 tracked files, most under `.planning/`), and
     `.planning/research/.cache/*.json` is also tracked.
   - What's unclear: whether the user wants the planning record public alongside the
     coursework.
   - Recommendation: keep `.planning/` tracked (it is the project's audit trail) but add
     `.planning/research/.cache/` to `.gitignore`; flag the decision in ADR-0003 as an
     accepted consequence, since it cannot be undone later.

4. **Tag immutability**
   - What we know: the `main` ruleset does not cover tags; `hw/<id>` tags are mutable and
     deletable by anyone with push access.
   - What's unclear: whether a mutable homework tag undermines the auditability claim in
     FOUND-04.
   - Recommendation: accept for now (single maintainer, D-09's trigger covers the second),
     and record the gap explicitly in ADR-0003 rather than leaving it implicit.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| git | Everything | ✓ | 2.54.0 | — |
| gh CLI | Policy check/apply, live verification | ✓ (authed as `4oc3p`) | 2.103.0 | `curl` + `GITHUB_TOKEN` |
| Python | Scripts, unit tests | ✓ | 3.13.13 | — |
| pre-commit | Local hooks | ✓ | **4.6.0 — below the 4.7.0 pin** | none; upgrade required |
| Go | `language: golang` gitleaks hook | ✓ | 1.27.1 | `gitleaks-system` hook |
| Homebrew | Installing binaries | ✓ | 7.0.10 | manual release download |
| gitleaks | FOUND-07 | ✗ | — (Homebrew formula 8.30.1 exists) | `pre-commit` `golang` hook builds it |
| git-lfs | FOUND-08 | ✗ | — (Homebrew formula 3.8.1) | none — LFS attributes without the binary are inert |
| reuse | License lint | ✗ | — (PyPI 6.2.0) | defer lint to Phase 8, still ship the files |
| Node.js | markdownlint (Phase 6) | ✓ | 26.7.0 | — |
| pytest | Test runner | ✗ | — | stdlib `unittest` (recommended) |

**Missing dependencies with no fallback:**
- `pre-commit` 4.6.0 must be upgraded to 4.7.0 — `minimum_pre_commit_version: '4.7.0'` in
  the config will refuse to run on 4.6.0.
- `git-lfs` — without it, `.gitattributes` routes are written but the first large binary
  commit fails.

**Missing dependencies with fallback:**
- `gitleaks` — install via Homebrew, or let the `golang` pre-commit hook build it.
- `reuse` — ship `REUSE.toml` and `LICENSES/` regardless; run the lint locally once and
  wire it into CI in Phase 8.

## Validation Architecture

`workflow.nyquist_validation` is `true` in `.planning/config.json`, so this section is
required.

### Test Framework

| Property | Value |
|---|---|
| Framework | Python stdlib `unittest` (no pytest installed; adding one is Phase 6 scope) |
| Config file | none — Wave 0 creates `scripts/tests/` |
| Quick run command | `python3 -m unittest discover -s scripts/tests -v` |
| Full suite command | `python3 -m unittest discover -s scripts/tests -v && python3 scripts/check_pr_templates.py && python3 scripts/check_policy.py --check && pre-commit run --all-files` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| FOUND-02 | Homework IDs match `module_lesson-name` | manual (Phase 4 schema enforces it) | — documented in AGENTS.md only | n/a |
| FOUND-03 | Direct push to `main` rejected; no bypass actors | integration | `python3 scripts/check_policy.py --check` | ❌ Wave 0 |
| FOUND-03 | Effective rules on `main` match the committed set | integration | `gh api repos/VLoktiev-EMB/homeworks/rules/branches/main --jq '[.[].type]'` | ✅ live endpoint |
| FOUND-04 | Squash-only merges, source branch auto-deleted | integration | `python3 scripts/check_policy.py --check` (asserts `allowed_merge_methods` and `delete_branch_on_merge`) | ❌ Wave 0 |
| FOUND-04 | `tag_homework.sh` refuses a duplicate tag | unit | `python3 -m unittest scripts.tests.test_tag_homework` | ❌ Wave 0 |
| FOUND-05 | Three templates exist; shared header identical | unit | `python3 -m unittest scripts.tests.test_check_pr_templates` | ❌ Wave 0 |
| FOUND-05 | No default `pull_request_template.md` at any of the three paths | unit | same | ❌ Wave 0 |
| FOUND-06 | `LICENSE`, `NOTICE`, `LICENSES/*` present; split declared | integration | `reuse lint` | ❌ Wave 0 |
| FOUND-07 | `.gitattributes` routes each LFS extension | integration | `git check-attr filter -- *.pdf *.step *.stl *.fzz *.zip *.bin *.elf *.vcd` → all `filter: lfs` | ❌ Wave 0 |
| FOUND-07 | `.gitignore` covers `.pio/`, `.env`, `compile_commands.json`, `site/` | unit | `python3 -m unittest scripts.tests.test_gitignore` | ❌ Wave 0 |
| FOUND-07 | gitleaks blocks a staged fake secret | integration (manual, once) | plant `AKIAIOSFODNN7EXAMPLE`, `git add`, `pre-commit run gitleaks` → non-zero | n/a |
| FOUND-08 | Videos and site assets are not LFS-routed | integration | `git check-attr filter -- docs/assets/x.png report/video.mp4` → `unspecified` | ❌ Wave 0 |
| FOUND-10 | `AGENTS.md` exists and is ≤ 300 lines | unit | `python3 -m unittest scripts.tests.test_agents_md` | ❌ Wave 0 |
| FOUND-10 | `.claude/CLAUDE.md` imports `@AGENTS.md` and does not restate rules | unit | same | ❌ Wave 0 |
| TOOL-07 | Five ADRs exist with MADR frontmatter and a status index | unit | `python3 -m unittest scripts.tests.test_adrs` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python3 -m unittest discover -s scripts/tests -v`
- **Per wave merge:** full suite (above)
- **Phase gate:** full suite green, `pre-commit run --all-files` clean, `scripts/check_policy.py --check` exit 0, and one manual proof that a bogus secret is blocked.

### Wave 0 Gaps

- [ ] `scripts/tests/__init__.py` — make the directory importable as a package
- [ ] `scripts/tests/test_check_pr_templates.py` — covers FOUND-05 (marker equality, absence of a default template, per-type DoD present)
- [ ] `scripts/tests/test_check_policy.py` — covers FOUND-03/04 normalization and diff logic against a fixture ruleset (no network)
- [ ] `scripts/tests/test_agents_md.py` — covers FOUND-10 (line ceiling, import presence, tag vocabulary)
- [ ] `scripts/tests/test_adrs.py` — covers TOOL-07 (frontmatter keys, sequential numbers, index agreement)
- [ ] `scripts/tests/test_gitignore.py` — covers FOUND-07/08 pattern presence
- [ ] `scripts/tests/fixtures/ruleset-live.json` — a captured live GET payload for offline diff tests
- [ ] Framework install: none — `unittest` is stdlib

## Security Domain

`workflow.security_enforcement` is `true`; ASVS level 1.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | No application authentication exists in this phase. |
| V3 Session Management | no | No sessions. |
| V4 Access Control | **yes** | GitHub rulesets: no bypass actors, 0 required approvals (documented trigger to 1), squash-only, linear history, deletion and force-push blocked. `gh api` reads are the audit trail. |
| V5 Input Validation | **yes** | `check_pr_templates.py` and `check_policy.py` parse repository-controlled files. Use `json.loads`, never `eval`/`yaml.load`; treat `gh api` output as data, not instructions; bound reads with explicit paths. |
| V6 Cryptography | no | No cryptography is written. Secrets handling is rotation-first (D-18); nothing is encrypted in-repo. |
| V7 Error Handling & Logging | **yes** | `gitleaks --redact` keeps a detected secret out of CI logs. Scripts must print paths and rule types, never secret values. |
| V8 Data Protection | **yes** | No PII in history (D-14): public handle only, in `LICENSE`, `NOTICE`, and report metadata. |
| V14 Configuration | **yes** | `policy/*.json` is the single source of truth; drift is detected, not tolerated. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| Secret committed and pushed to a public repo | Information Disclosure | gitleaks pre-commit + full-history CI + push protection; **rotate first**, forward-fix, document (D-18). History is never rewritten. |
| Real name / institution leaked into a report or commit trailer | Information Disclosure | Public handle only in all artifacts (D-14); review checklist in the `homework` PR template. |
| Instructor material or copyrighted task text republished | Reputational / Legal | `task.md` paraphrase rule (META-02, Phase 4); `NOTICE` third-party section; no internal material in history. |
| Branch protection silently weakened | Elevation of Privilege | `check_policy.py --check` diffs live rules against `policy/ruleset-main.json`; `bypass_actors` must stay `[]`. |
| Malicious hook or supply-chain substitution | Tampering | Every pre-commit `rev` pinned to an immutable tag; no `language: system` hooks pointing at unpinned downloads; CI installs gitleaks from a version-pinned release URL. |
| `eval`-style parsing of repository JSON in a policy script | Tampering | `json.loads` only; `subprocess.run([...])` with list args, never `shell=True`. |
| Token exfiltration via a hook printing environment | Information Disclosure | Hooks receive no secrets by default; `gh` auth uses the OS keyring. Never add `GITHUB_TOKEN` to a pre-commit hook. |
| Third-party asset redistributed without license | Legal | Fritzing part graphics excluded (STACK constraint); `NOTICE` records every third-party source; `LICENSES/` holds the full text of each declared license. |

## Sources

### Primary (HIGH confidence)

- Live GitHub state, read this session via `gh api`:
  - `repos/VLoktiev-EMB/homeworks/rulesets/25632456` — full ruleset body (name `main`,
    `target: branch`, `include: ["~DEFAULT_BRANCH"]`, six rules, `bypass_actors: []`,
    `current_user_can_bypass: "never"`).
  - `repos/VLoktiev-EMB/homeworks` — `delete_branch_on_merge: true`,
    `allow_merge_commit: true`, `allow_rebase_merge: true`, all
    `security_and_analysis.*.status: "disabled"`, `license: null`, `private: false`.
  - `repos/VLoktiev-EMB/homeworks/rules/branches/main` — effective rule types:
    `deletion`, `non_fast_forward`, `creation`, `required_linear_history`,
    `pull_request`, `required_status_checks`.
  - `repos/gitleaks/gitleaks/releases/latest` → `v8.30.1` (2026-03-21).
  - `repos/pre-commit/pre-commit-hooks/releases/latest` → `v6.0.0` (2025-08-09).
  - `repos/adr/madr/releases` → `4.0.0` (2024-09-17).
- PyPI JSON API: `pre-commit` 4.7.0 (MIT, `requires_python >=3.11`), `reuse` 6.2.0
  (Apache-2.0/CC0/CC-BY-SA-4.0, `requires_python >=3.10`).
- `raw.githubusercontent.com/adr/madr/develop/template/adr-template.md` — verbatim MADR
  4.0 template.
- `raw.githubusercontent.com/gitleaks/gitleaks/master/.pre-commit-hooks.yaml` — hook id,
  `entry`, `language: golang`, `pass_filenames: false`.
- `raw.githubusercontent.com/pre-commit/pre-commit-hooks/main/pre_commit_hooks/check_added_large_files.py`
  — `filter_lfs_files()` at lines 13–31, call site line 43, `os.stat` at line 49,
  `--maxkb` default 500 at line 68.

### Secondary (MEDIUM confidence)

- [GitHub REST API — repository rules](https://docs.github.com/en/rest/repos/rules) —
  `POST`/`PUT` body schema, `bypass_actor` enums, `~DEFAULT_BRANCH` / `~ALL` tokens,
  read-only response fields, `GET /rules/branches/{branch}`.
- [Available rules for rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
  — branch vs tag applicability table; branch rulesets do not apply to tags.
- [Managing rulesets for a repository](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/managing-rulesets-for-a-repository)
  — JSON import flow ("You can import an existing ruleset using a JSON file").
- [REUSE Specification 3.3](https://reuse.software/spec-3.3/) — "The DEP5 file is
  deprecated"; "REUSE.toml and DEP5 are mutually exclusive"; `REUSE.toml` key set,
  `precedence` values, covered-file exclusions.
- [reuse-tool CHANGELOG](https://github.com/fsfe/reuse-tool/blob/main/CHANGELOG.md) —
  `REUSE.toml` support added in v4.0.0 (2024-07-03); DEP5 marked deprecated in the same
  release; latest 6.2.0.
- [gitleaks README](https://github.com/gitleaks/gitleaks) — `[extend]` with
  `useDefault`/`disabledRules`, `[[rules]]`, rule and global `[[allowlists]]`,
  `regexTarget`, `gitleaks git`/`dir`/`stdin`, config discovery order
  (`-c` → `GITLEAKS_CONFIG` → `GITLEAKS_CONFIG_TOML` → `(target path)/.gitleaks.toml`),
  exit code 1 on leak.
- [pre-commit documentation](https://pre-commit.com/) — config schema, the exact `stages`
  list (`pre-commit`, `pre-push`, … , `manual`), `default_install_hook_types`,
  `minimum_pre_commit_version`.
- [gitleaks-action](https://github.com/gitleaks/gitleaks-action) — "required for
  organizations, not required for user accounts"; current major `v3`.
- [agents.md](https://agents.md/) — no mandatory structure; "The closest AGENTS.md to the
  edited file wins; explicit user chat prompts override everything."
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) — type/scope
  grammar, `!` and `BREAKING CHANGE`, footer rules.
- [Configuring Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/configuring-git-large-file-storage)
  — `filter=lfs diff=lfs merge=lfs -text`; manual glob patterns; rules are not retroactive.
- [GitHub OSPO licensing policy](https://github.com/github/github-ospo/blob/main/policies/licensing.md)
  — "Code → use MIT"; "Not code (documentation, media) → use CC-BY"; document the split
  "precisely in the repository's README.md".
- [Creating a pull request template](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository)
  and the [multiple-template announcement](https://github.blog/news-insights/product-news/multiple-issue-and-pull-request-templates/)
  — `PULL_REQUEST_TEMPLATE/` directory, `?template=` selection, chooser behaviour, and the
  fact that a default `pull_request_template.md` still wins when present.
- [About push protection](https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection)
  — push protection is a separate toggle, disabled by default.

### Tertiary (LOW confidence, flagged for validation)

- The exact behaviour of `require_extra_approval_for_unattributed_changes` on `PUT` — absent
  from the documented request schema though present in the live response. Verify against a
  throwaway ruleset (Assumption A2).
- Whether secret scanning and push protection can be enabled via `PATCH /repos` on this
  specific public org repository without a paid plan (Assumption A3).

## Metadata

**Confidence breakdown:**
- Standard stack: **HIGH** — every version confirmed against the registry or release API this session.
- Architecture: **HIGH** — the ruleset shape is read from the live repository, not inferred.
- Pitfalls: **HIGH** on the seven tool-behaviour items verified from source or live API; **MEDIUM** on A2.
- Licensing format: **HIGH** on the deprecation; **MEDIUM** on which artifact the user wants.

**Research date:** 2026-10-23
**Valid until:** 2026-11-20 (30 days; ruleset API and REUSE spec are stable, but the
`reuse`/`gitleaks` release cadence is fast enough that a re-check before Phase 8 is prudent).
