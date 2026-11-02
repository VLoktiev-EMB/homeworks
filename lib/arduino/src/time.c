#include <Arduino.h>

#include "arduino/time.h"

static uint32_t arduino_now_ms(void *ctx)
{
    (void)ctx;
    return (uint32_t)millis();
}

static const port_time_ops_t ARDUINO_TIME_OPS = {
    arduino_now_ms,
};

port_time_t arduino_time_port(void)
{
    port_time_t port = {&ARDUINO_TIME_OPS, NULL};
    return port;
}
