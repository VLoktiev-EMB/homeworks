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

## Definition of Done

- [ ] Decision recorded as an ADR under `docs/decisions/`, or an explicit note that no ADR applies
- [ ] Policy check passes: `python3 scripts/check_policy.py --check`
- [ ] No new secrets: `gitleaks git` reports nothing on the branch
- [ ] Documentation updated wherever the change alters contributor behavior
