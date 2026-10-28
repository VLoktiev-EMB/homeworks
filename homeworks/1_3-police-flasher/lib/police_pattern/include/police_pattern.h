#pragma once

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Framework-free police-flasher pattern.

   The red and blue LEDs share one push-pull GPIO: OUTPUT + HIGH lights red,
   OUTPUT + LOW lights blue, and INPUT (high impedance) turns both off. The
   white third LED has its own active-high GPIO.

   The pattern is a fixed step table. `police_pattern_update` consumes elapsed
   time supplied by the caller and never reads a clock, allocates, or blocks,
   so the same table runs unchanged on the target and under a native test.
   The cadence doubles on every full cycle, which makes the visible speed
   alternate between fast and slow. */

typedef enum police_pair_state { POLICE_PAIR_OFF = 0, POLICE_PAIR_RED, POLICE_PAIR_BLUE } police_pair_state_t;

/* One resolved pattern step. `pair` names which lamp the shared pin must
   light; `white_on` is the third LED's level. */
typedef struct police_outputs {
    police_pair_state_t pair;
    bool white_on;
} police_outputs_t;

/* Caller-owned progress. `step_started_ms` is the deadline base for the
   current step, `cycle` counts completed full patterns, and `slow` selects
   the doubled cadence. */
typedef struct police_pattern {
    uint16_t step;
    uint32_t step_started_ms;
    uint16_t cycle;
    bool slow;
} police_pattern_t;

/* Seed the pattern at `now_ms`; the first update before the first deadline
   reports the initial state without advancing. A NULL pattern is ignored. */
void police_pattern_init(police_pattern_t *pattern, uint32_t now_ms);

/* Advance every step whose deadline the caller's clock has passed, then write
   the resulting outputs. Returns true when at least one step advanced.
   A NULL pattern or NULL outputs leaves the call without effect and returns
   false; the outputs are otherwise always written, even when no step moved.
   The catch-up loop is bounded by one full pattern, so a long stall advances
   at most one cycle rather than spinning on a stale deadline. */
bool police_pattern_update(police_pattern_t *pattern, uint32_t now_ms, police_outputs_t *outputs);

/* Duration of the current step at the current speed. Exposed so a caller can
   log or test the cadence without copying the table; a NULL pattern returns
   zero. */
uint32_t police_pattern_step_duration_ms(const police_pattern_t *pattern);

#ifdef __cplusplus
}
#endif
