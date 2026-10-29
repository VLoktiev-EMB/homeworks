---
phase: quick
plan: 261029-kbn
type: execute
wave: 1
depends_on: []
files_modified:
  - homeworks/1_5-button-bounce/report.md
  - homeworks/1_5-button-bounce/README.md
  - homeworks/1_5-button-bounce/homework.yaml
files_added:
  - homeworks/1_5-button-bounce/assets/measurements/serial.log
  - homeworks/1_5-button-bounce/assets/measurements/digital.csv
autonomous: true
requirements: ["QUICK-261029-kbn"]
estimate:
  tokens: 40000
  raw_tokens: 40000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "Every ledger row L-01 through L-13 carries a captured value, and each Label is `measured` or `calculated`; no ledger row keeps an unmeasured label."
    - "The per-press counts match the locked table exactly, and the totals read 65 MCU edges against 74 analyzer edges, a difference of -9 edges (-12.2%)."
    - "L-11 reads 978.1 us with 1222.6 us as the release-only secondary value; L-12 reads 1 ms from C-06."
    - "Section 1 and all thirteen ledger rows name implementation commit a99da51, and no earlier firmware hash survives."
    - "homework.yaml sets status and report.status to complete and lists both measurement files under assets."
    - "README.md carries a complete status and a Measurements section that links both evidence files with the headline results."
    - "No edited file claims that the hw/1_5-button-bounce tag exists."
  artifacts:
    - path: homeworks/1_5-button-bounce/report.md
      provides: "Filled ledger, C-06, measured analysis, and updated traceability"
    - path: homeworks/1_5-button-bounce/homework.yaml
      provides: "Complete status and the two measurement assets"
    - path: homeworks/1_5-button-bounce/README.md
      provides: "Complete status and a Measurements section"
    - path: homeworks/1_5-button-bounce/assets/measurements/serial.log
      provides: "Ten-press firmware evidence, bytes unchanged"
    - path: homeworks/1_5-button-bounce/assets/measurements/digital.csv
      provides: "24 MS/s analyzer export, bytes unchanged"
  key_links:
    - "digital.csv holds 74 transitions (37 falling, 37 rising) over the 12.364 s capture and serial.log TOTAL holds 65 edges, so the comparison is 65 versus 74, not a falling-only count."
    - "A 10 ms gap over the E transitions yields the five bounce events and the 160.625 us maximum HIGH gap; burst 10's duration_us and min_stable_ms are not per-event metrics."
    - "C-06 applies the debounce criterion to the measured 160.625 us gap and yields L-12 = 1 ms; C-04 adds the 20x and 124x margins without dropping the [5] published row."
    - "The firmware falling and rising fields count the level at ISR entry, so the falling-level comparison 35 versus 37 is secondary to the 65 versus 74 edge total."
    - "a99da51 is the merged main commit that contains the final firmware and replaces every earlier hash."
---

<objective>
Fill the `1_5-button-bounce` measurement ledger from the committed serial log and analyzer export,
rewrite the report's quantitative prose so it answers the four assignment questions, mark the
homework and report complete in `homework.yaml`, and add a Measurements section to the README.

Purpose: the firmware and wiring already ship, and the ten-press bench evidence now exists. The
report still labels every measurement row as outstanding and the metadata still says the homework
is in progress, so the artifact does not yet carry the evidence it describes.

Output: one atomic `docs(1_5)` commit touching `report.md`, `README.md`, `homework.yaml`, and the
two evidence files, with the evidence bytes unchanged and no tag created.
</objective>

<context>
@.planning/STATE.md
@AGENTS.md
@.claude/CLAUDE.md
@.agents/standards/report.md
@schema/homework.schema.json
@.agents/skills/hw-report/SKILL.md
@homeworks/1_5-button-bounce/report.md
@homeworks/1_5-button-bounce/README.md
@homeworks/1_5-button-bounce/homework.yaml
@homeworks/1_5-button-bounce/task.md
@homeworks/1_5-button-bounce/assets/measurements/serial.log
@homeworks/1_5-button-bounce/assets/measurements/digital.csv
</context>

## Owner decisions (locked — do not revisit)

1. The analyzer is a Saleae Logic 8-channel at 24 MS/s, capture delta-T 12.364 s, 74 transitions
   (37 falling, 37 rising). The firmware captured 65 edges (35 falling-level, 30 rising-level).
2. Per-press comparison (MCU edges / analyzer edges, MCU falling-level / analyzer falling,
   analyzer bounce):
   1: 4/6, 3/3, release 363.167 us; 2: 2/2, 1/1, none; 3: 18/20, 9/10, release 3780.25 us;
   4: 2/2, 1/1, none; 5: 2/4, 1/2, press 0.25 us; 6: 2/2, 1/1, none; 7: 2/2, 1/1, none;
   8: 25/28, 14/14, release 305.5 us; 9: 6/6, 3/3, release 441.333 us; 10: 2/2, 1/1, none.
   Totals: MCU 65 edges, analyzer 74; difference -9 edges (-12.2%). MCU falling-level 35 versus
   analyzer falling 37.
3. Five bounce events: one press-phase event at 0.25 us, four release-phase events at 363.167,
   3780.25, 305.5 and 441.333 us. Mean over five is 978.1 us; the release-only mean is 1222.6 us.
   L-11's headline value is 978.1 us, with the release-only mean as a secondary statement.
4. Minimum sufficient debounce is 1 ms, derived from the maximum HIGH gap of 160.625 us. The 20 ms
   window is about 124x that measured gap and 20x the derived 1 ms minimum.
5. The firmware's 250 ms quiet-gap segmentation merged rapid presses (burst 10 contains presses
   6-10), so that burst's duration_us (1797561 us) and min_stable_ms (237 ms) are not single-bounce
   metrics. Use a 10 ms cluster gap over the E transitions for per-event bounce duration and
   minimum debounce, and say so.
6. The firmware's falling and rising fields count the level read at each ISR entry, not the
   transition direction; the analyzer counts true transitions. The reliable comparison is the edge
   total (65 versus 74); the falling-level comparison (35 versus 37) is secondary and carries that
   caveat.
7. The implementation commit in section 1 and every ledger row becomes a99da51, the merged main
   commit that contains the final firmware. Do not invent another hash.
8. `homework.yaml`: status complete, report status complete, and the two measurement files added to
   assets.
9. README: status becomes complete, and a new Measurements section links
   `assets/measurements/serial.log` and `assets/measurements/digital.csv` with the headline results.
10. Keep the ten report headings, evidence labels, traceability matrix, limitations, and honest
    measured/calculated labels. Add calculation row C-06 for the measured 1 ms minimum and update
    C-04's margin to reference the measured value while keeping the published-reference row.
11. Traceability: T-09 `manual` with L-13 evidence; T-10 `verified` with L-01..L-13; T-11
    `verified` with C-03, C-06, L-12.
12. Do not claim the `hw/1_5-button-bounce` tag exists; the tag remains an owner action after this
    pull request.

## Working-tree facts

- Branch is `hw/1_5-button-bounce`; `git status --porcelain` shows only
  `?? homeworks/1_5-button-bounce/assets/measurements/`.
- The evidence files are untracked and must keep their exact bytes:
  - `serial.log` SHA-256
    `4bc013f8d9dfc8b3436ba56511d885d8eda64b88f1f6a12e9319beab54360168`
  - `digital.csv` SHA-256
    `3eb4e27f0e8a773ee3ec0d49a9b1efacfb3587936d15f1a2a562a56ca0591e5f`
- `.vscode/settings.json` is the local editor settings file named by the owner constraint: it is
  currently clean and must never be staged.
- The report currently repeats the earlier firmware commit in section 1 and all thirteen ledger
  rows; every occurrence is replaced by a99da51.
- `.agents/standards/report.md` is the authoritative report contract. The `hw-report` skill's Quick
  Reference table is older than that contract; do not rename any report heading to match it.
- The standard mentions `scripts/check_report.py`, but this tree has no such script and no
  `check-report` hook. The available machine gate is `uv run scripts/check_metadata.py` plus the
  pre-commit hooks; do not run a checker that does not exist.
- Do not touch `task.md`, `src/`, `platformio.ini`, `assets/diagram.json`, `assets/schematic.svg`,
  or the untracked `.pio`, `.cache`, and `.vscode` state.

## Tasks

<task type="auto">
  <name>Task 1: Fill the measurement ledger and rewrite the quantitative report prose</name>
  <files>homeworks/1_5-button-bounce/report.md</files>
  <action>
Rewrite `homeworks/1_5-button-bounce/report.md` so every bench claim is backed by the two evidence
files. Keep the ten level-2 headings, their order, the six evidence-table headers, the label
vocabulary, the traceability matrix, section 10, and the Decision Appendix. Add relative links to
`assets/measurements/serial.log` and `assets/measurements/digital.csv` where the methodology and
results cite them; every relative link must resolve under the homework directory.

Use these locked measurement facts:
- Analyzer: Saleae Logic 8-channel, 24 MS/s, 1.65 V threshold, channel D0 on GPIO 16; capture
  delta-T 12.364 s; 74 transitions, 37 falling and 37 rising.
- Firmware: 65 edges, 35 falling-level and 30 rising-level, from the TOTAL line.
- Difference: -9 edges, -12.2%.
- Five bounce events: one press-phase at 0.25 us and four release-phase at 363.167, 3780.25, 305.5
  and 441.333 us. Mean 978.1 us; release-only mean 1222.6 us.
- Maximum HIGH gap inside a bounce cluster: 160.625 us; minimum sufficient debounce 1 ms.
- The 20 ms window is 20x the 1 ms measured minimum and about 124x the 160.625 us gap.
- Burst 10's duration_us 1797561 us and min_stable_ms 237 ms are not single-bounce metrics; the
  per-event analysis uses a 10 ms cluster gap over the E transitions.
- The firmware counts the level at ISR entry, not the transition direction; the edge total is the
  primary comparison and the falling-level comparison is secondary.

Apply these edits in order.

1. Lead paragraph: state that the implementation and the ten-press capture are complete, name the
   Saleae Logic 8-channel analyzer at 24 MS/s, cite both evidence files, and say every ledger row is
   labelled measured or calculated.

2. Section 1 table: set Homework status and Report status to complete; set Implementation commit to
   a99da51.

3. Section 2: replace the final paragraph with one that says this implementation delivers the
   firmware, the wiring source of truth, the measurement procedure, and the ten-press capture in
   `assets/measurements/`, with the captured data reported in section 7 and analyzed in section 8.

4. Section 3: in A-01 validation, make the edge total the primary comparison and the falling-level
   count secondary; in A-05 validation, cite the two attached evidence files; in A-06, make the
   assumption the measured HIGH gaps and the validation the 10 ms cluster, the 160.625 us maximum
   gap, and the 1 ms derived minimum; in A-08 validation, record 24 MS/s, the 1.65 V threshold, and
   the export path.

5. Section 4 Limitations: replace the sentence that says no bench data exists with the measured
   limits: the ISR recorded 65 of the analyzer's 74 transitions, the 24 MS/s analyzer resolves
   41.7 ns, the measured 0.25 us press event spans six samples, and the 250 ms burst segmentation
   merges rapid presses, so per-event metrics need the 10 ms cluster. Keep the timestamp-wrap,
   capture-capacity, and threshold limitations.

6. Section 5 Electrical Calculations: keep C-04 and its [5] provenance; set its Result to
   `3.2 published; 20 measured` and extend its Assumption effect to say 20 ms is 20x the C-06
   minimum and about 124x the measured HIGH gap. Add C-06 after C-05 with Quantity
   `Minimum debounce from the measured maximum HIGH gap`, Formula
   `W = floor(max_high_us / 1000) + 1`, Units `ms`, Input provenance
   `max_high_us = 160.625 us from the 10 ms-clustered analyzer capture, assets/measurements/digital.csv; criterion from [5]`,
   Result `1`, Uncertainty `1 ms quantization; 41.7 ns analyzer sample interval at 24 MS/s`, and
   Assumption effect `A-06; 20 ms is 20x this measured minimum and about 124x the measured HIGH gap.`

7. Section 6 Methodology: replace the `at least 10 MS/s` analyzer description with the Saleae Logic
   8-channel at 24 MS/s, 1.65 V threshold, D0 on GPIO 16, capture 12.364 s, 74 transitions. Add the
   analysis method: pair the press and release BURST lines with analyzer clusters formed by a 10 ms
   gap over the E transitions; bounce duration is a multi-transition cluster span; the minimum
   debounce uses the largest HIGH interval inside a bounce cluster. Add the counting-convention
   caveat from locked decision 6. Keep the serial and build facts.

8. Section 7 Results: replace the opening paragraph with the build/schematic/lint status plus the
   capture summary (74 transitions over 12.364 s, 65 firmware edges, -9 edges / -12.2%, five bounce
   events, mean 978.1 us, 1 ms minimum). Update the Test coverage paragraph to name the bench
   capture in `assets/measurements/` as the verification path. Fill the ledger as follows, keeping
   the existing eight-column header.
   - For L-01 through L-10: Quantity `Press N edges and bounce`; Label `measured`; Instrument
     `Saleae Logic 8-channel at 24 MS/s; ESP32-S3 CHANGE ISR`; Method `Pair the press and release BURST lines with the analyzer clusters`;
     Uncertainty `41.7 ns analyzer sample interval; ISR entry latency and 1 us micros resolution`;
     Implementation commit `a99da51`. Set Value exactly to:
     L-01 `serial-log: MCU 4 edges (falling-level 3); user-reported: analyzer 6 edges (3 falling); release bounce 363.167 us`
     L-02 `serial-log: MCU 2 edges (falling-level 1); user-reported: analyzer 2 edges (1 falling); no bounce`
     L-03 `serial-log: MCU 18 edges (falling-level 9); user-reported: analyzer 20 edges (10 falling); release bounce 3780.25 us`
     L-04 `serial-log: MCU 2 edges (falling-level 1); user-reported: analyzer 2 edges (1 falling); no bounce`
     L-05 `serial-log: MCU 2 edges (falling-level 1); user-reported: analyzer 4 edges (2 falling); press bounce 0.25 us`
     L-06 `serial-log: MCU 2 edges (falling-level 1); user-reported: analyzer 2 edges (1 falling); no bounce`
     L-07 `serial-log: MCU 2 edges (falling-level 1); user-reported: analyzer 2 edges (1 falling); no bounce`
     L-08 `serial-log: MCU 25 edges (falling-level 14); user-reported: analyzer 28 edges (14 falling); release bounce 305.5 us`
     L-09 `serial-log: MCU 6 edges (falling-level 3); user-reported: analyzer 6 edges (3 falling); release bounce 441.333 us`
     L-10 `serial-log: MCU 2 edges (falling-level 1); user-reported: analyzer 2 edges (1 falling); no bounce`
   - L-11: Quantity `Mean bounce duration (five events)`; Label `measured`; Value
     `serial-log: mean 978.1 us across 5 bounce events; release-only mean 1222.6 us`; Instrument
     `Saleae Logic 8-channel at 24 MS/s`; Method `Arithmetic mean of the five measured bounce-event durations`;
     Uncertainty `Event spread 0.25 us to 3780.25 us; one press-phase and four release-phase events`;
     commit `a99da51`.
   - L-12: Quantity `Minimum sufficient debounce`; Label `calculated`; Value `1 ms from C-06`;
     Instrument `Saleae Logic 8-channel at 24 MS/s`; Method
     `C-06 applied to the 160.625 us maximum HIGH gap`; Uncertainty
     `1 ms quantization; 41.7 ns analyzer sample interval`; commit `a99da51`.
   - L-13: Quantity `MCU versus analyzer edge count`; Label `measured`; Value
     `serial-log: MCU 65 edges (falling-level 35); user-reported: analyzer 74 edges (37 falling); difference -9 edges (-12.2%)`;
     Instrument `Saleae Logic 8-channel at 24 MS/s; ESP32-S3 CHANGE ISR`; Method
     `Compare the TOTAL line with the analyzer transition total over the same capture`; Uncertainty
     `ISR entry latency and 1 us micros resolution; the firmware counts the level at ISR entry while the analyzer counts true transitions`;
     commit `a99da51`.
   - Traceability: set T-07 to `verified` with evidence `L-01 through L-13; T-01 through T-12`; set
     T-09 evidence to `L-13; src/main.cpp` and status `manual`; set T-10 evidence to
     `L-01 through L-13` and status `verified`; set T-11 evidence to `C-03; C-06; L-12` and status
     `verified`.

9. Section 8 Analysis: rewrite the quantitative prose so it answers the four assignment questions.
   State that the MCU recorded 65 edges against 74 analyzer edges (-9, -12.2%), that it never
   over-counts, and that it misses 2, 2, 2 and 3 edges in presses 1, 3, 5 and 8 while presses 2, 4,
   6, 7, 9 and 10 agree exactly. State that the misses are edges below the ISR's resolution or entry
   latency and that the falling-level comparison 35 versus 37 is secondary because the firmware
   counts the level at ISR entry. State the five bounce events, the 978.1 us mean and the 1222.6 us
   release-only mean. State that burst 10's 1797561 us duration and 237 ms min_stable_ms are
   segmentation artifacts and that the 10 ms cluster analysis is the per-event basis. State that
   the 160.625 us maximum HIGH gap yields the 1 ms minimum through C-06, and that the 20 ms window
   is 20x the derived minimum and about 124x the measured gap. Keep one paragraph that begins
   `Industry note:`.

10. Section 9 Conclusions: answer the four questions with the measured values; keep a standalone
    paragraph that begins `Status:` and names commit a99da51, the green target build, the green
    schematic check, the green offline lint, and the attached evidence. State that the
    `hw/1_5-button-bounce` tag has not been created by this change. Rewrite Next Steps so the owner
    capture and ledger-filling steps are gone; the remaining steps are opening the pull request,
    merging after the `gate` check is green, and creating the tag through
    `scripts/tag_homework.sh` after the merge.

Do not rename headings, do not change section 10, and do not add a new calculation row other than
C-06.
  </action>
  <verify>
    <automated>python3 -c "import pathlib,sys;t=pathlib.Path('homeworks/1_5-button-bounce/report.md').read_text(encoding='utf-8');req=['a99da51','C-06','978.1','1222.6','160.625','74 transitions','65 edges','-9 edges','-12.2%','Press 1','Press 10'];miss=[x for x in req if x not in t];led=t.split('### Measurement Ledger')[1].split('### Traceability Matrix')[0];lr=[l for l in led.splitlines() if l.startswith('| L-')];bad=[l for l in lr if '| not measured |' in l];t9=[l for l in t.splitlines() if l.startswith('| T-09 |')][0];t10=[l for l in t.splitlines() if l.startswith('| T-10 |')][0];t11=[l for l in t.splitlines() if l.startswith('| T-11 |')][0];ok=len(lr)==13 and not bad and 'manual' in t9 and 'L-13' in t9 and 'verified' in t10 and 'verified' in t11 and 'C-06' in t11;sys.exit(0 if not miss and ok and '66f966b' not in t else 1)"</automated>
  </verify>
  <done>
    Section 1 and all thirteen ledger rows name a99da51. Every ledger row carries a captured value
    with label measured or calculated. C-06 exists, C-04 keeps its published row and adds the
    measured margins. The analysis answers the four questions with the locked values, the results
    narrative and conclusions no longer say the capture is outstanding, and the tag is not claimed.
  </done>
</task>

<task type="auto">
  <name>Task 2: Mark the homework complete and add the README Measurements section</name>
  <files>homeworks/1_5-button-bounce/homework.yaml, homeworks/1_5-button-bounce/README.md</files>
  <action>
Update the metadata and the README.

In `homeworks/1_5-button-bounce/homework.yaml`:
- Set the top-level `status` to `complete`.
- Set `report.status` to `complete`.
- Add `assets/measurements/serial.log` and `assets/measurements/digital.csv` to `assets`, keeping
  the existing diagram and schematic entries and the schema path pattern.
- Leave every other key unchanged: id, title, board, framework, language, source, toolchain, tests.

In `homeworks/1_5-button-bounce/README.md`:
- Replace the status sentence with one that states the homework is complete: firmware, wiring, and
  the ten-press bench capture are done, and the report records the measured results.
- Add a `## Measurements` section after `## Wiring` and before `## Build`. It links
  `[serial.log](assets/measurements/serial.log)` and `[digital.csv](assets/measurements/digital.csv)`
  and gives the headline results: Saleae Logic 8-channel at 24 MS/s, capture 12.364 s, 74 analyzer
  transitions (37 falling, 37 rising); 65 firmware edges (35 falling-level, 30 rising-level), a
  difference of -9 edges (-12.2%); five bounce events with a 978.1 us mean (release-only 1222.6 us,
  press-phase 0.25 us, release events 363.167, 3780.25, 305.5 and 441.333 us); minimum sufficient
  debounce 1 ms from the 160.625 us maximum HIGH gap, with the 20 ms window about 124x that gap.
- Replace the measurement-procedure step that tells the reader to fill the ledger, because the
  ledger already records the captured values; make it say the procedure is repeated and both files
  are updated if the button or wiring changes.
- Add the two evidence files to the Layout list.
- Do not claim the tag exists and do not state that measurements are still outstanding.
  </action>
  <verify>
    <automated>python3 -c "import pathlib,sys;y=pathlib.Path('homeworks/1_5-button-bounce/homework.yaml').read_text(encoding='utf-8');r=pathlib.Path('homeworks/1_5-button-bounce/README.md').read_text(encoding='utf-8');ym=[x for x in ['status: complete','assets/measurements/serial.log','assets/measurements/digital.csv'] if x not in y];yb=[x for x in ['in-progress','draft'] if x in y];rm=[x for x in ['## Measurements','assets/measurements/serial.log','assets/measurements/digital.csv','978.1','1222.6','1 ms','-12.2%'] if x not in r];rb=[x for x in ['in-progress','pending'] if x in r];sys.exit(1 if ym or yb or rm or rb else 0)"</automated>
  </verify>
  <done>
    `homework.yaml` sets both status fields to complete and lists both evidence files under assets.
    The README status is complete, a Measurements section links both files with the headline
    results, the procedure no longer tells the reader to fill an already-filled ledger, and the
    layout names the evidence.
  </done>
</task>

<task type="auto">
  <name>Task 3: Run the gates, confirm the evidence bytes, and commit once</name>
  <files>
    homeworks/1_5-button-bounce/report.md,
    homeworks/1_5-button-bounce/README.md,
    homeworks/1_5-button-bounce/homework.yaml,
    homeworks/1_5-button-bounce/assets/measurements/serial.log,
    homeworks/1_5-button-bounce/assets/measurements/digital.csv
  </files>
  <action>
Verify the finished artifact and make one atomic commit.

Run from the repository root, in this order:
1. `uv run scripts/check_metadata.py`.
2. `pio run -d homeworks/1_5-button-bounce`.
3. Stage exactly the three edited documents and the two evidence files with explicit paths; never
   use `git add -A` or `git add .`.
4. Run `pre-commit run --files` on the same five paths. If a hook rewrites a file, re-stage only
   the three edited documents and re-run; if a hook rewrites either evidence file, stop and report
   the byte change instead of re-staging it.
5. Commit once with a Conventional Commit subject such as
   `docs(1_5): record the button bounce measurements and mark the homework complete`.
6. Confirm the two evidence hashes still match the values in Working-tree facts, that the commit
   contains both evidence files, and that the commit does not contain the editor settings file named
   in Working-tree facts.

Do not create, move, or push a tag. Do not stage the editor settings file. Do not touch `task.md`,
`src/`, `platformio.ini`, or the assets other than the two measurement files.
  </action>
  <verify>
    <automated>uv run scripts/check_metadata.py && pio run -d homeworks/1_5-button-bounce && pre-commit run --files homeworks/1_5-button-bounce/report.md homeworks/1_5-button-bounce/README.md homeworks/1_5-button-bounce/homework.yaml homeworks/1_5-button-bounce/assets/measurements/serial.log homeworks/1_5-button-bounce/assets/measurements/digital.csv && test "$(shasum -a 256 homeworks/1_5-button-bounce/assets/measurements/serial.log | awk '{print $1}')" = "4bc013f8d9dfc8b3436ba56511d885d8eda64b88f1f6a12e9319beab54360168" && test "$(shasum -a 256 homeworks/1_5-button-bounce/assets/measurements/digital.csv | awk '{print $1}')" = "3eb4e27f0e8a773ee3ec0d49a9b1efacfb3587936d15f1a2a562a56ca0591e5f" && git rev-parse --verify HEAD >/dev/null && test -n "$(git show --name-only --format= HEAD -- homeworks/1_5-button-bounce/assets/measurements/serial.log)" && test -n "$(git show --name-only --format= HEAD -- homeworks/1_5-button-bounce/assets/measurements/digital.csv)" && test -z "$(git show --name-only --format= HEAD -- .vscode/settings.json)"</automated>
  </verify>
  <done>
    The metadata checker and the target build pass, the five files pass pre-commit, one commit
    contains the three documents and both unchanged evidence files, the editor settings file is not
    in the commit, and no tag exists or was moved.
  </done>
</task>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| bench evidence to report | The serial log and analyzer export are the only source of measured values; the report must not infer a value they do not contain. |
| working tree to commit | Only the five intended paths may enter the commit; local editor and generated state must stay out. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-QBN-01 | Tampering | `assets/measurements/serial.log`, `assets/measurements/digital.csv` | high | mitigate | Record the SHA-256 of both files in the plan and re-check them after the commit; never rewrite evidence bytes. |
| T-QBN-02 | Repudiation | `report.md` measurement ledger | high | mitigate | Every row carries the locked value, the instrument, the method, the uncertainty, and commit a99da51; no unlabelled or unmeasured row survives. |
| T-QBN-03 | Information disclosure | commit contents | medium | mitigate | Stage explicit paths only; the editor settings file and local build state never enter the commit. |
| T-QBN-SC | Tampering | package-manager installs | high | mitigate | No npm/pip/cargo install is planned; `uv` runs only the pinned metadata script. A package install would need the legitimacy gate and a blocking human checkpoint. |
</threat_model>

<verification>
Run from the repository root after the three tasks:

- `uv run scripts/check_metadata.py` — the metadata contract accepts status complete and the two
  new assets.
- `pio run -d homeworks/1_5-button-bounce` — the target build stays green.
- `pre-commit run --files homeworks/1_5-button-bounce/report.md homeworks/1_5-button-bounce/README.md homeworks/1_5-button-bounce/homework.yaml homeworks/1_5-button-bounce/assets/measurements/serial.log homeworks/1_5-button-bounce/assets/measurements/digital.csv`
  — hygiene, YAML lint, metadata, large-file, generated-file, and secret hooks pass.
- `git status --porcelain` — the editor settings file remains unstaged; the five intended paths are
  the only change.
- Ledger scan: the region between `### Measurement Ledger` and `### Traceability Matrix` contains
  thirteen `L-` rows and no unmeasured label cell.
- Evidence scan: both SHA-256 values equal the Working-tree facts values.
- Claim scan: no edited file asserts that the `hw/1_5-button-bounce` tag exists.
</verification>

<success_criteria>
- `uv run scripts/check_metadata.py` exits 0.
- `pio run -d homeworks/1_5-button-bounce` exits 0.
- `pre-commit run --files <the five paths>` exits 0.
- `report.md` has thirteen filled ledger rows, all with label measured or calculated, and section 1
  plus every row names a99da51.
- The ledger values match decisions 1 through 4 exactly, including 65 versus 74 edges, -9
  (-12.2%), 978.1 us, 1222.6 us, and 1 ms.
- C-06 exists; C-04 keeps its published [5] row and states the measured margins.
- T-09 is manual with L-13; T-10 and T-11 are verified with the required evidence.
- `homework.yaml` sets both status fields to complete and lists both evidence files.
- README has a Measurements section linking both files with the headline results.
- The two evidence files have unchanged SHA-256 values and are committed.
- The commit does not contain the editor settings file; no tag is created or moved.
</success_criteria>

<output>
Execute the three tasks in order and commit once, staging only the three edited documents and the
two evidence files. Write the execution summary to
`.planning/quick/261029-kbn-fill-the-1-5-button-bounce-measurement-l/261029-kbn-SUMMARY.md`.
Do not create or move the `hw/1_5-button-bounce` tag; that remains an owner action after the pull
request merges.
</output>
