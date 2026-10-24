# Architecture Decision Records

This directory records the irreversible and cross-cutting decisions that shape the
repository: the layout, the architecture, the Git policy, the licensing boundary, and the
asset policy. Each record follows the [MADR 4.0](https://adr.github.io/madr/) full template
([`template.md`](../../templates/adr/template.md)) and states the context, the drivers, the options considered,
the outcome, and how compliance is confirmed. Code shows what the system does; these records
explain why it does it that way.

## Numbering rules

- Numbering is **sequential on acceptance**: a new record takes the next free number.
- Numbers are **never reused**. A withdrawn decision keeps its number and changes its
  `status`; a replaced decision is marked `superseded by ADR-NNNN`.
- The next number is always **highest existing number + 1**, regardless of gaps left by
  rejected proposals.
- Records are cited by number from other documents and from pull requests, so a number is a
  permanent cross-reference.

## Status index

| Number | Title | Status | Date |
|--------|-------|--------|------|
| 0001 | Monorepo with independent PlatformIO projects | accepted | 2026-10-23 |
| 0002 | Ports and adapters, no universal hardware abstraction layer | accepted | 2026-10-23 |
| 0003 | Git policy and protected main branch | accepted | 2026-10-23 |
| 0004 | License and attribution | accepted | 2026-10-23 |
| 0005 | Asset and LFS policy | accepted | 2026-10-23 |
| 0006 | Public commit identity | accepted | 2026-10-23 |
| 0007 | Symlinked shared libraries via lib_deps and library.json | accepted | 2026-10-23 |
| 0008 | Common depends on port; ports are consumer-owned | accepted | 2026-10-24 |

Next number: **0009**.
