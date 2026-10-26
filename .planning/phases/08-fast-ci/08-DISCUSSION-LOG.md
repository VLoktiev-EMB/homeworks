# Phase 8: Fast CI - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-26
**Phase:** 8-Fast CI
**Areas discussed:** Pending todos, Topology & gate, Changed-only plumbing, Build vs test
per entry, Simulation policy, Meta job surface, Caching & timeouts, Branch protection

---

## Pending todos

| Option | Description | Selected |
|--------|-------------|----------|
| PR-title check | Standardize PR titles and add a machine check in CI; the squash subject is published history | ✓ |
| Expand README + SVG | Homework README and schematic content; Phase 11 | |
| Promote merge_firmware | Already executed in Phase 7 | |
| None — already resolved | The remaining matches are complete or belong elsewhere | |

**User's choice:** PR-title check.
**Notes:** The other four matches were reviewed and not folded: IntelliSense was resolved by
Phase 06.1, the ceremony trim is complete, the README/SVG work is Phase 11 content, and
`merge_firmware.py` was already promoted in Phase 7.

---

## Topology & gate

| Option | Description | Selected |
|--------|-------------|----------|
| One `ci.yml` | One PR-time workflow with `meta`, `changes`, `build`, `simulate`, `gate`; absorbs `homework.yml` and `generated-views.yml`; `docs.yml` stays main-only | ✓ |
| Keep four + add `ci.yml` | Add a fifth workflow but leave meta checks as separate required checks | |
| Four + `workflow_run` fan-in | Aggregate multiple workflows behind one gate via `workflow_run` | |

**User's choice:** One `ci.yml`.
**Notes:** A single required check is only reachable when all gated jobs share a workflow,
because `needs:` cannot cross workflow boundaries. `docs.yml` cannot join a PR gate: Pages
deployment needs the `github-pages` environment and OIDC.

| Option | Description | Selected |
|--------|-------------|----------|
| Separate `nightly.yml` | Full build + native tests for every project, no simulation, cron ~03:00 UTC; own concurrency and failure signal | ✓ |
| Schedule in `ci.yml` | One file, but shares the PR concurrency group and mixes triggers | |
| Reusable workflow | `nightly.yml` calls a reusable workflow from `ci.yml` | |

**User's choice:** Separate `nightly.yml`.
**Notes:** Nightly has a different input (all projects, no diff) and must not be cancelled by
PR concurrency.

---

## Changed-only plumbing

| Option | Description | Selected |
|--------|-------------|----------|
| `affected.py --base` | `fetch-depth: 0` plus `uv run scripts/affected.py --base origin/<base_ref>`; `origin/main` fallback on dispatch | ✓ |
| `paths-filter` + `--paths-from` | Third-party filter feeding the existing script | |
| `base.sha` + full fetch | Use `github.event.pull_request.base.sha` directly | |

**User's choice:** `affected.py --base`.
**Notes:** `affected.py` already owns the tested fanout, the explicit no-build-impact set,
and fail-safe widening; a second glob dialect would create two answers to one question.

| Option | Description | Selected |
|--------|-------------|----------|
| Skip via job `if` | `toJson(fromJson(...)) != '[]'` at job level; intentional skip is success for `gate` | ✓ |
| Synthetic noop entry | Always append a fake project so the matrix is non-empty | |
| Dedicated noop job | A separate job that runs only when the matrix is empty | |

**User's choice:** Skip via job `if`.
**Notes:** The job-level condition is evaluated before matrix materialisation, avoiding
GitHub's empty-matrix failure. No fake entry pollutes the `affected.py` contract.

---

## Build vs test per entry

| Option | Description | Selected |
|--------|-------------|----------|
| Native env convention | `env == 'native'` runs `pio test`; every other env runs `pio run` | ✓ |
| Extend `affected.py` | Add a `kind` field to the locked 05/D-22 output | |
| `test_framework` detection | Infer testability from the INI section | |

**User's choice:** Native env convention.
**Notes:** Both `platformio.ini` files already document that `native` is reached with
`pio test -e native`, never `pio run -e native`. The top-level `tests/` project needs no
special case because its only env is `native`.

| Option | Description | Selected |
|--------|-------------|----------|
| No fail-fast, cap 4 | `fail-fast: false`, `max-parallel: 4` | ✓ |
| Unbounded parallel | `fail-fast: false` with no cap | |
| Fail-fast true | First failure cancels the rest | |

**User's choice:** No fail-fast, cap 4.
**Notes:** Keeps independent failures visible while preventing a `lib/**` fanout from
occupying every runner at 30+ homeworks.

---

## Simulation policy

| Option | Description | Selected |
|--------|-------------|----------|
| Opt-in label | Run only with a maintainer-applied `simulate` label and a non-empty `simulate` array | ✓ |
| Auto for changed projects | Run whenever `affected.py` returns simulation entries | |
| Manual dispatch only | No PR simulation at all | |

**User's choice:** Opt-in label.
**Notes:** The roadmap calls simulation optional; the free Wokwi plan allows about 50 minutes
per rolling 30 days. Fork PRs cannot apply labels.

| Option | Description | Selected |
|--------|-------------|----------|
| Same-repo + step token | Job-level same-repo guard plus label; token checked at step level | ✓ |
| Label only | Rely on the label permission model | |
| Lint-only for forks | A separate token-free job for fork PRs | |

**User's choice:** Same-repo + step token.
**Notes:** Job-level `if` referencing `secrets.*` can break YAML evaluation, so the token
check lives on a step. A skipped simulation is success for `gate`.

| Option | Description | Selected |
|--------|-------------|----------|
| Logs + JSON, 7d | `serial.log`, scenario stdout, duration/quota JSON, 7-day retention | ✓ |
| Raw log, 14d | The CLI log only | |
| No artifact | Rely on the job log | |

**User's choice:** Logs + JSON, 7d.

---

## Meta job surface

| Option | Description | Selected |
|--------|-------------|----------|
| `pre-commit --all-files` | One check step plus cached hook environments keyed on the config hash | ✓ |
| Individual linters | Separate steps per tool | |
| pre-commit.ci | External service | |

**User's choice:** `pre-commit --all-files`.
**Notes:** One config remains the source of truth for local and CI. `default_stages` keeps
clang-tidy out of this command. Cache has no `restore-keys` so a near-miss cannot run
unreviewed linter versions.

| Option | Description | Selected |
|--------|-------------|----------|
| Parallel jobs | `docs-build` and `python-tests` as separate jobs feeding `gate` | ✓ |
| Inside `meta` | Both checks in the same job | |
| Python only | Site build stays main-only | |

**User's choice:** Parallel jobs.
**Notes:** Resolves WR-13 without slowing lint feedback and keeps failures attributable.

| Option | Description | Selected |
|--------|-------------|----------|
| Strict type+scope | `^(feat|fix|test|refactor|perf|docs|style|chore)\([a-z0-9._-]+\): .+$` | ✓ |
| Loose type | Any `type(scope): summary` shape | |
| Strict + scope↔branch | Also require the scope to match the branch/homework id | |

**User's choice:** Strict type+scope.
**Notes:** The check is skipped on `workflow_dispatch`, where there is no PR title.

| Option | Description | Selected |
|--------|-------------|----------|
| Host-TU only | clang-tidy over `lib/common`, `lib/port`, `lib/host` with a fresh database | ✓ |
| Close native-TU gap | Also analyse native test translation units | |
| No clang-tidy in CI | Keep it pre-push only | |

**User's choice:** Host-TU only.
**Notes:** The native test TU needs the `unity_config.h` fix; the gap stays recorded in
ADR-0013 rather than half-working in the gate.

---

## Caching & timeouts

| Option | Description | Selected |
|--------|-------------|----------|
| Packages + cache + pip | `~/.platformio/packages`, `~/.platformio/.cache`, `~/.cache/pip`; pin-derived key; no broad restore-keys | ✓ |
| Official cache only | `~/.cache/pip` and `~/.platformio/.cache` only | |
| Whole `~/.platformio` | Cache the entire PlatformIO home | |

**User's choice:** Packages + cache + pip.
**Notes:** The pins live in `platformio.shared.ini`, so the key hashes that file as well as
each `platformio.ini`. The 10 GB repository cache cap and the large ESP32 toolchain make
scope and key derivation important.

| Option | Description | Selected |
|--------|-------------|----------|
| Generous, then tighten | meta 15, docs 15, python 10, build 30, simulate 10, gate 5, nightly 90; measure and tighten later | ✓ |
| Tight from start | meta 10, build 15, simulate 5 | |
| Keep 45 everywhere | Preserve the current timeout | |

**User's choice:** Generous, then tighten.
**Notes:** F-15 records that the only measured run is the cold single-project baseline; a
tight timeout guessed up front would fail on cold runners.

---

## Branch protection

| Option | Description | Selected |
|--------|-------------|----------|
| After first green run | Owner adds `gate` as required in the GitHub UI ruleset after the first green `ci.yml` run | ✓ |
| Before first run | Add the required check before it has ever passed | |
| Script via API | Change the ruleset programmatically | |

**User's choice:** After first green run.
**Notes:** A required check must have passed within the last 7 days to be selectable. Rulesets
stay a UI artifact per `AGENTS.md`, so this is a human checkpoint.

| Option | Description | Selected |
|--------|-------------|----------|
| Test + document | `test_ci_workflows.py` asserts the literal `gate` id; `AGENTS.md` records the ruleset coupling | ✓ |
| Review only | Rely on code review | |
| Rename to `required-gate` | Use a different stable name | |

**User's choice:** Test + document.
**Notes:** GitHub matches required checks by literal name; a silent rename would leave the
check `Pending` and block every merge.

---

## Claude's Discretion

- Every job id except `gate`, the step order inside `meta`, and reuse of existing pinned
  action SHAs.
- The `gate` failure diagnostic and how it prints `toJSON(needs.*.result)`.
- The shape of the duration/quota JSON artifact.
- The nightly cron minute within ~03:00 UTC.
- Whether `docs-build` calls `check_lfs_pointers.sh` exactly as `docs.yml` does.

## Deferred Ideas

- clang-tidy over native test translation units (ADR-0013 gap).
- Merge-queue (`merge_group`) support.
- Nightly failure notifications.
- Weekly full simulation matrix.
- Programmatic ruleset changes via the GitHub API.
- A reusable workflow shared by `ci.yml` and `nightly.yml`.
- ESP-IDF compile-database completeness fallback.
