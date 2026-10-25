/* Composition root for the police flasher homework.

   The frame tables live in the homework-local `pattern` library, so the same
   sources compile for the ESP32-S3 target and for the native Unity suite. This
   file only builds the adapters, owns the schedule state Arduino requires to
   outlive setup(), and writes the levels the table describes. */

#include <Arduino.h>

#include "arduino/gpio.h"
#include "arduino/log.h"
#include "arduino/time.h"
#include "common/timing.h"
#include "pattern/pattern.h"
#include "port/gpio.h"
#include "port/log.h"
#include "port/status.h"
#include "port/time.h"

/* Must match the wiring recorded in assets/ and in the report. GPIO4 drives the
   anti-parallel pair through one 150 ohm resistor; GPIO6 drives the third LED.
   GPIO5 exists only for the alternative three-LED profile. */
static const uint8_t LED_A_PIN = 4;
static const uint8_t LED_B_PIN = 5;
static const uint8_t LED_C_PIN = 6;
static const uint8_t BUTTON_PIN = 7;

static const uint16_t BASE_MS = 400u;

/* File-scope storage is an Arduino composition-root necessity: setup() runs once
   and loop() runs forever, so the contracts must outlive setup(). This is not
   the global mutable state that library code prohibits (ADR-0008): the
   instances are owned here and passed to the contract calls by pointer. */
static port_gpio_t gpio;
static port_time_t clock_port;
static port_log_t logger;
static pattern_frame_t frame;
static uint32_t step_started_ms;
static uint16_t step_index;

/* Single-GPIO profile: led_a wins, led_b drives LOW, and an all-off frame leaves
   the pin high-impedance. The adapter rejects PORT_GPIO_INPUT as a write level,
   so the off state is a mode change rather than a write. */
static void apply_frame(void) {
    if (!frame.led_a && !frame.led_b) {
        (void)gpio.set_mode(gpio.ctx, LED_A_PIN, PORT_GPIO_INPUT);
    } else {
        (void)gpio.set_mode(gpio.ctx, LED_A_PIN, PORT_GPIO_OUTPUT);
        (void)gpio.write(gpio.ctx, LED_A_PIN,
                         frame.led_a ? PORT_GPIO_HIGH : PORT_GPIO_LOW);
    }
    (void)gpio.set_mode(gpio.ctx, LED_C_PIN, PORT_GPIO_OUTPUT);
    (void)gpio.write(gpio.ctx, LED_C_PIN,
                     frame.led_c ? PORT_GPIO_HIGH : PORT_GPIO_LOW);
}

void setup(void) {
    port_status_t status;

    gpio = arduino_gpio_port();
    clock_port = arduino_time_port();
    logger = arduino_log_port();

    status = gpio.set_mode(gpio.ctx, LED_A_PIN, PORT_GPIO_OUTPUT);
    if (status == PORT_OK) {
        status = gpio.set_mode(gpio.ctx, LED_C_PIN, PORT_GPIO_OUTPUT);
    }
    if (status == PORT_OK) {
        status = gpio.set_mode(gpio.ctx, BUTTON_PIN, PORT_GPIO_INPUT_PULLUP);
    }

    step_index = 0u;
    step_started_ms = port_time_now_ms(&clock_port);
    frame = pattern_frame_at(PATTERN_MODE_ALTERNATING, step_index, BASE_MS);
    apply_frame();

    if (status == PORT_OK) {
        port_log_write(&logger, PORT_LOG_INFO, "pattern ready");
    } else {
        port_log_write(&logger, PORT_LOG_ERROR, "pattern init failed");
    }
}

void loop(void) {
    uint32_t now_ms = port_time_now_ms(&clock_port);

    /* A signed view of the unsigned difference treats a backwards clock jump as
       "not yet", while a forward wrap still reads as a small positive elapsed. */
    if ((int32_t)common_elapsed_ms(now_ms, step_started_ms) >= (int32_t)frame.hold_ms) {
        step_index = (uint16_t)((step_index + 1u) %
                                pattern_frame_count(PATTERN_MODE_ALTERNATING));
        step_started_ms += frame.hold_ms;
        frame = pattern_frame_at(PATTERN_MODE_ALTERNATING, step_index, BASE_MS);
        /* A stall longer than one hold must not make the next loop burst. */
        if ((int32_t)common_elapsed_ms(now_ms, step_started_ms) >
            (int32_t)frame.hold_ms) {
            step_started_ms = now_ms;
        }
        apply_frame();
    }
}
