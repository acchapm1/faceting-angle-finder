# Faceting Angle Finder — I2C bring-up test
#
# Runs on a Feather RP2350 with AS5600 (STEMMA QT) and SSD1309 OLED on the
# shared I2C bus. Output goes to the USB serial REPL (open with `screen`,
# Mu, the Thonny REPL, or `tio /dev/tty.usbmodem*`).
#
# What it does, in a loop every 2 seconds:
#   1. Scans the I2C bus and prints found addresses.
#   2. Reports OK / MISSING for AS5600 (0x36) and SSD1309 OLED (0x3C).
#   3. If AS5600 is present, reads its STATUS, AGC, and RAW_ANGLE registers
#      so you can verify the magnet is detected and the gap is in range.
#
# Replace with the real angle-display firmware once bring-up is confirmed.

import time

import board
import busio

AS5600_ADDR = 0x36
OLED_ADDR = 0x3C

REG_STATUS = 0x0B
REG_RAW_ANGLE_HI = 0x0C
REG_AGC = 0x1A

EXPECTED = {
    AS5600_ADDR: "AS5600 (rotary encoder)",
    OLED_ADDR:   "SSD1309 OLED",
}


def scan(i2c):
    while not i2c.try_lock():
        pass
    try:
        return i2c.scan()
    finally:
        i2c.unlock()


def read_register(i2c, addr, reg, length=1):
    buf = bytearray(length)
    while not i2c.try_lock():
        pass
    try:
        i2c.writeto_then_readfrom(addr, bytes([reg]), buf)
    finally:
        i2c.unlock()
    return buf


def as5600_diagnostics(i2c):
    status = read_register(i2c, AS5600_ADDR, REG_STATUS)[0]
    magnet = bool(status & 0x20)
    too_strong = bool(status & 0x08)
    too_weak = bool(status & 0x10)

    agc = read_register(i2c, AS5600_ADDR, REG_AGC)[0]
    hi, lo = read_register(i2c, AS5600_ADDR, REG_RAW_ANGLE_HI, 2)
    raw_angle = ((hi & 0x0F) << 8) | lo
    angle_deg = raw_angle * 360.0 / 4096.0

    print("  AS5600 diagnostics:")
    print("    magnet detected:", "yes" if magnet else "NO  (no field seen — check magnet orientation and gap)")
    print("    too strong:     ", "YES (move magnet farther)" if too_strong else "no")
    print("    too weak:       ", "YES (move magnet closer)" if too_weak else "no")
    print("    AGC:            ", agc, " (good range 64-192; 0 or 255 = out of range)")
    print("    raw angle:      ", raw_angle, "/ 4095")
    print("    angle:           {:.2f} deg".format(angle_deg))


print()
print("=" * 60)
print("Faceting Angle Finder - I2C bring-up")
print("=" * 60)

# Feather RP2350: board.I2C() returns the SDA/SCL bus, which is the same
# physical bus as the STEMMA QT port. The OLED on the header and the
# AS5600 on the STEMMA QT cable share this bus.
i2c = board.I2C()

while True:
    found = scan(i2c)
    print()
    print("Scan result:", [hex(a) for a in found] or "(no devices)")

    for addr, name in EXPECTED.items():
        marker = "[OK]     " if addr in found else "[MISSING]"
        print(" ", marker, hex(addr), "-", name)

    if AS5600_ADDR in found:
        as5600_diagnostics(i2c)

    if set(EXPECTED) <= set(found):
        print()
        print("All expected devices present.")
        print("Slowly rotate a diametric magnet near the AS5600 — angle should sweep smoothly.")
    else:
        print()
        print("Devices missing. Check:")
        print("  - STEMMA QT cable fully seated at both ends (Feather and AS5600)?")
        print("  - OLED VCC->3V3, GND->GND, SDA->SDA, SCL->SCL all soldered/connected?")
        print("  - Voltage at OLED VCC actually 3.3V?")
        print("  - No short between SDA and SCL or between either and GND?")

    time.sleep(2)
