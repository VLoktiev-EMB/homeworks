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
| course-index | Placeholder stub for answering which homeworks exist and how to find one from the generated course index. Use only to look up the manual index-reading fallback until this skill is promoted. | `.claude/skills/course-index/SKILL.md` |
| hw-build | Builds a homework's PlatformIO target and runs its native suite, repairing a failure at most twice before escalating with the evidence. Use after a code block, before writing the report, or when a build is red. | `.claude/skills/hw-build/SKILL.md` |
| hw-flash | Uploads a built homework to its board after an explicit confirmation and captures a bounded serial log to an ignored path. Use after a green build, when the board is connected and the user wants the firmware on it. | `.claude/skills/hw-flash/SKILL.md` |
| hw-report | Placeholder for assembling a homework report from the measured evidence. Use only to look up the manual report fallback until this skill is promoted. | `.claude/skills/hw-report/SKILL.md` |
| new-homework | Scaffolds a new PlatformIO homework through the repository's only supported path, then guides the user block by block from intake to report. Use when starting a new assignment, creating a homeworks directory, or asking for the guided homework workflow. | `.claude/skills/new-homework/SKILL.md` |
| schematic | Placeholder for editing the Wokwi project diagram until this skill is promoted. Use only to look up the manual diagram-editor and lint fallback. | `.claude/skills/schematic/SKILL.md` |
| simulate | Placeholder for running the Wokwi scenario and recording its evidence. Use only to look up the manual simulation command until this skill is promoted. | `.claude/skills/simulate/SKILL.md` |
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
