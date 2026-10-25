#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "common/timing.h"
#include "pattern/pattern.h"
#include "port/gpio.h"
#include "port/status.h"
#include "port/time.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Button timing. A press must survive the debounce window before it counts, and
   a press held at least this long cycles the speed instead of the mode. */
#define PATTERN_CONTROLLER_DEBOUNCE_MS 30u
#define PATTERN_CONTROLLER_LONG_PRESS_MS 600u

typedef struct pattern_controller_config {
    uint8_t pin_a;
    uint8_t pin_b;
    uint8_t pin_c;
    uint8_t button_pin;
    pattern_gpio_profile_t profile;
} pattern_controller_config_t;

/* Last successfully applied state of one pin. `as_input` records the
   high-impedance off state, which the level enum cannot express; a pin leaving
   that state needs an explicit OUTPUT mode before the next write. */
typedef struct pattern_pin_output {
    bool applied;
    bool as_input;
    port_gpio_level_t level;
} pattern_pin_output_t;

typedef struct pattern_controller {
    pattern_controller_config_t config;
    port_gpio_t gpio;
    port_time_t time;
    common_debounce_t debounce;
    pattern_mode_t mode;
    size_t speed_index;
    uint16_t step_index;
    uint32_t step_started_ms;
    bool button_pressed;
    uint32_t press_started_ms;
    bool long_press_handled;
    pattern_pin_output_t output_a;
    pattern_pin_output_t output_b;
    pattern_pin_output_t output_c;
    bool ready;
    port_status_t status;
} pattern_controller_t;

/* Copies the ports and config, configures the pins the profile needs, applies
   frame 0, and returns the first failing status. A NULL argument or a missing
   callback is PORT_ERR_INVALID_ARG. */
port_status_t pattern_controller_init(pattern_controller_t *controller,
                                      const pattern_controller_config_t *config,
                                      port_gpio_t gpio, port_time_t time);

/* One non-blocking step: debounce the button, act on a short or long press,
   advance at most one frame, and apply the changed outputs. A NULL or unready
   controller is a no-op. */
void pattern_controller_tick(pattern_controller_t *controller);

pattern_mode_t pattern_controller_mode(const pattern_controller_t *controller);
uint16_t pattern_controller_base_ms(const pattern_controller_t *controller);
port_status_t pattern_controller_status(const pattern_controller_t *controller);

#ifdef __cplusplus
}
#endif
