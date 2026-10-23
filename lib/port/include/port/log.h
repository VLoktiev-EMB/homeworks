#pragma once

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Four logging levels, ordered from most to least severe. */
typedef enum port_log_level {
    PORT_LOG_ERROR = 0,
    PORT_LOG_WARN,
    PORT_LOG_INFO,
    PORT_LOG_DEBUG
} port_log_level_t;

/* Consumer-owned logging contract.

   The write callback returns `void`, not `port_status_t`: a failed log write
   must never alter control flow, so the caller has nothing useful to branch
   on. This is the documented exception beside the time read.

   The consumer owns the interface, the adapter owns the state behind `ctx`,
   and an adapter factory returns this struct by value. A NULL sink - a zeroed
   `port_log_t`, or a NULL `port_log_t *` - discards output, so logging stays
   optional at the composition root.

   This contract does not name a framework type, does not own state, does not
   block, and does not encode device behaviour. */
typedef struct port_log {
    void (*write)(void *ctx, port_log_level_t level, const char *message);
    void *ctx;
} port_log_t;

static inline void port_log_write(const port_log_t *log, port_log_level_t level,
                                  const char *message) {
    if (log != NULL && log->write != NULL) {
        log->write(log->ctx, level, message);
    }
}

#ifdef __cplusplus
}
#endif
