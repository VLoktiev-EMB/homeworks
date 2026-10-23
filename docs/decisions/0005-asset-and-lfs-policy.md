---
status: accepted
date: 2026-10-23
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# Asset and LFS policy

## Context and Problem Statement

The course produces artifacts that are not text: datasheets, mechanical models, simulation
archives, firmware images used as evidence, and logic-analyzer captures. Some are large and
not diffable; some are large and *must* be diffable; and the documentation site that publishes
these artifacts has its own delivery constraints. Choosing wrong in either direction is
expensive — a bloated history cannot be rewritten under the no-rewrite policy, and a
mis-routed asset can break the published site. Which binary assets travel through Git LFS, and
which stay ordinary Git objects?

## Decision Drivers

* Repository size and clone time must stay reasonable across thirty-plus homeworks.
* Diffability matters: text and near-text artifacts should remain reviewable in a pull request.
* The published documentation site must be able to serve every image it references.
* The rule must be declared before the first large binary arrives, not retrofitted after it is
  already in history.

## Considered Options

* Keep all binaries in normal Git
* Route everything binary through LFS
* Declare a selective, pre-declared LFS policy with a size guard

## Decision Outcome

Chosen option: "Declare a selective, pre-declared LFS policy with a size guard", because it
routes exactly the large non-diffable binaries to LFS, keeps text and site assets as ordinary
Git objects, and prevents the retrofit problem by declaring the patterns before any binary is
committed.

The LFS patterns are declared on day one in `.gitattributes` for eight extensions: `.pdf`,
`.step`, `.stl`, `.fzz`, `.zip`, `.bin`, `.elf`, and `.vcd`. A pre-commit size guard fails a
staged file above **1024 kB** that is not routed by an LFS attribute, so a large binary either
matches a declared pattern or is rejected — the threshold never has to creep upward.

**Videos are never committed.** They are linked from the reports to an external host
(YouTube or Drive) and their extensions are gitignored. **Documentation images stay ordinary
Git objects**: screenshots are optimized to a small WebP or PNG and committed normally,
because GitHub Pages cannot serve LFS content. The same applies to SVG, Markdown, YAML, and
JSON, which are text and gain nothing from LFS.

### Consequences

* Good, because history stays small and the clone remains usable; the large non-diffable
  artifacts are stored out of band.
* Good, because the rule is declared before the first binary, so no file has to be migrated
  and no history has to be rewritten.
* Good, because site images keep working: they are ordinary objects that Pages can serve.
* Bad, because LFS storage and bandwidth are finite (the free allowance is 10 GiB each), and
  downloads by readers and CI count against the owner's bandwidth; a full-matrix CI job that
  fetches LFS files is a real budget item.
* Bad, because the size guard measures the working tree and relies on the LFS attribute to
  exempt a routed file; a mis-declared path fails the hook rather than silently bloating the
  repository, which is the safer failure but still a friction point.
* Bad, because a contributor without `git-lfs` installed can create attributes that are
  inert; onboarding must state the requirement.

### Confirmation

The routing table in `.gitattributes` and the size guard in `.pre-commit-config.yaml` are
asserted by the asset-policy test added alongside them: every declared pattern resolves to the
`lfs` filter, a large unrouted file is rejected, and video extensions are ignored. A further
check confirms that a documentation image path is *not* LFS-routed, so the Pages constraint
cannot be broken silently. The LFS attribute list and its test are the machine-readable
surface for this decision.

## Pros and Cons of the Options

### Keep all binaries in normal Git

Commit every asset as an ordinary object.

* Good, because there is no extra tooling and no LFS quota to manage.
* Neutral, because Pages can serve everything that is committed.
* Bad, because a handful of PDFs and STEP files makes the repository uncloneable in practice,
  and the damage is permanent under the no-rewrite policy.
* Bad, because CI checkouts and caches grow with every artifact.

### Route everything binary through LFS

Put every non-text file in LFS.

* Good, because the routing rule is simple: binary means LFS.
* Good, because history stays small without per-extension judgement.
* Bad, because the documentation site cannot serve LFS objects, so every committed image
  would be broken on Pages.
* Bad, because it burns the LFS bandwidth allowance on small images that Git handles fine.

### Declare a selective, pre-declared LFS policy with a size guard

Eight declared extensions in LFS, a size guard, videos linked, site images in Git.

* Good, because each asset is routed by a decision that was made deliberately and is visible
  in one file.
* Good, because the size guard catches the case the pattern list missed instead of letting it
  into history.
* Good, because the Pages constraint is satisfied by design.
* Neutral, because it requires contributors to install `git-lfs`.
* Bad, because a new asset type needs a one-line policy change before it can be committed,
  which is a deliberate speed bump.

## More Information

The eight extensions and the 1024 kB threshold are fixed here; adding a pattern is an ordinary
pull request that changes both the attribute file and its test. Git LFS on GitHub Pages is the
constraint that decides the documentation-image question — Pages cannot serve LFS content at
all — and it is not expected to change. The licensing of any third-party graphic is governed by
[ADR-0004](0004-license-and-attribution.md) and by the `NOTICE` file; an asset being allowed
into LFS says nothing about its redistribution rights.
