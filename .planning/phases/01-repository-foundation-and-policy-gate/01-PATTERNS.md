# Phase 1: Repository Foundation and Policy Gate - Pattern Map

**Mapped:** 2026-10-23
**Files analyzed:** 36 required (+1 conditional)
**Analogs found:** 3 files exist in the repo; only 1 is a strong role match

## Honest Assessment First

This repository is **deliberately near-empty**: 20 tracked files, of which 13 are
`.planning/` artifacts. There is **no Python, YAML, TOML, `.gitignore`, `.gitattributes`,
`LICENSE`, or CI file anywhere in the tracked tree** (verified: `git ls-files | grep -Ec
'\.(py|ya?ml|toml)$'` → `0`).

Therefore, for most Phase 1 files there is **no codebase analog**. Inventing one would
mislead the planner. The table below says exactly where an analog exists and where the
planner must instead use the authoritative external format reference recorded in
`01-RESEARCH.md`.

**Three real analogs exist, all git-tracked:**

| Analog | What it legitimately teaches |
|---|---|
| `scripts/review_smoke_test.sh` | Bash script shape: shebang, header comment, `set -uo pipefail`, repo-root resolution, fail-fast dependency check, temp dir, exit-code discipline. |
| `.claude/CLAUDE.md` | Markdown prose conventions (heading depth, bold-lead bullets, ~90-column wrap) **and** the six `<!-- GSD:... -->` managed blocks that the adapter rewrite must preserve. |
| `.planning/config.json` | JSON house style: 2-space indent, trailing newline, no comments. |

**Explicitly excluded as analogs:**
- `homeworks.code-workspace` — **untracked** (`git status` → `??`), and it is JSONC
  (tabs, comments possible). RESEARCH Pitfall 8 forbids validating it as JSON in Phase 1.
  It is not source and must not be pattern-mapped.
- `.planning/**` Markdown — it is GSD planning state, not a repository artifact. Its
  section/table style may be *loosely* imitated, but `AGENTS.md` and ADRs must follow
  their own external conventions, not the planning-document style.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/tag_homework.sh` | utility (shell) | request-response (`git`/`gh` calls) | `scripts/review_smoke_test.sh` | **exact** |
| `scripts/check_policy.py` | utility (python) | request-response (`gh api`) + transform | none | **none** |
| `scripts/check_pr_templates.py` | utility (python) | transform (parse + compare) | none | **none** |
| `scripts/tests/*.py` (7 files) | test | transform | none | **none** |
| `scripts/tests/fixtures/ruleset-live.json` | test fixture | data | `.planning/config.json` (JSON style only) | partial (style) |
| `policy/ruleset-main.json` | config | data | `.planning/config.json` (JSON style only) | partial (style) |
| `policy/repository.json` | config | data | `.planning/config.json` (JSON style only) | partial (style) |
| `.pre-commit-config.yaml` | config | event-driven (git hook) | none | **none** |
| `.github/workflows/security.yml` | config (CI) | event-driven | none | **none** |
| `.gitignore` | config | n/a | none | **none** |
| `.gitattributes` | config | n/a | none | **none** |
| `REUSE.toml` | config | n/a | none | **none** |
| `LICENSE` | legal text | n/a | none | **none** |
| `NOTICE` | legal text | n/a | none | **none** |
| `LICENSES/MIT.txt`, `LICENSES/CC-BY-4.0.txt` | legal text (verbatim) | n/a | none | **none** |
| `AGENTS.md` | documentation (rulebook) | n/a | `.claude/CLAUDE.md` (prose style only) | partial |
| `.claude/CLAUDE.md` (modify) | documentation (adapter) | n/a | `.claude/CLAUDE.md` (self; GSD blocks) | **exact** |
| `README.md` (modify) | documentation | n/a | `README.md` (self, 1 line) | **exact** |
| `.github/PULL_REQUEST_TEMPLATE/{homework,infra,docs}.md` | documentation (contract) | n/a | none | **none** |
| `docs/decisions/README.md` | documentation (index) | n/a | none | **none** |
| `docs/decisions/template.md` | documentation (template) | n/a | none | **none** |
| `docs/decisions/0001..0005-*.md` (5 files) | documentation (ADR) | n/a | none | **none** |
| `.gitleaks.toml` (CONDITIONAL) | config | n/a | none | **none** |

**Coverage:** 5 exact (1 script + 3 self/README-family + 1 adapter), 4 partial,
27 with no analog.

---

## Pattern Assignments

### `scripts/tag_homework.sh` (utility, request-response)

**Analog:** `scripts/review_smoke_test.sh` — the only tracked script; same role
(deterministic repo helper), same language, same exit-code contract.

**Script header and safety pattern** (lines 1-17):

```bash
#!/usr/bin/env bash
# Smoke test for the configured GSD reviewer lanes.
#
# Runs every reviewer on a tiny prompt containing a known bug and checks that
# each lane returns a non-empty review. Artifacts are written to a temp dir and
# are not committed.
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GSD_TOOLS="${GSD_TOOLS:-$HOME/.claude/gsd-core/bin/gsd-tools.cjs}"
RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/gsd-review-smoke.XXXXXX")"
PROMPT="$RUN_DIR/prompt.md"

if [ ! -f "$GSD_TOOLS" ]; then
  echo "FAIL: gsd-tools not found at $GSD_TOOLS" >&2
  exit 1
fi
```

Copy for `tag_homework.sh`: `#!/usr/bin/env bash`, a `#` header describing *what and
why*, `set -uo pipefail` (note: **not** `-e` — the analog deliberately omits it so it can
collect per-check results), `REPO_ROOT="$(git rev-parse --show-toplevel)"`, `FAIL:` /
`PASS:` message prefixes, errors to `>&2`, and an environment-variable override with a
`${VAR:-default}` default.

**Aggregate-result and exit pattern** (lines 66-92):

```bash
status=0
for name in codex-glm codex-beam antigravity; do
  ...
  if [ "$exit_code" != "0" ] || [ "$stubbed" = "true" ]; then
    echo "FAIL $name: invocation exit=$exit_code stubbed=$stubbed"
    ...
    status=1
  else
    echo "PASS $name: ..."
  fi
done

echo
echo "Artifacts: $RUN_DIR"
exit "$status"
```

`tag_homework.sh` should mirror this: accumulate failures in `status`, print one
`PASS`/`FAIL` line per precondition, and `exit "$status"` at the very end — never exit
early inside the check sequence. The D-11 preconditions (PR merged, homework exists, tag
unused, then create + push `hw/<id>`) map onto the same "run each check, then act" shape.

**Differences to note for the planner:** the analog has no `--help`, no argument
parsing, and no `usage()`; `tag_homework.sh <id>` needs both. There is no precedent for
argument parsing in this repo — write it simply and validate `<id>` against
`^[0-9]+_[0-9]+-.+$` (FOUND-02 shape) inline.

---

### `.claude/CLAUDE.md` (documentation, adapter — MODIFY)

**Analog:** itself. The file is **GSD-generated** and carries six marker-delimited
blocks. Rewriting it naively to "~30 lines" will fight the generator and will discard
blocks marked do-not-edit.

**GSD-managed block inventory** (verified line numbers in the current 772-line file):

| Marker | Lines | Disposition in Phase 1 |
|---|---|---|
| `<!-- GSD:project-start source:PROJECT.md -->` … `-end` | 1-43 | **Remove from CLAUDE.md** — content becomes the opening of `AGENTS.md`. |
| `<!-- GSD:stack-start source:research/STACK.md -->` … `-end` | 45-728 (684 lines) | **Remove from CLAUDE.md** — becomes `docs/standards/` material (publishable in Phase 5). |
| `<!-- GSD:conventions-start -->` … `-end` | 730-735 | **Remove** — superseded by the `AGENTS.md` rules section. |
| `<!-- GSD:architecture-start -->` … `-end` | 737-742 | **Remove** — superseded by `AGENTS.md` layout section. |
| `<!-- GSD:skills-start source:skills/ -->` … `-end` | 744-749 | **Keep** — generator-owned. |
| `<!-- GSD:workflow-start source:GSD defaults -->` … `-end` | 751-764 | **Keep verbatim** — this is D-06's "Claude-specific GSD block". |
| `<!-- GSD:profile-start -->` … `-end` | 766-772 | **Keep verbatim** — explicitly "do not edit manually". |

**Exact text to preserve** (lines 751-772):

```markdown
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
```

**Critical planning implication:** D-01's "~30 lines" is achievable only as: `@AGENTS.md`
import + a short Claude-specific note + the three kept blocks (~20 lines of
generator-owned content). The planner should state the resulting length as
"~30 lines of hand-written content plus generator-owned blocks", not assert a hard
line count that the GSD blocks would violate. The `test_agents_md.py` ceiling check
applies to **`AGENTS.md` (≤ 300 lines)**, not to the adapter.

---

### `README.md` (documentation — MODIFY)

**Analog:** itself; current content is exactly one line:

```markdown
# homeworks
```

That is the whole file (11 bytes). There is no existing README structure to imitate —
the planner writes D-16 content fresh. Required sections per D-16: purpose, the
MIT / CC-BY-4.0 split linking `LICENSE` and `NOTICE`, links to `AGENTS.md` and
`docs/decisions/`, and an explicit early-phase status line. Per the research's OSPO
citation, the license split must be stated "precisely in the repository's README.md" —
this is the authoritative requirement, not a codebase pattern.

**House Markdown conventions** (from `.claude/CLAUDE.md` lines 1-42, the only substantial
prose in the repo): `##` for top-level sections, `###` for subsections, **bold-lead
bullets** (`- **Language**: ...`), and prose wrapped at ~90 columns. Reuse these in
`README.md`, `AGENTS.md`, and the ADRs.

---

### `AGENTS.md` (documentation, rulebook)

**Analog:** `.claude/CLAUDE.md` for *typography only*, not structure.
**Authoritative source:** `01-RESEARCH.md` §"`AGENTS.md` — what the convention actually
requires" (lines 807-833) — the agents.md convention mandates no headings; the
recommended six-section order is given there.

**Pattern to copy — enforcement tags** (RESEARCH Pattern 2, lines 366-377):

```markdown
**[MUST]** **[ENFORCED: pre-commit]** Commits must pass gitleaks before they exist.

**[SHOULD]** **[ENFORCED: review]** Prefer one homework per pull request.
```

Vocabulary is literal and machine-matchable: `[MUST]`, `[SHOULD]`,
`[ENFORCED: pre-commit]`, `[ENFORCED: CI]`, `[ENFORCED: review]`. No `[MAY]`, no `[INFO]`.

**Section order** (RESEARCH lines 826-833): project paragraph → agent quick-start
(canonical commands) → repository layout → rules (each tagged) → routing table →
nearest-file precedence rule.

**Hard constraint:** ≤ 300 lines (D-02). Depth goes behind links to `docs/standards/`,
which does **not** exist until Phase 5 — so Phase 1 must not link to files that will 404.
Route to `docs/decisions/`, `scripts/`, and future `docs/standards/` with an explicit
"planned" marker, or omit the dead links.

---

### `policy/ruleset-main.json` and `policy/repository.json` (config, data)

**Analog:** none. `.planning/config.json` supplies *style only*: 2-space indent and a
trailing newline (both verified). It is not a schema or structure precedent.

**Authoritative content:** `01-RESEARCH.md` §Code Examples, lines 520-591 —
the ruleset writable-subset JSON and the repository settings JSON are given verbatim.
Use them as-is.

**Critical rule for the planner:** commit **only writable fields**. Do not export the
live GET response (RESEARCH Pitfall 2 and Anti-Pattern list). The committed ruleset must
contain no `id`, `node_id`, `source_type`, `source`, `created_at`, `updated_at`,
`_links`, or `current_user_can_bypass`.

---

### `scripts/check_policy.py` (utility, request-response + transform)

**Analog:** none — **there is no Python file in this repository.** Do not pretend
`review_smoke_test.sh` is a Python precedent; only its *CLI and exit-code discipline*
transfers conceptually.

**Authoritative content:** `01-RESEARCH.md` lines 734-783 (script shape), plus its
explicit design constraints:
- resolve the repo from `origin`, never hard-code `VLoktiev-EMB/homeworks`;
- `--check` is read-only (never `POST`/`PUT`/`PATCH`);
- `--apply` re-reads and re-runs the check so partial application cannot report success;
- exit `0` match / `1` drift / `2` usage or environment error;
- print a `difflib.unified_diff` of normalized objects plus one line per repo setting;
- `--apply` twice must be a no-op with no API error.

**Normalization algorithm to copy:** RESEARCH Pattern 1 (lines 344-363), the
`project(live, desired)` function and the `READ_ONLY` set. Sort rule lists by `type`,
never by index.

**Security constraints from the repo's own config** (`.planning/config.json`:
`security_enforcement: true`, `security_asvs_level: 1`): use `json.loads` only, never
eval/yaml; `subprocess.run([...])` with list args, never `shell=True`; never print a
secret value. These come from RESEARCH §Security Domain (lines 990, 1005).

---

### `scripts/check_pr_templates.py` (utility, transform)

**Analog:** none (no Python in repo).
**Authoritative content:** `01-RESEARCH.md` Pattern 3 (lines 378-405) and D-24.

**The contract this script enforces** — shared header delimiters:

```markdown
<!-- pr-header:start -->
## Pull request

- **Type:** `homework` | `infra` | `docs`
- **Phase / requirement:** `<e.g. FOUND-03, Phase 1>`
- **ADR / issue:** `<docs/decisions/0003-... or #123>`

Verification (paste run links):
- [ ] `meta` checks passed — `<link>`
- [ ] build passed — `<link>`
- [ ] native tests passed — `<link>`
- [ ] `gitleaks` passed — `<link>`
<!-- pr-header:end -->
```

The script compares **only** the byte range between the markers across the three
templates, and additionally asserts that no default `PULL_REQUEST_TEMPLATE.md` /
`pull_request_template.md` exists at the root or inside the template directory
(RESEARCH anti-pattern; GitHub would silently prefer it). Per-type DoD differs by design
(D-23) — a full-file equality check is wrong and must not be written.

---

### `.github/PULL_REQUEST_TEMPLATE/{homework,infra,docs}.md` (documentation, contract)

**Analog:** none. No `.github/` directory exists.
**Authoritative content:** D-22 (shared header fields), D-23 (per-type DoD lists),
RESEARCH Pattern 3 (header block above). Three files only; no default template.

---

### `.pre-commit-config.yaml` and `.github/workflows/security.yml` (config, event-driven)

**Analog:** none. No YAML, no `.github/`, no hook config exists.
**Authoritative content:** `01-RESEARCH.md` lines 593-656 — both files are given
complete and version-pinned. Copy them literally.

Non-obvious constraints the planner must carry over (all RESEARCH-verified):
- `minimum_pre_commit_version: '4.7.0'` — the locally installed 4.6.0 will refuse to run;
  upgrading is a Wave 0 prerequisite, not a code change.
- `default_install_hook_types: [pre-commit]` — Phase 6 adds `pre-push`; do not add it now.
- `security.yml` needs `fetch-depth: 0` and `--log-opts="--all"`; without both the scan is
  meaningless.
- Do **not** use `gitleaks/gitleaks-action` (org license key required — Pitfall 7).
- Do **not** add a `check-json` hook (Pitfall 8: the future workspace file is JSONC).

---

### `.gitignore` and `.gitattributes` (config)

**Analog:** none.
**Authoritative content:** `01-RESEARCH.md` lines 658-730, both files complete.
Copy verbatim including the D-21/D-20 category comments. The `.gitignore` must include
`.planning/research/.cache/` (RESEARCH Open Question 3) — note this is a *new* ignore for
files currently tracked; the planner must include "`git rm --cached` the six cached
research JSONs" as a step, or the ignore entry is inert.

The LFS tuple is exactly `filter=lfs diff=lfs merge=lfs -text`. The size guard coexists
with LFS because `check-added-large-files` filters LFS-tracked files first
(RESEARCH Pitfall 4) — do **not** add exclusion regexes.

---

### `LICENSE`, `NOTICE`, `LICENSES/MIT.txt`, `LICENSES/CC-BY-4.0.txt`, `REUSE.toml` (legal/config)

**Analog:** none.
**Authoritative content:** external only — the OSPO split (D-13: MIT code, CC-BY-4.0
docs), D-14 (public handle only, e.g. `VLoktiev-EMB`; no real name, no institution),
D-15, and REUSE 3.3.

**Substitution the planner must adopt:** D-15 says `.reuse/dep5`; RESEARCH Open
Question 1 and the REUSE 3.3 spec say DEP5 is **deprecated** and `reuse-tool` 6.2.0 uses
`REUSE.toml`. Use `REUSE.toml`, record the substitution in ADR-0004's
`## More Information`, and treat the two formats as mutually exclusive (never ship both).
`LICENSES/MIT.txt` and `LICENSES/CC-BY-4.0.txt` are required filenames by REUSE 3.3.

REUSE covers **all** project files, so `REUSE.toml` globs must end with a catch-all
covering `.planning/**`, `scripts/**`, and `policy/*.json` (RESEARCH Pitfall 6).

---

### `docs/decisions/` — `README.md`, `template.md`, `0001`-`0005` (documentation, ADR)

**Analog:** none. No `docs/` tree exists.
**Authoritative content:** `01-RESEARCH.md` lines 785-805 — the exact MADR 4.0 section
order, verified verbatim from `adr/madr` template at release 4.0.0:

frontmatter (`status`, `date`, `decision-makers`, `consulted`, `informed`) →
`# {title}` → `## Context and Problem Statement` → `## Decision Drivers` →
`## Considered Options` → `## Decision Outcome` (body starts
`Chosen option: "{title}", because …`) → `### Consequences` → `### Confirmation` →
`## Pros and Cons of the Options` (one `###` per option; bullets labelled
`Good, because …`, `Neutral, because …`, `Bad, because …`) → `## More Information`.

**Two things the planner must encode:**
1. ADR numbers are **sequential and permanent** (D-27). Phase 1 ships exactly `0001`
   through `0005` in the D-25 assignments; Phase 2's symlink decision is `0006`.
2. `docs/decisions/README.md` is the status index and must agree with each ADR's
   frontmatter `status` — this is what `test_adrs.py` checks.
3. RESEARCH Open Question 2: `REQUIREMENTS.md` SIM-02 refers to "ADR-0004" for the
   simulation spike; that reference is stale. Add the note in ADR-0004's
   `## More Information`; do not renumber.

---

### `scripts/tests/*` (test, transform) and `scripts/tests/fixtures/ruleset-live.json`

**Analog:** none. There is no test directory, no `pytest`, and no `unittest` usage.
**Authoritative content:** `.planning/phases/01-repository-foundation-and-policy-gate/
01-VALIDATION.md` §Test Infrastructure and §Wave 0 Requirements.

Conventions to follow, all from `01-VALIDATION.md`:
- Framework is **stdlib `unittest`** — no pytest (Phase 6 scope). Do not add a test
  dependency.
- Quick run: `python3 -m unittest discover -s scripts/tests -v`.
- `scripts/tests/__init__.py` is required so `python3 -m unittest scripts.tests.X` works
  (the validation table invokes tests both ways — keep both forms passing by making the
  directory a package).
- Tests must be **offline**: `test_check_policy.py` runs against
  `scripts/tests/fixtures/ruleset-live.json`, never the network. `test_check_pr_templates.py`
  reads the real template files (repository-controlled, no network).
- Fixture JSON follows the `.planning/config.json` JSON style (2-space, trailing newline).

Required test files and what each asserts (from 01-VALIDATION.md lines 55-64 and the
RESEARCH test map):

| File | Asserts |
|---|---|
| `test_check_policy.py` | normalization projects to declared keys; rule list sorted by `type`; drift → exit 1 |
| `test_check_pr_templates.py` | header byte-range identical across three templates; no default template; per-type DoD present |
| `test_tag_homework.py` | refuses an already-existing `hw/<id>` tag |
| `test_agents_md.py` | `AGENTS.md` exists, ≤ 300 lines, contains `[MUST]`/`[SHOULD]`/`[ENFORCED:` tokens; adapter imports `@AGENTS.md` |
| `test_adrs.py` | frontmatter keys, sequential numbering `0001`-`0005`, index agrees |
| `test_gitignore.py` | `.pio/`, `.env`, `compile_commands.json`, `site/`, `.planning/research/.cache/` present |
| `test_license_hygiene.py` | copyright lines contain the public handle only; no real name or institution |

---

## Shared Patterns

### Exit-code and output discipline
**Source:** `scripts/review_smoke_test.sh` lines 37-92 (tracked).
**Apply to:** `scripts/tag_homework.sh` (direct), and conceptually to both Python scripts.
One `PASS`/`FAIL` line per check, human-readable artifact paths, `>&2` for errors,
single `exit "$status"` at the end. Reserved exit codes for `check_policy.py`: `0` / `1`
/ `2` (RESEARCH lines 779-781) — Phase 8 CI keys off these, so they are a contract.

### Repo-root resolution
**Source:** `scripts/review_smoke_test.sh` line 9.
**Apply to:** every script that touches repository files.
```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
```

### Documentation typography
**Source:** `.claude/CLAUDE.md` lines 1-42 (tracked).
**Apply to:** `README.md`, `AGENTS.md`, all ADRs, all PR templates.
`##`/`###` heading hierarchy, bold-lead bullets, ~90-column prose wrap, fenced code
blocks with a language tag. Tables for structured lists (the research and validation
files use the same style consistently).

### Machine-matchable tokens
**Source:** D-03 via RESEARCH Pattern 2.
**Apply to:** `AGENTS.md` and any future checker.
Literal `[MUST]`, `[SHOULD]`, `[ENFORCED: pre-commit]`, `[ENFORCED: CI]`,
`[ENFORCED: review]`. The same discipline applies to the PR-header markers
(`<!-- pr-header:start -->` / `<!-- pr-header:end -->`) — no variants, no whitespace
drift.

### Secret-hygiene discipline
**Source:** RESEARCH §Security Domain.
**Apply to:** every script and the CI workflow.
`--redact` on every gitleaks invocation; never echo a detected value; never add
`GITHUB_TOKEN` to a hook; `json.loads` only.

---

## No Analog Found

The planner should use the cited `01-RESEARCH.md` section instead of hunting for a
codebase precedent for any of these:

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `AGENTS.md` | documentation | n/a | Rulebook convention is external (agents.md); only typography transfers from `.claude/CLAUDE.md`. |
| `.gitignore` | config | n/a | No ignore file exists anywhere in the repo or history. |
| `.gitattributes` | config | n/a | No LFS or attribute file exists. |
| `.pre-commit-config.yaml` | config (hook) | event-driven | No YAML or hook configuration exists; `pre-commit` is not yet installed at the pinned version. |
| `.github/workflows/security.yml` | config (CI) | event-driven | No `.github/` tree, no workflow, no prior CI in history. |
| `LICENSE`, `NOTICE`, `LICENSES/*` | legal text | n/a | No license metadata exists; `license: null` on the live repo. |
| `REUSE.toml` | config | n/a | REUSE tooling not installed; format is external-only. |
| `policy/*.json` | config | data | No policy-as-code exists; `.planning/config.json` is a style reference only. |
| `scripts/*.py` | utility | transform / request-response | **Zero Python files in the repository.** |
| `scripts/tests/**` | test | transform | No test framework, directory, or fixture exists. |
| `.github/PULL_REQUEST_TEMPLATE/*.md` | documentation | n/a | No PR template has ever existed here. |
| `docs/decisions/**` | documentation | n/a | No `docs/` tree exists. |
| `.gitleaks.toml` (conditional) | config | n/a | D-17: create **only** for a verified false positive, with the allowlist entry reviewed in a PR. Default state is absent. |

---

## Metadata

**Analog search scope:** repository root, `scripts/`, `.claude/`, `.planning/`, and full
`git ls-files` + `git log` history (20 tracked files, 17 commits).
**Files scanned:** 5 read in full or targeted (`scripts/review_smoke_test.sh`,
`.claude/CLAUDE.md` header + tail, `.planning/config.json`, `README.md`,
`homeworks.code-workspace`), plus the phase artifacts.
**Tracked-source check:** every named analog verified with `git ls-files --error-unmatch`
— `scripts/review_smoke_test.sh`, `.claude/CLAUDE.md`, `README.md` are tracked.
`homeworks.code-workspace` is untracked and excluded. No `.gsd/capabilities/` mirror
exists in this repository.
**Pattern extraction date:** 2026-10-23
