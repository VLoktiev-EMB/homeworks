#include <stddef.h>
#include <stdint.h>

#include <unity.h>

#include "common/crc.h"

/* The standard check vector of the CRC-16/CCITT-FALSE catalogue entry. */
static const uint8_t CHECK_VECTOR[] = {'1', '2', '3', '4', '5', '6', '7', '8', '9'};
#define CHECK_VECTOR_LENGTH (sizeof(CHECK_VECTOR))

void setUp(void) {}

void tearDown(void) {}

static void test_crc16_check_value(void)
{
    TEST_ASSERT_EQUAL_HEX16(0x29B1u, common_crc16(CHECK_VECTOR, CHECK_VECTOR_LENGTH));
}

static void test_crc16_empty_input_is_initial_value(void)
{
    TEST_ASSERT_EQUAL_HEX16(0xFFFFu, common_crc16(NULL, 0u));
    TEST_ASSERT_EQUAL_HEX16(0xFFFFu, common_crc16_update(0xFFFFu, CHECK_VECTOR, 0u));
}

static void test_crc16_update_matches_one_shot(void)
{
    uint16_t incremental = common_crc16_update(0xFFFFu, CHECK_VECTOR, 4u);

    incremental = common_crc16_update(incremental, CHECK_VECTOR + 4u, CHECK_VECTOR_LENGTH - 4u);

    TEST_ASSERT_EQUAL_HEX16(common_crc16(CHECK_VECTOR, CHECK_VECTOR_LENGTH), incremental);
}

static void test_crc16_null_with_length_is_unchanged(void)
{
    /* The signature cannot report an error, so the unchanged input is the
       documented result; returning 0 would collide with a legitimate CRC. */
    TEST_ASSERT_EQUAL_HEX16(0x1234u, common_crc16_update(0x1234u, NULL, 5u));
    TEST_ASSERT_EQUAL_HEX16(0x0000u, common_crc16_update(0x0000u, NULL, 1u));
}

static void test_crc16_single_bit_change_differs(void)
{
    static const uint8_t original[] = {0x00u, 0x7Fu, 0xFFu, 0x42u};
    static const uint8_t flipped[] = {0x00u, 0x7Fu, 0xFEu, 0x42u};

    TEST_ASSERT_NOT_EQUAL(common_crc16(original, sizeof(original)), common_crc16(flipped, sizeof(flipped)));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_crc16_check_value);
    RUN_TEST(test_crc16_empty_input_is_initial_value);
    RUN_TEST(test_crc16_update_matches_one_shot);
    RUN_TEST(test_crc16_null_with_length_is_unchanged);
    RUN_TEST(test_crc16_single_bit_change_differs);
    return UNITY_END();
}
