#pragma once

#include "port/log.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ESP-IDF logging adapter.

   Returns the consumer-owned log contract over the framework C logging call.
   The four port levels map one-to-one to the framework severity levels. No
   framework type crosses this header. */
port_log_t espidf_log_port(void);

#ifdef __cplusplus
}
#endif
