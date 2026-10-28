---
name: course-index
description: Use when searching for available homeworks, finding an assignment by ID, board, or framework, checking homework implementation status, or inspecting course metadata.
metadata:
  version: "1.0"
  status: active
---

# Course Index

Query, discover, and inspect homework assignments across the monorepo.

## Overview

The course index is the authoritative registry of all PlatformIO homework projects. It answers which homeworks exist, their target boards, frameworks, and implementation statuses directly from the generated index in `README.md` and project metadata.

## When to Use

- Looking up which homework assignments currently exist.
- Finding an assignment by its numerical prefix (e.g. `1_3`), slug, or title.
- Checking which board profile or framework an assignment targets.
- Checking homework completion status (`planned`, `in-progress`, `completed`).

### When NOT to Use

- For creating a new homework (use `new-homework`).
- For compiling or flashing firmware (use `hw-build` or `hw-flash`).

## Quick Reference

| Discovery Task | Command or Source of Truth |
|---|---|
| View complete course table | Inspect `README.md` under `## Homeworks` |
| Validate all homework metadata | `uv run scripts/check_metadata.py` |
| View single project config | `cat homeworks/<id>/homework.yaml` |
| Inspect available boards | `ls boards/` or `cat boards/<board>.yaml` |

## Discovery Rules

1. **Single Source of Truth**: The table in `README.md` is the index of every `homework.yaml`. Always read `README.md` to answer which homeworks exist.
2. **Deterministic Identifiers**: Every homework ID matches `^[0-9]+_[0-9]+-[a-z0-9-]+$` (e.g. `1_3-police-flasher`). The prefix represents `module_lesson`.
3. **Board Profiles**: Target boards map to validated definitions in `boards/<board>.yaml` (e.g. `boards/esp32-s3-devkitc-1.yaml`).

## Common Mistakes & Red Flags

- **Mistake**: Inventing custom homework ID formats (e.g. `hw3`, `lab-01`) instead of the standardized `module_lesson-slug` pattern.
