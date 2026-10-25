---
created: 2026-10-25T20:38:25.579Z
title: Promote merge_firmware.py into a shared tool
area: tooling
severity: minor
files:
  - homeworks/1_3-police-flasher/merge_firmware.py
  - homeworks/1_3-police-flasher/platformio.ini
---

## Problem

`merge_firmware.py` is a PlatformIO post action that merges the bootloader, the
partition table, and the application into `$BUILD_DIR/firmware.merged.bin`, because
Wokwi needs one complete flash image and the homework's custom 16 MB partition table
means the application binary alone is not bootable. It lives inside a single homework
directory today, so the next homework that needs a Wokwi flash image will copy it.

The duplication is not accidental: `STATE.md` records the Phase 04.2 decision that the
script stays project-local for now, because `espressif32@8.0.0` renamed the package to
`tool-esptool` and ships esptool 5, whose subcommand is `merge-bin` with
`--flash-mode` and `--flash-size` — so the script PlatformIO/Wokwi publishes cannot be
used unchanged. Promotion to `scripts/pio/` was explicitly deferred to Phase 7/8.

The open question now is whether that deferral still holds after the first real CI run,
or whether the shared home should be decided before the second homework copies the file.

## Solution

TBD — candidate shape:

1. Confirm the trigger: promote when a second homework needs a merged image, or when
   Phase 7 (simulation spike) / Phase 8 (CI) lands, whichever comes first. Record the
   trigger in the decision table so it does not stay implicit in `STATE.md`.
2. Decide the shared home and the contract: `scripts/pio/merge_firmware.py` consumed by
   `extra_scripts = post:../../scripts/pio/merge_firmware.py`, versus a published
   `library.json`/PlatformIO package. The relative-post-script path has to survive the
   per-homework build directory and must not break `pio run -d <project>`.
3. Keep the tool version-aware: it must resolve `tool-esptool` on espressif32@8.x and
   fail with a clear message on a platform whose package name or esptool major differs,
   rather than silently producing a wrong image.
4. Add a test that runs the merge against a fixture build directory and asserts the
   output path and offset ordering, so a shared tool has the same evidence a
   project-local one had.
5. Remove the per-homework copy in the same change, so two sources of truth never
   coexist.
