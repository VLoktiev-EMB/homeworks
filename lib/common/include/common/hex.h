#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Hexadecimal encode and decode with an explicit output capacity and a pinned
   failure contract.

   Encoding:
     - emits lowercase ASCII;
     - requires out_size >= 2 * length + 1 (the extra byte is the terminator);
     - always null-terminates the output;
     - excludes the terminator from *out_length.

   Decoding:
     - requires an even length;
     - accepts either case;
     - rejects any character outside '0'-'9', 'a'-'f' or 'A'-'F';
     - requires out_size >= length / 2.

   A zero-length input succeeds: encode writes only the terminator and reports
   *out_length == 0, while decode writes nothing and reports *out_length == 0.

   Failure contract (pinned, applies to both functions): on every failure path
   the function returns false, sets *out_length = 0 before returning, and
   writes no byte to out. It never writes at or past out_size. A NULL
   `out_length` is a caller error and returns false without writing anything.

   Neither function allocates, consults the locale or uses stdio formatting. */

bool common_hex_encode(const uint8_t *data, size_t length, char *out, size_t out_size, size_t *out_length);

bool common_hex_decode(const char *text, size_t length, uint8_t *out, size_t out_size, size_t *out_length);

#ifdef __cplusplus
}
#endif
