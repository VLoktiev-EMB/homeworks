#include <stddef.h>

#include "host/fake_log.h"

static void host_fake_log_write(void *ctx, port_log_level_t level, const char *message) {
    host_fake_log_t *fake = (host_fake_log_t *)ctx;
    host_fake_log_line_t *line;
    size_t index;

    if (fake == NULL) {
        return;
    }
    if (fake->count >= HOST_FAKE_LOG_LINES) {
        fake->dropped++;
        return;
    }
    line = &fake->lines[fake->count];
    line->level = level;
    if (message == NULL) {
        line->text[0] = '\0';
    } else {
        for (index = 0u; index + 1u < HOST_FAKE_LOG_TEXT && message[index] != '\0'; ++index) {
            line->text[index] = message[index];
        }
        line->text[index] = '\0';
    }
    fake->count++;
}

void host_fake_log_reset(host_fake_log_t *fake) {
    if (fake == NULL) {
        return;
    }
    fake->count = 0u;
    fake->dropped = 0u;
}

port_log_t host_fake_log_port(host_fake_log_t *fake) {
    port_log_t port = {host_fake_log_write, fake};

    return port;
}

size_t host_fake_log_count(const host_fake_log_t *fake) {
    if (fake == NULL) {
        return 0u;
    }
    return fake->count;
}

const host_fake_log_line_t *host_fake_log_at(const host_fake_log_t *fake, size_t index) {
    if (fake == NULL || index >= fake->count) {
        return NULL;
    }
    return &fake->lines[index];
}
