#include <stddef.h>

#include <unity.h>

#include "bounce_logic.h"

/* The suite is framework-free: it exercises the pure analysis that the
   firmware shares with the host build. Timestamps are hand-written so every
   expectation is arithmetic rather than a recorded trace. */

void setUp(void) {}

void tearDown(void) {}

static void test_capture_preserves_order_and_reports_overflow(void)
{
    bounce_capture_t capture;
    bounce_edge_t edge;
    size_t index;

    bounce_capture_reset(&capture);
    TEST_ASSERT_EQUAL_UINT(0u, bounce_capture_count(&capture));

    for (index = 0u; index < BOUNCE_CAPTURE_CAPACITY; index++) {
        TEST_ASSERT_TRUE(bounce_capture_push(&capture, (uint32_t)index, (index & 1u) != 0u));
    }

    TEST_ASSERT_EQUAL_UINT(BOUNCE_CAPTURE_CAPACITY, bounce_capture_count(&capture));
    TEST_ASSERT_TRUE(bounce_capture_at(&capture, 0u, &edge));
    TEST_ASSERT_EQUAL_UINT32(0u, edge.at_us);
    TEST_ASSERT_FALSE(edge.level);
    TEST_ASSERT_TRUE(bounce_capture_at(&capture, BOUNCE_CAPTURE_CAPACITY - 1u, &edge));
    TEST_ASSERT_EQUAL_UINT32((uint32_t)(BOUNCE_CAPTURE_CAPACITY - 1u), edge.at_us);

    TEST_ASSERT_FALSE(bounce_capture_push(&capture, 999u, true));
    TEST_ASSERT_TRUE(capture.overflowed);
    TEST_ASSERT_EQUAL_UINT(BOUNCE_CAPTURE_CAPACITY, bounce_capture_count(&capture));
    TEST_ASSERT_FALSE(bounce_capture_at(&capture, BOUNCE_CAPTURE_CAPACITY, &edge));
    TEST_ASSERT_FALSE(bounce_capture_at(NULL, 0u, &edge));
    TEST_ASSERT_FALSE(bounce_capture_at(&capture, 0u, NULL));
}

static void test_capture_copy_is_bounded(void)
{
    bounce_capture_t capture;
    bounce_edge_t destination[4];
    size_t copied;

    bounce_capture_reset(&capture);
    TEST_ASSERT_TRUE(bounce_capture_push(&capture, 100u, true));
    TEST_ASSERT_TRUE(bounce_capture_push(&capture, 200u, false));
    TEST_ASSERT_TRUE(bounce_capture_push(&capture, 300u, true));

    copied = bounce_capture_copy(&capture, destination, 4u);
    TEST_ASSERT_EQUAL_UINT(3u, copied);
    TEST_ASSERT_EQUAL_UINT32(300u, destination[2].at_us);

    copied = bounce_capture_copy(&capture, destination, 2u);
    TEST_ASSERT_EQUAL_UINT(2u, copied);
    TEST_ASSERT_EQUAL_UINT32(200u, destination[1].at_us);
    TEST_ASSERT_EQUAL_UINT(0u, bounce_capture_copy(NULL, destination, 2u));
    TEST_ASSERT_EQUAL_UINT(0u, bounce_capture_copy(&capture, NULL, 2u));
    TEST_ASSERT_EQUAL_UINT(0u, bounce_capture_copy(&capture, destination, 0u));
}

static void test_clean_press_needs_no_debounce(void)
{
    const bounce_edge_t edges[] = {{1000u, false}};
    bounce_stats_t stats;

    TEST_ASSERT_TRUE(bounce_analyze(edges, 1u, false, &stats));
    TEST_ASSERT_TRUE(stats.valid);
    TEST_ASSERT_EQUAL_UINT(1u, stats.edges);
    TEST_ASSERT_EQUAL_UINT(1u, stats.falling);
    TEST_ASSERT_EQUAL_UINT(0u, stats.rising);
    TEST_ASSERT_EQUAL_UINT32(0u, stats.duration_us);
    TEST_ASSERT_EQUAL_UINT32(0u, stats.max_high_us);
    TEST_ASSERT_EQUAL_UINT32(0u, stats.min_stable_ms);
    TEST_ASSERT_TRUE(stats.settled_low);
}

static void test_bouncing_press_counts_both_directions(void)
{
    const bounce_edge_t edges[] = {
        {100u, false}, {250u, true}, {400u, false}, {900u, true}, {1000u, false}, {1200u, true}, {1300u, false},
    };
    bounce_stats_t stats;

    TEST_ASSERT_TRUE(bounce_analyze(edges, 7u, false, &stats));
    TEST_ASSERT_EQUAL_UINT(4u, stats.falling);
    TEST_ASSERT_EQUAL_UINT(3u, stats.rising);
    TEST_ASSERT_EQUAL_UINT32(1200u, stats.duration_us);
    TEST_ASSERT_EQUAL_UINT32(150u, stats.max_high_us);
    TEST_ASSERT_EQUAL_UINT32(500u, stats.max_low_us);
    TEST_ASSERT_EQUAL_UINT32(1u, stats.min_stable_ms);
    TEST_ASSERT_TRUE(stats.settled_low);
}

static void test_long_high_gap_sets_the_window(void)
{
    const bounce_edge_t edges[] = {
        {0u, false},
        {500u, true},
        {4000u, false},
    };
    bounce_stats_t stats;

    TEST_ASSERT_TRUE(bounce_analyze(edges, 3u, false, &stats));
    TEST_ASSERT_EQUAL_UINT32(3500u, stats.max_high_us);
    TEST_ASSERT_EQUAL_UINT32(4u, stats.min_stable_ms);
    TEST_ASSERT_EQUAL_UINT(2u, stats.falling);
}

static void test_release_burst_is_not_a_press(void)
{
    const bounce_edge_t edges[] = {
        {100u, true},
        {200u, false},
        {3000u, true},
    };
    bounce_stats_t stats;

    TEST_ASSERT_TRUE(bounce_analyze(edges, 3u, false, &stats));
    TEST_ASSERT_FALSE(stats.settled_low);
    TEST_ASSERT_EQUAL_UINT(2u, stats.rising);
    TEST_ASSERT_EQUAL_UINT(1u, stats.falling);
    TEST_ASSERT_EQUAL_UINT32(100u, stats.max_high_us);
    TEST_ASSERT_EQUAL_UINT32(1u, stats.min_stable_ms);
}

static void test_duration_survives_the_microsecond_wrap(void)
{
    const bounce_edge_t edges[] = {
        {0xFFFFF000u, false},
        {0x00001000u, true},
    };
    bounce_stats_t stats;

    TEST_ASSERT_TRUE(bounce_analyze(edges, 2u, false, &stats));
    TEST_ASSERT_EQUAL_UINT32(8192u, stats.duration_us);
}

static void test_empty_or_invalid_input_is_rejected(void)
{
    bounce_edge_t edge = {0u, false};
    bounce_stats_t stats;

    TEST_ASSERT_FALSE(bounce_analyze(NULL, 0u, false, &stats));
    TEST_ASSERT_FALSE(stats.valid);
    TEST_ASSERT_EQUAL_UINT(0u, stats.edges);

    TEST_ASSERT_FALSE(bounce_analyze(&edge, 0u, false, &stats));
    TEST_ASSERT_FALSE(stats.valid);

    TEST_ASSERT_FALSE(bounce_analyze(&edge, 1u, true, NULL));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_capture_preserves_order_and_reports_overflow);
    RUN_TEST(test_capture_copy_is_bounded);
    RUN_TEST(test_clean_press_needs_no_debounce);
    RUN_TEST(test_bouncing_press_counts_both_directions);
    RUN_TEST(test_long_high_gap_sets_the_window);
    RUN_TEST(test_release_burst_is_not_a_press);
    RUN_TEST(test_duration_survives_the_microsecond_wrap);
    RUN_TEST(test_empty_or_invalid_input_is_rejected);
    return UNITY_END();
}
