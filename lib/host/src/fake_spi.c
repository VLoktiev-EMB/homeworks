#include <stddef.h>

#include "host/fake_spi.h"

static port_status_t consume_forced_status(host_fake_spi_t *fake) {
    port_status_t status = fake->forced_status;

    if (status != PORT_OK) {
        fake->forced_status = PORT_OK;
    }
    return status;
}

static port_status_t host_fake_spi_transfer(void *ctx, const uint8_t *tx, uint8_t *rx,
                                            size_t length) {
    host_fake_spi_t *fake = (host_fake_spi_t *)ctx;
    port_status_t forced;
    size_t index;

    if (fake == NULL || length > HOST_FAKE_SPI_CAPACITY || (tx == NULL && length > 0u)) {
        return PORT_ERR_INVALID_ARG;
    }
    forced = consume_forced_status(fake);
    if (forced != PORT_OK) {
        return forced;
    }
    for (index = 0; index < length; ++index) {
        fake->tx[index] = tx[index];
    }
    fake->length = length;
    if (rx != NULL) {
        for (index = 0; index < length; ++index) {
            rx[index] = tx[index];
        }
    }
    fake->transfers++;
    return PORT_OK;
}

static port_status_t host_fake_spi_write(void *ctx, const uint8_t *data, size_t length) {
    host_fake_spi_t *fake = (host_fake_spi_t *)ctx;
    port_status_t forced;
    size_t index;

    if (fake == NULL || length > HOST_FAKE_SPI_CAPACITY || (data == NULL && length > 0u)) {
        return PORT_ERR_INVALID_ARG;
    }
    forced = consume_forced_status(fake);
    if (forced != PORT_OK) {
        return forced;
    }
    for (index = 0; index < length; ++index) {
        fake->tx[index] = data[index];
    }
    fake->length = length;
    fake->transfers++;
    return PORT_OK;
}

void host_fake_spi_reset(host_fake_spi_t *fake) {
    size_t index;

    if (fake == NULL) {
        return;
    }
    for (index = 0; index < HOST_FAKE_SPI_CAPACITY; ++index) {
        fake->tx[index] = 0u;
    }
    fake->length = 0u;
    fake->transfers = 0u;
    fake->forced_status = PORT_OK;
}

void host_fake_spi_fail_next(host_fake_spi_t *fake, port_status_t status) {
    if (fake == NULL) {
        return;
    }
    fake->forced_status = status;
}

port_spi_t host_fake_spi_port(host_fake_spi_t *fake) {
    port_spi_t port = {host_fake_spi_transfer, host_fake_spi_write, fake};

    return port;
}
