#pragma once

#include "port/gpio.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Arduino GPIO adapter.

   Maps the three port modes and the two port levels onto the framework C API
   and returns the consumer-owned contract by value. A pin is passed through as
   `uint8_t`; no framework type crosses this header. */
port_gpio_t arduino_gpio_port(void);

#ifdef __cplusplus
}
#endif
