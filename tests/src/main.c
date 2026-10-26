/* Compiled only by `pio run -t compiledb`; this file is never linked into a
   Unity app because tests/platformio.ini sets test_build_src = false. It exists
   so the compilation database also contains the shared translation units. */
#include "common/timing.h"
#include "host/fake_time.h"
#include "port/status.h"
#include "port/time.h"

int main(void)
{
    host_fake_time_t fake;
    port_time_t clock;
    common_debounce_t debounce = {0};
    port_status_t status = PORT_OK;
    uint32_t elapsed;

    host_fake_time_reset(&fake);
    clock = host_fake_time_port(&fake);
    elapsed = common_elapsed_ms(port_time_now_ms(&clock), 0u);
    (void)common_debounce_update(&debounce, &clock, false, 10u);
    (void)status;
    (void)elapsed;
    return 0;
}
