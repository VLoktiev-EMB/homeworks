/* Firmware for the contact-bounce homework.
 *
 * The firmware owns the whole measurement path: the pin, the CHANGE interrupt,
 * the 256-edge capture shared with the ISR, the burst analysis, the serial
 * protocol, and the online debounce.
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
#include <string.h>

#include "arduino/gpio.h"
#include "arduino/log.h"
#include "arduino/time.h"
#include "common/timing.h"
#include "port/gpio.h"
#include "port/log.h"
#include "port/time.h"

/* Must match the wiring recorded in assets/ and in the report. */
static const uint8_t BUTTON_PIN = 16;
static const uint32_t QUIET_GAP_MS = 250u;
static const uint32_t DEBOUNCE_MS = 20u;
static const size_t CAPTURE_CAPACITY = 256u;

typedef struct edge_record {
    uint32_t at_us;
    bool level;
} edge_record_t;

/* The capture is the only state shared between the ISR and loop(). The ISR is
   the only writer: it cannot be preempted by the loop task, so it needs no lock.
   The loop briefly disables interrupts while it copies and clears, so an edge
   can never land mid-copy. This is an interrupt-disable window, not a mutex.
   The sequence counter lets the loop notice a new edge without touching it. */
static edge_record_t capture[CAPTURE_CAPACITY];
static volatile size_t capture_count = 0u;
static volatile bool capture_overflowed = false;
static volatile uint32_t isr_edge_sequence = 0u;

/* File-scope storage is an Arduino composition-root necessity: setup() runs
   once and loop() runs forever, so the contracts must outlive setup(). */
static port_gpio_t gpio;
static port_time_t clock_port;
static port_log_t logger;

static common_debounce_t debounce_state = {true, true, 0u};
static edge_record_t snapshot[CAPTURE_CAPACITY];

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
    const uint32_t at_us = (uint32_t)micros();

    if (capture_count < CAPTURE_CAPACITY) {
        capture[capture_count].at_us = at_us;
        capture[capture_count].level = level_high;
        capture_count++;
    } else {
        capture_overflowed = true;
    }
    isr_edge_sequence = isr_edge_sequence + 1u;
}

static void dump_burst(void)
{
    size_t count;
    bool overflowed;
    size_t index;
    uint32_t falling = 0u;
    uint32_t rising = 0u;
    uint32_t duration_us;
    uint32_t max_high_us = 0u;
    uint32_t min_stable_ms;
    bool settled_low;

    noInterrupts();
    count = capture_count;
    overflowed = capture_overflowed;
    memcpy(snapshot, capture, count * sizeof(edge_record_t));
    capture_count = 0u;
    capture_overflowed = false;
    interrupts();

    if (count == 0u) {
        return;
    }

    for (index = 0u; index < count; index++) {
        if (snapshot[index].level) {
            rising++;
        } else {
            falling++;
        }

        if (index + 1u < count && snapshot[index].level) {
            const uint32_t gap_us = snapshot[index + 1u].at_us - snapshot[index].at_us;

            if (gap_us > max_high_us) {
                max_high_us = gap_us;
            }
        }
    }

    duration_us = snapshot[count - 1u].at_us - snapshot[0u].at_us;
    /* The debounce accepts a candidate once elapsed >= the window, so a HIGH
       gap equal to the window would still register. One millisecond more is the
       smallest window that rejects every HIGH interval inside the burst. */
    min_stable_ms = max_high_us > 0u ? max_high_us / 1000u + 1u : 0u;
    settled_low = !snapshot[count - 1u].level;

    raw_falling_total += falling;
    raw_rising_total += rising;

    Serial.printf("BURST edges=%lu falling=%lu rising=%lu duration_us=%lu max_high_us=%lu "
                  "min_stable_ms=%lu settled=%s overflow=%u\n",
                  (unsigned long)count, (unsigned long)falling, (unsigned long)rising, (unsigned long)duration_us,
                  (unsigned long)max_high_us, (unsigned long)min_stable_ms, settled_low ? "LOW" : "HIGH",
                  overflowed ? 1u : 0u);

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

    /* Waiting for the quiet gap keeps the dump off the wire until the bounce
       has stopped, so serial traffic never interleaves with the burst. */
    if (have_edges && common_elapsed_ms(now_ms, last_edge_ms) >= QUIET_GAP_MS) {
        dump_burst();
        have_edges = false;
    }

    delay(1);
}
