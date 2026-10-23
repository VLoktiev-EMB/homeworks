#include <stddef.h>

#include "host/fake_i2c.h"

static port_status_t consume_forced_status(host_fake_i2c_t *fake) {
    port_status_t status = fake->forced_status;

    if (status != PORT_OK) {
        fake->forced_status = PORT_OK;
    }
    return status;
}

static port_status_t host_fake_i2c_write(void *ctx, uint8_t address, const uint8_t *data,
                                         size_t length) {
    host_fake_i2c_t *fake = (host_fake_i2c_t *)ctx;
    port_status_t forced;
    size_t index;

    if (fake == NULL || length > HOST_FAKE_I2C_CAPACITY || (data == NULL && length > 0u)) {
        return PORT_ERR_INVALID_ARG;
    }
    forced = consume_forced_status(fake);
    if (forced != PORT_OK) {
        return forced;
    }
    for (index = 0; index < length; ++index) {
        fake->buffer[index] = data[index];
    }
    fake->length = length;
    fake->last_address = address;
    fake->transactions++;
    return PORT_OK;
}

static port_status_t host_fake_i2c_read(void *ctx, uint8_t address, uint8_t *data,
                                        size_t length) {
    host_fake_i2c_t *fake = (host_fake_i2c_t *)ctx;
    port_status_t forced;
    size_t index;

    if (fake == NULL || length > HOST_FAKE_I2C_CAPACITY || (data == NULL && length > 0u) ||
        length > fake->length) {
        return PORT_ERR_INVALID_ARG;
    }
    forced = consume_forced_status(fake);
    if (forced != PORT_OK) {
        return forced;
    }
    for (index = 0; index < length; ++index) {
        data[index] = fake->buffer[index];
    }
    fake->last_address = address;
    fake->transactions++;
    return PORT_OK;
}

static port_status_t host_fake_i2c_write_read(void *ctx, uint8_t address, const uint8_t *tx,
                                              size_t tx_length, uint8_t *rx,
                                              size_t rx_length) {
    host_fake_i2c_t *fake = (host_fake_i2c_t *)ctx;
    port_status_t forced;
    size_t index;

    if (fake == NULL || tx_length > HOST_FAKE_I2C_CAPACITY ||
        rx_length > HOST_FAKE_I2C_CAPACITY || rx_length > tx_length ||
        (tx == NULL && tx_length > 0u) || (rx == NULL && rx_length > 0u)) {
        return PORT_ERR_INVALID_ARG;
    }
    forced = consume_forced_status(fake);
    if (forced != PORT_OK) {
        return forced;
    }
    for (index = 0; index < tx_length; ++index) {
        fake->buffer[index] = tx[index];
    }
    fake->length = tx_length;
    for (index = 0; index < rx_length; ++index) {
        rx[index] = fake->buffer[index];
    }
    fake->last_address = address;
    fake->transactions++;
    return PORT_OK;
}

void host_fake_i2c_reset(host_fake_i2c_t *fake) {
    size_t index;

    if (fake == NULL) {
        return;
    }
    for (index = 0; index < HOST_FAKE_I2C_CAPACITY; ++index) {
        fake->buffer[index] = 0u;
    }
    fake->length = 0u;
    fake->last_address = 0u;
    fake->transactions = 0u;
    fake->forced_status = PORT_OK;
}

void host_fake_i2c_fail_next(host_fake_i2c_t *fake, port_status_t status) {
    if (fake == NULL) {
        return;
    }
    fake->forced_status = status;
}

void host_fake_i2c_preset(host_fake_i2c_t *fake, const uint8_t *data, size_t length) {
    size_t index;

    if (fake == NULL || data == NULL || length > HOST_FAKE_I2C_CAPACITY) {
        return;
    }
    for (index = 0; index < length; ++index) {
        fake->buffer[index] = data[index];
    }
    fake->length = length;
}

port_i2c_t host_fake_i2c_port(host_fake_i2c_t *fake) {
    port_i2c_t port = {host_fake_i2c_write, host_fake_i2c_read, host_fake_i2c_write_read, fake};

    return port;
}
