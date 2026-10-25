---
phase: quick-261025-vih
plan: "01"
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/phases/04.2-tracer-homework-1-3/04.2-VALIDATION.md
  - .planning/STATE.md
  - homeworks/1_3-police-flasher/report.md
  - .planning/phases/04.2-tracer-homework-1-3/04.2-SECURITY.md
autonomous: true
user_setup: []
estimate:
  tokens: 14000
  raw_tokens: 14000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "The 04.2-VALIDATION.md META-02 row records the owner's 2026-10-25 D-09 confirmation, and no cell of that row still says the confirmation is pending."
    - "STATE.md keeps the historical 'originality review pending' bullet verbatim, adds a later bullet that closes D-09 and names it as superseding the earlier note, and adds a second bullet that records the PR-body count decision."
    - "The report's section 7 serial observation and assumption A-05 state that the firmware has no transition logging and only the two handshake events; no report sentence claims that mode or speed transitions are reported over the serial port."
    - "04.2-SECURITY.md names `9e1238d` in T-4.2-15, records the `WOKWI_CLI_TOKEN=dummy` placeholder with no real credential in T-4.2-10, and leaves all 25 threats closed with unchanged dispositions."
    - "04.2-PR-BODY.md is byte-identical to HEAD; the decision to leave it is recorded in STATE.md and names the friction log's 19 entries as the canonical count."
    - "The final gate is green: `pre-commit run --all-files`, the metadata checker, and the 38-case homework native suite pass, and no checker, hook, workflow, firmware source, schema, or ledger value was changed."
  artifacts:
    - ".planning/phases/04.2-tracer-homework-1-3/04.2-VALIDATION.md"
    - ".planning/STATE.md"
    - "homeworks/1_3-police-flasher/report.md"
    - ".planning/phases/04.2-tracer-homework-1-3/04.2-SECURITY.md"
  key_links:
    - "04.2-VALIDATION.md META-02 row -> .planning/phases/04-metadata-contract-and-scaffolding/04-UAT.md: the same confirmed result and the same 2026-10-25 date."
    - "STATE.md new decision bullet -> 04-UAT.md: the same result, owner, and date, with the historical pending entry retained as the superseded record."
    - "report.md section 7 -> homeworks/1_3-police-flasher/src/main.cpp: the described serial surface matches the two `port_log_write` calls and their two literals."
    - "04.2-SECURITY.md T-4.2-15 -> report.md metadata table and ledger: the same implementation commit `9e1238d`."
---

<objective>
Close the six residual findings in `04.2-VERIFICATION.md` so the phase verdict can be re-verified at 96/96 without touching firmware, tests, CI, or checkers.

Purpose: the verifier scored 95/96 because two live tracked records still described the D-09 paraphrase review as pending, the report's section 7 still claimed a serial transition log the firmware cannot emit, and three security/PR records had drifted from the current tree. This is a documentation-reconciliation change, not a feature.

Output: a confirmed META-02 validation row, an appended STATE.md decision pair, a corrected report serial observation plus the matching A-05 validation method, and accurate T-4.2-10 / T-4.2-15 texts — with `04.2-PR-BODY.md` deliberately untouched.

Decision already made for finding 6 — do not improvise it: the tracked `04.2-PR-BODY.md` stays byte-identical to HEAD. Plan 04.2-11 forbids editing the tracked body after PR #10 opened, and editing the live PR description is an outward-facing owner action that the orchestrator must confirm separately. The friction log is the canonical entry count and now holds 19 entries; the submitted body's "18" is a historical snapshot. STATE.md records this decision, including that any future correction would update the tracked file and PR #10 together in one owner-approved action.

Scope note: API-coverage, assumption-delta, and schema-push planner contributions do not apply. No external API is integrated, no schema or migration exists, and no package is installed.
</objective>

<execution_context>
@~/.claude/gsd-core/workflows/execute-plan.md
@~/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@AGENTS.md
@.claude/CLAUDE.md
@.planning/phases/04.2-tracer-homework-1-3/04.2-VERIFICATION.md
@.planning/phases/04.2-tracer-homework-1-3/04.2-VALIDATION.md
@.planning/phases/04.2-tracer-homework-1-3/04.2-SECURITY.md
@.planning/phases/04.2-tracer-homework-1-3/04.2-PR-BODY.md
@.planning/phases/04.2-tracer-homework-1-3/04.2-11-PLAN.md
@.planning/phases/04-metadata-contract-and-scaffolding/04-UAT.md
@homeworks/1_3-police-flasher/report.md
@homeworks/1_3-police-flasher/src/main.cpp
@homeworks/1_3-police-flasher/README.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Record the confirmed D-09 result in the validation contract and the state log</name>
  <files>.planning/phases/04.2-tracer-homework-1-3/04.2-VALIDATION.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/04.2-tracer-homework-1-3/04.2-VALIDATION.md (the META-02 row and the Approval line)
    - .planning/STATE.md (the Decisions section and line 125, the historical D-09 note)
    - .planning/phases/04-metadata-contract-and-scaffolding/04-UAT.md (the owner's confirmation wording and date)
    - .planning/phases/04.2-tracer-homework-1-3/04.2-SECURITY.md (T-4.2-02, the same result and date)
    - .planning/phases/04.2-tracer-homework-1-3/04.2-VERIFICATION.md (gap 1 and plan 04.2-10 truth 7)
    - .planning/phases/04.2-tracer-homework-1-3/04.2-PR-BODY.md (the D-09 section and the 18-count sentences)
  </read_first>
  <action>Close finding 1 in `04.2-VALIDATION.md`. In the META-02 row of the Per-Task Verification Map, replace only the final status cell `⏳ manual-only (D-09 human confirmation pending)` with `✅ confirmed by owner 2026-10-25`. Keep every other cell of that row unchanged, including the automated-command column that says `none — D-09 checklist recorded in the PR and the report's decision appendix`. In the bottom `**Approval:**` paragraph, replace the clause `PILOT-01 manual traceability review and META-02 D-09 review remain manual-only` with `the PILOT-01 manual traceability review remains manual-only, and the META-02 D-09 review was confirmed by the repository owner on 2026-10-25`. Do not change the frontmatter (`status: validated`, `nyquist_compliant: true`), the PILOT-01 row, the Manual-Only Verifications table, or the validation-audit counts.

  Close finding 2 in `.planning/STATE.md` by appending two bullets at the end of the `### Decisions` list, after the last `[Phase 04.2]` bullet (`No hw/1_3-police-flasher tag exists...`). Do not rewrite, reorder, or delete the historical bullet that says `the originality review pending; no completed user sign-off is claimed` — it stays as the record of what was true at that point. Append these two bullets verbatim as the new last entries:

  `- [Phase 04.2]: D-09 is closed — the repository owner performed the paraphrase comparison on 2026-10-25 and confirmed no verbatim sentence, no distinctive phrasing, and no original file committed. The result is recorded in 04-UAT.md, 04.2-SECURITY.md T-4.2-02, 04.2-VALIDATION.md (META-02), the PR body, and report appendix item 9 / T-13; this entry supersedes the earlier originality-review-pending note, which stays as the historical record.`

  `- [Phase 04.2]: The "18"-entry count in 04.2-PR-BODY.md stays as submitted. 04.2-FRICTION-LOG.md is the canonical count and holds 19 entries since plan 08 added F-19. The tracked body is not edited after PR #10 opened (plan 11), and no live-description edit is made here because changing PR #10 is an outward-facing owner action confirmed separately; a correction would update the tracked file and PR #10 together in one owner-approved action.`

  Do not edit the frontmatter, the Current Position block, the progress counts, the Performance Metrics, or the quick-task table. Commit only `04.2-VALIDATION.md` with the message `docs(04.2): record the confirmed D-09 paraphrase review`. Leave `.planning/STATE.md` modified and uncommitted: the quick orchestrator owns the docs commit that includes it (quick.md Step 8). Do not stage any other path.</action>
  <verify>
    <automated>python3 -c 'import pathlib; v=pathlib.Path(".planning/phases/04.2-tracer-homework-1-3/04.2-VALIDATION.md").read_text(); rows=[l for l in v.splitlines() if l.startswith("| 01-02, 04-03, 05-03, 07-02 |")]; assert len(rows)==1, rows; r=rows[0]; assert "2026-10-25" in r and "confirmed" in r.lower(); assert "confirmation pending" not in r; assert "D-09 review was confirmed by the repository owner on 2026-10-25" in v; s=pathlib.Path(".planning/STATE.md").read_text(); assert s.index("the originality review pending") < s.index("D-09 is closed"); assert "no completed user sign-off is claimed" in s; assert "entry count in 04.2-PR-BODY.md" in s and "19 entries" in s and "outward-facing" in s'</automated>
    <automated>python3 -c 'import subprocess; out=subprocess.run(["git","diff","--name-only"],capture_output=True,text=True).stdout.split(); allowed={".planning/phases/04.2-tracer-homework-1-3/04.2-VALIDATION.md",".planning/STATE.md"}; assert set(out)<=allowed, out'</automated>
  </verify>
  <acceptance_criteria>
    - The META-02 row status cell reads `✅ confirmed by owner 2026-10-25` and contains no pending wording.
    - The Approval paragraph records the owner's confirmation and keeps the PILOT-01 manual review statement.
    - STATE.md keeps the historical pending bullet verbatim and gains two later bullets: the D-09 closure and the PR-body count decision.
    - Only `04.2-VALIDATION.md` is committed by this task; STATE.md and the other target files remain uncommitted for the following tasks.
  </acceptance_criteria>
  <done>The validation contract and the state log both carry the owner's 2026-10-25 confirmation, the historical entry is intact and explicitly superseded, and the PR-body count decision is recorded without editing the submitted body.</done>
</task>

<task type="auto">
  <name>Task 2: Make the report's serial claims describe the handshake-only firmware</name>
  <files>homeworks/1_3-police-flasher/report.md</files>
  <read_first>
    - homeworks/1_3-police-flasher/report.md (section 3 assumption A-05, section 6 tail, section 7 Serial observation, L-10, line 420)
    - homeworks/1_3-police-flasher/src/main.cpp (the two `port_log_write` calls and the absence of a log port in `pattern_controller_tick`)
    - .planning/phases/04.2-tracer-homework-1-3/04.2-VERIFICATION.md (gap 2 and the section 7 anti-pattern row)
    - .planning/phases/04.2-tracer-homework-1-3/04.2-09-PLAN.md (the corrected section 6 and L-10 wording this task must match)
  </read_first>
  <action>Close finding 3 in `report.md` section 7. Replace the entire three-sentence `**Serial observation.**` paragraph (currently ending with `neither was recorded here either.`) with this two-sentence paragraph:

  `**Serial observation.** No serial log was captured in this session, and the firmware has no transition logging: `pattern_controller_tick` receives no log port, so it cannot report a mode or a speed change over the serial port. The `pattern ready` and `pattern init failed` handshake messages described in the methodology are the only serial events the firmware is designed to emit, and neither was recorded here.`

  The replacement must keep the claim negative — the firmware does not report transitions — and must agree with section 6's statement that exactly two serial events exist and that the controller performs no transition logging.

  Correct the same defect in assumption A-05, whose validation method still says `observe the mode and speed changes over the serial log`. Replace that validation cell with `Continuity test with the board unpowered; observe the button presses on GPIO7 with a logic analyzer and confirm the resulting mode and speed changes on the LEDs, because the current firmware has no serial transition log.` Change only that cell; keep the rest of the A-05 row.

  Do not change the implementation commit `9e1238d`, any ledger row, any label, the heading text, or any other paragraph. This is prose only; the firmware tree at `9e1238d` and the working tree are unchanged, so the implementation commit stays correct. Commit only `report.md` with the message `docs(1_3): correct the report serial observation`.</action>
  <verify>
    <automated>python3 -c 'import pathlib; t=pathlib.Path("homeworks/1_3-police-flasher/report.md").read_text(); p=t.split("**Serial observation.**",1)[1].split("**Bench results.**",1)[0]; assert "no transition logging" in p; assert "pattern ready" in p and "pattern init failed" in p; assert "reports through the serial port" not in p; assert "transitions that the firmware" not in p; assert "neither was recorded" in p; a=[l for l in t.splitlines() if l.startswith("| A-05 |")]; assert len(a)==1, a; assert "over the serial log" not in a[0].lower(); assert "logic analyzer" in a[0].lower(); assert "exactly two serial events" in t; assert "| Implementation commit | `9e1238d` |" in t'</automated>
    <automated>! grep -q '/Users/' homeworks/1_3-police-flasher/report.md</automated>
  </verify>
  <acceptance_criteria>
    - Section 7 states that no serial log was captured and that the firmware has no transition logging, naming only the two handshake events.
    - No sentence in section 7 claims mode or speed transitions are reported over the serial port.
    - A-05's validation method uses a logic analyzer on GPIO7 and states the absence of a serial transition log.
    - The implementation commit and every ledger value are unchanged, and the report contains no private home path.
  </acceptance_criteria>
  <done>The report's serial claims match `src/main.cpp` and section 6, with section 7 and A-05 both describing the handshake-only surface.</done>
</task>

<task type="auto">
  <name>Task 3: Correct the stale security register text and prove the submitted PR body is untouched</name>
  <files>.planning/phases/04.2-tracer-homework-1-3/04.2-SECURITY.md</files>
  <read_first>
    - .planning/phases/04.2-tracer-homework-1-3/04.2-SECURITY.md (T-4.2-10, T-4.2-15, the audit trail, the sign-off)
    - homeworks/1_3-police-flasher/report.md (metadata table and ledger commit `9e1238d`)
    - homeworks/1_3-police-flasher/README.md (the `WOKWI_CLI_TOKEN=dummy` placeholder sentence)
    - .planning/phases/04.2-tracer-homework-1-3/04.2-PR-BODY.md (the 18-count sentences at lines 15 and 81 that must stay as submitted)
    - .planning/phases/04.2-tracer-homework-1-3/04.2-11-PLAN.md (the no-edit-after-open rule and the `git diff --quiet` gate)
    - .planning/phases/04.2-tracer-homework-1-3/04.2-VERIFICATION.md (the two security warnings and the PR-body warning)
  </read_first>
  <action>Close findings 4 and 5 in `04.2-SECURITY.md`. In T-4.2-15, replace `6a60426` with `9e1238d` so the mitigation reads `Every ledger row carries method, uncertainty, and the implementation commit `9e1238d`; the metadata table agrees.` In T-4.2-10, replace the mitigation `The token is absent, was never set, and appears in no tracked file; grep for `WOKWI_CLI_TOKEN=` finds nothing.` with `No real credential is present: the only tracked occurrence is the documented placeholder `WOKWI_CLI_TOKEN=dummy` in the homework README, used to exercise the option-path handling; the token was never set to a real value, no other tracked file carries it, and no secret is committed.` Keep both threats' severity, disposition, and `closed` status unchanged.

  Append one row to the Security Audit Trail table: `| 2026-10-25 | 25 | 25 | 0 | orchestrator (T-4.2-10 and T-4.2-15 text corrected to match the tracked artifacts; no status change) |`. Do not change `threats_open: 0`, `status: verified`, the sign-off checkboxes, or any other threat row.

  Close finding 6 by decision, not by edit: do not modify `04.2-PR-BODY.md` in any way, do not run `gh pr edit`, and do not amend or recreate the pull request description. The STATE.md bullet added in task 1 is the record of that decision, and this task's proof is the unchanged-file gate below. Commit only `04.2-SECURITY.md` with the message `docs(04.2): correct the stale security register text`.

  Then run the repository gate: `pre-commit run --all-files`, the metadata checker, and the homework native suite. If a hook modifies a file or a gate fails, fix only the cause in the files this plan owns and re-run; do not disable a hook, weaken a checker, or touch the workflow.</action>
  <verify>
    <automated>python3 -c 'import pathlib; s=pathlib.Path(".planning/phases/04.2-tracer-homework-1-3/04.2-SECURITY.md").read_text(); assert "6a60426" not in s; assert "`9e1238d`" in s; r=[l for l in s.splitlines() if l.startswith("| T-4.2-10 |")]; assert len(r)==1, r; assert "WOKWI_CLI_TOKEN=dummy" in r[0]; assert "finds nothing" not in r[0]; assert "no real credential" in r[0].lower(); assert "no secret is committed" in r[0].lower(); assert "no status change" in s'</automated>
    <automated>git diff --quiet HEAD -- .planning/phases/04.2-tracer-homework-1-3/04.2-PR-BODY.md</automated>
    <automated>pre-commit run --all-files</automated>
    <automated>UV_CACHE_DIR="${TMPDIR:-/tmp}/uv-cache" uv run scripts/check_metadata.py homeworks/1_3-police-flasher</automated>
    <automated>pio test -d homeworks/1_3-police-flasher -e native</automated>
  </verify>
  <acceptance_criteria>
    - T-4.2-15 names `9e1238d`; no `6a60426` remains in the file.
    - T-4.2-10 records the `WOKWI_CLI_TOKEN=dummy` placeholder, states that no real credential exists, and no longer claims the grep finds nothing.
    - The audit trail has the dated correction row; all 25 threats stay closed and `threats_open: 0`.
    - `04.2-PR-BODY.md` is byte-identical to HEAD and no live pull-request edit was attempted.
    - `pre-commit run --all-files`, the metadata checker, and the 38-case native suite all pass.
  </acceptance_criteria>
  <done>The security register matches the current tree, the submitted PR body is provably untouched, and the repository gate is green without weakening any checker.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| working tree -> public repository | Documentation edits are published immediately and cannot be unpublished by rewriting history. |
| historical record -> current claim | Appending a superseding entry must not erase what was previously recorded. |
| quoted evidence -> tracked file | Text copied from the README or report could carry a real token, a home path, or an institution name. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-VIH-01 | Information Disclosure | report.md, 04.2-SECURITY.md, 04.2-VALIDATION.md | high | mitigate | Quote only the already-documented `dummy` placeholder; run the report `/Users/` gate; rely on the gitleaks and Cyrillic hooks in `pre-commit run --all-files`; introduce no institution, enrolment identifier, or real credential. |
| T-VIH-02 | Tampering | `.planning/STATE.md` and the submitted `04.2-PR-BODY.md` | medium | mitigate | STATE.md is append-only: the historical pending bullet stays verbatim and the new bullet states that it supersedes it; the PR body is left byte-identical and the `git diff --quiet HEAD` gate proves it. |
| T-VIH-03 | Repudiation | D-09 confirmation record | medium | mitigate | The confirmation cites the owner and the date and points to `04-UAT.md`, T-4.2-02, and the report appendix, so the claim is traceable rather than asserted. |
| T-VIH-SC | Tampering | package installs | low | accept | No package is installed by this plan; the existing PyYAML and jsonschema pins are unchanged and the CI action pins are untouched. |
</threat_model>

<verification>
Run from the repository root after all three tasks:

1. `python3 -c` gate from task 1: the META-02 row is confirmed, the historical STATE bullet survives, and both new bullets exist after it.
2. `python3 -c` gate from task 2: section 7 and A-05 describe the handshake-only surface, and the implementation commit is still `9e1238d`.
3. `python3 -c` gate from task 3: no `6a60426`, and T-4.2-10 records the dummy placeholder accurately.
4. `git diff --quiet HEAD -- .planning/phases/04.2-tracer-homework-1-3/04.2-PR-BODY.md` exits 0.
5. `pre-commit run --all-files` exits 0 and modifies no file.
6. `UV_CACHE_DIR="${TMPDIR:-/tmp}/uv-cache" uv run scripts/check_metadata.py homeworks/1_3-police-flasher` reports `PASS`.
7. `pio test -d homeworks/1_3-police-flasher -e native` reports 38 of 38 cases passed.
8. `git diff --name-only HEAD` lists only `.planning/STATE.md` (left for the orchestrator's docs commit); the three task commits touch only the validation, report, and security files.
9. `git diff --name-only HEAD -- AGENTS.md .pre-commit-config.yaml .github scripts schema homeworks/1_3-police-flasher/src homeworks/1_3-police-flasher/lib homeworks/1_3-police-flasher/platformio.ini` prints nothing, proving no checker, hook, workflow, schema, or firmware source changed.
</verification>

<success_criteria>
- Finding 1: the META-02 validation row and the Approval line record the owner's 2026-10-25 confirmation.
- Finding 2: STATE.md gains a D-09 closure bullet and a PR-body decision bullet, with the historical pending bullet intact.
- Finding 3: report section 7 and A-05 state the firmware has no transition logging and only the two handshake events.
- Finding 4: T-4.2-15 names `9e1238d`.
- Finding 5: T-4.2-10 records the `WOKWI_CLI_TOKEN=dummy` placeholder and no real credential.
- Finding 6: `04.2-PR-BODY.md` is untouched and the decision to leave it is recorded.
- No checker, hook, workflow, schema, firmware source, ledger value, or threat status was changed; all artifacts stay in English and carry no secret, home path, institution, or enrolment identifier.
</success_criteria>

<output>
Create `.planning/quick/261025-vih-fix-the-six-residual-findings-from-the-p/261025-vih-SUMMARY.md` when done.
</output>
