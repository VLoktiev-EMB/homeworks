#include <stddef.h>

#include "host/fake_time.h"

static uint32_t host_fake_time_now_ms(void *ctx) {
    const host_fake_time_t *fake = (const host_fake_time_t *)ctx;

    return fake->now_ms;
}

void host_fake_time_reset(host_fake_time_t *fake) {
    if (fake == NULL) {
        return;
    }
    fake->now_ms = 0u;
}

void host_fake_time_advance(host_fake_time_t *fake, uint32_t delta_ms) {
    if (fake == NULL) {
        return;
    }
    fake->now_ms += delta_ms;
}

port_time_t host_fake_time_port(host_fake_time_t *fake) {
    port_time_t port = {host_fake_time_now_ms, fake};

    return port;
}
