#include <stdbool.h>
#include <stdint.h>

#include <unity.h>

#include "blink_modes/blink_modes.h"
#include "host/fake_gpio.h"
#include "host/fake_time.h"

/* Both buttons are active LOW. The fixture seeds the idle level HIGH and then
   mirrors the firmware poll sequence: one poll registers the new raw level,
   a later poll at least debounce_ms afterwards confirms it. */

static const blink_modes_config_t CONFIG = {
    .led_a_pin = 15u,
    .led_b_pin = 16u,
    .external_button_pin = 21u,
    .boot_button_pin = 0u,
    .fast_period_ms = 200u,
    .slow_period_ms = 1000u,
    .debounce_ms = 20u,
};

static host_fake_gpio_t fake_gpio;
static host_fake_time_t fake_time;
static blink_modes_t state;

void setUp(void)
{
    host_fake_gpio_reset(&fake_gpio);
    host_fake_time_reset(&fake_time);
    fake_gpio.level[CONFIG.external_button_pin] = PORT_GPIO_HIGH;
    fake_gpio.level[CONFIG.boot_button_pin] = PORT_GPIO_HIGH;
    TEST_ASSERT_EQUAL_INT(PORT_OK, blink_modes_init(&state, &CONFIG));
}

void tearDown(void) {}

static port_status_t update(void)
{
    port_gpio_t gpio = host_fake_gpio_port(&fake_gpio);
    port_time_t time = host_fake_time_port(&fake_time);

    return blink_modes_update(&state, &gpio, &time);
}

static void update_ok(void)
{
    TEST_ASSERT_EQUAL_INT(PORT_OK, update());
}

static void press(uint8_t pin)
{
    fake_gpio.level[pin] = PORT_GPIO_LOW;
    update_ok();
    host_fake_time_advance(&fake_time, CONFIG.debounce_ms + 1u);
    update_ok();
}

static void release(uint8_t pin)
{
    fake_gpio.level[pin] = PORT_GPIO_HIGH;
    update_ok();
    host_fake_time_advance(&fake_time, CONFIG.debounce_ms + 1u);
    update_ok();
}

static void test_startup_selects_mode_1_and_lights_both_leds(void)
{
    update_ok();

    TEST_ASSERT_EQUAL_INT(BLINK_MODE_SYNC_FAST, blink_modes_current(&state));
    TEST_ASSERT_TRUE(blink_modes_led_a_on(&state));
    TEST_ASSERT_TRUE(blink_modes_led_b_on(&state));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[CONFIG.led_a_pin]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[CONFIG.led_b_pin]);
}

static void test_mode_1_toggles_both_leds_every_200_ms(void)
{
    update_ok();

    host_fake_time_advance(&fake_time, 199u);
    update_ok();
    TEST_ASSERT_TRUE(blink_modes_led_a_on(&state));
    TEST_ASSERT_TRUE(blink_modes_led_b_on(&state));

    host_fake_time_advance(&fake_time, 1u);
    update_ok();
    TEST_ASSERT_FALSE(blink_modes_led_a_on(&state));
    TEST_ASSERT_FALSE(blink_modes_led_b_on(&state));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[CONFIG.led_a_pin]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[CONFIG.led_b_pin]);

    host_fake_time_advance(&fake_time, 200u);
    update_ok();
    TEST_ASSERT_TRUE(blink_modes_led_a_on(&state));
    TEST_ASSERT_TRUE(blink_modes_led_b_on(&state));
}

static void test_boot_selects_mode_2_and_alternates_every_1000_ms(void)
{
    update_ok();
    press(CONFIG.boot_button_pin);

    TEST_ASSERT_EQUAL_INT(BLINK_MODE_ALTERNATE_SLOW, blink_modes_current(&state));
    TEST_ASSERT_TRUE(blink_modes_led_a_on(&state));
    TEST_ASSERT_FALSE(blink_modes_led_b_on(&state));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[CONFIG.led_a_pin]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[CONFIG.led_b_pin]);

    host_fake_time_advance(&fake_time, 999u);
    update_ok();
    TEST_ASSERT_TRUE(blink_modes_led_a_on(&state));
    TEST_ASSERT_FALSE(blink_modes_led_b_on(&state));

    host_fake_time_advance(&fake_time, 1u);
    update_ok();
    TEST_ASSERT_FALSE(blink_modes_led_a_on(&state));
    TEST_ASSERT_TRUE(blink_modes_led_b_on(&state));
}

static void test_external_button_returns_to_mode_1(void)
{
    update_ok();
    press(CONFIG.boot_button_pin);
    release(CONFIG.boot_button_pin);
    TEST_ASSERT_EQUAL_INT(BLINK_MODE_ALTERNATE_SLOW, blink_modes_current(&state));

    press(CONFIG.external_button_pin);

    TEST_ASSERT_EQUAL_INT(BLINK_MODE_SYNC_FAST, blink_modes_current(&state));
    TEST_ASSERT_TRUE(blink_modes_led_a_on(&state));
    TEST_ASSERT_TRUE(blink_modes_led_b_on(&state));
}

static void test_debounce_rejects_a_short_glitch(void)
{
    update_ok();

    fake_gpio.level[CONFIG.boot_button_pin] = PORT_GPIO_LOW;
    update_ok();
    host_fake_time_advance(&fake_time, 10u);
    update_ok();

    fake_gpio.level[CONFIG.boot_button_pin] = PORT_GPIO_HIGH;
    update_ok();
    host_fake_time_advance(&fake_time, 10u);
    update_ok();

    TEST_ASSERT_EQUAL_INT(BLINK_MODE_SYNC_FAST, blink_modes_current(&state));
}

static void test_selected_mode_persists_until_the_other_button(void)
{
    int step;

    update_ok();
    press(CONFIG.boot_button_pin);
    release(CONFIG.boot_button_pin);
    TEST_ASSERT_EQUAL_INT(BLINK_MODE_ALTERNATE_SLOW, blink_modes_current(&state));

    for (step = 0; step < 10; ++step) {
        host_fake_time_advance(&fake_time, 1000u);
        update_ok();
        TEST_ASSERT_EQUAL_INT(BLINK_MODE_ALTERNATE_SLOW, blink_modes_current(&state));
    }
}

static void test_simultaneous_press_selects_mode_2(void)
{
    update_ok();
    press(CONFIG.boot_button_pin);
    release(CONFIG.boot_button_pin);

    fake_gpio.level[CONFIG.external_button_pin] = PORT_GPIO_LOW;
    fake_gpio.level[CONFIG.boot_button_pin] = PORT_GPIO_LOW;
    update_ok();
    host_fake_time_advance(&fake_time, CONFIG.debounce_ms + 1u);
    update_ok();

    TEST_ASSERT_EQUAL_INT(BLINK_MODE_ALTERNATE_SLOW, blink_modes_current(&state));
}

static void test_read_failure_does_not_fabricate_a_press(void)
{
    update_ok();

    host_fake_gpio_fail_next(&fake_gpio, PORT_ERR_IO);
    TEST_ASSERT_EQUAL_INT(PORT_ERR_IO, update());
    TEST_ASSERT_EQUAL_INT(BLINK_MODE_SYNC_FAST, blink_modes_current(&state));
}

static void test_late_poll_keeps_phase_parity(void)
{
    update_ok();

    host_fake_time_advance(&fake_time, 800u);
    update_ok();
    TEST_ASSERT_TRUE(blink_modes_led_a_on(&state));
    TEST_ASSERT_TRUE(blink_modes_led_b_on(&state));

    host_fake_time_advance(&fake_time, 200u);
    update_ok();
    TEST_ASSERT_FALSE(blink_modes_led_a_on(&state));
    TEST_ASSERT_FALSE(blink_modes_led_b_on(&state));
}

static void test_mode_switch_restarts_the_phase(void)
{
    update_ok();
    host_fake_time_advance(&fake_time, 150u);
    update_ok();

    press(CONFIG.boot_button_pin);
    TEST_ASSERT_TRUE(blink_modes_led_a_on(&state));

    host_fake_time_advance(&fake_time, 999u);
    update_ok();
    TEST_ASSERT_TRUE(blink_modes_led_a_on(&state));

    host_fake_time_advance(&fake_time, 1u);
    update_ok();
    TEST_ASSERT_FALSE(blink_modes_led_a_on(&state));
}

static void test_init_rejects_null(void)
{
    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, blink_modes_init(NULL, &CONFIG));
    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, blink_modes_init(&state, NULL));
}

static void test_zero_periods_fall_back_to_defaults(void)
{
    blink_modes_config_t config = CONFIG;
    blink_modes_t local;

    config.fast_period_ms = 0u;
    config.slow_period_ms = 0u;
    config.debounce_ms = 0u;

    TEST_ASSERT_EQUAL_INT(PORT_OK, blink_modes_init(&local, &config));
    TEST_ASSERT_EQUAL_UINT32(BLINK_MODES_DEFAULT_FAST_PERIOD_MS, local.config.fast_period_ms);
    TEST_ASSERT_EQUAL_UINT32(BLINK_MODES_DEFAULT_SLOW_PERIOD_MS, local.config.slow_period_ms);
    TEST_ASSERT_EQUAL_UINT32(BLINK_MODES_DEFAULT_DEBOUNCE_MS, local.config.debounce_ms);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_startup_selects_mode_1_and_lights_both_leds);
    RUN_TEST(test_mode_1_toggles_both_leds_every_200_ms);
    RUN_TEST(test_boot_selects_mode_2_and_alternates_every_1000_ms);
    RUN_TEST(test_external_button_returns_to_mode_1);
    RUN_TEST(test_debounce_rejects_a_short_glitch);
    RUN_TEST(test_selected_mode_persists_until_the_other_button);
    RUN_TEST(test_simultaneous_press_selects_mode_2);
    RUN_TEST(test_read_failure_does_not_fabricate_a_press);
    RUN_TEST(test_late_poll_keeps_phase_parity);
    RUN_TEST(test_mode_switch_restarts_the_phase);
    RUN_TEST(test_init_rejects_null);
    RUN_TEST(test_zero_periods_fall_back_to_defaults);
    return UNITY_END();
}
