---
source_url: TODO
retrieved: TODO
attribution: TODO
license: TODO
---

# Dual LED Modes with External and BOOT Buttons

## Task

Paraphrase: configure two GPIO pins as outputs driving red LEDs through 220 ohm
series resistors, configure an external button on GPIO21 as `INPUT_PULLUP`, and
use the onboard BOOT button on GPIO0 as `INPUT` because the DevKitC-1 provides
its external pull-up. The firmware keeps the selected mode in RAM and starts in
mode 1. Mode 1 (external button) blinks both LEDs together every 200 ms; mode 2
(BOOT) alternates them every 1000 ms. A press of either button selects its mode
until the other button is pressed.

## Acceptance criteria

- Both LEDs blink together with a 200 ms period in mode 1.
- The LEDs alternate with a 1000 ms period in mode 2.
- The external button selects mode 1; BOOT selects mode 2.
- The selected mode persists while powered and resets to mode 1 after reset.
- The target build succeeds and the pure logic passes native tests.
- The wiring and bill of materials agree with `assets/diagram.json`.
