/* Composition root for an ESP-IDF homework.

   The starter code drives one LED through the consumer-owned port contracts and
   the ESP-IDF adapters, so a target build compiles both the contract and the
   adapter. Replace the loop body with the assignment behaviour; keep the
   contracts and the adapter factories. */

#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include "espidf/gpio.h"
#include "espidf/log.h"
#include "port/gpio.h"
#include "port/log.h"

/* Must match the wiring recorded in assets/ and in the report. */
static const uint8_t LED_PIN = 2;

/* app_main is called by the FreeRTOS scheduler, which is C; the C++ entry point
   therefore needs C linkage or the symbol is mangled and never found. */
extern "C" void app_main(void) {
    /* Function-scope contracts: app_main outlives them for the life of the
       task, and passing them by pointer keeps library code free of globals. */
    port_gpio_t gpio = espidf_gpio_port();
    port_log_t logger = espidf_log_port();
    port_gpio_level_t level = PORT_GPIO_LOW;

    if (gpio.set_mode(gpio.ctx, LED_PIN, PORT_GPIO_OUTPUT) != PORT_OK) {
        port_log_write(&logger, PORT_LOG_ERROR, "LED pin configuration failed");
    } else {
        port_log_write(&logger, PORT_LOG_INFO, "LED pin configured as output");
    }

    for (;;) {
        level = (level == PORT_GPIO_LOW) ? PORT_GPIO_HIGH : PORT_GPIO_LOW;
        if (gpio.write(gpio.ctx, LED_PIN, level) != PORT_OK) {
            port_log_write(&logger, PORT_LOG_ERROR, "LED write failed");
        }
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
