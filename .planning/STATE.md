---
gsd_state_version: "1.0"
current_phase: 3
current_phase_name: Shared Core and Dependency Rule
status: planning
stopped_at: Phase 02 complete, ready to plan Phase 3
last_updated: "2026-10-23T20:09:15.947Z"
last_activity: 2026-10-23
last_activity_desc: Phase 02 complete, transitioned to Phase 3
state_head: cc013e07011f30505a468f6223a544652f51ee34
progress:
  total_phases: 11
  completed_phases: 2
  total_plans: 13
  completed_plans: 13
  percent: 18
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-23)

**Core value:** Every homework ships as a self-contained, reproducible, industry-standard engineering artifact — code, evidence, and report — that can be understood and verified a year later.
**Current focus:** Phase 3 — Shared Core and Dependency Rule

## Current Position

Phase: 3 — Shared Core and Dependency Rule
Plan: Not started
Status: Ready to plan
Last activity: 2026-10-23 — Phase 02 complete, transitioned to Phase 3

Progress: [██░░░░░░░░] 18%

## Performance Metrics

**Velocity:**
- Total plans completed: 13
- Average duration: —
- Total execution time: 0.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 8 | - | - |
| 02 | 5 | - | - |

**Recent Trend:**
- Last 5 plans: —
- Trend: —

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Phase 2: pins validated in practice — PlatformIO Core 6.2.0 + `platformio/espressif32` 8.0.0 build native, Arduino and ESP-IDF; 16 MB flash and octal PSRAM proven from `sdkconfig.json` and `esptool image-info`, never from `platformio.ini`.
- Phase 2: `platformio.shared.ini` is hand-authored; its generator and drift check remain Phase 5 (META-05). ADR-0007 records the `symlink://` + `library.json` decision.
- Phase 2: the entry point is one `.cpp` with `ARDUINO` / `ESP_PLATFORM` / host branches; library sources stay pure C behind `extern "C"` headers.
- Phase 2: ESP-IDF generated files are ignored by scoped `homeworks/*/` patterns plus the extended `no-generated-files` hook; authored `sdkconfig.defaults` stays visible.
- Roadmap: 11 small phases; policy precedes the first public push, metadata contract precedes its generators, and the shared-library dependency rule ships with the shared core.
- Research findings adopted: `lib_deps = <name>=symlink://...` over `lib_extra_dirs`; clang-format 120 documented as an ESP-IDF approximation; esp-clangd; Wokwi primary with Velxio fallback; CI simulation only after the Phase 7 spike; MkDocs Material 9.7.7 with Zensical-compatible config.
- Simulation spike (Phase 7) is the evidence gate: no CI simulation and no simulation-based report claim before ADR-0004.
- Documentation site is folded into Phase 5 (generated views) rather than a standalone single-requirement phase.

### Pending Todos

None yet.

### Blockers/Concerns

- Resolved: the course allows public solutions and does not require AI-assistance disclosure
  (user, 2026-10-23). No Phase 1 sign-off blocker remains.
- STM32 board models are unconfirmed; Renode/Wokwi STM32 paths are deferred to v2 until the
  course reaches STM32.
- **[Phase 2 carry-forward, CR-01]** `platformio.shared.ini` sets
  `board_build.partitions = default_16MB.csv`, which PlatformIO resolves relative to the
  project directory; the only copy lives in `homeworks/0_0-toolchain-smoke/`, which Phase 3
  removes. Move the CSV to a permanent location (and add an existence test) before the smoke
  project is deleted, or every new ESP32 project will fail to build.
- **[Phase 2 carry-forward, WR-01..WR-04]** Tests in `scripts/tests/test_pio_scripts.py`
  hard-read the temporary smoke project; ADR-0007 over-claims test coverage; library version
  is duplicated in each `.c`; several broad `.gitignore` patterns can hide authored files.
  See `.planning/phases/02-toolchain-truth/02-REVIEW.md` and its disposition ledger.

## Deferred Items

Items acknowledged and deferred at milestone close, most recent first:

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-10-23T20:09:15.947Z
Stopped at: Phase 02 complete, ready to plan Phase 3
Resume file: None
