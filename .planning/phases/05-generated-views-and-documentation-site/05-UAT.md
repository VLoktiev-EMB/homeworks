---
status: testing
phase: 05-generated-views-and-documentation-site
source: [05-VERIFICATION.md]
started: 2026-10-26T00:00:00Z
updated: 2026-10-26T00:00:00Z
---

## Current Test

number: 1
name: GitHub Pages deploys the built site, and the rendered pages match the generated tree
expected: |
  The `docs` workflow's build-and-deploy job is green; the home page shows the
  six-column generated table, the Homeworks/Boards/Decisions navigation resolves,
  and a math-bearing page renders through the vendored KaTeX fonts.
awaiting: user response

## Tests

### 1. GitHub Pages deploys the built site, and the rendered pages match the generated tree
expected: |
  Set Settings -> Pages -> Build and deployment -> Source = GitHub Actions.
  Then merge the phase branch (or run the `docs` workflow via `workflow_dispatch`)
  and open https://vloktiev-emb.github.io/homeworks/.
  The `build and deploy` job is green; the home page shows the six-column generated
  table; the Homeworks/Boards/Decisions navigation resolves; a math-bearing page
  renders through the vendored KaTeX fonts.
result: [pending]

### 2. Review the 23 judgment-tier `must_haves.prohibitions` across the nine plans
expected: |
  A human confirms each must-NOT held. The named prohibitions are: no CDN assets,
  no report-body copying, no writes under `docs/decisions/`, no arbitrary pin
  selection, no matrix under-approximation, no PR write permissions, and no
  `gh-pages` publication. Mechanical checks found no violation; the plans mark
  these `verification: judgment`, which ADR-550 routes to an explicit human
  checkpoint rather than an automatic pass.
result: [pending]

## Summary

total: 2
passed: 0
issues: 0
pending: 2
skipped: 0
blocked: 0

## Gaps
