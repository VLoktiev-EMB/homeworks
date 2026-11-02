#ifndef PORT_SPI_H
#define PORT_SPI_H

#pragma once

#include <stddef.h>
#include <stdint.h>

#include "port/status.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Consumer-owned SPI operations table.

   Placed in Flash / ROM (.rodata) as a const struct. */
typedef struct port_spi_ops {
    port_status_t (*transfer)(void *ctx, const uint8_t *tx, uint8_t *rx, size_t length);
    port_status_t (*write)(void *ctx, const uint8_t *data, size_t length);
} port_spi_ops_t;

/* Consumer-owned SPI bus contract.

   The chip-select line, clock mode and frequency are bus configuration owned
   by the adapter, not per-call parameters; a consumer that needs two devices
   holds two bus instances. Each call performs one transfer of `length` bytes.

   This contract does not name a framework type, does not own state, does not
   block, and does not encode device behaviour. */
typedef struct port_spi {
    const port_spi_ops_t *ops;
    void *ctx;
} port_spi_t;

/* Safe inline dispatch helpers verifying pointers before dereferencing. */
static inline port_status_t port_spi_transfer(const port_spi_t *spi, const uint8_t *tx, uint8_t *rx, size_t length)
{
    if (spi == NULL || spi->ops == NULL || spi->ops->transfer == NULL) {
        return PORT_ERR_INVALID_ARG;
    }
    return spi->ops->transfer(spi->ctx, tx, rx, length);
}

static inline port_status_t port_spi_write(const port_spi_t *spi, const uint8_t *data, size_t length)
{
    if (spi == NULL || spi->ops == NULL || spi->ops->write == NULL) {
        return PORT_ERR_INVALID_ARG;
    }
    return spi->ops->write(spi->ctx, data, length);
}

#ifdef __cplusplus
}
#endif

#endif /* PORT_SPI_H */
