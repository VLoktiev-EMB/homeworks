#pragma once

#include "port/time.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ESP-IDF time adapter.

   Returns the consumer-owned time contract backed by the framework microsecond
   clock, divided to milliseconds. No framework type crosses this header. */
port_time_t espidf_time_port(void);

#ifdef __cplusplus
}
#endif
