#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include <unity.h>

#include "common/hex.h"

#define CANARY_ENCODE 'X'
#define CANARY_DECODE 0x5Au

void setUp(void) {}

void tearDown(void) {}

static void test_hex_encode_known_bytes(void) {
    static const uint8_t input[] = {0x00u, 0x7Fu, 0xFFu};
    char out[7];
    size_t out_length = 99u;

    TEST_ASSERT_TRUE(common_hex_encode(input, sizeof(input), out, sizeof(out), &out_length));
    TEST_ASSERT_EQUAL_UINT32(6u, (uint32_t)out_length);
    TEST_ASSERT_EQUAL_STRING("007fff", out);
    TEST_ASSERT_EQUAL_CHAR('\0', out[6]);
}

static void test_hex_round_trip(void) {
    uint8_t source[256];
    uint8_t decoded[256];
    char encoded[513];
    size_t encoded_length = 0u;
    size_t decoded_length = 0u;
    size_t index;

    for (index = 0u; index < sizeof(source); index++) {
        source[index] = (uint8_t)index;
    }

    TEST_ASSERT_TRUE(
        common_hex_encode(source, sizeof(source), encoded, sizeof(encoded), &encoded_length));
    TEST_ASSERT_EQUAL_UINT32(512u, (uint32_t)encoded_length);
    TEST_ASSERT_EQUAL_CHAR('\0', encoded[512]);

    TEST_ASSERT_TRUE(common_hex_decode(encoded, encoded_length, decoded, sizeof(decoded),
                                       &decoded_length));
    TEST_ASSERT_EQUAL_UINT32(256u, (uint32_t)decoded_length);
    TEST_ASSERT_EQUAL_MEMORY(source, decoded, sizeof(source));
}

static void test_hex_decode_accepts_uppercase(void) {
    uint8_t out[2] = {0u, 0u};
    size_t out_length = 0u;

    TEST_ASSERT_TRUE(common_hex_decode("A0fF", 4u, out, sizeof(out), &out_length));
    TEST_ASSERT_EQUAL_UINT32(2u, (uint32_t)out_length);
    TEST_ASSERT_EQUAL_UINT8(0xA0u, out[0]);
    TEST_ASSERT_EQUAL_UINT8(0xFFu, out[1]);
}

static void test_hex_decode_rejects_odd_length(void) {
    uint8_t out[2] = {CANARY_DECODE, CANARY_DECODE};
    size_t out_length = 99u;

    TEST_ASSERT_FALSE(common_hex_decode("abc", 3u, out, sizeof(out), &out_length));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)out_length);
    TEST_ASSERT_EQUAL_UINT8(CANARY_DECODE, out[0]);
}

static void test_hex_decode_rejects_non_hex_character(void) {
    uint8_t out[2] = {CANARY_DECODE, CANARY_DECODE};
    size_t out_length = 99u;

    TEST_ASSERT_FALSE(common_hex_decode("zz", 2u, out, sizeof(out), &out_length));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)out_length);
    TEST_ASSERT_EQUAL_UINT8(CANARY_DECODE, out[0]);

    TEST_ASSERT_FALSE(common_hex_decode("0g", 2u, out, sizeof(out), &out_length));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)out_length);
    TEST_ASSERT_EQUAL_UINT8(CANARY_DECODE, out[0]);
}

static void test_hex_encode_zero_length(void) {
    char out[1] = {CANARY_ENCODE};
    size_t out_length = 99u;

    TEST_ASSERT_TRUE(common_hex_encode(NULL, 0u, out, sizeof(out), &out_length));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)out_length);
    TEST_ASSERT_EQUAL_CHAR('\0', out[0]);
}

static void test_hex_decode_zero_length(void) {
    size_t out_length = 99u;

    TEST_ASSERT_TRUE(common_hex_decode(NULL, 0u, NULL, 0u, &out_length));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)out_length);
}

static void test_hex_insufficient_capacity_writes_nothing(void) {
    static const uint8_t one_byte[] = {0xABu};
    char encoded[4];
    uint8_t decoded[4];
    size_t out_length;

    /* Encode needs 2 * 1 + 1 = 3 bytes; two is one short. */
    encoded[0] = CANARY_ENCODE;
    encoded[1] = CANARY_ENCODE;
    out_length = 99u;
    TEST_ASSERT_FALSE(common_hex_encode(one_byte, 1u, encoded, 2u, &out_length));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)out_length);
    TEST_ASSERT_EQUAL_CHAR(CANARY_ENCODE, encoded[0]);
    TEST_ASSERT_EQUAL_CHAR(CANARY_ENCODE, encoded[1]);

    /* Decode needs length / 2 = 2 bytes; one is one short. */
    decoded[0] = CANARY_DECODE;
    decoded[1] = CANARY_DECODE;
    out_length = 99u;
    TEST_ASSERT_FALSE(common_hex_decode("a0b1", 4u, decoded, 1u, &out_length));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)out_length);
    TEST_ASSERT_EQUAL_UINT8(CANARY_DECODE, decoded[0]);
    TEST_ASSERT_EQUAL_UINT8(CANARY_DECODE, decoded[1]);

    /* A NULL out_length is a caller error on both paths. */
    TEST_ASSERT_FALSE(common_hex_encode(one_byte, 1u, encoded, sizeof(encoded), NULL));
    TEST_ASSERT_FALSE(common_hex_decode("a0", 2u, decoded, sizeof(decoded), NULL));
}

static void test_hex_enough_capacity_is_required(void) {
    static const uint8_t one_byte[] = {0xFFu};
    char encoded[3];
    uint8_t decoded[1];
    size_t out_length = 99u;

    /* Exact boundaries succeed: 2 * 1 + 1 for encode, 2 / 2 for decode. */
    TEST_ASSERT_TRUE(common_hex_encode(one_byte, 1u, encoded, 3u, &out_length));
    TEST_ASSERT_EQUAL_UINT32(2u, (uint32_t)out_length);
    TEST_ASSERT_EQUAL_STRING("ff", encoded);

    TEST_ASSERT_TRUE(common_hex_decode("ff", 2u, decoded, 1u, &out_length));
    TEST_ASSERT_EQUAL_UINT32(1u, (uint32_t)out_length);
    TEST_ASSERT_EQUAL_UINT8(0xFFu, decoded[0]);

    /* A zero-capacity encode cannot hold even the terminator. */
    out_length = 99u;
    TEST_ASSERT_FALSE(common_hex_encode(NULL, 0u, encoded, 0u, &out_length));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)out_length);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_hex_encode_known_bytes);
    RUN_TEST(test_hex_round_trip);
    RUN_TEST(test_hex_decode_accepts_uppercase);
    RUN_TEST(test_hex_decode_rejects_odd_length);
    RUN_TEST(test_hex_decode_rejects_non_hex_character);
    RUN_TEST(test_hex_encode_zero_length);
    RUN_TEST(test_hex_decode_zero_length);
    RUN_TEST(test_hex_insufficient_capacity_writes_nothing);
    RUN_TEST(test_hex_enough_capacity_is_required);
    return UNITY_END();
}
