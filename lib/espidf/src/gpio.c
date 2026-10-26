#include <stdint.h>

#include "driver/gpio.h"
#include "esp_err.h"

#include "espidf/gpio.h"

static port_status_t map_esp_err(esp_err_t err)
{
    if (err == ESP_OK) {
        return PORT_OK;
    }
    return PORT_ERR_IO;
}

static port_status_t espidf_set_mode(void *ctx, uint8_t pin, port_gpio_mode_t mode)
{
    (void)ctx;

    /* The pin mask shifts `1ULL` by the pin number, so a value at or above 64
     would be undefined behaviour. Reject it before the shift. */
    if (pin >= 64) {
        return PORT_ERR_INVALID_ARG;
    }

    gpio_config_t config = {0};
    config.pin_bit_mask = (1ULL << pin);
    config.pull_up_en = GPIO_PULLUP_DISABLE;
    config.pull_down_en = GPIO_PULLDOWN_DISABLE;
    config.intr_type = GPIO_INTR_DISABLE;

    switch (mode) {
    case PORT_GPIO_INPUT:
        config.mode = GPIO_MODE_INPUT;
        break;
    case PORT_GPIO_OUTPUT:
        config.mode = GPIO_MODE_OUTPUT;
        break;
    case PORT_GPIO_INPUT_PULLUP:
        config.mode = GPIO_MODE_INPUT;
        config.pull_up_en = GPIO_PULLUP_ENABLE;
        break;
    default:
        return PORT_ERR_INVALID_ARG;
    }

    return map_esp_err(gpio_config(&config));
}

static port_status_t espidf_write(void *ctx, uint8_t pin, port_gpio_level_t level)
{
    (void)ctx;

    if (pin >= 64) {
        return PORT_ERR_INVALID_ARG;
    }

    if (level != PORT_GPIO_LOW && level != PORT_GPIO_HIGH) {
        return PORT_ERR_INVALID_ARG;
    }

    return map_esp_err(gpio_set_level((gpio_num_t)pin, (uint32_t)level));
}

static port_status_t espidf_read(void *ctx, uint8_t pin, port_gpio_level_t *level)
{
    (void)ctx;

    if (pin >= 64) {
        return PORT_ERR_INVALID_ARG;
    }

    if (level == NULL) {
        return PORT_ERR_INVALID_ARG;
    }

    /* gpio_get_level returns a level, not an error code, so there is nothing to
     map here. */
    *level = gpio_get_level((gpio_num_t)pin) == 1 ? PORT_GPIO_HIGH : PORT_GPIO_LOW;
    return PORT_OK;
}

port_gpio_t espidf_gpio_port(void)
{
    port_gpio_t port = {espidf_set_mode, espidf_write, espidf_read, NULL};
    return port;
}
