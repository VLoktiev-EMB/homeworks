#pragma once

#include "port/log.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Arduino logging adapter.

   Returns the consumer-owned log contract. Output goes through the framework's
   unconditional formatted writer, not through a level-gated macro, so a level
   is always emitted whatever the framework debug setting is. */
port_log_t arduino_log_port(void);

#ifdef __cplusplus
}
#endif
