---
phase: "10"
slug: "report-and-evidence-system"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-27"
---

# Phase 10 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `homework.yaml` -> checker | Metadata fields (`report.path`, `report.status`) are untrusted strings controlling filesystem access | YAML mapping |
| `task.md` -> checker | Frontmatter parsed by `StrictBaseLoader`; nested structures must not crash loader | YAML frontmatter |
| `report.md` -> filesystem | Markdown report read by `read_regular_text`; must not follow symlinks or exceed 1 MB | File bytes |
| `assets/diagram.json` -> checker | Wokwi JSON read and parsed; must not follow symlinks or crash JSON parser | JSON data |
| `report.md` links -> `resolve_artifact` | Relative artifact links resolved against directory tree; must not escape root | Path tokens |
| Pre-commit hook -> environment | Hook configuration in `.pre-commit-config.yaml` runs in developer and CI environments | Python hook entry |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-10-01 | Tampering / Info Disclosure | `scripts/check_report.py` report read | high | mitigate | `read_regular_text` refuses symlinks and opens with `O_NOFOLLOW`; `RPT-002` reports without reading | closed |
| T-10-02 | Denial of Service | `scripts/report/contract.py` size gate | medium | mitigate | `REPORT_MAX_BYTES = 1024 * 1024` checked before parsing; raises `RPT-004` | closed |
| T-10-03 | Tampering | positional path resolution | medium | mitigate | `resolve_root`/`relative_path` only; non-directories exit 2; reports repo-relative paths | closed |
| T-10-04 | Tampering | `homework.yaml` load | medium | mitigate | `StrictSafeLoader` rejects duplicate keys before gate reads `report.status` | closed |
| T-10-05 | Tampering | `assets/diagram.json` read | medium | mitigate | Read through `read_regular_text` and bound by 1 MB size gate | closed |
| T-10-06 | Tampering | BOM `Ref` comparison | low | accept | Value compared directly, never used as path; normalization exact | closed |
| T-10-07 | Tampering / Info Disclosure | `resolve_artifact` | high | mitigate | Absolute tokens refused; lexical and realpath containment enforced | closed |
| T-10-08 | Information Disclosure | artifact existence check | medium | mitigate | Only `Path.exists()` called; no file opened or directory listing echoed | closed |
| T-10-09 | Tampering | ledger commit cell | low | mitigate | Hex-shape and equality verified; never executed | closed |
| T-10-10 | Denial of Service | reference/id scans | low | mitigate | Single linear pass over parsed structure; no backtracking regex | closed |
| T-10-11 | Tampering / Info Disclosure | `RPT-404` link targets | high | mitigate | External schemes skipped without I/O; relative targets contained | closed |
| T-10-12 | Tampering | `homework.yaml` duplicate keys | medium | mitigate | `StrictSafeLoader` used at load site in `scripts/check_report.py` | closed |
| T-10-13 | Spoofing | `RPT-402`/`RPT-403` identity | low | mitigate | Comparison against normalized metadata values, never display prose | closed |
| T-10-14 | Repudiation | `RPT-407`/`RPT-408` claims | low | accept | Proves claim token exists; semantic truth verified by review (D-14) | closed |
| T-10-15 | Tampering | `_candidates` report template | medium | mitigate | `is_symlink()` and `is_file()` refusal; duplicate-target check | closed |
| T-10-16 | Tampering | `scripts/metadata/render.py` | low | mitigate | Closed six-key map; unknown tokens cause exit 2 | closed |
| T-10-17 | Tampering | template↔checker drift | medium | mitigate | `TemplateParityTests` fails on any single-literal drift | closed |
| T-10-18 | Repudiation | `### Next Steps` and traceability | medium | mitigate | Restates only items from `Status:` paragraph; tokens resolve | closed |
| T-10-19 | Tampering | evidence relabelling | medium | mitigate | Ledger, calculation, and commit values preserved; validated by rules | closed |
| T-10-20 | Tampering | checklist standard drift | low | mitigate | Checklist derived from rule registry; tested by contract tests | closed |
| T-10-21 | Repudiation | self-audit honesty | low | accept | Machine gate proves structure; honest claim remains review responsibility | closed |
| T-10-22 | Tampering | calculation catalog accuracy | low | accept | Formulas and units catalogued; values verified in peer review | closed |
| T-10-23 | Tampering | `check-report` hook | high | mitigate | `pass_filenames: false`, check-only command; hook-shape test | closed |
| T-10-24 | Supply Chain | hook dependencies | high | mitigate | Exactly `["PyYAML==6.0.3"]`, already pinned; no new dependencies | closed |
| T-10-25 | Tampering | `AGENTS.md` / PR template drift | low | mitigate | Rule-id set test keeps standard in sync across repo | closed |
| T-10-26 | Tampering | `.agents/skills/` mirror | medium | mitigate | Generated by `gen_skills.py`; `gen-skills-check` drift gate | closed |
| T-10-27 | Tampering | `scripts/report/contract.py` diagram parse | medium | mitigate | `json.loads` inside `try`, shape-checked for `parts` list | closed |
| T-10-28 | Denial of Service | `StrictSafeLoader` depth limit | high | mitigate | Bound depth to 64; raises `ComposerError`; emits `RPT-001` (CR-01) | closed |
| T-10-29 | Denial of Service | `parse_diagram` recursion | high | mitigate | Catches `(ValueError, RecursionError)`; returns `Diagram(error=...)` (CR-02) | closed |
| T-10-30 | Tampering / Info Disclosure | `report.path` traversal | high | mitigate | Rejects absolute/`..`; lexical and parent realpath containment (CR-03) | closed |
| T-10-31 | Tampering | intermediate symlink walk | high | mitigate | Walks parent components with `os.lstat`, refusing symlinks (CR-03) | closed |
| T-10-32 | Denial of Service | `report.path` unrepresentable chars | high | mitigate | Refuses NUL and surrogates before filesystem access (CR-04, WR-14) | closed |
| T-10-33 | Denial of Service | `StrictBaseLoader` depth limit | high | mitigate | `DepthBoundedLoaderMixin` applied to `StrictBaseLoader` (CR-05) | closed |
| T-10-34 | DoS / Info Disclosure | `_contained_report_path` walk | medium | mitigate | Catches `(OSError, ValueError)` safely; emits `RPT-001` (WR-11) | closed |
| T-10-35 | Info Disclosure / Tampering | metadata symlink refusal | high | mitigate | Refuses symlinked `homework.yaml` and `task.md` with `is_symlink()` (CR-06) | closed |
| T-10-36 | Info Disclosure / Tampering | diagram assets directory symlink | high | mitigate | Checks `assets/` with `os.lstat` before reading `diagram.json` (WR-12) | closed |
| T-10-37 | Tampering | `read_regular_text` TOCTOU | medium | mitigate | Opens with `O_NOFOLLOW` and verifies via `fstat(fd)` (WR-13) | closed |
| T-10-SC | Supply Chain | package dependencies | low | accept | Standard library only; no new packages added | closed |

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-10-01 | T-10-06 | BOM reference designator comparison is string-only; no filesystem operations | Phase 10 Plan | 2026-10-27 |
| R-10-02 | T-10-14 | Claim existence is machine-checked; claim truth is review-enforced (D-14) | Phase 10 Plan | 2026-10-27 |
| R-10-03 | T-10-21 | Self-audit structure verified by machine; veracity remains human review duty | Phase 10 Plan | 2026-10-27 |
| R-10-04 | T-10-22 | Electrical calculations catalog formulas verified against domain physics | Phase 10 Plan | 2026-10-27 |
| R-10-05 | T-10-SC | Only pinned stdlib and pre-approved PyYAML used | Phase 10 Plan | 2026-10-27 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-27 | 38 | 38 | 0 | GSD Security Auditor (Plan-time STRIDE + Gap Closure) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-27
