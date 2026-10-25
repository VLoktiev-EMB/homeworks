#include <stddef.h>

#include <unity.h>

#include "pattern/pattern.h"

void setUp(void) {}

void tearDown(void) {}

static void test_alternating_frames_alternate_a_and_b(void) {
    static const bool expected_a[4] = {true, false, true, false};
    static const bool expected_b[4] = {false, true, false, true};
    static const bool expected_c[4] = {false, false, true, true};
    size_t index;

    TEST_ASSERT_EQUAL_UINT(4u, (unsigned)pattern_frame_count(PATTERN_MODE_ALTERNATING));
    for (index = 0u; index < 4u; ++index) {
        pattern_frame_t frame =
            pattern_frame_at(PATTERN_MODE_ALTERNATING, (uint16_t)index, 400u);

        TEST_ASSERT_TRUE(frame.led_a == expected_a[index]);
        TEST_ASSERT_TRUE(frame.led_b == expected_b[index]);
        TEST_ASSERT_TRUE(frame.led_c == expected_c[index]);
        TEST_ASSERT_EQUAL_UINT(400u, (unsigned)frame.hold_ms);
        /* Exactly one of the anti-parallel pair is active on every frame. */
        TEST_ASSERT_TRUE(frame.led_a != frame.led_b);
    }
}

static void test_frame_count_per_mode(void) {
    TEST_ASSERT_EQUAL_UINT(4u, (unsigned)pattern_frame_count(PATTERN_MODE_ALTERNATING));
    TEST_ASSERT_EQUAL_UINT(8u, (unsigned)pattern_frame_count(PATTERN_MODE_DOUBLE_FLASH));
    TEST_ASSERT_EQUAL_UINT(4u, (unsigned)pattern_frame_count(PATTERN_MODE_CHASE));
    TEST_ASSERT_EQUAL_UINT(1u, (unsigned)pattern_frame_count(PATTERN_MODE_SOLID));
}

static void test_mode_cycle_wraps(void) {
    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_DOUBLE_FLASH,
                          pattern_mode_next(PATTERN_MODE_ALTERNATING));
    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_CHASE,
                          pattern_mode_next(PATTERN_MODE_DOUBLE_FLASH));
    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_SOLID, pattern_mode_next(PATTERN_MODE_CHASE));
    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_ALTERNATING,
                          pattern_mode_next(PATTERN_MODE_SOLID));
}

static void test_mode_cycle_rejects_an_invalid_mode(void) {
    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_ALTERNATING,
                          pattern_mode_next((pattern_mode_t)99));
}

static void test_speed_table(void) {
    TEST_ASSERT_EQUAL_UINT(3u, (unsigned)pattern_speed_count());
    TEST_ASSERT_EQUAL_UINT(400u, (unsigned)pattern_speed_base_ms(0u));
    TEST_ASSERT_EQUAL_UINT(200u, (unsigned)pattern_speed_base_ms(1u));
    TEST_ASSERT_EQUAL_UINT(100u, (unsigned)pattern_speed_base_ms(2u));
    TEST_ASSERT_EQUAL_UINT(400u, (unsigned)pattern_speed_base_ms(3u));
}

static void test_invalid_mode_frame_is_all_off_with_the_base_hold(void) {
    pattern_frame_t frame = pattern_frame_at((pattern_mode_t)99, 0u, 123u);

    TEST_ASSERT_FALSE(frame.led_a);
    TEST_ASSERT_FALSE(frame.led_b);
    TEST_ASSERT_FALSE(frame.led_c);
    TEST_ASSERT_EQUAL_UINT(123u, (unsigned)frame.hold_ms);
    TEST_ASSERT_EQUAL_UINT(1u, (unsigned)pattern_frame_count((pattern_mode_t)99));
}

static void test_invalid_step_frame_is_all_off_with_the_base_hold(void) {
    pattern_frame_t frame = pattern_frame_at(PATTERN_MODE_ALTERNATING, 4u, 400u);

    TEST_ASSERT_FALSE(frame.led_a);
    TEST_ASSERT_FALSE(frame.led_b);
    TEST_ASSERT_FALSE(frame.led_c);
    TEST_ASSERT_EQUAL_UINT(400u, (unsigned)frame.hold_ms);
}

static void test_every_frame_holds_at_least_25_ms_at_the_fastest_base(void) {
    pattern_mode_t mode;

    for (mode = PATTERN_MODE_ALTERNATING; mode < PATTERN_MODE_COUNT;
         mode = (pattern_mode_t)(mode + 1)) {
        size_t count = pattern_frame_count(mode);
        size_t index;

        for (index = 0u; index < count; ++index) {
            pattern_frame_t frame = pattern_frame_at(mode, (uint16_t)index, 100u);

            TEST_ASSERT_TRUE(frame.hold_ms >= 25u);
        }
    }
}

static void test_solid_frame_is_all_on_for_four_bases(void) {
    pattern_frame_t frame = pattern_frame_at(PATTERN_MODE_SOLID, 0u, 400u);

    TEST_ASSERT_TRUE(frame.led_a);
    TEST_ASSERT_TRUE(frame.led_b);
    TEST_ASSERT_TRUE(frame.led_c);
    TEST_ASSERT_EQUAL_UINT(1600u, (unsigned)frame.hold_ms);
}

static void test_equal_holds_remain_distinct_frames(void) {
    pattern_frame_t first = pattern_frame_at(PATTERN_MODE_ALTERNATING, 0u, 400u);
    pattern_frame_t second = pattern_frame_at(PATTERN_MODE_ALTERNATING, 1u, 400u);
    pattern_frame_t third = pattern_frame_at(PATTERN_MODE_ALTERNATING, 2u, 400u);

    TEST_ASSERT_EQUAL_UINT(first.hold_ms, third.hold_ms);
    TEST_ASSERT_TRUE(first.led_a != second.led_a);
    TEST_ASSERT_TRUE(first.led_c != third.led_c);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_alternating_frames_alternate_a_and_b);
    RUN_TEST(test_frame_count_per_mode);
    RUN_TEST(test_mode_cycle_wraps);
    RUN_TEST(test_mode_cycle_rejects_an_invalid_mode);
    RUN_TEST(test_speed_table);
    RUN_TEST(test_invalid_mode_frame_is_all_off_with_the_base_hold);
    RUN_TEST(test_invalid_step_frame_is_all_off_with_the_base_hold);
    RUN_TEST(test_every_frame_holds_at_least_25_ms_at_the_fastest_base);
    RUN_TEST(test_solid_frame_is_all_on_for_four_bases);
    RUN_TEST(test_equal_holds_remain_distinct_frames);
    return UNITY_END();
}
