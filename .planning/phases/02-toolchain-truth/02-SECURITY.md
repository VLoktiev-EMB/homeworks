---
phase: "02"
slug: "toolchain-truth"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-23"
---

# Phase 02 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Repository source tree ↔ PlatformIO registry | Pinned packages and toolchains are downloaded once and executed locally | Platform and toolchain binaries; version pins |
| Shared config ↔ project environments | `platformio.shared.ini` supplies board, flash and PSRAM settings through named template sections | Build flags, partition table, SDK configuration |
| Build artifacts ↔ git index | `.pio/`, `compile_commands.json`, generated `CMakeLists.txt` and `sdkconfig.<env>` are produced by the build | Generated files, absolute local paths |
| Evidence ↔ claims | 16 MB flash and octal PSRAM are asserted from images and generated config, never from `platformio.ini` | Build artifacts, image headers |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-02-01 | Tampering | `platformio.shared.ini` version pins | high | mitigate | Exact pin `platform = espressif32@8.0.0`; `pio --version` 6.2.0 and `pio pkg show` 8.0.0 re-checked at the phase gate (02-05) | closed |
| T-02-02 | Elevation of Privilege | `scripts/pio/compiledb.py` through `extra_scripts` | medium | mitigate | One repository script, relative `pre:../../scripts/pio/compiledb.py` path, no `shell=True`, one SCons key; data-level contract test in `scripts/tests/test_pio_scripts.py` | closed |
| T-02-03 | Information Disclosure | `compile_commands.json` | medium | mitigate | Stays in `.gitignore` (D-18), absent from `files_modified`; the committed-script test rejects absolute paths | closed |
| T-02-04 | Information Disclosure | `sdkconfig.<env>`, `CMakeLists.txt`, `src/CMakeLists.txt` | medium | mitigate | Scoped `.gitignore` patterns plus the extended `no-generated-files` hook; `git check-ignore` and `git ls-files -ci` verified in 02-04 | closed |
| T-02-05 | Tampering (integrity of the source tree) | Over-broad ignore pattern hiding authored config | medium | mitigate | Patterns scoped to `homeworks/*/`; `!homeworks/*/sdkconfig.defaults` re-includes the authored fragment; `VISIBLE` list, pair test and root `CMakeLists.txt` check | closed |
| T-02-06 | Tampering | N16R8 board overrides (`qio_opi`, 16 MB, partition table) | high | mitigate | Evidence from artifacts: `qio_opi/include`, `ARDUINO_PARTITION_default_16MB`, preprocessed `CONFIG_SPIRAM`, `esptool image-info` 16 MB (02-03) | closed |
| T-02-07 | Tampering | `extends` silently dropping the parent `build_flags` | medium | mitigate | `[env:esp32s3_arduino]` carries only `extends` and `lib_deps`; all-record `BOARD_HAS_PSRAM` count proves parent flags survived (02-03) | closed |
| T-02-08 | Tampering | Registry package substitution for `espressif32` | high | mitigate | Exact pin `espressif32@8.0.0`; `pio pkg show` confirms the resolved version; Package Legitimacy Audit in `02-RESEARCH.md` | closed |
| T-02-09 | Tampering | Project partition table substitution | high | mitigate | `default_16MB.csv` is committed source; build succeeds without the missing-table error; image header and `sdkconfig.json` checked independently (02-04) | closed |
| T-02-10 | Tampering | 16 MB / octal PSRAM configuration | high | mitigate | Project-local `sdkconfig.defaults`; `sdkconfig.json` asserts `FLASHSIZE_16MB`, `SPIRAM_MODE_OCT`, `SPIRAM_MODE_QUAD=false`; image header checked (02-04) | closed |
| T-02-11 | Information Disclosure | Build-generated files entering the index | medium | mitigate | Scoped `.gitignore` plus the 02-02 pre-commit hook; re-asserted with `git check-ignore` and `git ls-files -ci` (02-04) | closed |
| T-02-12 | Repudiation | ADR-0007 and the phase SUMMARY | medium | mitigate | MADR record with index entry and date; `scripts/tests/test_adrs.py` enforces title/status/date agreement (02-05) | closed |
| T-02-13 | Tampering | Version pins at the final gate | high | mitigate | `pio --version` 6.2.0 and `pio pkg show platformio/espressif32` 8.0.0 re-run in the end-to-end gate (02-05) | closed |
| T-02-14 | Information Disclosure | Tracked generated artifacts at the final gate | medium | mitigate | `git ls-files -ci --exclude-standard` over the six declared pathspecs returns empty (02-05) | closed |
| T-02-15 | Tampering (misleading evidence) | `-DARDUINO_BOARD` display name | medium | mitigate | Board name excluded from every evidence path; the four artifact checks are the substitute (02-03) | closed |
| T-02-SC | Tampering | PlatformIO package installs | high | mitigate | `02-RESEARCH.md` §Package Legitimacy Audit: every `platformio/*` and `espressif/*` package verdict OK, no SUS or SLOP; exact pins only | closed |

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
| 2026-10-23 | 16 | 16 | 0 | gsd-execute-phase orchestrator (ASVS L1, register authored at plan time) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-23
