# Skill state file

`new-homework` keeps one checkpoint record per homework at `.skill-state/<id>.json`.
Resolve the path under the chosen root: the repository root, or the `--dir` root when
the homework is scaffolded somewhere else. The file is gitignored and machine-local,
so it is never a repository artifact and may be deleted at any time. Write it before
every checkpoint menu, whatever the user then chooses.

## Shape

```json
{
  "schema_version": 1,
  "homework_id": "1_4-example",
  "skill": "new-homework",
  "mode": "guided",
  "root": "repository",
  "intake": {
    "board": "esp32-s3-devkitc-1",
    "framework": "arduino",
    "language": "cpp",
    "specification": "free-form",
    "simulation": "none",
    "simulation_token_present": false,
    "tests": "unity-native",
    "deliverables": ["readme", "report"],
    "provenance": {
      "source_url": "https://example.invalid/assignment",
      "retrieved": "2026-10-26T20:00:00Z",
      "attribution": "Course assignment, paraphrased in English.",
      "license": "MIT",
      "status": "complete"
    }
  },
  "blocks": [
    {"id": "scaffold", "status": "done"},
    {"id": "controller", "status": "in-progress"}
  ],
  "next_block": "controller",
  "assumptions": [],
  "conflicts": [],
  "checkpoints": [
    {"name": "intake", "at": "2026-10-26T20:05:00Z", "commit": "abc1234"}
  ]
}
```

The example above uses the Arduino framework, so its `intake.language` is `cpp`; an
ESP-IDF run records `c`.

## Fields

| Field | Type | Values |
|-------|------|--------|
| `schema_version` | integer | `1` |
| `homework_id` | string | matches `^[0-9]+_[0-9]+-[a-z0-9-]+$` |
| `skill` | string | the literal `new-homework` |
| `mode` | string | `guided` or `one-shot` |
| `root` | string | `repository` or `temporary` |
| `intake.board` | string | a board id |
| `intake.framework` | string | `arduino` or `espidf` |
| `intake.language` | string | `cpp` for `arduino`, `c` for `espidf` |
| `intake.specification` | string | `ready` or `free-form` |
| `intake.simulation` | string | `none`, `wokwi` or `other` |
| `intake.simulation_token_present` | boolean | `true` or `false` |
| `intake.tests` | string | `unity-native` or `none` |
| `intake.deliverables` | array of strings | the documents the assignment requires |
| `intake.provenance` | object | `source_url`, `retrieved`, `attribution`, `license`, each a string, plus `status` of `complete` or `blocked` |
| `blocks` | array of objects | each `{id, status}`; `id` is `scaffold`, `controller`, `native-tests`, `wiring` or `report`, and `status` is `pending`, `in-progress` or `done` |
| `next_block` | string or `null` | a block id, or `null` when nothing remains |
| `assumptions` | array of objects | the record shape below, with `kind: ambiguity` |
| `conflicts` | array of objects | the record shape below, with `kind: spec-conflict` |
| `checkpoints` | array of objects | each `{name, at, commit}`; `name` is `intake`, `code` or `report`, `at` is an ISO-8601 instant, `commit` is a short hash or `null` |

Every assumption and conflict record carries these keys: `id` (string), `kind`
(`spec-conflict` or `ambiguity`), `topic` (string), `specification` (string),
`best_practice` (string), `recommendation` (string), `impact_if_wrong` (string),
`recorded_at` (ISO-8601 instant), `commit` (short hash or `null`) and `status`
(`proposed`, `accepted` or `rejected`). A record stays `proposed` until the user
accepts it; silence, delay and an indirect answer are never acceptance.

## Block pauses and the three checkpoints

The two menus write different things, and the file keeps them distinct. A block pause
updates that block's `status` and `next_block`; it does not append a named checkpoint.
Only the three checkpoints append to `checkpoints[]`, one `{name, at, commit}` entry
each, so `intake`, `code` and `report` appear at most once each.

## Git absence

`commit` is the short hash from `git rev-parse --short HEAD`, taken with the failure
tolerated rather than raised. When the call fails, or the chosen root is not a git
worktree, record `"commit": null` and `"root": "temporary"`. A git failure is not an
error: a temporary root must stay resumable.

## Resume

If the file already exists when the skill starts, ask `[Продовжити | Почати заново |
Стоп]`. `Продовжити` resumes from `next_block` and never rewrites a completed block's
record; `Почати заново` starts clean; `Стоп` leaves the file untouched. Only the
explicit clean start may overwrite an abandoned record, so a stale file is never
silently discarded.

## Write discipline

- Create the parent directories under the chosen root.
- Write the whole document to a temporary file in the same directory, then move it into
  place with `os.replace`, so no reader ever observes a half-written file.
- Refuse a symlink at any component. Inspect each component of `.skill-state/<id>.json`
  with `lstat` before reading or writing, and never follow a link.
- Delete the file only after the report checkpoint succeeds. Keep it on abort, on stop
  and on any failure, so the run is resumable.
- Never write a token value. The file records only `simulation_token_present`.
- Never store an original assignment text. The file records the user's English
  paraphrase and the source reference, never a verbatim copy of course material.
