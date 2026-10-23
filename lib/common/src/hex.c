#include "common/hex.h"

static const char HEX_DIGITS[] = "0123456789abcdef";

/* Value of one hexadecimal digit, or -1 when the character is not one.
   Locale-independent by construction: only the ASCII ranges are accepted. */
static int hex_digit_value(char character) {
    if (character >= '0' && character <= '9') {
        return character - '0';
    }
    if (character >= 'a' && character <= 'f') {
        return character - 'a' + 10;
    }
    if (character >= 'A' && character <= 'F') {
        return character - 'A' + 10;
    }
    return -1;
}

bool common_hex_encode(const uint8_t *data, size_t length, char *out, size_t out_size,
                       size_t *out_length) {
    size_t index;
    size_t needed;

    if (out_length == NULL) {
        return false;
    }
    /* Pinned failure contract: zero the reported length before any check that
       can fail, and write no output byte until every check has passed. */
    *out_length = 0u;

    if (out == NULL) {
        return false;
    }
    /* Reject a length whose doubled size would overflow size_t. */
    if (length > (SIZE_MAX - 1u) / 2u) {
        return false;
    }
    needed = length * 2u + 1u;
    if (out_size < needed) {
        return false;
    }
    if (data == NULL && length != 0u) {
        return false;
    }

    for (index = 0u; index < length; index++) {
        out[index * 2u] = HEX_DIGITS[(data[index] >> 4) & 0x0Fu];
        out[index * 2u + 1u] = HEX_DIGITS[data[index] & 0x0Fu];
    }
    out[length * 2u] = '\0';
    *out_length = length * 2u;
    return true;
}

bool common_hex_decode(const char *text, size_t length, uint8_t *out, size_t out_size,
                       size_t *out_length) {
    size_t index;
    size_t needed;

    if (out_length == NULL) {
        return false;
    }
    *out_length = 0u;

    if ((length & 1u) != 0u) {
        return false;
    }
    needed = length / 2u;
    if (out_size < needed) {
        return false;
    }
    if (text == NULL && length != 0u) {
        return false;
    }
    if (out == NULL && needed != 0u) {
        return false;
    }

    /* Validate every digit before writing the first byte, so a rejected input
       leaves the caller's buffer untouched. */
    for (index = 0u; index < length; index++) {
        if (hex_digit_value(text[index]) < 0) {
            return false;
        }
    }

    for (index = 0u; index < needed; index++) {
        out[index] = (uint8_t)((hex_digit_value(text[index * 2u]) << 4) |
                               hex_digit_value(text[index * 2u + 1u]));
    }
    *out_length = needed;
    return true;
}
