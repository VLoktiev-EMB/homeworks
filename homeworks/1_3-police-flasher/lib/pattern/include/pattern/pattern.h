#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Pure police-flasher frame tables.

   This module owns no hardware and no clock. A frame is a snapshot of three LED
   flags plus the hold time at which the caller should sample the next one, so
   the native suite can pin every step without an adapter. The tables are data,
   not control flow: equal holds stay distinct frames and play in index order. */

typedef enum pattern_mode {
    PATTERN_MODE_ALTERNATING = 0,
    PATTERN_MODE_DOUBLE_FLASH,
    PATTERN_MODE_CHASE,
    PATTERN_MODE_SOLID,
    PATTERN_MODE_COUNT
} pattern_mode_t;

/* Wiring profile. `PATTERN_GPIO_SINGLE` drives two anti-parallel LEDs from one
   pin; `PATTERN_GPIO_THREE_LEDS` drives one LED per pin. */
typedef enum pattern_gpio_profile { PATTERN_GPIO_THREE_LEDS = 0, PATTERN_GPIO_SINGLE = 1 } pattern_gpio_profile_t;

/* One step of a pattern. `hold_ms` is how long this step stays on screen. */
typedef struct pattern_frame {
    bool led_a;
    bool led_b;
    bool led_c;
    uint16_t hold_ms;
} pattern_frame_t;

/* The next mode in the fixed cycle; an invalid mode returns ALTERNATING. */
pattern_mode_t pattern_mode_next(pattern_mode_t mode);

/* Number of frames in `mode`; an invalid mode has one all-off frame. */
size_t pattern_frame_count(pattern_mode_t mode);

/* Frame `step` of `mode`, scaled from `base_ms`. An invalid mode or a step past
   the table returns an all-off frame with the caller's base hold. */
pattern_frame_t pattern_frame_at(pattern_mode_t mode, uint16_t step, uint16_t base_ms);

/* Number of selectable speeds and the base hold for speed `index`. */
size_t pattern_speed_count(void);
uint16_t pattern_speed_base_ms(size_t index);

#ifdef __cplusplus
}
#endif
