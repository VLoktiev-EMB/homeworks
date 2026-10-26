#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "port/time.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Framework-free timing helpers.

   This module never reads a clock: elapsed time and expiry are computed from
   values the caller supplies, and the debounce helper borrows a `port_time_t`
   from its caller. That keeps lib/common free of a framework header and makes
   every result reproducible under a fake clock.

   Expiry horizon: `common_timer_expired` decides by the sign of the 32-bit
   difference now - deadline. That detects at most 2^31 - 1 ms (about 24.85
   days) into the future; a deadline farther away wraps to a negative
   difference and therefore reads as already expired. It is NOT a 49.7-day
   horizon. */

/* Three fields, not two: a `stable` / `last_change_ms` pair cannot distinguish
   "no pending change" from "a change that began at time zero", so the next
   transition would latch immediately. `candidate` names the level being
   observed and `candidate_since_ms` is the moment that candidacy began. */
typedef struct common_debounce {
    bool stable;
    bool candidate;
    uint32_t candidate_since_ms;
} common_debounce_t;

/* Unsigned subtraction: correct across the 32-bit wrap. */
uint32_t common_elapsed_ms(uint32_t now_ms, uint32_t since_ms);

/* Signed-difference expiry; see the horizon note above. */
bool common_timer_expired(uint32_t now_ms, uint32_t deadline_ms);

/* Debounce `raw_input` against `stable_ms`, reading time through `time`.
   Returns the current stable level. A NULL state returns false; a NULL time
   pointer or NULL now_ms callback returns the state's unchanged stable level. */
bool common_debounce_update(common_debounce_t *state, const port_time_t *time, bool raw_input, uint32_t stable_ms);

#ifdef __cplusplus
}
#endif
