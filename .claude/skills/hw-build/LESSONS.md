# Lessons

## 2026-10-26 — initial 0.1 contract, phase 9 planning run

- The native environment repeats `-Wall -Wextra -Werror`, so a signed/unsigned
  comparison or an unused local fails only the host build while the target build stays
  green. Both host fakes must be reset in `setUp`, and the idle `INPUT_PULLUP` button
  must be seeded to `PORT_GPIO_HIGH`, because the fake models every pin as LOW at reset
  and that level reads as "button pressed" (F-05). The rule it implies: treat a red
  native run as a fixture or warning-shape question before treating it as a controller
  bug.
