---
phase: "03"
slug: "shared-core-and-dependency-rule"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-24"
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` (stdlib) + Unity 2.6.1 (C) |
| **Config file** | none — `python3 -m unittest discover -s scripts/tests -v`; PlatformIO config at `tests/platformio.ini` |
| **Quick run command** | `python3 -m unittest discover -s scripts/tests -v` |
| **Full suite command** | `pio test -d tests -e native && python3 -m unittest discover -s scripts/tests -v && pre-commit run --all-files` |
| **Estimated runtime** | ~90 seconds (20-run determinism test dominates) |

---

## Sampling Rate

- **After every task commit:** `python3 -m unittest discover -s scripts/tests -v`; for C
  changes also `pio test -d tests -e native`.
- **After every plan wave:** the full suite command above.
- **Before `/gsd-verify-work`:** Full suite must be green, plus a manual 20-run
  determinism confirmation.
- **Max feedback latency:** ~120 seconds per task.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | D-18 | T-03-01 / — | Partitions path resolved inside the repo root | unit (Python) | `python3 -m unittest scripts.tests.test_pio_scripts -v` | ✅ exists | ✅ green |
| 03-02-01 | 02 | 2 | D-19, D-20 | — | Test suite never hard-reads a deleted project | unit (Python) | `python3 -m unittest scripts.tests.test_pio_scripts -v` | ✅ exists | ✅ green |
| 03-03-01 | 03 | 2 | D-01, D-02 | — | ADR numbering stays sequential and permanent | unit (Python) | `python3 -m unittest scripts.tests.test_adrs -v` | ✅ exists | ✅ green |
| 03-04-01 | 04 | 3 | ARCH-01, ARCH-07 | T-03-02 / — | Header-only contracts, no framework includes | static scan (Python) | `python3 -m unittest scripts.tests.test_architecture_headers -v` | ✅ exists | ✅ green |
| 03-04-02 | 04 | 3 | ARCH-01 | — | Contracts callable through a vtable | unit (C) | `pio test -d tests -e native --filter test_port_contracts` | ✅ exists | ✅ green |
| 03-05-01 | 05 | 3 | ARCH-03 | — | Fakes mirror the real contract and inject errors | unit (C) | `pio test -d tests -e native --filter test_host_fakes` | ✅ exists | ✅ green |
| 03-06-01 | 06 | 3 | ARCH-02 | — | No blocking/sleep token in `common` | unit (C + Python) | `pio test -d tests -e native --filter test_common_*`; `python3 -m unittest scripts.tests.test_check_architecture -v` | ✅ exists | ✅ green |
| 03-07-01 | 07 | 4 | ARCH-06 | — | Native project builds without a target toolchain | integration (PlatformIO) | `python3 -m unittest scripts.tests.test_native_purity -v` | ✅ exists | ✅ green |
| 03-07-02 | 07 | 4 | ARCH-06 | — | Identical suite result over 20 runs | integration (PlatformIO) | `python3 -m unittest scripts.tests.test_native_determinism -v` | ✅ exists | ✅ green |
| 03-08-01 | 08 | 5 | ARCH-05 | T-03-03 / — | Checker rejects every forbidden edge; no silent pass | unit (Python, fixture trees) | `python3 -m unittest scripts.tests.test_check_architecture -v` | ✅ exists | ✅ green |
| 03-08-02 | 08 | 5 | ARCH-05 | — | Local hook blocks a forbidden include | pre-commit | `pre-commit run check-architecture --all-files` | ✅ exists | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/platformio.ini` and `tests/test/test_*/*.c` — the entire native project.
- [x] `scripts/architecture/allowlist.json` — empty, schema described in the checker.
- [x] `scripts/tests/test_check_architecture.py` — positive tree + at least twelve negative
      fixture cases (framework include, adapter include, reverse edge, adapter→common,
      `host`→framework, path escape, blocking token, allowlisted violation, stale
      allowlist, malformed allowlist, multi-adapter env, `host` in target env).
- [x] `scripts/tests/test_architecture_headers.py` — header layout, `#pragma once`,
      `extern "C"` guard, C-standard-only includes for `port`/`common`/`host`.
- [x] `scripts/tests/test_native_determinism.py` — 20 runs, normalized digest, explicit
      failure when `pio` is absent.
- [x] `scripts/tests/test_native_purity.py` — host-compiler-only compile database and the
      negative `pio run` build.
- [x] No framework install needed: Python tests are stdlib-only; Unity arrives through
      PlatformIO on the first test run.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| No universal HAL / whole-driver abstraction in the five headers | ARCH-07 | Requires judgment over API shape, not a machine-checkable property | Read `lib/port/include/port/*.h`; confirm each contract exposes bus-level transfer/read/write only, with no driver-state struct and no framework type |
| `common` contains no homework-specific logic | ARCH-02, D-12 | Semantic judgment; the scanner can only catch known tokens | Read `lib/common/` and confirm only `ring_buffer`, `timing`, and `crc`/`hex` primitives are present |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 120s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-10-24 — 11/11 mapped behaviors green; two manual-only
judgment checks remain deliberately human (ARCH-07 API shape, ARCH-02 domain scope).

## Validation Audit 2026-10-23

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
