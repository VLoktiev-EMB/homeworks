#pragma once

#ifdef __cplusplus
extern "C" {
#endif

/* Single failure vocabulary for every contract call that can fail.
   Time reads and log writes do not fail and do not return it. */
typedef enum port_status_t {
    PORT_OK = 0,
    PORT_ERR_TIMEOUT,
    PORT_ERR_IO,
    PORT_ERR_INVALID_ARG,
    PORT_ERR_NOT_SUPPORTED
} port_status_t;

#ifdef __cplusplus
}
#endif
