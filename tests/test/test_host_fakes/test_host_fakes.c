#include <stddef.h>
#include <stdint.h>

#include <unity.h>

#include "host/fake_gpio.h"
#include "host/fake_i2c.h"
#include "host/fake_log.h"
#include "host/fake_spi.h"
#include "host/fake_time.h"
#include "port/gpio.h"
#include "port/i2c.h"
#include "port/log.h"
#include "port/spi.h"
#include "port/time.h"

static host_fake_gpio_t fake;
static port_gpio_t gpio;
static host_fake_i2c_t i2c_fake;
static port_i2c_t i2c;
static host_fake_spi_t spi_fake;
static port_spi_t spi;
static host_fake_log_t log_fake;
static port_log_t log_contract;
static host_fake_time_t time_fake;

void setUp(void)
{
    host_fake_gpio_reset(&fake);
    gpio = host_fake_gpio_port(&fake);
    host_fake_i2c_reset(&i2c_fake);
    i2c = host_fake_i2c_port(&i2c_fake);
    host_fake_spi_reset(&spi_fake);
    spi = host_fake_spi_port(&spi_fake);
    host_fake_log_reset(&log_fake);
    log_contract = host_fake_log_port(&log_fake);
    host_fake_time_reset(&time_fake);
}

void tearDown(void) {}

static void test_fake_gpio_records_writes(void)
{
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.write(gpio.ctx, 5u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)fake.writes);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake.level[5]);
}

static void test_fake_gpio_replays_levels(void)
{
    port_gpio_level_t level = PORT_GPIO_LOW;

    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.write(gpio.ctx, 7u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.read(gpio.ctx, 7u, &level));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, level);
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)fake.reads);

    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.write(gpio.ctx, 7u, PORT_GPIO_LOW));
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.read(gpio.ctx, 7u, &level));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, level);
    TEST_ASSERT_EQUAL_UINT32(2u, (uint32_t)fake.reads);
}

static void test_fake_gpio_out_of_range_pin_is_rejected(void)
{
    port_gpio_level_t level = PORT_GPIO_LOW;

    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, gpio.write(gpio.ctx, HOST_FAKE_GPIO_PINS, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)fake.writes);
    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, gpio.set_mode(gpio.ctx, HOST_FAKE_GPIO_PINS, PORT_GPIO_OUTPUT));
    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, gpio.read(gpio.ctx, HOST_FAKE_GPIO_PINS, &level));
    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, gpio.read(gpio.ctx, 0u, NULL));
}

static void test_fake_gpio_forced_status_is_one_shot(void)
{
    host_fake_gpio_fail_next(&fake, PORT_ERR_IO);

    TEST_ASSERT_EQUAL_INT(PORT_ERR_IO, gpio.write(gpio.ctx, 1u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)fake.writes);
    TEST_ASSERT_EQUAL_INT(PORT_OK, fake.forced_status);

    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.write(gpio.ctx, 1u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)fake.writes);
}

static void test_fake_gpio_set_mode_and_write_mark_configured(void)
{
    port_gpio_level_t level = PORT_GPIO_LOW;

    TEST_ASSERT_FALSE(fake.configured[4]);
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.set_mode(gpio.ctx, 4u, PORT_GPIO_OUTPUT));
    TEST_ASSERT_TRUE(fake.configured[4]);

    TEST_ASSERT_FALSE(fake.configured[9]);
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.write(gpio.ctx, 9u, PORT_GPIO_HIGH));
    TEST_ASSERT_TRUE(fake.configured[9]);

    TEST_ASSERT_FALSE(fake.configured[12]);
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.read(gpio.ctx, 12u, &level));
    TEST_ASSERT_FALSE(fake.configured[12]);
}

static void test_gpio_fake_returns_the_real_gpio_contract_type(void)
{
    port_gpio_t returned = host_fake_gpio_port(&fake);

    TEST_ASSERT_EQUAL_PTR(&fake, returned.ctx);
    TEST_ASSERT_EQUAL_INT(PORT_OK, returned.write(returned.ctx, 2u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake.level[2]);
}

static void test_fake_i2c_write_then_read(void)
{
    const uint8_t payload[2] = {0xDEu, 0xADu};
    uint8_t received[2] = {0u, 0u};

    TEST_ASSERT_EQUAL_INT(PORT_OK, i2c.write(i2c.ctx, 0x3Cu, payload, 2u));
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)i2c_fake.transactions);
    TEST_ASSERT_EQUAL_UINT8(0x3Cu, i2c_fake.last_address);

    TEST_ASSERT_EQUAL_INT(PORT_OK, i2c.read(i2c.ctx, 0x3Cu, received, 2u));
    TEST_ASSERT_EQUAL_UINT8(0xDEu, received[0]);
    TEST_ASSERT_EQUAL_UINT8(0xADu, received[1]);
    TEST_ASSERT_EQUAL_UINT32(2u, (uint32_t)i2c_fake.transactions);
}

static void test_fake_i2c_combined_transfer(void)
{
    const uint8_t command[3] = {0x01u, 0x02u, 0x03u};
    uint8_t response[3] = {0u, 0u, 0u};

    TEST_ASSERT_EQUAL_INT(PORT_OK, i2c.write_read(i2c.ctx, 0x20u, command, 3u, response, 3u));
    TEST_ASSERT_EQUAL_UINT8(0x01u, response[0]);
    TEST_ASSERT_EQUAL_UINT8(0x02u, response[1]);
    TEST_ASSERT_EQUAL_UINT8(0x03u, response[2]);
    TEST_ASSERT_EQUAL_UINT8(0x20u, i2c_fake.last_address);
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)i2c_fake.transactions);
}

static void test_fake_i2c_oversized_write_is_rejected(void)
{
    uint8_t payload[HOST_FAKE_I2C_CAPACITY + 1u] = {0u};

    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, i2c.write(i2c.ctx, 0x10u, payload, HOST_FAKE_I2C_CAPACITY + 1u));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)i2c_fake.transactions);

    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, i2c.write(i2c.ctx, 0x10u, NULL, 1u));
}

static void test_fake_i2c_two_instances_hold_separate_buffers(void)
{
    host_fake_i2c_t first;
    host_fake_i2c_t second;
    port_i2c_t first_port;
    port_i2c_t second_port;
    const uint8_t first_data[2] = {0x11u, 0x22u};
    const uint8_t second_data[2] = {0x33u, 0x44u};
    uint8_t received[2] = {0u, 0u};

    host_fake_i2c_reset(&first);
    host_fake_i2c_reset(&second);
    first_port = host_fake_i2c_port(&first);
    second_port = host_fake_i2c_port(&second);

    TEST_ASSERT_EQUAL_INT(PORT_OK, first_port.write(first_port.ctx, 1u, first_data, 2u));
    TEST_ASSERT_EQUAL_INT(PORT_OK, second_port.write(second_port.ctx, 2u, second_data, 2u));

    TEST_ASSERT_EQUAL_INT(PORT_OK, first_port.read(first_port.ctx, 1u, received, 2u));
    TEST_ASSERT_EQUAL_UINT8(0x11u, received[0]);
    TEST_ASSERT_EQUAL_UINT8(0x22u, received[1]);

    TEST_ASSERT_EQUAL_INT(PORT_OK, second_port.read(second_port.ctx, 2u, received, 2u));
    TEST_ASSERT_EQUAL_UINT8(0x33u, received[0]);
    TEST_ASSERT_EQUAL_UINT8(0x44u, received[1]);
}

static void test_fake_spi_loops_back(void)
{
    const uint8_t outgoing[3] = {0xA1u, 0xB2u, 0xC3u};
    uint8_t incoming[3] = {0u, 0u, 0u};

    TEST_ASSERT_EQUAL_INT(PORT_OK, spi.transfer(spi.ctx, outgoing, incoming, 3u));
    TEST_ASSERT_EQUAL_UINT8(0xA1u, incoming[0]);
    TEST_ASSERT_EQUAL_UINT8(0xB2u, incoming[1]);
    TEST_ASSERT_EQUAL_UINT8(0xC3u, incoming[2]);
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)spi_fake.transfers);
    TEST_ASSERT_EQUAL_UINT32(3u, (uint32_t)spi_fake.length);
}

static void test_fake_spi_write_records_without_receive_buffer(void)
{
    const uint8_t outgoing[2] = {0x5Au, 0xA5u};
    uint8_t oversized[HOST_FAKE_SPI_CAPACITY + 1u] = {0u};

    TEST_ASSERT_EQUAL_INT(PORT_OK, spi.write(spi.ctx, outgoing, 2u));
    TEST_ASSERT_EQUAL_UINT32(2u, (uint32_t)spi_fake.length);
    TEST_ASSERT_EQUAL_UINT8(0x5Au, spi_fake.tx[0]);
    TEST_ASSERT_EQUAL_UINT8(0xA5u, spi_fake.tx[1]);
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)spi_fake.transfers);

    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, spi.write(spi.ctx, oversized, HOST_FAKE_SPI_CAPACITY + 1u));
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)spi_fake.transfers);
}

static void test_bus_fakes_keep_separate_contexts(void)
{
    const uint8_t payload[1] = {0x77u};
    uint8_t received[1] = {0u};

    TEST_ASSERT_EQUAL_PTR(&i2c_fake, i2c.ctx);
    TEST_ASSERT_EQUAL_PTR(&spi_fake, spi.ctx);

    TEST_ASSERT_EQUAL_INT(PORT_OK, i2c.write(i2c.ctx, 0x0Au, payload, 1u));
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)i2c_fake.transactions);
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)spi_fake.transfers);

    TEST_ASSERT_EQUAL_INT(PORT_OK, spi.transfer(spi.ctx, payload, received, 1u));
    TEST_ASSERT_EQUAL_UINT8(0x77u, received[0]);
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)spi_fake.transfers);
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)i2c_fake.transactions);

    TEST_ASSERT_EQUAL_INT(PORT_OK, i2c.read(i2c.ctx, 0x0Au, received, 1u));
    TEST_ASSERT_EQUAL_UINT8(0x77u, received[0]);
}

static void test_fake_log_captures_level_and_text(void)
{
    const host_fake_log_line_t *line;

    port_log_write(&log_contract, PORT_LOG_WARN, "bus not ready");

    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)host_fake_log_count(&log_fake));
    line = host_fake_log_at(&log_fake, 0u);
    TEST_ASSERT_NOT_NULL(line);
    TEST_ASSERT_EQUAL_INT(PORT_LOG_WARN, line->level);
    TEST_ASSERT_EQUAL_STRING("bus not ready", line->text);

    port_log_write(&log_contract, PORT_LOG_ERROR, NULL);
    line = host_fake_log_at(&log_fake, 1u);
    TEST_ASSERT_NOT_NULL(line);
    TEST_ASSERT_EQUAL_INT('\0', line->text[0]);
    TEST_ASSERT_EQUAL_UINT32(2u, (uint32_t)host_fake_log_count(&log_fake));
}

static void test_fake_log_truncates_long_text_safely(void)
{
    char message[HOST_FAKE_LOG_TEXT + 16u];
    const host_fake_log_line_t *line;
    size_t index;

    for (index = 0u; index + 1u < sizeof(message); ++index) {
        message[index] = 'x';
    }
    message[sizeof(message) - 1u] = '\0';

    port_log_write(&log_contract, PORT_LOG_INFO, message);

    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)host_fake_log_count(&log_fake));
    line = host_fake_log_at(&log_fake, 0u);
    TEST_ASSERT_NOT_NULL(line);
    TEST_ASSERT_EQUAL_INT('x', line->text[HOST_FAKE_LOG_TEXT - 2u]);
    TEST_ASSERT_EQUAL_INT('\0', line->text[HOST_FAKE_LOG_TEXT - 1u]);
}

static void test_fake_log_drops_after_capacity(void)
{
    size_t index;

    for (index = 0u; index < HOST_FAKE_LOG_LINES; ++index) {
        port_log_write(&log_contract, PORT_LOG_DEBUG, "line");
    }
    TEST_ASSERT_EQUAL_UINT32((uint32_t)HOST_FAKE_LOG_LINES, (uint32_t)host_fake_log_count(&log_fake));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)log_fake.dropped);

    port_log_write(&log_contract, PORT_LOG_DEBUG, "overflow");
    TEST_ASSERT_EQUAL_UINT32((uint32_t)HOST_FAKE_LOG_LINES, (uint32_t)host_fake_log_count(&log_fake));
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)log_fake.dropped);
}

static void test_fake_log_at_out_of_range_is_null(void)
{
    port_log_write(&log_contract, PORT_LOG_ERROR, "only line");

    TEST_ASSERT_NOT_NULL(host_fake_log_at(&log_fake, 0u));
    TEST_ASSERT_NULL(host_fake_log_at(&log_fake, 1u));
    TEST_ASSERT_NULL(host_fake_log_at(&log_fake, HOST_FAKE_LOG_LINES));
    TEST_ASSERT_NULL(host_fake_log_at(NULL, 0u));
}

static void test_all_fakes_expose_the_real_contract_types(void)
{
    port_time_t time_port = host_fake_time_port(&time_fake);
    port_gpio_t gpio_contract = host_fake_gpio_port(&fake);
    port_i2c_t i2c_contract = host_fake_i2c_port(&i2c_fake);
    port_spi_t spi_contract = host_fake_spi_port(&spi_fake);
    port_log_t log_port = host_fake_log_port(&log_fake);

    TEST_ASSERT_EQUAL_PTR(&time_fake, time_port.ctx);
    TEST_ASSERT_EQUAL_PTR(&fake, gpio_contract.ctx);
    TEST_ASSERT_EQUAL_PTR(&i2c_fake, i2c_contract.ctx);
    TEST_ASSERT_EQUAL_PTR(&spi_fake, spi_contract.ctx);
    TEST_ASSERT_EQUAL_PTR(&log_fake, log_port.ctx);

    port_log_write(&log_port, PORT_LOG_ERROR, "contract");
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)host_fake_log_count(&log_fake));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_fake_gpio_records_writes);
    RUN_TEST(test_fake_gpio_replays_levels);
    RUN_TEST(test_fake_gpio_out_of_range_pin_is_rejected);
    RUN_TEST(test_fake_gpio_forced_status_is_one_shot);
    RUN_TEST(test_fake_gpio_set_mode_and_write_mark_configured);
    RUN_TEST(test_gpio_fake_returns_the_real_gpio_contract_type);
    RUN_TEST(test_fake_i2c_write_then_read);
    RUN_TEST(test_fake_i2c_combined_transfer);
    RUN_TEST(test_fake_i2c_oversized_write_is_rejected);
    RUN_TEST(test_fake_i2c_two_instances_hold_separate_buffers);
    RUN_TEST(test_fake_spi_loops_back);
    RUN_TEST(test_fake_spi_write_records_without_receive_buffer);
    RUN_TEST(test_bus_fakes_keep_separate_contexts);
    RUN_TEST(test_fake_log_captures_level_and_text);
    RUN_TEST(test_fake_log_truncates_long_text_safely);
    RUN_TEST(test_fake_log_drops_after_capacity);
    RUN_TEST(test_fake_log_at_out_of_range_is_null);
    RUN_TEST(test_all_fakes_expose_the_real_contract_types);
    return UNITY_END();
}
