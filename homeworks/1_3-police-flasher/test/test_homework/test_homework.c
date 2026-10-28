#include <stddef.h>

#include <unity.h>

#include "host/fake_gpio.h"
#include "port/gpio.h"

/* The fake is the test double for the consumer-owned GPIO contract: both tests
   exercise the contract itself, so the file stays framework-free and runs in
   [env:native]. */
void setUp(void) {}

void tearDown(void) {}

static void test_fake_records_a_write(void)
{
    host_fake_gpio_t fake;
    port_gpio_t port;

    host_fake_gpio_reset(&fake);
    port = host_fake_gpio_port(&fake);

    TEST_ASSERT_EQUAL_INT(PORT_OK, port.set_mode(port.ctx, 2u, PORT_GPIO_OUTPUT));
    TEST_ASSERT_EQUAL_INT(PORT_OK, port.write(port.ctx, 2u, PORT_GPIO_HIGH));

    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake.level[2]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_OUTPUT, fake.mode[2]);
    TEST_ASSERT_EQUAL_UINT(1u, fake.writes);
}

static void test_fake_rejects_a_pin_at_or_above_the_bound(void)
{
    host_fake_gpio_t fake;
    port_gpio_t port;

    host_fake_gpio_reset(&fake);
    port = host_fake_gpio_port(&fake);

    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, port.set_mode(port.ctx, HOST_FAKE_GPIO_PINS, PORT_GPIO_OUTPUT));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_fake_records_a_write);
    RUN_TEST(test_fake_rejects_a_pin_at_or_above_the_bound);
    return UNITY_END();
}
