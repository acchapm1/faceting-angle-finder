# Faceting Angle Finder (faf)

A digital angle finder for gem faceting machines. Reads the handpiece tilt angle via an AS5600 hall-effect rotary encoder on the pivot axle and displays it on a 2.42" OLED. Built with CircuitPython on an Adafruit Feather RP2350.

## Why

Mast-style faceting machines (like the Vevor) have a mechanical protractor at the pivot, but reading it accurately while cutting is awkward. This project adds a large, clear digital readout with tare, target-angle alerts, and a buzzer — all for ~$30 in parts.

## How it works

A 6mm diametrically-magnetized neodymium magnet is glued to the exposed end of the handpiece pivot axle. An AS5600 magnetic rotary encoder sits on a small 3D-printed bracket attached to the fixed arm, 1-2 mm above the magnet. As the handpiece tilts 0-90 degrees, the AS5600 reads the magnetic field rotation and reports a 12-bit angle over I2C.

The Feather RP2350 reads the sensor, applies filtering, and displays the angle as large digits on the OLED. A tare button lets you zero against the machine's own protractor at any known angle. A buzzer beeps when you reach a programmed target angle.

## Hardware

| Component | Part |
|---|---|
| MCU | Adafruit Feather RP2350 (#6000) |
| Sensor | AS5600 breakout, STEMMA QT (#6357) |
| Display | 2.42" SSD1309 128x64 OLED (I2C) |
| Power | 1000mAh LiPo (~15-18 hrs runtime) |
| Enclosure | PETG, printed on Bambu P1S |

Full BOM and wiring details are in [todo.md](todo.md).

## Repo structure

```
firmware/          CircuitPython code (code.py, lib/, boot.py)
hardware/          Wiring diagram, bill of materials
enclosure/         3D-printable bracket and display box (STEP + 3MF)
img/               Reference photos of the mast assembly
```

## Status

**Pre-build.** Parts are on order. Firmware and enclosure design will begin once the faceting machine and components arrive.

## Key specs

- 0.5 degree accuracy target (0.1 degree display resolution)
- 12-bit sensor (0.088 degree native resolution)
- Single-button tare against the machine's protractor
- Target-angle alert with buzzer
- Battery powered, charges over USB-C
- No machine modification required (magnet glues to exposed axle end, bracket clamps to fixed arm)

## License

MIT
