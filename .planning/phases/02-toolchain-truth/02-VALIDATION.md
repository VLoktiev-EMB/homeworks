---
phase: "2"
slug: "toolchain-truth"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-23"
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | No firmware unit-test framework in this phase (D-16). Evidence is build commands plus artifact assertions. |
| **Config file** | `homeworks/0_0-toolchain-smoke/platformio.ini` |
| **Quick run command** | `cd homeworks/0_0-toolchain-smoke && pio run -e native` |
| **Full suite command** | `pio run -e native && pio run -e esp32s3_arduino && pio run -e esp32s3_espidf` |
| **Estimated runtime** | ~31 s cold (0.34 s + 5.70 s + 24.73 s, re-measured 2026-10-23), < 5 s warm |

---

## Sampling Rate

- **After every task commit:** Run the quick command (`pio run -e native`) — no toolchain
  download, proves the `symlink://` wiring.
- **After every plan wave:** Run the full suite (all three environments).
- **Before `/gsd-verify-work`:** Full suite green, both `compile_commands.json` assertions pass,
  and `esptool image-info` reports `Flash size: 16MB`.
- **Max feedback latency:** 30 seconds.

---

## Per-Task Verification Map

Task IDs are assigned by the planner; this table binds each requirement to its proof now so no
task can silently drop one. `Plan`/`Wave` are filled from the PLAN.md frontmatter after planning.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-05/T2 | 02-05 | 4 | FOUND-09 | T-02-01 | Version pins read from registry, not floating | smoke | `pio --version \| grep -q '6.2.0'` | ✅ | ✅ green |
| 02-05/T2 | 02-05 | 4 | FOUND-09 | T-02-01 | Platform pin resolves to 8.0.0 | smoke | `pio pkg show platformio/espressif32 \| grep -q '8.0.0'` | ✅ | ✅ green |
| 02-03/T2 | 02-03 | 2 | FOUND-09 | T-02-02 | 16 MB flash actually linked (Arduino) | integration | `pio pkg exec -p tool-esptool -- esptool --chip esp32s3 image-info .pio/build/esp32s3_arduino/firmware.bin \| grep -q 'Flash size: 16MB'` | ✅ | ✅ green |
| 02-03/T2 | 02-03 | 2 | FOUND-09 | T-02-02 | Octal PSRAM selected by the Arduino core | integration | `grep -rq 'qio_opi/include' .pio/build/esp32s3_arduino/compile_commands.json` | ✅ | ✅ green |
| 02-04/T2 | 02-04 | 3 | FOUND-09 | T-02-02 | 16 MB + octal PSRAM in ESP-IDF sdkconfig | integration | Python assert on `.pio/build/esp32s3_espidf/config/sdkconfig.json` (`FLASHSIZE_16MB`, `SPIRAM_MODE_OCT`) | ✅ | ✅ green |
| 02-01/T1 | 02-01 | 1 | ARCH-04 | T-02-03 | Symlinked libraries actually link (native) | integration | `pio run -e native` then assert LDF graph names `common` and `port` | ✅ | ✅ green |
| 02-03/T2 | 02-03 | 2 | ARCH-04 | T-02-03 | CDB contains shared-library sources (Arduino) | integration | Python assert over `compile_commands.json` after `-e esp32s3_arduino` for `lib/common/src/`, `lib/port/src/`, adapter and `src/main.cpp` (64 entries observed) | ✅ | ✅ green |
| 02-04/T2 | 02-04 | 3 | ARCH-04 | T-02-03 | CDB contains shared-library sources (ESP-IDF) | integration | Python assert over `compile_commands.json` after `-e esp32s3_espidf` for the same four sources (1074 entries observed) | ✅ | ✅ green |
| 02-01/T2 | 02-01 | 1 | ARCH-04 | T-02-03 | Every library declares itself | static | `python3 -m unittest scripts.tests.test_pio_scripts` asserts all five `library.json` manifests | ✅ | ✅ green |
| 02-05/T2 | 02-05 | 4 | D-03 | — | No generator ran; file committed by hand | review | `git log --diff-filter=A -- platformio.shared.ini` shows a hand-authored add, no script | ✅ | ✅ green (bounded source audit: mentions=6, write-like=0) |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] A small Python assertion helper for `compile_commands.json` — satisfied inline: each
      environment's checks run immediately after its own `-t compiledb` (D-19 order), and a
      permanent gate remains Phase 8 (TOOL-05/TOOL-06).
- [x] `scripts/tests/test_pio_scripts.py` — committed in 02-01 with 11 data-level tests; the
      repository suite runs it via `python3 -m unittest discover -s scripts/tests`.
- [x] A fixture that isolates the CDB between environments — ordering, not a fixture: the
      single database is asserted right after the build that produced it (P8), as recorded in
      02-03, 02-04 and 02-05.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `platformio.shared.ini` was authored, not generated | D-03 | Absence of a generator is a negative claim; no command can prove it | Review the commit that adds the file; confirm no `scripts/` entry writes it |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s (warm full suite; cold first ESP-IDF build is documented as slower)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-10-23 — 5 plans, 10 tasks, all FOUND-09 and ARCH-04 proofs green;
one manual-only claim (D-03) retained with a bounded source audit.

## Validation Audit 2026-10-23

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
