---
phase: "04"
slug: "metadata-contract-and-scaffolding"
status: verified
threats_open: 0
asvs_level: 1
created: "2026-10-25"
---

# Phase 04 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| filesystem → checker | `homework.yaml` under `homeworks/` is untrusted input parsed by PyYAML | Authored YAML |
| schema file → validator | A malformed or over-permissive schema silently weakens every check | JSON Schema |
| checker → CI | Exit codes and `--json` records are consumed by Phase 8 automation | Process exit / JSON |
| template data → generated project | Every template file becomes code and configuration in a homework directory | Rendered source |
| starter code → shared libraries | The entry point calls `lib/port` through an adapter contract | Public C API |
| rendered project → toolchain | The shared partition path and the shared ini resolve by relative depth | Build configuration |
| task.md → checker | Authored prose plus YAML frontmatter is untrusted input | Authored Markdown |
| allowlist → checker | Committed data can silently widen the Cyrillic gate | Policy configuration |
| docs/decisions → tests | A moved template breaks a path assertion if any consumer is missed | Public documentation |
| CLI arguments → scaffold | `<id>`, `--template` and `--dir` are untrusted input that reach the filesystem | Command line |
| template data → writable tree | Rendered bytes are written into `homeworks/<id>` | Rendered source |
| pre-commit environment → PyPI | The hook installs two pinned packages into an isolated environment | Third-party packages |
| documentation → repository rules | `AGENTS.md` and the ADRs are normative text consumed by agents and reviewers | Public documentation |
| license declaration → published artifacts | `REUSE.toml` decides the license of every new path | License policy |
| filesystem tree → scaffold plan | Existing entries under `homeworks/` may be symlinks or non-directories; the scaffold must classify them without traversing them | Filesystem metadata |
| plan → write phase | Only CREATE records may be written; every CONFLICT or ERROR must stop the run before the first `mkdir` | Plan records |
| authored YAML → loader | `homework.yaml` and `task.md` frontmatter may contain any YAML node, including unhashable keys | Authored YAML |
| checker records → allowlist | An over-broad or stale exemption is a security-relevant change | Policy configuration |
| filesystem path → identity check | `_homework_directory` decides which directory an `id` must equal | Filesystem metadata |
| filesystem path spelling → identity check | The same tree can be named with `/tmp/...` and `/private/tmp/...`; only the ancestor prefix may be reconciled | Filesystem metadata |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-04-01 | Denial of Service | `validate_homework_text` | medium | mitigate | `StrictSafeLoader` (SafeLoader subclass) plus a 64 KiB `MAX_INPUT_BYTES` cap before parsing; oversized or malformed input is an ERROR record at exit 1 | closed |
| T-04-04 | Tampering | `schema/homework.schema.json` | high | mitigate | Every shape is an anchored `pattern`; the suite asserts the schema contains no `format` keyword | closed |
| T-04-20 | Tampering | duplicate YAML mapping keys | medium | mitigate | `StrictSafeLoader.construct_mapping` rejects a repeated key and names it; a duplicate-key fixture asserts exit 1 | closed |
| T-04-07 | Repudiation | checker output | medium | mitigate | Sorted paths, no timestamps, no writes; a test compares two consecutive runs byte-for-byte | closed |
| T-04-08 | Information Disclosure | record rendering | low | mitigate | Repository-relative POSIX paths only; no absolute root or identity is echoed | closed |
| T-04-SC (04-01) | Tampering | package installs (`uv`, pre-commit) | high | mitigate | Blocking human-verify gate before the first install; PyYAML 6.0.3 and jsonschema 4.26.0 pinned in the PEP 723 header | closed |
| T-04-06 | Tampering | `templates/**` | high | mitigate | Closed placeholder map (`PLACEHOLDER` regex) plus a lint that rejects any unknown `{{token}}` and any `${...}` interpolation | closed |
| T-04-09 | Tampering | `templates/homework-*/src/main.cpp` | medium | mitigate | The entry point includes only `port/` and adapter headers through `extern "C"` contracts | closed |
| T-04-10 | Repudiation | template content | medium | mitigate | No template carries a timestamp, a build output or a generated CMake file | closed |
| T-04-SC (04-02) | Tampering | package installs | high | mitigate | This plan installs nothing; pins are owned by 04-01 and re-verified by 04-04's drift test | closed |
| T-04-05 | Information Disclosure | `validate_task_text` Cyrillic scan | high | mitigate | Per-character `unicodedata.name`-based `is_cyrillic_char` covering every assigned Cyrillic block; suppression only through an exact-path allowlist entry with a non-empty reason | closed |
| T-04-15 | Denial of Service | frontmatter parsing | medium | mitigate | `StrictBaseLoader` only, 64 KiB cap, fence and mapping shape validated before use; malformed input is an ERROR record at exit 1 | closed |
| T-04-11 | Tampering | `source.reference` / `source_url` authority split | medium | mitigate | Cross-validation makes a disagreement exit 1; the sentinel rule closes the same status branch used for the four task fields | closed |
| T-04-16 | Tampering | `templates/adr/template.md` | low | mitigate | The scaffold renders only `templates/homework-<name>/` and `templates/task/task.md`, so the MADR single-brace template is never interpolated | closed |
| T-04-21 | Tampering | duplicate `task.md` frontmatter keys | medium | mitigate | `StrictBaseLoader.construct_mapping` rejects a repeated key and names it; a duplicate-key fixture asserts exit 1 | closed |
| T-04-SC (04-03) | Tampering | package installs | high | mitigate | No new package is declared; pins remain owned by 04-01 and are re-checked in 04-04 | closed |
| T-04-02 | Tampering | `scripts/new_homework` path resolution | high | mitigate | Anchored `HOMEWORK_ID` check, `TEMPLATE_NAME` regex, dynamic resolution to `templates/homework-<name>/template.yaml`, and a `resolve()` + `relative_to()` containment proof | closed |
| T-04-03 | Tampering / Elevation of Privilege | atomic writes and symlinks | high | mitigate | Symlinked template entries and targets are refused; `mkstemp` in the lstat-verified target directory then `os.replace`; nothing is written before the whole candidate validates | closed |
| T-04-17 | Repudiation | scaffold output | high | mitigate | Sorted paths, no clock read, byte-based idempotency, two committed golden trees and a two-run byte-identity test | closed |
| T-04-18 | Information Disclosure | record rendering | low | mitigate | Repository-relative POSIX paths only; the temporary root is never echoed | closed |
| T-04-SC (04-04) | Tampering | pre-commit installs two PyPI packages | high | mitigate | Both versions pinned; the drift test keeps the PEP 723 header and the pre-commit declaration identical | closed |
| T-04-12 | Repudiation | ADR Confirmation sections | medium | mitigate | Each Confirmation names commands runnable today and names Phase 8 as the CI owner | closed |
| T-04-13 | Tampering | `REUSE.toml` annotation order | high | mitigate | The MIT catch-all stays first and the CC-BY-4.0 annotation follows it; `reuse lint` and the license-hygiene test are the gates | closed |
| T-04-14 | Repudiation | `AGENTS.md` repository layout | medium | mitigate | Paths that exist moved out of "Planned"; the 300-line ceiling is re-run | closed |
| T-04-19 | Tampering | `AGENTS.md` rulebook invariants | high | mitigate | Exactly one backticked anchored homework-ID regex (1 span) and a 227-line file against the 300-line ceiling | closed |
| T-04-SC (04-05) | Tampering | package installs during the gate | high | mitigate | The gate installs nothing new; it reuses the pins fixed by 04-01 and 04-04 | closed |
| T-04-22 | Tampering | `scripts/new_homework` target-component walk (`_component_conflict`) | high | mitigate | `os.lstat` every component before any `exists()`/`read_bytes()`; a symlinked intermediate component is CONFLICT and blocks the write phase | closed |
| T-04-23 | Elevation of Privilege | write phase (`_write_all`, `_write_atomic`) | high | mitigate | `_write_all` runs only when no record is CONFLICT or ERROR (line 524–529); each file goes through `mkstemp` in the verified target directory and `os.replace` | closed |
| T-04-SC (04-06) | Tampering | PyPI pins for `scripts/new_homework` | high | mitigate | No dependency change: PyYAML 6.0.3 and jsonschema 4.26.0 stay aligned by `test_metadata_deps.py` | closed |
| T-04-24 | Tampering / Denial of Service | `StrictSafeLoader` and `StrictBaseLoader` `construct_mapping` | high | mitigate | An unhashable constructed key delegates to `BaseConstructor.construct_mapping`, raising `ConstructorError`; both validators convert it to an ERROR record at exit 1 | closed |
| T-04-25 | Repudiation | `apply_allowlist` in `scripts/metadata/contract.py` | medium | mitigate | Suppression is keyed on the exact record path; an entry that suppressed no record is returned as stale and fails the run | closed |
| T-04-SC (04-07) | Tampering | PyPI pins for the checker and scaffold | high | mitigate | No dependency change; both entry scripts stay aligned with the pre-commit hook | closed |
| T-04-26 | Tampering / Elevation of Privilege | `scripts/new_homework` `_contained_target` base inspection | high | mitigate | `os.lstat` the `homeworks` base before `_build_plan`; a symlink or non-directory exits 2, and the resolved base must equal `<root>/homeworks` | closed |
| T-04-27 | Tampering | `scripts/metadata/contract.py` `_homework_directory` | medium | mitigate | The containing directory is derived from lexical `os.path.abspath` parts, never from `resolve()`, so a symlinked ancestor cannot disable the id-equals-directory rule | closed |
| T-04-28 | Tampering (TOCTOU) | plan→write window in `_write_all` | medium | accept | Accepted debt: closing the window needs directory file descriptors or `O_NOFOLLOW`; the deterministic symlinked-base escape is removed and the residual needs a concurrent local actor | closed |
| T-04-SC (04-08) | Tampering | PyPI pins for the checker and scaffold | high | mitigate | No dependency change; both entry scripts stay aligned with the pre-commit hook | closed |
| T-04-29 | Tampering | `scripts/metadata/contract.py` `_homework_directory` | high | mitigate | Only the ancestor prefix is reconciled with `resolve()`, so an ordinary `/tmp` versus `/private/tmp` invocation no longer returns `None`; the mismatch stays an ERROR record at exit 1 | closed |
| T-04-30 | Tampering / Elevation of Privilege | `homeworks` component and tail in `_homework_directory` | medium | mitigate | Requires `parts[-3] == "homeworks"` and `parts[-1] == "homework.yaml"`, returning `parts[-2]` without resolving the base | closed |
| T-04-SC (04-09) | Tampering | PyPI pins for the checker and scaffold | high | mitigate | No dependency change; `test_metadata_deps.py` still aligns both entry scripts with the pre-commit hook | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

**Totals:** 39 threats, 39 closed, 0 open. No open threat is at or above the `high` block threshold.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-04-01 | T-04-28 | TOCTOU between plan and write in `_write_all`: a component swapped after classification could redirect a write. Closing it needs directory file descriptors or `O_NOFOLLOW`; the verifier recorded no deterministic evidence, and exploitation needs a concurrent local actor. The deterministic symlinked-base escape is removed. | repository maintainer | 2026-10-25 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-25 | 39 | 39 | 0 | gsd-secure-phase orchestrator (Claude) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-25
