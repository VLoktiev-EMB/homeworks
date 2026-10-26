#pragma once

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Consumer-owned time contract.

   The struct is a borrowed view: the pointer passed to a consumer is owned by
   its caller, adapters and fakes return it by value from a factory, and the
   state behind `ctx` belongs to whoever created the instance. Nothing here is
   stored in a global; two instances therefore stay independent.

   Time is 32-bit milliseconds. Differences are computed with unsigned or
   signed 32-bit arithmetic so the wrap at 2^32 ms is handled by the arithmetic
   rather than by a comparison of absolute timestamps (about 49.7 days of raw
   range, but any signed-difference horizon is 2^31 - 1 ms). */
typedef struct port_time {
    uint32_t (*now_ms)(void *ctx);
    void *ctx;
} port_time_t;

static inline uint32_t port_time_now_ms(const port_time_t *time)
{
    return time->now_ms(time->ctx);
}

#ifdef __cplusplus
}
#endif
