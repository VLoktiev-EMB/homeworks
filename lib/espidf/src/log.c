#include <stdint.h>

#include "esp_log.h"

#include "espidf/log.h"

static void espidf_log_write(void *ctx, port_log_level_t level, const char *message)
{
    (void)ctx;
    esp_log_level_t mapped;

    switch (level) {
    case PORT_LOG_ERROR:
        mapped = ESP_LOG_ERROR;
        break;
    case PORT_LOG_WARN:
        mapped = ESP_LOG_WARN;
        break;
    case PORT_LOG_INFO:
        mapped = ESP_LOG_INFO;
        break;
    case PORT_LOG_DEBUG:
    default:
        mapped = ESP_LOG_DEBUG;
        break;
    }

    /* The fixed "port" tag is a deliberate phase decision: one tag for every
     adapter instance means the ESP-IDF runtime filter cannot distinguish
     adapters from each other. */
    esp_log_write(mapped, "port", "%s\n", message == NULL ? "" : message);
}

static const port_log_ops_t ESPIDF_LOG_OPS = {
    espidf_log_write,
};

port_log_t espidf_log_port(void)
{
    port_log_t port = {&ESPIDF_LOG_OPS, NULL};
    return port;
}
