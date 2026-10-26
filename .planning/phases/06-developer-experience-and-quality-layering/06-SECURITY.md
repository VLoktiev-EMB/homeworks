---
phase: "6"
slug: "developer-experience-and-quality-layering"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-26"
---

# Phase 6 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| pre-commit hook environment → repository files | A pinned third-party hook repository runs code on every commit | Executable hook code, repository source |
| formatter / analyzer binary → source tree | clang-format and clang-tidy rewrite or read tracked source | Source bytes, configuration |
| pre-push guard → compile database | The guard decides whether the database is trustworthy for analysis | `compile_commands.json`, source/config mtimes |
| language server wrapper → compiler binaries | `clangd-wrapper.sh` resolves and execs an installed esp-clangd | Executable path, `--query-driver` globs, toolchain packages |
| generator template → generated editor/workspace files | The single editor contract is rendered into owned files | JSON settings, manifest hashes |
| authored docs → published site | Markdown guide and ADRs are rendered by MkDocs | Documentation text, nav structure |
| pre-commit-managed environments → dependency graph | Hook repos and wheels are downloaded at fixed revs | Supply-chain trust for clang-format, clang-tidy, ruff, yamllint, markdownlint-cli2, cpp-linter-hooks |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-6-01 | Tampering | `.pre-commit-config.yaml` `mirrors-clang-format` repo | high | mitigate | Exact tag `v23.1.3`, never a branch or floating rev; `git ls-remote` revalidation recorded in `06-RESEARCH.md`; any bump is a reviewed diff to this file | closed |
| T-6-02 | Elevation of Privilege | `scripts/clangd-wrapper.sh` `--query-driver` | high | mitigate | Exactly two absolute globs limited to PlatformIO `toolchain-*/bin/*` and `tool-*/bin/*`; no recursive all-paths wildcard; `ClangdWrapperTests` asserts the exact argument string; ADR 0013 records the execution implication | closed |
| T-6-03 | Information Disclosure | `.vscode/settings.json`, `scripts/clangd-wrapper.sh` | medium | mitigate | No credential or token in either file (grep-verified); the wrapper reads only `$HOME` and `$PLATFORMIO_CORE_DIR`; gitleaks stays a pre-commit hook | closed |
| T-6-04 | Tampering | `homeworks.code-workspace`, `generated.manifest` | medium | mitigate | Workspace `settings` live in `templates/views/workspace.json.tmpl`; regeneration only through `gen_views.py --all`; `gen-views-check` and `no-generated-files` reject a hand edit | closed |
| T-6-05 | Tampering | markdownlint-cli2 / yamllint / ruff-check file scopes | medium | mitigate | Explicit `files:`/`exclude:` regexes; generated pages named explicitly; `HookLayeringTests` asserts hook ids and stage assignment | closed |
| T-6-06 | Tampering | hook entries that auto-fix | high | mitigate | `ruff-check` used, never `ruff-format`; markdownlint-cli2 and yamllint run with no `--fix`; every hook is check-only per 05/D-21 and leaves the tree byte-identical | closed |
| T-6-07 | Tampering | `scripts/clang-tidy-db`, `cpp-linter-hooks` | high | mitigate | A local guard ordered before the clang-tidy repo exits 1 with the exact regeneration command on absent or stale database; never writes the database; `ClangTidyDbGuardTests` proves every branch | closed |
| T-6-08 | Tampering | clang-tidy version selection | high | mitigate | `--version=23.1.3` pins the wheel to the same LLVM release as clang-format; the platform `tool-clangtidy` 19.1.0 is never used; `HookLayeringTests` asserts the pinned argument | closed |
| T-6-09 | Tampering | `mkdocs.yml`, `generated.manifest` nav entry | medium | mitigate | Nav entry lives in `templates/views/mkdocs.yml.tmpl`; regeneration only through `gen_views.py --all`; `PinConsistencyTests` fails when an authored page is missing from the nav | closed |
| T-6-10 | Information Disclosure / Safety | `docs/standards/vscode.md`, `AGENTS.md` | medium | mitigate | Guide documents only pre-commit-delivered tools and one filesystem symlink; grep-verified absence of `brew install`, `apt-get install`, `pip install --user`, `npm install -g`; `RulebookAndGuideTests` asserts it | closed |
| T-6-SC | Tampering | npm / pip / cargo installs pulled by hook environments and documentation | high | mitigate | `06-RESEARCH.md` §Package Legitimacy Audit lists every hook repo and wheel as OK with no `[ASSUMED]`/`[SUS]` entry; every hook is pinned by exact `rev`; plans 06-02 and 06-05 install no package | closed |

*Status: open · closed · open — below {block_on} threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

No accepted risks.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-26 | 11 | 11 | 0 | gsd-secure-phase (ASVS L1, grep-depth) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
