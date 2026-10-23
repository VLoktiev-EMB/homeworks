# Toolchain smoke project (temporary)

This project is **temporary**. It exists only to verify that the pinned PlatformIO
toolchain, the shared configuration in `platformio.shared.ini`, and the shared libraries in
`lib/` actually build and link. It is **not coursework**: it carries no `homework.yaml`, no
`task.md`, and no report, and it will be deleted in Phase 3 once the shared `tests/` project
and the Unity suite supersede it.

The Arduino and ESP-IDF environments expect different `toolchain-xtensa-esp-elf` versions
(14.2.0 for Arduino and 15.2.0 for ESP-IDF). That is normal PlatformIO behaviour, not a
defect, and the versions must not be aligned by hand.
