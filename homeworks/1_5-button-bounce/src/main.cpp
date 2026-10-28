/* Composition root for the contact-bounce homework.
 *
 * The Arduino layer owns only what needs the framework: the pin, the CHANGE
 * interrupt, the microsecond timestamp, and the critical section that shares
 * the capture with the ISR. The analysis itself lives in the framework-free
 * `bounce_logic` library, so the host suite can verify it byte for byte.
 *
 * Serial protocol (115200 baud):
 *   BOUNCE_LOGGER 1
 *   BUTTON_PIN=<n> QUIET_GAP_MS=<n> DEBOUNCE_MS=<n>
 *   BURST edges=<n> falling=<n> rising=<n> duration_us=<n> max_high_us=<n>
 *         min_stable_ms=<n> settled=<LOW|HIGH> overflow=<0|1>
 *   E <index> <at_us> <L|H>          (one line per captured edge)
 *   TOTAL falling=<n> rising=<n> debounced=<n>
 *   READY
 *
 * A burst is dumped only after QUIET_GAP_MS without a new edge, so the serial
 * traffic never interleaves with the bounce it is describing. */

#include <Arduino.h>

#include "arduino/gpio.h"
#include "arduino/log.h"
#include "arduino/time.h"
#include "bounce_logic.h"
#include "common/timing.h"
#include "port/gpio.h"
#include "port/log.h"
#include "port/time.h"

/* Must match the wiring recorded in assets/ and in the report. */
static const uint8_t BUTTON_PIN = 16;
static const uint32_t QUIET_GAP_MS = 250u;
static const uint32_t DEBOUNCE_MS = 20u;

/* The capture is written by the ISR and drained by loop(); the mutex is the
   only state shared across that boundary. The sequence counter lets the loop
   notice a new edge without touching the capture. */
static portMUX_TYPE capture_mutex = portMUX_INITIALIZER_UNLOCKED;
static bounce_capture_t capture;
static volatile uint32_t isr_edge_sequence = 0u;

/* File-scope storage is an Arduino composition-root necessity: setup() runs
   once and loop() runs forever, so the contracts must outlive setup(). */
static port_gpio_t gpio;
static port_time_t clock_port;
static port_log_t logger;

static common_debounce_t debounce_state = {true, true, 0u};
static bounce_edge_t snapshot[BOUNCE_CAPTURE_CAPACITY];

static uint32_t last_seen_sequence = 0u;
static uint32_t last_edge_ms = 0u;
static bool have_edges = false;
static bool last_stable_high = true;
static uint32_t raw_falling_total = 0u;
static uint32_t raw_rising_total = 0u;
static uint32_t debounced_press_total = 0u;

static void IRAM_ATTR button_isr(void)
{
    const bool level_high = digitalRead(BUTTON_PIN) == HIGH;

    portENTER_CRITICAL_ISR(&capture_mutex);
    (void)bounce_capture_push(&capture, (uint32_t)micros(), level_high);
    portEXIT_CRITICAL_ISR(&capture_mutex);
    isr_edge_sequence = isr_edge_sequence + 1u;
}

static void dump_burst(void)
{
    bounce_stats_t stats;
    size_t count;
    bool overflowed;
    size_t index;

    portENTER_CRITICAL(&capture_mutex);
    count = bounce_capture_count(&capture);
    overflowed = capture.overflowed;
    (void)bounce_capture_copy(&capture, snapshot, BOUNCE_CAPTURE_CAPACITY);
    bounce_capture_reset(&capture);
    portEXIT_CRITICAL(&capture_mutex);

    if (!bounce_analyze(snapshot, count, overflowed, &stats)) {
        return;
    }

    raw_falling_total += (uint32_t)stats.falling;
    raw_rising_total += (uint32_t)stats.rising;

    Serial.printf("BURST edges=%lu falling=%lu rising=%lu duration_us=%lu max_high_us=%lu "
                  "min_stable_ms=%lu settled=%s overflow=%u\n",
                  (unsigned long)stats.edges, (unsigned long)stats.falling, (unsigned long)stats.rising,
                  (unsigned long)stats.duration_us, (unsigned long)stats.max_high_us,
                  (unsigned long)stats.min_stable_ms, stats.settled_low ? "LOW" : "HIGH", overflowed ? 1u : 0u);

    for (index = 0u; index < count; index++) {
        Serial.printf("E %lu %lu %c\n", (unsigned long)index, (unsigned long)snapshot[index].at_us,
                      snapshot[index].level ? 'H' : 'L');
    }

    Serial.printf("TOTAL falling=%lu rising=%lu debounced=%lu\n", (unsigned long)raw_falling_total,
                  (unsigned long)raw_rising_total, (unsigned long)debounced_press_total);
    Serial.println("READY");
}

void setup(void)
{
    gpio = arduino_gpio_port();
    clock_port = arduino_time_port();
    logger = arduino_log_port();

    Serial.begin(115200);
    bounce_capture_reset(&capture);

    if (gpio.set_mode(gpio.ctx, BUTTON_PIN, PORT_GPIO_INPUT_PULLUP) != PORT_OK) {
        port_log_write(&logger, PORT_LOG_ERROR, "button pin configuration failed");
    }

    /* On the ESP32-S3 variant the Arduino pin number is the GPIO number, so
       the direct form is exactly what digitalPinToInterrupt() resolves to. */
    attachInterrupt(BUTTON_PIN, button_isr, CHANGE);

    Serial.println("BOUNCE_LOGGER 1");
    Serial.printf("BUTTON_PIN=%u QUIET_GAP_MS=%lu DEBOUNCE_MS=%lu\n", (unsigned)BUTTON_PIN, (unsigned long)QUIET_GAP_MS,
                  (unsigned long)DEBOUNCE_MS);
    Serial.println("READY");
}

void loop(void)
{
    const uint32_t now_ms = port_time_now_ms(&clock_port);
    port_gpio_level_t level = PORT_GPIO_HIGH;
    bool stable_high;

    if (gpio.read(gpio.ctx, BUTTON_PIN, &level) != PORT_OK) {
        return;
    }

    stable_high = common_debounce_update(&debounce_state, &clock_port, level == PORT_GPIO_HIGH, DEBOUNCE_MS);
    if (last_stable_high && !stable_high) {
        debounced_press_total++;
    }
    last_stable_high = stable_high;

    if (isr_edge_sequence != last_seen_sequence) {
        last_seen_sequence = isr_edge_sequence;
        last_edge_ms = now_ms;
        have_edges = true;
    }

    if (have_edges && common_elapsed_ms(now_ms, last_edge_ms) >= QUIET_GAP_MS) {
        dump_burst();
        have_edges = false;
    }

    delay(1);
}
