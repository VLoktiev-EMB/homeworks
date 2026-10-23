#pragma once

#include <stddef.h>

#include "port/log.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Bounded, caller-owned capturing log sink.

   The sink stores up to HOST_FAKE_LOG_LINES lines of HOST_FAKE_LOG_TEXT bytes
   each. A message longer than the text capacity is truncated with a
   terminating null byte and still counted as one recorded line. Once every
   line is occupied, further messages increment `dropped` and are not stored,
   so an overflow is reported by a counter instead of overwriting captured
   output. A NULL message is stored as an empty string.

   `count` is the authority for what has been captured; lines at or above
   `count` are unspecified and `host_fake_log_at` never exposes them. The
   struct is caller-owned and allocation-free, so two instances stay
   independent. */
#define HOST_FAKE_LOG_LINES 32
#define HOST_FAKE_LOG_TEXT 64

typedef struct host_fake_log_line {
    port_log_level_t level;
    char text[HOST_FAKE_LOG_TEXT];
} host_fake_log_line_t;

typedef struct host_fake_log {
    host_fake_log_line_t lines[HOST_FAKE_LOG_LINES];
    size_t count;
    size_t dropped;
} host_fake_log_t;

void host_fake_log_reset(host_fake_log_t *fake);
port_log_t host_fake_log_port(host_fake_log_t *fake);
size_t host_fake_log_count(const host_fake_log_t *fake);
const host_fake_log_line_t *host_fake_log_at(const host_fake_log_t *fake, size_t index);

#ifdef __cplusplus
}
#endif
