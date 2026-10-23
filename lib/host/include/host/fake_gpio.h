#pragma once

#include <stdbool.h>
#include <stddef.h>

#include "port/gpio.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Bounded, caller-owned GPIO recording double.

   Every pin state lives in a fixed array, so a write can never outgrow the
   test process. A pin at or above HOST_FAKE_GPIO_PINS is rejected with
   PORT_ERR_INVALID_ARG rather than wrapping into another pin's slot, and the
   same constant bounds storage, counting and rejection.

   `configured[pin]` has exactly one meaning: this fake has seen either a
   `set_mode` or a `write` for the pin. Both operations set it; `read` never
   does, because reading a stored level says nothing about how the pin was
   configured. Reset clears it.

   `forced_status` is one-shot failure injection: any value other than PORT_OK
   is returned by the next operation and then replaced by PORT_OK, so a test
   can script exactly one failure. PORT_OK therefore means "no forcing". The
   forced status is consumed only after the call's own argument and bound
   checks pass, so an invalid pin still reports PORT_ERR_INVALID_ARG. */
#define HOST_FAKE_GPIO_PINS 64

typedef struct host_fake_gpio {
    port_gpio_mode_t mode[HOST_FAKE_GPIO_PINS];
    port_gpio_level_t level[HOST_FAKE_GPIO_PINS];
    bool configured[HOST_FAKE_GPIO_PINS];
    port_status_t forced_status;
    size_t writes;
    size_t reads;
} host_fake_gpio_t;

void host_fake_gpio_reset(host_fake_gpio_t *fake);
void host_fake_gpio_fail_next(host_fake_gpio_t *fake, port_status_t status);

port_gpio_t host_fake_gpio_port(host_fake_gpio_t *fake);

#ifdef __cplusplus
}
#endif
