#include <stddef.h>
#include <stdint.h>

#include <unity.h>

#include "common/ring_buffer.h"

#define STORAGE_CAPACITY 4u

static uint8_t storage[STORAGE_CAPACITY];
static common_ring_buffer_t rb;

void setUp(void)
{
    TEST_ASSERT_TRUE(common_ring_buffer_init(&rb, storage, STORAGE_CAPACITY));
}

void tearDown(void) {}

static void test_ring_buffer_starts_empty(void)
{
    uint8_t value = 0u;

    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)common_ring_buffer_count(&rb));
    TEST_ASSERT_EQUAL_UINT32((uint32_t)STORAGE_CAPACITY, (uint32_t)common_ring_buffer_capacity(&rb));
    TEST_ASSERT_FALSE(common_ring_buffer_pop(&rb, &value));
}

static void test_ring_buffer_push_and_pop_order(void)
{
    uint8_t value = 0u;

    TEST_ASSERT_TRUE(common_ring_buffer_push(&rb, 10u));
    TEST_ASSERT_TRUE(common_ring_buffer_push(&rb, 11u));
    TEST_ASSERT_EQUAL_UINT32(2u, (uint32_t)common_ring_buffer_count(&rb));

    TEST_ASSERT_TRUE(common_ring_buffer_pop(&rb, &value));
    TEST_ASSERT_EQUAL_UINT8(10u, value);
    TEST_ASSERT_TRUE(common_ring_buffer_pop(&rb, &value));
    TEST_ASSERT_EQUAL_UINT8(11u, value);
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)common_ring_buffer_count(&rb));
}

static void test_ring_buffer_full_returns_false(void)
{
    uint32_t index;

    for (index = 0u; index < STORAGE_CAPACITY; index++) {
        TEST_ASSERT_TRUE(common_ring_buffer_push(&rb, (uint8_t)index));
    }

    TEST_ASSERT_EQUAL_UINT32((uint32_t)STORAGE_CAPACITY, (uint32_t)common_ring_buffer_count(&rb));
    TEST_ASSERT_FALSE(common_ring_buffer_push(&rb, 99u));
    TEST_ASSERT_EQUAL_UINT32((uint32_t)STORAGE_CAPACITY, (uint32_t)common_ring_buffer_count(&rb));
}

static void test_ring_buffer_empty_returns_false(void)
{
    uint8_t value = 0u;

    TEST_ASSERT_FALSE(common_ring_buffer_pop(&rb, &value));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)common_ring_buffer_count(&rb));
}

static void test_ring_buffer_wraps_without_allocation(void)
{
    uint8_t value = 0u;

    /* Fill, drain two, then refill behind the tail so both indices wrap. */
    TEST_ASSERT_TRUE(common_ring_buffer_push(&rb, 12u));
    TEST_ASSERT_TRUE(common_ring_buffer_push(&rb, 13u));
    TEST_ASSERT_TRUE(common_ring_buffer_push(&rb, 14u));
    TEST_ASSERT_TRUE(common_ring_buffer_push(&rb, 15u));

    TEST_ASSERT_TRUE(common_ring_buffer_pop(&rb, &value));
    TEST_ASSERT_EQUAL_UINT8(12u, value);
    TEST_ASSERT_TRUE(common_ring_buffer_pop(&rb, &value));
    TEST_ASSERT_EQUAL_UINT8(13u, value);

    TEST_ASSERT_TRUE(common_ring_buffer_push(&rb, 20u));
    TEST_ASSERT_TRUE(common_ring_buffer_push(&rb, 21u));
    TEST_ASSERT_EQUAL_UINT32(4u, (uint32_t)common_ring_buffer_count(&rb));

    TEST_ASSERT_TRUE(common_ring_buffer_pop(&rb, &value));
    TEST_ASSERT_EQUAL_UINT8(14u, value);
    TEST_ASSERT_TRUE(common_ring_buffer_pop(&rb, &value));
    TEST_ASSERT_EQUAL_UINT8(15u, value);
    TEST_ASSERT_TRUE(common_ring_buffer_pop(&rb, &value));
    TEST_ASSERT_EQUAL_UINT8(20u, value);
    TEST_ASSERT_TRUE(common_ring_buffer_pop(&rb, &value));
    TEST_ASSERT_EQUAL_UINT8(21u, value);
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)common_ring_buffer_count(&rb));
    TEST_ASSERT_FALSE(common_ring_buffer_pop(&rb, &value));
}

static void test_ring_buffer_init_rejects_zero_capacity(void)
{
    common_ring_buffer_t candidate = {0};

    TEST_ASSERT_FALSE(common_ring_buffer_init(&candidate, storage, 0u));
    TEST_ASSERT_NULL(candidate.storage);
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)candidate.capacity);

    TEST_ASSERT_FALSE(common_ring_buffer_init(&candidate, NULL, STORAGE_CAPACITY));
    TEST_ASSERT_NULL(candidate.storage);

    TEST_ASSERT_FALSE(common_ring_buffer_init(NULL, storage, STORAGE_CAPACITY));
}

static void test_ring_buffer_zero_initialised_is_safe(void)
{
    common_ring_buffer_t zero = {0};
    uint8_t value = 0xAAu;

    /* The storage / capacity pair is the guard: a {0} struct is empty, not
       undefined. No call may crash or write through the NULL storage. */
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)common_ring_buffer_count(&zero));
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)common_ring_buffer_capacity(&zero));
    TEST_ASSERT_FALSE(common_ring_buffer_push(&zero, 1u));
    TEST_ASSERT_FALSE(common_ring_buffer_pop(&zero, &value));
    TEST_ASSERT_EQUAL_UINT8(0xAAu, value);

    common_ring_buffer_clear(&zero);
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)common_ring_buffer_count(&zero));

    /* NULL pointers are the same empty case. */
    TEST_ASSERT_EQUAL_UINT32(0u, (uint32_t)common_ring_buffer_count(NULL));
    TEST_ASSERT_FALSE(common_ring_buffer_push(NULL, 1u));
    TEST_ASSERT_FALSE(common_ring_buffer_pop(NULL, &value));
    common_ring_buffer_clear(NULL);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_ring_buffer_starts_empty);
    RUN_TEST(test_ring_buffer_push_and_pop_order);
    RUN_TEST(test_ring_buffer_full_returns_false);
    RUN_TEST(test_ring_buffer_empty_returns_false);
    RUN_TEST(test_ring_buffer_wraps_without_allocation);
    RUN_TEST(test_ring_buffer_init_rejects_zero_capacity);
    RUN_TEST(test_ring_buffer_zero_initialised_is_safe);
    return UNITY_END();
}
