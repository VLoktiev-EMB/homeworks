@AGENTS.md

# Claude Code adapter

`AGENTS.md` is the canonical rulebook for this repository and wins on any conflict with
this file. This adapter carries Claude Code mechanics only and deliberately restates no
rule — edit `AGENTS.md` instead.

The blocks below are generator-owned. Their markers, inner text, and source attributes
are preserved verbatim; do not edit inside them.

<!-- GSD:skills-start source:skills/ -->

## Project Skills

| Skill | Description | Path |
|-------|-------------|------|
| course-index | Use when searching for available homeworks, finding an assignment by ID, board, or framework, checking homework implementation status, or inspecting course metadata. | `.claude/skills/course-index/SKILL.md` |
| hw-build | Use when compiling a homework PlatformIO target, verifying buildability after code changes, running native logic tests, or diagnosing compiler and linker errors. | `.claude/skills/hw-build/SKILL.md` |
| hw-flash | Use when firmware is successfully built, a physical target board is connected via USB, and you need to flash the microcontroller or capture serial monitor logs. | `.claude/skills/hw-flash/SKILL.md` |
| hw-report | Use when authoring, structuring, or updating a homework report (report.md), filling in the 10 standard sections, or preparing for report contract validation. | `.claude/skills/hw-report/SKILL.md` |
| new-homework | Use when starting a new homework assignment, scaffolding a fresh homework directory, or requesting the step-by-step guided homework workflow. | `.claude/skills/new-homework/SKILL.md` |
| schematic | Use when designing, editing, or formatting Wokwi diagram.json schematics, generating Mermaid circuit flowcharts for READMEs or reports, or untangling overlapping wiring. | `.claude/skills/schematic/SKILL.md` |
| simulate | Use when running Wokwi simulation scenarios headlessly, verifying circuit behavior without physical hardware, linting diagrams offline, or capturing simulated test evidence. | `.claude/skills/simulate/SKILL.md` |
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-fast` for a trivial task inline, with no subagents and no PLAN.md
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
