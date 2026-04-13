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

## Deploying

Copy the contents of this directory to the `CIRCUITPY` drive that appears when the Feather is plugged in via USB-C. The board runs `code.py` automatically on boot.

Libraries can also be installed via circup:

```bash
circup install adafruit_ssd1306 adafruit_framebuf adafruit_bus_device
```

There is no official Adafruit driver for the AS5600 — the raw I2C driver is included in `code.py`.
