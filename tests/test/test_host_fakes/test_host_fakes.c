#include <stddef.h>
#include <stdint.h>

#include <unity.h>

#include "host/fake_gpio.h"
#include "port/gpio.h"

static host_fake_gpio_t fake;
static port_gpio_t gpio;

void setUp(void) {
    host_fake_gpio_reset(&fake);
    gpio = host_fake_gpio_port(&fake);
}

void tearDown(void) {}

static void test_fake_gpio_records_writes(void) {
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.write(gpio.ctx, 5u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)fake.writes);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake.level[5]);
}

static void test_fake_gpio_replays_levels(void) {
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

static void test_fake_gpio_out_of_range_pin_is_rejected(void) {
    port_gpio_level_t level = PORT_GPIO_LOW;

    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG,
                          gpio.write(gpio.ctx, HOST_FAKE_GPIO_PINS, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)fake.writes);
    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG,
                          gpio.set_mode(gpio.ctx, HOST_FAKE_GPIO_PINS, PORT_GPIO_OUTPUT));
    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG,
                          gpio.read(gpio.ctx, HOST_FAKE_GPIO_PINS, &level));
    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, gpio.read(gpio.ctx, 0u, NULL));
}

static void test_fake_gpio_forced_status_is_one_shot(void) {
    host_fake_gpio_fail_next(&fake, PORT_ERR_IO);

    TEST_ASSERT_EQUAL_INT(PORT_ERR_IO, gpio.write(gpio.ctx, 1u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)fake.writes);
    TEST_ASSERT_EQUAL_INT(PORT_OK, fake.forced_status);

    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.write(gpio.ctx, 1u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)fake.writes);
}

static void test_fake_gpio_set_mode_and_write_mark_configured(void) {
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

static void test_gpio_fake_returns_the_real_gpio_contract_type(void) {
    port_gpio_t returned = host_fake_gpio_port(&fake);

    TEST_ASSERT_EQUAL_PTR(&fake, returned.ctx);
    TEST_ASSERT_EQUAL_INT(PORT_OK, returned.write(returned.ctx, 2u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake.level[2]);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_fake_gpio_records_writes);
    RUN_TEST(test_fake_gpio_replays_levels);
    RUN_TEST(test_fake_gpio_out_of_range_pin_is_rejected);
    RUN_TEST(test_fake_gpio_forced_status_is_one_shot);
    RUN_TEST(test_fake_gpio_set_mode_and_write_mark_configured);
    RUN_TEST(test_gpio_fake_returns_the_real_gpio_contract_type);
    return UNITY_END();
}
