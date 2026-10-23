#pragma once

#include "port/gpio.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ESP-IDF GPIO adapter.

   Returns the consumer-owned GPIO contract over the framework C driver. A pin
   at or above 64 is rejected before it reaches the pin mask, and driver errors
   are translated to the port vocabulary. No framework type crosses this
   header. */
port_gpio_t espidf_gpio_port(void);

#ifdef __cplusplus
}
#endif
