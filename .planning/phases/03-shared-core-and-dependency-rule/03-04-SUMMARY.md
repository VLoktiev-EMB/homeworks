---
phase: 03-shared-core-and-dependency-rule
plan: 04
subsystem: shared-core
tags: [c11, ring-buffer, crc16, hex-codec, unity, allocation-free, framework-free]

# Dependency graph
requires:
  - phase: 03-shared-core-and-dependency-rule
    provides: "tests/ native PlatformIO project, port_time_t contract, Unity 2.6.1 pin (plan 03-01)"
provides:
  - "Caller-owned fixed-capacity byte ring buffer with defined uninitialised and concurrency semantics"
  - "CRC-16/CCITT-FALSE one-shot and incremental helpers pinned by the 0x29B1 check value"
  - "Capacity-checked hexadecimal encode/decode with a pinned *out_length = 0 failure contract"
  - "Three additional independent Unity suites in the shared native project"
affects: [03-02, 03-03, 03-05, 03-08, 03-09, 11]

actuals:
  tokens: 5959
  tasks: 3
  commits: 3
  plan_head_before: b035239026a43deea099ad0aa96639dd882bdc2e
  plan_head_after: 9a403f326973b21a629f89abc679cc94ffbb8c0e

tech-stack:
  added: []
  patterns:
    - "Every common module includes only its own header and C standard headers"
    - "Caller-owned storage guarded by a pointer/capacity pair, never an initialized flag"
    - "Pinned failure contracts validated before the first output byte is written"
    - "Prose disclaimers (integrity-not-security, not-ISR-safe) live beside the declaration they qualify"

key-files:
  created:
    - lib/common/include/common/ring_buffer.h
    - lib/common/src/ring_buffer.c
    - lib/common/include/common/crc.h
    - lib/common/src/crc.c
    - lib/common/include/common/hex.h
    - lib/common/src/hex.c
    - tests/test/test_common_ring_buffer/test_ring_buffer.c
    - tests/test/test_common_crc/test_crc.c
    - tests/test/test_common_hex/test_hex.c
  modified: []

key-decisions:
  - "The ring buffer uses `count` as the single authority for full and empty, so no slot is reserved as a sentinel and the full capacity is usable"
  - "A zero-initialised common_ring_buffer_t is defined as an empty buffer; the storage/capacity pair is the guard and no initialized flag exists"
  - "CRC continues from the unchanged input on a NULL pointer with non-zero length, because the signature cannot report an error and returning 0 would collide with a legitimate CRC"
  - "Hex decode validates every digit before writing any byte, which is what makes the no-output-on-failure canary test hold"
  - "Hex encode rejects a length whose doubled size would overflow size_t, rather than relying on the capacity comparison alone"

patterns-established:
  - "Header shell: #pragma once, C standard headers, extern \"C\" guard last"
  - "Source includes its own header first, then only what it needs"
  - "Failure paths set *out_length = 0 immediately, before any check that can fail"

requirements-completed: [ARCH-02]

coverage:
  - id: D1
    description: "Caller-owned ring buffer with ordered wrap, full/empty return values, and a defined uninitialised state"
    requirement: ARCH-02
    verification:
      - kind: unit
        ref: "tests/test/test_common_ring_buffer/test_ring_buffer.c#7 cases"
        status: pass
      - kind: automated
        ref: "python3 -c header assertions over lib/common/include/common/ring_buffer.h"
        status: pass
    human_judgment: false
  - id: D2
    description: "CRC-16/CCITT-FALSE one-shot and incremental helpers matching the standard check vector"
    requirement: ARCH-02
    verification:
      - kind: unit
        ref: "tests/test/test_common_crc/test_crc.c#test_crc16_check_value"
        status: pass
      - kind: automated
        ref: "python3 -c header assertions over lib/common/include/common/crc.h"
        status: pass
    human_judgment: false
  - id: D3
    description: "Hexadecimal encode/decode inverse for all 256 byte values with rejected input and an untouched buffer on failure"
    requirement: ARCH-02
    verification:
      - kind: unit
        ref: "tests/test/test_common_hex/test_hex.c#9 cases"
        status: pass
      - kind: automated
        ref: "python3 -c header assertions over lib/common/include/common/hex.h"
        status: pass
    human_judgment: false
  - id: D4
    description: "Prose claims beside the declarations: CRC is integrity not security, and the ring buffer is not ISR-safe"
    requirement: ARCH-02
    verification: []
    human_judgment: true
    rationale: "The automated checks prove the words are present, not that the disclaimer is strong enough to stop a reader treating CRC as a trust signal or the buffer as ISR-safe. Only review can judge that."

duration: 1 min
completed: 2026-10-24
status: complete
---

# Phase 03 Plan 04: Shared Core Primitives Summary

**A caller-owned ring buffer, CRC-16/CCITT-FALSE and capacity-checked hex codecs, each allocation-free, clock-free and pinned by its own Unity suite.**

## Performance

- **Duration:** 1 min
- **Started:** 2026-10-23T22:28:06Z
- **Completed:** 2026-10-23T22:29:35Z
- **Tasks:** 3
- **Files modified:** 9 (9 created, 0 modified)

## Accomplishments

- `pio test -d tests -e native` exits 0 with 40 Unity cases across five suites: 15 timing, 4 fake-clock, 7 ring-buffer, 5 CRC and 9 hex.
- The ring buffer is proven to wrap in order with no allocation, and a `{0}` struct is defined as empty rather than undefined: `count`/`capacity` return 0, `push`/`pop` return false, `clear` is a no-op.
- CRC-16/CCITT-FALSE reproduces the standard check value exactly — the nine ASCII bytes of `123456789` give `0x29B1` — and incremental updates agree with the one-shot form.
- Hex encode/decode round-trip every byte from `0x00` to `0xFF`; an odd length, a non-hex character or insufficient capacity all return false with `*out_length = 0` and a canary byte at `out[0]` unchanged.
- No new translation unit allocates, blocks, sleeps, reads a clock or includes a framework header; each includes only its own header.
- The repository Python gate stays green: `python3 -m unittest discover -s scripts/tests -v` reports 122 tests OK.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end ring buffer — caller-owned storage, wrap, full/empty, uninitialised safety** - `8788666` (feat)
2. **Task 2: CRC-16/CCITT-FALSE — check value, incremental update, integrity disclaimer** - `f7cde6c` (feat)
3. **Task 3: Hexadecimal codecs — pinned failure contract, capacity checks, boundary tests** - `9a403f3` (feat)

**Plan metadata:** committed after this file was written (docs: complete plan)

## Exact Signatures

```c
bool common_ring_buffer_init(common_ring_buffer_t *rb, uint8_t *storage, size_t capacity);
bool common_ring_buffer_push(common_ring_buffer_t *rb, uint8_t value);
bool common_ring_buffer_pop(common_ring_buffer_t *rb, uint8_t *value);
size_t common_ring_buffer_count(const common_ring_buffer_t *rb);
size_t common_ring_buffer_capacity(const common_ring_buffer_t *rb);
void common_ring_buffer_clear(common_ring_buffer_t *rb);

uint16_t common_crc16_update(uint16_t crc, const uint8_t *data, size_t length);
uint16_t common_crc16(const uint8_t *data, size_t length);

bool common_hex_encode(const uint8_t *data, size_t length, char *out, size_t out_size,
                       size_t *out_length);
bool common_hex_decode(const char *text, size_t length, uint8_t *out, size_t out_size,
                       size_t *out_length);
```

## Observed Contracts

- **CRC check value:** `common_crc16("123456789", 9) == 0x29B1`; empty input returns the initial value `0xFFFF`; a NULL pointer with non-zero length returns the unchanged input CRC.
- **Ring buffer full/empty:** `count` alone decides both. `head` is the next write index and `tail` the next read index, each taken modulo `capacity`. A buffer is usable only when `storage != NULL && capacity > 0`.
- **Ring buffer uninitialised convention:** a `{0}` struct is empty for every call; `init` rejects NULL storage and zero capacity and leaves the struct untouched.
- **Hex failure convention:** both functions set `*out_length = 0` on entry when the pointer is non-NULL and write no output byte until all validation has passed. Encode requires `out_size >= 2 * length + 1`; decode requires an even length and `out_size >= length / 2`.
- **Concurrency scope:** the ring buffer header states the type is single-threaded, not ISR-safe, not lock-free and not reentrant, and that a shared buffer needs a caller-supplied critical section.

## Named Test Cases

- `test_ring_buffer_starts_empty`, `test_ring_buffer_push_and_pop_order`, `test_ring_buffer_full_returns_false`, `test_ring_buffer_empty_returns_false`, `test_ring_buffer_wraps_without_allocation`, `test_ring_buffer_init_rejects_zero_capacity`, `test_ring_buffer_zero_initialised_is_safe`
- `test_crc16_check_value`, `test_crc16_empty_input_is_initial_value`, `test_crc16_update_matches_one_shot`, `test_crc16_null_with_length_is_unchanged`, `test_crc16_single_bit_change_differs`
- `test_hex_encode_known_bytes`, `test_hex_round_trip`, `test_hex_decode_accepts_uppercase`, `test_hex_decode_rejects_odd_length`, `test_hex_decode_rejects_non_hex_character`, `test_hex_encode_zero_length`, `test_hex_decode_zero_length`, `test_hex_insufficient_capacity_writes_nothing`, `test_hex_enough_capacity_is_required`

## Files Created/Modified

- `lib/common/include/common/ring_buffer.h` — struct, six declarations, uninitialised-state rule, ISR/concurrency note
- `lib/common/src/ring_buffer.c` — modular index arithmetic with `count` as the authority
- `lib/common/include/common/crc.h` — initial value, polynomial, NULL contract and integrity-only scope
- `lib/common/src/crc.c` — bitwise CRC with no table
- `lib/common/include/common/hex.h` — capacity rules and the pinned failure contract
- `lib/common/src/hex.c` — lowercase encode and validate-then-write decode
- `tests/test/test_common_ring_buffer/test_ring_buffer.c` — 7 cases
- `tests/test/test_common_crc/test_crc.c` — 5 cases
- `tests/test/test_common_hex/test_hex.c` — 9 cases

## Decisions Made

- Used `count` as the single full/empty authority instead of reserving one slot, so a four-byte buffer really stores four bytes and the wrap test reads all four back in order.
- Kept the "uninitialised is empty" rule in prose rather than adding an `initialized` flag; a flag can disagree with the pointer, and the pointer/capacity pair is already the guard.
- Chose the unchanged-input CRC contract for `data == NULL && length != 0`, rejecting the alternative of returning zero, which would silently collide with a legitimate CRC value.
- Validated every hex digit before writing any byte so the canary test asserts a real guarantee rather than an incidental one.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The plan-level `<verification>` line says "six suites green". This worktree's baseline contains two suites from plan 03-01, and this plan adds three, so a green run here shows five suites (40 cases). The sixth suite belongs to a sibling wave-2 plan and appears only after the wave merges; nothing in this plan is missing.
- No deviations, no auto-fixes and no authentication gates. A transient sandbox network denial during the first PlatformIO run did not affect the build or the result.

## User Setup Required

None - no external service configuration required.

## Threat Surface

All four threats in the plan's register are mitigated as designed: `count`-authoritative index arithmetic with an ordered wrap test (T-03-30), the check value pinned so the polynomial cannot drift and the integrity-only disclaimer in the header (T-03-31), failure paths that write nothing and a canary test proving it (T-03-32), and no package installed at all (T-03-SC). No new surface beyond the plan was introduced.

## Known Stubs

None.

## Next Phase Readiness

- The proven-minimum shared core is complete: `ring_buffer`, `timing`, `crc` and `hex`, each with its own deterministic suite and no framework dependency.
- The header shell, failure-contract and caller-owned-storage conventions are set for the remaining Phase 3 plans.
- Sibling plans still own the `port` contracts, host fakes, adapters, the architecture checker and the retirement of the Phase 2 stub headers/sources; this plan touched none of them.

---
*Phase: 03-shared-core-and-dependency-rule*
*Completed: 2026-10-24*

## Self-Check: PASSED

- All 9 declared files exist on disk.
- All three task commits (`8788666`, `f7cde6c`, `9a403f3`) are ancestors of HEAD.
- `pio test -d tests -e native`: 40 Unity cases across 5 suites, exit 0.
- `python3 -m unittest discover -s scripts/tests -v`: 122 tests OK.
- `git rev-list --count b035239..HEAD` measures 3 commits, matching the three tasks.
- Self-check verdict: PASSED.
