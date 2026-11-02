#include <stdint.h>

#include "esp_timer.h"

#include "espidf/time.h"

static uint32_t espidf_now_ms(void *ctx)
{
    (void)ctx;
    return (uint32_t)(esp_timer_get_time() / 1000);
}

static const port_time_ops_t ESPIDF_TIME_OPS = {
    espidf_now_ms,
};

port_time_t espidf_time_port(void)
{
    port_time_t port = {&ESPIDF_TIME_OPS, NULL};
    return port;
}
