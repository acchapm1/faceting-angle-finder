# Angle Finder — Alternative Hardware Builds (MicroPython)

Both options use Waveshare all-in-one boards with integrated touch displays, paired with the AS5600 hall sensor on the pivot axle. These boards run **MicroPython** (not CircuitPython).

See `alt-hardware.md` for the hardware links.

---

## Option 1: RP2350-Touch-LCD-3.5 (the big screen)

### Board specs

| Spec | Detail |
|---|---|
| MCU | RP2350B, dual Cortex-M33 @ 150 MHz |
| RAM | 520 KB SRAM |
| Flash | 16 MB |
| Display | 3.5" IPS, 320x480, 65K colors, ST7796 driver (SPI) |
| Touch | Capacitive, FT6336 controller (I2C) |
| IMU | QMI8658 6-axis accel + gyro (could serve as Option B backup) |
| RTC | PCF85063 with battery backup |
| Audio | ES8311 codec + onboard mic + MX1.25 speaker connector |
| Power mgmt | AXP2101 PMIC |
| Battery | 3.7V MX1.25 LiPo header (charge + discharge) |
| USB | USB-C |
| Camera | OV2640/OV5640 interface (unused) |
| Storage | TF/microSD card slot |
| Expansion | 22x GPIO, 2x SPI, 2x I2C, 2x UART, 7x ADC, 18x PWM |
| Price | ~$25–30 (Waveshare / Amazon) |

Source: [Waveshare docs](https://docs.waveshare.com/RP2350-Touch-LCD-3.5), [Waveshare product page](https://www.waveshare.com/rp2350-touch-lcd-3.5.htm)

### Pros

- Largest display — 3.5" color IPS with touch gives a polished, professional UI
- 320x480 resolution — room for big angle digits, touch buttons, target display, status bar
- Built-in IMU — QMI8658 can serve as Option B accelerometer backup without extra hardware
- Built-in RTC — could log cutting sessions with timestamps
- Built-in audio codec — can drive a speaker for beep alerts (no separate piezo needed)
- Built-in battery charging — just plug in a LiPo
- 22 GPIO available — plenty of room for AS5600 I2C + future expansion
- RP2350B is very fast (150 MHz M33) — smooth UI updates

### Cons

- **Largest enclosure** — the 3.5" screen makes the display box significantly bigger; may be too bulky to clamp to the mast post. A tabletop stand with a cable to the sensor bracket is more realistic.
- **MicroPython only** — no CircuitPython board definition available
- **Most complex firmware** — driving the ST7796 color LCD + FT6336 touch + building a full touch UI is more work than an OLED with two buttons
- **Most expensive option** — ~$25–30 for the board alone
- **Overkill for v1** — camera, microSD, audio codec, RTC are all unused for a basic angle finder

### External wiring (AS5600 only)

The board has 22 GPIO and 2 I2C controllers. Internal peripherals (touch, IMU, RTC, PMIC, audio) share I2C0. The AS5600 goes on I2C1 using two free GPIO pins from the expansion header.

```
Internal (already on-board):
  ST7796 display ── SPI
  FT6336 touch   ── I2C0
  QMI8658 IMU    ── I2C0
  PCF85063 RTC   ── I2C0
  AXP2101 PMIC   ── I2C0
  ES8311 audio   ── I2C0

External (you wire to expansion header):
  AS5600 (addr 0x36) ── I2C1 (two free GPIO pins as SDA1/SCL1)
  VCC → 3V3
  GND → GND

LiPo battery → MX1.25 battery header (built in)
```

**Pin confirmation needed:** check the schematic or expansion header pinout to identify which specific GPIO pins are broken out and can be configured as I2C1. The RP2350 is flexible — almost any GPIO pair can be assigned to I2C1 in software.

### Firmware approach (MicroPython)

1. **Display:** Use Waveshare's provided ST7796 MicroPython driver. Framebuffer writes for the angle display, colored rectangles for touch buttons.
2. **Touch:** FT6336 driver (Waveshare provides). Read x/y coordinates, map to on-screen button regions.
3. **AS5600:** Same raw I2C code as `todo-hall.md`, on I2C1:
   ```python
   from machine import I2C, Pin
   i2c_ext = I2C(1, sda=Pin(XX), scl=Pin(XX), freq=400000)
   ```
4. **IMU (bonus):** Read QMI8658 for tilt cross-check against AS5600 — no extra hardware needed.
5. **Audio alert:** Drive the speaker through ES8311 for target-reached beep, or just toggle a GPIO if a simpler piezo is preferred.

### UI layout (320x480)

```
┌──────────────────────────────┐
│                              │
│         4 3 . 2 °            │  ← main angle, large font
│                              │
│  ────────────────────────── │
│   Target: 43.0°     [SET]    │  ← target + touch button
│   ▲ 0.2°  (raise)           │  ← directional hint
│                              │
│  ┌────────┐  ┌────────┐     │
│  │  TARE  │  │  HOLD  │     │  ← touch buttons
│  └────────┘  └────────┘     │
│                              │
│  Magnet: OK  │  Batt: 87%   │  ← status bar
└──────────────────────────────┘
```

### Enclosure

- Board + screen is roughly 90x55mm — enclosure needs to be ~100x65x20mm minimum.
- Too bulky for a mast clamp — **tabletop stand** (angled, with a cable running to the sensor bracket on the pivot) is the better approach.
- Or: mount flat on the table, tilted toward you with a small wedge/easel printed in PETG.

---

## Option 2: RP2040-Touch-LCD-1.69 (the compact one)

### Board specs

| Spec | Detail |
|---|---|
| MCU | RP2040, dual Cortex-M0+ @ 133 MHz |
| RAM | 264 KB SRAM |
| Flash | 4 MB |
| Display | 1.69" IPS, 240x280, 262K colors, ST7789V2 driver (SPI) |
| Touch | Capacitive, CST816T controller (I2C) |
| IMU | QMI8658 6-axis accel + gyro |
| RTC | PCF85063A with battery backup |
| Buzzer | onboard (no external piezo needed) |
| Battery | 3.7V LiPo header with ETA6096 charge IC |
| USB | USB-C |
| Expansion | 4x multi-function GPIO (I2C + UART capable) |
| Price | ~$17–22 (Waveshare) / ~$30 (Amazon) |

Source: [Waveshare product page](https://www.waveshare.com/rp2040-touch-lcd-1.69.htm), [Waveshare wiki](https://www.waveshare.com/wiki/RP2040-Touch-LCD-1.69)

### Pros

- **Most self-contained.** Display, touch, buzzer, IMU, RTC, and battery charging all on one tiny board. Add the AS5600 and you're done — fewest external parts of any build option.
- **Built-in buzzer** — no separate piezo to wire. Target-reached alert works out of the box.
- **Built-in IMU** — Option B accelerometer backup with zero extra hardware.
- **Small and light** — could potentially clamp to the mast post, though the 1.69" display is smaller than the 2.42" OLED in the Feather build.
- **Color display** — 262K colors at 240x280 is more than enough for a nice UI. Can use color coding (green = on target, red = off target).
- **Cheapest integrated option** — ~$17–22 from Waveshare direct.

### Cons

- **Only 4 free GPIO.** The display, touch, IMU, RTC, and buzzer consume most of the RP2040's pins internally. Only 4 GPIO pads are broken out. This is enough for I2C to the AS5600 (2 pins), but leaves only 2 pins for anything else — no room for physical buttons. Touch-only input.
- **Small display.** 1.69" is actually smaller than the 2.42" SSD1309 OLED you already have. At bench distance while faceting, the color and touch are nice but the digits will be smaller.
- **MicroPython only** — no CircuitPython board definition.
- **RP2040 (not RP2350)** — slower, less RAM. Not a real limitation for this project, but less future headroom.
- **4 MB flash** — tight if you want to store MicroPython + display driver + fonts + calibration data. Doable but not generous.
- **No STEMMA QT / Qwiic** — AS5600 must be hand-wired to the GPIO pads.

### External wiring (AS5600 only)

```
Internal (already on-board):
  ST7789V2 display ── SPI
  CST816T touch    ── I2C (internal)
  QMI8658 IMU      ── I2C (internal)
  PCF85063A RTC    ── I2C (internal)
  Buzzer           ── GPIO (internal)

External (solder to expansion pads):
  AS5600 (addr 0x36):
    SDA → one of the 4 free GPIO pads (confirm pin # from schematic)
    SCL → another free GPIO pad
    VCC → 3V3
    GND → GND

  Remaining: 2 free GPIO pads (available for future use or a physical button if wanted)

LiPo battery → onboard battery header
```

**Critical: confirm the 4 free GPIO pin numbers** from the Waveshare schematic or wiki before ordering. Need to verify at least 2 of them can be assigned to I2C in MicroPython (the RP2040 is flexible — any GPIO can be I2C, but the pads might not be adjacent or convenient).

### Firmware approach (MicroPython)

1. **Display:** Use Waveshare's provided ST7789V2 driver. Smaller canvas (240x280) but still color.
2. **Touch:** CST816T driver (Waveshare provides). Simple tap/swipe gestures for tare, target entry, settings.
3. **AS5600:** Same raw I2C code, on whichever I2C bus the free GPIO pins support:
   ```python
   from machine import I2C, Pin
   i2c_ext = I2C(1, sda=Pin(XX), scl=Pin(XX), freq=400000)
   ```
4. **Buzzer:** Already on-board, just toggle the buzzer GPIO pin from MicroPython.
5. **IMU:** Read QMI8658 for tilt backup.

### UI layout (240x280)

Tighter than the 3.5" but still workable as a color display:

```
┌─────────────────────┐
│                     │
│      4 3 . 2 °      │  ← main angle, large
│                     │
│  ─────────────────  │
│  Target: 43.0°      │
│  ▲ 0.2°             │  ← directional hint
│                     │
│  [TARE]    [SET]    │  ← touch buttons
│                     │
│  Mag:OK  Bat:87%    │  ← status
└─────────────────────┘
```

### Enclosure

- Very compact board — possibly small enough to clamp to the mast post directly.
- Needs a window for the display and access for touch.
- USB-C and battery header accessible.
- Wire runs from the GPIO pads to the AS5600 sensor bracket (12–15 inches).

---

## Comparison: all build options

| | Feather + OLED (todo-hall.md) | RP2350-LCD-3.5 (Option 1) | RP2040-LCD-1.69 (Option 2) | Touch Display (todo-display.md) |
|---|---|---|---|---|
| MCU | RP2350 | RP2350B | RP2040 | RP2350B |
| Display | 2.42" OLED mono | 3.5" IPS color touch | 1.69" IPS color touch | 3.5" IPS color touch |
| Touch | no (2 buttons) | yes | yes | yes |
| Buzzer | external piezo | speaker via codec | onboard | speaker via codec |
| IMU backup | no | yes (QMI8658) | yes (QMI8658) | yes (QMI8658) |
| Battery | yes (Feather) | yes (onboard) | yes (onboard) | yes (onboard) |
| Free GPIO | many | 22 | **4 (tight)** | 22 |
| Firmware | CircuitPython | MicroPython | MicroPython | MicroPython |
| Parts count | 6 external | 2 (AS5600 + magnet) | 2 (AS5600 + magnet) | 2 (AS5600 + magnet) |
| Total cost | ~$30–37 | ~$35–40 | ~$25–32 | ~$40–50 |
| Enclosure | small (mast clamp) | large (tabletop) | small (mast clamp?) | large (tabletop) |
| Complexity | low | medium-high | medium | medium-high |
| Best for | simplest build, CircuitPython | best UI/display, most expandable | most compact all-in-one | same as Option 1 |

---

## Parts list (shared by both options)

### From Adafruit

| # | Part | Part # | Approx. | Notes |
|---|---|---|---|---|
| 1 | AS5600 breakout (STEMMA QT) | #6357 | $5.95 | hall sensor, I2C addr 0x36 |
| 2 | 6mm x 3mm diametrically-magnetized magnet | add-on with #6357 | $2.50 | MUST be diametrically magnetized |

### Board-specific

| Option | Board | Source | Approx. |
|---|---|---|---|
| 1 | RP2350-Touch-LCD-3.5 | Waveshare / Amazon | ~$25–30 |
| 2 | RP2040-Touch-LCD-1.69 | Waveshare / Amazon | ~$17–22 |

### Already have

| Part | Notes |
|---|---|
| PETG filament | enclosures |
| Bambu Labs P1S | printing |
| Cyanoacrylate / UV adhesive | magnet bonding |
| Diametrically magnetized magnets | ordered for Feather build |

### No longer needed (vs Feather build)

| Part | Why |
|---|---|
| Feather RP2350 | Waveshare board replaces it |
| SSD1309 2.42" OLED | integrated display |
| Tactile buttons | touch screen replaces them |
| Piezo buzzer | onboard buzzer (1.69") or speaker codec (3.5") |
| LiPo battery | still needed but plugs into the Waveshare board's header |

---

## Magnet + sensor bracket

Identical to `todo-hall.md` — magnet glues to the exposed pivot axle end, AS5600 mounts on a printed bracket attached to the fixed arm, 1–2 mm air gap. No changes from the Feather build.

---

## Tasks (either option)

### Pre-machine

- [ ] Order chosen Waveshare board (if not already on hand)
- [ ] AS5600 + magnet already ordered for Feather build
- [ ] Flash MicroPython, run Waveshare display + touch demos
- [ ] Identify free I2C GPIO pins from schematic/wiki
- [ ] Solder wires to free GPIO pads for AS5600 I2C
- [ ] Confirm AS5600 responds at 0x36 on external I2C bus
- [ ] Read angle while waving magnet, display on screen
- [ ] Build basic touch UI: large angle display + tare touch button
- [ ] Add filtering, tare logic, target angle entry screen
- [ ] Test onboard buzzer (1.69") or speaker (3.5") for target alert

### Machine-in-hand

- [ ] Measure pivot axle end diameter (for magnet jig)
- [ ] Measure fixed arm dimensions (for sensor bracket)
- [ ] Measure mast post diameter (for clamp) or decide on tabletop stand (3.5" option)
- [ ] Glue magnet, mount AS5600, verify status
- [ ] Print sensor bracket + enclosure
- [ ] Tare against protractor, verify ≤0.5° across 0–90°
- [ ] First cutting session

---

## Questions

1. **Which option appeals more?** Option 1 (3.5" big screen, tabletop stand) gives the best UI. Option 2 (1.69" compact) is the smallest, most self-contained build with the fewest external parts. Both are MicroPython.
2. **Have you used MicroPython before?** It's similar to CircuitPython but not identical — different library ecosystem, different file structure, slightly different I2C API. If you're comfortable with Python in general, the transition is straightforward.
3. **Are these boards already on hand, or would you order them?** If ordering, the 1.69" is cheaper. If this is a future upgrade from the Feather build, either works — the AS5600 + magnet + sensor bracket are the same across all builds.
4. **For the 1.69" option: are 4 free GPIO enough?** You get I2C for the AS5600 (2 pins) and 2 pins left over. No room for physical buttons — touch-only. Is that OK, or do you want a physical tare button as a tactile backup?
