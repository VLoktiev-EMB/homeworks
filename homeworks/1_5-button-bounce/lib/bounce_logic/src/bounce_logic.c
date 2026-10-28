#include "bounce_logic.h"

#include <string.h>

void bounce_capture_reset(bounce_capture_t *capture)
{
    if (capture == NULL) {
        return;
    }

    capture->count = 0;
    capture->overflowed = false;
}

bool bounce_capture_push(bounce_capture_t *capture, uint32_t at_us, bool level)
{
    if (capture == NULL) {
        return false;
    }
    if (capture->count >= BOUNCE_CAPTURE_CAPACITY) {
        capture->overflowed = true;
        return false;
    }

    capture->storage[capture->count].at_us = at_us;
    capture->storage[capture->count].level = level;
    capture->count++;
    return true;
}

size_t bounce_capture_count(const bounce_capture_t *capture)
{
    if (capture == NULL) {
        return 0u;
    }

    return capture->count;
}

bool bounce_capture_at(const bounce_capture_t *capture, size_t index, bounce_edge_t *edge)
{
    if (capture == NULL || edge == NULL || index >= capture->count) {
        return false;
    }

    *edge = capture->storage[index];
    return true;
}

size_t bounce_capture_copy(const bounce_capture_t *capture, bounce_edge_t *destination, size_t capacity)
{
    size_t copied;

    if (capture == NULL || destination == NULL || capacity == 0u) {
        return 0u;
    }

    copied = capture->count < capacity ? capture->count : capacity;
    memcpy(destination, capture->storage, copied * sizeof(bounce_edge_t));
    return copied;
}

bool bounce_analyze(const bounce_edge_t *edges, size_t count, bool overflowed, bounce_stats_t *stats)
{
    size_t index;

    if (stats == NULL) {
        return false;
    }

    memset(stats, 0, sizeof(*stats));
    stats->overflowed = overflowed;

    if (edges == NULL || count == 0u) {
        return false;
    }

    stats->valid = true;
    stats->edges = count;
    stats->first_us = edges[0].at_us;
    stats->last_us = edges[count - 1u].at_us;
    stats->duration_us = stats->last_us - stats->first_us;
    stats->settled_low = !edges[count - 1u].level;

    for (index = 0u; index < count; index++) {
        if (edges[index].level) {
            stats->rising++;
        } else {
            stats->falling++;
        }

        if (index + 1u < count) {
            uint32_t gap_us = edges[index + 1u].at_us - edges[index].at_us;

            if (edges[index].level) {
                if (gap_us > stats->max_high_us) {
                    stats->max_high_us = gap_us;
                }
            } else if (gap_us > stats->max_low_us) {
                stats->max_low_us = gap_us;
            }
        }
    }

    if (stats->max_high_us > 0u) {
        stats->min_stable_ms = stats->max_high_us / 1000u + 1u;
    }

    return true;
}
