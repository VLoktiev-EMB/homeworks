---
status: diagnosed
trigger: "Test 1 in UAT (.planning/phases/09-agent-workflow-and-skills/09-UAT.md). Command: `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20`, run from the repository root. Actual: `.skill-state/logs/1_3-police-flasher.log: REFUSED — capture unavailable: no bytes captured` (exit 1). Reproduced twice; RESET pressed during the second 20 s window; firmware confirmed flashed; board on /dev/cu.usbmodem2101 (USB VID:PID 303A:1001)."
created: 2026-10-27T00:00:00Z
updated: 2026-10-27T00:00:00Z
goal: find_root_cause_only
---

## Current Focus

hypothesis: "`pio device monitor` opens /dev/cu.usbmodem2101 with DTR and RTS asserted (pyserial's defaults, because PlatformIO leaves monitor_dtr/monitor_rts unset). On the ESP32-S3 USB-Serial-JTAG, RTS asserted is the chip-reset state (esptool's USBJTAGSerialReset uses RTS=True for reset; idle/out-of-reset is DTR=0/RTS=0). The monitor therefore resets/holds the S3 in reset or a reset loop for the whole capture, so the application never runs and emits nothing. Physical EN cannot override a driven-low EN, which is why the user's RESET press during the second window changed nothing. A second, independent contributing condition: the firmware emits exactly one line in setup() and nothing in loop(), so even with correct line state a passive capture that starts after boot would still collect zero bytes."
test: "Trace the invocation end to end in source: serial_capture argv (no DTR/RTS), PlatformIO monitor option defaults and pyserial open(), esptool USB-JTAG reset truth table, and the firmware's complete output surface."
expecting: "Confirmed. If instead the ROM console were confined to UART0, the sdkconfig would show no USB secondary and the firmware would have to use Serial (it does not)."
next_action: "Write the diagnosis; no fix in this mode."

## Symptoms

expected: "With a board connected after a confirmed upload, run `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20`. Exit 0, a `CAPTURED — N bytes captured` line naming `.skill-state/logs/1_3-police-flasher.log`, and a log holding the raw device bytes."
actual: "`.skill-state/logs/1_3-police-flasher.log: REFUSED — capture unavailable: no bytes captured` (exit 1). Reproduced twice. RESET (EN) pressed during the second 20 s window; still zero bytes."
errors: "capture unavailable: no bytes captured (exit 1)"
reproduction: "UV run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20 from the repository root, board on /dev/cu.usbmodem2101."
started: "Discovered during UAT of phase 09 (2026-10-27)."

## Eliminated

- hypothesis: "(a) The application console is routed to UART0 while the only connected port is USB-Serial-JTAG, so the log bytes never reach the host."
  evidence: "The firmware never uses `Serial`. It writes via `port_log_write` -> `lib/arduino/src/log.c` `log_printf`, and in the active core `log_printf` -> `ets_printf` (`framework-arduinoespressif32/cores/esp32/esp32-hal-uart.c` `log_printfv`/`log_printf`). On ESP32-S3 `esp_rom_printf` is aliased to `ets_printf` (`components/esp_rom/esp32s3/ld/esp32s3.rom.api.ld:48`), and the ROM console output is mirrored to the USB-Serial-JTAG: the app's actual compile config `framework-arduinoespressif32-esp32s3-libs/qio_opi/include/sdkconfig.h` has `CONFIG_ESP_CONSOLE_UART_DEFAULT=1` (primary UART0), `CONFIG_ESP_CONSOLE_SECONDARY_USB_SERIAL_JTAG=1`, `CONFIG_ESP_ROM_CONSOLE_OUTPUT_SECONDARY=1`, `CONFIG_USJ_ENABLE_USB_SERIAL_JTAG=1`. `esp_rom_install_uart_printf()` sets `g_usb_print=true` on S3 and is called by the bootloader (`bootloader_support/src/bootloader_console.c:55`) and CPU1 startup (`esp_system/port/cpu_start.c:239`). ARDUINO_USB_CDC_ON_BOOT=0 only affects the `Serial` object (`HardwareSerial.h:438-452` -> `Serial0`), which this firmware never touches. Corroborated in the field: PlatformIO issue #1733 shows the S3 ROM banner (`ESP-ROM:esp32s3...`, `waiting for download`) arriving over the USB port. So the log line is not confined to UART0."
  timestamp: 2026-10-27

- hypothesis: "(c) The monitor selects the wrong port or fails silently."
  evidence: "`pio device list --json-output` shows exactly one board port: `/dev/cu.usbmodem2101`, `USB VID:PID=303A:1001`. The board manifest `boards/esp32-s3-devkitc-1.json` declares `hwids: [[0x303A,0x1001]]`, and PlatformIO's `SerialPortFinder._find_board_device` matches it. The helper's failure is `no bytes captured`, not `command exited N before the bound`; `capture_pty` raises the latter on EOF/read error, so the monitor stayed alive for the full 20 s (a reconnect/retry loop), not an early port-selection failure."
  timestamp: 2026-10-27

- hypothesis: "(d) Firmware/board mismatch (wrong environment or wrong binary)."
  evidence: "`homeworks/1_3-police-flasher/platformio.ini` has `default_envs = esp32s3_arduino`; the upload command from `hw-flash` is `pio run -d homeworks/1_3-police-flasher -t upload` (no `-e`, single default env). The board is an ESP32-S3 (VID:PID 303A:1001); the env targets `board = esp32-s3-devkitc-1`, `framework = arduino`. The user confirmed the flash. No evidence of a mismatch."
  timestamp: 2026-10-27

- hypothesis: "(e) `--raw`/`--quiet`/PTY interaction drops the bytes."
  evidence: "The automated suite (`scripts/tests/test_serial_capture.py`) proves the PTY path preserves `bytes(range(256))` and that the child sees a TTY; a piped child is the case that fails. `--raw` only disables encodings/transformations and `--quiet` only suppresses diagnostics; device data goes to the child's stdout (the PTY slave), and the helper reads it on the master. The monitor's stderr is `subprocess.DEVNULL`, so diagnostics are lost, not device bytes. Ruled out as the cause of zero device bytes."
  timestamp: 2026-10-27

- hypothesis: "(b) Boot-only logging alone explains the zero bytes (as the sole cause)."
  evidence: "It is a real contributing gap — `homeworks/1_3-police-flasher/src/main.cpp` logs once in `setup()` (`pattern ready` / `pattern init failed`) and `loop()` only ticks the controller; grep finds no other output anywhere in the firmware or libraries. But it cannot by itself explain the second run: with the chip actually running the app, the user's physical RESET would re-run `setup()` and re-emit the line, and the USB-JTAG buffers output (IDF USB-JTAG console docs: small internal buffer plus a 50 ms wait when full). The unchanged zero result after RESET instead points to the chip not running at all — the DTR/RTS hold. Retained as a contributing condition, not the sole cause."
  timestamp: 2026-10-27

## Evidence

- timestamp: 2026-10-27
  checked: "`scripts/serial_capture.py` `_build_command` (lines 288-303)"
  found: "The monitor argv is exactly `pio device monitor -d homeworks/<id> --raw --quiet` (+ `-e`/`-b` only when supplied). No `--dtr`, no `--rts`, no reset control. `capture_and_store` (275-285) raises `CaptureFailed('no bytes captured')` when the collected byte string is empty."
  implication: "The helper has no way to influence the serial line state that the monitor applies at open."

- timestamp: 2026-10-27
  checked: "PlatformIO monitor option defaults and open path"
  found: "`platformio/project/options.py` defines `env.monitor_rts` and `env.monitor_dtr` with `default=None`; `apply_project_monitor_options` therefore leaves them `None`. `platformio/device/monitor/terminal.py:178-199` sets `serial_instance.dtr/rts` only when the option is not None, then calls `serial_instance.open()`."
  implication: "PlatformIO does not set the lines; pyserial's defaults decide them."

- timestamp: 2026-10-27
  checked: "pyserial defaults and open behaviour"
  found: "`serial/serialutil.py:216-217` initialises `_rts_state = True` and `_dtr_state = True`; `serial/serialposix.py:335-338` calls `_update_dtr_state()` and `_update_rts_state()` during `open()` (dsrdtr/rtscts are false), i.e. it asserts both control lines on the open port."
  implication: "`pio device monitor` opens /dev/cu.usbmodem2101 with DTR asserted and RTS asserted."

- timestamp: 2026-10-27
  checked: "esptool USB-JTAG reset truth table"
  found: "`tool-esptoolpy/esptool/reset.py` `USBJTAGSerialReset.reset()` starts at `_setRTS(False); _setDTR(False)  # Idle`, marks `_setRTS(True)  # Reset`, and ends `_setDTR(False); _setRTS(False)  # Chip out of reset`. `ClassicReset`/`HardReset` likewise document `_setRTS(True)  # EN=LOW, chip in reset`."
  implication: "For the ESP32-S3 USB-Serial-JTAG, RTS asserted is the reset state; the out-of-reset idle state is DTR=0/RTS=0. The monitor leaves RTS asserted, so the chip is reset/held or repeatedly reset, and the app never runs normally."

- timestamp: 2026-10-27
  checked: "DTR/RTS control is actually operative on this Mac/board"
  found: "The upload leg `pio run -t upload` succeeded and uses esptool's USB-JTAG reset sequence over the same `/dev/cu.usbmodem2101`; `pio device list` shows the port and VID:PID 303A:1001."
  implication: "The SET_CONTROL_LINE_STATE path works on this host and device, so the monitor's asserted RTS/DTR are effective, not ignored."

- timestamp: 2026-10-27
  checked: "firmware output surface"
  found: "Grep across `homeworks/1_3-police-flasher/src`, its `lib/`, and `lib/arduino` finds exactly one output path: `main.cpp:49` `port_log_write(..., 'pattern ready')` and `main.cpp:51` `'pattern init failed'`, both in `setup()`. `loop()` calls `pattern_controller_tick` only; the controller has no logger and no print. `lib/arduino/src/log.c:28` forwards to `log_printf`."
  implication: "The firmware produces bytes only during a short window at boot; there is no output during the 20 s capture."

- timestamp: 2026-10-27
  checked: "console routing in the actual compiled configuration"
  found: "The env uses `board_build.arduino.memory_type = qio_opi`, so the app compiles against `framework-arduinoespressif32-esp32s3-libs/qio_opi/include/sdkconfig.h`: `CONFIG_ESP_CONSOLE_UART_DEFAULT 1` (line 922), `CONFIG_ESP_CONSOLE_SECONDARY_USB_SERIAL_JTAG 1` (923), `CONFIG_ESP_ROM_CONSOLE_OUTPUT_SECONDARY 1` (456), `CONFIG_USJ_ENABLE_USB_SERIAL_JTAG 1` (799). `esp32s3.rom.api.ld:48` aliases `esp_rom_printf = ets_printf`; `esp_rom_install_uart_printf()` (esp_rom_sys.c:72-85) sets `g_usb_print = true`; it is called by the bootloader and CPU1 startup."
  implication: "The firmware's `log_printf`/`ets_printf` output is mirrored to the USB-Serial-JTAG, so console routing is not why the host saw zero bytes."

- timestamp: 2026-10-27
  checked: "Espressif esptool documentation, ESP32-S3 Boot Mode Selection (https://docs.espressif.com/projects/esptool/en/latest/esp32s3/advanced-topics/boot-mode-selection.html)"
  found: "Verbatim: 'Some OS and/or drivers may activate RTS and or DTR automatically when opening the serial port (true only for some serial terminal programs, not esptool), pulling them low together and holding the ESP in reset. If RTS is wired directly to EN then RTS/CTS \"hardware flow control\" needs to be disabled in the serial program to avoid this.' The same page: DTR/RTS are active-low (True = 0 V), and DTR/RTS drive GPIO0 and EN."
  implication: "This is the exact observed failure: pyserial asserts DTR and RTS on open (active low -> both low), which holds the chip in reset. The monitor's own open of the port prevents the application from running."

- timestamp: 2026-10-27
  checked: "external field reports"
  found: "PlatformIO issue #4354: the monitor 'will use the RTS/DTR lines, too - which effectively resets the microcontroller and preventing it from running'. PlatformIO issue #1733: an ESP32-S3 over USB-JTAG ends in `boot:0x0 (DOWNLOAD(USB/UART0)) ... waiting for download`; a commenter's working fix is `pio device monitor --rts 1 --dtr 1` plus a manual RESET, noting the default monitor line state is what drops the S3 into download mode. A field note for pyserial on ESP32-S3 USB-JTAG recommends pre-setting `dtr=False`/`rts=False` before `open()` to stop the port-open reset."
  implication: "The monitor's line state on ESP32-S3 native USB is a known cause of the chip not running the application during monitoring; the exact polarity that counts as idle differs between USB-CDC (1,1) and USB-Serial-JTAG (0,0 per esptool)."

## Resolution

root_cause: "primary: `scripts/serial_capture.py` runs `pio device monitor` without `--dtr`/`--rts` (and the project sets no `monitor_dtr`/`monitor_rts`), so pyserial opens /dev/cu.usbmodem2101 with DTR and RTS asserted. On the ESP32-S3 USB-Serial-JTAG, RTS asserted is the chip-reset state (esptool's USBJTAGSerialReset: RTS=True 'Reset', idle/out-of-reset DTR=0/RTS=0). The monitor therefore resets and/or holds the S3 in reset or a reset loop for the entire capture; the application never runs, emits nothing, and the physical EN button cannot override a driven-low EN. Contributing condition: the firmware emits exactly one line in `setup()` and nothing in `loop()`, so even a correct line state would give a passive capture that starts after boot zero bytes. Both must be addressed for the UAT truth to hold."
fix: "(not applied — find_root_cause_only)"
verification: "(none — diagnosis only)"
files_changed: []
