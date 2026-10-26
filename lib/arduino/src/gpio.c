#include <Arduino.h>

#include "arduino/gpio.h"

static port_status_t arduino_set_mode(void *ctx, uint8_t pin, port_gpio_mode_t mode)
{
    (void)ctx;
    uint8_t arduino_mode;

    switch (mode) {
    case PORT_GPIO_INPUT:
        arduino_mode = INPUT;
        break;
    case PORT_GPIO_OUTPUT:
        arduino_mode = OUTPUT;
        break;
    case PORT_GPIO_INPUT_PULLUP:
        arduino_mode = INPUT_PULLUP;
        break;
    default:
        return PORT_ERR_INVALID_ARG;
    }

    pinMode((uint8_t)pin, arduino_mode);
    return PORT_OK;
}

static port_status_t arduino_write(void *ctx, uint8_t pin, port_gpio_level_t level)
{
    (void)ctx;
    uint8_t arduino_level;

    switch (level) {
    case PORT_GPIO_LOW:
        arduino_level = LOW;
        break;
    case PORT_GPIO_HIGH:
        arduino_level = HIGH;
        break;
    default:
        return PORT_ERR_INVALID_ARG;
    }

    digitalWrite((uint8_t)pin, arduino_level);
    return PORT_OK;
}

static port_status_t arduino_read(void *ctx, uint8_t pin, port_gpio_level_t *level)
{
    (void)ctx;

    if (level == NULL) {
        return PORT_ERR_INVALID_ARG;
    }

    *level = digitalRead((uint8_t)pin) == HIGH ? PORT_GPIO_HIGH : PORT_GPIO_LOW;
    return PORT_OK;
}

port_gpio_t arduino_gpio_port(void)
{
    port_gpio_t port = {arduino_set_mode, arduino_write, arduino_read, NULL};
    return port;
}
