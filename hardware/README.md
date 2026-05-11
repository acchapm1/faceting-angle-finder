# hardware/

Wiring diagrams and bill of materials for the Faceting Angle Finder.

## Contents

| File | Purpose |
|---|---|
| `wiring-diagram.md` | ASCII wiring diagrams with labeled pins (block diagram, pin map, I2C bus, power, buttons, buzzer, cable run) |
| `bom.md` | Full bill of materials with part numbers, sources, and costs |

## Summary

All components share a single I2C bus on the Feather RP2350:

- **AS5600** (addr 0x36) connected via STEMMA QT cable
- **SSD1309 OLED** (addr 0x3C) hand-wired to the header
- **Tare button** on D5, **Menu button** on D6 (pulled up internally, wired to GND)
- **Piezo buzzer** on D9
- **LiPo battery** via JST PH connector on the Feather
