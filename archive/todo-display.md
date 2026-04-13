# Angle Finder — Integrated Touch Display Build

Uses the Waveshare RP2350-Touch-LCD-3.5 as an all-in-one MCU + display, paired with the AS5600 hall sensor on the pivot axle. The big screen and touch input replace the small OLED + physical buttons from the other builds.

## Why this option

- **One board = MCU + display + touch + IMU + battery charging.** No separate OLED, no buttons to wire, no separate MCU board. Dramatically fewer parts and connections.
- **3.5" 320x480 capacitive touch IPS** — large, bright, readable at arm's length while faceting. Far better than the 1.3" OLED.
- **Touch UI** replaces physical buttons — tare, target angle entry, settings, all on-screen. More flexible and easier to extend.
- **Built-in 6-axis IMU (QMI8658)** — could serve as a backup/cross-check for the AS5600, or used for Option B (accelerometer tilt) without any additional hardware.
- **LiPo battery header** — untethered operation from day one, no extra charger board.
- **RP2350B** — dual M33 cores at 150 MHz, 520 KB RAM, 16 MB flash. Massively overpowered for this project, which means headroom for a richer UI.

## Board specs (Waveshare RP2350-Touch-LCD-3.5)

| Spec | Detail |
|---|---|
| MCU | RP2350B, dual Cortex-M33 @ 150 MHz |
| RAM | 520 KB SRAM |
| Flash | 16 MB |
| Display | 3.5" IPS, 320x480, 65K colors, ST7796 driver (SPI) |
| Touch | Capacitive, FT6336 controller (I2C) |
| IMU | QMI8658 6-axis accel + gyro |
| RTC | PCF85063 (with battery backup header) |
| Audio | ES8311 low-power codec |
| Power mgmt | AXP2101 PMIC |
| Battery | 3.7V MX1.25 LiPo header (charge + discharge) |
| USB | USB-C |
| Camera | OV2640/OV5640 interface (unused for this project) |
| TF card | microSD slot |
| Expansion | 22x multi-function GPIO, 2x SPI, 2x I2C, 2x UART, 7x ADC, 18x PWM |
| Price | ~$25–30 (Waveshare store / Amazon) |

Source: https://docs.waveshare.com/RP2350-Touch-LCD-3.5

## Complexity assessment — honest take

This is a **medium complexity upgrade** from the Feather + OLED build. Here's what gets harder and what gets easier:

### What gets easier

- **Fewer parts.** No OLED, no buttons, no buzzer wiring, no separate MCU board. Just the Waveshare board + AS5600 + magnet.
- **Better UI.** Touch screen means you can build a real interface — big angle display, touch-to-set-target, calibration wizard, settings screen. No more squinting at 128x64 pixels.
- **Battery built in.** Just plug in a LiPo.

### What gets harder

- **Display driver.** The ST7796 over SPI is a color LCD, not a simple framebuffer OLED. In CircuitPython you'd use `displayio` with a custom init sequence. In MicroPython (more likely — see below), you'd use a `st7796` driver with framebuffer writes. Either way, it's more code than `ssd1306.text()`.
- **Touch input.** The FT6336 touch controller is I2C-based and straightforward to read (x, y, touch count), but you need to write the UI logic for buttons, sliders, etc. — no free lunch here.
- **CircuitPython support is uncertain.** There is no official CircuitPython board definition for the RP2350-Touch-LCD-3.5 as of now. The smaller Waveshare boards (1.28", LCD-0.96) have CircuitPython support, but this one may not yet. **MicroPython is the safer bet** — Waveshare provides MicroPython examples for this board.
- **Pin allocation.** The display (SPI) and touch (I2C) consume some GPIO. You need to verify that at least one I2C bus and 1–2 GPIO pins are free on the expansion header for the AS5600 and (optionally) a piezo buzzer. The board has 22 GPIO broken out, so this should be fine, but you'll need to check the schematic to confirm which specific pins are available.
- **Enclosure is larger.** The board is physically bigger than a Feather — the display box on the mast needs to accommodate a 3.5" screen.

### CircuitPython vs MicroPython

| | CircuitPython | MicroPython |
|---|---|---|
| Board support | not yet for this board | yes, Waveshare provides examples |
| Display driver | `displayio` + ST7796 init sequence (community) | `st7796` driver (Waveshare provides) |
| Touch driver | `adafruit_focaltouch` (FT6336 compatible) | Waveshare provides FT6336 driver |
| AS5600 driver | raw I2C (same code as todo-hall.md) | raw I2C (same code, minor syntax diff) |
| Ecosystem | Adafruit libraries, `circup` | less structured, but more raw hardware access |

**Recommendation: start with MicroPython** using Waveshare's provided examples to get the display and touch working, then port to CircuitPython later if a board definition becomes available. The AS5600 I2C code is nearly identical between the two — it's just register reads.

If CircuitPython is a hard requirement, consider the Feather RP2350 + separate display approach instead (see alternative section at the bottom).

## Parts list

### Order

| # | Part | Source | Part # | Approx. | Notes |
|---|---|---|---|---|---|
| 1 | Waveshare RP2350-Touch-LCD-3.5 | Waveshare / Amazon | SKU 33894 | ~$25–30 | MCU + display + touch + IMU + battery charging, all-in-one |
| 2 | AS5600 breakout (STEMMA QT) | Adafruit | #6357 | $5.95 | hall sensor, I2C addr 0x36 |
| 3 | 6mm x 3mm diametrically-magnetized magnet | Adafruit (add-on) | — | $2.50 | MUST be diametrically magnetized |
| 4 | 4-wire cable, ~400mm | generic or STEMMA QT | — | $1–2 | AS5600 to Waveshare board (I2C + power) |
| 5 | 3.7V LiPo battery (500–1000mAh) | Adafruit / Amazon | — | $5–8 | MX1.25 connector, for untethered operation |
| 6 | M3 screws / heat-set inserts (x4) | generic | — | $3 | sensor bracket + display housing |

### Already have

| Part | Notes |
|---|---|
| PETG filament | for 3D-printed enclosures on P1S |
| Bambu Labs P1S | for printing |
| Cyanoacrylate / UV adhesive | magnet bonding |

### No longer needed (compared to Feather build)

| Part | Why |
|---|---|
| Feather RP2350 | Waveshare board replaces it |
| SSD1306 OLED | 3.5" LCD is the display |
| Tactile buttons (x2) | touch screen replaces them |
| Piezo buzzer | board has audio codec — can drive a small speaker, or use a buzzer on a GPIO pin |

### Total new spend

~$40–50 (vs ~$28–33 for the Feather build). The premium buys you the big touch screen and fewer parts.

## Wiring

Much simpler than the other builds — just the AS5600 connects externally.

```
Waveshare RP2350-Touch-LCD-3.5:
  Internal (already wired on-board):
    ST7796 display ── SPI
    FT6336 touch   ── I2C (internal bus)
    QMI8658 IMU    ── I2C (internal bus)
    PCF85063 RTC   ── I2C (internal bus)
    AXP2101 PMIC   ── I2C (internal bus)
    ES8311 audio   ── I2C (internal bus)

  External (you wire):
    AS5600 breakout ── I2C (expansion header or second I2C bus)
      SDA → available GPIO on expansion header
      SCL → available GPIO on expansion header
      VCC → 3V3
      GND → GND

    Optional piezo buzzer:
      (+) → available GPIO pin
      (-) → GND

    LiPo battery:
      plug into MX1.25 battery header (built in)
```

### I2C bus consideration

The board's internal peripherals (touch, IMU, RTC, PMIC, audio) likely share one I2C bus. The RP2350 has two hardware I2C controllers, so the AS5600 can go on the second I2C bus using two free GPIO pins configured as I2C1. This avoids any address conflicts and keeps the external sensor isolated from the internal bus.

**Needs confirmation:** check the schematic or expansion header pinout to identify which GPIO pins are broken out and available for I2C1. This is the one thing that must be verified before committing to this board.

## Magnet mounting

Identical to `todo-hall.md` — see that file for the full magnet section. Summary:

1. 6mm diametrically-magnetized magnet glued centered on the exposed pivot axle end
2. AS5600 breakout mounted on a printed bracket attached to the fixed arm
3. 1–2 mm air gap between magnet and sensor IC

## Firmware plan (MicroPython)

### 1. Bring-up

- Flash MicroPython (Waveshare provides a .uf2 or .bin)
- Run Waveshare's display demo — confirm screen works
- Run Waveshare's touch demo — confirm touch input works
- I2C scan on the expansion bus — confirm AS5600 at 0x36
- Read AS5600 angle, print to console

### 2. Display layout

The 320x480 resolution gives plenty of room:

```
┌────────────────────────────┐
│                            │
│        4 3 . 2 °           │  ← main angle, large font (~80px)
│                            │
│  ──────────────────────── │
│                            │
│   Target: 43.0°   [SET]    │  ← target angle + touch button
│                            │
│   ▲ 0.2°  (raise)         │  ← directional hint when near target
│                            │
│  ┌──────┐  ┌──────┐       │
│  │ TARE │  │ HOLD │       │  ← touch buttons
│  └──────┘  └──────┘       │
│                            │
│  Magnet: OK  │  Batt: 87% │  ← status bar
└────────────────────────────┘
```

### 3. Touch UI

- **TARE button:** touch to tare against the machine's protractor at current angle. Prompt for the reference angle (on-screen number pad or +/- buttons).
- **SET button:** enter target angle via on-screen number input.
- **HOLD button:** freeze the display reading.
- **Settings gear icon:** calibration, display brightness, buzzer on/off.

### 4. AS5600 driver

Same raw I2C code as `todo-hall.md`, adapted for MicroPython syntax:

```python
from machine import I2C, Pin

_AS5600_ADDR = 0x36
_RAW_ANGLE_HI = 0x0C

# Use the second I2C bus on available expansion GPIO
i2c = I2C(1, sda=Pin(XX), scl=Pin(XX), freq=400000)  # XX = confirm from pinout

def read_angle():
    data = i2c.readfrom_mem(_AS5600_ADDR, _RAW_ANGLE_HI, 2)
    raw = ((data[0] & 0x0F) << 8) | data[1]
    return raw * 360.0 / 4096.0

def read_status():
    data = i2c.readfrom_mem(_AS5600_ADDR, 0x0B, 1)
    status = data[0]
    return {
        'detected': bool(status & 0x20),
        'too_strong': bool(status & 0x08),
        'too_weak': bool(status & 0x10)
    }
```

### 5. Filtering

Same IIR / moving-average as the other builds. 10–20 sample window, α ≈ 0.1.

### 6. Tare / zero

Same logic: `offset = known_angle - raw_degrees`, persist to flash file.

Touch UI makes this nicer — prompt "Set handpiece to __ degrees on protractor" with a number pad.

### 7. Target angle alert

- On-screen: big green/red color change when within ±0.2° of target, directional arrows when close.
- Audio: the ES8311 codec can drive a small speaker for a beep, or just wire a piezo to a free GPIO.
- Visual: flash/invert the screen colors briefly.

### 8. Bonus: built-in IMU as backup

The QMI8658 IMU on the board could serve as an Option B accelerometer backup — read tilt from gravity, compare to the AS5600 reading. Useful for:
- Cross-checking the hall sensor during calibration
- Falling back to accelerometer mode if the magnet fails
- No extra hardware needed, it's already on the board

## Mechanical plan (P1S printed parts)

### Part 1: Sensor bracket

Same design as `todo-hall.md` — printed bracket mounts AS5600 to the fixed arm over the magnet.

### Part 2: Display enclosure

This is the bigger design challenge vs the other builds:

- The display is 3.5" — the enclosure is significantly larger than the small OLED box.
- Needs a window for the screen and an open area for touch input.
- Mount to the mast post via a clamp, or sit on the table near the machine with a stand.
- USB-C port accessible for charging / power.
- Battery compartment inside for the LiPo.
- Cable exit for the I2C wire to the AS5600 sensor bracket.
- Consider a tilting mount so you can angle the screen toward your eyes.

**Rough dimensions:** ~100mm x 65mm x 20mm (just the board + case walls). With a mast clamp, it might be too heavy/bulky to hang off the mast post — a **tabletop stand** with a short cable to the sensor bracket may be more practical.

### Part 3: Magnet alignment jig

Same as `todo-hall.md` — optional printed centering sleeve for the magnet.

## Tasks

### Pre-machine (do now at the desk)

- [ ] Order Waveshare RP2350-Touch-LCD-3.5 + LiPo battery
- [ ] Order AS5600 (#6357) + magnet add-on from Adafruit
- [ ] Flash MicroPython, run Waveshare display + touch demos
- [ ] Identify free I2C pins on expansion header (check schematic/wiki)
- [ ] Wire AS5600 to expansion I2C, confirm 0x36 responds
- [ ] Read AS5600 angle while waving magnet — confirm values change on screen
- [ ] Build basic UI: large angle display + tare touch button
- [ ] Test built-in QMI8658 IMU — read tilt angle, compare to AS5600 with magnet
- [ ] Add filtering, tare logic, target angle entry screen
- [ ] Add visual alert (color change) when target angle is reached

### Machine-in-hand (after delivery)

- [ ] Measure pivot axle end diameter (for magnet centering jig)
- [ ] Measure fixed arm dimensions (for sensor bracket)
- [ ] Measure mast post diameter (for clamp or decide on tabletop stand)
- [ ] Glue magnet, mount AS5600, check status
- [ ] Print sensor bracket, mount on fixed arm
- [ ] Print display enclosure (mast-mount or tabletop stand)
- [ ] Run cable from sensor bracket to display
- [ ] Tare against protractor at 45°, sweep 0–90°, verify ≤0.5°
- [ ] First real cutting session
- [ ] Update GitHub repo

## Comparison: all three build options

| | Option B (todo.md) | Option A Feather (todo-hall.md) | Option A Display (this file) |
|---|---|---|---|
| MCU | XIAO RP2040 | Feather RP2350 | Waveshare RP2350-Touch-LCD-3.5 |
| Sensor | LSM6DS3TR-C (accel) | AS5600 (hall) | AS5600 (hall) + QMI8658 backup |
| Display | 1.3" SSD1306 OLED | 1.3" SSD1306 OLED | 3.5" IPS touch LCD (built in) |
| Input | 2 physical buttons | 2 physical buttons | capacitive touch screen |
| Battery | no (USB only) | future (add charger) | yes (built-in LiPo header) |
| Firmware | CircuitPython | CircuitPython | MicroPython (likely) |
| Parts count | 8 | 6 | 3 (board + AS5600 + magnet) |
| Total cost | ~$20–25 | ~$28–33 | ~$40–50 |
| Enclosure size | small | small | larger (3.5" screen) |
| Complexity | low | low | medium |
| Wow factor | functional | functional | polished product |

---

## Questions

1. **MicroPython OK?** CircuitPython may not have a board definition for this Waveshare board yet. MicroPython is supported with Waveshare-provided examples. Is switching from CircuitPython to MicroPython a dealbreaker, or are you OK with it? (The AS5600 code is nearly identical either way.)
2. **Mounting: mast clamp or tabletop stand?** The 3.5" display enclosure is bigger and heavier than the OLED box. Clamping it to the mast post may be awkward. A small tabletop stand next to the machine with a wire running to the sensor bracket might work better. What's your preference?
3. **Speaker or piezo?** The board has an ES8311 audio codec that can drive a small speaker. Want actual audio feedback (beep tones through a speaker), or is a simple piezo on a GPIO pin fine?
4. **Are you leaning toward this build, or weighing all three options?** This is the most polished end product but costs more and uses MicroPython. The Feather build (`todo-hall.md`) is simpler and stays on CircuitPython.
