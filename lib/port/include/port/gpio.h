#pragma once

#include <stdint.h>

#include "port/status.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Pin modes this phase can express.

   Pull-down input and floating input are deliberately absent: an adapter that
   accepted them would have to invent a default, so a future need is an
   additive enum member rather than an implicit behaviour. */
typedef enum port_gpio_mode { PORT_GPIO_INPUT = 0, PORT_GPIO_OUTPUT, PORT_GPIO_INPUT_PULLUP } port_gpio_mode_t;

/* Digital level. Explicit values keep the zero case unambiguous. */
typedef enum port_gpio_level { PORT_GPIO_LOW = 0, PORT_GPIO_HIGH = 1 } port_gpio_level_t;

/* Consumer-owned GPIO contract.

   The consumer owns the interface, the adapter owns the state behind `ctx`,
   and an adapter factory returns this struct by value. Nothing is stored in a
   global, because a second instance is a second `ctx`, not a second global.

   A pin is `uint8_t` because this phase targets the ESP32-S3 GPIO range
   (0..48); the ESP-IDF adapter rejects a pin at or above 64, so the narrower
   field cannot silently truncate a valid board pin.

   This contract does not name a framework type, does not own state, does not
   block, and does not encode device behaviour. */
typedef struct port_gpio {
    port_status_t (*set_mode)(void *ctx, uint8_t pin, port_gpio_mode_t mode);
    port_status_t (*write)(void *ctx, uint8_t pin, port_gpio_level_t level);
    port_status_t (*read)(void *ctx, uint8_t pin, port_gpio_level_t *level);
    void *ctx;
} port_gpio_t;

#ifdef __cplusplus
}
#endif
