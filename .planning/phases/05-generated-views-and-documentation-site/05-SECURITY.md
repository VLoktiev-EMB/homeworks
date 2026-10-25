---
phase: "5"
slug: "generated-views-and-documentation-site"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-26"
---

# Phase 5 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `homework.yaml` / `boards/*.yaml` → generator | Authored repository metadata is parsed and rendered into owned files | Untrusted-ish YAML strings entering Markdown, JSON and INI surfaces |
| generator `--check` → working tree | The drift gate must observe without mutating | Read-only repository state |
| `git diff` → `affected.py` matrix | Changed paths become CI build/simulation inputs | Path strings from git, including attacker-chosen filenames |
| upstream distribution → `docs/assets/vendor/` | Third-party tarball bytes enter the repository | Executable JS, CSS, binary fonts |
| pull request / `main` push → GitHub Actions | Untrusted PR content reaches CI and, on `main`, the Pages deploy | Workflow permissions, OIDC token, published artifact |
| pip/uv → dependency graph | Package installs in the hook, CI and docs builds | Supply-chain trust for `PyYAML`, `mkdocs`, `mkdocs-material`, `pymdown-extensions` |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-5-01 | Tampering | `scripts/metadata/render.py` | medium | mitigate | One non-recursive `re.sub` pass; `RendererContractTests` | closed |
| T-5-02 | Tampering | `scripts/metadata/platformio.py` | medium | mitigate | Rules moved verbatim with review comments; architecture checker exit 0 | closed |
| T-5-03 | Elevation of Privilege | `requirements-docs.txt` | high | mitigate | Exact pins for three named packages; legitimacy audit in RESEARCH | closed |
| T-5-04 | Tampering | `scripts/metadata/board_profile.py` | high | mitigate | `additionalProperties: false`, anchored patterns, enums, `MAX_INPUT_BYTES`, duplicate-key loader; `BoardProfileTests` | closed |
| T-5-05 | Information Disclosure | record paths | medium | mitigate | `contract.relative_path` degrades out-of-root paths to final component | closed |
| T-5-06 | Spoofing | `pinout_url` | low | accept | `https://`-only pattern; destination reviewed as authored content | closed — below high threshold, accepted |
| T-5-07 | Tampering | `_homework_rows` cell rendering | high | mitigate | `_escape_cell` collapses control chars/newlines and escapes `\|`; `EscapeTests` | closed |
| T-5-08 | Tampering | `_component_conflict` / `_write_atomic` | high | mitigate | `lstat` component walk before any read; temp file + `os.replace` | closed |
| T-5-09 | Repudiation | Orphan deletion | high | mitigate | Deletion requires prior manifest entry AND generated header; else `ORPHAN` exit 1 | closed |
| T-5-10 | Tampering | `--check` mode | high | mitigate | No write path in check mode; `RealTreeSmokeTest` asserts clean `git status` | closed |
| T-5-11 | Tampering | `_changed_paths` | high | mitigate | `-z` parsing, `surrogateescape`, containment test rejecting absolute/`..` paths | closed |
| T-5-12 | Repudiation | `_fan_out` fail-safe | high | mitigate | Explicit `NO_BUILD_IMPACT`; everything else widens; `FanoutTests` | closed |
| T-5-13 | Tampering | `_consumers` | medium | mitigate | Graph from `lib_deps` + `library.json` only, read through the 05-01 module; `seen` bounds the walk | closed |
| T-5-14 | Tampering | `workspace` folder fragment | high | mitigate | `json.dumps(ensure_ascii=False)` only; ASCII path with no `..`; `WorkspaceTests` | closed |
| T-5-15 | Tampering | `shared-ini` pin substitution | high | mitigate | Closed `render()` map raises on unknown token or `${...}` | closed |
| T-5-16 | Repudiation | `shared-ini` disagreement | high | mitigate | >1 distinct pin pair blocks with exit 1, one record per homework, no partial write | closed |
| T-5-17 | Tampering | `docs/assets/vendor/katex/0.19.0/**` | high | mitigate | 24-file allowlist, `sha256sum -c` ledger, `PROVENANCE.txt`, discrimination test; `KatexVendoringTests` | closed |
| T-5-18 | Elevation of Privilege | `render-math.js` | medium | mitigate | ASCII-only authored script, four fixed delimiters, never executed at build time | closed |
| T-5-19 | Tampering | Page templates / `_escape_cell` | high | mitigate | Every metadata value escapes; no raw HTML; empty-after-escape title refused | closed |
| T-5-20 | Tampering | Page target paths | high | mitigate | Static allowlist, anchored id/stem patterns, `lstat` walk before write | closed |
| T-5-21 | Repudiation | Orphan scan over page directories | high | mitigate | Orphan exits 1; write mode removes only prior-manifest + generated-header files | closed |
| T-5-22 | Tampering | Decision nav labels | medium | mitigate | Frontmatter skipped, first `# ` heading taken, quotes normalised; `NavTests` | closed |
| T-5-23 | Tampering | `mkdocs.yml` configuration surface | high | mitigate | One template owns the file; `PinConsistencyTests` rejects plugins beyond `search`, `hooks:`, `INHERIT:`, `custom_dir` | closed |
| T-5-24 | Repudiation | Nav completeness | medium | mitigate | Nav path contract asserted; nav set must equal `docs/` Markdown set; strict build is a separately named CI step | closed |
| T-5-25 | Elevation of Privilege | Pull-request drift job | high | mitigate | `permissions: contents: read`, no secrets, no `pull_request_target`, `persist-credentials: false` | closed |
| T-5-26 | Tampering | Deploy workflow | high | mitigate | OIDC + `github-pages` environment, no `contents: write`, no `gh-deploy`, no deploy key; LFS-pointer guard | closed — first deploy verified after merge |
| T-5-27 | Tampering | Every `uses:` reference | high | mitigate | Full 40-hex SHA pins, revalidated with `git ls-remote` before writing; `WorkflowTextTests` | closed |
| T-5-28 | Tampering | `paths.py`, `yaml_loader.py` and re-exports | medium | mitigate | Stdlib/PyYAML-only; `ModuleBoundaryTests` asserts no `jsonschema` or `contract` in `sys.modules` | closed |
| T-5-29 | Tampering | `validate_board_text` YAML parse | high | mitigate | `StrictSafeLoader` rejects duplicate keys; two duplicate-key fixtures prove `safe_load` is not in the path | closed |
| T-5-30 | Tampering | Symlinked board document or `boards/` | medium | mitigate | Symlinked directory is a `CheckError`, symlinked document an `ERROR`; neither followed | closed |
| T-5-31 | Tampering | `_load_homeworks` / generator import graph | high | mitigate | `StrictSafeLoader` exit 2 on duplicate key; `ModuleBoundaryTests` bounds the import graph | closed |
| T-5-32 | Repudiation | `_projects` set and `NO_BUILD_IMPACT` | high | mitigate | Top-level `tests/` consumer included; both directions tested entry by entry | closed |
| T-5-33 | Tampering | Optional `report` block / board-profile parse | medium | mitigate | Missing report renders literal `none`; id/stem mismatch or duplicate key exits 2 before any write | closed |
| T-5-36 | Repudiation | PlatformIO Core pin | high | mitigate | Machine-readable `; PlatformIO Core:` header; `read_shared_core_pin` strict parse; `SharedIniTests` | closed |
| T-5-SC | Tampering | npm/pip/cargo installs | high | mitigate | Only named, versioned pins enter the graph (`PyYAML==6.0.3`; the three docs pins); no new package, no hash pinning per D-30 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

**Verification depth:** ASVS level 1. Register authored at plan time; every `mitigate` row was closed by confirming the named control exists in the merged implementation and that its cited test class or command passes. This is grep-and-test depth, not L2 boundary-placement or L3 end-to-end tracing.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-5-01 | T-5-06 | `pinout_url` is constrained to `https://` but the destination is authored content, not attacker-controlled input. | Repository owner (phase planning) | 2026-10-26 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-26 | 35 | 35 | 0 | gsd-secure-phase (L1 grep + test evidence) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-26
