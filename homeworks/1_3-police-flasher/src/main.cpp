/* Composition root for the police flasher homework.

   The pattern tables and the controller live in the homework-local `pattern`
   library, so the same sources compile for the ESP32-S3 target and for the
   native Unity suite. This file only builds the adapters and ticks the
   controller; it holds no pattern logic of its own. */

#include <Arduino.h>

#include "arduino/gpio.h"
#include "arduino/log.h"
#include "arduino/time.h"
#include "pattern/controller.h"
#include "pattern/pattern.h"
#include "port/gpio.h"
#include "port/log.h"
#include "port/status.h"
#include "port/time.h"

/* Must match the wiring recorded in assets/ and in the report. GPIO4 drives the
   anti-parallel pair through one 150 ohm resistor; GPIO6 drives the third LED;
   GPIO7 reads the button. GPIO5 exists only for the alternative three-LED
   profile. */
static const uint8_t LED_A_PIN = 4;
static const uint8_t LED_B_PIN = 5;
static const uint8_t LED_C_PIN = 6;
static const uint8_t BUTTON_PIN = 7;

/* File-scope storage is an Arduino composition-root necessity: setup() runs once
   and loop() runs forever, so the objects must outlive setup(). This is not the
   global mutable state that library code prohibits (ADR-0008): the controller is
   owned here and passed to the contract calls by pointer. */
static pattern_controller_t controller;
static port_gpio_t gpio;
static port_time_t clock_port;
static port_log_t logger;

void setup(void)
{
    const pattern_controller_config_t config = {LED_A_PIN, LED_B_PIN, LED_C_PIN, BUTTON_PIN, PATTERN_GPIO_SINGLE};
    port_status_t status;

    gpio = arduino_gpio_port();
    clock_port = arduino_time_port();
    logger = arduino_log_port();

    status = pattern_controller_init(&controller, &config, gpio, clock_port);
    pattern_controller_set_logger(&controller, logger);
    if (status == PORT_OK) {
        port_log_write(&logger, PORT_LOG_INFO, "pattern ready");
    } else {
        port_log_write(&logger, PORT_LOG_ERROR, "pattern init failed");
    }
}

void loop(void)
{
    pattern_controller_tick(&controller);
}
