/* Composition root for the two-LED mode homework.

   The Arduino adapters are the only framework-aware objects here. The mode
   selection, debounce and blink schedule live in the homework-private
   `blink_modes` library, which is framework-free and covered by the native
   suite. */

#include <Arduino.h>

#include "arduino/gpio.h"
#include "arduino/log.h"
#include "arduino/time.h"
#include "blink_modes/blink_modes.h"
#include "port/gpio.h"
#include "port/log.h"
#include "port/time.h"

/* Must match the wiring recorded in assets/diagram.json and in the report. */
static const uint8_t LED_A_PIN = 15;
static const uint8_t LED_B_PIN = 16;
static const uint8_t EXTERNAL_BUTTON_PIN = 21;
static const uint8_t BOOT_BUTTON_PIN = 0;

/* File-scope storage is an Arduino composition-root necessity: setup() runs
   once and loop() runs forever, so the borrowed contract views and the mode
   state must outlive setup(). The library owns no global of its own. */
static port_gpio_t gpio;
static port_log_t logger;
static port_time_t clock_port;
static blink_modes_t blink;
static blink_mode_t last_mode = BLINK_MODE_SYNC_FAST;
static bool fault_reported = false;

static bool configure_pin(uint8_t pin, port_gpio_mode_t mode, const char *failure_message)
{
    if (gpio.set_mode(gpio.ctx, pin, mode) != PORT_OK) {
        port_log_write(&logger, PORT_LOG_ERROR, failure_message);
        return false;
    }
    return true;
}

void setup(void)
{
    blink_modes_config_t config;

    gpio = arduino_gpio_port();
    logger = arduino_log_port();
    clock_port = arduino_time_port();

    configure_pin(LED_A_PIN, PORT_GPIO_OUTPUT, "LED A pin configuration failed");
    configure_pin(LED_B_PIN, PORT_GPIO_OUTPUT, "LED B pin configuration failed");
    configure_pin(EXTERNAL_BUTTON_PIN, PORT_GPIO_INPUT_PULLUP, "External button pin configuration failed");
    /* GPIO0: the DevKitC-1 carries the external pull-up, so INPUT is correct.
       pinMode(INPUT) disables the chip-internal pull-up. */
    configure_pin(BOOT_BUTTON_PIN, PORT_GPIO_INPUT, "BOOT button pin configuration failed");

    config.led_a_pin = LED_A_PIN;
    config.led_b_pin = LED_B_PIN;
    config.external_button_pin = EXTERNAL_BUTTON_PIN;
    config.boot_button_pin = BOOT_BUTTON_PIN;
    config.fast_period_ms = BLINK_MODES_DEFAULT_FAST_PERIOD_MS;
    config.slow_period_ms = BLINK_MODES_DEFAULT_SLOW_PERIOD_MS;
    config.debounce_ms = BLINK_MODES_DEFAULT_DEBOUNCE_MS;

    if (blink_modes_init(&blink, &config) != PORT_OK) {
        port_log_write(&logger, PORT_LOG_ERROR, "Blink mode state initialisation failed");
        return;
    }

    last_mode = blink_modes_current(&blink);
    port_log_write(&logger, PORT_LOG_INFO, "Mode 1 selected at startup: both LEDs, 200 ms");
}

void loop(void)
{
    port_status_t status;
    blink_mode_t mode;

    status = blink_modes_update(&blink, &gpio, &clock_port);
    if (status != PORT_OK) {
        if (!fault_reported) {
            port_log_write(&logger, PORT_LOG_ERROR, "GPIO access failed; the blink schedule continues");
            fault_reported = true;
        }
    } else {
        fault_reported = false;
    }

    mode = blink_modes_current(&blink);
    if (mode != last_mode) {
        if (mode == BLINK_MODE_SYNC_FAST) {
            port_log_write(&logger, PORT_LOG_INFO, "Mode 1 selected: both LEDs, 200 ms");
        } else {
            port_log_write(&logger, PORT_LOG_INFO, "Mode 2 selected: alternating LEDs, 1000 ms");
        }
        last_mode = mode;
    }

    /* A one-millisecond yield, not the mode timing: it lets the idle task run
       while keeping input sampling far finer than the 20 ms debounce. */
    delay(1);
}
