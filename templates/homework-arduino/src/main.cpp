/* Composition root for an Arduino homework.

   The starter code drives one LED through the consumer-owned port contracts and
   the Arduino adapters, so a target build compiles both the contract and the
   adapter. Replace the loop body with the assignment behaviour; keep the
   contracts and the adapter factories. */

#include <Arduino.h>

#include "arduino/gpio.h"
#include "arduino/log.h"
#include "port/gpio.h"
#include "port/log.h"

/* Must match the wiring recorded in assets/ and in the report. */
static const uint8_t LED_PIN = 2;

/* File-scope storage is an Arduino composition-root necessity: setup() runs once
   and loop() runs forever, so the contracts must outlive setup(). This is not
   the global mutable state that library code prohibits (ADR-0008): the
   instances are owned here and passed to the contract calls by pointer. */
static port_gpio_t gpio;
static port_log_t logger;
static port_gpio_level_t level = PORT_GPIO_LOW;

void setup(void)
{
    gpio = arduino_gpio_port();
    logger = arduino_log_port();

    if (gpio.set_mode(gpio.ctx, LED_PIN, PORT_GPIO_OUTPUT) != PORT_OK) {
        port_log_write(&logger, PORT_LOG_ERROR, "LED pin configuration failed");
    } else {
        port_log_write(&logger, PORT_LOG_INFO, "LED pin configured as output");
    }
}

void loop(void)
{
    level = (level == PORT_GPIO_LOW) ? PORT_GPIO_HIGH : PORT_GPIO_LOW;
    if (gpio.write(gpio.ctx, LED_PIN, level) != PORT_OK) {
        port_log_write(&logger, PORT_LOG_ERROR, "LED write failed");
    }
    delay(500);
}
