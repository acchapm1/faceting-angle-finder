# Bill of Materials

> Faceting Angle Finder (faf)
> Last Updated: 2026-04-13

## Order from Adafruit

| # | Part | Part # | Approx. | Notes |
|---|---|---|---|---|
| 1 | Feather RP2350 (no PSRAM) | #6000 | $12.50 | MCU, STEMMA QT built in, LiPo charger, CircuitPython |
| 2 | AS5600 breakout (STEMMA QT) | #6357 | $5.95 | I2C, addr 0x36, STEMMA QT connectors |
| 3 | 6mm x 3mm diametrically-magnetized neodymium magnet | add-on with #6357 | $2.50 | MUST be diametrically magnetized (poles on sides, not faces) |
| 4 | STEMMA QT / Qwiic cable, 400mm | #5385 or similar | $1.50 | AS5600 on pivot to Feather in display box (12-15" run) |

## Order from Amazon / generic

| # | Part | Approx. | Notes |
|---|---|---|---|
| 5 | 3.7V LiPo battery, 1000mAh, JST PH 2-pin | $8-10 | Plugs into Feather battery header, ~15-18 hrs runtime, ~50x30x6mm |
| 6 | Momentary tactile buttons (x2) | $1 | 6mm through-hole, tare + menu |
| 7 | Piezo buzzer, passive, 3.3V | $1 | Target-angle alert |
| 8 | M3x8 socket head screws (x4) | $2 | Sensor bracket + display box assembly |
| 9 | M3 heat-set inserts (x4) | $1 | Press into PETG printed parts |

## Already have

| Part | Notes |
|---|---|
| 2.42" SSD1309 128x64 OLED (HiLetgo, 4-pin I2C) | Display, 71x43mm board, I2C addr 0x3C, SSD1306-compatible driver |
| XIAO RP2040 | Kept as spare, not used in this build |
| PETG filament | For 3D-printed enclosures on P1S |
| Bambu Labs P1S | For printing enclosures |
| Cyanoacrylate (superglue) or UV-cure adhesive | To bond magnet to axle end |

## Total new spend

~$30-37 (Adafruit parts + battery + generic parts + shipping). Saved $3-5 by using the OLED already on hand.

## Power budget

| Component | Draw | Notes |
|---|---|---|
| Feather RP2350 (active) | ~30 mA | M33 cores running, I2C polling |
| AS5600 | ~6 mA | Continuous measurement |
| SSD1309 2.42" OLED | ~20-30 mA | Depends on pixel fill |
| **Total steady state** | **~55-65 mA** | |

With a 1000 mAh battery: **~15-18 hours runtime.** Charges in ~5 hours over USB-C (Feather charges at 200 mA).
