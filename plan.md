# Angle Finder — Implementation Plan

Monitors the angle of a faceting machine handpiece and displays it live.

## Accuracy target

**Revised target: 0.5° accuracy** (from the original 0.01° in `concept.md`). This is a huge simplification — it brings the project squarely into hobby-grade sensor territory and removes the need for precision ICs, careful mechanical integration, or elaborate calibration.

Quick vocabulary so we stay honest:

- **Resolution** — smallest change the display can show. We'll still show 0.1° on the display because it looks good and costs nothing.
- **Accuracy** — how close the reading is to truth. Target: ±0.5°.
- **Repeatability** — returning the same reading at the same physical position. Should easily beat accuracy (±0.1° is realistic) as long as the sensor is rigidly mounted.

At 0.5° accuracy, a single tare against a known reference (e.g., set the handpiece horizontal against the lap and press "zero") is all the calibration you need.

## Two viable sensing approaches

### Option A — Hobby magnetic encoder on the mast pivot

A small diametrically-magnetized magnet is glued to the end of the mast pivot shaft, and a hall-effect angle IC sits 1–3 mm away reading the magnetic field angle. This is exactly the "hall sensor angle finder" idea in `concept.md`.

**Sensor choice at 0.5° target: AS5600** (~$3–5 on a breakout). 12-bit / 0.088° resolution, I2C, works great with CircuitPython, and its accuracy is comfortably inside 0.5° when the magnet is centered within a reasonable tolerance. No need to step up to the AS5048A for this target.

**Pros:**
- Direct measurement of the actual pivot angle — no gravity dependence
- Rock-solid repeatability
- Independent of whether the machine is level
- Cheap sensor

**Cons:**
- Requires a small mechanical integration: magnet holder on the pivot shaft end, sensor PCB fixed to the non-rotating frame, concentric to ~1 mm
- Has to survive near coolant water and grit

### Option B — Accelerometer-based inclinometer on the handpiece (easiest retrofit)

A MEMS accelerometer clamped to the handpiece measures tilt relative to gravity.

**Sensor choice at 0.5° target: MPU6050, LSM6DSOX, or MMA8452** — any of the common cheap IMU breakouts. With a moving-average filter over ~20–50 samples, these will sit comfortably under 0.5° error for a static/slow-moving handpiece. An ADXL345 or ADXL345-equivalent is fine too. If you already have *any* accelerometer breakout in your parts bin, it probably works.

**Pros:**
- No mechanical modification to the machine — just clamp the PCB to the handpiece
- Gravity *is* the natural reference for a faceting angle (faceting machines are levelled)
- Simplest possible build

**Cons:**
- Only works if the machine is level (or you tare against the lap each session — easy)
- Sensitive to vibration — need low-pass filtering

### Recommendation

**Start with Option B using whatever cheap accelerometer you can get fastest** (MPU6050 or LSM6DSOX breakout, ~$5–10). With 0.5° as the target, the hard parts go away:

- No precision sensor needed
- No pivot-shaft machining needed
- No two-point calibration — a single-button tare against "horizontal on the lap" is enough
- You can clamp and unclamp it, swap handpieces, etc.

If Option B turns out not to hold 0.5° in practice due to vibration or drift, Option A with an AS5600 is a cheap backup — same MCU, same display, just a different sensor.

## Hardware plan (recommended build)

- **MCU:** XIAO RP2040 (you have it). CircuitPython. I2C on the standard pads.
- **Sensor:** MPU6050 or LSM6DSOX I2C breakout (Option B), or AS5600 I2C breakout + 6 mm diametric magnet (Option A). Both are on the same I2C bus, so you could even wire both during prototyping.
- **Display:** 1.3" SSD1306/SH1106 OLED over I2C is fine and cheap. If you want larger digits at bench distance, a 2.42" SH1106 OLED or a small ST7789 LCD both work. Share the I2C bus with the sensor (OLED) or use SPI (LCD).
- **Enclosure:** printed on the P1S in PETG — better heat and moisture resistance than PLA.
- **Power:** USB-C from the XIAO for v1. Battery can come later if wanted.
- **Buttons:** one momentary button for "zero/tare" against the lap. Optional second for "hold."

The XIAO ESP32-C3 is not needed for v1. Keep it in reserve for a later wireless/logging version.

## Firmware plan (CircuitPython on RP2040)

1. **Bring-up**
   - I2C scan, confirm sensor + OLED respond.
   - Read raw sensor at full rate, print to serial.
2. **Sensor driver**
   - Option B (accelerometer): use the Adafruit CircuitPython driver for the chosen IMU. Compute tilt from `atan2(ax, sqrt(ay² + az²))` or `atan2` on the two axes in the tilt plane, depending on sensor orientation.
   - Option A (AS5600): `adafruit_as5600` or direct I2C reads of the ANGLE register, unwrap to 0–360°.
3. **Filtering**
   - Moving average over ~20–50 samples, or a single-pole IIR (`y = y + α(x-y)` with α ≈ 0.05). The handpiece angle doesn't change fast while cutting, so aggressive filtering is free.
4. **Tare / zero**
   - Button press captures the current filtered reading as zero-offset.
   - Persist to flash via `microcontroller.nvm` or a small JSON file on the CIRCUITPY drive.
   - At 0.5° accuracy, single-point tare is sufficient — no two-point calibration needed.
5. **Display**
   - Large-digit readout: `XX.X°` (display 0.1° — cheap and looks good).
   - Small second line: tare state, filter indicator.
6. **Serial output** (optional)
   - Stream readings over USB CDC for logging or debugging.

## Mechanical plan (P1S)

- Sensor housing that clamps to the handpiece barrel (Option B) OR a pivot-end cap + magnet holder + fixed sensor bracket (Option A).
- Display + MCU enclosure with a cable back to the sensor head, so the electronics stay away from coolant.
- PETG recommended; design clearance for a silicone gasket if it'll be near water.

## Milestones

1. Decide Option A vs Option B (questions below).
2. Order sensor + OLED (if not already on hand).
3. Breadboard: XIAO RP2040 reads sensor, prints to serial.
4. Add OLED + filtering + tare button.
5. Print mechanical housing on the P1S, install on machine.
6. Bench-check against the machine's existing protractor at several angles to confirm ≤0.5° error.
7. Real-world cut test.

## Questions to refine the plan

With 0.5° as the target, most of the hardware-selection risk goes away. A few things still worth confirming:

1. **Option A vs Option B preference.** My recommendation is B (accelerometer clamped to the handpiece) because it's dead-simple and needs zero mechanical work. Any reason to prefer A (magnet on pivot shaft) — e.g., the machine isn't always level, or you already have a good pivot-shaft spot in mind?
2. **Parts on hand.** Do you already have *any* of these: an MPU6050/LSM6DS/ADXL345 accelerometer breakout, an AS5600 breakout, an SSD1306 or SH1106 OLED? If yes, v1 is effectively free to build.
3. **Angle range used while cutting.** Faceting is typically 0–90° from horizontal — confirm, so we pick the right axis mapping and display format.
4. **Is the machine mounted level and stationary?** (If yes, gravity-referenced Option B is rock-solid. If the machine gets moved or isn't level, Option A is safer.)
5. **Display size / viewing distance.** Small 1.3" OLED is fine if it sits <30 cm from your eyes; a 2.42" OLED or a small color LCD is worth it if you're looking at it from farther away while cutting.
6. **Buttons.** Just a tare/zero button? Or also a "hold" button that freezes the display?
7. **Photos of the mast, pivot point, and handpiece** would still help — not for sensor selection now, but for designing the 3D-printed clamp/housing.
8. **Existing angle reference on the Vevor** — is there a protractor scale we'd be supplementing, or is this the only angle readout?


## Answers to refine plan

1. Option B to start with.  My only concern is where to mount it as the main part of the hand piece that holds the dop needs to rotate 360 continous for creating round girdles.
2. I do not have any of those, which is the best quality
3. 0-90
4. yes the machine will be on a table and leveled.
5. A small oled display should be fine, when faceting I am fairy close to the mast that the hand piece is mounted on.
6. A tar/zero would be good if we have a means of knowing the angle of the hand piece when taring it.  like a jig to hold it in place.   Eventually id like a means to program an angle in and then have the display flash or buzzer to beep when the angle is reached.
7. There are images in the img dir next to this file.
8. there is a protractor on the hand piece.   see images below.

## Images
 [[mastsideview.jpg]]
 [[mastfrontview.jpg]]
 [[mastrangeofmotion.png]]

## Revised plan based on answers and images

### Mounting: where the sensor actually goes

Looking at the images, the handpiece has two independent motions:

- **Tilt** — the whole assembly pivots around a horizontal pin at the top of the mast block, swinging the dop end through ~0–90° from horizontal. This is the angle we care about. The protractor scale is mounted here.
- **Girdle rotation** — only the brass barrel at the *dop end* spins 360° continuously. The upper portion of the handpiece (the silver body between the tilt pivot and the return spring) does NOT rotate with it.

**The sensor clamps to the non-rotating upper body of the handpiece, between the tilt pivot and the spring.** That section tilts 1:1 with the protractor but never rotates. The 360° girdling concern goes away — you just don't put the sensor on the brass barrel below the spring.

I'd suggest a printed split-clamp (two halves, two M3 screws) that grips that upper body like a mic clip. Small, light, cable runs up to the display box on the mast post.

### Part recommendations (Option B, nothing on hand)

Since you don't already have parts, here's a specific shopping list at 0.5° accuracy:

- **Accelerometer:** **Adafruit LSM6DS3TR-C breakout (#4503)**. ~$12. STEMMA QT / Qwiic connector, great CircuitPython driver, much less drift/noise than an MPU6050, still cheap. (LSM6DSOX was first choice but is out of stock at Adafruit with no ETA. The LSM6DS3TR-C is the same family, same register map, same driver package — marginally noisier on paper but identical in practice at 0.5° accuracy.)
  - Avoid the MPU6050. It's cheap and everywhere, but it's noisier and less temperature-stable than the LSM6DS family, and the difference matters at the 0.5° level without heavy filtering.
- **Display:** **Adafruit 1.3" 128×64 OLED SH1106/SSD1306** (#938 or similar) on I2C. Big enough that `XX.X°` digits are very readable at mast distance. If you want bigger, a 2.42" SH1106 is still I2C and drops in.
- **MCU:** XIAO RP2040 (have it). I2C + one GPIO for a button + one GPIO for a piezo buzzer.
- **Button:** any momentary tactile button. One for tare, one for "set target angle" / cycle through menu.
- **Buzzer:** a small piezo (3.3 V, ~$1) driven by a GPIO through a transistor or directly if it's passive-with-driver. Used for "target angle reached."
- **Cables:** STEMMA QT / Qwiic cables let you chain the OLED and the LSM6DSOX on the same I2C bus with no soldering. This is the fastest path to a working prototype.
- **Enclosure:** two printed parts on the P1S:
  1. A split-clamp sensor head that grips the upper handpiece body, with a short strain-relieved cable to the display box.
  2. A display box that clamps to the mast vertical post, with the OLED + button(s) + buzzer facing you.

### Tare and target-angle features

Your question 6 is a good one — tare is only useful if you know what angle you're taring against. The machine already has a protractor scale right at the pivot. So the tare flow is:

1. Set the handpiece to a known angle on the existing protractor — say, exactly 45.0°.
2. Hold the tare button. The firmware computes `offset = 45.0° − current_raw_reading` and saves it to flash.
3. From then on, displayed angle = raw − offset, and it reads out in the same reference as the protractor.

You can tare against any angle, not just zero — that means you don't need a separate jig. The machine's own scale *is* the reference.

For the **target-angle / beep-when-reached** feature (your "eventually" goal), the firmware will:

1. Second button cycles a small menu: set target angle (up/down with the same buttons, or enter via serial).
2. Store targets in flash.
3. When `abs(current − target) < 0.2°`, flash the display and pulse the buzzer. When within 0.5° but not inside 0.2°, show a directional hint (`▲ 0.3°` meaning "raise 0.3°").
4. Multiple saved targets for cutting a whole tier at a time would be a v2 nice-to-have.

This kind of feature is easy on CircuitPython and doesn't change the hardware plan — it's just firmware.

### Updated hardware bill of materials

| Part | Part # / source | Approx. cost | Purpose |
|---|---|---|---|
| XIAO RP2040 | have it | — | MCU |
| LSM6DS3TR-C breakout | Adafruit #4503 | ~$12 | tilt sensor |
| 1.3" OLED (SH1106/SSD1306 I2C) | Adafruit / Amazon | ~$10 | display |
| STEMMA QT cables (2) | Adafruit | ~$2 | no-solder I2C |
| Momentary tactile buttons (2) | generic | ~$1 | tare + menu |
| Piezo buzzer | generic | ~$1 | target-reached alert |
| PETG filament | have it | — | enclosures |
| M3 screws / heat-set inserts | generic | ~$3 | clamp hardware |

Total new spend: roughly **$25–30**.

### Updated milestones

1. Order LSM6DS3TR-C + OLED + STEMMA QT cables.
2. Breadboard on the XIAO RP2040: I2C scan, read accelerometer, print tilt to serial, confirm numbers match the protractor within a degree or so raw.
3. Add OLED, filtering, large-digit layout.
4. Add tare button. Verify: set to 45° on the protractor, press tare, reading = 45.0°. Sweep the whole 0–90° range and compare to protractor at several points.
5. Add target-angle menu + buzzer.
6. Print split-clamp sensor head and mast-mounted display box. Cable between them.
7. Install on machine. Bench-check against the protractor across the full range.
8. Real cutting session — do facets actually meet cleanly with this as the angle reference?

### Open questions / things to confirm before ordering

1. **Diameter of the upper handpiece body** (the silver section between the tilt pivot and the return spring) — need this for the split-clamp design. A caliper measurement is best; otherwise, a photo with a ruler alongside would work.
2. **Diameter of the mast vertical post** for the display-box clamp.
3. **Cable length** from sensor head to display box — guess ~30 cm based on the images; confirm by measuring the distance from the handpiece's tilted mid-position to a comfortable display spot on the mast.
4. **Is there room above the tilt pivot** to glue a small magnet to the pivot pin end, in case you ever want to switch to Option A later? (No action now — just worth looking.)
5. **Buzzer volume** — faceting machines are noisy-ish. Is a small piezo audible over the lap, or do we want a louder one / vibration alert / big visual indicator instead?

## Open Answers / confirmation

1. I do not have the faceting machine yet, its in the mail, create a checkpoint to follow up on this later.  If possilble create a reminder Cowork to get these measurements on April 22nd, 2026. 
2. Same answer as #1
3. 12-15"
4. yes there is room
5. a small piezo alarm will work. 
