---
phase: "03"
slug: "shared-core-and-dependency-rule"
status: verified
threats_open: 0
asvs_level: 1
created: "2026-10-24"
---

# Phase 03 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| PlatformIO registry → local build | Unity 2.6.1 is fetched on first use; the pin is the only control | Third-party source archive |
| `lib/host` → native build | A test double is linked into the same binary as `common` | Test-only C symbols |
| injected `ctx` → adapter | The consumer passes an opaque pointer across the seam | Caller-owned state |
| published record → future contributors | An accepted ADR is read as normative after the code has moved on | Public documentation |
| record prose → public repository | Anything written here is published and permanent | Public documentation |
| consumer → adapter | The consumer passes buffers and lengths across an opaque pointer | Caller-owned buffers |
| contract design → future homework | A too-wide contract becomes the repository's shadow framework | Public C API |
| caller buffer → shared primitive | Every function trusts a caller-supplied pointer and length | Caller-owned buffers |
| checksum output → report claim | A CRC value can be mistaken for a security control if the prose is loose | Digest value |
| fake → production code | A fake that drifts from the real contract makes a green suite meaningless | Test-only C symbols |
| fake storage → test process | An unbounded write corrupts the run rather than failing it | Test-only storage |
| `host` library → firmware | A single wrong `lib_deps` entry would ship test doubles to a board | Build configuration |
| adapter → framework | A translated call runs with driver privileges on the target | GPIO / log / time calls |
| framework types → public headers | A leaked framework type makes every consumer depend on the framework version | Public C API |
| adapter → native build | An adapter accidentally linked into `tests/` would break the "no target toolchain" property | Build configuration |
| repository layout → every ESP32 project | `board_build.partitions` resolves relative to each project directory | Partition table |
| deleted project → test suite | A test that hard-reads a deleted path fails the whole gate | Test fixtures |
| manifest version → build graph | Duplicated version strings drift silently | Package metadata |
| repository tree → checker process | The checker reads every source file and any symlink it encounters | Source tree |
| allowlist file → policy | A permissive entry silently disables a rule for one path | Policy configuration |
| pre-commit hook → developer machine | The hook runs the repository script with developer privileges | Source tree |
| native build → purity claim | A toolchain or framework include that slips into the database invalidates success criterion 1 | Build database |
| suite output → digest | A too-wide match turns an unstable line into a false determinism signal | Test transcript |
| wall clock → gate runtime | Twenty runs without a timeout can hang an executor or a future CI job | Process runtime |
| temporary fixture → real tree | A copied symlink or an unresolved relative path could make the fixture compile the real sources | Temporary fixtures |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-03-24 | Tampering | `tests/lib_deps` Unity entry | high | mitigate | Exact pin `throwtheswitch/Unity@2.6.1` in `tests/platformio.ini`; installed manifest asserted | closed |
| T-03-25 | Tampering | `host_fake_time_port` / `port_time_t` seam | medium | mitigate | Fakes return the same `port_time_t` type as adapters, so signature drift is a compile error | closed |
| T-03-26 | Information Disclosure | `tests/compile_commands.json` | low | mitigate | `.gitignore` ignores `compile_commands.json`; never listed in `files_modified` | closed |
| T-03-SC (03-01) | Tampering | PlatformIO package installs | high | mitigate | Only pinned `throwtheswitch/Unity@2.6.1` is added; audit-recorded in RESEARCH | closed |
| T-03-27 | Information Disclosure | ADR-0008 prose | medium | mitigate | Public handle only; `test_adrs.py` rejects email shapes in every record | closed |
| T-03-SC (03-02) | Tampering | package installs | high | mitigate | Plan installs nothing; Unity remains the only external package | closed |
| T-03-28 | Elevation of Privilege | `lib/port` header surface | high | mitigate | Bus-level operations only; no native-handle accessor or driver-state struct; checker enforces the include matrix | closed |
| T-03-29 | Tampering | `port_gpio_level_t` / `port_status_t` enum values | low | mitigate | Explicit enumerator values; `test_status_values_are_stable` pins them | closed |
| T-03-SC (03-03) | Tampering | package installs | high | mitigate | Plan installs nothing; Unity pinned by 03-01 | closed |
| T-03-30 | Tampering | ring-buffer index arithmetic | medium | mitigate | `count` is authoritative for full/empty; wrap test reads values back in order; zero-init means empty | closed |
| T-03-31 | Spoofing | CRC-16 as a trust signal | medium | mitigate | Header states "data-integrity … NOT authentication, NOT tamper detection"; standard check value pinned in the suite | closed |
| T-03-32 | Tampering | hex output buffer on rejected input | medium | mitigate | Every failure sets `*out_length = 0` and writes no byte; canary test proves the buffer is untouched | closed |
| T-03-SC (03-04) | Tampering | package installs | high | mitigate | No third-party CRC or codec library introduced | closed |
| T-03-33 | Elevation of Privilege | `lib/host` linked into firmware | high | mitigate | `host` only in `tests/lib_deps`; checker rejects `host` in any non-native environment | closed |
| T-03-34 | Tampering | fake buffers (`mode`, `level`, `buffer`, `lines`) | medium | mitigate | Named bound constants; over-bound requests return `PORT_ERR_INVALID_ARG` or increment `dropped`; each bound has a named test | closed |
| T-03-SC (03-05) | Tampering | package installs | high | mitigate | Plan installs nothing; Unity remains pinned by 03-01 | closed |
| T-03-35 | Tampering | `gpio_config_t` construction, pin guard, level mapping | high | mitigate | Zero-initialised config; `pin >= 64` rejected before the `1ULL << pin` shift; errors mapped to `PORT_ERR_IO` | closed |
| T-03-36 | Information Disclosure | adapter public headers | medium | mitigate | Headers include only the matching `port` header; scan finds no `esp_err_t`, `gpio_num_t` or `esp_log_level_t` | closed |
| T-03-37 | Spoofing | Arduino log output compiled out | medium | mitigate | Adapter calls `log_printf` unconditionally; source assertion rejects `log_i`/`log_d`/`Serial` | closed |
| T-03-SC (03-06) | Tampering | package installs | high | mitigate | No new package; pinned `platformio/espressif32` 8.0.0 already cached | closed |
| T-03-38 | Tampering | `board_build.partitions` resolution | high | mitigate | One committed `partitions/default_16MB.csv`; both sections point at it; existence and normalization tests | closed |
| T-03-39 | Repudiation | dedicated deletion commit | medium | mitigate | Deletion is its own `chore(03)` commit; verify asserts subject, empty tree and empty index | closed |
| T-03-40 | Tampering | version single-source | low | mitigate | `library.json` is the only version site; verify rejects stale strings and version functions | closed |
| T-03-SC (03-07) | Tampering | package installs | high | mitigate | Plan installs nothing; no registry build | closed |
| T-03-41 | Information Disclosure | `os.walk` over `lib/**` with symlinks | high | mitigate | `followlinks=False`; `Path.resolve()` containment; `..` and absolute includes classified as escapes | closed |
| T-03-42 | Repudiation | empty or missing tree | high | mitigate | Missing `lib/` or zero-file scan raises `CheckError` (exit 2); real-tree test asserts PASS lines | closed |
| T-03-43 | Elevation of Privilege | `scripts/architecture/allowlist.json` | medium | mitigate | Empty by default; entry needs `path`, known `rule`, non-empty `reason`; stale entries fail; exit 2 on malformed input | closed |
| T-03-44 | Tampering | `pre-commit` hook invocation | low | mitigate | `language: system`, fixed `entry`, `pass_filenames: false`; list-form subprocess arguments only | closed |
| T-03-SC (03-08) | Tampering | package installs | high | mitigate | Checker is stdlib-only; hook reuses the pinned pre-commit runtime | closed |
| T-03-45 | Tampering | `tests/compile_commands.json` | high | mitigate | Every entry's compiler asserted host-only; include paths scanned for framework and toolchain tokens; framework fixture fails the build | closed |
| T-03-46 | Repudiation | 20-run digest | medium | mitigate | Per-line anchored matches; seven-suite and `failed=0` assertions; offline unit test pins the parser | closed |
| T-03-47 | Denial of Service | twenty sequential `pio test` runs | low | mitigate | One warm-up build and a 300-second timeout per run; `RUNS = 20` is not environment-overridable | closed |
| T-03-48 | Tampering | temporary fixture containment | medium | mitigate | Every fixture path resolved and asserted relative to the temporary root; `.pio` and `compile_commands.json` excluded on copy | closed |
| T-03-SC (03-09) | Tampering | package installs | high | mitigate | Both modules stdlib-only; Unity cached by the warm run | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

**Totals:** 34 threats, 34 closed, 0 open. No open threat is at or above the `high` block threshold.

---

## Accepted Risks Log

No accepted risks.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-24 | 34 | 34 | 0 | gsd-secure-phase orchestrator (Claude) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-24
