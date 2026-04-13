# Angle Finder — TODO (Accelerometer Build — Superseded)

> **Archived:** This was the original accelerometer-based (LSM6DS3TR-C) build plan.
> Superseded by the hall sensor (AS5600) build in the main `todo.md`.

## GitHub Project Setup

**Suggested repo names** (pick one):

- `facet-angle-finder`
- `mast-angle-finder`
- `gemcutter-angle`

### Create the repo and push

```bash
# 1. Initialize git in this directory
cd /Users/acchapm1/tools/acc-2ndbrain/faceting/anglefinder
git init

# 2. Create the GitHub repo (public, with description)
gh repo create facet-angle-finder \
  --public \
  --description "Digital angle finder for gem faceting machines — CircuitPython on XIAO RP2040 + LSM6DSOX accelerometer" \
  --source . \
  --remote origin

# 3. Stage and commit
git add concept.md plan.md todo.md img/
git commit -m "Initial project docs: concept, plan, todo, reference images"

# 4. Push
git push -u origin main
```

### Recommended repo structure (after firmware work begins)

```
facet-angle-finder/
  README.md               # project overview, photos, wiring diagram
  concept.md              # original idea and questions
  plan.md                 # full implementation plan
  todo.md                 # this file
  LICENSE                 # MIT or your preference
  img/                    # reference photos
  firmware/
    code.py               # main CircuitPython entry point
    lib/                   # vendored CircuitPython libraries
    boot.py               # optional: filesystem config for NVM writes
  hardware/
    wiring-diagram.png    # fritzing or hand-drawn
    bom.md                # bill of materials (also below)
  enclosure/
    sensor-clamp.step     # split-clamp for handpiece body
    display-box.step      # mast-mounted display housing
    sensor-clamp.3mf      # print-ready sliced file
    display-box.3mf       # print-ready sliced file
```

---

## Getting back to this project

When the machine arrives and parts are in hand, open a Claude Code session in this directory:

```bash
cd /Users/acchapm1/tools/acc-2ndbrain/faceting/anglefinder
claude
```

Claude will automatically load the project memory and know:
- What this project is
- What decisions have been made
- What measurements are still needed
- Where you left off

Just say: **"The machine arrived, ready to continue the angle finder build"** and provide the two caliper measurements (handpiece body diameter and mast post diameter).

---

## Parts List

### Order now

| # | Part | Source | Part # | Approx. | Notes |
|---|---|---|---|---|---|
| 1 | LSM6DS3TR-C 6-DoF IMU breakout | Adafruit | #4503 | $12 | accelerometer + gyro, STEMMA QT, I2C addr 0x6A (LSM6DSOX out of stock, same family) |
| 2 | 1.3" 128x64 OLED SSD1306 (generic) | Amazon | — | $3–5 | I2C, addr 0x3C or 0x3D, 4-pin (VCC/GND/SCL/SDA), solder wires |
| 3 | STEMMA QT / Qwiic cable, 100mm (x1) | Adafruit | #4210 | $1 | sensor-to-MCU only (OLED is hand-wired) |
| 4 | Momentary tactile buttons (x2) | generic | — | $1 | 6mm through-hole, for tare + menu |
| 5 | Piezo buzzer, passive, 3.3V compatible | generic | — | $1 | for target-angle alert |
| 6 | M3x8 socket head screws (x4) | generic | — | $2 | for split-clamp assembly |
| 7 | M3 heat-set inserts (x4) | generic | — | $1 | press into PETG clamp halves |
| 8 | 4-pin JST-SH cable, 300mm | Adafruit / generic | — | $2 | sensor head to display box (or use longer STEMMA QT) |

**Total: ~$20–25**

### Already have

| Part | Notes |
|---|---|
| Seeed Studio XIAO RP2040 | MCU, CircuitPython, USB-C power |
| PETG filament | for 3D-printed enclosures on P1S |
| Bambu Labs P1S | for printing enclosures |

### Optional / future

| Part | When | Why |
|---|---|---|
| AS5600 breakout + 6mm diametric magnet | if accelerometer has vibration issues | Option A fallback — rotary encoder on pivot |
| LiPo battery + charger board | v2 | untethered operation |
| XIAO ESP32-C3 | v2 | wireless angle logging / remote display |

---

## Wiring (breadboard prototype)

All components share the I2C bus on the XIAO RP2040.

```
XIAO RP2040 Pinout (relevant pins):
  D4 (SDA) ──── I2C data bus
  D5 (SCL) ──── I2C clock bus
  D0       ──── Tare button (to GND, use internal pullup)
  D1       ──── Menu button (to GND, use internal pullup)
  D2       ──── Piezo buzzer (+)
  3V3      ──── sensor VCC, OLED VCC
  GND      ──── common ground

I2C bus:
  LSM6DS3TR-C  addr 0x6A ─┐  (STEMMA QT cable to MCU)
  OLED         addr 0x3C ─┤── SDA/SCL shared bus
                           └── 3V3 + GND  (OLED hand-wired)
```

### Breadboard hookup

LSM6DS3TR-C uses STEMMA QT to the MCU. OLED is hand-wired. Buttons and buzzer are hand-wired.

```
LSM6DS3TR-C breakout (STEMMA QT to XIAO, or hand-wire):
  VIN  → 3V3
  GND  → GND
  SDA  → D4
  SCL  → D5

OLED breakout:
  VCC  → 3V3
  GND  → GND
  SDA  → D4
  SCL  → D5

Tare button:
  one leg  → D0
  other leg → GND

Menu button:
  one leg  → D1
  other leg → GND

Piezo buzzer:
  (+)  → D2
  (-)  → GND
```

---

## CircuitPython Setup

### Install CircuitPython on the XIAO RP2040

1. Download the latest CircuitPython `.uf2` for the XIAO RP2040 from circuitpython.org
2. Hold the BOOT button on the XIAO, plug in USB — it mounts as `RPI-RP2`
3. Drag the `.uf2` file onto `RPI-RP2` — it reboots and mounts as `CIRCUITPY`

### Required libraries

Download from the Adafruit CircuitPython Bundle (matching your CP version) and copy to `CIRCUITPY/lib/`:

```
lib/
  adafruit_lsm6ds/        # LSM6DSOX driver (folder)
  adafruit_register/       # register abstraction (folder, dependency)
  adafruit_bus_device/     # I2C/SPI helpers (folder, dependency)
  adafruit_displayio_ssd1306.mpy   # if using SSD1306 OLED
  adafruit_framebuf.mpy    # if using framebuffer OLED driver
  adafruit_ssd1306.mpy     # framebuf-based SSD1306 driver (simpler)
```

Or use `circup` to install automatically:

```bash
pip install circup
circup install adafruit_lsm6ds adafruit_ssd1306 adafruit_framebuf adafruit_bus_device adafruit_register
# The adafruit_lsm6ds package includes drivers for LSM6DSOX, LSM6DS3TR-C, and LSM6DS3
# In code.py, use: from adafruit_lsm6ds.lsm6ds3trc import LSM6DS3TRC
```

---

## Pre-machine tasks (do now with parts on the desk)

- [ ] Order parts (see parts list above)
- [ ] Create GitHub repo (see commands above)
- [ ] Install CircuitPython on XIAO RP2040
- [ ] Install CircuitPython libraries
- [ ] Breadboard: I2C scan — confirm sensor (0x6A) and OLED (0x3C) respond
- [ ] Breadboard: read raw accelerometer, print tilt angle to serial console
- [ ] Breadboard: display angle on OLED with large digits
- [ ] Breadboard: add moving-average filter, verify stable readings
- [ ] Breadboard: wire tare button, test offset logic
- [ ] Breadboard: wire buzzer, test tone output
- [ ] Tilt breadboard by hand, compare to phone inclinometer app — should agree within ~1°

## Machine-in-hand tasks (after ~April 22)

- [ ] Measure upper handpiece body diameter with calipers
- [ ] Measure mast post diameter with calipers
- [ ] Confirm cable length (sensor head to display position on mast)
- [ ] Design and print split-clamp sensor head (PETG)
- [ ] Design and print mast-mounted display box (PETG)
- [ ] Install on machine, run cable
- [ ] Tare against protractor at 45°, sweep 0–90° and compare readings
- [ ] Verify ≤0.5° accuracy across full range
- [ ] Add target-angle menu + buzzer alert (firmware)
- [ ] First real cutting session — do facets meet cleanly?
- [ ] Write README.md with photos and build instructions
- [ ] Tag v1.0.0 release on GitHub
