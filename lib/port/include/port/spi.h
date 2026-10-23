#pragma once

#include <stddef.h>
#include <stdint.h>

#include "port/status.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Consumer-owned SPI bus contract.

   The chip-select line, clock mode and frequency are bus configuration owned
   by the adapter, not per-call parameters; a consumer that needs two devices
   holds two bus instances. Each call performs one transfer of `length` bytes.

   This contract does not name a framework type, does not own state, does not
   block, and does not encode device behaviour. */
typedef struct port_spi {
    port_status_t (*transfer)(void *ctx, const uint8_t *tx, uint8_t *rx, size_t length);
    port_status_t (*write)(void *ctx, const uint8_t *data, size_t length);
    void *ctx;
} port_spi_t;

#ifdef __cplusplus
}
#endif
