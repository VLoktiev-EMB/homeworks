#include <stddef.h>
#include <stdint.h>

#include <unity.h>

#include "port/gpio.h"
#include "port/status.h"

/* File-scope fake state. Every callback receives the same pointer through its
   `ctx` argument, so observing the recorded pointer proves the plumbing. */
typedef struct fake_pin {
    uint8_t mode[4];
    port_gpio_level_t level[4];
    int writes;
    void *seen_ctx[3];
    int seen_count;
} fake_pin_t;

static void record_ctx(fake_pin_t *state, void *ctx) {
    if (state->seen_count < 3) {
        state->seen_ctx[state->seen_count] = ctx;
        state->seen_count++;
    }
}

static port_status_t fake_set_mode(void *ctx, uint8_t pin, port_gpio_mode_t mode) {
    fake_pin_t *state = ctx;

    if (state == NULL || pin >= 4u) {
        return PORT_ERR_INVALID_ARG;
    }
    record_ctx(state, ctx);
    state->mode[pin] = (uint8_t)mode;
    return PORT_OK;
}

static port_status_t fake_write(void *ctx, uint8_t pin, port_gpio_level_t level) {
    fake_pin_t *state = ctx;

    if (state == NULL || pin >= 4u) {
        return PORT_ERR_INVALID_ARG;
    }
    if (level != PORT_GPIO_LOW && level != PORT_GPIO_HIGH) {
        return PORT_ERR_INVALID_ARG;
    }
    record_ctx(state, ctx);
    state->level[pin] = level;
    state->writes++;
    return PORT_OK;
}

static port_status_t fake_read(void *ctx, uint8_t pin, port_gpio_level_t *level) {
    fake_pin_t *state = ctx;

    if (state == NULL || level == NULL || pin >= 4u) {
        return PORT_ERR_INVALID_ARG;
    }
    record_ctx(state, ctx);
    *level = state->level[pin];
    return PORT_OK;
}

void setUp(void) {}

void tearDown(void) {}

static void test_gpio_ctx_reaches_every_callback(void) {
    fake_pin_t state = {0};
    const port_gpio_t gpio = { fake_set_mode, fake_write, fake_read, &state };
    port_gpio_level_t level = PORT_GPIO_LOW;

    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.set_mode(gpio.ctx, 1u, PORT_GPIO_OUTPUT));
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.write(gpio.ctx, 1u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.read(gpio.ctx, 1u, &level));

    TEST_ASSERT_EQUAL_INT(3, state.seen_count);
    TEST_ASSERT_EQUAL_PTR(&state, state.seen_ctx[0]);
    TEST_ASSERT_EQUAL_PTR(&state, state.seen_ctx[1]);
    TEST_ASSERT_EQUAL_PTR(&state, state.seen_ctx[2]);
}

static void test_gpio_write_then_read_round_trip(void) {
    fake_pin_t state = {0};
    const port_gpio_t gpio = { fake_set_mode, fake_write, fake_read, &state };
    port_gpio_level_t level = PORT_GPIO_LOW;

    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.set_mode(gpio.ctx, 3u, PORT_GPIO_OUTPUT));
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.write(gpio.ctx, 3u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.read(gpio.ctx, 3u, &level));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, level);

    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.write(gpio.ctx, 3u, PORT_GPIO_LOW));
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio.read(gpio.ctx, 3u, &level));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, level);
    TEST_ASSERT_EQUAL_INT(2, state.writes);
}

static void test_gpio_invalid_level_is_rejected(void) {
    fake_pin_t state = {0};
    const port_gpio_t gpio = { fake_set_mode, fake_write, fake_read, &state };

    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG,
                          gpio.write(gpio.ctx, 0u, (port_gpio_level_t)99));
    TEST_ASSERT_EQUAL_INT(0, state.writes);
}

static void test_gpio_two_contexts_are_independent(void) {
    fake_pin_t first = {0};
    fake_pin_t second = {0};
    const port_gpio_t gpio_a = { fake_set_mode, fake_write, fake_read, &first };
    const port_gpio_t gpio_b = { fake_set_mode, fake_write, fake_read, &second };
    port_gpio_level_t level = PORT_GPIO_LOW;

    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio_a.write(gpio_a.ctx, 0u, PORT_GPIO_HIGH));
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio_b.write(gpio_b.ctx, 0u, PORT_GPIO_LOW));

    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio_a.read(gpio_a.ctx, 0u, &level));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, level);
    TEST_ASSERT_EQUAL_INT(PORT_OK, gpio_b.read(gpio_b.ctx, 0u, &level));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, level);

    TEST_ASSERT_EQUAL_INT(1, first.writes);
    TEST_ASSERT_EQUAL_INT(1, second.writes);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_gpio_ctx_reaches_every_callback);
    RUN_TEST(test_gpio_write_then_read_round_trip);
    RUN_TEST(test_gpio_invalid_level_is_rejected);
    RUN_TEST(test_gpio_two_contexts_are_independent);
    return UNITY_END();
}
