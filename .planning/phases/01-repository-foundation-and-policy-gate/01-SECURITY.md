---
phase: "01"
slug: "repository-foundation-and-policy-gate"
status: verified
threats_open: 0
asvs_level: 1
created: "2026-10-23"
---

# Phase 01 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| committed policy → live GitHub | `check_policy.py` reads repository-controlled JSON and live API responses; either side influences the drift verdict. | Policy configuration (non-secret), ruleset definitions |
| developer workstation → GitHub | `gh api` credentials live in the OS keyring; output must never include tokens. | OAuth token (secret, never emitted) |
| working tree → git index | Attribute and ignore rules decide what enters permanent public history. | Source, binaries, possible secrets |
| developer workstation → public history | The staged hook is the last local chance to stop a secret; CI is the backstop. | Repository content, secret material |
| CI runner → public logs | A detected secret is sensitive inside the build log itself. | Gitleaks findings (redacted) |
| third-party code → hook execution | pre-commit hooks ship executable code from pinned revisions. | Third-party code |
| repository artifacts → public readership | Every published byte carries identity and license grant permanently. | License text, author identity |
| third-party content → redistribution | Copied templates or graphics without attribution create legal exposure. | MADR template, Fritzing graphics |
| template directory → contributor checklist | Template text is the reviewer's contract. | PR templates |
| rulebook → agent behavior | Every later agent run follows these rules. | AGENTS.md rules |
| adapter → generator ownership | GSD owns marker blocks in the adapter. | Generator markers |
| decision records → future maintainers | The index is the machine-readable surface. | ADR numbering and index |
| human operator → tags on origin | A manual tag can be duplicated, moved, or force-pushed; no tag ruleset exists. | Tag refs |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-1-01 | Elevation of Privilege | ruleset-main.json / live ruleset | high | mitigate | `check_policy.py --check` diffs the normalized writable subset; `bypass_actors` asserted empty; drift exits 1. Verified: `policy/ruleset-main.json` has `bypass_actors: []`. | closed |
| T-1-02 | Information Disclosure | secret committed and pushed | critical | mitigate | gitleaks pre-commit (staged, redacted) plus full-history CI scan on every PR; server-side push protection enabled in `policy/repository.json`; rotate-first incident rule in `AGENTS.md`. | closed |
| T-1-03 | Information Disclosure | LICENSE / NOTICE / report metadata | high | mitigate | Handle-only rule; `test_license_hygiene.py` compares artifacts against the configured git identity. | closed |
| T-1-04 | Tampering | `scripts/check_policy.py` input parsing | medium | mitigate | `json.loads` only; `subprocess.run` with list arguments; no `eval`, no `yaml.load`, no `shell=True`. | closed |
| T-1-05 | Tampering | supply chain via hook/workflow definitions | medium | mitigate | Hook revs pinned (`v8.30.1`, `v6.0.0`); gitleaks installed from a version-pinned release URL; hosted action contract-tested absent. | closed |
| T-1-06 | Tampering / Legal | third-party attributions | medium | mitigate | `NOTICE`, `LICENSES/`, and `REUSE.toml`; `reuse lint` joins CI; undeclared files fail. | closed |
| T-1-07 | Tampering | `hw/<id>` tag refs | low | accept | Accepted risk documented in ADR-0003 and the Accepted Risks Log below; `scripts/tag_homework.sh` is the only supported path. | closed |
| T-1-08 | Information Disclosure | secret value reaching CI logs | medium | mitigate | `--redact` on every gitleaks invocation (hook entry and CI step); no `GITHUB_TOKEN` in hooks; contract test asserts the flag. | closed |
| T-1-09 | Denial of Service | `.gitattributes` LFS routing | low | mitigate | Only the eight declared extensions route to LFS; everything else stays under the 1024 kB pre-commit guard. Verified: eight `filter=lfs` entries. | closed |
| T-1-10 | Tampering | PR template selection | low | mitigate | `check_pr_templates.py` asserts no default template at any fallback path and keeps the shared header byte-identical. Verified: only the three typed templates exist. | closed |
| T-1-11 | Tampering | `.claude/CLAUDE.md` adapter | low | mitigate | `test_agents_md.py` asserts the adapter imports `AGENTS.md`, carries no duplicated rules, and preserves every generator marker pair. | closed |
| T-1-12 | Repudiation | `docs/decisions/` index | low | mitigate | `test_adrs.py` enforces sequential numbering and index agreement. Verified: ADR-0001…0005 plus index. | closed |
| T-1-13 | Information Disclosure | AGENTS.md / README prose | high | mitigate | Handle-only identity rule; no real name, institution, or email. Verified by repo-wide email grep. | closed |
| T-1-14 | Information Disclosure | ADR prose | high | mitigate | Same handle-only rule across `docs/decisions/`; a no-email test and review. | closed |
| T-1-SC | Tampering | third-party packages (pre-commit, reuse, gitleaks, git-lfs) | high | mitigate | Package-legitimacy audit in `01-RESEARCH.md`; exact version pins; no unpinned install path. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

**threats_open: 0** — no open threat at or above the `high` block threshold.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-1-01 | T-1-07 | Branch rulesets do not apply to tag refs, so a maintainer with push access can move or delete a `hw/<id>` tag outside `scripts/tag_homework.sh`. Accepted for a single-maintainer repository; ADR-0003 records the trigger to revisit (second maintainer, or a tag-immutability requirement). | VLoktiev-EMB | 2026-10-23 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-23 | 15 | 15 | 0 | gsd-secure-phase (ASVS L1, grep-depth) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-23
