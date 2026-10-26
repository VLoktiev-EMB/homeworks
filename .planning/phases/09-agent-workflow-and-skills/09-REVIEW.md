---
phase: 09-agent-workflow-and-skills
reviewed: 2026-10-26T22:38:23Z
depth: standard
files_reviewed: 49
files_reviewed_list:
  - .agents/skills/_shared/guardrails.md
  - .agents/skills/course-index/CHANGELOG.md
  - .agents/skills/course-index/LESSONS.md
  - .agents/skills/course-index/SKILL.md
  - .agents/skills/hw-flash/CHANGELOG.md
  - .agents/skills/hw-flash/LESSONS.md
  - .agents/skills/hw-flash/SKILL.md
  - .agents/skills/hw-report/CHANGELOG.md
  - .agents/skills/hw-report/LESSONS.md
  - .agents/skills/hw-report/SKILL.md
  - .agents/skills/new-homework/CHANGELOG.md
  - .agents/skills/new-homework/LESSONS.md
  - .agents/skills/schematic/CHANGELOG.md
  - .agents/skills/schematic/LESSONS.md
  - .agents/skills/schematic/SKILL.md
  - .agents/skills/simulate/CHANGELOG.md
  - .agents/skills/simulate/LESSONS.md
  - .agents/skills/simulate/SKILL.md
  - .claude/CLAUDE.md
  - .claude/skills/_shared/guardrails.md
  - .claude/skills/course-index/CHANGELOG.md
  - .claude/skills/course-index/LESSONS.md
  - .claude/skills/course-index/SKILL.md
  - .claude/skills/hw-flash/CHANGELOG.md
  - .claude/skills/hw-flash/LESSONS.md
  - .claude/skills/hw-flash/SKILL.md
  - .claude/skills/hw-report/CHANGELOG.md
  - .claude/skills/hw-report/LESSONS.md
  - .claude/skills/hw-report/SKILL.md
  - .claude/skills/new-homework/CHANGELOG.md
  - .claude/skills/new-homework/LESSONS.md
  - .claude/skills/schematic/CHANGELOG.md
  - .claude/skills/schematic/LESSONS.md
  - .claude/skills/schematic/SKILL.md
  - .claude/skills/simulate/CHANGELOG.md
  - .claude/skills/simulate/LESSONS.md
  - .claude/skills/simulate/SKILL.md
  - .gitignore
  - .pre-commit-config.yaml
  - AGENTS.md
  - docs/decisions/README.md
  - docs/standards/vscode.md
  - generated.skills.manifest
  - scripts/affected.py
  - scripts/gen_skills.py
  - scripts/tests/temp_root.py
  - scripts/tests/test_affected.py
  - scripts/tests/test_gen_skills.py
  - scripts/tests/test_tooling_config.py
findings:
  critical: 2
  warning: 8
  info: 5
  total: 15
status: issues_found
---

# Phase 09: Code Review Report

**Reviewed:** 2026-10-26T22:38:23Z
**Depth:** standard
**Files Reviewed:** 49
**Status:** issues_found

## Summary

The canonical `.claude/skills/` tree and the generated `.agents/skills/` mirror are in
sync: `python3 scripts/gen_skills.py --check` reports every record `UNCHANGED` and the
manifest bytes are identical. Cross-references from the skills to
`templates/report/report.md`, `homeworks/1_3-police-flasher/report.md`, the README
`<!-- BEGIN GENERATED: homeworks -->` / `<!-- END GENERATED -->` region,
`homeworks/<id>/assets/diagram.json`, `scenario.yaml`, `scripts/tag_homework.sh`, and
`scripts/new_homework:90` all resolve today. `wokwi-cli lint --offline` accepts both the
diagram-file and project-directory forms, so the schematic and simulate fallbacks are
valid commands.

The serious defects are concentrated in `hw-flash`: it instructs an action the shared
guardrails forbid (persisting raw device output that may contain a credential), and its
capture assumes a `monitor_speed` setting that does not exist, so on the only real
homework the monitor would use PlatformIO's 9600 default while the project documents
115200. The generator also has edge-case logic errors that the current tree does not
trigger but that would silently mis-project a future skill.

I also inspected `new-homework/SKILL.md`, `new-homework/references/*`, and `hw-build/**`
for cross-reference consistency even though they are not in the supplied `files` list
(they are listed by the in-scope `generated.skills.manifest`). The `new-homework`
findings below carry a scope note. `uv run` was blocked by the sandbox's uv-cache
permission, so the generator was exercised through `python3 scripts/gen_skills.py`; the
module is the same one the `gen-skills-check` hook runs.

## Narrative Findings (AI reviewer)

Findings are grouped by severity below; the mirror was proven in sync before the review,
so every finding is either a prose/instruction defect or a generator edge case.

## Critical Issues

### CR-01: `hw-flash` writes raw device output to a log, which the guardrails forbid

**File:** `.agents/skills/hw-flash/SKILL.md:126-147` (mirror of
`.claude/skills/hw-flash/SKILL.md:124-145`); rule at
`.agents/skills/_shared/guardrails.md:51-56`

**Issue:** The shared guardrails say, as a `[MUST]`, "Never echo a token, and never write
a credential to the state file or a log." The `hw-flash` capture section says: "Write the
raw bytes to `.skill-state/logs/<id>.log`" and then concedes "The device may print
anything, including a secret." The mitigation offered ("Never quote log content into a
report, a commit, or the conversation") governs *disclosure*, not the write, and does not
remove the credential from the log file. The guardrails also say no skill may override a
rule in that file with its own prompt wording, so the two instructions cannot both stand.
This is a security-rule violation, not a wording preference.

**Fix:** Decide the policy before shipping and make the two files agree. Either:

1. Add an explicit, scoped exception to the guardrails for an ignored, local-only capture
   with mandatory redaction, and implement the redaction/refusal in `hw-flash`; or
2. Do not persist raw output. Keep the bounded bytes in memory and write only a redacted
   or structured summary (for example, byte count plus a fixed redaction of
   credential-shaped tokens), never the raw stream.

A minimal refusal check, added before the write, looks like:

```python
CREDENTIAL = re.compile(rb"(?i)(token|secret|password|api[_-]?key)[=:]\s*\S+")
if CREDENTIAL.search(out):
    raise CaptureFailed("credential-shaped device output; refusing to write the log")
```

Update `.agents/skills/hw-flash/CHANGELOG.md` and `LESSONS.md` with the chosen rule so the
mirror does not re-introduce the violation on the next regeneration.

### CR-02: The capture baud assumption is false for the only real homework

**File:** `.agents/skills/hw-flash/SKILL.md:115-122` (mirror of
`.claude/skills/hw-flash/SKILL.md:113-120`)

**Issue:** The skill says "Never hardcode `-b 115200`. The monitor inherits
`monitor_speed` from `platformio.ini` and takes the port selection from PlatformIO."
Neither `platformio.shared.ini` nor `homeworks/1_3-police-flasher/platformio.ini`
declares `monitor_speed` (verified by grep), while the homework report records that "the
serial port is opened at 115200 baud"
(`homeworks/1_3-police-flasher/report.md:211-213`). `pio device monitor` defaults to 9600
when `monitor_speed` is absent (`pio device monitor --help`: `-b, --baud INTEGER ...
[default=9600]`). On the repository's only real project, the skill's capture therefore
produces a corrupted log and still reports "capture succeeded" because bytes were
collected. The "never hardcode" rule is sound in principle, but the project setting it
relies on does not exist.

**Fix:** Make the claim true, and make the absence explicit:

```ini
; platformio.shared.ini (or the homework's platformio.ini)
[env]
monitor_speed = 115200
```

Then have the skill stop and ask when `monitor_speed` is absent, rather than silently
accepting 9600:

```text
If the resolved environment has no monitor_speed, stop before the capture and ask for
the baud rate; do not let PlatformIO default to 9600.
```

If a project really needs a non-default rate, pass `-b <n>` only from that project value
and record it in the outcome, as the existing "user explicitly names a baud rate" rule
already says.

## Warnings

### WR-01: The capture snippet does not implement the rules stated around it

**File:** `.agents/skills/hw-flash/SKILL.md:88-108`; conflicting rules at lines 32, 76,
110-113, 126

**Issue:** Three defects in the only executable capture example:

1. **Environment flag:** The rule at line 32 says to add `-e <env>` to "both the upload and
   the monitor command" when `default_envs` is absent or names several environments. The
   snippet hardcodes
   `["pio", "device", "monitor", "-d", f"homeworks/{hw_id}", "--raw"]` and never adds
   `-e`. An agent copying the snippet violates the rule.
2. **Exit code:** The outcome rule says the capture failed when the monitor "exits non-zero
   before the bound." The snippet calls `proc.communicate(timeout=20)` and never reads
   `proc.returncode`, so a monitor that exits 1 after two seconds is indistinguishable
   from a successful 20-second timeout. It also does not catch `FileNotFoundError` from
   `Popen` when `pio` is missing, so "cannot start" produces a traceback rather than the
   documented `capture unavailable` outcome.
3. **Log write:** The snippet collects `out` and never writes it to the announced
   `.skill-state/logs/<id>.log`; the write discipline in the next section is prose only.
   An agent executing the snippet alone has no log file and no atomic replace.

**Fix:** Build the argv from the resolved environment and use the return code:

```python
argv = ["pio", "device", "monitor", "-d", f"homeworks/{hw_id}", "--raw"]
if env is not None:
    argv += ["-e", env]
try:
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
except OSError as exc:
    raise CaptureFailed(f"monitor cannot start: {exc}") from exc
timed_out = False
try:
    out, err = proc.communicate(timeout=20)
except subprocess.TimeoutExpired:
    timed_out = True
    proc.kill()
    out, err = proc.communicate()
if not timed_out and proc.returncode != 0:
    raise CaptureFailed(f"monitor exited {proc.returncode} before the bound")
write_atomically_after_component_check(out)
```

### WR-02: `gen_skills.py` adds the "explicit only" banner for `disable-model-invocation: false`

**File:** `scripts/gen_skills.py:319-325`

**Issue:** The banner is added whenever the key appears in the dropped set, without
reading its value:

```python
if "disable-model-invocation" in dropped:
    banner = f"> **Invocation:** explicit only — run `/{skill_name}`. ..."
```

The docstring's rationale is that *dropping the field* widens invocation because absence
means "the model may invoke." That rationale applies only to a true value. For
`disable-model-invocation: false`, dropping the field does not widen invocation (false is
the default), yet the mirror claims explicit-only. A probe against the real generator
confirmed it: a canonical skill with `disable-model-invocation: false` produced

```text
---
name: alpha
description: Alpha with a false invocation flag.
metadata:
  version: "0.1"
  status: active
---
<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->
> **Invocation:** explicit only — run `/alpha`. Do not invoke this skill automatically.
```

The current tree has only `true` and absent, so this is latent, but it silently inverts
the invocation policy of a future skill.

**Fix:** Parse the scalar and add the banner only for a true YAML boolean:

```python
if "disable-model-invocation" in dropped and _is_true(disable_value):
    banner = ...
```

Accept `true`, `yes`, `on`, and `1` (case-insensitive) and treat `false`/`no`/`off`/`0`
as not explicit-only. Add a regression case to `scripts/tests/test_gen_skills.py`.

### WR-03: The line-based frontmatter parser under-validates and can reject valid YAML

**File:** `scripts/gen_skills.py:246-293, 296-318`

**Issue:** The custom parser is deliberate (no YAML round-trip), but three reachable
defects follow from it:

1. **Duplicate keys are accepted and mirrored.** `_scan_blocks` emits one block per
   occurrence and `_transform_skill` appends every portable block. A probe with two
   `description:` lines produced no error; the mirror would carry both, which is invalid
   YAML for a client. The last `name` wins only for the directory check.
2. **`description` is not required.** A canonical skill without it is transformed into a
   mirror without it, even though the Agent Skills contract requires a description to be
   discoverable. The unknown-field refusal does not cover this.
3. **A legal trailing comment on `name:` is read as part of the name.**
   `_scalar` returns `alpha  # the skill name` for
   `name: alpha  # the skill name`, and the generator exits 2 with a name/directory
   mismatch. A probe confirmed the failure. The parser already preserves column-0
   comments, so rejecting this valid spelling is inconsistent.

**Fix:** Track seen top-level keys and raise `CheckError` on a duplicate; require a
non-empty `description`; and in `_scalar`, strip an unquoted ` #...` suffix before
unquoting (or reject it with a clear diagnostic). Add one test per case.

### WR-04: `new-homework` waits for exit 2 from a generator that exits 1 for a missing README

**File:** `.claude/skills/new-homework/SKILL.md:85-93` (not in the supplied `files` list;
listed by the in-scope `generated.skills.manifest` and described by the in-scope
`new-homework` changelog)

**Issue:** The skill says to skip view regeneration "only when the target root has no
authored `README.md` carrying the generated marker region and the generator exits 2."
`gen_views.py` classifies an absent region file as `ERROR` and write mode returns 1
(`scripts/gen_views.py:759-770`; `scripts/tests/test_gen_views.py:437-440` asserts exit 1
for the write mode). Exit 2 is reserved for an ambiguous marker layout or a usage error
(`scripts/gen_views.py:293-313`). An agent following the documented condition will see
exit 1 on a README-less root and treat it as an unexpected failure rather than the
documented skip.

**Fix:** State both cases explicitly:

```text
Skip the regeneration when the generator exits 1 with `README.md: ERROR` (the README is
absent) or exits 2 because the marker region is missing or ambiguous. Never create a
README to force the generator to run.
```

### WR-05: The `--dir` workflow validates the wrong root

**File:** `.claude/skills/new-homework/SKILL.md:93-105`

**Issue:** The skill promises "Resolve every `homeworks/<id>` path against the chosen
root, so a `--dir` run never reads or builds the repository's homework by accident," and
it adds `--dir <root>` to the scaffold and view commands. The final validation command is
plain `uv run scripts/check_metadata.py homeworks/<id>`, with no `--dir`. For a chosen
root, `check_metadata.py` resolves the positional path against the repository root
(`scripts/check_metadata.py:311-320`), so it validates the wrong homework or fails with a
missing path.

**Fix:**

```bash
UV_CACHE_DIR="${TMPDIR:-/tmp}/uv-cache" uv run scripts/check_metadata.py \
  --dir <root> homeworks/<id>
```

or make the positional path absolute and pass `--dir`. Add a sentence to the "For another
root" instruction that covers every command in the skill, not just the scaffold and the
view generator.

### WR-06: `AGENTS.md` describes an `affected.py` no-build-impact set that no longer exists

**File:** `AGENTS.md:67-72`; actual set at `scripts/affected.py:99-120`

**Issue:** The paragraph says the no-build-impact set is "`.planning/`, `docs/`,
`.github/`, `templates/views/`, `boards/` and the generated view files." The actual
`NO_BUILD_IMPACT` tuple also contains `.claude/`, `.agents/`, `.skill-state/`,
`generated.skills.manifest`, and `scripts/gen_skills.py` (all added for this phase). An
agent reading the rulebook would expect a skill change to widen the build matrix, when the
mapper deliberately selects nothing. The Phase 9 entries are also the ones most likely to
be tested by a reviewer.

**Fix:** Replace the parenthetical with the full set, or avoid duplicating it:

```text
an explicit no-build-impact set (see `NO_BUILD_IMPACT` in `scripts/affected.py`:
`.planning/`, `docs/`, `.github/`, `templates/views/`, `boards/`, `.claude/`,
`.agents/`, `.skill-state/`, the generated view and skill ledgers, and
`scripts/gen_skills.py`) selects nothing
```

### WR-07: `no-generated-files` does not cover the template-tree generated patterns

**File:** `.pre-commit-config.yaml:133-139`; patterns declared at `.gitignore:33-37`

**Issue:** The hook's `git ls-files -ci --exclude-standard` pathspec includes
`compile_commands.json`, `site`, `.pio`, `.skill-state`, and the three
`homeworks/*/` patterns, but it omits the equivalent
`templates/homework-*/CMakeLists.txt`, `templates/homework-*/src/CMakeLists.txt`, and
`templates/homework-*/sdkconfig.*` patterns that `.gitignore` declares. `compile_commands.json`
is covered globally, but `git add -f templates/homework-espidf/CMakeLists.txt` (or a
`sdkconfig.<env>`) would be tracked and the hook would pass, contradicting the
`AGENTS.md` rule that the hook fails when any generated file is tracked. The
`TemplateIgnoreTests` class tests only the `.gitignore` patterns, not the hook.

**Fix:** Add the three template pathspecs to the `git ls-files` arguments, and add a
`TemplateIgnoreTests` case that runs the hook's pathspec against a tracked synthetic
template output:

```yaml
entry: >-
  bash -c 'tracked=$(git ls-files -ci --exclude-standard --
  compile_commands.json site .pio .skill-state
  "homeworks/*/CMakeLists.txt"
  "homeworks/*/src/CMakeLists.txt" "homeworks/*/sdkconfig.*"
  "templates/homework-*/CMakeLists.txt"
  "templates/homework-*/src/CMakeLists.txt" "templates/homework-*/sdkconfig.*") || exit 1;
  ...'
```

### WR-08: The uv cache override falls back to a fixed shared `/tmp` path

**File:** `.claude/skills/new-homework/SKILL.md:72,83,95,98`

**Issue:** Every `uv run` in the skill uses
`UV_CACHE_DIR="${TMPDIR:-/tmp}/uv-cache"`. When `TMPDIR` is unset (common on Linux), this
is the fixed, world-writable `/tmp/uv-cache`. A local process can pre-create that path or
replace it with a symlink so the user's `uv` resolves package data through it. The repo's
own test suites invoke `uv run` without the override, so the override exists only to work
around the F-01 cache-permission issue, not as a contract.

**Fix:** Use a per-user, unpredictable cache path:

```bash
UV_CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/uv" uv run ...
```

or `mkdir -m 700 "$(mktemp -d "${TMPDIR:-/tmp}/uv-cache.XXXXXX")"` with a cleanup trap,
and never a fixed name under `/tmp`.

## Info

### IN-01: `NO_BUILD_IMPACT` is not tested entry by entry

**File:** `scripts/tests/test_affected.py:236-251`

**Issue:** The `affected.py` docstring says "`NO_BUILD_IMPACT` is explicit and tested
entry by entry." The Phase 9 entry `.skill-state/` has no case in
`NO_BUILD_IMPACT_PATHS`, so a future deletion of that entry from the tuple would not fail
a test.

**Fix:** Add `.skill-state/1_3-police-flasher.json` to `NO_BUILD_IMPACT_PATHS` and assert
the empty payload like the other entries.

### IN-02: The `no-generated-files` description omits the new state directory

**File:** `docs/standards/vscode.md:176-177`

**Issue:** The hook description lists `compile_commands.json`, `site/`, `.pio/`, and an
ESP-IDF build output inside a homework, but the hook also checks `.skill-state` (the
Phase 9 checkpoint directory). A reader of the onboarding guide will not know a tracked
checkpoint fails the gate.

**Fix:** Add `.skill-state/` to the parenthetical, and mention the template outputs if
WR-07 is fixed.

### IN-03: The simulation phase reference is stale

**File:** `docs/standards/vscode.md:148-150`

**Issue:** The guide says a no-hardware simulation path "belongs to Phase 7." Phase 7 has
delivered the Wokwi path, and Phase 9 added the `simulate` skill. The sentence is not
wrong about the editor setup, but the forward-looking phase reference no longer describes
the repository.

**Fix:** Say "Simulation is documented by the `simulate` skill and
`docs/decisions/0014-simulator-selection.md`" or drop the phase reference.

### IN-04: The generator tests do not cover the edge cases above

**File:** `scripts/tests/test_gen_skills.py:164-328`

**Issue:** `TransformTests` covers a true `disable-model-invocation` but not `false`;
`FailureTests` covers an unknown key but not a duplicate key, a missing `description`, or
a trailing comment on `name`. The current suite therefore passes while WR-02 and WR-03
are live.

**Fix:** Add one case per defect: `false` produces no banner; a duplicate `description`
exits 2; a missing `description` exits 2; `name: alpha  # comment` succeeds.

### IN-05: The `gen-skills-check` hook's `files` pattern is untested

**File:** `scripts/tests/test_tooling_config.py:1235-1318`

**Issue:** `HookLayeringTests` proves the new hook runs at `pre-commit`, but no test
asserts its `files` regex matches `.claude/skills/**`, `.agents/skills/**`, and
`generated.skills.manifest`. A future edit to the folded regex could stop the hook from
running on the exact inputs it exists to guard.

**Fix:** Add a case that extracts the `files` field from the `gen-skills-check` block and
`re.search`es it against a canonical skill path, a mirror path, `scripts/gen_skills.py`,
and the manifest, mirroring `MarkdownlintSurfaceTests`.

---

_Reviewed: 2026-10-26T22:38:23Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
