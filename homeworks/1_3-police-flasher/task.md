---
source_url: https://github.com/VLoktiev-EMB/homeworks
retrieved: 2026-10-23T00:00:00Z
attribution: Course handout 1.3 (paraphrased); original access-restricted and not redistributed
license: LicenseRef-Proprietary
---

# Police Flasher

## Task

Build a police-style flasher on an ESP32-S3 board with the Arduino framework. The firmware
drives a small set of LED outputs from a state machine, repeats a recognisable alternating
pattern, and lets the user choose both the pattern and its speed while the board runs.

### Objective

Produce a repeating beacon pattern in which the primary LEDs alternate, and keep the
pattern logic separate from the board so it can be exercised on a host.

### Observable behaviour

- The two primary LEDs alternate; they are never lit at the same time.
- The sequence repeats steadily for as long as the board runs.
- A third LED joins the pattern with an additional flash.
- The pattern can be changed at run time, without a reset.
- The flash rate can be changed through several discrete speeds.
- The flasher also works on a single GPIO: the pin drives two LEDs connected in opposite
  directions, so a high level lights one and a low level lights the other.

### Extensions

The assignment calls for the core alternation plus four extensions:

1. A third LED takes part in the pattern.
2. The speed is variable and selected at run time.
3. A richer pattern plays in addition to the plain alternation.
4. The flasher runs with only one GPIO.

### Acceptance criteria

- The project builds for its declared ESP32-S3 Arduino environment.
- The pattern logic is covered by native unit tests, and the whole suite passes.
- On every frame of the alternating pattern, exactly one of the two primary LEDs is lit.
- Pattern and speed selection behave as the report documents.
- The wiring diagram in `assets/diagram.json` and the pin map in the report agree.
