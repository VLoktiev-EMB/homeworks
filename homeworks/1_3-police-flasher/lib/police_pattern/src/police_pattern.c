#include <stddef.h>

#include "common/timing.h"
#include "police_pattern.h"

/* One full pattern: a red double flash, a blue double flash, then three white
   strobe pulses and a pause. The trailing pause is long enough that the speed
   change at the cycle boundary is visible as a distinct cadence. */
typedef struct police_step {
    police_pair_state_t pair;
    bool white_on;
    uint32_t duration_ms;
} police_step_t;

static const police_step_t POLICE_STEPS[] = {
    {POLICE_PAIR_RED, false, 140u},  {POLICE_PAIR_OFF, false, 100u},  {POLICE_PAIR_RED, false, 140u},
    {POLICE_PAIR_OFF, false, 100u},  {POLICE_PAIR_BLUE, false, 140u}, {POLICE_PAIR_OFF, false, 100u},
    {POLICE_PAIR_BLUE, false, 140u}, {POLICE_PAIR_OFF, false, 380u},  {POLICE_PAIR_OFF, true, 70u},
    {POLICE_PAIR_OFF, false, 70u},   {POLICE_PAIR_OFF, true, 70u},    {POLICE_PAIR_OFF, false, 70u},
    {POLICE_PAIR_OFF, true, 70u},    {POLICE_PAIR_OFF, false, 620u},
};

#define POLICE_STEP_COUNT ((uint16_t)(sizeof(POLICE_STEPS) / sizeof(POLICE_STEPS[0])))

static uint32_t step_duration_ms(uint16_t step, bool slow)
{
    uint32_t duration = POLICE_STEPS[step].duration_ms;

    return slow ? duration * 2u : duration;
}

static void write_outputs(uint16_t step, police_outputs_t *outputs)
{
    outputs->pair = POLICE_STEPS[step].pair;
    outputs->white_on = POLICE_STEPS[step].white_on;
}

static void advance(police_pattern_t *pattern)
{
    pattern->step++;
    if (pattern->step >= POLICE_STEP_COUNT) {
        pattern->step = 0u;
        pattern->cycle++;
        pattern->slow = !pattern->slow;
    }
}

void police_pattern_init(police_pattern_t *pattern, uint32_t now_ms)
{
    if (pattern == NULL) {
        return;
    }

    pattern->step = 0u;
    pattern->step_started_ms = now_ms;
    pattern->cycle = 0u;
    pattern->slow = false;
}

bool police_pattern_update(police_pattern_t *pattern, uint32_t now_ms, police_outputs_t *outputs)
{
    bool advanced = false;
    uint16_t guard;

    if (pattern == NULL || outputs == NULL) {
        return false;
    }

    /* A stalled caller catches up at most one full pattern per call; the
       deadline advances by whole step durations, so the cadence never drifts
       by the polling period. */
    for (guard = 0u; guard < POLICE_STEP_COUNT; guard++) {
        uint32_t duration = step_duration_ms(pattern->step, pattern->slow);

        if (!common_timer_expired(now_ms, pattern->step_started_ms + duration)) {
            break;
        }
        pattern->step_started_ms += duration;
        advance(pattern);
        advanced = true;
    }

    write_outputs(pattern->step, outputs);
    return advanced;
}

uint32_t police_pattern_step_duration_ms(const police_pattern_t *pattern)
{
    if (pattern == NULL) {
        return 0u;
    }

    return step_duration_ms(pattern->step, pattern->slow);
}
