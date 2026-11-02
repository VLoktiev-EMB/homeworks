#ifndef PORT_I2C_H
#define PORT_I2C_H

#pragma once

#include <stddef.h>
#include <stdint.h>

#include "port/status.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Consumer-owned I2C operations table.

   Placed in Flash / ROM (.rodata) as a const struct. */
typedef struct port_i2c_ops {
    port_status_t (*write)(void *ctx, uint8_t address, const uint8_t *data, size_t length);
    port_status_t (*read)(void *ctx, uint8_t address, uint8_t *data, size_t length);
    port_status_t (*write_read)(void *ctx, uint8_t address, const uint8_t *tx, size_t tx_length, uint8_t *rx,
                                size_t rx_length);
} port_i2c_ops_t;

/* Consumer-owned I2C bus contract.

   `address` is the 7-bit bus address. Each call performs exactly one bus
   transaction; register maps, page boundaries and device initialisation
   belong to the consumer, never to this bus. Clock speed, pull-ups and the
   underlying framework handle are adapter-owned bus configuration.

   This contract does not name a framework type, does not own state, does not
   block, and does not encode device behaviour. */
typedef struct port_i2c {
    const port_i2c_ops_t *ops;
    void *ctx;
} port_i2c_t;

/* Safe inline dispatch helpers verifying pointers before dereferencing. */
static inline port_status_t port_i2c_write(const port_i2c_t *i2c, uint8_t address, const uint8_t *data, size_t length)
{
    if (i2c == NULL || i2c->ops == NULL || i2c->ops->write == NULL) {
        return PORT_ERR_INVALID_ARG;
    }
    return i2c->ops->write(i2c->ctx, address, data, length);
}

static inline port_status_t port_i2c_read(const port_i2c_t *i2c, uint8_t address, uint8_t *data, size_t length)
{
    if (i2c == NULL || i2c->ops == NULL || i2c->ops->read == NULL) {
        return PORT_ERR_INVALID_ARG;
    }
    return i2c->ops->read(i2c->ctx, address, data, length);
}

static inline port_status_t port_i2c_write_read(const port_i2c_t *i2c, uint8_t address, const uint8_t *tx,
                                                size_t tx_length, uint8_t *rx, size_t rx_length)
{
    if (i2c == NULL || i2c->ops == NULL || i2c->ops->write_read == NULL) {
        return PORT_ERR_INVALID_ARG;
    }
    return i2c->ops->write_read(i2c->ctx, address, tx, tx_length, rx, rx_length);
}

#ifdef __cplusplus
}
#endif

#endif /* PORT_I2C_H */
