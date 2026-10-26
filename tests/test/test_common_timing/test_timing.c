#include <stddef.h>

#include <unity.h>

#include "common/timing.h"
#include "host/fake_time.h"

static host_fake_time_t fake;
static common_debounce_t debounce;

void setUp(void)
{
    host_fake_time_reset(&fake);
    debounce.stable = false;
    debounce.candidate = false;
    debounce.candidate_since_ms = 0u;
}

void tearDown(void) {}

static void test_elapsed_handles_wraparound(void)
{
    TEST_ASSERT_EQUAL_UINT32(32u, common_elapsed_ms(0x00000010u, 0xFFFFFFF0u));
}

static void test_elapsed_is_zero(void)
{
    TEST_ASSERT_EQUAL_UINT32(0u, common_elapsed_ms(0u, 0u));
    TEST_ASSERT_EQUAL_UINT32(0u, common_elapsed_ms(1234u, 1234u));
}

static void test_timer_expired_at_deadline(void)
{
    TEST_ASSERT_TRUE(common_timer_expired(100u, 100u));
    TEST_ASSERT_FALSE(common_timer_expired(99u, 100u));
}

static void test_timer_expired_at_wraparound(void)
{
    /* A deadline just below the wrap expires once time passes it. */
    TEST_ASSERT_FALSE(common_timer_expired(0xFFFFFFE0u, 0xFFFFFFF0u));
    TEST_ASSERT_TRUE(common_timer_expired(0x00000010u, 0xFFFFFFF0u));
}

static void test_timer_expired_beyond_signed_horizon(void)
{
    /* 0xC0000000 is more than 2^31 - 1 ms ahead, so the signed difference is
       positive and a deadline past the ~24.85-day horizon reads as expired. */
    TEST_ASSERT_TRUE(common_timer_expired(0u, 0xC0000000u));
}

static void test_debounce_waits_stable_ms(void)
{
    const port_time_t clock = host_fake_time_port(&fake);

    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, true, 50u));
    host_fake_time_advance(&fake, 49u);
    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, true, 50u));
}

static void test_debounce_flips_at_stable_ms(void)
{
    const port_time_t clock = host_fake_time_port(&fake);

    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, true, 50u));
    host_fake_time_advance(&fake, 50u);
    TEST_ASSERT_TRUE(common_debounce_update(&debounce, &clock, true, 50u));
}

static void test_debounce_restarts_window(void)
{
    const port_time_t clock = host_fake_time_port(&fake);

    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, true, 50u));
    host_fake_time_advance(&fake, 30u);
    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, false, 50u));
    host_fake_time_advance(&fake, 30u);
    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, true, 50u));
    host_fake_time_advance(&fake, 20u);
    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, true, 50u));
}

static void test_debounce_window_restarts(void)
{
    const port_time_t clock = host_fake_time_port(&fake);

    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, true, 40u));
    host_fake_time_advance(&fake, 25u);
    /* Returning to the stable level cancels the pending change. */
    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, false, 40u));
    host_fake_time_advance(&fake, 15u);
    /* A fresh candidate at t=40 must wait its own 40 ms, not promote at t=40. */
    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, true, 40u));
    host_fake_time_advance(&fake, 39u);
    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, true, 40u));
    host_fake_time_advance(&fake, 1u);
    TEST_ASSERT_TRUE(common_debounce_update(&debounce, &clock, true, 40u));
}

static void test_debounce_zero_stable_ms(void)
{
    const port_time_t clock = host_fake_time_port(&fake);

    /* A zero window promotes the candidate on the first observing call. */
    TEST_ASSERT_TRUE(common_debounce_update(&debounce, &clock, true, 0u));
}

static void test_debounce_null_state_is_safe(void)
{
    const port_time_t clock = host_fake_time_port(&fake);

    TEST_ASSERT_FALSE(common_debounce_update(NULL, &clock, true, 10u));
}

static void test_debounce_null_time_is_safe(void)
{
    common_debounce_t state = {true, false, 0u};

    TEST_ASSERT_TRUE(common_debounce_update(&state, NULL, false, 10u));
}

static void test_debounce_null_callback_is_safe(void)
{
    port_time_t broken = {.now_ms = NULL, .ctx = NULL};
    common_debounce_t state = {true, false, 0u};

    TEST_ASSERT_TRUE(common_debounce_update(&state, &broken, false, 10u));
    state.stable = false;
    TEST_ASSERT_FALSE(common_debounce_update(&state, &broken, true, 10u));
}

static void test_two_debounces_are_independent(void)
{
    const port_time_t clock = host_fake_time_port(&fake);
    common_debounce_t first = {false, false, 0u};
    common_debounce_t second = {false, false, 0u};

    TEST_ASSERT_FALSE(common_debounce_update(&first, &clock, true, 10u));
    TEST_ASSERT_FALSE(common_debounce_update(&second, &clock, false, 10u));
    host_fake_time_advance(&fake, 10u);
    TEST_ASSERT_TRUE(common_debounce_update(&first, &clock, true, 10u));
    TEST_ASSERT_FALSE(common_debounce_update(&second, &clock, false, 10u));
}

static void test_debounce_uses_fake_time(void)
{
    const port_time_t clock = host_fake_time_port(&fake);

    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, true, 50u));
    host_fake_time_advance(&fake, 49u);
    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, true, 50u));
    host_fake_time_advance(&fake, 1u);
    TEST_ASSERT_TRUE(common_debounce_update(&debounce, &clock, true, 50u));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_elapsed_handles_wraparound);
    RUN_TEST(test_elapsed_is_zero);
    RUN_TEST(test_timer_expired_at_deadline);
    RUN_TEST(test_timer_expired_at_wraparound);
    RUN_TEST(test_timer_expired_beyond_signed_horizon);
    RUN_TEST(test_debounce_waits_stable_ms);
    RUN_TEST(test_debounce_flips_at_stable_ms);
    RUN_TEST(test_debounce_restarts_window);
    RUN_TEST(test_debounce_window_restarts);
    RUN_TEST(test_debounce_zero_stable_ms);
    RUN_TEST(test_debounce_null_state_is_safe);
    RUN_TEST(test_debounce_null_time_is_safe);
    RUN_TEST(test_debounce_null_callback_is_safe);
    RUN_TEST(test_two_debounces_are_independent);
    RUN_TEST(test_debounce_uses_fake_time);
    return UNITY_END();
}
