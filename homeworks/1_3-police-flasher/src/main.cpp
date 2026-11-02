/* Composition root for the police-flasher homework.

   The pure blink logic lives in lib/police_pattern and takes elapsed
   milliseconds from its caller. This file owns the framework instances, maps
   the resolved pattern step onto the two GPIOs, and polls the pattern once per
   millisecond.

   Wiring (see assets/diagram.json and the report):
     - GPIO4 drives the red and blue pair in push-pull. OUTPUT + HIGH lights
       red (GPIO -> resistor -> LED -> GND); OUTPUT + LOW lights blue
       (3V3 -> resistor -> LED -> GPIO); INPUT releases the pin so both are
       off.
     - GPIO5 drives the white third LED active-high through its own resistor. */

#include <Arduino.h>

#include "arduino/gpio.h"
#include "arduino/log.h"
#include "arduino/time.h"
#include "police_pattern.h"
#include "port/gpio.h"
#include "port/log.h"
#include "port/time.h"

/* Must match the wiring recorded in assets/ and in the report. */
static const uint8_t PAIR_PIN = 4;
static const uint8_t WHITE_PIN = 5;

/* File-scope storage is an Arduino composition-root necessity: setup() runs
   once and loop() runs forever, so the contracts must outlive setup(). The
   instances are owned here and passed to the contract calls by pointer. */
static port_gpio_t gpio;
static port_log_t logger;
static port_time_t clock_port;
static police_pattern_t pattern;

static void report_status(const char *operation, port_status_t status)
{
    if (status != PORT_OK) {
        port_log_write(&logger, PORT_LOG_ERROR, operation);
    }
}

static void apply_outputs(const police_outputs_t *outputs)
{
    if (outputs == NULL) {
        return;
    }

    if (outputs->pair == POLICE_PAIR_RED) {
        report_status("pair pin mode failed", port_gpio_set_mode(&gpio, PAIR_PIN, PORT_GPIO_OUTPUT));
        report_status("red write failed", port_gpio_write(&gpio, PAIR_PIN, PORT_GPIO_HIGH));
    } else if (outputs->pair == POLICE_PAIR_BLUE) {
        report_status("pair pin mode failed", port_gpio_set_mode(&gpio, PAIR_PIN, PORT_GPIO_OUTPUT));
        report_status("blue write failed", port_gpio_write(&gpio, PAIR_PIN, PORT_GPIO_LOW));
    } else {
        report_status("pair pin release failed", port_gpio_set_mode(&gpio, PAIR_PIN, PORT_GPIO_INPUT));
    }

    report_status("white write failed",
                  port_gpio_write(&gpio, WHITE_PIN, outputs->white_on ? PORT_GPIO_HIGH : PORT_GPIO_LOW));
}

void setup(void)
{
    police_outputs_t outputs = {POLICE_PAIR_OFF, false};

    gpio = arduino_gpio_port();
    logger = arduino_log_port();
    clock_port = arduino_time_port();

    report_status("white pin configuration failed", port_gpio_set_mode(&gpio, WHITE_PIN, PORT_GPIO_OUTPUT));
    report_status("white initial level failed", port_gpio_write(&gpio, WHITE_PIN, PORT_GPIO_LOW));
    report_status("pair pin release failed", port_gpio_set_mode(&gpio, PAIR_PIN, PORT_GPIO_INPUT));

    police_pattern_init(&pattern, port_time_now_ms(&clock_port));
    (void)police_pattern_update(&pattern, port_time_now_ms(&clock_port), &outputs);
    apply_outputs(&outputs);

    port_log_write(&logger, PORT_LOG_INFO, "police flasher started");
}

void loop(void)
{
    police_outputs_t outputs = {POLICE_PAIR_OFF, false};

    if (police_pattern_update(&pattern, port_time_now_ms(&clock_port), &outputs)) {
        apply_outputs(&outputs);
    }

    delay(1);
}
