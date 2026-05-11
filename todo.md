# Faceting Angle Finder (faf) — TODO

## GitHub Project

**Repo:** https://github.com/acchapm1/faceting-angle-finder

```bash
# clone
git clone https://github.com/acchapm1/faceting-angle-finder.git

# or, from the existing local working copy
cd /Users/acchapm1/tools/acc-2ndbrain/faceting/anglefinder
git pull
```

### Repo structure (evolving as firmware / enclosure work progresses)

```
faceting-angle-finder/
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
    sensor-bracket.step   # AS5600 bracket for fixed arm / pivot axle
    display-box.step      # mast-mounted display housing
    sensor-bracket.3mf    # print-ready sliced file
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

Just say: **"The machine arrived, ready to continue the angle finder build"** and provide the caliper measurements (pivot axle end diameter, fixed arm dimensions, mast post diameter).

---

## Why the hall sensor (AS5600)

- Measures the actual pivot angle directly — no gravity dependence, no vibration sensitivity
- Rock-solid repeatability — the magnet-to-sensor geometry is fixed
- Works regardless of whether the machine is level
- The AS5600 is cheap (~$3–5), I2C, 12-bit (0.088° resolution), and well within 0.5° accuracy
- Exposed axle end + fixed arm means no machining — just glue + a printed bracket

---

## Parts List

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
| 5 | M3x8 socket head screws (x4) | $2 | sensor bracket + display box assembly |
| 6 | M3 heat-set inserts (x4) | $1 | press into PETG printed parts |

### Already have

| Part | Notes |
|---|---|
| 2.42" SSD1309 128x64 OLED (HiLetgo, 4-pin I2C) | display, 71x43mm board, I2C addr 0x3C, SSD1306-compatible driver |
| 3.7V LiPo battery, 1000mAh, JST PH 2-pin | ~18 hrs runtime, ~50x30x6mm |
| Momentary tactile buttons (x2) | 6mm through-hole, tare + menu |
| Piezo buzzer, passive, 3.3V | target-angle alert |
| SS12D00-G3 slide switches (x2) | SPDT, 0.3A/50V — one for battery power, one for buzzer mute |
| 5x7 cm double-sided protoboard (x2+) | carrier boards for OLED + Feather sandwich layout |
| XIAO RP2040 | kept as spare — not used in this build |
| PETG filament | for 3D-printed enclosures on P1S |
| Bambu Labs P1S | for printing enclosures |
| Cyanoacrylate (superglue) or UV-cure adhesive | to bond magnet to handpiece shaft end |

### Optional / future

| Part | When | Why |
|---|---|---|
| XIAO ESP32-C3 | v2 | wireless angle logging / remote display |
| LSM6DS3TR-C | if already ordered | can use as fallback or different project, addr 0x6A doesn't conflict |

### Power budget

| Component | Draw | Notes |
|---|---|---|
| Feather RP2350 (active) | ~30 mA | M33 cores running, I2C polling |
| AS5600 | ~6 mA | continuous measurement |
| SSD1309 2.42" OLED | ~20–30 mA | larger panel draws slightly more than 1.3"; depends on pixel fill |
| **Total steady state** | **~55–65 mA** | |

With a 1000 mAh battery: **~15–18 hours runtime.** Charges in ~5 hours over USB-C (Feather charges at 200 mA). Comfortably past the 10-hour target.

### Total new spend

~$20–25 (Adafruit parts + M3 hardware + shipping). Saved on OLED, battery, buttons, buzzer, and switches already on hand.

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
- Cable routing: 4 wires (VCC, GND, SDA, SCL) run from the bracket down to the display box.

### Bracket orientation

The AS5600 IC is on one side of the breakout PCB. The bracket positions the PCB so the IC faces the magnet. Check your specific breakout — most have the IC on the top side with a small circle marking.

---

## Wiring

The Feather RP2350 has a built-in STEMMA QT connector, so the AS5600 plugs in with a single cable. The OLED is hand-wired to the same I2C bus. Buttons, buzzer, and slide switches go to GPIO pins / inline on the Feather header.

```
Feather RP2350 (#6000) Pinout (relevant pins):
  STEMMA QT ── I2C bus (SDA/SCL/3V3/GND) ── AS5600 via cable
  SDA        ── also broken out on header (for hand-wiring OLED)
  SCL        ── also broken out on header (for hand-wiring OLED)
  D5         ── Tare button (to GND, use internal pullup)
  D6         ── Menu button (to GND, use internal pullup)
  D9         ── Piezo buzzer (+) via SS12D00 mute switch
  3V3        ── OLED VCC
  GND        ── common ground
  BAT        ── LiPo + (via SS12D00 power switch)

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

Piezo buzzer (via mute switch):
  D9             → SS12D00 center (common) pin
  SS12D00 pin 1  → buzzer (+)        [switch in "sound" position]
  SS12D00 pin 3  → leave unconnected [switch in "mute" position = open circuit]
  buzzer (-)     → GND
  # Alternative: wire both side pins so mute position goes to GND, which clamps
  # the line more firmly but doesn't change behavior meaningfully.

Power switch (inline on battery +):
  LiPo JST (+)   → SS12D00 center (common) pin
  SS12D00 pin 1  → Feather JST battery (+) [switch ON]
  SS12D00 pin 3  → leave unconnected       [switch OFF]
  LiPo JST (−)   → Feather JST battery (−) direct
  # NOTE: When USB-C is plugged in, Feather runs off USB regardless of this
  # switch. That's desirable — the switch only controls untethered battery use.
  # Charging still works with the switch OFF (USB → charger → battery directly
  # is NOT cut by this switch since the switch is between battery and Feather
  # VBAT, not between charger and battery — double check wiring against your
  # specific Feather rev before final assembly).

LiPo battery (1000mAh, JST PH 2-pin):
  Plug into Feather JST battery connector via the SS12D00 power switch above.
  Charges via USB-C automatically when plugged in.
```

---

## CircuitPython Setup

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

1. **Bring-up**
   - I2C scan — confirm AS5600 at 0x36 and OLED at 0x3C.
   - Read `as5600_status()` — verify magnet detected, not too strong/weak. Display status on serial. If magnet not detected, check air gap and magnet orientation.
   - Read raw angle, print to serial while slowly tilting the handpiece. Confirm the value changes smoothly over the full 0–90° range.

2. **Angle mapping**
   - The AS5600 reports 0–4095 over a full 360° rotation. You'll only use ~25% of that range (0–90° tilt).
   - Convert: `angle_deg = raw * 360.0 / 4096.0`
   - The zero point depends on how the magnet is oriented when glued — tare handles this.

3. **Filtering**
   - IIR or moving-average filter — the AS5600 is inherently less noisy than an accelerometer so you can use lighter filtering (10–20 samples or α ≈ 0.1).

4. **Tare / zero**
   - Set handpiece to a known angle on the protractor, press tare.
   - `offset = known_angle - current_raw_degrees`
   - `displayed = current_raw_degrees + offset`
   - Persist to `microcontroller.nvm` or JSON on CIRCUITPY.

5. **Display**
   - Large `XX.X°` on top, status line on bottom.
   - Add a magnet-status indicator on the status line (good/weak/strong) — the AS5600 reports this for free. Useful during initial setup.

6. **Target angle + buzzer**
   - Same button logic, same flash/beep behavior.

7. **Serial output**
   - Optional USB CDC stream for debugging/logging.

---

## Mechanical plan (P1S printed parts)

### Part 1: Handpiece cradle + sensor bracket (split design)

**Design goal:** the handpiece must be removable for close inspection of the gem (since the magnet at the end of the handpiece shaft is what holds the dop), while the AS5600 sensor stays permanently mounted to the arm. Re-inserting the handpiece should not require re-taring.

**Concept — split V-block cradle:**

- The cradle is a two-piece V-block mounted to the arm where the handpiece normally sits.
- **Bottom half** is a fixed V-groove permanently bolted to the arm. The AS5600 breakout is mounted directly to (or beside) this bottom half, positioned so it will align with the end of the handpiece shaft when the handpiece is seated.
- **Top half** is a removable cap held by one or two thumbscrews (M3 knurled or a quick-release cam lever). Lifting it releases the handpiece; the sensor and bottom half stay put.
- When the handpiece is lowered back into the V, the magnet on the shaft's end lands in the same position every time (within ~0.5 mm), well inside the AS5600's tolerance.
- Locating pin or shoulder at the end of the V constrains axial (in/out) position of the handpiece so the air gap stays consistent.

**Magnet location change:**

- Previously the plan glued the magnet to the pivot axle. Revised: the magnet is glued to the **end of the handpiece shaft** (the end opposite the dop/gem).
- This way the sensor reads the angle of the handpiece itself — the thing whose angle you actually care about — and removing the handpiece doesn't disturb the sensor.
- Sensor sits at the "butt" end of the handpiece when cradled, with the 1–2 mm air gap to the magnet.

**Bracket requirements:**

- PETG, moisture resistant for coolant exposure.
- Air gap adjustment: slot + screw, or a few printed shim washers.
- Cable management: STEMMA QT cable routes from the sensor along the arm down to the display box.
- Must clear the full handpiece sweep (0–90°) and not interfere with the protractor scale.
- Thumbscrew/cam lever on the cap should be operable with gloved/wet hands.

### Part 2: Display box (PCB sandwich)

Clamps to the mast vertical post. Houses Feather RP2350, OLED, buttons, buzzer, slide switches, and LiPo battery, built on two 5x7cm double-sided protoboards in a sandwich layout.

**PCB sandwich layout:**

- **Front board (5x7 cm protoboard):** OLED mounts to the front face. The OLED board (71x43 mm) nearly fills the protoboard — essentially a carrier.
- **Rear board (5x7 cm protoboard):** Feather RP2350 soldered on. Tactile buttons on top edge, SS12D00 slide switches on one side edge (power) and opposite side or top edge (buzzer mute), piezo buzzer tucked behind. Battery in a pocket behind/below.
- The two boards are connected by a short ribbon cable or 4-pin header strip carrying SDA, SCL, 3V3, GND to the OLED.
- Overall box internal dims roughly 80 x 55 x 30 mm to allow the two-board stack plus battery.

**Enclosure features:**

- Window on front face for OLED active area.
- Cutouts on side/top for tactile buttons (tare, menu).
- Slots on edges for the two SS12D00 slide switches — labeled "PWR" and "BUZZ".
- USB-C port accessible for charging (Feather runs from USB and charges battery when plugged in — works regardless of power switch position, see wiring notes).
- Piezo buzzer vent hole aligned with buzzer body.
- STEMMA QT cable exits toward the pivot area / arm (12–15 inch run to the sensor cradle).
- Mast clamp integrated on the back of the enclosure.

### Part 3: Magnet alignment jig (optional, nice-to-have)

A small disposable printed sleeve that slips over the handpiece shaft end and centers the 6mm magnet while the glue cures. Ensures the magnet is concentric with the shaft. Peel off after curing.

---

## Tasks

### Pre-machine (do now at the desk)

- [x] Order Feather RP2350 (#6000), AS5600 (#6357) + magnet add-on, STEMMA QT cable from Adafruit
- [x] Order LiPo battery, buttons, buzzer, magnets from Amazon
- [x] Have 2.42" SSD1309 OLED on hand (from parts drawer)
- [x] Have LiPo battery, tactile buttons, piezo buzzer on hand
- [x] Have SS12D00-G3 SPDT slide switches on hand (x2 — power + buzzer mute)
- [x] Have 5x7 cm double-sided protoboards on hand (carrier / sandwich layout)
- [x] Create GitHub repo — https://github.com/acchapm1/faceting-angle-finder
- [ ] Install CircuitPython on Feather RP2350
- [ ] Install libraries (`adafruit_ssd1306`, `adafruit_framebuf`, `adafruit_bus_device`)
- [ ] Write AS5600 I2C driver (code above, or test on breadboard with magnet taped nearby)
- [ ] Breadboard: plug AS5600 into Feather via STEMMA QT, I2C scan, confirm 0x36 and OLED at 0x3C
- [ ] Breadboard: read angle while waving a diametric magnet near the sensor — confirm values change
- [ ] Breadboard: display angle on OLED with large digits
- [ ] Breadboard: add filter, tare button, buzzer

### Machine-in-hand (after delivery)

- [ ] Measure handpiece shaft diameter (butt end) with calipers — sets V-block geometry and magnet jig
- [ ] Measure handpiece overall length + cradle seating location on arm
- [ ] Measure the arm's handpiece-mount interface (for split V-block cradle)
- [ ] Measure mast post diameter (for display box clamp)
- [ ] Glue diametric magnet centered on handpiece shaft butt end, let cure
- [ ] Check `as5600_status()` — confirm magnet detected, strength OK
- [ ] Print split V-block cradle (bottom half + removable top cap with thumbscrew)
- [ ] Mount AS5600 to fixed bottom half of cradle, aligned with handpiece shaft end
- [ ] Test handpiece removal + re-insertion — verify angle reading is consistent (no re-tare needed)
- [ ] Adjust air gap — aim for 1–2 mm, check AGC register for optimal signal
- [ ] Assemble PCB sandwich: OLED on front board, Feather + switches + buttons + buzzer on rear board
- [ ] Wire SS12D00 power switch inline on battery + lead
- [ ] Wire SS12D00 mute switch inline between D9 and piezo buzzer
- [ ] Print display box, mount on mast post
- [ ] Run STEMMA QT cable from sensor cradle to display box
- [ ] Tare against protractor at 45°, sweep 0–90°, verify ≤0.5° accuracy
- [ ] Verify handpiece removal mid-session does not disturb tare
- [ ] Add target-angle menu + buzzer alert
- [ ] First real cutting session
- [ ] Write README.md with photos and build instructions
- [ ] Tag v1.0.0 release on GitHub

---

## Questions

1. **Handpiece shaft butt-end geometry.** The magnet now glues to the end of the handpiece shaft (not the pivot axle). Is that end flat, rounded, or threaded? Diameter? Needed for the magnet centering jig and the V-block sensor alignment. (Measure when machine arrives.)
2. **How does the handpiece currently seat on the arm?** V-groove, round socket, split clamp, or something else? The split cradle design needs to match or replace whatever interface exists.
3. **Handpiece repeatability.** When you lift and re-seat the handpiece, does it return to the same angle (visually, against the protractor)? If the existing cradle already enforces that, the split-cap design can mimic it; if not, the new cradle needs tighter tolerancing.
4. **Clearance behind the handpiece butt.** The sensor needs ~15–20 mm behind the handpiece butt end to sit. Is there clearance, or does something (counterweight, arm structure) get in the way at full 0–90° sweep? (Answer when machine is in hand.)
5. **Mast post diameter** (for display box clamp).

---

## Design revision — 2026-04-22: arm-mounted case

### Decision

All electronics (Feather, OLED, AS5600, battery, buttons, buzzer, switches) now mount to the **arm** (the part attached to the mast that holds the quill cradle), not the mast post itself. The arm swings with the quill's angular motion, so a sensor fixed to the arm reads the arm's angle directly relative to a reference on the mast — or, if the pivot is between the mast and arm, the AS5600 magnet sits on that pivot pin.

### Terminology update

- **Mast** — vertical post
- **Arm** — the part attached to the mast (was called "fixed arm" in earlier docs)
- **Quill** — the handpiece that sits in the black cradle on top of the arm and is removed for facet inspection (previously called "handpiece")
- **Cradle** — the black V-block on top of the arm that holds the quill

### Mast measurement (known)

- [x] Mast post diameter: **15 mm**

### Mechanical changes from previous plan

- Sensor magnet moves from the quill shaft end back to the **quill cradle pivot pin** on the arm. The arm rotates around this pin relative to the mast, which is what sets the cutting angle.
- The whole electronics case mounts to the **side of the arm** and rides with it through the full angular sweep.
- Quill remains freely removable from the cradle without disturbing anything — the sensor is nowhere near the quill itself.
- Display readability: since the case moves with the arm, the OLED orientation relative to the user changes slightly through the sweep. Acceptable — large digits will still be legible.
- No separate display box on the mast. Single integrated case on the arm.

### Measurements needed before enclosure CAD can start

**Arm geometry (the part in img/mastsideview.jpg attached to the mast):**

- [ ] Arm cross-section at the case mount point — width × height (note shape: rectangular / round / tapered)
- [ ] Arm length from mast to quill cradle center - 60mm
- [ ] Preferred case position along the arm (closer to mast = less vibration; closer to cradle = easier to read)
- [ ] Which side of the arm the case mounts to (left or right as user faces machine in cutting position)
- [ ] Clearance around the arm (distance to splash pan, lap, any other obstruction) through full 0–90° quill travel

**Pivot axis (critical for AS5600 magnet placement):**

- [ ] Quill cradle pivot pin diameter
- [ ] Pivot pin length, and whether either end is exposed / accessible
- [ ] Distance from pivot pin axis to the side face of the arm where the case mounts
- [ ] Whether magnet can glue to an exposed pin end, or whether a coupling arm is needed

**Mounting method:**

- [ ] Preferred attachment — non-destructive clamp, set screws, adhesive, or OK to drill/tap the arm

**Range of motion:**

- [ ] Actual angular range the arm sweeps through (e.g. 0° to ~95°)
- [ ] Any mechanical stops at the extremes

### Next design-phase tasks

- [ ] Caliper all arm dimensions listed above
- [ ] Photograph arm from side, end, and close-up of pivot pin/cradle (with caliper in frame)
- [ ] Decide mount side (left/right) based on user handedness and cutting position
- [ ] User will design the case in CAD given the measurements and the PCB sandwich footprint (roughly 80 × 55 × 30 mm internal for Feather + OLED + battery)
- [ ] Confirm sensor-to-magnet geometry: AS5600 IC face parallel to magnet face, 0.5–3 mm air gap, centered on pivot axis within ~1 mm
