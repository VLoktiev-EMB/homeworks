#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Framework-free contact-bounce capture and analysis.
 *
 * The capture is a fixed-capacity list of edges in the order the interrupt
 * observed them. It owns no memory, allocates nothing, reads no clock, and is
 * not thread-safe: the caller supplies both the timestamp and the critical
 * section that shares it with an ISR.
 *
 * A level of `true` means HIGH (button released with a pull-up); `false` means
 * LOW (button pressed). Timestamps are 32-bit microseconds, so a difference is
 * computed with unsigned arithmetic and stays correct across the wrap. */

#define BOUNCE_CAPTURE_CAPACITY 256u

typedef struct bounce_edge {
    uint32_t at_us;
    bool level;
} bounce_edge_t;

typedef struct bounce_capture {
    bounce_edge_t storage[BOUNCE_CAPTURE_CAPACITY];
    size_t count;
    bool overflowed;
} bounce_capture_t;

/* Reset `capture` to empty and clear the overflow flag. A NULL capture is a
 * no-op. */
void bounce_capture_reset(bounce_capture_t *capture);

/* Append one edge. Returns false when the capture is full or NULL; a full
 * capture sets `overflowed` so the dump can say the burst is incomplete. */
bool bounce_capture_push(bounce_capture_t *capture, uint32_t at_us, bool level);

/* Number of stored edges (0 for NULL). */
size_t bounce_capture_count(const bounce_capture_t *capture);

/* Read the edge at chronological index `index` into `edge`. Returns false for
 * NULL arguments or an index at or beyond the stored count. */
bool bounce_capture_at(const bounce_capture_t *capture, size_t index, bounce_edge_t *edge);

/* Copy up to `capacity` edges into `destination`, oldest first. Returns the
 * number copied (0 for NULL arguments or zero capacity). */
size_t bounce_capture_copy(const bounce_capture_t *capture, bounce_edge_t *destination, size_t capacity);

typedef struct bounce_stats {
    size_t edges;
    size_t falling;
    size_t rising;
    uint32_t first_us;
    uint32_t last_us;
    uint32_t duration_us;
    uint32_t max_high_us;
    uint32_t max_low_us;
    uint32_t min_stable_ms;
    bool settled_low;
    bool overflowed;
    bool valid;
} bounce_stats_t;

/* Summarize a burst. Returns false and zeroes `stats` when `stats` is NULL or
 * `edges` is NULL or empty. A burst whose last edge is LOW is a press; a burst
 * whose last edge is HIGH is a release.
 *
 * `min_stable_ms` is the smallest millisecond debounce window that cannot
 * accept any HIGH interval inside the burst. It is the longest HIGH gap plus
 * one millisecond, because `common_debounce_update` accepts a candidate once
 * elapsed >= stable_ms; a window equal to the gap would accept it. A burst with
 * no HIGH interval needs no debounce and reports 0. */
bool bounce_analyze(const bounce_edge_t *edges, size_t count, bool overflowed, bounce_stats_t *stats);

#ifdef __cplusplus
}
#endif
