# Embedded C and firmware architecture standard

This standard defines the engineering rules and best practices for writing reliable, maintainable,
and secure pure C (C99/C11) in this repository. It applies to all shared libraries (`lib/`),
homework firmwares (`homeworks/*/src/`, `homeworks/*/lib/`), and host tests (`tests/`).

Every AI agent and human engineer writing or reviewing firmware in this repository MUST comply
with this document.

---

## 1. Architecture and encapsulation

### 1.1. Opaque pointers and state encapsulation
- **[MUST]** Stateful domain entities must never leak private implementation details into public
  headers (`.h`).
- When a module's internal state must be protected against external tampering (such as corruption
  of timing periods, debounce states, or buffer indices):
  - In dynamic-allocation environments, declare an incomplete type in the header (`typedef struct foo foo_t;`)
    and define the structure exclusively in the `.c` file.
  - In static-allocation environments (mandatory here, see Section 2), if the caller must allocate
    the state structure directly on the stack or in BSS without dynamic allocation:
    - Separate public configuration (`foo_config_t`) from runtime state (`foo_t`).
    - Keep fields private by convention and treat the struct as opaque: callers must NEVER directly read
      or mutate struct members. All interactions MUST pass through accessor functions (`foo_get_*`,
      `foo_set_*`, `foo_update`).
    - Validate internal state invariants defensively inside update functions (e.g., check that denominators
      or timing periods are non-zero before division).

### 1.2. Hardware abstraction layer (HAL) and dependency injection
- **[MUST]** Pure domain logic (state machines, pattern generators, filters, protocol decoders, burst analyzers)
  must have ZERO framework headers (`Arduino.h`, `esp_*.h`, FreeRTOS) and ZERO direct vendor-lock calls
  (`digitalRead`, `micros`, `delay`, `Serial.print`).
- All hardware interactions in domain logic must be injected via abstract contract interfaces (`lib/port`):
  `port_gpio_t`, `port_time_t`, `port_i2c_t`, `port_spi_t`, `port_log_t`.
- **[MUST]** Every homework assignment must encapsulate its pure logic in a standalone homework-private
  library (e.g., `homeworks/<id>/lib/<name>/`) covered by host-side Unity tests (`[env:native]`), leaving
  `src/main.cpp` as a thin composition root that wires adapters to the domain logic.

### 1.3. Function tables in Flash (`.rodata`) vs RAM context
- **[MUST]** Interface contracts must separate the operations vtable (`const ops_t *`) from the runtime
  instance context (`void *ctx`):
  - The operations table contains function pointers and is declared as `const ops_t` placed in Flash/ROM
    (`.rodata`).
  - Storing bare function pointers directly inside mutable RAM structs per instance is forbidden in new
    contracts: it wastes scarce RAM and introduces security/safety vulnerabilities (function pointers in
    RAM can be overwritten by buffer overflows).
  - The instance struct must only hold two pointers: `const ops_t *ops` and `void *ctx`.
- **[MUST]** Public contract headers must provide safe, defensive inline helper functions (e.g.,
  `port_gpio_write()`, `port_time_now_ms()`) that verify `NULL` pointers before dispatching through
  the function pointer.

### 1.4. Symbol prefixes (Pseudo-namespaces)
- **[MUST]** To avoid symbol collisions in C flat namespaces:
  - All public types, enums, structs, constants, and functions must be prefixed with the module name
    (e.g., `common_ring_buffer_*`, `port_gpio_*`, `police_pattern_*`, `blink_modes_*`).
  - Enum members must include the type prefix in uppercase (e.g., `PORT_GPIO_INPUT`, `PORT_STATUS_OK`).

---

## 2. Memory and resource management

### 2.1. Zero dynamic memory allocation
- **[MUST]** Firmware targets and shared firmware libraries MUST NEVER use dynamic memory allocation
  (`malloc`, `calloc`, `realloc`, `free`).
- Storage must be:
  1. Statically allocated at the composition root (`main.cpp`), OR
  2. Caller-owned and passed into initialization functions by pointer with explicit capacity bounds.

### 2.2. Defensive sizing and buffer bounds
- **[MUST]** Always calculate buffer sizes using `sizeof(*ptr)` rather than `sizeof(type)` to remain
  resilient against future type refactoring.
- **[MUST]** All string and buffer manipulation must require an explicit capacity limit (e.g.,
  `snprintf` instead of `sprintf`, bounded `memcpy` / `strncpy` equivalents).
- **[MUST]** Bounded queues and ring buffers must explicitly guard against overflow and return false or
  a designated error status when capacity is exceeded.

### 2.3. Ring buffer efficiency and concurrency
- **[SHOULD]** In ring buffers and cyclic queues, avoid modulo arithmetic (`% capacity`) on platforms
  lacking hardware integer division. Prefer power-of-two capacities with bitwise masking (`(head + 1) & mask`)
  or an explicit boundary check (`if (++head >= capacity) head = 0;`).
- When a ring buffer is intended for Single-Producer Single-Consumer (SPSC) lock-free communication across
  an ISR or task boundary, the implementation must not share a mutable `count` variable.

---

## 3. Header hygiene and preprocessor

### 3.1. Standard include guards
- **[MUST]** Every header file (`.h`) must use standard ISO C include guards (`#ifndef MODULE_H / #define MODULE_H ... #endif`).
  `#pragma once` may be added as an optimization, but standard guards are required for strict ISO C and
  MISRA C:2012 Rule 4.10 compliance.

### 3.2. Minimal `#include` and forward declarations
- **[MUST]** Headers must only `#include` what is strictly necessary to define their own types.
- If a header only references a struct via pointer (e.g., `const port_time_t *time`), prefer a forward
  declaration (`typedef struct port_time port_time_t;`) over including the full foreign header, avoiding
  unnecessary coupling between library layers.

### 3.3. Static internal linkage
- **[MUST]** Every function and file-scope variable that is not part of the public API must be declared
  `static` in the `.c` file.
- Global mutable variables are strictly forbidden outside the single composition root (`main.cpp`).

### 3.4. Pure C clean boundaries
- **[MUST]** All public header files must wrap declarations in `extern "C" { ... }` blocks when compiled
  under C++ (`#ifdef __cplusplus`).
- C interface headers and pure logic must never use C++ language extensions (such as pass-by-reference
  `&`, `class`, or `nullptr`).

---

## 4. Type safety and const-correctness

### 4.1. Fixed-width integer types
- **[MUST]** Always use explicit-width integer types from `<stdint.h>` (`uint8_t`, `int16_t`, `uint32_t`, etc.)
  for hardware registers, pin numbers, timestamps, buffer indices, and serial communication protocols.
- Naked platform-dependent types (`int`, `long`, `short`, `unsigned`) are prohibited for hardware and
  protocol state, and are allowed only for loop counters or C standard library integration (`size_t`).

### 4.2. Boolean flags
- **[MUST]** Use `<stdbool.h>` and `bool`, `true`, `false` for all boolean flags and predicates.
  Do not invent custom integer macros or `typedef int BOOL`.

### 4.3. Comprehensive const-correctness
- **[MUST]** Pass all read-only buffer pointers as `const uint8_t *` or `const char *`.
- **[MUST]** Lookup tables, step sequences, and constant configuration tables must be qualified as
  `static const` so the linker places them in Flash memory (`.rodata`) rather than consuming precious RAM.

---

## 5. Concurrency, interrupts (ISR), and error handling

### 5.1. Volatile qualification and atomic variables
- **[MUST]** Any variable or buffer modified inside an Interrupt Service Routine (ISR) and read in the
  main loop / task MUST be declared `volatile` (or use C11 `<stdatomic.h>`).
- If an array or struct is shared with an ISR, the elements themselves or the pointer to the buffer
  must be qualified `volatile` to prevent the compiler from optimizing out memory reads or caching stale values.

### 5.2. Minimal critical sections & Ping-Pong double buffering
- **[MUST]** Keep ISRs as short as humanly possible: record timestamp, sample pin/register, increment
  index, and exit. Never perform logging, string formatting, or heavy computation in an ISR.
- **[MUST]** Critical sections in the main loop (where interrupts are disabled) must be bounded to a few
  CPU cycles.
- **[MUST]** NEVER execute a bulk memory copy (e.g., `memcpy` of a 256-entry array) or blocking I/O with
  interrupts disabled.
- **[SHOULD]** Use **Ping-Pong (double) buffering**:
  - The ISR writes to the currently active buffer.
  - When the buffer is ready, the main loop swaps buffer pointers inside a momentary critical section
    (taking < 10 CPU cycles).
  - The main loop then processes and logs the captured data outside the critical section with interrupts
    fully enabled.

### 5.3. Multi-core SMP synchronization (ESP32)
- **[MUST]** On multi-core microcontrollers (such as ESP32 / ESP32-S3), be aware that simple interrupt-disable
  primitives (`noInterrupts()`, `portDISABLE_INTERRUPTS()`) are local to the executing core only.
- When an ISR can trigger on Core 0 while tasks execute on Core 1, protect shared state using a spinlock
  (`portENTER_CRITICAL` / `portEXIT_CRITICAL`) or lock-free atomic queues.

### 5.4. Non-blocking asynchronous I/O
- **[MUST]** The main execution loop (`loop()`) must never be stalled by synchronous, blocking I/O.
- Dumping large debug records over UART (e.g., 256 lines at 115200 baud = ~450 ms of blocking transmission)
  freezes the system and drops subsequent events. Pace serial transmissions or buffer them asynchronously.

### 5.5. Explicit error propagation
- **[MUST]** Public functions that can fail must return a status enum (`port_status_t`) or a `bool`.
  Never silently drop or ignore error returns from hardware transactions (I2C, SPI, GPIO configuration).
- **[MUST]** Check all pointer arguments for `NULL` at public API boundaries before dereferencing.

---

## 6. Code review checklist for agents

When authoring or reviewing firmware code in this repository, verify every item below:

| Dimension | Review check |
|:---|:---|
| **Architecture** | Is pure domain logic decoupled from Arduino/ESP-IDF into a pure C library? |
| **Architecture** | Are hardware dependencies injected via `lib/port` contracts? |
| **Architecture** | Are vtable function pointers placed in Flash (`const ops *`) instead of RAM? |
| **Architecture** | Are all public functions and types prefixed with the module namespace? |
| **Memory** | Is dynamic allocation completely absent (`malloc`/`free` = 0)? |
| **Memory** | Are buffer sizes computed with `sizeof(*ptr)` and explicitly bounded? |
| **Headers** | Does the header use standard `#ifndef` include guards and minimal `#include`s? |
| **Headers** | Are internal functions and file-scope variables marked `static`? |
| **Types** | Are fixed-width types (`uint8_t`, `uint32_t`) and `bool` used everywhere? |
| **Types** | Are constant tables and input buffers qualified `const`? |
| **Concurrency**| Are all variables shared with an ISR qualified `volatile`? |
| **Concurrency**| Are critical sections minimal (< 10 cycles, zero-copy buffer swap, no `memcpy`)? |
| **Reliability**| Are pointer arguments checked for `NULL` before dereferencing? |
| **Reliability**| Are timing differences computed via unsigned arithmetic `(now - since)`? |
| **Reliability**| Are divisors checked against zero before division? |
