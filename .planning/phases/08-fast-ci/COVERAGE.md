# Phase 8 — API Coverage Matrix

The phase integrates GitHub Actions as an external platform: it authors workflows, not API
clients. The detector fired on a deferred-ideas line about the "GitHub API"; the real integration
surface is the workflow feature set below. Every capability starts as INTEGRATE; the OPT-OUT rows
are the subtraction record, each with a reason.

| capability | decision | reason |
|---|---|---|
| `pull_request` trigger with explicit `types` (`opened`, `synchronize`, `reopened`, `edited`) | INTEGRATE | The title check must re-run on a retitle; `edited` is not a default type (RESEARCH Open Question 2). |
| `workflow_dispatch` trigger | INTEGRATE | Manual re-run with the `origin/main` fallback and a skipped title check (Pitfall 14). |
| `schedule` trigger (cron) | INTEGRATE | Nightly full matrix (TOOL-06); the only trigger that proves the whole tree daily. |
| Job fan-in through `needs` plus `toJSON(needs)` | INTEGRATE | The single required check `gate` depends on the allowlisted result set (D-2). |
| Dynamic matrix through `fromJson` | INTEGRATE | `scripts/affected.py` owns the matrix; `changes` publishes it (D-3, D-5). |
| `actions/cache` | INTEGRATE | Toolchain and pre-commit caches keyed on reviewed pin files (D-13, D-18). |
| `actions/upload-artifact` | INTEGRATE | Simulation evidence with 7-day retention (D-10). |
| Repository rulesets API (programmatic required-check creation) | OPT-OUT | `AGENTS.md` keeps rulesets in the GitHub UI; a required check is added by hand after the first green run (D-20). Declined in CONTEXT `<deferred>`. |
| Merge queue (`merge_group` trigger) | OPT-OUT | No merge queue is enabled; adding the trigger without a queue would leave the required check pending. Deferred in CONTEXT. |
| `pull_request_target` trigger | OPT-OUT | It would hand a repository secret to untrusted pull-request code; the fork guard and the same-repository check make it unnecessary (D-9, T-8-11). |
| GitHub Pages deployment and the `github-pages` environment | OPT-OUT | The documentation site was removed in commit `9d28f5d`; the ROADMAP amendment of 2026-10-26 puts no build or deploy in scope. |
| Failure notifications (issues, webhooks, chat) | OPT-OUT | Deferred: the red nightly run and its log are the signal. |
