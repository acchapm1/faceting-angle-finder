# Mast Position Sensor

> Status: Idea
> Created: 2026-04-13

Linear sensor on the mast to track handpiece height. Zero at the lowest carriage position, reading upward in 0.1mm increments.

## Use case

Repeatable height indexing alongside the angle readout — facet depth control, or returning to a saved height position between cuts.

## Sensor options

### Option A — AS5311 magnetic linear encoder (recommended)

The linear cousin of the AS5600 already used for angle sensing. Reads a multi-pole magnetic strip and reports position with ~0.5 um resolution — far exceeding the 0.1mm target.

- Magnetic strip glued along the mast post
- AS5311 sensor mounted on the display box or carriage (moves with the handpiece)
- I2C or SPI, works with the Feather RP2350
- ~$10-15 for the sensor + strip
- **Pro:** non-contact, no wear, ignores coolant, same sensor family as the AS5600
- **Con:** needs a straight magnetic strip the full length of the mast; sensor-to-strip air gap is tight (~0.5mm)

### Option B — Slide potentiometer

A 50-100mm linear potentiometer mounted alongside the mast with a linkage to the carriage.

- Analog read on a Feather ADC pin
- ~$5
- **Pro:** dead simple, cheap
- **Con:** limited travel range, mechanical linkage is fiddly, wears over time, coolant exposure

### Option C — VL53L1X time-of-flight laser

ToF sensor at the base of the mast pointing up at the carriage underside.

- I2C (addr 0x29, no conflict with AS5600 at 0x36 or OLED at 0x3C)
- ~$10-15 on a breakout
- **Pro:** no mechanical mounting along the mast, no contact
- **Con:** ~1mm practical accuracy — borderline for 0.1mm target

### Option D — DRO linear scale / digital caliper

Capacitive linear encoder (the kind used on milling machines or cheap digital calipers).

- 0.01mm resolution, trivially meets 0.1mm
- ~$15-30 depending on length
- **Pro:** extremely precise, designed for this kind of measurement
- **Con:** bulkier mounting, need to decode the serial data protocol (well-documented)

## Recommendation

Option A (AS5311 + magnetic strip) is the best fit — same sensor family as the AS5600, non-contact, coolant-resistant, and resolution is overkill for 0.1mm.

Option D (DRO linear scale) is the fallback if guaranteed industrial precision matters more than compactness.

## Display behavior

The angle readout is the primary display. The mast position shows in two cases:

- **Auto:** When the carriage is moving (position delta exceeds a threshold), the display switches to height (`XX.X mm`) automatically. Returns to angle after the carriage stops (short timeout, ~1-2 seconds).
- **Manual:** Pressing a button toggles to the height display. Pressing again (or timeout) returns to angle.

This keeps the angle front and center during cutting while making the height visible whenever you're adjusting carriage position.

## Firmware impact

Minimal. The main loop adds one more sensor read per cycle. Display logic needs a mode flag (angle vs height) driven by movement detection and button input. The Feather has plenty of I2C/ADC headroom.

## Open questions

1. **Mast travel distance** — how far does the carriage slide? Sets the sensor/strip length.
2. **Carriage mounting surface** — is there a flat surface on the carriage or mast sleeve where a sensor could sit at a fixed distance from the post?
3. **Primary use case** — repeatable depth-of-cut between facets, or returning to a saved height position, or both?
