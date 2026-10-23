#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Fixed-capacity byte ring buffer over caller-owned storage.

   The buffer owns no memory: `storage` points at `capacity` bytes supplied by
   the caller, and no function here allocates, frees, blocks, sleeps or reads a
   clock. `capacity` counts bytes, not elements.

   Full and empty are reported through the return value:
     - `common_ring_buffer_push` returns false when the buffer is full;
     - `common_ring_buffer_pop` returns false when the buffer is empty.
   Neither call waits for room or for data.

   Uninitialised state is defined rather than undefined. A struct whose
   `storage` is NULL, or whose `capacity` is 0, is an empty buffer: `count` and
   `capacity` return 0, `push` and `pop` return false, and `clear` does
   nothing. The `storage` / `capacity` pair is the guard; there is deliberately
   no `initialized` flag, because a flag and the pointer could disagree.

   Concurrency contract: this type is single-threaded domain logic. It is not
   ISR-safe and it is not lock-free or reentrant. A caller that shares one
   buffer across an interrupt boundary must supply its own critical section. */

typedef struct common_ring_buffer {
    uint8_t *storage;
    size_t capacity;
    size_t head;
    size_t tail;
    size_t count;
} common_ring_buffer_t;

/* Bind caller-owned `storage` of `capacity` bytes to `rb`, resetting it empty.
   Returns false and leaves `rb` untouched when `rb` or `storage` is NULL, or
   `capacity` is 0. */
bool common_ring_buffer_init(common_ring_buffer_t *rb, uint8_t *storage, size_t capacity);

/* Append `value` as the newest byte. Returns false when the buffer is full or
   unusable. */
bool common_ring_buffer_push(common_ring_buffer_t *rb, uint8_t value);

/* Remove the oldest byte into `value`. Returns false when the buffer is empty,
   unusable, or `value` is NULL. */
bool common_ring_buffer_pop(common_ring_buffer_t *rb, uint8_t *value);

/* Number of stored bytes (0 for an unusable buffer). */
size_t common_ring_buffer_count(const common_ring_buffer_t *rb);

/* Configured capacity in bytes (0 for an unusable buffer). */
size_t common_ring_buffer_capacity(const common_ring_buffer_t *rb);

/* Discard every stored byte. A no-op for an unusable buffer. */
void common_ring_buffer_clear(common_ring_buffer_t *rb);

#ifdef __cplusplus
}
#endif
