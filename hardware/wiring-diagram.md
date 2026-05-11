# Wiring Diagrams

> Faceting Angle Finder (faf)
> Last Updated: 2026-05-11

All ASCII diagrams. Pin labels match silkscreen on the Adafruit Feather RP2350 (#6000).

---

## 1. System block diagram

```
                +---------------------------+
                |   LiPo 1000 mAh, JST PH   |
                |       (already have)      |
                +-------------+-------------+
                              |
                       BAT+   |   BAT-
                              |
                  +-----------+-----------+
                  |  SS12D00 power switch |   <-- "PWR"
                  |    (inline on BAT+)   |
                  +-----------+-----------+
                              |
                              v
+--------------------------------------------------------------+
|                  Feather RP2350 (#6000)                      |
|                                                              |
|   USB-C (charge + serial)        STEMMA QT  ->  AS5600       |
|                                                              |
|   3V3, GND, SDA, SCL  ----------------------> OLED SSD1309   |
|   D5  ----------------> Tare button -------> GND             |
|   D6  ----------------> Menu button -------> GND             |
|   D9  --[ SS12D00 "BUZZ" mute switch ]----> Piezo (+) -> GND |
+--------------------------------------------------------------+
```

---

## 2. Feather RP2350 pin map (the pins this project uses)

```
   ============== Feather RP2350 (#6000) ==============
   Top edge:  STEMMA QT connector  (SDA / SCL / 3V3 / GND)

   Left header (pin -> use)            Right header (pin -> use)
   ------------------------            -------------------------
   RST   (reset)                       VUSB  (5V from USB-C)
   3V3   -> OLED VCC                   EN    (enable, n/c)
   GND   -> common ground rail         VBAT  -> from PWR switch
   A0    (n/c)                         GND   (alt ground)
   A1    (n/c)                         SCL   -> OLED SCL
   A2    (n/c)                         SDA   -> OLED SDA
   A3    (n/c)                         D5    -> Tare button
   D24   (n/c, also A4)                D6    -> Menu button
   D25   (n/c, also A5)                D9    -> Buzzer (via mute switch)
                                       D10   (n/c)
                                       D11   (n/c)
                                       D12   (n/c)
                                       D13   (onboard LED, n/c)

   Other connectors:
     STEMMA QT  -> AS5600 breakout (I2C + 3V3 + GND, one 4-pin cable)
     JST PH 2-pin (BAT) -> LiPo battery via SS12D00 power switch
     USB-C  -> charging + CircuitPython serial / file transfer
```

Note: SDA/SCL on the right header are electrically the same net as the SDA/SCL pins inside the STEMMA QT connector. Both devices live on the same I2C bus.

---

## 3. I2C bus (AS5600 + OLED on one bus)

```
   Feather RP2350
   +---------------------------+
   |                           |
   |    [ STEMMA QT port ]----------+ (4-pin JST SH)
   |                           |    |
   |    SDA  (header pin) ---+ |    |    +-----------------+
   |    SCL  (header pin) -+ | |    +--->| AS5600 breakout |
   |    3V3  (header pin) | | |         |  Adafruit #6357 |
   |    GND  (header pin) | | |         |  I2C addr 0x36  |
   |                      | | |         |                 |
   +----------------------|-|-|---+     | DIR -> GND      |
                          | | |         |  (solder jumper |
                          | | |         |   for CW count) |
                          | | |         | OUT -> n/c      |
                          | | |         +-----------------+
                          | | |
                  +-------v-v-v-------+
                  |   SSD1309 OLED    |
                  |   2.42" 128x64    |
                  |   I2C addr 0x3C   |
                  |                   |
                  |  VCC -> 3V3       |
                  |  GND -> GND       |
                  |  SDA -> SDA       |
                  |  SCL -> SCL       |
                  +-------------------+

   I2C addresses on the shared bus:
     0x36  AS5600 (rotary encoder)
     0x3C  SSD1309 OLED
   No conflict. Both pulled up by AS5600 breakout's onboard 10k resistors.
```

---

## 4. AS5600 (STEMMA QT, no soldering needed for I2C)

```
   +-------------------------------+
   |     AS5600 breakout #6357     |
   |                               |
   |   [STEMMA QT]  [STEMMA QT]    |  <-- 2 ports, daisy-chain capable
   |                               |
   |   Pins broken out on header:  |
   |     VIN  3V3  GND  SDA  SCL   |
   |     DIR  OUT                  |
   |                               |
   |   Diametric magnet sits       |
   |   below the IC (1-2 mm gap)   |
   +-------------------------------+

   Required connections:
     STEMMA QT cable  -> Feather STEMMA QT port    (I2C + power)
     DIR pad          -> GND via solder jumper     (sets CW = increasing count)
     OUT pad          -> leave unconnected         (analog/PWM, unused)

   Magnet (6 mm x 3 mm, diametrically magnetized) glued to the quill
   cradle pivot pin, centered within ~1 mm of the rotation axis.
```

---

## 5. OLED (hand-wired to Feather header)

```
   SSD1309 2.42" OLED                 Feather RP2350 header
   (HiLetgo, 4-pin I2C)
   +--------------+
   |  GND   o-----------------------> GND
   |  VCC   o-----------------------> 3V3
   |  SCL   o-----------------------> SCL  (same net as STEMMA QT SCL)
   |  SDA   o-----------------------> SDA  (same net as STEMMA QT SDA)
   +--------------+

   I2C address 0x3C. Driven by adafruit_ssd1306 (SSD1309 is compatible).
```

---

## 6. Buttons (tare + menu, active-low to GND)

```
   Tare button (momentary, 6 mm tactile)
                                  +-----+
   Feather D5  -------------------|     |-----+
                                  +-----+     |
                                              v
                                             GND

   Menu button (momentary, 6 mm tactile)
                                  +-----+
   Feather D6  -------------------|     |-----+
                                  +-----+     |
                                              v
                                             GND

   Firmware enables internal pullups on D5 and D6.
   Pressed = LOW, released = HIGH. No external resistor needed.
```

---

## 7. Buzzer with SS12D00 mute switch

```
   Feather D9 ----+
                  |
                  v
              +-------+
              |   o   |  <- SS12D00 center (common) pin
              |  / |  |
              | /  |  |  Slide switch position controls path:
              |o   o  |    Up   = D9 -> buzzer (+)   "sound"
              +-------+    Down = D9 -> open        "mute"
                |   |
                |   +------ leave unconnected (mute side)
                |
                +------> Piezo buzzer (+)
                            |
                            v
                       Piezo (-) -> GND

   The buzzer is passive — firmware drives a square wave on D9.
   In "mute" position the path opens, no current flows, no sound.
```

---

## 8. Power: battery + SS12D00 power switch

```
   LiPo 3.7V 1000 mAh                Feather RP2350
   (JST PH 2-pin)                    BAT JST connector
   +---------+                       +-----------+
   |  BAT+   o------+                |   BAT+    o
   |         |      |                |           |
   |  BAT-   o-----------------------|   BAT-    o
   +---------+      |                +-----------+
                    |                      ^
                    v                      |
                +-------+                  |
                |   o   |  <- SS12D00 center (common)
                |  / |  |
                | /  |  |  Up   = battery -> Feather   "ON"
                |o   o  |  Down = open                  "OFF"
                +-------+
                    |   |
                    |   +-- leave unconnected (OFF side)
                    |
                    +-----> Feather BAT+

   Behavior:
     - USB-C plugged in:  Feather runs from USB regardless of switch.
                          Battery charges through Feather's onboard charger.
     - USB-C unplugged + switch ON:  Feather runs from battery.
     - USB-C unplugged + switch OFF: Feather is off, no quiescent drain.

   Both SS12D00 switches are SS12D00-G3 SPDT, 0.3 A @ 50 V.
   Well under the ~65 mA system draw — no thermal concern.
```

---

## 9. Cable run (sensor on arm -> case on arm)

```
   Quill cradle pivot pin (rotation axis)
        |
        v
   +---------+                   STEMMA QT cable
   | AS5600  |---------[ ~150-200 mm ]-----------+
   | sensor  |                                   |
   +---------+                                   v
                                          +------------+
                                          | Display    |
                                          | case on    |
                                          | arm side   |
                                          | (Feather + |
                                          |  OLED +    |
                                          |  battery)  |
                                          +------------+

   The case rides with the arm, so cable length is short (no longer
   the 400 mm to a mast-mounted box per the original plan).
   A 200 mm STEMMA QT cable is plenty; cut the 400 mm to length
   or substitute a shorter one if available.
```

---

## Bus / signal summary

| Net | Feather pin | Goes to |
|---|---|---|
| 3V3 | 3V3 header pin and STEMMA QT pin 4 | OLED VCC, AS5600 VIN |
| GND | GND header pins, STEMMA QT pin 1 | OLED GND, AS5600 GND, button returns, buzzer (-), battery (-) |
| SDA | SDA header pin = STEMMA QT pin 2 | OLED SDA, AS5600 SDA |
| SCL | SCL header pin = STEMMA QT pin 3 | OLED SCL, AS5600 SCL |
| D5  | D5 | Tare button -> GND |
| D6  | D6 | Menu button -> GND |
| D9  | D9 | Buzzer (+) via "BUZZ" mute switch |
| BAT+ | JST BAT (+) | LiPo (+) via "PWR" power switch |
| BAT- | JST BAT (-) | LiPo (-) direct |

---

## Build-order checklist

1. Solder DIR -> GND jumper on AS5600 breakout.
2. Plug STEMMA QT cable: Feather STEMMA QT port <-> AS5600.
3. Hand-wire OLED (4 wires) to Feather 3V3/GND/SDA/SCL header pins.
4. Wire tare button between D5 and GND.
5. Wire menu button between D6 and GND.
6. Wire D9 -> SS12D00 "BUZZ" center, "BUZZ" pin 1 -> piezo (+), piezo (-) -> GND.
7. Wire LiPo (+) -> SS12D00 "PWR" center, "PWR" pin 1 -> Feather BAT (+).
8. Wire LiPo (-) -> Feather BAT (-) direct.
9. Power on, run I2C scan. Expect 0x36 and 0x3C.
