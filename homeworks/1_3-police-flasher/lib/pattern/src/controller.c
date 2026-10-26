#include <stddef.h>

#include "pattern/controller.h"

/* Keep the first failure of a tick or of init: a later successful call must not
   hide the operation that actually failed. */
static port_status_t first_failure(port_status_t current, port_status_t result)
{
    if (current != PORT_OK) {
        return current;
    }
    return result;
}

/* Apply one pin only when the desired state differs from the last successfully
   applied one. A failed mode change or write leaves the stored state untouched,
   so the next tick retries the same desired value. */
static port_status_t apply_pin(pattern_controller_t *controller, uint8_t pin, pattern_pin_output_t *state,
                               bool as_input, port_gpio_level_t level)
{
    port_status_t status;

    if (as_input) {
        if (state->applied && state->as_input) {
            return PORT_OK;
        }
        status = controller->gpio.set_mode(controller->gpio.ctx, pin, PORT_GPIO_INPUT);
        if (status != PORT_OK) {
            return status;
        }
        state->applied = true;
        state->as_input = true;
        return PORT_OK;
    }

    if (!state->applied || state->as_input) {
        /* Leaving the high-impedance state needs an explicit OUTPUT mode. */
        status = controller->gpio.set_mode(controller->gpio.ctx, pin, PORT_GPIO_OUTPUT);
        if (status != PORT_OK) {
            return status;
        }
        state->applied = true;
        state->as_input = false;
        status = controller->gpio.write(controller->gpio.ctx, pin, level);
        if (status != PORT_OK) {
            return status;
        }
        state->level = level;
        return PORT_OK;
    }

    if (state->level == level) {
        return PORT_OK;
    }
    status = controller->gpio.write(controller->gpio.ctx, pin, level);
    if (status != PORT_OK) {
        /* The stored level stays behind so the next tick retries. */
        return status;
    }
    state->level = level;
    return PORT_OK;
}

static port_status_t apply_frame(pattern_controller_t *controller)
{
    uint16_t base_ms = pattern_speed_base_ms(controller->speed_index);
    pattern_frame_t frame = pattern_frame_at(controller->mode, controller->step_index, base_ms);
    port_status_t status = PORT_OK;

    if (controller->config.profile == PATTERN_GPIO_THREE_LEDS) {
        status = first_failure(status, apply_pin(controller, controller->config.pin_a, &controller->output_a, false,
                                                 frame.led_a ? PORT_GPIO_HIGH : PORT_GPIO_LOW));
        status = first_failure(status, apply_pin(controller, controller->config.pin_b, &controller->output_b, false,
                                                 frame.led_b ? PORT_GPIO_HIGH : PORT_GPIO_LOW));
    } else {
        /* Single pin: `led_a` wins, `led_b` drives LOW, and neither leaves the
           pin high-impedance. SOLID is all-on, so pin A stays HIGH there. */
        bool as_input = !frame.led_a && !frame.led_b;
        port_gpio_level_t level = frame.led_a ? PORT_GPIO_HIGH : PORT_GPIO_LOW;

        status = first_failure(status,
                               apply_pin(controller, controller->config.pin_a, &controller->output_a, as_input, level));
    }
    status = first_failure(status, apply_pin(controller, controller->config.pin_c, &controller->output_c, false,
                                             frame.led_c ? PORT_GPIO_HIGH : PORT_GPIO_LOW));
    return status;
}

static void reset_schedule(pattern_controller_t *controller, uint32_t now_ms)
{
    controller->step_index = 0u;
    controller->step_started_ms = now_ms;
}

static void advance_schedule(pattern_controller_t *controller, uint32_t now_ms)
{
    uint16_t base_ms = pattern_speed_base_ms(controller->speed_index);
    uint16_t hold_ms = pattern_frame_at(controller->mode, controller->step_index, base_ms).hold_ms;
    uint32_t elapsed_ms = common_elapsed_ms(now_ms, controller->step_started_ms);

    if ((int32_t)elapsed_ms < 0) {
        /* A backwards clock jump must not look like an overdue frame. */
        controller->step_started_ms = now_ms;
        return;
    }
    if (elapsed_ms < (uint32_t)hold_ms) {
        return;
    }

    /* Exactly one frame per tick: a late loop must not catch up in a burst. */
    controller->step_index = (uint16_t)((controller->step_index + 1u) % pattern_frame_count(controller->mode));
    controller->step_started_ms += (uint32_t)hold_ms;
    hold_ms = pattern_frame_at(controller->mode, controller->step_index, base_ms).hold_ms;
    if ((int32_t)common_elapsed_ms(now_ms, controller->step_started_ms) > (int32_t)hold_ms) {
        /* Still more than one hold behind after the single advance: resync so
           the schedule cannot drift or burst. */
        controller->step_started_ms = now_ms;
    }
}

port_status_t pattern_controller_init(pattern_controller_t *controller, const pattern_controller_config_t *config,
                                      port_gpio_t gpio, port_time_t time)
{
    port_status_t status = PORT_OK;

    if (controller == NULL || config == NULL) {
        return PORT_ERR_INVALID_ARG;
    }
    if (gpio.set_mode == NULL || gpio.write == NULL || gpio.read == NULL || time.now_ms == NULL) {
        return PORT_ERR_INVALID_ARG;
    }

    controller->config = *config;
    controller->gpio = gpio;
    controller->time = time;
    controller->debounce.stable = false;
    controller->debounce.candidate = false;
    controller->debounce.candidate_since_ms = 0u;
    controller->mode = PATTERN_MODE_ALTERNATING;
    controller->speed_index = 0u;
    controller->step_index = 0u;
    controller->button_pressed = false;
    controller->press_started_ms = 0u;
    controller->long_press_handled = false;
    controller->output_a.applied = false;
    controller->output_a.as_input = false;
    controller->output_a.level = PORT_GPIO_LOW;
    controller->output_b.applied = false;
    controller->output_b.as_input = false;
    controller->output_b.level = PORT_GPIO_LOW;
    controller->output_c.applied = false;
    controller->output_c.as_input = false;
    controller->output_c.level = PORT_GPIO_LOW;
    controller->ready = false;
    controller->status = PORT_OK;

    status = first_failure(status, gpio.set_mode(gpio.ctx, config->pin_a, PORT_GPIO_OUTPUT));
    if (config->profile == PATTERN_GPIO_THREE_LEDS) {
        /* Pin B exists only in the three-LED profile; leaving it untouched in
           the single-GPIO profile is the documented wiring. */
        status = first_failure(status, gpio.set_mode(gpio.ctx, config->pin_b, PORT_GPIO_OUTPUT));
    }
    status = first_failure(status, gpio.set_mode(gpio.ctx, config->pin_c, PORT_GPIO_OUTPUT));
    status = first_failure(status, gpio.set_mode(gpio.ctx, config->button_pin, PORT_GPIO_INPUT_PULLUP));

    controller->step_started_ms = port_time_now_ms(&controller->time);
    status = first_failure(status, apply_frame(controller));

    controller->status = status;
    /* Runtime failures never make the controller inert; the status reports
       them and the next tick retries. */
    controller->ready = true;
    return status;
}

void pattern_controller_tick(pattern_controller_t *controller)
{
    port_status_t tick_status = PORT_OK;
    port_status_t read_status;
    port_gpio_level_t level = PORT_GPIO_HIGH;
    bool raw_pressed;
    bool now_pressed;
    bool was_pressed;
    bool changed_output = false;
    uint32_t now_ms;

    if (controller == NULL || !controller->ready) {
        return;
    }
    if (controller->time.now_ms == NULL) {
        return;
    }

    now_ms = port_time_now_ms(&controller->time);

    /* Output first: this keeps an injected one-shot failure deterministic — a
       pending write consumes it before the button read does. */
    advance_schedule(controller, now_ms);
    tick_status = first_failure(tick_status, apply_frame(controller));

    was_pressed = controller->button_pressed;
    now_pressed = was_pressed;
    read_status = controller->gpio.read(controller->gpio.ctx, controller->config.button_pin, &level);
    if (read_status == PORT_OK) {
        raw_pressed = (level == PORT_GPIO_LOW);
        now_pressed = common_debounce_update(&controller->debounce, &controller->time, raw_pressed,
                                             PATTERN_CONTROLLER_DEBOUNCE_MS);
    } else {
        /* A failed read keeps the previous stable level. */
        tick_status = first_failure(tick_status, read_status);
    }

    if (now_pressed && !was_pressed) {
        controller->press_started_ms = now_ms;
        controller->long_press_handled = false;
    }
    if (now_pressed && !controller->long_press_handled &&
        (int32_t)common_elapsed_ms(now_ms, controller->press_started_ms) >= (int32_t)PATTERN_CONTROLLER_LONG_PRESS_MS) {
        controller->speed_index = (controller->speed_index + 1u) % pattern_speed_count();
        controller->long_press_handled = true;
        reset_schedule(controller, now_ms);
        changed_output = true;
    }
    if (!now_pressed && was_pressed) {
        if (!controller->long_press_handled) {
            controller->mode = pattern_mode_next(controller->mode);
            reset_schedule(controller, now_ms);
            changed_output = true;
        }
        /* The release of a long press must not also count as a short press. */
        controller->long_press_handled = false;
    }
    controller->button_pressed = now_pressed;

    if (changed_output) {
        /* A mode or speed change takes effect on this tick, not the next one. */
        tick_status = first_failure(tick_status, apply_frame(controller));
    }
    controller->status = tick_status;
}

pattern_mode_t pattern_controller_mode(const pattern_controller_t *controller)
{
    if (controller == NULL) {
        return PATTERN_MODE_ALTERNATING;
    }
    return controller->mode;
}

uint16_t pattern_controller_base_ms(const pattern_controller_t *controller)
{
    if (controller == NULL) {
        return 400u;
    }
    return pattern_speed_base_ms(controller->speed_index);
}

port_status_t pattern_controller_status(const pattern_controller_t *controller)
{
    if (controller == NULL) {
        return PORT_ERR_INVALID_ARG;
    }
    return controller->status;
}
