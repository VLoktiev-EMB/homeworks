---
phase: "8"
slug: "fast-ci"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-26"
---

# Phase 8 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| fork or contributor branch → pull-request workflow | The diff, the PR title and every `platformio.ini` are contributor-controlled | Untrusted source and metadata |
| GitHub expression context → shell | `${{ }}` values reach `run:` unless routed through `env:` | Contributor-controlled strings |
| downloaded release asset → runner | gitleaks and wokwi-cli binaries arrive over the network | Executable binaries |
| previous runs → cache | A cache entry restores into a later job | Cached toolchains |
| schedule trigger → default-branch checkout | The nightly run executes whatever the default branch contains | Trusted default-branch source |
| git history → job log | A found secret would be printed by a verbose scanner | Secret material |
| pull-request label → job execution | A maintainer-applied label is the only manual switch | Authorization decision |
| scenario output → artifact | The scenario stdout and serial log leave the runner | Reproduction evidence |
| rulebook text → contributor behaviour | A stale claim about a check teaches the wrong gate | Policy text |
| ruleset (UI) → required check | The check name is set by hand outside version control | Merge gate configuration |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-8-01 | Elevation / Tampering | `meta` title step | high | mitigate | `github.event.pull_request.title` enters only through `env: PR_TITLE`; the shell quotes `"$PR_TITLE"`; the regex is a literal | closed |
| T-8-02 | Elevation / Tampering | `build` steps | high | mitigate | `matrix.project` and `matrix.env` enter through `env:` and are quoted; no `${{ matrix.* }}` in a `run:` body | closed |
| T-8-03 | Information Disclosure | `meta`, `changes`, `build` | high | mitigate | Every job declares `contents: read`; none references `secrets.*`; no `pull_request_target` trigger | closed |
| T-8-04 | Tampering | every `uses:` and every pip install | high | mitigate | Actions pin a commit SHA; pip pins exact versions; gitleaks and wokwi binaries are checksum-verified | closed |
| T-8-05 | Tampering | `actions/cache` keys | medium | mitigate | Keys derive from reviewed pin files with no `restore-keys` | closed |
| T-8-06 | Repudiation | `gate` aggregation | high | mitigate | The jq filter allows only `success` and `skipped`; any other dependency result fails the required check | closed |
| T-8-07 | Information Disclosure | nightly `secrets` job log | high | mitigate | The scan runs with `--redact`; the job holds `contents: read` only | closed |
| T-8-08 | Tampering | nightly `build` commands | high | mitigate | `matrix.project` and `matrix.env` arrive through `env:` and are quoted | closed |
| T-8-09 | Tampering | nightly cache | medium | mitigate | The key derives from the reviewed `platformio.shared.ini` pin; no `restore-keys`; only the default branch seeds it | closed |
| T-8-10 | Denial of Service | nightly schedule | low | accept | Per-entry 90-minute budget bounded by GitHub concurrency limits; non-cancelling group; a runaway run is visible and risks no data | closed (accepted) |
| T-8-11 | Information Disclosure | `simulate` job | high | mitigate | Job-level `if` requires the head repository to equal `github.repository`; the token reaches only a job-level `env` and is never echoed | closed |
| T-8-12 | Elevation / Tampering | `simulate` build and scenario steps | high | mitigate | Matrix values enter through `env:` and are quoted; `--scenario` and `--diagram-file` stay project-relative | closed |
| T-8-13 | Tampering | wokwi-cli download | high | mitigate | Pinned to 0.28.1 and checked against the recorded SHA-256 before install | closed |
| T-8-14 | Denial of Service | Wokwi free-tier quota | medium | mitigate | Maintainer label, `max-parallel: 2`, 10-minute job timeout with 15-second scenario timeout, dependency-result checks; nightly never simulates | closed |
| T-8-15 | Information Disclosure | uploaded artifacts | medium | mitigate | Only the serial log, scenario stdout and quota JSON are uploaded, with 7-day retention | closed |
| T-8-16 | Repudiation | `python-tests`, `static-analysis` | medium | mitigate | Both jobs are named in `gate.needs`, so a failure blocks the merge | closed |
| T-8-17 | Repudiation | `AGENTS.md` enforcement claims | medium | mitigate | Every CI claim names a job that exists; the layout names exactly `ci.yml` and `nightly.yml` | closed |
| T-8-18 | Tampering | required-check configuration | medium | mitigate | The ruleset stays a UI artifact; the rename obligation is written into the rulebook and the decision row | closed |
| T-8-19 | Repudiation | decision index | low | accept | Documentation-only change; a missing row is caught in review; no runtime behaviour depends on it | closed (accepted) |
| T-8-20 | Tampering | `meta` step order | high | mitigate | The history scan runs after checkout and before `pre-commit install-hooks`; a test asserts the ordering | closed |
| T-8-21 | Tampering | `simulate` artifact name | high | mitigate | Project and environment values are sanitized in shell into `$GITHUB_ENV`; the upload name reads `${{ env.ARTIFACT_NAME }}` | closed |
| T-8-22 | Denial of Service | quota spent before the policy result | medium | mitigate | `needs: [changes, meta]` with both results required `success` before any metered minute | closed |
| T-8-23 | Repudiation | simulation evidence contract | medium | mitigate | Evidence files are created before the run; `quota.json` records exit code and byte count; upload uses `if: always()` and `if-no-files-found: error` | closed |
| T-8-SC/01 | Tampering | plan 01 pip installs and downloaded binaries | high | mitigate | Exact pins and SHA-256 verification; package-legitimacy audit recorded; no `[SLOP]` package | closed |
| T-8-SC/02 | Tampering | plan 02 gitleaks download | high | mitigate | Pinned 8.30.1 with the committed SHA-256 verified before execution | closed |
| T-8-SC/03 | Tampering | plan 03 pip installs and the wokwi binary | high | mitigate | Exact pins plus a SHA-256 check on the binary | closed |
| T-8-SC/04 | Tampering | plan 04 supply chain | low | accept | The plan installs nothing and downloads nothing | closed (accepted) |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-8-01 | T-8-10 | A runaway nightly is visible as a red scheduled run; no data is at risk and the 90-minute budget is per matrix entry | repository owner | 2026-10-26 |
| AR-8-02 | T-8-19 | A missing decision-index row is a documentation defect caught in review; no runtime behaviour depends on it | repository owner | 2026-10-26 |
| AR-8-03 | T-8-SC/04 | Plan 04 introduces no dependency or download, so the supply-chain surface is unchanged from plan 03 | repository owner | 2026-10-26 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-26 | 27 | 27 | 0 | gsd-secure-phase (ASVS L1) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-26
