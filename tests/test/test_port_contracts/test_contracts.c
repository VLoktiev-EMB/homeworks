#include <stddef.h>
#include <stdint.h>

#include <unity.h>

#include "port/gpio.h"
#include "port/i2c.h"
#include "port/spi.h"
#include "port/status.h"

/* File-scope fake state. Every callback receives the same pointer through its
   `ctx` argument, so observing the recorded pointer proves the plumbing. */
typedef struct fake_pin {
    uint8_t mode[4];
    port_gpio_level_t level[4];
    int writes;
    void *seen_ctx[3];
    int seen_count;
} fake_pin_t;

static void record_ctx(fake_pin_t *state, void *ctx) {
    if (state->seen_count < 3) {
        state->seen_ctx[state->seen_count] = ctx;
        state->seen_count++;
    }
}

static port_status_t fake_set_mode(void *ctx, uint8_t pin, port_gpio_mode_t mode) {
    fake_pin_t *state = ctx;

    if (state == NULL || pin >= 4u) {
        return PORT_ERR_INVALID_ARG;
    }
    record_ctx(state, ctx);
    state->mode[pin] = (uint8_t)mode;
    return PORT_OK;
}

static port_status_t fake_write(void *ctx, uint8_t pin, port_gpio_level_t level) {
    fake_pin_t *state = ctx;

    if (state == NULL || pin >= 4u) {
        return PORT_ERR_INVALID_ARG;
    }
    if (level != PORT_GPIO_LOW && level != PORT_GPIO_HIGH) {
        return PORT_ERR_INVALID_ARG;
    }
    record_ctx(state, ctx);
    state->level[pin] = level;
    state->writes++;
    return PORT_OK;
}

static port_status_t fake_read(void *ctx, uint8_t pin, port_gpio_level_t *level) {
    fake_pin_t *state = ctx;

    if (state == NULL || level == NULL || pin >= 4u) {
        return PORT_ERR_INVALID_ARG;
    }
    record_ctx(state, ctx);
    *level = state->level[pin];
    return PORT_OK;
}

/* I2C loopback: writes land in a fixed buffer that a later read copies out. */
typedef struct fake_i2c {
    uint8_t buffer[32];
    size_t length;
    size_t last_tx_length;
    size_t last_rx_length;
    uint8_t last_address;
    int transactions;
} fake_i2c_t;

#define FAKE_BUS_CAPACITY 32u

static port_status_t fake_i2c_write(void *ctx, uint8_t address, const uint8_t *data,
                                    size_t length) {
    fake_i2c_t *bus = ctx;
    size_t i;

    if (bus == NULL || data == NULL || length > FAKE_BUS_CAPACITY) {
        return PORT_ERR_INVALID_ARG;
    }
    bus->last_address = address;
    for (i = 0; i < length; i++) {
        bus->buffer[i] = data[i];
    }
    bus->length = length;
    bus->transactions++;
    return PORT_OK;
}

static port_status_t fake_i2c_read(void *ctx, uint8_t address, uint8_t *data, size_t length) {
    fake_i2c_t *bus = ctx;
    size_t i;

    if (bus == NULL || data == NULL || length > bus->length) {
        return PORT_ERR_INVALID_ARG;
    }
    bus->last_address = address;
    for (i = 0; i < length; i++) {
        data[i] = bus->buffer[i];
    }
    bus->transactions++;
    return PORT_OK;
}

static port_status_t fake_i2c_write_read(void *ctx, uint8_t address, const uint8_t *tx,
                                         size_t tx_length, uint8_t *rx, size_t rx_length) {
    fake_i2c_t *bus = ctx;
    size_t i;

    if (bus == NULL || tx == NULL || rx == NULL) {
        return PORT_ERR_INVALID_ARG;
    }
    if (tx_length > FAKE_BUS_CAPACITY || rx_length > FAKE_BUS_CAPACITY) {
        return PORT_ERR_INVALID_ARG;
    }
    bus->last_address = address;
    bus->last_tx_length = tx_length;
    bus->last_rx_length = rx_length;
    for (i = 0; i < tx_length; i++) {
        bus->buffer[i] = tx[i];
    }
    for (i = 0; i < rx_length; i++) {
        rx[i] = bus->buffer[i];
    }
    bus->length = rx_length;
    bus->transactions++;
    return PORT_OK;
}

/* SPI loopback: the transmit log records what crossed the vtable. */
typedef struct fake_spi {
    uint8_t tx_log[32];
    size_t length;
    int transfers;
} fake_spi_t;

static port_status_t fake_spi_transfer(void *ctx, const uint8_t *tx, uint8_t *rx,
                                       size_t length) {
    fake_spi_t *spi = ctx;
    size_t i;

    if (spi == NULL || length > FAKE_BUS_CAPACITY) {
        return PORT_ERR_INVALID_ARG;
    }
    if (tx == NULL && rx == NULL) {
        return PORT_ERR_INVALID_ARG;
    }
    for (i = 0; i < length; i++) {
        if (tx != NULL) {
            spi->tx_log[i] = tx[i];
        }
        if (rx != NULL) {
            rx[i] = (tx != NULL) ? tx[i] : (uint8_t)0;
        }
    }
    spi->length = length;
    spi->transfers++;
    return PORT_OK;
}

static port_status_t fake_spi_write(void *ctx, const uint8_t *data, size_t length) {
    fake_spi_t *spi = ctx;
    size_t i;

    if (spi == NULL || data == NULL || length > FAKE_BUS_CAPACITY) {
        return PORT_ERR_INVALID_ARG;
    }
    for (i = 0; i < length; i++) {
        spi->tx_log[i] = data[i];
    }
    spi->length = length;
    spi->transfers++;
    return PORT_OK;
}

void setUp(void) {}

void tearDown(void) {}

static void test_gpio_ctx_reaches_every_callback(void) {
    fake_pin_t state = {0};
    const port_gpio_t gpio = { fake_set_mode, fake_write, fake_read, &state };
    port_gpio_level_t level = PORT_GPIO_LOW;

    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.set_mode(gpio.ctx, 1u, PORT_GPIO_OUTPUT));
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.write(gpio.ctx, 1u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.read(gpio.ctx, 1u, &level));

    TEST_ASSERT_EQUAL_INT(3, state.seen_count);
    TEST_ASSERT_EQUAL_PTR(&state, state.seen_ctx[0]);
    TEST_ASSERT_EQUAL_PTR(&state, state.seen_ctx[1]);
    TEST_ASSERT_EQUAL_PTR(&state, state.seen_ctx[2]);
}

static void test_gpio_write_then_read_round_trip(void) {
    fake_pin_t state = {0};
    const port_gpio_t gpio = { fake_set_mode, fake_write, fake_read, &state };
    port_gpio_level_t level = PORT_GPIO_LOW;

    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.set_mode(gpio.ctx, 3u, PORT_GPIO_OUTPUT));
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.write(gpio.ctx, 3u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.read(gpio.ctx, 3u, &level));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, level);

    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.write(gpio.ctx, 3u, PORT_GPIO_LOW));
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.read(gpio.ctx, 3u, &level));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, level);
    TEST_ASSERT_EQUAL_INT(2, state.writes);
}

static void test_gpio_invalid_level_is_rejected(void) {
    fake_pin_t state = {0};
    const port_gpio_t gpio = { fake_set_mode, fake_write, fake_read, &state };

    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG,
                          gpio.write(gpio.ctx, 0u, (port_gpio_level_t)99));
    TEST_ASSERT_EQUAL_INT(0, state.writes);
}

static void test_gpio_two_contexts_are_independent(void) {
    fake_pin_t first = {0};
    fake_pin_t second = {0};
    const port_gpio_t gpio_a = { fake_set_mode, fake_write, fake_read, &first };
    const port_gpio_t gpio_b = { fake_set_mode, fake_write, fake_read, &second };
    port_gpio_level_t level = PORT_GPIO_LOW;

    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio_a.write(gpio_a.ctx, 0u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio_b.write(gpio_b.ctx, 0u, PORT_GPIO_LOW));

    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio_a.read(gpio_a.ctx, 0u, &level));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, level);
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio_b.read(gpio_b.ctx, 0u, &level));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, level);

    TEST_ASSERT_EQUAL_INT(1, first.writes);
    TEST_ASSERT_EQUAL_INT(1, second.writes);
}

static void test_i2c_write_then_read_loopback(void) {
    fake_i2c_t bus = {0};
    const port_i2c_t i2c = { fake_i2c_write, fake_i2c_read, fake_i2c_write_read, &bus };
    const uint8_t payload[3] = {0x01u, 0x02u, 0x03u};
    uint8_t received[3] = {0};

    TEST_ASSERT_EQUAL_INT(PORT_OK, i2c.write(i2c.ctx, 0x3Cu, payload, 3u));
    TEST_ASSERT_EQUAL_UINT8(0x3Cu, bus.last_address);
    TEST_ASSERT_EQUAL_UINT32(3u, (uint32_t)bus.length);

    TEST_ASSERT_EQUAL_INT(PORT_OK, i2c.read(i2c.ctx, 0x3Cu, received, 3u));
    TEST_ASSERT_EQUAL_UINT8_ARRAY(payload, received, 3u);
    TEST_ASSERT_EQUAL_INT(2, bus.transactions);
}

static void test_i2c_combined_write_read_passes_both_lengths(void) {
    fake_i2c_t bus = {0};
    const port_i2c_t i2c = { fake_i2c_write, fake_i2c_read, fake_i2c_write_read, &bus };
    const uint8_t tx[2] = {0xA5u, 0x5Au};
    uint8_t rx[2] = {0};

    TEST_ASSERT_EQUAL_INT(PORT_OK, i2c.write_read(i2c.ctx, 0x20u, tx, 2u, rx, 2u));
    TEST_ASSERT_EQUAL_UINT32(2u, (uint32_t)bus.last_tx_length);
    TEST_ASSERT_EQUAL_UINT32(2u, (uint32_t)bus.last_rx_length);
    TEST_ASSERT_EQUAL_UINT8_ARRAY(tx, rx, 2u);
}

static void test_i2c_null_buffer_is_rejected(void) {
    fake_i2c_t bus = {0};
    const port_i2c_t i2c = { fake_i2c_write, fake_i2c_read, fake_i2c_write_read, &bus };

    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, i2c.write(i2c.ctx, 0x10u, NULL, 1u));
    TEST_ASSERT_EQUAL_INT(0, bus.transactions);
}

static void test_spi_transfer_copies_without_allocation(void) {
    fake_spi_t state = {0};
    const port_spi_t spi = { fake_spi_transfer, fake_spi_write, &state };
    const uint8_t tx[3] = {0x11u, 0x22u, 0x33u};
    uint8_t rx[3] = {0};

    TEST_ASSERT_EQUAL_INT(PORT_OK, spi.transfer(spi.ctx, tx, rx, 3u));
    TEST_ASSERT_EQUAL_UINT8_ARRAY(tx, rx, 3u);
    TEST_ASSERT_EQUAL_UINT8_ARRAY(tx, state.tx_log, 3u);
    TEST_ASSERT_EQUAL_INT(1, state.transfers);
}

static void test_spi_write_records_the_transmitted_bytes(void) {
    fake_spi_t state = {0};
    const port_spi_t spi = { fake_spi_transfer, fake_spi_write, &state };
    const uint8_t payload[2] = {0xDEu, 0xADu};

    TEST_ASSERT_EQUAL_INT(PORT_OK, spi.write(spi.ctx, payload, 2u));
    TEST_ASSERT_EQUAL_UINT8_ARRAY(payload, state.tx_log, 2u);
    TEST_ASSERT_EQUAL_UINT32(2u, (uint32_t)state.length);
}

static void test_bus_contracts_use_their_own_context(void) {
    fake_i2c_t i2c_state = {0};
    fake_spi_t spi_state = {0};
    const port_i2c_t i2c = { fake_i2c_write, fake_i2c_read, fake_i2c_write_read, &i2c_state };
    const port_spi_t spi = { fake_spi_transfer, fake_spi_write, &spi_state };
    const uint8_t payload[1] = {0x7Eu};

    TEST_ASSERT_EQUAL_INT(PORT_OK, i2c.write(i2c.ctx, 0x08u, payload, 1u));
    TEST_ASSERT_EQUAL_INT(PORT_OK, spi.write(spi.ctx, payload, 1u));

    TEST_ASSERT_EQUAL_UINT8(0x7Eu, i2c_state.buffer[0]);
    TEST_ASSERT_EQUAL_UINT8(0x7Eu, spi_state.tx_log[0]);
    TEST_ASSERT_EQUAL_INT(1, i2c_state.transactions);
    TEST_ASSERT_EQUAL_INT(1, spi_state.transfers);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_gpio_ctx_reaches_every_callback);
    RUN_TEST(test_gpio_write_then_read_round_trip);
    RUN_TEST(test_gpio_invalid_level_is_rejected);
    RUN_TEST(test_gpio_two_contexts_are_independent);
    RUN_TEST(test_i2c_write_then_read_loopback);
    RUN_TEST(test_i2c_combined_write_read_passes_both_lengths);
    RUN_TEST(test_i2c_null_buffer_is_rejected);
    RUN_TEST(test_spi_transfer_copies_without_allocation);
    RUN_TEST(test_spi_write_records_the_transmitted_bytes);
    RUN_TEST(test_bus_contracts_use_their_own_context);
    return UNITY_END();
}
