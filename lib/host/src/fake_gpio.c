#include <stddef.h>

#include "host/fake_gpio.h"

static port_status_t consume_forced_status(host_fake_gpio_t *fake) {
    port_status_t status = fake->forced_status;

    if (status != PORT_OK) {
        fake->forced_status = PORT_OK;
    }
    return status;
}

static port_status_t host_fake_set_mode(void *ctx, uint8_t pin, port_gpio_mode_t mode) {
    host_fake_gpio_t *fake = (host_fake_gpio_t *)ctx;
    port_status_t forced;

    if (fake == NULL || pin >= HOST_FAKE_GPIO_PINS) {
        return PORT_ERR_INVALID_ARG;
    }
    forced = consume_forced_status(fake);
    if (forced != PORT_OK) {
        return forced;
    }
    fake->mode[pin] = mode;
    fake->configured[pin] = true;
    return PORT_OK;
}

static port_status_t host_fake_write(void *ctx, uint8_t pin, port_gpio_level_t level) {
    host_fake_gpio_t *fake = (host_fake_gpio_t *)ctx;
    port_status_t forced;

    if (fake == NULL || pin >= HOST_FAKE_GPIO_PINS) {
        return PORT_ERR_INVALID_ARG;
    }
    forced = consume_forced_status(fake);
    if (forced != PORT_OK) {
        return forced;
    }
    fake->level[pin] = level;
    fake->configured[pin] = true;
    fake->writes++;
    return PORT_OK;
}

static port_status_t host_fake_read(void *ctx, uint8_t pin, port_gpio_level_t *level) {
    host_fake_gpio_t *fake = (host_fake_gpio_t *)ctx;
    port_status_t forced;

    if (fake == NULL || level == NULL || pin >= HOST_FAKE_GPIO_PINS) {
        return PORT_ERR_INVALID_ARG;
    }
    forced = consume_forced_status(fake);
    if (forced != PORT_OK) {
        return forced;
    }
    *level = fake->level[pin];
    fake->reads++;
    return PORT_OK;
}

void host_fake_gpio_reset(host_fake_gpio_t *fake) {
    size_t index;

    if (fake == NULL) {
        return;
    }
    for (index = 0; index < HOST_FAKE_GPIO_PINS; ++index) {
        fake->mode[index] = PORT_GPIO_INPUT;
        fake->level[index] = PORT_GPIO_LOW;
        fake->configured[index] = false;
    }
    fake->forced_status = PORT_OK;
    fake->writes = 0;
    fake->reads = 0;
}

void host_fake_gpio_fail_next(host_fake_gpio_t *fake, port_status_t status) {
    if (fake == NULL) {
        return;
    }
    fake->forced_status = status;
}

port_gpio_t host_fake_gpio_port(host_fake_gpio_t *fake) {
    port_gpio_t port = {host_fake_set_mode, host_fake_write, host_fake_read, fake};

    return port;
}
