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

- [ ] Build passes: `pio run` succeeds for every environment the homework touches
- [ ] Native tests pass: `python3 -m unittest discover -s scripts/tests -v`
- [ ] Report contains every required section, from objective through conclusion
- [ ] Every measurement carries a provenance label (measured, simulated, or calculated)
- [ ] Generated index and workspace are refreshed; `git status` shows no drift
- [ ] Simulation evidence is attached when the homework is simulated
