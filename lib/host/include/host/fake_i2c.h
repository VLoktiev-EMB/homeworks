#pragma once

#include <stddef.h>
#include <stdint.h>

#include "port/i2c.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Single-device loopback I2C double.

   One instance models one device per transaction, not a multi-device bus: it
   records the last address and keeps a single HOST_FAKE_I2C_CAPACITY-byte
   buffer, so two devices at different addresses cannot be modelled in one
   instance. A consumer that needs two devices holds two fake instances, each
   with its own ctx and its own buffer.

   `write` records up to the capacity at `address`; `read` copies the stored
   buffer out; `write_read` records the transmit bytes and then loops that same
   buffer back into `rx`, which models one transaction without modelling a
   device. A transfer beyond the capacity, a read longer than the stored data,
   or an `rx` longer than the just-recorded `tx` returns PORT_ERR_INVALID_ARG
   rather than truncating silently.

   `host_fake_i2c_preset` is a setup helper, not a bus operation: it has no
   status return, and a NULL pointer or a length above the capacity leaves the
   stored buffer unchanged.

   `forced_status` is one-shot: any value other than PORT_OK is returned by the
   next operation and then replaced by PORT_OK, so PORT_OK means "no forcing".
   The forced status is consumed only after the call's own checks pass. */
#define HOST_FAKE_I2C_CAPACITY 32

typedef struct host_fake_i2c {
    uint8_t buffer[HOST_FAKE_I2C_CAPACITY];
    size_t length;
    uint8_t last_address;
    size_t transactions;
    port_status_t forced_status;
} host_fake_i2c_t;

void host_fake_i2c_reset(host_fake_i2c_t *fake);
void host_fake_i2c_fail_next(host_fake_i2c_t *fake, port_status_t status);
void host_fake_i2c_preset(host_fake_i2c_t *fake, const uint8_t *data, size_t length);

port_i2c_t host_fake_i2c_port(host_fake_i2c_t *fake);

#ifdef __cplusplus
}
#endif
