#pragma once

#include <stddef.h>
#include <stdint.h>

#include "port/spi.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Bounded SPI recording double.

   `transfer` records the transmitted bytes and loops them back into `rx` when
   a receive buffer is supplied; `write` records them without touching any
   receive buffer. The stored bytes are the last transfer, capped at
   HOST_FAKE_SPI_CAPACITY. A transfer longer than the capacity returns
   PORT_ERR_INVALID_ARG rather than truncating silently.

   `forced_status` is one-shot: any value other than PORT_OK is returned by the
   next operation and then replaced by PORT_OK, so PORT_OK means "no forcing".
   The forced status is consumed only after the call's own checks pass. */
#define HOST_FAKE_SPI_CAPACITY 32

typedef struct host_fake_spi {
    uint8_t tx[HOST_FAKE_SPI_CAPACITY];
    size_t length;
    size_t transfers;
    port_status_t forced_status;
} host_fake_spi_t;

void host_fake_spi_reset(host_fake_spi_t *fake);
void host_fake_spi_fail_next(host_fake_spi_t *fake, port_status_t status);

port_spi_t host_fake_spi_port(host_fake_spi_t *fake);

#ifdef __cplusplus
}
#endif
