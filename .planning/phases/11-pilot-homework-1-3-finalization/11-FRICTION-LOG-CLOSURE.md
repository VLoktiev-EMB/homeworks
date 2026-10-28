# Phase 11 Friction Log Closure: Disposition of F-01 through F-19

This document records the final audit and formal closure of all nineteen friction points identified during the Phase 4.2 tracer homework implementation (`04.2-FRICTION-LOG.md`), in accordance with decision D-11-13 and requirement PILOT-02.

Every item in the log has either been resolved by automated tooling built in Phases 5 through 11 or closed by an explicit architectural decision recorded in the repository.

---

## Friction Audit and Dispositions

| ID | Title / Step | Resolution & Evidence | Status |
|---|---|---|---|
| **F-01** | Scaffold homework idempotency and caching | Resolved in Phase 4 and Phase 5 (`scripts/new_homework`), wrapped in Phase 9 (`new-homework` skill). The scaffold detects existing files as `UNCHANGED` and `UV_CACHE_DIR` is standard across all CLI scripts. | **CLOSED** |
| **F-02** | Provenance ISO 8601 timestamp shape | Resolved in Phase 4 and Phase 10: `schema/homework.schema.json` and `scripts/check_metadata.py` enforce ISO 8601 with timezone (`valid_iso8601`); `task.md` template carries compliant default timestamp. | **CLOSED** |
| **F-03** | Cold PlatformIO package downloads | Resolved in Phase 8 CI architecture (`ci.yml`): caches `~/.platformio/.cache`, `~/.platformio/packages`, and `~/.cache/pip`. Target build and native test durations drop significantly on warm runs. | **CLOSED** |
| **F-04** | Private library discovery & implicit coupling | Resolved in Phase 5 scaffolding templates: `templates/homework-*/` structure `lib/` with minimal `library.json` (no framework/platform restriction) and clean `lib_deps` declarations. | **CLOSED** |
| **F-05** | Native `-Werror` & fake button default level | Resolved in Phase 5: homework templates and test doubles seed idle `INPUT_PULLUP` pins to `PORT_GPIO_HIGH` and reset mock state in `setUp()`. Native suite compiles cleanly with zero warnings. | **CLOSED** |
| **F-06** | Controller seam high-impedance mode cost | Evaluated under decision D-05: premature abstraction rejected. Controller tracks `as_input` pin state cleanly in `controller.c` (`apply_pin`) in ~10 lines; kept homework-local until multiple homeworks demonstrate recurring need. | **CLOSED** |
| **F-07** | Half-bridge limitations in report | Resolved in Phase 10 and Phase 11: `report.md` Section 4 (Limitations), Section 7, and Decision Appendix explicitly document the high-impedance floating node and SOLID mode precedence. Checked by `check_report.py`. | **CLOSED** |
| **F-08** | Wokwi CLI token gating | Resolved in Phase 7 and Phase 8: offline diagram lint (`wokwi-cli lint --offline`) runs in local pre-commit and PR validation without tokens; CI simulation executes under maintainer label control with repository secrets. | **CLOSED** |
| **F-09** | 16 MB merged image generation | Resolved in Phase 7: promoted `scripts/pio/merge_firmware.py` supporting esptool 5 `merge-bin` syntax and flash boundaries. Shared across all projects requiring partition merging. | **CLOSED** |
| **F-10** | Wokwi CLI option paths & scenario format | Resolved in Phase 7: path resolution relative to project directory validated with `WOKWI_CLI_TOKEN=dummy`. Scenario format pinned and documented in standards and project READMEs. | **CLOSED** |
| **F-11** | Report authoring from bare template | Resolved in Phase 10 & 10.1: `templates/report/report.md` provides full 10-section skeleton; `scripts/check_report.py` enforces structure, headings, and referential integrity. | **CLOSED** |
| **F-12** | Evidence label vocabulary & transition log | Resolved in Phase 10 & Phase 11: closed label vocabulary enforced (`measured`, `calculated`, `simulated`, `datasheet`, `not measured`, `measured (observed)`). Phase 11 added firmware transition logging, satisfying `measured (observed)` on L-10. | **CLOSED** |
| **F-13** | Traceability matrix and decision appendix | Resolved in Phase 10 & Phase 11: matrix structure validated by `check_report.py`; all 20 claims trace directly to verified artifacts, test runs, or documented decisions without drift. | **CLOSED** |
| **F-14** | README & workspace integration edits | Resolved in Phase 5: `scripts/gen_views.py --all` automatically discovers homework projects and renders the root `README.md` table and `homeworks.code-workspace` folders, checked for drift by pre-commit. | **CLOSED** |
| **F-15** | Cold CI run timeout bounds | Resolved in Phase 8: CI job timeout bounded accurately based on measured runner metrics; matrix runs complete in 1-3 minutes. | **CLOSED** |
| **F-16** | Metadata and architecture CI checks | Resolved in Phase 8: `.github/workflows/ci.yml` `meta` job runs `pre-commit run --all-files`, which executes `check_metadata.py`, `check_report.py`, and `check_architecture.py` on every PR. | **CLOSED** |
| **F-17** | GitHub Action pin confirmation | Resolved in Phase 8 & Phase 10.1: action pins verified with immutable SHAs in `ci.yml` and `nightly.yml`, exercised on PR runs. | **CLOSED** |
| **F-18** | IDE untracked files & inner gitignore | Resolved in Phase 5 & Phase 6: `.gitignore` rules updated to ignore inner `.vscode/`, `.pio/`, and compile databases across all homework subtrees. | **CLOSED** |
| **F-19** | Simulation option-path verification | Resolved in Phase 7: path resolution regression tests added to test suite (`test_simulation_paths.py`), and documentation updated to mandate project-relative arguments. | **CLOSED** |

---

## Conclusion

All nineteen friction points identified in Phase 4.2 are formally closed. The repository tooling, testing infrastructure, scaffolding templates, and validation gates established across Phases 5–11 eliminate the original friction, making `homeworks/1_3-police-flasher` a robust reference artifact for future course assignments.
