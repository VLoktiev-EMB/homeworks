#include <stddef.h>
#include <stdint.h>

#include <unity.h>

#include "host/fake_gpio.h"
#include "host/fake_time.h"
#include "pattern/controller.h"
#include "pattern/pattern.h"
#include "port/gpio.h"
#include "port/status.h"
#include "port/time.h"

static host_fake_gpio_t fake_gpio;
static host_fake_time_t fake_time;
static port_gpio_t gpio;
static port_time_t clock_port;
static pattern_controller_t controller;

static pattern_controller_config_t single_config(void)
{
    pattern_controller_config_t config = {4u, 5u, 6u, 7u, PATTERN_GPIO_SINGLE};

    return config;
}

static pattern_controller_config_t three_led_config(void)
{
    pattern_controller_config_t config = {4u, 5u, 6u, 7u, PATTERN_GPIO_THREE_LEDS};

    return config;
}

void setUp(void)
{
    host_fake_gpio_reset(&fake_gpio);
    host_fake_time_reset(&fake_time);
    /* The fake models every pin as LOW at reset, but an idle INPUT_PULLUP
       button reads HIGH on hardware; seed that level before the first tick. */
    fake_gpio.level[7] = PORT_GPIO_HIGH;
    gpio = host_fake_gpio_port(&fake_gpio);
    clock_port = host_fake_time_port(&fake_time);
}

void tearDown(void) {}

static void init_single(void)
{
    pattern_controller_config_t config = single_config();

    TEST_ASSERT_EQUAL_INT(PORT_OK, pattern_controller_init(&controller, &config, gpio, clock_port));
}

static void init_three_led(void)
{
    pattern_controller_config_t config = three_led_config();

    TEST_ASSERT_EQUAL_INT(PORT_OK, pattern_controller_init(&controller, &config, gpio, clock_port));
}

static void tick_after(uint32_t delta_ms)
{
    host_fake_time_advance(&fake_time, delta_ms);
    pattern_controller_tick(&controller);
}

/* A 60 ms debounced press: 30 ms to accept the press and 30 ms to accept the
   release. Comfortably shorter than PATTERN_CONTROLLER_LONG_PRESS_MS. */
static void press_short(void)
{
    fake_gpio.level[7] = PORT_GPIO_LOW;
    pattern_controller_tick(&controller);
    tick_after(30u);
    fake_gpio.level[7] = PORT_GPIO_HIGH;
    pattern_controller_tick(&controller);
    tick_after(30u);
}

/* A debounced press held past the long-press threshold, then released. */
static void press_long(void)
{
    fake_gpio.level[7] = PORT_GPIO_LOW;
    pattern_controller_tick(&controller);
    tick_after(30u);
    tick_after(600u);
    fake_gpio.level[7] = PORT_GPIO_HIGH;
    pattern_controller_tick(&controller);
    tick_after(30u);
}

static void test_init_configures_pins(void)
{
    init_single();

    TEST_ASSERT_EQUAL_INT(PORT_GPIO_OUTPUT, fake_gpio.mode[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_OUTPUT, fake_gpio.mode[6]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_INPUT_PULLUP, fake_gpio.mode[7]);
    /* Pin B belongs to the three-LED profile only. */
    TEST_ASSERT_FALSE(fake_gpio.configured[5]);
    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_ALTERNATING, pattern_controller_mode(&controller));
    TEST_ASSERT_EQUAL_UINT(400u, (unsigned)pattern_controller_base_ms(&controller));
    TEST_ASSERT_EQUAL_INT(PORT_OK, pattern_controller_status(&controller));
}

static void test_first_frame_drives_pin_a_high(void)
{
    init_single();

    TEST_ASSERT_EQUAL_INT(PORT_GPIO_OUTPUT, fake_gpio.mode[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[6]);
}

static void test_399_ms_does_not_advance_a_400_ms_frame(void)
{
    size_t writes;

    init_single();
    writes = fake_gpio.writes;

    tick_after(399u);

    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_UINT((unsigned)writes, (unsigned)fake_gpio.writes);
}

static void test_400_ms_advances_one_frame(void)
{
    init_single();

    tick_after(400u);

    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[6]);
}

static void test_five_ticks_do_not_drift(void)
{
    static const port_gpio_level_t expected_a[5] = {PORT_GPIO_LOW, PORT_GPIO_HIGH, PORT_GPIO_LOW, PORT_GPIO_HIGH,
                                                    PORT_GPIO_LOW};
    static const port_gpio_level_t expected_c[5] = {PORT_GPIO_LOW, PORT_GPIO_HIGH, PORT_GPIO_HIGH, PORT_GPIO_LOW,
                                                    PORT_GPIO_LOW};
    size_t index;

    init_single();
    for (index = 0u; index < 5u; ++index) {
        tick_after(400u);
        TEST_ASSERT_EQUAL_INT(expected_a[index], fake_gpio.level[4]);
        TEST_ASSERT_EQUAL_INT(expected_c[index], fake_gpio.level[6]);
        TEST_ASSERT_EQUAL_INT(PORT_GPIO_OUTPUT, fake_gpio.mode[4]);
    }
}

static void test_a_stall_advances_exactly_one_frame(void)
{
    init_single();

    tick_after(900u);
    /* Frame 1 alone is the LOW/LOW state; frame 0 and frame 2 are both HIGH. */
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[6]);

    pattern_controller_tick(&controller);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[6]);
}

static void test_the_32_bit_wrap_advances_one_frame(void)
{
    fake_time.now_ms = 0xFFFFFF00u;
    init_single();

    tick_after(400u);

    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[6]);
}

static void test_a_backwards_clock_jump_changes_no_output(void)
{
    size_t writes;

    init_single();
    tick_after(400u);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[4]);
    writes = fake_gpio.writes;

    fake_time.now_ms = 100u;
    pattern_controller_tick(&controller);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_UINT((unsigned)writes, (unsigned)fake_gpio.writes);

    /* The resynced schedule then advances at most one frame, not a burst. */
    tick_after(400u);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[6]);
}

static void test_a_10_ms_blip_does_not_change_the_mode(void)
{
    init_single();

    fake_gpio.level[7] = PORT_GPIO_LOW;
    pattern_controller_tick(&controller);
    tick_after(10u);
    fake_gpio.level[7] = PORT_GPIO_HIGH;
    pattern_controller_tick(&controller);
    tick_after(30u);

    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_ALTERNATING, pattern_controller_mode(&controller));
    TEST_ASSERT_EQUAL_UINT(400u, (unsigned)pattern_controller_base_ms(&controller));
}

static void test_a_590_ms_press_advances_the_mode_once(void)
{
    init_single();

    fake_gpio.level[7] = PORT_GPIO_LOW;
    pattern_controller_tick(&controller);
    tick_after(30u);
    tick_after(560u);
    fake_gpio.level[7] = PORT_GPIO_HIGH;
    pattern_controller_tick(&controller);
    tick_after(30u);

    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_DOUBLE_FLASH, pattern_controller_mode(&controller));

    pattern_controller_tick(&controller);
    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_DOUBLE_FLASH, pattern_controller_mode(&controller));
}

static void test_a_long_press_advances_the_speed_only(void)
{
    init_single();

    fake_gpio.level[7] = PORT_GPIO_LOW;
    pattern_controller_tick(&controller);
    tick_after(30u);
    tick_after(600u);
    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_ALTERNATING, pattern_controller_mode(&controller));
    TEST_ASSERT_EQUAL_UINT(200u, (unsigned)pattern_controller_base_ms(&controller));

    tick_after(70u);
    fake_gpio.level[7] = PORT_GPIO_HIGH;
    pattern_controller_tick(&controller);
    tick_after(30u);

    /* The release of the long press must not also count as a short press. */
    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_ALTERNATING, pattern_controller_mode(&controller));
    TEST_ASSERT_EQUAL_UINT(200u, (unsigned)pattern_controller_base_ms(&controller));
}

static void test_a_short_press_advances_to_double_flash(void)
{
    init_single();

    press_short();

    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_DOUBLE_FLASH, pattern_controller_mode(&controller));
    TEST_ASSERT_EQUAL_UINT(400u, (unsigned)pattern_controller_base_ms(&controller));
}

static void test_an_all_off_frame_drives_pin_a_to_input(void)
{
    init_single();
    press_short();
    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_DOUBLE_FLASH, pattern_controller_mode(&controller));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_OUTPUT, fake_gpio.mode[4]);

    tick_after(200u);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_INPUT, fake_gpio.mode[4]);

    /* Leaving the high-impedance state restores OUTPUT and the level. */
    tick_after(200u);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_OUTPUT, fake_gpio.mode[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[4]);
}

static void test_solid_drives_pin_a_high_in_the_single_profile(void)
{
    init_single();

    press_short();
    press_short();
    press_short();

    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_SOLID, pattern_controller_mode(&controller));
    TEST_ASSERT_EQUAL_UINT(400u, (unsigned)pattern_controller_base_ms(&controller));
    /* `led_a` wins, so the LOW-lit LED of the anti-parallel pair stays dark. */
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_OUTPUT, fake_gpio.mode[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[4]);
}

static void test_the_three_led_profile_drives_pins_independently(void)
{
    init_three_led();

    TEST_ASSERT_EQUAL_INT(PORT_GPIO_OUTPUT, fake_gpio.mode[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_OUTPUT, fake_gpio.mode[5]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_OUTPUT, fake_gpio.mode[6]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[5]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[6]);

    tick_after(400u);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[5]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[6]);

    tick_after(400u);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[5]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[6]);
}

static void test_a_failed_read_keeps_the_stable_level(void)
{
    size_t reads;

    init_single();
    reads = fake_gpio.reads;
    host_fake_gpio_fail_next(&fake_gpio, PORT_ERR_IO);

    pattern_controller_tick(&controller);

    TEST_ASSERT_EQUAL_INT(PORT_ERR_IO, pattern_controller_status(&controller));
    TEST_ASSERT_EQUAL_UINT((unsigned)reads, (unsigned)fake_gpio.reads);
    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_ALTERNATING, pattern_controller_mode(&controller));
    TEST_ASSERT_EQUAL_UINT(400u, (unsigned)pattern_controller_base_ms(&controller));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[4]);

    /* The controller stays ready: the next tick clears the status. */
    pattern_controller_tick(&controller);
    TEST_ASSERT_EQUAL_INT(PORT_OK, pattern_controller_status(&controller));
}

static void test_a_failed_write_is_retried_on_the_next_tick(void)
{
    size_t writes;

    init_single();
    writes = fake_gpio.writes;
    host_fake_time_advance(&fake_time, 400u);
    host_fake_gpio_fail_next(&fake_gpio, PORT_ERR_IO);

    pattern_controller_tick(&controller);

    TEST_ASSERT_EQUAL_INT(PORT_ERR_IO, pattern_controller_status(&controller));
    TEST_ASSERT_EQUAL_UINT((unsigned)writes, (unsigned)fake_gpio.writes);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[4]);

    /* No time passes; the same desired value is retried and succeeds. */
    pattern_controller_tick(&controller);

    TEST_ASSERT_EQUAL_INT(PORT_OK, pattern_controller_status(&controller));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_UINT((unsigned)(writes + 1u), (unsigned)fake_gpio.writes);
}

static void test_null_and_unready_entry_points_are_no_ops(void)
{
    pattern_controller_config_t config = single_config();
    pattern_controller_t zeroed = {0};
    size_t writes;

    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, pattern_controller_init(NULL, &config, gpio, clock_port));
    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, pattern_controller_init(&controller, NULL, gpio, clock_port));
    pattern_controller_tick(NULL);
    pattern_controller_tick(&zeroed);
    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_ALTERNATING, pattern_controller_mode(NULL));
    TEST_ASSERT_EQUAL_UINT(400u, (unsigned)pattern_controller_base_ms(NULL));
    TEST_ASSERT_EQUAL_INT(PORT_ERR_INVALID_ARG, pattern_controller_status(NULL));

    /* A controller that is not ready does not touch the ports. */
    init_single();
    controller.ready = false;
    writes = fake_gpio.writes;
    tick_after(400u);
    TEST_ASSERT_EQUAL_UINT((unsigned)writes, (unsigned)fake_gpio.writes);
}

static void test_a_mode_change_restarts_at_frame_zero(void)
{
    init_single();
    tick_after(400u);
    tick_after(400u);
    /* Alternating frame 2 carries the third LED. */
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[6]);

    press_short();

    /* DOUBLE_FLASH frame 0 is the first LED alone: the reset is observable. */
    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_DOUBLE_FLASH, pattern_controller_mode(&controller));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[6]);
}

static void test_a_speed_change_restarts_at_frame_zero(void)
{
    init_single();
    tick_after(400u);
    tick_after(400u);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[6]);

    press_long();

    TEST_ASSERT_EQUAL_UINT(200u, (unsigned)pattern_controller_base_ms(&controller));
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_HIGH, fake_gpio.level[4]);
    TEST_ASSERT_EQUAL_INT(PORT_GPIO_LOW, fake_gpio.level[6]);
}

static void test_the_full_mode_cycle_returns_to_alternating(void)
{
    init_single();

    press_short();
    press_short();
    press_short();
    press_short();

    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_ALTERNATING, pattern_controller_mode(&controller));
}

static void test_the_full_speed_cycle_returns_to_400_ms(void)
{
    init_single();

    press_long();
    TEST_ASSERT_EQUAL_UINT(200u, (unsigned)pattern_controller_base_ms(&controller));

    press_long();
    TEST_ASSERT_EQUAL_UINT(100u, (unsigned)pattern_controller_base_ms(&controller));

    press_long();
    TEST_ASSERT_EQUAL_UINT(400u, (unsigned)pattern_controller_base_ms(&controller));
    TEST_ASSERT_EQUAL_INT(PATTERN_MODE_ALTERNATING, pattern_controller_mode(&controller));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_init_configures_pins);
    RUN_TEST(test_first_frame_drives_pin_a_high);
    RUN_TEST(test_399_ms_does_not_advance_a_400_ms_frame);
    RUN_TEST(test_400_ms_advances_one_frame);
    RUN_TEST(test_five_ticks_do_not_drift);
    RUN_TEST(test_a_stall_advances_exactly_one_frame);
    RUN_TEST(test_the_32_bit_wrap_advances_one_frame);
    RUN_TEST(test_a_backwards_clock_jump_changes_no_output);
    RUN_TEST(test_a_10_ms_blip_does_not_change_the_mode);
    RUN_TEST(test_a_590_ms_press_advances_the_mode_once);
    RUN_TEST(test_a_long_press_advances_the_speed_only);
    RUN_TEST(test_a_short_press_advances_to_double_flash);
    RUN_TEST(test_an_all_off_frame_drives_pin_a_to_input);
    RUN_TEST(test_solid_drives_pin_a_high_in_the_single_profile);
    RUN_TEST(test_the_three_led_profile_drives_pins_independently);
    RUN_TEST(test_a_failed_read_keeps_the_stable_level);
    RUN_TEST(test_a_failed_write_is_retried_on_the_next_tick);
    RUN_TEST(test_null_and_unready_entry_points_are_no_ops);
    RUN_TEST(test_a_mode_change_restarts_at_frame_zero);
    RUN_TEST(test_a_speed_change_restarts_at_frame_zero);
    RUN_TEST(test_the_full_mode_cycle_returns_to_alternating);
    RUN_TEST(test_the_full_speed_cycle_returns_to_400_ms);
    return UNITY_END();
}
