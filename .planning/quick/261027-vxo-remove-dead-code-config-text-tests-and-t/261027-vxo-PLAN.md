---
phase: quick-261027-vxo
plan: "01"
type: execute
wave: 1
depends_on: []
files_modified:
  - scripts/ci/check_lfs_pointers.sh
  - scripts/review_smoke_test.sh
  - scripts/tests/test_tooling_config.py
  - scripts/tests/test_ci_workflows.py
  - .claude/skills/course-index/CHANGELOG.md
  - .claude/skills/course-index/LESSONS.md
  - .claude/skills/hw-build/CHANGELOG.md
  - .claude/skills/hw-build/LESSONS.md
  - .claude/skills/hw-flash/CHANGELOG.md
  - .claude/skills/hw-flash/LESSONS.md
  - .claude/skills/hw-report/CHANGELOG.md
  - .claude/skills/hw-report/LESSONS.md
  - .claude/skills/new-homework/CHANGELOG.md
  - .claude/skills/new-homework/LESSONS.md
  - .claude/skills/schematic/CHANGELOG.md
  - .claude/skills/schematic/LESSONS.md
  - .claude/skills/simulate/CHANGELOG.md
  - .claude/skills/simulate/LESSONS.md
  - .agents/skills/course-index/CHANGELOG.md
  - .agents/skills/course-index/LESSONS.md
  - .agents/skills/hw-build/CHANGELOG.md
  - .agents/skills/hw-build/LESSONS.md
  - .agents/skills/hw-flash/CHANGELOG.md
  - .agents/skills/hw-flash/LESSONS.md
  - .agents/skills/hw-report/CHANGELOG.md
  - .agents/skills/hw-report/LESSONS.md
  - .agents/skills/new-homework/CHANGELOG.md
  - .agents/skills/new-homework/LESSONS.md
  - .agents/skills/schematic/CHANGELOG.md
  - .agents/skills/schematic/LESSONS.md
  - .agents/skills/simulate/CHANGELOG.md
  - .agents/skills/simulate/LESSONS.md
  - .claude/skills/hw-build/SKILL.md
  - .claude/skills/hw-flash/SKILL.md
  - .claude/skills/new-homework/SKILL.md
  - .claude/skills/hw-build/references/repair-loop.md
  - .agents/skills/hw-build/SKILL.md
  - .agents/skills/hw-flash/SKILL.md
  - .agents/skills/new-homework/SKILL.md
  - .agents/skills/hw-build/references/repair-loop.md
  - generated.skills.manifest
  - AGENTS.md
autonomous: true
user_setup: []
estimate:
  tokens: 45000
  raw_tokens: 45000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "`scripts/ci/check_lfs_pointers.sh`, `scripts/review_smoke_test.sh`, `scripts/tests/test_tooling_config.py` and `scripts/tests/test_ci_workflows.py` are absent from the tracked tree, and no tracked file outside `.planning/` names any of them."
    - "`python3 -m unittest discover scripts/tests` reports `Ran 397 tests` and `OK (skipped=1)` — 522 before, minus the 86 tests in `test_tooling_config.py` and the 39 in `test_ci_workflows.py`."
    - "No `CHANGELOG.md` or `LESSONS.md` exists under `.claude/skills/` or `.agents/skills/`, and `generated.skills.manifest` lists 11 entries instead of 25."
    - "No file under `.claude/skills/`, `.agents/skills/`, `AGENTS.md` or `generated.skills.manifest` mentions a changelog or a lessons entry, so no instruction points at a deleted artifact."
    - "`templates/homework-espidf/` no longer contains `.pio` or `.cache`, while its ten tracked files are byte-identical."
    - "`uv run scripts/gen_skills.py --check`, `pre-commit run --all-files`, both PlatformIO commands, both checker scripts and the full stdlib suite are green, with every hook, pin and generator unchanged."
    - "HEAD is one atomic Conventional Commit containing exactly the planned tracked paths and no `.planning/` path."
  artifacts:
    - "scripts/tests/ (minus test_tooling_config.py and test_ci_workflows.py, with __init__.py and temp_root.py intact)"
    - ".claude/skills/ (seven skills carrying SKILL.md, optional references/ and _shared/guardrails.md)"
    - ".agents/skills/ (regenerated mirror, 11 files)"
    - "generated.skills.manifest (11 entries)"
    - "AGENTS.md (skills layout bullet without the process documents)"
    - "templates/homework-espidf/ (ten tracked files, no .pio or .cache)"
  key_links:
    - ".claude/skills/ canonical tree -> scripts/gen_skills.py -> .agents/skills/ and generated.skills.manifest: the manifest is the drift ledger, so a canonical deletion that is not followed by a generator run leaves a stale manifest and fails the `gen-skills-check` hook."
    - "deleted test_ci_workflows.py -> .github/workflows/ci.yml: the module asserted the `pull_request_target` and `permissions: read` invariants; the workflow stays byte-identical, so the coverage goes and the subject remains."
    - "deleted test_tooling_config.py -> scripts/clangd-wrapper.sh and .clang-format: the config-text assertions go, the wrapper and the formatter policy stay and remain exercised by the pre-commit and pre-push stages."
    - "templates/homework-espidf/ tracked files -> scripts/new_homework: the template stays the ESP-IDF scaffold source; only its ignored build output is removed."
---

<objective>
Remove four dead paths, the fourteen skill process documents with their prose pointers, and the ESP-IDF template's local build output, then regenerate the skills mirror.

Purpose: the maintainer confirmed on 2026-10-27 that the repository should carry only what directly affects the homework artifact. The deleted scripts guard a documentation site removed in `9d28f5d` or test the reviewers themselves; the two test modules assert configuration text rather than behavior; the skill changelogs and lessons files are process records that `SKILL.md` and `references/` do not need.

Output: 18 tracked file deletions (4 dead paths + 14 skill process documents), 14 mirror deletions produced by the generator, 9 edited files (three canonical `SKILL.md` bodies, `hw-build/references/repair-loop.md`, their four mirror copies, `generated.skills.manifest`, `AGENTS.md`), and the removal of two ignored build directories inside `templates/homework-espidf/`.

Accepted losses, recorded so no later reader mistakes them for oversights:
- Automated coverage of `scripts/clangd-wrapper.sh` behavior and of the `pull_request_target` / `permissions: read` CI invariants. Both subjects stay; review and the pre-push stage remain the gates.
- The post-run changelog/lessons ritual (`D-17`) is removed from the prose that referenced it, because leaving the instruction would recreate the deleted files on the next skill run and drift the mirror.

Explicitly not touched: `.planning/` (other than this quick-task directory), every generator and scaffold (`gen_views.py`, `gen_skills.py`, `affected.py`, `new_homework`, `templates/`, `homeworks.code-workspace`), every linter and static-analysis tool (`clang-format`, `clang-tidy`, `clangd-wrapper.sh`, `gen_clangd_db.py`, `ruff`, `yamllint`, `check_architecture.py`), every pre-commit hook and every CI job, and every surviving test module in `scripts/tests/`.
</objective>

<execution_context>
@~/.claude/gsd-core/workflows/execute-plan.md
@~/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@AGENTS.md
@.planning/todos/pending/2026-10-27-trim-non-artifact-surface.md
@.planning/notes/repo-surface-trim-2026-10-27.md
@scripts/gen_skills.py
@generated.skills.manifest
</context>

<tasks>

<task type="auto">
  <name>Task 1: Delete the two dead scripts and the two configuration-text test modules</name>
  <files>scripts/ci/check_lfs_pointers.sh, scripts/review_smoke_test.sh, scripts/tests/test_tooling_config.py, scripts/tests/test_ci_workflows.py</files>
  <read_first>
    - .planning/todos/pending/2026-10-27-trim-non-artifact-surface.md (sections D1 and D2: the four paths and the accepted coverage loss)
    - scripts/tests/ (directory listing: `__init__.py`, `temp_root.py` and the surviving modules that must remain)
  </read_first>
  <action>
    Delete exactly four tracked files with `git rm`, so each deletion is staged in the index and removed from the working tree: `scripts/ci/check_lfs_pointers.sh`, `scripts/review_smoke_test.sh`, `scripts/tests/test_tooling_config.py`, `scripts/tests/test_ci_workflows.py`.

    Delete nothing else. `scripts/tests/__init__.py`, `scripts/tests/temp_root.py`, `test_affected.py`, `test_gen_schematic.py`, `test_gen_skills.py`, `test_gen_views.py`, `test_homework_metadata.py`, `test_merge_firmware.py`, `test_new_homework.py`, `test_platformio_readers.py`, `test_report.py`, `test_serial_capture.py` and `test_simulation_paths.py` all stay. `scripts/ci/` becomes empty and disappears from git on its own; do not create a placeholder file there and do not move the deleted script anywhere else.

    Do not compensate for the deleted coverage: do not add a replacement test, do not edit `.pre-commit-config.yaml`, do not edit any `.github/workflows/*.yml` file, and do not edit `scripts/clangd-wrapper.sh`, `scripts/gen_clangd_db.py` or `.clang-format`. No tracked file outside `.planning/` references these four paths, so no reference needs repairing; the `.planning/` hits are phase history and stay untouched.

    Leave the pre-existing unstaged modification to `.planning/todos/pending/2026-10-27-trim-non-artifact-surface.md` alone. Do not stage it and do not revert it.
  </action>
  <verify>
    <automated>test ! -e scripts/ci/check_lfs_pointers.sh &amp;&amp; test ! -e scripts/review_smoke_test.sh &amp;&amp; test ! -e scripts/tests/test_tooling_config.py &amp;&amp; test ! -e scripts/tests/test_ci_workflows.py</automated>
    <automated>! git grep -nE 'check_lfs_pointers|review_smoke_test|test_tooling_config|test_ci_workflows' -- . ':!.planning'</automated>
    <automated>out=$(python3 -m unittest discover scripts/tests 2>&amp;1) &amp;&amp; printf '%s\n' "$out" | grep -qE '^Ran 397 tests$' &amp;&amp; printf '%s\n' "$out" | grep -q '^OK (skipped=1)$'</automated>
  </verify>
  <acceptance_criteria>
    - All four paths are absent from both the working tree and the index (`git ls-files` reports none of them).
    - `git grep` finds no reference outside `.planning/`.
    - The suite reports `Ran 397 tests` followed by `OK (skipped=1)` and no failure or error.
    - Every surviving test module and `scripts/tests/__init__.py` is still present.
    - No hook, workflow, checker or formatter file is modified.
  </acceptance_criteria>
  <done>The four dead paths are gone, the remaining suite is green at 397 tests, and no tracked reference outside the planning archive names them.</done>
</task>

<task type="auto">
  <name>Task 2: Delete the skill process documents, clear their prose pointers, and regenerate the mirror</name>
  <files>.claude/skills/*/CHANGELOG.md, .claude/skills/*/LESSONS.md, .claude/skills/hw-build/SKILL.md, .claude/skills/hw-flash/SKILL.md, .claude/skills/new-homework/SKILL.md, .claude/skills/hw-build/references/repair-loop.md, .agents/skills/, generated.skills.manifest, AGENTS.md</files>
  <read_first>
    - .claude/skills/hw-build/SKILL.md (the `## State and commits` sentence naming the optional changelog entry, and the `## After the run` section that closes the file)
    - .claude/skills/hw-flash/SKILL.md (the `## After the run` section: the changelog paragraph followed by the `Never commit, push…` paragraph)
    - .claude/skills/new-homework/SKILL.md (the `## After the run` section: the changelog paragraph followed by the `docs/standards/vscode.md` paragraph)
    - .claude/skills/hw-build/references/repair-loop.md (the `## What the loop remembers` paragraph naming the optional changelog or lessons entry)
    - AGENTS.md (the `.claude/skills/` bullet in the Repository layout section)
    - scripts/gen_skills.py (the orphan classifier: write mode deletes a mirror orphan only when line 1 carries the generated marker, and rewrites `generated.skills.manifest`)
  </read_first>
  <action>
    Delete the fourteen process documents with `git rm`: `CHANGELOG.md` and `LESSONS.md` in each of `.claude/skills/course-index/`, `hw-build/`, `hw-flash/`, `hw-report/`, `new-homework/`, `schematic/` and `simulate/`. Do not delete `SKILL.md`, `references/`, `_shared/guardrails.md`, or anything under `.agents/skills/` by hand.

    Then remove every prose pointer at a deleted artifact, keeping each edit to the minimum sentence.

    1. `.claude/skills/hw-build/SKILL.md`, in `## State and commits`: change "this skill records its result in the conversation and in the optional changelog entry." to "this skill records its result in the conversation." Then delete the `## After the run` heading and the whole paragraph beneath it — the one that begins "Draft a dated" and ends "without that confirmation." — which sit at the end of the file; the file must end after "…exactly the action it announced." with a single trailing newline and no trailing blank line.
    2. `.claude/skills/hw-flash/SKILL.md`: delete that same paragraph (beginning "Draft a dated", ending "without that confirmation."). Keep the `## After the run` heading, because the `Never commit, push, open a pull request or create a tag.` paragraph follows it and remains the section body.
    3. `.claude/skills/new-homework/SKILL.md`: delete that same paragraph. Keep the `## After the run` heading, because the `Point an editor question at docs/standards/vscode.md` paragraph follows it and remains the section body.
    4. `.claude/skills/hw-build/references/repair-loop.md`, in `## What the loop remembers`: change "this skill records its result only in the conversation and, after the run, in the optional changelog or lessons entry." to "this skill records its result only in the conversation."
    5. `AGENTS.md`, Repository layout: change the `.claude/skills/` bullet from "the canonical authored skills, each with `SKILL.md`, `CHANGELOG.md`, `LESSONS.md` and optional `references/`, plus `_shared/guardrails.md`" to "the canonical authored skills, each with `SKILL.md` and optional `references/`, plus `_shared/guardrails.md`", reflowing the two lines to the file's existing width.

    Do not remove any other sentence, heading, sentence-level rule, or guardrail sentence from these files, and do not touch `course-index`, `hw-report`, `schematic` or `simulate` `SKILL.md` files: none of them names the deleted documents.

    Do not edit `scripts/tests/temp_root.py` or `scripts/tests/test_gen_skills.py`. Their `CHANGELOG.md` / `LESSONS.md` fixtures build a synthetic skills tree in a temporary directory and prove the generator mirrors arbitrary files; they are unrelated to the real tree and must keep passing unchanged.

    Finally run `uv run scripts/gen_skills.py` once with cwd at the checkout root. The generator is the only writer of the mirror: it deletes the fourteen orphaned `.agents/skills/*/CHANGELOG.md` and `LESSONS.md` files (their line 1 carries the generated marker), rewrites the four mirror files whose canonical source changed (`.agents/skills/hw-build/SKILL.md`, `.agents/skills/hw-flash/SKILL.md`, `.agents/skills/new-homework/SKILL.md`, `.agents/skills/hw-build/references/repair-loop.md`), and rewrites `generated.skills.manifest` from 25 entries to 11. Do not hand-edit anything under `.agents/skills/` or the manifest.
  </action>
  <verify>
    <automated>test "$(find .claude/skills .agents/skills \( -name CHANGELOG.md -o -name LESSONS.md \) | wc -l | tr -d ' ')" = "0"</automated>
    <automated>uv run scripts/gen_skills.py --check</automated>
    <automated>python3 -c "import json; d = json.load(open('generated.skills.manifest')); assert len(d['entries']) == 11, len(d['entries'])"</automated>
    <automated>! git grep -niE 'changelog|lessons' -- .claude .agents AGENTS.md generated.skills.manifest</automated>
  </verify>
  <acceptance_criteria>
    - No `CHANGELOG.md` or `LESSONS.md` exists under either skills tree.
    - `gen_skills.py --check` exits 0 and reports every mirror file and the manifest as `UNCHANGED`.
    - `generated.skills.manifest` holds exactly 11 entries (7 `SKILL.md`, 3 reference files, `_shared/guardrails.md`).
    - No changelog or lessons mention survives under `.claude/`, `.agents/`, `AGENTS.md` or the manifest, case-insensitively.
    - `scripts/tests/temp_root.py` and `scripts/tests/test_gen_skills.py` are unmodified.
    - Only the four named canonical files and `AGENTS.md` were edited by hand.
  </acceptance_criteria>
  <done>The fourteen process documents are gone from both trees, every pointer to them is gone, and the mirror and manifest are regenerated and drift-free.</done>
</task>

<task type="auto">
  <name>Task 3: Remove the template build junk, run the full gate, and commit once</name>
  <files>templates/homework-espidf/.pio, templates/homework-espidf/.cache</files>
  <precondition>`pio`, `uv` and `pre-commit` resolve on PATH and the pinned pre-commit environments are already installed, so the gate runs without fetching hook environments.</precondition>
  <read_first>
    - .gitignore (the `.pio` and `.cache/` rules that make both directories untracked and ignored)
    - AGENTS.md (Agent quick-start: the six gate commands and the Conventional Commit rule)
    - .planning/STATE.md (the recorded sandbox limitation for `end-of-file-fixer` on `.vscode/settings.json`)
  </read_first>
  <action>
    Remove the template's local build output with `rm -rf templates/homework-espidf/.pio templates/homework-espidf/.cache`. Both are ignored and untracked, so this produces no git change. Leave every tracked file in `templates/homework-espidf/` untouched: `.clangd`, `README.md`, `assets/.gitkeep`, `homework.yaml`, `include/.gitkeep`, `platformio.ini`, `sdkconfig.defaults`, `src/main.c`, `template.yaml`, `test/test_homework/test_homework.c`. Do not delete `templates/homework-espidf/compile_commands.json`: it is ignored and untracked, but it is outside the confirmed scope of this task, so leave it for a separate decision. Do not remove the template directory and do not touch `templates/homework-arduino/` or `templates/views/`.

    Run the full gate from the checkout root, in this order, and stop on the first red result:
    1. `pio run -d homeworks/1_3-police-flasher`
    2. `pio test -d tests -e native`
    3. `python3 -m unittest discover scripts/tests` (must report `Ran 397 tests` and `OK (skipped=1)`)
    4. `python3 scripts/check_metadata.py`
    5. `python3 scripts/check_report.py`
    6. `uv run scripts/gen_skills.py --check`
    7. `pre-commit run --all-files`

    If `pre-commit run --all-files` reports `end-of-file-fixer` failing on `.vscode/settings.json` with an `Operation not permitted` error while that file is unchanged, that is the sandbox limitation recorded in `.planning/STATE.md`, not a defect in this change: re-run that single hook outside the sandbox and confirm the file is byte-identical. Any other hook failure is a real failure and must be fixed. If a hook rewrites a file, inspect the diff, re-run the affected commands, and stage the rewritten file.

    Commit exactly the planned tracked paths in one atomic commit — no `git add -A`, no `git add .`. Stage the deleted and edited paths by explicit path (or `git add -u` followed by a `git status` review), and leave `.planning/todos/pending/2026-10-27-trim-non-artifact-surface.md` out of the commit: it carried an unstaged modification before this task started and is not part of the change. Use the subject `chore(quick-261027-vxo): remove dead scripts, config-text tests, and skill process docs`. Confirm afterwards that the commit touches no `.planning/` path, that no hook, workflow, checker, formatter or generator file appears in it, and that the only remaining unstaged change is the pre-existing planning todo.
  </action>
  <verify>
    <automated>test ! -d templates/homework-espidf/.pio &amp;&amp; test ! -d templates/homework-espidf/.cache &amp;&amp; test "$(git ls-files templates/homework-espidf | wc -l | tr -d ' ')" = "10"</automated>
    <automated>pio run -d homeworks/1_3-police-flasher &gt;/dev/null &amp;&amp; pio test -d tests -e native &gt;/dev/null</automated>
    <automated>out=$(python3 -m unittest discover scripts/tests 2>&amp;1) &amp;&amp; printf '%s\n' "$out" | grep -qE '^Ran 397 tests$' &amp;&amp; printf '%s\n' "$out" | grep -q '^OK (skipped=1)$'</automated>
    <automated>python3 scripts/check_metadata.py &gt;/dev/null &amp;&amp; python3 scripts/check_report.py &gt;/dev/null &amp;&amp; uv run scripts/gen_skills.py --check &gt;/dev/null</automated>
    <automated>pre-commit run --all-files</automated>
    <automated>test "$(git log -1 --pretty=%s)" = "chore(quick-261027-vxo): remove dead scripts, config-text tests, and skill process docs" &amp;&amp; test -z "$(git show --name-only --format= HEAD | grep '^\.planning/')" &amp;&amp; test -z "$(git status --porcelain -- . ':!.planning')"</automated>
  </verify>
  <acceptance_criteria>
    - `templates/homework-espidf/` holds no `.pio` or `.cache` directory and still has its ten tracked files.
    - Both PlatformIO commands, both checker scripts, the stdlib suite at 397 tests, the mirror check and `pre-commit run --all-files` are green.
    - HEAD is one commit with the exact subject above, containing no `.planning/` path and no hook, workflow, checker, formatter or generator file.
    - The only unstaged path left is the pre-existing `.planning/todos/…` modification.
  </acceptance_criteria>
  <done>The template build junk is gone, every gate command is green, and one atomic commit carries the trim.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| working tree -> git index | Deletions are staged explicitly per path; a blanket stage would sweep the pre-existing `.planning/` modification and any unrelated file into the commit. |
| canonical `.claude/skills/` tree -> generated mirror | Only `scripts/gen_skills.py` writes `.agents/skills/` and its manifest; a hand deletion there would leave the ledger stale. |
| local build output -> tracked template | `templates/homework-espidf/` mixes ten tracked scaffold files with ignored build output; a directory-wide removal would delete the scaffold source. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-VXO-01 | Tampering | `.github/workflows/*.yml` contract coverage | medium | accept | Deleting `test_ci_workflows.py` removes the automated `pull_request_target` / `permissions: read` assertions. The workflows stay byte-identical and review remains the gate; the loss is the confirmed decision in D2 and is recorded in this plan rather than hidden. |
| T-VXO-02 | Tampering | `scripts/clangd-wrapper.sh` coverage | medium | accept | Deleting `test_tooling_config.py` removes `ClangdWrapperTests` and the format/tidy config assertions. The wrapper, `.clang-format` and the hook pins are unchanged and stay exercised by the pre-commit and pre-push stages; no replacement test is invented. |
| T-VXO-03 | Tampering | `.agents/skills/` mirror and `generated.skills.manifest` | medium | mitigate | The canonical deletions are followed by exactly one generator run, then `--check` proves the committed mirror and the 11-entry manifest match; a hand-edited mirror would leave an orphan and fail the `gen-skills-check` hook. |
| T-VXO-04 | Tampering | `templates/homework-espidf/` | low | mitigate | Only the two ignored directories are removed, and the verify step asserts the ten tracked files survive; `compile_commands.json` is deliberately left alone because it is outside the confirmed scope. |
| T-VXO-SC | Tampering | npm/pip/cargo installs | high | mitigate | No package is installed, added or upgraded; the existing pinned pre-commit environments are reused and no dependency file changes. |
</threat_model>

<verification>
- Four dead paths absent; no tracked reference outside `.planning/`.
- Stdlib suite at `Ran 397 tests` / `OK (skipped=1)`.
- No `CHANGELOG.md` or `LESSONS.md` under either skills tree; manifest at 11 entries; `gen_skills.py --check` green.
- No changelog or lessons mention under `.claude/`, `.agents/`, `AGENTS.md`, or the manifest.
- `templates/homework-espidf/` without `.pio`/`.cache` and with its ten tracked files.
- `pio run`, `pio test`, both checker scripts, the mirror check and `pre-commit run --all-files` green.
- One atomic commit, planned paths only, no `.planning/` path.
</verification>

<success_criteria>
- The repository no longer carries the four dead paths, the fourteen skill process documents, or the template's local build output.
- Nothing in the repository instructs an agent to write a changelog or lessons entry, and nothing references a deleted path.
- Every generator, scaffold, linter, hook and CI job is untouched and still green.
- The trim lands as one Conventional Commit that a reviewer can read in full.
</success_criteria>

<output>
Create `.planning/quick/261027-vxo-remove-dead-code-config-text-tests-and-t/261027-vxo-SUMMARY.md` when done.
</output>
