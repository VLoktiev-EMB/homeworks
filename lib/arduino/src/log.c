#include <Arduino.h>

#include "arduino/log.h"

static void arduino_log_write(void *ctx, port_log_level_t level, const char *message)
{
    (void)ctx;
    char prefix;

    switch (level) {
    case PORT_LOG_ERROR:
        prefix = 'E';
        break;
    case PORT_LOG_WARN:
        prefix = 'W';
        break;
    case PORT_LOG_INFO:
        prefix = 'I';
        break;
    case PORT_LOG_DEBUG:
    default:
        prefix = 'D';
        break;
    }

    /* Unconditional: log_i/log_d compile to nothing at the default
     CORE_DEBUG_LEVEL, which would silently drop every record. */
    log_printf("%c %s\n", prefix, message == NULL ? "" : message);
}

port_log_t arduino_log_port(void)
{
    port_log_t port = {arduino_log_write, NULL};
    return port;
}
