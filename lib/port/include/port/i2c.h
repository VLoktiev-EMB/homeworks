#pragma once

#include <stddef.h>
#include <stdint.h>

#include "port/status.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Consumer-owned I2C bus contract.

   `address` is the 7-bit bus address. Each call performs exactly one bus
   transaction; register maps, page boundaries and device initialisation
   belong to the consumer, never to this bus. Clock speed, pull-ups and the
   underlying framework handle are adapter-owned bus configuration.

   This contract does not name a framework type, does not own state, does not
   block, and does not encode device behaviour. */
typedef struct port_i2c {
    port_status_t (*write)(void *ctx, uint8_t address, const uint8_t *data, size_t length);
    port_status_t (*read)(void *ctx, uint8_t address, uint8_t *data, size_t length);
    port_status_t (*write_read)(void *ctx, uint8_t address, const uint8_t *tx, size_t tx_length,
                                uint8_t *rx, size_t rx_length);
    void *ctx;
} port_i2c_t;

#ifdef __cplusplus
}
#endif
