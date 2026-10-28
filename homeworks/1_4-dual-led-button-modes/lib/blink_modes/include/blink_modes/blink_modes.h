#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "common/timing.h"
#include "port/gpio.h"
#include "port/status.h"
#include "port/time.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Pure mode-selection and blink schedule for the two-LED homework.

   The module owns no framework header and no clock: the caller passes the
   GPIO and time contracts, so the same code runs against the Arduino adapters
   and against the host fakes in [env:native].

   Two buttons are active LOW: the external button is wired to ground and uses
   the internal pull-up, while the on-board BOOT button relies on the
   DevKitC-1 external pull-up. A press is the stable HIGH-to-LOW edge, so a
   release never selects a mode. */

typedef enum blink_mode {
    BLINK_MODE_SYNC_FAST = 0,     /* Mode 1: both LEDs together, 200 ms period. */
    BLINK_MODE_ALTERNATE_SLOW = 1 /* Mode 2: LEDs alternate, 1000 ms period. */
} blink_mode_t;

#define BLINK_MODES_DEFAULT_FAST_PERIOD_MS 200u
#define BLINK_MODES_DEFAULT_SLOW_PERIOD_MS 1000u
#define BLINK_MODES_DEFAULT_DEBOUNCE_MS 20u

/* A zero period or zero debounce selects its default, so the update never
   divides by zero and the caller cannot accidentally disable the filter. */
typedef struct blink_modes_config {
    uint8_t led_a_pin;
    uint8_t led_b_pin;
    uint8_t external_button_pin;
    uint8_t boot_button_pin;
    uint32_t fast_period_ms;
    uint32_t slow_period_ms;
    uint32_t debounce_ms;
} blink_modes_config_t;

typedef struct blink_modes {
    blink_modes_config_t config;
    blink_mode_t mode;
    uint32_t phase_since_ms;
    bool phase_on;
    common_debounce_t external_debounce;
    common_debounce_t boot_debounce;
    bool external_stable_prev;
    bool boot_stable_prev;
    bool applied_a_on;
    bool applied_b_on;
    bool outputs_applied;
    bool ready;
} blink_modes_t;

/* Copies the configuration and selects mode 1. Returns PORT_ERR_INVALID_ARG
   for a NULL state or configuration. */
port_status_t blink_modes_init(blink_modes_t *state, const blink_modes_config_t *config);

/* Polls both buttons, applies a mode change, advances the blink phase and
   writes only the LED levels that changed. A failed read keeps the previous
   debounced level, and a failed write is retried on the next call; both are
   reported through PORT_ERR_IO while the schedule keeps running. */
port_status_t blink_modes_update(blink_modes_t *state, const port_gpio_t *gpio, const port_time_t *time);

blink_mode_t blink_modes_current(const blink_modes_t *state);

/* The intended schedule, not the last written level: a failed write is still
   retried, and the caller can inspect what the mode asks for. */
bool blink_modes_led_a_on(const blink_modes_t *state);
bool blink_modes_led_b_on(const blink_modes_t *state);

#ifdef __cplusplus
}
#endif
