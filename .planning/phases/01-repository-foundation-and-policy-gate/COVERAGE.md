# API Coverage — GitHub REST API

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
> Scope: the surface actually reachable through `scripts/check_policy.py`, which is the
> only shipped component that talks to GitHub. `scripts/tag_homework.sh` uses the `gh`
> CLI's first-class `pr`/`tag` commands, not the REST API.

| capability | decision | reason |
|---|---|---|
| `GET repos/{owner}/{repo}` | INTEGRATE | Read repository settings and `security_and_analysis` for the drift check. |
| `PATCH repos/{owner}/{repo}` | INTEGRATE | Apply `policy/repository.json` in `--apply` mode. |
| `GET repos/{owner}/{repo}/rulesets` | INTEGRATE | Resolve the ruleset id by its committed name; never hard-code an id. |
| `GET repos/{owner}/{repo}/rulesets/{id}` | INTEGRATE | Read the live ruleset and project it onto the committed subset. |
| `PUT repos/{owner}/{repo}/rulesets/{id}` | INTEGRATE | Apply `policy/ruleset-main.json` in `--apply` mode. |
| `POST repos/{owner}/{repo}/rulesets` | OPT-OUT | The ruleset is created once during repository provisioning; the checker updates an existing ruleset and fails loudly if it is absent. |
| `DELETE repos/{owner}/{repo}/rulesets/{id}` | OPT-OUT | Destructive and never part of an idempotent apply; removal is a manual, reviewed action. |
| `GET repos/{owner}/{repo}/rules/branches/{branch}` | OPT-OUT | The shipped checker compares the ruleset object directly; the effective-rules endpoint is used only in ad-hoc acceptance commands, not in code. |
| `security_and_analysis.secret_scanning` | INTEGRATE | Enabled and asserted by `policy/repository.json`. |
| `security_and_analysis.secret_scanning_push_protection` | INTEGRATE | Enabled and asserted by `policy/repository.json`. |
| `security_and_analysis.secret_scanning_validity_checks` | OPT-OUT | Not available on the free organization plan (ADR-0003); revisit when the plan changes. |
| `security_and_analysis.secret_scanning_non_provider_patterns` | OPT-OUT | Not available on the free organization plan (ADR-0003); revisit when the plan changes. |
| Classic branch protection (`/branches/{branch}/protection`) | OPT-OUT | Rulesets supersede it; enabling both would create two conflicting sources of truth. |
| Releases and tags REST API | OPT-OUT | Homework tags are created through git and `scripts/tag_homework.sh`, not the Releases API. |
| GraphQL API | OPT-OUT | The REST endpoints above fully cover the policy assertions; GraphQL adds no capability here. |
| Actions workflow runs and check-runs API | OPT-OUT | CI results are read from the pull-request UI in this phase; Phase 8 introduces programmatic CI gating if needed. |
| Webhooks | OPT-OUT | The project configures no webhooks. |
| Organization and team membership API | OPT-OUT | Authorization is delegated to the maintainer's existing `gh` credentials; the checker never inspects membership. |
