# CLAUDE.md

## Project

Faceting Angle Finder (faf) — a digital angle readout for mast-style gem faceting machines.

## Tech stack

- **Language:** CircuitPython (on Adafruit Feather RP2350)
- **Sensor:** AS5600 hall-effect rotary encoder (I2C, addr 0x36)
- **Display:** 2.42" SSD1309 128x64 OLED (I2C, addr 0x3C, SSD1306-compatible driver)
- **Power:** 1000mAh LiPo via Feather's built-in charger
- **Enclosure:** PETG, designed for Bambu P1S

## Key files

- `todo.md` — master task list, parts, wiring, firmware plan, mechanical plan
- `hardware/bom.md` — bill of materials
- `firmware/` — CircuitPython code (code.py, boot.py, lib/)
- `enclosure/` — 3D-printable STEP and 3MF files
- `concept.md` — original project idea and Q&A
- `plan.md` — implementation plan with both sensor approaches evaluated

## Conventions

- Firmware is pure CircuitPython — no MicroPython, no C extensions
- AS5600 has no Adafruit driver; use raw I2C reads (two registers for 12-bit angle)
- All I2C devices share one bus: AS5600 at 0x36, OLED at 0x3C
- Accuracy target: 0.5 degrees. Display resolution: 0.1 degrees.
- Tare is single-point against the machine's protractor at any known angle

## Hardware pin assignments (Feather RP2350)

- STEMMA QT: AS5600 (I2C + power)
- SDA/SCL header: OLED (hand-wired)
- D5: Tare button (internal pullup, active low)
- D6: Menu button (internal pullup, active low)
- D9: Piezo buzzer

## Status

Pre-build. Parts ordered, waiting for faceting machine delivery. Next steps are breadboard prototyping (I2C scan, sensor read, OLED display).
