#include <stddef.h>

#include "pattern/pattern.h"

/* A table row stores the LED flags plus a rational hold, `base * num / den`.
   Every half-base hold divides a base of 100 or more, so no hold can round to
   zero, and the integer division is visible in one place. */
typedef struct pattern_step {
    bool led_a;
    bool led_b;
    bool led_c;
    uint8_t hold_num;
    uint8_t hold_den;
} pattern_step_t;

/* Alternating: A, B, A+C, B+C, one base each. Exactly one of `led_a` and
   `led_b` is active in every frame, and the third LED joins the second half. */
static const pattern_step_t ALTERNATING[] = {
    {true, false, false, 1u, 1u},
    {false, true, false, 1u, 1u},
    {true, false, true, 1u, 1u},
    {false, true, true, 1u, 1u},
};

/* Double flash: two short on-pulses per side, separated by a short gap and
   closed by a long gap. The second pulse of the B half carries the third LED. */
static const pattern_step_t DOUBLE_FLASH[] = {
    {true, false, false, 1u, 2u},
    {false, false, false, 1u, 2u},
    {true, false, false, 1u, 2u},
    {false, false, false, 1u, 1u},
    {false, true, false, 1u, 2u},
    {false, false, false, 1u, 2u},
    {false, true, true, 1u, 2u},
    {false, false, false, 1u, 1u},
};

/* Chase: one LED at a time at half base, then a half-base pause. */
static const pattern_step_t CHASE[] = {
    {true, false, false, 1u, 2u},
    {false, true, false, 1u, 2u},
    {false, false, true, 1u, 2u},
    {false, false, false, 1u, 2u},
};

/* Solid: one all-on frame held for four bases, so the mode occupies a cycle
   length comparable with the other three. */
static const pattern_step_t SOLID[] = {
    {true, true, true, 4u, 1u},
};

typedef struct pattern_table {
    const pattern_step_t *steps;
    size_t count;
} pattern_table_t;

/* An unknown mode is an empty table, which every caller reads as one all-off
   frame. Keeping the fallback in data, not in a branch, means a new mode is one
   table plus one switch arm. */
static pattern_table_t table_for(pattern_mode_t mode) {
    pattern_table_t table = {NULL, 0u};

    switch (mode) {
        case PATTERN_MODE_ALTERNATING:
            table.steps = ALTERNATING;
            table.count = sizeof(ALTERNATING) / sizeof(ALTERNATING[0]);
            break;
        case PATTERN_MODE_DOUBLE_FLASH:
            table.steps = DOUBLE_FLASH;
            table.count = sizeof(DOUBLE_FLASH) / sizeof(DOUBLE_FLASH[0]);
            break;
        case PATTERN_MODE_CHASE:
            table.steps = CHASE;
            table.count = sizeof(CHASE) / sizeof(CHASE[0]);
            break;
        case PATTERN_MODE_SOLID:
            table.steps = SOLID;
            table.count = sizeof(SOLID) / sizeof(SOLID[0]);
            break;
        default:
            break;
    }
    return table;
}

pattern_mode_t pattern_mode_next(pattern_mode_t mode) {
    switch (mode) {
        case PATTERN_MODE_ALTERNATING:
            return PATTERN_MODE_DOUBLE_FLASH;
        case PATTERN_MODE_DOUBLE_FLASH:
            return PATTERN_MODE_CHASE;
        case PATTERN_MODE_CHASE:
            return PATTERN_MODE_SOLID;
        case PATTERN_MODE_SOLID:
            return PATTERN_MODE_ALTERNATING;
        default:
            return PATTERN_MODE_ALTERNATING;
    }
}

size_t pattern_frame_count(pattern_mode_t mode) {
    pattern_table_t table = table_for(mode);

    return table.count == 0u ? 1u : table.count;
}

pattern_frame_t pattern_frame_at(pattern_mode_t mode, uint16_t step, uint16_t base_ms) {
    pattern_frame_t frame = {false, false, false, base_ms};
    pattern_table_t table = table_for(mode);

    if (table.count == 0u || (size_t)step >= table.count) {
        return frame;
    }

    frame.led_a = table.steps[step].led_a;
    frame.led_b = table.steps[step].led_b;
    frame.led_c = table.steps[step].led_c;
    frame.hold_ms = (uint16_t)(((uint32_t)base_ms * table.steps[step].hold_num) /
                               table.steps[step].hold_den);
    return frame;
}

size_t pattern_speed_count(void) {
    return 3u;
}

uint16_t pattern_speed_base_ms(size_t index) {
    switch (index) {
        case 0u:
            return 400u;
        case 1u:
            return 200u;
        case 2u:
            return 100u;
        default:
            return 400u;
    }
}
