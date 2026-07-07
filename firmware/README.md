# firmware/

CircuitPython firmware for the Faceting Angle Finder.

## Contents

| File | Purpose |
|---|---|
| `code.py` | Main entry point — sensor reading, filtering, display, tare, buzzer logic |
| `boot.py` | Optional filesystem config for NVM writes (tare offset persistence) |
| `lib/` | Vendored CircuitPython libraries (`adafruit_ssd1306`, `adafruit_framebuf`, `adafruit_bus_device`) |

## Target hardware

- Adafruit Feather RP2350 (#6000)
- AS5600 magnetic rotary encoder (I2C, addr 0x36)
- 2.42" SSD1309 OLED (I2C, addr 0x3C)

## CircuitPython firmware

Running **CircuitPython 10.2.1**. The `.uf2` firmware images are git-ignored (large,
re-downloadable binaries) — grab the current build for this board from
<https://circuitpython.org/board/adafruit_feather_rp2350/>.

To (re)flash: double-click RESET to enter the UF2 bootloader (drive `RP2350`
appears), then copy the `.uf2` onto it. If the board is ever stuck in safe mode
("core code crashed hard / Heap allocation when VM not running"), reflash and then
run `import storage; storage.erase_filesystem()` from the REPL to reformat CIRCUITPY.

## Deploying

Copy the contents of this directory to the `CIRCUITPY` drive that appears when the Feather is plugged in via USB-C. The board runs `code.py` automatically on boot.

> `font5x8.bin` must live at the **root** of CIRCUITPY (not in `lib/`) — `adafruit_framebuf` loads it from the current working directory for OLED text.

Libraries can also be installed via circup:

```bash
circup install adafruit_ssd1306 adafruit_framebuf adafruit_bus_device
```

There is no official Adafruit driver for the AS5600 — the raw I2C driver is included in `code.py`.
