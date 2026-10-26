#include "common/ring_buffer.h"

/* A buffer is usable only when it was bound to caller-owned storage. The
   `storage` / `capacity` pair is the single source of truth: there is no
   separate initialised flag that could disagree with it. */
static bool ring_buffer_is_usable(const common_ring_buffer_t *rb)
{
    return rb != NULL && rb->storage != NULL && rb->capacity > 0u;
}

bool common_ring_buffer_init(common_ring_buffer_t *rb, uint8_t *storage, size_t capacity)
{
    if (rb == NULL || storage == NULL || capacity == 0u) {
        return false;
    }

    rb->storage = storage;
    rb->capacity = capacity;
    rb->head = 0u;
    rb->tail = 0u;
    rb->count = 0u;
    return true;
}

bool common_ring_buffer_push(common_ring_buffer_t *rb, uint8_t value)
{
    if (!ring_buffer_is_usable(rb) || rb->count >= rb->capacity) {
        return false;
    }

    /* `head` is the next write index; `count` alone decides full, so the
       buffer never needs to reserve one slot as a sentinel. */
    rb->storage[rb->head] = value;
    rb->head = (rb->head + 1u) % rb->capacity;
    rb->count += 1u;
    return true;
}

bool common_ring_buffer_pop(common_ring_buffer_t *rb, uint8_t *value)
{
    if (!ring_buffer_is_usable(rb) || rb->count == 0u || value == NULL) {
        return false;
    }

    /* `tail` is the next read index; `count` alone decides empty. */
    *value = rb->storage[rb->tail];
    rb->tail = (rb->tail + 1u) % rb->capacity;
    rb->count -= 1u;
    return true;
}

size_t common_ring_buffer_count(const common_ring_buffer_t *rb)
{
    if (!ring_buffer_is_usable(rb)) {
        return 0u;
    }
    return rb->count;
}

size_t common_ring_buffer_capacity(const common_ring_buffer_t *rb)
{
    if (!ring_buffer_is_usable(rb)) {
        return 0u;
    }
    return rb->capacity;
}

void common_ring_buffer_clear(common_ring_buffer_t *rb)
{
    if (!ring_buffer_is_usable(rb)) {
        return;
    }

    rb->head = 0u;
    rb->tail = 0u;
    rb->count = 0u;
}
