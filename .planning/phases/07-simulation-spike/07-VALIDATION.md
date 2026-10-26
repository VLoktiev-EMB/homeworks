---
phase: "7"
slug: "simulation-spike"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-26"
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` (stdlib), 378 tests |
| **Config file** | none — discovery via `scripts/tests/` |
| **Quick run command** | `python3 -m unittest scripts.tests.test_simulation_paths scripts.tests.test_merge_firmware -v` |
| **Full suite command** | `UV_CACHE_DIR="$TMPDIR/uvcache" python3 -m unittest discover -s scripts/tests -t .` |
| **Estimated runtime** | targeted ~2 s; full suite ~37 s |

Sandbox note: the full suite fails 76 tests inside the command sandbox unless `UV_CACHE_DIR`
points at a writable directory. Use the `UV_CACHE_DIR` form in any agent-run gate.

---

## Sampling Rate

- **After every task commit:** Run the targeted modules for the touched area, plus
  `UV_CACHE_DIR="$TMPDIR/uvcache" uv run scripts/gen_views.py --all --check`
- **After every plan wave:** Run the full suite (378 tests) plus `pre-commit run --all-files`
- **Before `/gsd-verify-work`:** Full suite green, `gen-views-check` green, `wokwi-cli lint`
  exit 0, and `07-SPIKE-EVIDENCE.md` complete
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 7-01-01 | 01 | 1 | SIM-02 | T-07-01 | Token never written to a file, argv, or transcript | unit (pure function) | `python3 -m unittest scripts.tests.test_merge_firmware -v` | ✅ `scripts/tests/test_merge_firmware.py` | ✅ green |
| 7-01-02 | 01 | 1 | SIM-02 | T-07-01 | Documented command resolves option paths relative to the positional project dir | unit (subprocess) | `python3 -m unittest scripts.tests.test_simulation_paths -v` | ✅ `scripts/tests/test_simulation_paths.py` | ✅ green |
| 7-01-03 | 01 | 1 | SIM-02 | T-07-05 | Malformed inputs rejected offline by `lint` before any session | CLI exit code | `wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json` | ✅ command exists | ✅ green (exit 0, `Found 1 info`) |
| 7-02-01 | 02 | 2 | SIM-02 | T-07-03 | Token read with `read -rs`, never echoed, never logged | manual-only | owner-run checkpoint with fixed capture format | ✅ three runs recorded in `07-SPIKE-EVIDENCE.md` | ✅ green (3/3, exit 0) |
| 7-03-01 | 03 | 3 | SIM-02 | T-07-06 | Mutable container tag is pinned by recording `RepoDigests` | manual-only | owner-run checkpoint; digest recorded in evidence | ✅ digest recorded | ✅ green |
| 7-04-01 | 04 | 4 | SIM-02 | T-07-08 | Simulator output never presented as hardware evidence | unit (existing) | `python3 -m unittest scripts.tests.test_docs_pins.PinConsistencyTests.test_nav_lists_every_markdown_file_under_docs` | ✅ existing test | ✅ green |
| 7-04-02 | 04 | 4 | SIM-02 | T-07-09 | Generated views regenerate after the status flip and ADR addition | generator check | `UV_CACHE_DIR="$TMPDIR/uvcache" uv run scripts/gen_views.py --all --check` | ✅ command exists | ✅ green |
| 7-04-03 | 04 | 4 | SIM-03 | — | No Fritzing part graphics copied into assets or docs | manual-only | review: no new files under `docs/assets/` or `homeworks/*/assets/` | ✅ ADR-0014 paragraph reviewed; no part graphic added | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `scripts/tests/test_simulation_paths.py` — F-19 positive / negative / non-vacuity cases;
      skips when `shutil.which("wokwi-cli") is None` (repo convention)
- [x] `scripts/tests/test_merge_firmware.py` — imports the promoted module with a stub `env`;
      asserts argv order, `-o` target, quoting, and the missing-package message
- [x] `scripts/pio/merge_firmware.py` — the promoted file (Wave 0 because both the build and
      the tests consume it)
- [x] `pyproject.toml` — remove the now-dead `homeworks/*/merge_firmware.py` F821 ignore

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Executed Wokwi session (cold, warm, repeat) | SIM-02 | Token-gated and quota-metered; automating it would spend the owner's quota on every suite run | Follow the owner-run protocol in `07-RESEARCH.md` §Measurement Protocol Step 2; capture exit code, serial log, and dashboard delta per run |
| Velxio self-host boot attempt | SIM-02 | Docker daemon unreachable inside the sandbox; image pull needs the owner's network | Run the documented `docker run`, record digest, boot time, board list; record `not measured — <reason>` if it fails |
| Quota delta observation | SIM-02 | Only the vendor dashboard observes consumption | Note usage before and after each run; if granularity is coarse, record the `--timeout` bound labelled `calculated (upper bound)` |
| Fritzing licence boundary | SIM-03 | No artifact is produced; the criterion is an ADR paragraph | Review ADR-0014 for the attribution and part-graphics restriction statement |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-10-26

## Validation Audit 2026-10-26

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
