---
status: accepted
date: 2026-10-23
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# License and attribution

## Context and Problem Statement

The repository is public and mixes two kinds of material: source code that others may want
to reuse in their own projects, and course documentation and homework reports that are meant
to be read, quoted, and adapted with attribution. A single license either under-licenses the
code or misstates what the written material permits. The repository also publishes an
individual's work, so the identity attached to the copyright line becomes permanent the
moment it is committed. What licensing and attribution boundary should the repository declare?

## Decision Drivers

* Clarity for two different audiences: code consumers and readers of written material.
* Irrevocability: a published license grant cannot be withdrawn, and the no-rewrite policy
  means the copyright line cannot be corrected later.
* Minimal friction: per-file SPDX headers in thirty reports and dozens of YAML files would
  add noise to documents whose subject is embedded engineering, not licensing.
* Machine-checkability: the boundary should be verifiable by one lint run rather than by
  reading every file.

## Considered Options

* MIT for everything
* No license at all
* MIT for code, CC-BY-4.0 for documentation and homework reports

## Decision Outcome

Chosen option: "MIT for code, CC-BY-4.0 for documentation and homework reports", because it
matches what each kind of material is for — permissive reuse for code, attribution-preserving
reuse for written work — and follows the GitHub OSPO mixed-repository pattern.

The split is declared **once**, in `REUSE.toml`, as path globs: a catch-all MIT declaration
with a CC-BY-4.0 override for the documentation and report paths. There are no per-file SPDX
headers in reports or YAML. `NOTICE` carries the third-party attribution and trademark
sections, including the attribution for the MADR template this directory uses.

**Identity.** The public handle `VLoktiev-EMB` is the only identity used anywhere: the license
copyright line, `NOTICE`, the reports' author metadata, and these records. No real name and no
institution appear. This is a one-way decision — once published into history under the
no-rewrite policy, an identity cannot be removed.

### Consequences

* Good, because the boundary is one declarative artifact with two rule sets, reviewable as a
  diff.
* Good, because reports and YAML stay clean; a licensing header would be noise in a document
  about firmware.
* Good, because the split is checkable: `reuse lint` verifies that every covered file resolves
  to a declared license, and it joins CI in Phase 8.
* Bad, because a path-glob declaration can silently mis-route a new directory; the globs end
  with a catch-all and the lint run is what catches a mistake.
* Bad, because CC-BY-4.0 requires attribution, which is an obligation a reader can get wrong;
  `NOTICE` and the repository README state the expectation.

### Confirmation

`reuse lint` reports no uncovered files, and `LICENSES/MIT.txt` and
`LICENSES/CC-BY-4.0.txt` exist at the filenames REUSE requires. A sample of documentation
paths resolves to CC-BY-4.0 and a sample of code paths to MIT. The lint joins CI in Phase 8;
until then it is run locally before a release. The identity rule is confirmed by inspection:
the handle appears, no real name or institution does.

## Pros and Cons of the Options

### MIT for everything

One permissive license covering code, documentation, and reports.

* Good, because one license is the simplest possible statement.
* Neutral, because MIT is a software license being applied to prose.
* Bad, because it does not ask for attribution on written material, which is the one thing a
  course author reasonably wants when a report is reused.
* Bad, because it misdescribes the intent of the documentation.

### No license at all

Publish without a grant.

* Good, because it requires no decision and no files.
* Bad, because the default is "all rights reserved": nobody may legally reuse the code, which
  defeats the point of a public portfolio.
* Bad, because it is the hardest state to reverse cleanly, as every past contributor would
  need to be found.

### MIT for code, CC-BY-4.0 for documentation and homework reports

A per-material split declared in REUSE metadata.

* Good, because each kind of material gets the license that fits its purpose.
* Good, because it follows a documented organizational pattern rather than an improvised one.
* Neutral, because it needs one extra artifact (`REUSE.toml`) and a lint run to stay honest.
* Bad, because two licenses mean two obligations for a reader to distinguish; the README and
  `NOTICE` must state which applies where.

## More Information

**REUSE metadata substitution.** The decision was first described in terms of the legacy
`.reuse/dep5` file. DEP5 is deprecated in the REUSE specification, and `reuse-tool` 6.2.0
uses `REUSE.toml`; the two formats are mutually exclusive. The repository therefore uses
`REUSE.toml`, and this substitution is recorded here rather than silently applied.

**Boundary decision: pull-request templates stay MIT.** The files under
`.github/PULL_REQUEST_TEMPLATE/` are deliberately left on the MIT catch-all and are *not*
overridden to CC-BY-4.0. They are contribution machinery — checklists and prompts for people
submitting changes — not documentation and not a report, so the "written material is
CC-BY-4.0" rationale does not reach them. Recording the boundary prevents a later reader from
"fixing" the globs to cover them.

**Stale reference in the requirements.** `REQUIREMENTS.md` SIM-02 (Phase 7) states that the
simulation-spike result will be recorded in "ADR-0004". That reference is stale: number `0004`
is this license decision, and numbering is sequential and permanent, so the simulation
decision will take a later number — `0006` at the earliest, after the Phase 2 symlink
decision. The requirements text should be corrected when Phase 7 is planned; this record is
not renumbered.

The MIT and CC-BY-4.0 decision is one-way: the grants are irrevocable and the repository is
already public.
