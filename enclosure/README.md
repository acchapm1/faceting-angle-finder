# enclosure/

3D-printable parts for mounting the sensor and display on the faceting machine. Designed for PETG on a Bambu P1S.

## Contents

| File | Purpose |
|---|---|
| `sensor-bracket.step` | Mounts the AS5600 breakout to the fixed arm, centered over the magnet on the pivot axle end |
| `sensor-bracket.3mf` | Print-ready sliced file for the sensor bracket |
| `display-box.step` | Clamps to the mast post, houses the Feather RP2350, OLED, buttons, buzzer, and LiPo battery |
| `display-box.3mf` | Print-ready sliced file for the display box |

## Design notes

- **Sensor bracket:** Small, light, must not block the 0-90 degree handpiece arc. Adjustable air gap (1-2 mm) between the AS5600 IC and the magnet. STEMMA QT cable routes down to the display box.
- **Display box:** OLED window on the front face, buttons on top or side, USB-C port accessible for charging. Internal volume roughly 80x50x25 mm to fit the OLED board (71x43 mm), Feather (51x23 mm), and LiPo (~50x30x6 mm).
- **Material:** PETG for moisture resistance near coolant.
- **Exact dimensions** depend on caliper measurements of the pivot axle, fixed arm, and mast post (taken when the machine arrives).
