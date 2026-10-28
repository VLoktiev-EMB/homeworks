#include <stdint.h>

#include <unity.h>

#include "police_pattern.h"

/* The pattern library never reads a clock and never touches a framework type,
   so these tests drive it with an explicit millisecond value. */

void setUp(void) {}

void tearDown(void) {}

/* Advance exactly one step by moving the supplied clock to that step's
   deadline. The assertion proves the update accepted the boundary. */
static void advance_one(police_pattern_t *pattern, uint32_t *now_ms, police_outputs_t *outputs)
{
    *now_ms += police_pattern_step_duration_ms(pattern);
    TEST_ASSERT_TRUE(police_pattern_update(pattern, *now_ms, outputs));
}

static void test_init_reports_red_without_advancing(void)
{
    police_pattern_t pattern;
    police_outputs_t outputs = {POLICE_PAIR_OFF, false};

    police_pattern_init(&pattern, 0u);

    TEST_ASSERT_FALSE(police_pattern_update(&pattern, 0u, &outputs));
    TEST_ASSERT_EQUAL_INT(POLICE_PAIR_RED, outputs.pair);
    TEST_ASSERT_FALSE(outputs.white_on);
}

static void test_step_advances_only_at_its_deadline(void)
{
    police_pattern_t pattern;
    police_outputs_t outputs = {POLICE_PAIR_OFF, false};

    police_pattern_init(&pattern, 0u);

    TEST_ASSERT_FALSE(police_pattern_update(&pattern, 139u, &outputs));
    TEST_ASSERT_EQUAL_INT(POLICE_PAIR_RED, outputs.pair);

    TEST_ASSERT_TRUE(police_pattern_update(&pattern, 140u, &outputs));
    TEST_ASSERT_EQUAL_INT(POLICE_PAIR_OFF, outputs.pair);
    TEST_ASSERT_FALSE(outputs.white_on);
}

static void test_red_and_blue_alternate(void)
{
    static const police_pair_state_t expected[] = {
        POLICE_PAIR_RED, POLICE_PAIR_OFF,  POLICE_PAIR_RED, POLICE_PAIR_OFF, POLICE_PAIR_BLUE,
        POLICE_PAIR_OFF, POLICE_PAIR_BLUE, POLICE_PAIR_OFF, POLICE_PAIR_OFF, POLICE_PAIR_OFF,
        POLICE_PAIR_OFF, POLICE_PAIR_OFF,  POLICE_PAIR_OFF, POLICE_PAIR_OFF,
    };
    police_pattern_t pattern;
    police_outputs_t outputs = {POLICE_PAIR_OFF, false};
    uint32_t now_ms = 0u;
    uint16_t step;

    police_pattern_init(&pattern, now_ms);
    /* Fill the outputs for step 0; the call reports no advance. */
    TEST_ASSERT_FALSE(police_pattern_update(&pattern, now_ms, &outputs));

    for (step = 0u; step < (uint16_t)(sizeof(expected) / sizeof(expected[0])); step++) {
        TEST_ASSERT_EQUAL_INT(expected[step], outputs.pair);
        if (step + 1u < (uint16_t)(sizeof(expected) / sizeof(expected[0]))) {
            advance_one(&pattern, &now_ms, &outputs);
        }
    }
}

static void test_white_strobe_has_its_own_phase(void)
{
    police_pattern_t pattern;
    police_outputs_t outputs = {POLICE_PAIR_OFF, false};
    uint32_t now_ms = 0u;
    uint16_t step;

    police_pattern_init(&pattern, now_ms);

    /* Steps 0..7 are the red/blue phase: the white LED stays off. */
    for (step = 0u; step < 8u; step++) {
        TEST_ASSERT_FALSE(outputs.white_on);
        advance_one(&pattern, &now_ms, &outputs);
    }

    TEST_ASSERT_TRUE(outputs.white_on);
    advance_one(&pattern, &now_ms, &outputs);
    TEST_ASSERT_FALSE(outputs.white_on);
    advance_one(&pattern, &now_ms, &outputs);
    TEST_ASSERT_TRUE(outputs.white_on);
}

static void test_cycle_boundary_doubles_the_cadence(void)
{
    police_pattern_t pattern;
    police_outputs_t outputs = {POLICE_PAIR_OFF, false};
    uint32_t now_ms = 0u;
    uint16_t step;

    police_pattern_init(&pattern, now_ms);
    TEST_ASSERT_EQUAL_UINT32(140u, police_pattern_step_duration_ms(&pattern));

    for (step = 0u; step < 14u; step++) {
        advance_one(&pattern, &now_ms, &outputs);
    }

    TEST_ASSERT_EQUAL_UINT16(1u, pattern.cycle);
    TEST_ASSERT_EQUAL_UINT16(0u, pattern.step);
    TEST_ASSERT_TRUE(pattern.slow);
    TEST_ASSERT_EQUAL_UINT32(280u, police_pattern_step_duration_ms(&pattern));
}

static void test_deadline_survives_the_millisecond_wrap(void)
{
    police_pattern_t pattern;
    police_outputs_t outputs = {POLICE_PAIR_OFF, false};
    uint32_t now_ms;

    police_pattern_init(&pattern, 0xFFFFFFF0u);
    now_ms = (uint32_t)0xFFFFFFF0u + 148u;

    TEST_ASSERT_TRUE(police_pattern_update(&pattern, now_ms, &outputs));
    TEST_ASSERT_EQUAL_UINT16(1u, pattern.step);
}

static void test_null_arguments_are_ignored(void)
{
    police_pattern_t pattern;
    police_outputs_t outputs = {POLICE_PAIR_OFF, false};

    police_pattern_init(&pattern, 0u);
    police_pattern_init(NULL, 0u);

    TEST_ASSERT_FALSE(police_pattern_update(NULL, 0u, &outputs));
    TEST_ASSERT_FALSE(police_pattern_update(&pattern, 0u, NULL));
    TEST_ASSERT_EQUAL_UINT32(0u, police_pattern_step_duration_ms(NULL));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_init_reports_red_without_advancing);
    RUN_TEST(test_step_advances_only_at_its_deadline);
    RUN_TEST(test_red_and_blue_alternate);
    RUN_TEST(test_white_strobe_has_its_own_phase);
    RUN_TEST(test_cycle_boundary_doubles_the_cadence);
    RUN_TEST(test_deadline_survives_the_millisecond_wrap);
    RUN_TEST(test_null_arguments_are_ignored);
    return UNITY_END();
}
