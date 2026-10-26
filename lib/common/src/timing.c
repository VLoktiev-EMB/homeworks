#include <stddef.h>

#include "common/timing.h"

uint32_t common_elapsed_ms(uint32_t now_ms, uint32_t since_ms)
{
    return now_ms - since_ms;
}

bool common_timer_expired(uint32_t now_ms, uint32_t deadline_ms)
{
    /* Signed 32-bit difference: at most 2^31 - 1 ms (about 24.85 days) ahead.
       A deadline farther away wraps negative and therefore reads as expired. */
    return (int32_t)(now_ms - deadline_ms) >= 0;
}

bool common_debounce_update(common_debounce_t *state, const port_time_t *time, bool raw_input, uint32_t stable_ms)
{
    uint32_t now_ms;

    if (state == NULL) {
        return false;
    }
    if (time == NULL || time->now_ms == NULL) {
        return state->stable;
    }

    now_ms = port_time_now_ms(time);

    if (raw_input != state->candidate) {
        state->candidate = raw_input;
        state->candidate_since_ms = now_ms;
    }

    if (state->candidate != state->stable && common_elapsed_ms(now_ms, state->candidate_since_ms) >= stable_ms) {
        state->stable = state->candidate;
    }

    return state->stable;
}
