---
phase: 07
review: 07-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: open
    title: "\u041d\u0435\u0432\u0434\u0430\u043b\u0438\u0439 `esptool merge-bin` \u043d\u0435 \u043f\u0440\u043e\u0432\u0430\u043b\u044e\u0454 \u0437\u0431\u0456\u0440\u043a\u0443 \u2014 `pio run` \u043b\u0438\u0448\u0430\u0454\u0442\u044c\u0441\u044f \u0437\u0435\u043b\u0435\u043d\u0438\u043c"
  - id: WR-01
    severity: warning
    disposition: open
    title: "\u0417\u0430\u044f\u0432\u043b\u0435\u043d\u0438\u0439 implementation commit \u0431\u0456\u043b\u044c\u0448\u0435 \u043d\u0435 \u0454 \u043e\u0441\u0442\u0430\u043d\u043d\u0456\u043c \u043a\u043e\u043c\u0456\u0442\u043e\u043c, \u0449\u043e \u0437\u043c\u0456\u043d\u044e\u0454 build/simulation inputs"
  - id: WR-02
    severity: warning
    disposition: open
    title: "\u0420\u044f\u0434\u043e\u043a Velxio \u0432 \u043c\u0430\u0442\u0440\u0438\u0446\u0456 \u0440\u043e\u043b\u0435\u0439 \u0441\u0443\u043f\u0435\u0440\u0435\u0447\u0438\u0442\u044c \u0432\u043b\u0430\u0441\u043d\u043e\u043c\u0443 \u0434\u043e\u043a\u0430\u0437\u043e\u0432\u043e\u043c\u0443 \u0441\u0442\u043e\u0432\u043f\u0446\u044e \u0449\u043e\u0434\u043e STM32"
  - id: WR-03
    severity: warning
    disposition: open
    title: "\u00abBooted reproducibly\u00bb / \u00abrepeatable\u00bb \u0434\u043b\u044f Velxio \u2014 \u0432\u043b\u0430\u0441\u0442\u0438\u0432\u0456\u0441\u0442\u044c, \u044f\u043a\u043e\u0457 \u043d\u0435 \u0432\u0438\u043c\u0456\u0440\u044e\u0432\u0430\u043b\u0438"
  - id: WR-04
    severity: warning
    disposition: open
    title: "\u0423 Consequences \u0432\u0435\u0440\u0445\u043d\u044f \u043c\u0435\u0436\u0430 \u043a\u0432\u043e\u0442\u0438 \u043f\u043e\u0434\u0430\u043d\u0430 \u044f\u043a \u0444\u0430\u043a\u0442\u0438\u0447\u043d\u0435 \u0441\u043f\u043e\u0436\u0438\u0432\u0430\u043d\u043d\u044f"
  - id: WR-05
    severity: warning
    disposition: open
    title: "ADR \u043f\u0440\u0438\u043f\u0438\u0441\u0443\u0454 `test_merge_firmware` \u0434\u043e\u0432\u0435\u0434\u0435\u043d\u043d\u044f \u0441\u0442\u0432\u043e\u0440\u0435\u043d\u043d\u044f merged-\u043e\u0431\u0440\u0430\u0437\u0443"
  - id: WR-06
    severity: warning
    disposition: open
    title: "`test_merge_firmware` \u043d\u0435 \u043f\u0435\u0440\u0435\u043d\u043e\u0441\u0438\u0442\u044c\u0441\u044f \u043d\u0430 Windows, \u0445\u043e\u0447\u0430 \u043f\u0435\u0440\u0435\u0432\u0456\u0440\u044f\u0454 Windows-\u0433\u0456\u043b\u043a\u0443"
  - id: IN-01
    severity: info
    disposition: open
    title: "`_quote` \u043d\u0435 \u043d\u0435\u0439\u0442\u0440\u0430\u043b\u0456\u0437\u0443\u0454 shell-\u043c\u0435\u0442\u0430\u0441\u0438\u043c\u0432\u043e\u043b\u0438, \u0430 board-\u0437\u043d\u0430\u0447\u0435\u043d\u043d\u044f \u0432\u0437\u0430\u0433\u0430\u043b\u0456 \u043d\u0435 \u0446\u0438\u0442\u0443\u044e\u0442\u044c\u0441\u044f"
  - id: IN-02
    severity: info
    disposition: open
    title: "\u041d\u0435\u043c\u0430\u0454 \u0442\u0435\u0441\u0442\u0443 \u043d\u0430 \u0441\u0430\u043c\u0443 \u0434\u0456\u044e `merge_firmware()` \u0456 \u043d\u0430 \u0448\u043b\u044f\u0445 \u043f\u043e\u043c\u0438\u043b\u043a\u0438"
  - id: IN-03
    severity: info
    disposition: open
    title: "\u0422\u0435\u0441\u0442 \u0448\u043b\u044f\u0445\u0456\u0432 Wokwi \u0442\u0438\u0445\u043e \u0441\u043a\u0456\u043f\u0430\u0454\u0442\u044c\u0441\u044f, \u0430 `scripts/tests` \u043d\u0435 \u0437\u0430\u043f\u0443\u0441\u043a\u0430\u0454\u0442\u044c\u0441\u044f \u0432 CI"
  - id: IN-04
    severity: info
    disposition: open
    title: "\u0422\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043d\u044f \u00ab3/3\u00bb \u043d\u0435 \u043d\u0435\u0441\u0435 \u0437\u0430\u0441\u0442\u0435\u0440\u0435\u0436\u0435\u043d\u043d\u044f \u043f\u0440\u043e \u0432\u0456\u0434\u0441\u0443\u0442\u043d\u0456 serial-log \u0444\u0430\u0439\u043b\u0438 \u0437\u0430\u043f\u0443\u0441\u043a\u0456\u0432 2-3"
  - id: IN-05
    severity: info
    disposition: open
    title: "\u041a\u043e\u043c\u0435\u043d\u0442\u0430\u0440 \u0443 `pyproject.toml` \u043d\u0430\u0437\u0438\u0432\u0430\u0454 \u043d\u0435 \u0442\u043e\u0439 \u0441\u0438\u043c\u0432\u043e\u043b, \u0430 ignore \u0437\u0430\u043d\u0430\u0434\u0442\u043e \u0448\u0438\u0440\u043e\u043a\u0438\u0439"
  - id: IN-06
    severity: info
    disposition: open
    title: "ADR \u043a\u0430\u0436\u0435 \u00abreferenced by its immutable digest\u00bb, \u0430\u043b\u0435 digest \u0443 ADR \u0432\u0456\u0434\u0441\u0443\u0442\u043d\u0456\u0439"
open: 13
total: 13
recorded: 2026-10-26T16:02:24.722443Z
---

# Phase 07: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | open | - |
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| WR-06 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved.
