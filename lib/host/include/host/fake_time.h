#pragma once

#include <stdint.h>

#include "port/time.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Deterministic clock test double.

   The struct is caller-owned; the port returned by the factory borrows it, so
   an advance through the struct is observed by every port already obtained.
   There is no allocation and no global state, which keeps two instances
   independent and every run reproducible. */
typedef struct host_fake_time {
    uint32_t now_ms;
} host_fake_time_t;

void host_fake_time_reset(host_fake_time_t *fake);
void host_fake_time_advance(host_fake_time_t *fake, uint32_t delta_ms);

port_time_t host_fake_time_port(host_fake_time_t *fake);

#ifdef __cplusplus
}
#endif
