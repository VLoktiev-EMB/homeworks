#include <stdint.h>

#include <unity.h>

#include "host/fake_time.h"
#include "port/time.h"

static host_fake_time_t fake;

void setUp(void)
{
    /* Non-zero on purpose: the reset case proves it clears any value. */
    fake.now_ms = 0xDEADBEEFu;
}

void tearDown(void) {}

static void test_fake_time_reset(void)
{
    port_time_t port;

    host_fake_time_reset(&fake);
    TEST_ASSERT_EQUAL_UINT32(0u, fake.now_ms);
    port = host_fake_time_port(&fake);
    TEST_ASSERT_EQUAL_UINT32(0u, port_time_now_ms(&port));
}

static void test_fake_time_advance(void)
{
    port_time_t port;

    host_fake_time_reset(&fake);
    port = host_fake_time_port(&fake);
    host_fake_time_advance(&fake, 250u);
    TEST_ASSERT_EQUAL_UINT32(250u, port_time_now_ms(&port));
    host_fake_time_advance(&fake, 750u);
    TEST_ASSERT_EQUAL_UINT32(1000u, fake.now_ms);
    /* The port borrows the struct, so a port obtained earlier sees the advance. */
    TEST_ASSERT_EQUAL_UINT32(1000u, port_time_now_ms(&port));
}

static void test_fake_time_wraps(void)
{
    port_time_t port;

    host_fake_time_reset(&fake);
    port = host_fake_time_port(&fake);
    host_fake_time_advance(&fake, UINT32_MAX);
    TEST_ASSERT_EQUAL_UINT32(UINT32_MAX, fake.now_ms);
    TEST_ASSERT_EQUAL_UINT32(UINT32_MAX, port_time_now_ms(&port));
    host_fake_time_advance(&fake, 1u);
    TEST_ASSERT_EQUAL_UINT32(0u, fake.now_ms);
    TEST_ASSERT_EQUAL_UINT32(0u, port_time_now_ms(&port));
}

static void test_two_fakes_are_independent(void)
{
    host_fake_time_t first = {0u};
    host_fake_time_t second = {0u};
    port_time_t first_port;
    port_time_t second_port;

    first_port = host_fake_time_port(&first);
    second_port = host_fake_time_port(&second);

    host_fake_time_advance(&first, 123u);
    host_fake_time_advance(&second, 7u);
    TEST_ASSERT_EQUAL_UINT32(123u, port_time_now_ms(&first_port));
    TEST_ASSERT_EQUAL_UINT32(7u, port_time_now_ms(&second_port));

    host_fake_time_reset(&second);
    TEST_ASSERT_EQUAL_UINT32(123u, port_time_now_ms(&first_port));
    TEST_ASSERT_EQUAL_UINT32(0u, port_time_now_ms(&second_port));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_fake_time_reset);
    RUN_TEST(test_fake_time_advance);
    RUN_TEST(test_fake_time_wraps);
    RUN_TEST(test_two_fakes_are_independent);
    return UNITY_END();
}
