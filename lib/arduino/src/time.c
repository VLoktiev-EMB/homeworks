#include <Arduino.h>

#include "arduino/time.h"

static uint32_t arduino_now_ms(void *ctx)
{
    (void)ctx;
    return (uint32_t)millis();
}

port_time_t arduino_time_port(void)
{
    port_time_t port = {arduino_now_ms, NULL};
    return port;
}
