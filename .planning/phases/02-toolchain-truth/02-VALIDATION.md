---
phase: "2"
slug: "toolchain-truth"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
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
| **Estimated runtime** | ~26 s cold (0.27 s + 3.28 s + 22.21 s), < 5 s warm |

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
| TBD | TBD | TBD | FOUND-09 | T-02-01 | Version pins read from registry, not floating | smoke | `pio --version \| grep -q '6.2.0'` | ✅ | ⬜ pending |
| TBD | TBD | TBD | FOUND-09 | T-02-01 | Platform pin resolves to 8.0.0 | smoke | `pio pkg show platformio/espressif32 \| grep -q '8.0.0'` | ✅ | ⬜ pending |
| TBD | TBD | TBD | FOUND-09 | T-02-02 | 16 MB flash actually linked (Arduino) | integration | `esptool --chip esp32s3 image-info .pio/build/esp32s3_arduino/firmware.bin \| grep -q 'Flash size: 16MB'` | ✅ | ⬜ pending |
| TBD | TBD | TBD | FOUND-09 | T-02-02 | Octal PSRAM selected by the Arduino core | integration | `grep -rq 'qio_opi/include' .pio/build/esp32s3_arduino/compile_commands.json` | ✅ | ⬜ pending |
| TBD | TBD | TBD | FOUND-09 | T-02-02 | 16 MB + octal PSRAM in ESP-IDF sdkconfig | integration | Python assert on `.pio/build/esp32s3_espidf/config/sdkconfig.json` (`FLASHSIZE_16MB`, `SPIRAM_MODE_OCT`) | ✅ | ⬜ pending |
| TBD | TBD | TBD | ARCH-04 | T-02-03 | Symlinked libraries actually link (native) | integration | `pio run -e native` then assert LDF graph names `common` and `port` | ✅ | ⬜ pending |
| TBD | TBD | TBD | ARCH-04 | T-02-03 | CDB contains shared-library sources (Arduino) | integration | Python assert over `compile_commands.json` after `-e esp32s3_arduino` for `lib/common/src/`, `lib/port/src/`, adapter | ✅ | ⬜ pending |
| TBD | TBD | TBD | ARCH-04 | T-02-03 | CDB contains shared-library sources (ESP-IDF) | integration | Python assert over `compile_commands.json` after `-e esp32s3_espidf` (1074 entries observed) | ✅ | ⬜ pending |
| TBD | TBD | TBD | ARCH-04 | T-02-03 | Every library declares itself | static | `test -f lib/{common,port,arduino,espidf,host}/library.json` | ✅ | ⬜ pending |
| TBD | TBD | TBD | D-03 | — | No generator ran; file committed by hand | review | `git log --diff-filter=A -- platformio.shared.ini` shows a hand-authored add, no script | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] A small Python assertion helper for `compile_commands.json` — today the CDB checks are
      one-off shell snippets. A permanent gate is Phase 8 (TOOL-05/TOOL-06); this phase needs
      only enough to prove the criterion twice.
- [ ] `scripts/tests/test_compiledb.py` — the repository convention is that every new script
      under `scripts/` participates in `python3 -m unittest discover -s scripts/tests`.
      A minimal test (file exists, imports cleanly, no syntax errors) belongs in this phase.
- [ ] A fixture that isolates the CDB between environments (the same file is overwritten on each
      `-t compiledb` run, so assertions must run immediately after the matching build).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `platformio.shared.ini` was authored, not generated | D-03 | Absence of a generator is a negative claim; no command can prove it | Review the commit that adds the file; confirm no `scripts/` entry writes it |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
