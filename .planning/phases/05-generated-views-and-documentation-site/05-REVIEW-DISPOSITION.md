---
phase: 05
review: 05-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "Metadata reaches the published site as raw HTML — stored XSS via `title`, and unvalidated `report.path` breaks the link destination"
  - id: CR-02
    severity: critical
    disposition: fixed
    title: "The generator follows symlinked `homework.yaml` and view templates, unlike every other input it guards"
  - id: WR-01
    severity: warning
    disposition: open
    title: "`_escape_cell` does not escape backslashes, so its own escaping can be defeated"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`_nav_label` is not a YAML double-quoted-scalar encoder — a title/heading with `\\` or a newline emits an invalid `mkdocs.yml`"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "A deleted generated whole file is unrecoverable — `DELETED` blocks every run and the manifest keeps listing it"
  - id: WR-04
    severity: warning
    disposition: open
    title: "Board positionals are misclassified whenever the root spelling differs from the resolved root"
  - id: WR-05
    severity: warning
    disposition: open
    title: "The architecture gate never loads `extra_configs`, so an inherited `platform = native` is \"unset\" and produces false violations"
  - id: WR-06
    severity: warning
    disposition: open
    title: "The `check-architecture` pre-commit hook does not trigger on the shared INI reader it now depends on"
  - id: WR-07
    severity: warning
    disposition: open
    title: "The LFS-pointer guard exits 0 when it could not scan the tree"
  - id: WR-08
    severity: warning
    disposition: open
    title: "An empty `platform =` in the shared INI is reported as homework content violations instead of an environment error"
  - id: WR-09
    severity: warning
    disposition: open
    title: "`new_homework` parses `template.yaml` with `yaml.safe_load`, silently keeping the last duplicate key"
  - id: WR-10
    severity: warning
    disposition: open
    title: "A complete project with no `[env:]` section silently contributes nothing to the build matrix"
  - id: WR-11
    severity: warning
    disposition: open
    title: "`_pinout_link` validates only `|`, `<` and `>`; other Markdown-breaking characters still pass"
  - id: WR-12
    severity: warning
    disposition: open
    title: "`_write_atomic` replaces every generated file with a 0600-mode temp file"
  - id: WR-13
    severity: warning
    disposition: open
    title: "No pull request proves the site builds, and the Python test suite never runs in CI"
  - id: WR-14
    severity: warning
    disposition: open
    title: "Blocking-token detection is a raw substring match, so unrelated identifiers are flagged"
  - id: IN-01
    severity: info
    disposition: open
    title: "Dead module constants in `gen_views.py`"
  - id: IN-02
    severity: info
    disposition: open
    title: "The Core-pin reader is dead production code and the scaffold pin is a hardcoded duplicate"
  - id: IN-03
    severity: info
    disposition: open
    title: "Manifest entries with an unknown `owner` are never cleaned up"
  - id: IN-04
    severity: info
    disposition: open
    title: "A stray file listed in the manifest under another owner escapes both the orphan scan and the produced set"
  - id: IN-05
    severity: info
    disposition: open
    title: "`check_metadata` follows symlinked homework directories/documents while the rest of the tooling refuses them"
  - id: IN-06
    severity: info
    disposition: open
    title: "The scaffold hardcodes a board id without checking the profile exists"
  - id: IN-07
    severity: info
    disposition: open
    title: "`load_allowlist` ignores unknown keys in an allowlist entry"
  - id: IN-08
    severity: info
    disposition: open
    title: "`AGENTS.md` does not describe the new local gate or run the Python test suite"
open: 20
total: 24
unparsed: 24
recorded: 2026-10-26T00:00:00Z
---

# Phase 05: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | fixed | 05-REVIEW-FIX.md |
| CR-02 | critical | fixed | 05-REVIEW-FIX.md |
| WR-01 | warning | open | - |
| WR-02 | warning | fixed | 05-REVIEW-FIX.md |
| WR-03 | warning | fixed | 05-REVIEW-FIX.md |
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| WR-06 | warning | open | - |
| WR-07 | warning | open | - |
| WR-08 | warning | open | - |
| WR-09 | warning | open | - |
| WR-10 | warning | open | - |
| WR-11 | warning | open | - |
| WR-12 | warning | open | - |
| WR-13 | warning | open | - |
| WR-14 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |
| IN-07 | info | open | - |
| IN-08 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved.

`unparsed: 24` is recorded deliberately: `05-REVIEW.md` files its findings as
`#### <ID>: <title>` (four hashes), while the disposition parser matches `###`
(three). Every finding is therefore listed above from the review's own heading
list rather than from the parser's match set. The review's frontmatter counts
(2 critical, 14 warning, 8 info, 24 total) agree with the rows.
