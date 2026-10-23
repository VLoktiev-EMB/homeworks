#pragma once

#include "port/time.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Arduino time adapter.

   Returns the consumer-owned time contract backed by the framework millisecond
   clock. No framework type crosses this header: a consumer compiles against it
   without including the framework. */
port_time_t arduino_time_port(void);

#ifdef __cplusplus
}
#endif
