# Architecture Decision Records

This directory is the decision table for the repository and the archive of its deeper
records. The table is the index and the default record: a new decision is one row. An ADR
file is created only when the decision needs real argumentation — alternatives,
consequences, a long comparison — and is then linked from the `Record` column. A superseded
decision is marked in the `Status` column and the ADR is not rewritten.

The ADR bodies under this directory are historical. A path named in a record — including a
path that a superseded decision refers to — may no longer exist in the live tree.

| Date | Decision | Why | Change cost | Status | Record |
|------|----------|-----|-------------|--------|--------|
| 2026-10-23 | Monorepo with independent PlatformIO projects | per-project isolation, one CI surface, one metadata contract | high — moving a published homework path breaks tags and links | accepted | [0001](0001-monorepo-with-independent-projects.md) |
| 2026-10-23 | Ports and adapters, no universal HAL | teaches the real framework APIs; a HAL leaks | high — rewrites the shared core | accepted | [0002](0002-ports-and-adapters-no-universal-hal.md) |
| 2026-10-23 | Git policy and protected main | auditable, drift-detectable protection | low — settings can be re-declared | superseded 2026-10-25 — protection now lives in the GitHub UI and the drift check was removed | [0003](0003-git-policy-and-protected-main.md) |
| 2026-10-23 | License and attribution | two audiences, one declarative boundary | irreversible — a published grant cannot be withdrawn | superseded 2026-10-25 — one MIT licence remains and the two-licence declaration was removed | [0004](0004-license-and-attribution.md) |
| 2026-10-23 | Asset and LFS policy | size, diffability, Pages cannot serve LFS | moderate — re-routing a committed blob needs history surgery | accepted | [0005](0005-asset-and-lfs-policy.md) |
| 2026-10-23 | Public commit identity | published history is permanent | none — a naming rule | accepted | [0006](0006-public-commit-identity.md) |
| 2026-10-23 | Symlinked shared libraries via `lib_deps` and `library.json` | single-copy sources, explicit dependencies | high — every project repeats the spelling | accepted | [0007](0007-symlink-shared-libraries.md) |
| 2026-10-24 | `common` depends on `port`; ports are consumer-owned | one checkable include direction | high — reverses a prior decision | accepted | [0008](0008-common-depends-on-port.md) |
| 2026-10-24 | Homework metadata contract | one schema, five consumers | high — a field is a schema change | accepted | [0009](0009-homework-metadata-contract.md) |
| 2026-10-24 | Python dependency policy | exact pins without a global install | low — bump the pins in three places | amended 2026-10-25 — the mechanism stands but the pin-drift gate was retired | [0010](0010-python-dependency-policy.md) |
| 2026-10-25 | Squash-merge commit title and message | a reviewed body instead of concatenated subjects | low — two repository settings | superseded in mechanism 2026-10-25 — the settings live in the GitHub UI and drop-detection is gone | [0011](0011-squash-merge-commit-message.md) |
| 2026-10-25 | Ceremony trim: proportion process to frequency | recurring cost, not appearance, decides what stays | low — ceremony can be restored | accepted | — |
