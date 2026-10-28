#include <stddef.h>

#include "blink_modes/blink_modes.h"

static uint32_t effective_period(const blink_modes_t *state)
{
    if (state->mode == BLINK_MODE_SYNC_FAST) {
        return state->config.fast_period_ms;
    }
    return state->config.slow_period_ms;
}

static bool led_a_on(const blink_modes_t *state)
{
    if (state == NULL || !state->ready) {
        return false;
    }
    return state->phase_on;
}

static bool led_b_on(const blink_modes_t *state)
{
    if (state == NULL || !state->ready) {
        return false;
    }
    if (state->mode == BLINK_MODE_SYNC_FAST) {
        return state->phase_on;
    }
    return !state->phase_on;
}

static port_status_t read_button(const port_gpio_t *gpio, uint8_t pin, bool previous_stable, bool *raw_high)
{
    port_gpio_level_t level = PORT_GPIO_HIGH;

    if (gpio->read(gpio->ctx, pin, &level) != PORT_OK) {
        /* Keep the last debounced level: a failed read must never fabricate a
           press edge. */
        *raw_high = previous_stable;
        return PORT_ERR_IO;
    }

    *raw_high = (level == PORT_GPIO_HIGH);
    return PORT_OK;
}

static port_status_t write_led(const port_gpio_t *gpio, uint8_t pin, bool on, bool *applied)
{
    if (*applied == on) {
        return PORT_OK;
    }
    if (gpio->write(gpio->ctx, pin, on ? PORT_GPIO_HIGH : PORT_GPIO_LOW) != PORT_OK) {
        return PORT_ERR_IO;
    }
    *applied = on;
    return PORT_OK;
}

port_status_t blink_modes_init(blink_modes_t *state, const blink_modes_config_t *config)
{
    if (state == NULL || config == NULL) {
        return PORT_ERR_INVALID_ARG;
    }

    state->config = *config;
    if (state->config.fast_period_ms == 0u) {
        state->config.fast_period_ms = BLINK_MODES_DEFAULT_FAST_PERIOD_MS;
    }
    if (state->config.slow_period_ms == 0u) {
        state->config.slow_period_ms = BLINK_MODES_DEFAULT_SLOW_PERIOD_MS;
    }
    if (state->config.debounce_ms == 0u) {
        state->config.debounce_ms = BLINK_MODES_DEFAULT_DEBOUNCE_MS;
    }

    state->mode = BLINK_MODE_SYNC_FAST;
    state->phase_since_ms = 0u;
    state->phase_on = true;

    /* Idle buttons read HIGH, so the first stable level is HIGH and a later
       LOW transition is the press edge. */
    state->external_debounce = (common_debounce_t){true, true, 0u};
    state->boot_debounce = (common_debounce_t){true, true, 0u};
    state->external_stable_prev = true;
    state->boot_stable_prev = true;

    state->applied_a_on = false;
    state->applied_b_on = false;
    state->outputs_applied = false;
    state->ready = true;
    return PORT_OK;
}

port_status_t blink_modes_update(blink_modes_t *state, const port_gpio_t *gpio, const port_time_t *time)
{
    port_status_t result = PORT_OK;
    bool external_raw_high;
    bool boot_raw_high;
    bool external_stable;
    bool boot_stable;
    bool external_pressed;
    bool boot_pressed;
    bool mode_changed = false;
    bool a_on;
    bool b_on;
    uint32_t now_ms;
    uint32_t period_ms;
    uint32_t elapsed_ms;
    uint32_t steps;

    if (state == NULL || gpio == NULL || time == NULL || !state->ready) {
        return PORT_ERR_INVALID_ARG;
    }
    if (gpio->read == NULL || gpio->write == NULL || time->now_ms == NULL) {
        return PORT_ERR_INVALID_ARG;
    }

    now_ms = port_time_now_ms(time);

    if (read_button(gpio, state->config.external_button_pin, state->external_stable_prev, &external_raw_high) !=
        PORT_OK) {
        result = PORT_ERR_IO;
    }
    if (read_button(gpio, state->config.boot_button_pin, state->boot_stable_prev, &boot_raw_high) != PORT_OK) {
        result = PORT_ERR_IO;
    }

    external_stable =
        common_debounce_update(&state->external_debounce, time, external_raw_high, state->config.debounce_ms);
    boot_stable = common_debounce_update(&state->boot_debounce, time, boot_raw_high, state->config.debounce_ms);

    external_pressed = state->external_stable_prev && !external_stable;
    boot_pressed = state->boot_stable_prev && !boot_stable;
    state->external_stable_prev = external_stable;
    state->boot_stable_prev = boot_stable;

    /* The external button is evaluated first and BOOT second, so BOOT wins a
       simultaneous edge and the outcome is deterministic. */
    if (external_pressed && state->mode != BLINK_MODE_SYNC_FAST) {
        state->mode = BLINK_MODE_SYNC_FAST;
        mode_changed = true;
    }
    if (boot_pressed && state->mode != BLINK_MODE_ALTERNATE_SLOW) {
        state->mode = BLINK_MODE_ALTERNATE_SLOW;
        mode_changed = true;
    }

    if (mode_changed) {
        state->phase_since_ms = now_ms;
        state->phase_on = true;
    }

    period_ms = effective_period(state);
    elapsed_ms = common_elapsed_ms(now_ms, state->phase_since_ms);
    if (elapsed_ms >= period_ms) {
        /* Advance whole periods, not one edge: a late poll keeps the parity
           correct instead of drifting behind the wall clock. */
        steps = elapsed_ms / period_ms;
        if ((steps & 1u) != 0u) {
            state->phase_on = !state->phase_on;
        }
        state->phase_since_ms += steps * period_ms;
    }

    a_on = led_a_on(state);
    b_on = led_b_on(state);

    if (write_led(gpio, state->config.led_a_pin, a_on, &state->applied_a_on) != PORT_OK) {
        result = PORT_ERR_IO;
    }
    if (write_led(gpio, state->config.led_b_pin, b_on, &state->applied_b_on) != PORT_OK) {
        result = PORT_ERR_IO;
    }
    if (result == PORT_OK) {
        state->outputs_applied = true;
    }

    return result;
}

blink_mode_t blink_modes_current(const blink_modes_t *state)
{
    if (state == NULL || !state->ready) {
        return BLINK_MODE_SYNC_FAST;
    }
    return state->mode;
}

bool blink_modes_led_a_on(const blink_modes_t *state)
{
    return led_a_on(state);
}

bool blink_modes_led_b_on(const blink_modes_t *state)
{
    return led_b_on(state);
}
