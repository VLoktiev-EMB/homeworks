---
phase: "07"
slug: "simulation-spike"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-26"
---

# Phase 07 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| build path → shell command | PlatformIO build paths are interpolated into one `env.Execute` command string; a repository-controlled path containing spaces crosses here | repository paths (low) |
| test process → child `wokwi-cli` | The test spawns a third-party CLI with a composed environment; a token could leak into that child | child environment (medium) |
| repository → external tool binary | `wokwi-cli` is an unsigned GitHub-release binary; the phase records its version and short SHA | version metadata (low) |
| owner shell → Wokwi cloud | A bearer token crosses to `wss://wokwi.com/api/ws/beta` | bearer token (high) |
| repository → hosted simulator | `diagram.json`, `scenario.yaml`, the merged image and the ELF are uploaded per run | design and firmware inputs (medium) |
| vendor dashboard → evidence record | Quota consumption is observed only by the vendor | quota figures (low) |
| owner shell → container registry | The image is pulled from `ghcr.io` under a mutable tag | image tag and digest (medium) |
| container → host | Named volumes and a published port `3080` cross into the host | container state (medium) |
| container → repository | Nothing should cross: the AGPL image must not contaminate the MIT tree | none permitted (high) |
| metadata → generated views | `homework.yaml` and the ADR are inputs; the committed pages and nav are outputs | metadata (low) |
| evidence record → decision record | The ADR restates conclusions drawn from measured data; the handoff outcome is the only status gate | measurements (low) |
| external licence → repository | Fritzing and Velxio terms constrain what may be copied | licence-bound assets (high) |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-07-01 | Information disclosure | `scripts/tests/test_simulation_paths.py` | medium | mitigate | The child environment carries the literal `dummy` only and exactly four variable names; the module never reads an ambient `WOKWI_CLI_TOKEN` and never writes one to a log or fixture (`test_simulation_paths.py:43-49`). | closed |
| T-07-02 | Tampering | `env.Execute` command string in `scripts/pio/merge_firmware.py` | medium | mitigate | Every path argument passes through `_quote`; `test_every_image_path_is_quoted` asserts the quoting (`merge_firmware.py:43`, `test_merge_firmware.py:160`). The docstring claims quoting, not general shell-metacharacter sanitization. | closed |
| T-07-03 | Information disclosure | `WOKWI_CLI_TOKEN` in the owner shell | high | mitigate | `read -rs` at a silent prompt; no `set -x`; no argument, file or evidence write; the only permitted sentence is `token supplied by the repository owner; value not recorded` (`07-SPIKE-EVIDENCE.md:27,72,75`). | closed |
| T-07-04 | Tampering | `curl \| sh` CLI installer supply chain | medium | mitigate | No reinstall in this phase; the installed binary is pinned at `0.28.1 (7cf4ffaebfd8)` and recorded (`07-SPIKE-EVIDENCE.md:303`). | closed |
| T-07-05 | Tampering / denial of service | `diagram.json` and `scenario.yaml` sent to the hosted service | medium | mitigate | `wokwi-cli lint --offline` exits 0 before the paid session (`07-SPIKE-EVIDENCE.md:305`); the inputs are repository-reviewed in the same pull request. | closed |
| T-07-06 | Tampering | `ghcr.io/.../velxio:master` mutable tag | high | mitigate | The `RepoDigests` digest is the recorded identity; the container is named `velxio` and removed after capture (`07-SPIKE-EVIDENCE.md:131-136,182`). | closed |
| T-07-07 | Legal (non-STRIDE) | AGPLv3 image | high | mitigate | The image is referenced only; no source, layer or asset is vendored into the MIT repository; the boundary is stated in the evidence and in ADR-0014 §Licence boundary (`0014-simulator-selection.md:158`). | closed |
| T-07-08 | Repudiation / integrity | ADR-0014 and the report prose | high | mitigate | The five-label vocabulary is preserved (`07-SPIKE-EVIDENCE.md:12-20`); `simulated` never becomes `measured`; the ADR states no electrical claim (`0014-simulator-selection.md:144`); the whole-file forbidden-phrase sweep gates the report. | closed |
| T-07-09 | Tampering | generated files and `generated.manifest` | medium | mitigate | Only `scripts/gen_views.py --all` writes them; `--check` and the docs-pins nav test gate the result; the manifest digest is refreshed in the same change (`07-VALIDATION.md:54`). | closed |
| T-07-10 | Repudiation | the CI cost basis | medium | mitigate | The result is labelled `calculated`; inputs carry their own labels; `PRs_per_month = 20` is stated; sensitivity at 5 and 50 is shown; no CI run is claimed (`0014-simulator-selection.md:105-121`). | closed |
| T-07-11 | Repudiation | `simulation.status` versus the evidence | high | mitigate | The status flip reads `**Outcome:** scenario passed`; a failed or blocked outcome leaves `pending` and records the blocker (`07-SPIKE-EVIDENCE.md:633,641`; `report.md` T-15). | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

No accepted risks.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-26 | 11 | 11 | 0 | Claude (gsd-secure-phase) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-26
