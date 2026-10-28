---
name: hw-report
description: Use when authoring, structuring, or updating a homework report (report.md), filling in the 10 standard sections, or preparing for report contract validation.
metadata:
  version: "1.0"
  status: active
---

# Homework Report

Guide for authoring, structuring, and validating the 10-section engineering report (`report.md`).

## Overview

A homework report is an enduring engineering artifact understandable a year later. It follows the lean 10-section contract defined in `.agents/standards/report.md`, verifying metadata, section order, English prose, and valid measurement provenance.

## When to Use

- Authoring a new report for an assignment from `templates/report/report.md`.
- Updating measurements, electrical calculations, or architecture details in `report.md`.
- Auditing report evidence before opening a pull request.

### When NOT to Use

- For building firmware or running unit tests (use `hw-build`).
- For editing Wokwi schematics or wiring (use `schematic`).
- For creating new homework scaffolding (use `new-homework`).

## Quick Reference

| Section | Required Title | Focus & Core Content |
|---|---|---|
| **1** | `## 1. Title and Metadata` | Metadata table matching `homework.yaml` + implementation commit + wiring link |
| **2** | `## 2. Objective` | Assignment requirements and what this implementation delivers |
| **3** | `## 3. Assumptions` | Explicit engineering assumptions, impact if wrong, and validation method |
| **4** | `## 4. Theory` | Design model, calculations, electrical sizing, and known limitations |
| **5** | `## 5. Hardware and Wiring` | Circuit description, bill of materials table, and Mermaid schematic |
| **6** | `## 6. Firmware Architecture` | State machine, module roles, interfaces, non-blocking timing loop |
| **7** | `## 7. Test and Verification Strategy` | Native logic tests, hardware bench checks, simulation scenarios |
| **8** | `## 8. Measurement and Evidence Ledger` | Claims table with closed-vocabulary provenance labels |
| **9** | `## 9. Difficulties Encountered` | Surprises, hardware/tooling quirks, and engineering workarounds |
| **10** | `## 10. Conclusion and Next Steps` | Success evaluation against objectives, limitations, and future work |

## Core Contract Rules

The report follows `.agents/standards/report.md` and enforces the standard rules:

1. **Heading Sequence**: Exactly 10 section headings in ascending numerical order (`## 1.` to `## 10.`), matching the exact titles above without duplicates or omitted sections.
2. **File Integrity**: Document must be non-empty and under 256 kB.
3. **No Unresolved Placeholders**: Draft and complete reports must not contain `TODO` or `TBD`.
4. **English Language**: Text must be in English with ASCII identifiers and paths.
5. **Report Status**: Must declare status (`planned`, `draft`, `complete`, or `placeholder`). Only `placeholder` is exempt from content rules.

## Evidence Ledger Labels

Every row in Section 8 must carry an honest label from the closed vocabulary:

- `measured`: Reading obtained from a physical bench instrument (multimeter, scope, logic analyzer).
- `calculated`: Value derived from an electrical formula or theoretical model (never label calculations as measured!).
- `simulated`: Value captured from a Wokwi or simulator scenario run.
- `datasheet`: Nominal rating specified by the manufacturer's component datasheet.
- `not measured`: Explicitly unmeasured parameter with an honest engineering explanation.

## Common Mistakes & Red Flags

- **Red Flag**: Relabeling a theoretical calculation as `measured`. If it came from Ohm's law ($R = V/I$), it is `calculated`.
- **Red Flag**: Leaving unresolved `TODO` or `TBD` markers when transitioning a report to `draft` or `complete`.
- **Mistake**: Renaming section headings (e.g. changing `## 2. Objective` to `## 2. Goal`).
- **Mistake**: Omitting the implementation commit hash in Section 1.

## Workflow Reference

```bash
# Engineering standard reference
cat .agents/standards/report.md

# Starter skeleton
cat templates/report/report.md
```
