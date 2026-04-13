# Angle Finder — Hall Sensor Build (Option A)

Uses an AS5600 magnetic rotary encoder on the handpiece tilt axle instead of an accelerometer. The magnet glues to the exposed end of the pivot axle; the sensor PCB mounts to the fixed arm that the axle rotates in.

## Why this option

- Measures the actual pivot angle directly — no gravity dependence, no vibration sensitivity
- Rock-solid repeatability — the magnet-to-sensor geometry is fixed
- Works regardless of whether the machine is level
- The AS5600 is cheap (~$3–5), I2C, 12-bit (0.088° resolution), and well within 0.5° accuracy
- Exposed axle end + fixed arm means no machining — just glue + a printed bracket

## Parts list

### Order from Adafruit

| # | Part | Part # | Approx. | Notes |
|---|---|---|---|---|
| 1 | Feather RP2350 (no PSRAM) | #6000 | $12.50 | MCU, STEMMA QT built in, LiPo charger, CircuitPython |
| 2 | AS5600 breakout (STEMMA QT) | #6357 | $5.95 | I2C, addr 0x36, STEMMA QT connectors |
| 3 | 6mm x 3mm diametrically-magnetized neodymium magnet | add-on with #6357 | $2.50 | MUST be diametrically magnetized — see magnet section below |
| 4 | STEMMA QT / Qwiic cable, 400mm (x1) | #5385 or similar | $1.50 | AS5600 on pivot to Feather in display box (12–15" run, get 400mm) |

### Order from Amazon / generic

| # | Part | Approx. | Notes |
|---|---|---|---|
| 5 | 3.7V LiPo battery, 1000mAh, JST PH 2-pin | $8–10 | plugs into Feather battery header, ~18 hrs runtime, ~50x30x6mm |
| ~~6~~ | ~~1.3" SSD1306 OLED~~ | ~~$3–5~~ | ~~replaced by 2.42" SSD1309 already on hand~~ |
| 7 | Momentary tactile buttons (x2) | $1 | 6mm through-hole, tare + menu |
| 8 | Piezo buzzer, passive, 3.3V | $1 | target-angle alert |
| 9 | M3x8 socket head screws (x4) | $2 | sensor bracket + display box assembly |
| 10 | M3 heat-set inserts (x4) | $1 | press into PETG printed parts |

### Already have

| Part | Notes |
|---|---|
| 2.42" SSD1309 128x64 OLED (HiLetgo, 4-pin I2C) | display, 71x43mm board, I2C addr 0x3C, SSD1306-compatible driver |
| XIAO RP2040 | kept as spare — not used in this build |
| PETG filament | for 3D-printed enclosures on P1S |
| Bambu Labs P1S | for printing enclosures |
| Cyanoacrylate (superglue) or UV-cure adhesive | to bond magnet to axle end |

### Optional / future

| Part | When | Why |
|---|---|---|
| XIAO ESP32-C3 | v2 | wireless angle logging / remote display |
| LSM6DS3TR-C | if already ordered | can use as Option B fallback or different project, addr 0x6A doesn't conflict |

### Power budget

| Component | Draw | Notes |
|---|---|---|
| Feather RP2350 (active) | ~30 mA | M33 cores running, I2C polling |
| AS5600 | ~6 mA | continuous measurement |
| SSD1309 2.42" OLED | ~20–30 mA | larger panel draws slightly more than 1.3"; depends on pixel fill |
| **Total steady state** | **~55–65 mA** | |

With a 1000 mAh battery: **~15–18 hours runtime.** Charges in ~5 hours over USB-C (Feather charges at 200 mA). Comfortably past the 10-hour target.

### Total new spend

~$30–37 (Adafruit parts + battery + generic parts + shipping). Saved $3–5 by using the OLED already on hand.

**Does NOT need:** LSM6DS3TR-C, STEMMA QT adapter for MCU (Feather has it built in).

---

## Magnet mounting

### Critical: diametrically magnetized

```
CORRECT — diametrically magnetized     WRONG — axially magnetized
(poles on sides, field rotates          (poles on faces, field does
 with the axle)                          not rotate with the axle)

     ┌─────┐                                ┌─────┐
     │ N S │  ← poles left/right            │  N  │  ← pole on top
     │     │                                │     │
     │ S N │                                │  S  │  ← pole on bottom
     └─────┘                                └─────┘
```

The AS5600 reads the angle of the magnetic field vector in a plane perpendicular to the IC. If the magnet is axially magnetized, the field doesn't change as the axle rotates — no angle signal.

### Mounting steps

1. Clean the exposed end of the pivot axle with isopropyl alcohol.
2. Center the 6mm diametric magnet on the axle end. The magnet center should align with the axle center within ~1 mm. At 0.5° accuracy this tolerance is generous.
3. Glue in place with superglue or UV adhesive. Let cure fully before handling.
4. The magnet's north-south axis orientation relative to the handpiece doesn't matter — you'll tare it out in firmware.

### Air gap

The AS5600 datasheet specifies a 0.5–3 mm air gap between the magnet top face and the sensor IC. The sensor PCB needs to sit parallel to the magnet face, centered over it. The printed bracket positions this.

---

## Sensor bracket

A small 3D-printed bracket that mounts the AS5600 breakout PCB to the fixed arm of the mast assembly, positioned over the magnet on the axle end.

### Design requirements

- Attaches to the fixed arm (the silver bracket piece clamped to the mast post) — needs a clamp, set screw, or adhesive mounting depending on the arm geometry.
- Holds the AS5600 breakout centered over the axle end, parallel to the magnet face.
- Adjustable air gap — either a slot + screw for vertical adjustment, or print several versions with different offsets (1mm, 1.5mm, 2mm).
- PETG for moisture resistance near coolant.
- Small and light — the bracket must not interfere with the handpiece swing arc (0–90°).
- Cable routing: 4 wires (VCC, GND, SDA, SCL) run from the bracket down to the display box on the mast.

### Bracket orientation

The AS5600 IC is on one side of the breakout PCB. The bracket positions the PCB so the IC faces the magnet. Check your specific breakout — most have the IC on the top side with a small circle marking.

---

## Wiring

The Feather RP2350 has a built-in STEMMA QT connector, so the AS5600 plugs in with a single cable. The OLED is hand-wired to the same I2C bus. Buttons and buzzer go to GPIO pins on the Feather header.

```
Feather RP2350 (#6000) Pinout (relevant pins):
  STEMMA QT ── I2C bus (SDA/SCL/3V3/GND) ── AS5600 via cable
  SDA        ── also broken out on header (for hand-wiring OLED)
  SCL        ── also broken out on header (for hand-wiring OLED)
  D5         ── Tare button (to GND, use internal pullup)
  D6         ── Menu button (to GND, use internal pullup)
  D9         ── Piezo buzzer (+)
  3V3        ── OLED VCC
  GND        ── common ground

I2C bus (shared):
  AS5600    addr 0x36 ─┐  (STEMMA QT cable, no soldering)
  OLED      addr 0x3C ─┤── SDA/SCL shared bus
                        └── 3V3 + GND  (OLED hand-wired to header)
```

### Wiring detail

```
AS5600 breakout (Adafruit #6357):
  STEMMA QT cable from AS5600 → Feather STEMMA QT port (I2C + power, done)
  DIR pin → solder jumper to GND on breakout (sets CW increasing)
  OUT pin → leave unconnected (analog/PWM output, not used)

OLED (2.42" SSD1309, 4-pin I2C, hand-wired):
  VCC  → 3V3 on Feather header
  GND  → GND on Feather header
  SDA  → SDA on Feather header
  SCL  → SCL on Feather header

Tare button:
  one leg  → D5
  other leg → GND

Menu button:
  one leg  → D6
  other leg → GND

Piezo buzzer:
  (+)  → D9
  (-)  → GND

LiPo battery (1000mAh, JST PH 2-pin):
  Plug into Feather JST battery connector — runs untethered, charges via USB-C automatically
```

---

## CircuitPython setup

### Install CircuitPython

1. Download the latest CircuitPython `.uf2` for the **Feather RP2350** from circuitpython.org
2. Hold the BOOT button on the Feather, plug in USB-C — it mounts as `RPI-RP2`
3. Drag the `.uf2` file onto `RPI-RP2` — it reboots and mounts as `CIRCUITPY`

### Required libraries

Copy to `CIRCUITPY/lib/`:

```
lib/
  adafruit_bus_device/     # I2C helpers (folder, dependency)
  adafruit_ssd1306.mpy     # OLED driver
  adafruit_framebuf.mpy    # framebuffer dependency for ssd1306
```

Or via circup:

```bash
circup install adafruit_ssd1306 adafruit_framebuf adafruit_bus_device
```

**Note:** There is no official Adafruit CircuitPython driver for the AS5600. The AS5600 is simple enough to drive with raw I2C reads — it's just two register reads to get a 12-bit angle. The firmware section below includes the code.

### AS5600 raw I2C driver (goes in code.py or a helper)

```python
# AS5600 registers
_AS5600_ADDR = 0x36
_RAW_ANGLE_HI = 0x0C  # bits 11:8
_RAW_ANGLE_LO = 0x0D  # bits 7:0
_STATUS = 0x0B
_AGC = 0x1A
_MAGNITUDE_HI = 0x1B
_MAGNITUDE_LO = 0x1C

def read_as5600_angle(i2c):
    """Read raw angle from AS5600. Returns 0-4095 (0-360 degrees)."""
    buf = bytearray(2)
    i2c.writeto_then_readfrom(_AS5600_ADDR, bytes([_RAW_ANGLE_HI]), buf)
    raw = ((buf[0] & 0x0F) << 8) | buf[1]
    return raw

def as5600_degrees(i2c):
    """Read angle in degrees (0.0 - 359.9)."""
    raw = read_as5600_angle(i2c)
    return raw * 360.0 / 4096.0

def as5600_status(i2c):
    """Check magnet status. Returns (detected, too_strong, too_weak)."""
    buf = bytearray(1)
    i2c.writeto_then_readfrom(_AS5600_ADDR, bytes([_STATUS]), buf)
    status = buf[0]
    detected = bool(status & 0x20)
    too_strong = bool(status & 0x08)
    too_weak = bool(status & 0x10)
    return detected, too_strong, too_weak
```

---

## Firmware plan

Same structure as Option B, with the sensor driver swapped out.

1. **Bring-up**
   - I2C scan — confirm AS5600 at 0x36 and OLED at 0x3C.
   - Read `as5600_status()` — verify magnet detected, not too strong/weak. Display status on serial. If magnet not detected, check air gap and magnet orientation.
   - Read raw angle, print to serial while slowly tilting the handpiece. Confirm the value changes smoothly over the full 0–90° range.

2. **Angle mapping**
   - The AS5600 reports 0–4095 over a full 360° rotation. You'll only use ~25% of that range (0–90° tilt).
   - Convert: `angle_deg = raw * 360.0 / 4096.0`
   - The zero point depends on how the magnet is oriented when glued — tare handles this.

3. **Filtering**
   - Same IIR or moving-average filter as Option B, though the AS5600 is inherently less noisy than an accelerometer so you can use lighter filtering (10–20 samples or α ≈ 0.1).

4. **Tare / zero**
   - Same as Option B: set handpiece to a known angle on the protractor, press tare.
   - `offset = known_angle - current_raw_degrees`
   - `displayed = current_raw_degrees + offset`
   - Persist to `microcontroller.nvm` or JSON on CIRCUITPY.

5. **Display**
   - Same layout: large `XX.X°` on top, status line on bottom.
   - Add a magnet-status indicator on the status line (good/weak/strong) — the AS5600 reports this for free. Useful during initial setup.

6. **Target angle + buzzer**
   - Identical to Option B firmware — same button logic, same flash/beep behavior.

7. **Serial output**
   - Same optional USB CDC stream for debugging/logging.

---

## Mechanical plan (P1S printed parts)

### Part 1: Sensor bracket (new for Option A)

Mounts the AS5600 breakout to the fixed arm, centered over the magnet on the axle end.

- Attaches to the fixed arm via a small clamp or set screw.
- Holds the AS5600 PCB at 1–2 mm air gap above the magnet.
- Needs a slot or adjustable mount for dialing in the gap.
- STEMMA QT cable routes from the AS5600 down to the Feather in the display box.
- Keep it small — must not block the handpiece 0–90° arc.
- PETG, thin walls are fine since there's no mechanical load.

### Part 2: Display box

Clamps to the mast vertical post. Houses Feather RP2350, OLED, buttons, buzzer, and LiPo battery.

- OLED board is 71x43mm — this is the largest component and sets the box size. Internal box roughly 80x50x25mm.
- Feather (51x23mm) and LiPo (~50x30x6mm) stack behind the OLED.
- OLED window in the front face, buttons accessible on top or side. The 2.42" display gives big, readable digits.
- STEMMA QT cable exits toward the pivot area (12–15 inches to sensor bracket).
- USB-C port accessible for charging. When plugged in, the Feather runs from USB and charges the battery simultaneously.
- Battery sits behind or below the Feather, secured with a small shelf/lip in the printed enclosure.
- Cable length: 12–15 inches (your measurement).

### Part 3: Magnet alignment jig (optional, nice-to-have)

A small disposable printed sleeve that slips over the axle end and centers the 6mm magnet while the glue cures. Ensures the magnet is concentric with the axle. Peel off after curing.

---

## Tasks

### Pre-machine (do now at the desk)

- [x] Order Feather RP2350 (#6000), AS5600 (#6357) + magnet add-on, STEMMA QT cable from Adafruit
- [x] Order LiPo battery, buttons, buzzer, magnets from Amazon
- [x] Have 2.42" SSD1309 OLED on hand (from parts drawer)
- [ ] Install CircuitPython on Feather RP2350
- [ ] Install libraries (`adafruit_ssd1306`, `adafruit_framebuf`, `adafruit_bus_device`)
- [ ] Write AS5600 I2C driver (code above, or test on breadboard with magnet taped nearby)
- [ ] Breadboard: plug AS5600 into Feather via STEMMA QT, I2C scan, confirm 0x36 and OLED at 0x3C
- [ ] Breadboard: read angle while waving a diametric magnet near the sensor — confirm values change
- [ ] Breadboard: display angle on OLED with large digits
- [ ] Breadboard: add filter, tare button, buzzer

### Machine-in-hand (after delivery)

- [ ] Measure pivot axle end diameter with calipers (for magnet alignment jig)
- [ ] Measure fixed arm dimensions (for sensor bracket design)
- [ ] Measure mast post diameter (for display box clamp)
- [ ] Glue diametric magnet centered on axle end, let cure
- [ ] Check `as5600_status()` — confirm magnet detected, strength OK
- [ ] Print sensor bracket, mount AS5600 over magnet on fixed arm
- [ ] Adjust air gap — aim for 1–2 mm, check AGC register for optimal signal
- [ ] Print display box, mount on mast post
- [ ] Run cable from sensor bracket to display box
- [ ] Tare against protractor at 45°, sweep 0–90°, verify ≤0.5° accuracy
- [ ] Add target-angle menu + buzzer alert
- [ ] First real cutting session
- [ ] Write up results, update GitHub repo

---

## Questions

1. **Which end of the axle is exposed?** From the images it looks like the axle sticks out on the side closest to you (front). Confirm — this determines which side of the fixed arm gets the bracket.
2. **Axle end diameter?** Rough estimate is fine for now (exact measurement when the machine arrives). Needed for the optional magnet centering jig.
3. **Fixed arm geometry.** Is the fixed arm a flat plate, a round tube, or a cast block at the pivot area? This determines whether the sensor bracket clamps, screws, or adhesive-mounts to it. Can tell better once you have the machine in hand.
4. **Clearance behind the protractor.** The AS5600 bracket needs to sit near the axle end without interfering with the protractor scale or the handpiece sweep. Is there ~15–20 mm of clearance on the exposed axle side? (Answer when machine is in hand.)
5. **Are you leaning toward Option A instead of Option B now, or do you want to build both and compare?** If Option A only, you can skip the LSM6DS3TR-C order.
