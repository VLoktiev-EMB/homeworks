#pragma once

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* CRC-16/CCITT-FALSE over a caller-supplied byte buffer.

   Parameters, recorded here because they are part of the test contract:
     - initial value: 0xFFFF
     - polynomial:    0x1021 (the CCITT-FALSE polynomial)
     - final XOR:     none
     - reflected:     no

   Scope: this is a data-integrity check. It detects accidental corruption and
   transport noise. It is NOT authentication, NOT tamper detection and NOT a
   cryptographic hash: anyone can recompute the value, so it cannot establish
   trust in the bytes it covers.

   NULL contract: a NULL `data` with a non-zero `length` is a caller error; the
   function returns the unchanged input `crc` so that no legitimate zero value
   is invented. A NULL `data` with a zero `length` is a valid empty input.

   Neither function allocates, blocks or reads a clock. */

/* Continue a CRC-16/CCITT-FALSE computation from `crc` over `length` bytes of
   `data`. Pass 0xFFFF as `crc` to start a fresh computation. */
uint16_t common_crc16_update(uint16_t crc, const uint8_t *data, size_t length);

/* One-shot CRC-16/CCITT-FALSE of `data`, equivalent to
   `common_crc16_update(0xFFFF, data, length)`. */
uint16_t common_crc16(const uint8_t *data, size_t length);

#ifdef __cplusplus
}
#endif
