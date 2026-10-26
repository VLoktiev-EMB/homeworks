#include "common/crc.h"

uint16_t common_crc16_update(uint16_t crc, const uint8_t *data, size_t length)
{
    size_t index;
    int bit;

    /* A NULL pointer with a non-zero length cannot be read. Return the input
       unchanged rather than inventing a value that could collide with a real
       CRC. A NULL pointer with zero length is a valid empty input. */
    if (data == NULL && length != 0u) {
        return crc;
    }

    /* Bitwise implementation: no 256-byte table, no allocation, and the
       polynomial stays visible beside the code it defines. */
    for (index = 0u; index < length; index++) {
        crc ^= (uint16_t)((unsigned int)(uint16_t)data[index] << 8u);
        for (bit = 0; bit < 8; bit++) {
            if ((crc & 0x8000u) != 0u) {
                crc = (uint16_t)(((unsigned int)crc << 1u) ^ 0x1021u);
            } else {
                crc = (uint16_t)((unsigned int)crc << 1u);
            }
        }
    }

    return crc;
}

uint16_t common_crc16(const uint8_t *data, size_t length)
{
    return common_crc16_update(0xFFFFu, data, length);
}
