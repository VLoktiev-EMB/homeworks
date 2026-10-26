#include <stdint.h>

#include "esp_timer.h"

#include "espidf/time.h"

static uint32_t espidf_now_ms(void *ctx)
{
    (void)ctx;
    return (uint32_t)(esp_timer_get_time() / 1000);
}

port_time_t espidf_time_port(void)
{
    port_time_t port = {espidf_now_ms, NULL};
    return port;
}
