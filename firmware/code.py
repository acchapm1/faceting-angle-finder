# Faceting Angle Finder (faf) — angle display firmware
#
# Feather RP2350 + AS5600 magnetic encoder (I2C 0x36) + SSD1309 OLED (I2C 0x3C).
# Reads the handpiece tilt off the AS5600, filters it, and shows it big on the
# OLED. Tare button zeroes the reading at the current position. Menu button
# arms a target angle; the buzzer beeps as you approach and land on it.
#
# Tare offset and target angle persist across reboots in microcontroller.nvm,
# so no filesystem writes are needed (the USB host keeps CIRCUITPY read-only).
#
# The bring-up / I2C-scan diagnostic lives in bringup_test.py — copy it over
# code.py if you need to re-debug the hardware.
#
# Pins (see CLAUDE.md / todo.md):
#   STEMMA QT : AS5600 (I2C + power)
#   SDA/SCL   : OLED (hand-wired, same bus)
#   D5        : Tare button   (internal pullup, active low)
#   D6        : Menu button   (internal pullup, active low)
#   D9        : Piezo buzzer  (passive, via mute switch)

import struct
import time

import board
import digitalio
import pwmio

import adafruit_ssd1306

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AS5600_ADDR = 0x36
OLED_ADDR = 0x3C
OLED_W, OLED_H = 128, 64

# AS5600 registers
_STATUS = 0x0B
_RAW_ANGLE_HI = 0x0C  # 0x0C hi (bits 11:8), 0x0D lo (bits 7:0)
_AGC = 0x1A

# IIR smoothing factor (0..1). Higher = snappier, lower = smoother.
# The AS5600 is low-noise, so a light filter is plenty.
FILTER_ALPHA = 0.25

# Buzzer
BUZZ_FREQ = 2000  # Hz, near the piezo's resonant peak for loudness
TARGET_STEP = 5.0  # degrees the Menu button advances the target each press
TARGET_MAX = 90.0  # wrap the target back to off past this
NEAR_DEG = 2.0  # start "approaching" beeps within this many degrees
ON_TARGET_DEG = 0.3  # considered "on target" within this band

# Buttons are active-low with internal pullups.
DEBOUNCE_S = 0.03

# NVM layout: magic byte, then two little-endian floats (tare_offset, target).
# target == -1.0 means "no target armed".
_NVM_MAGIC = 0xFA
_NVM_FMT = "<Bff"
_NVM_SIZE = struct.calcsize(_NVM_FMT)


# ---------------------------------------------------------------------------
# AS5600 raw I2C driver (no Adafruit driver exists for this part)
# ---------------------------------------------------------------------------

def _read_reg(i2c, reg, length=1):
    buf = bytearray(length)
    while not i2c.try_lock():
        pass
    try:
        i2c.writeto_then_readfrom(AS5600_ADDR, bytes([reg]), buf)
    finally:
        i2c.unlock()
    return buf


def read_raw_angle(i2c):
    """12-bit raw angle, 0..4095 over a full 360 degrees."""
    hi, lo = _read_reg(i2c, _RAW_ANGLE_HI, 2)
    return ((hi & 0x0F) << 8) | lo


def read_status(i2c):
    """Return (magnet_detected, too_strong, too_weak, agc)."""
    status = _read_reg(i2c, _STATUS)[0]
    agc = _read_reg(i2c, _AGC)[0]
    return (
        bool(status & 0x20),
        bool(status & 0x08),
        bool(status & 0x10),
        agc,
    )


def raw_to_degrees(raw):
    return raw * 360.0 / 4096.0


# ---------------------------------------------------------------------------
# Angle math: unwrap around the 0/360 seam so the tared reading is continuous
# ---------------------------------------------------------------------------

def signed_delta(a, b):
    """Smallest signed difference a - b, wrapped into (-180, 180]."""
    d = (a - b) % 360.0
    if d > 180.0:
        d -= 360.0
    return d


# ---------------------------------------------------------------------------
# Persistence via microcontroller.nvm (survives reboot, no filesystem writes)
# ---------------------------------------------------------------------------

def load_state():
    """Return (tare_offset_deg, target_deg_or_None)."""
    try:
        import microcontroller

        raw = bytes(microcontroller.nvm[0:_NVM_SIZE])
        magic, offset, target = struct.unpack(_NVM_FMT, raw)
        if magic != _NVM_MAGIC:
            return 0.0, None
        return offset, (None if target < 0 else target)
    except Exception:
        return 0.0, None


def save_state(offset, target):
    try:
        import microcontroller

        packed = struct.pack(
            _NVM_FMT, _NVM_MAGIC, offset, -1.0 if target is None else target
        )
        microcontroller.nvm[0:_NVM_SIZE] = packed
    except Exception:
        pass  # NVM unavailable — non-fatal, tare just won't persist


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

class Button:
    """Active-low button with debounce. .pressed() is True once per press."""

    def __init__(self, pin):
        self.io = digitalio.DigitalInOut(pin)
        self.io.switch_to_input(pull=digitalio.Pull.UP)
        self._last = True  # released (high) with pullup
        self._last_change = time.monotonic()

    def pressed(self):
        now = time.monotonic()
        val = self.io.value
        if val != self._last and (now - self._last_change) >= DEBOUNCE_S:
            self._last_change = now
            self._last = val
            if val is False:  # high -> low = press
                return True
        elif val != self._last:
            self._last_change = now  # note the edge, wait out the debounce window
        return False


# ---------------------------------------------------------------------------
# Buzzer (passive piezo on D9, driven with PWM)
# ---------------------------------------------------------------------------

class Buzzer:
    def __init__(self, pin):
        self.pwm = pwmio.PWMOut(
            pin, frequency=BUZZ_FREQ, duty_cycle=0, variable_frequency=True
        )
        self._off_at = None

    def beep(self, duration=0.06, freq=BUZZ_FREQ):
        self.pwm.frequency = freq
        self.pwm.duty_cycle = 32768  # 50% square wave
        self._off_at = time.monotonic() + duration

    def update(self):
        if self._off_at is not None and time.monotonic() >= self._off_at:
            self.pwm.duty_cycle = 0
            self._off_at = None


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def draw(oled, angle, status_str, target, on_target):
    oled.fill(0)

    # Big angle, e.g. "42.3" scaled x4 (font5x8 -> ~24px wide, 32px tall glyphs).
    text = "{:.1f}".format(abs(angle))
    if angle < 0:
        text = "-" + text
    oled.text(text, 0, 4, 1, size=4)

    # Degree symbol as a small hollow square, just past the number block.
    dx = len(text) * 24 + 2
    if dx < OLED_W - 6:
        oled.rect(dx, 4, 5, 5, 1)

    # Status line along the bottom.
    oled.text(status_str, 0, OLED_H - 8, 1)

    # Target readout, right-aligned on the status line.
    if target is not None:
        tgt = "T{:.0f}".format(target)
        if on_target:
            tgt = "*" + tgt + "*"
        oled.text(tgt, OLED_W - len(tgt) * 6, OLED_H - 8, 1)

    oled.show()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    i2c = board.I2C()  # shared bus: AS5600 + OLED

    oled = adafruit_ssd1306.SSD1306_I2C(OLED_W, OLED_H, i2c, addr=OLED_ADDR)
    oled.fill(0)
    oled.text("Faceting Angle", 0, 0, 1)
    oled.text("Finder", 0, 10, 1)
    oled.text("starting...", 0, 28, 1)
    oled.show()

    tare_button = Button(board.D5)
    menu_button = Button(board.D6)
    buzzer = Buzzer(board.D9)

    tare_offset, target = load_state()

    # Seed the filter with the first real reading so it doesn't sweep from 0.
    filtered = raw_to_degrees(read_raw_angle(i2c))

    last_beep_bucket = None  # rate-limits approach beeps
    was_on_target = False
    last_draw = 0.0

    while True:
        # --- read + filter ---
        raw_deg = raw_to_degrees(read_raw_angle(i2c))
        # Filter in the wrapped domain so it behaves across the 0/360 seam.
        filtered += FILTER_ALPHA * signed_delta(raw_deg, filtered)
        filtered %= 360.0

        # Displayed angle = signed distance from the tare point.
        angle = signed_delta(filtered, tare_offset)

        # --- buttons ---
        if tare_button.pressed():
            tare_offset = filtered  # current position becomes 0.0
            save_state(tare_offset, target)
            buzzer.beep(0.04)
            angle = 0.0

        if menu_button.pressed():
            # Cycle the target: off -> 5 -> 10 -> ... -> 90 -> off
            if target is None:
                target = TARGET_STEP
            else:
                target += TARGET_STEP
                if target > TARGET_MAX:
                    target = None
            save_state(tare_offset, target)
            buzzer.beep(0.04)

        # --- magnet status ---
        detected, too_strong, too_weak, agc = read_status(i2c)
        if not detected:
            status = "NO MAGNET"
        elif too_weak:
            status = "gap: too far"
        elif too_strong:
            status = "gap: too near"
        else:
            status = "ok agc{}".format(agc)

        # --- target proximity + buzzer ---
        on_target = False
        if target is not None and detected:
            err = abs(abs(angle) - target)
            if err <= ON_TARGET_DEG:
                on_target = True
                if not was_on_target:
                    buzzer.beep(0.12, BUZZ_FREQ)  # landed
            elif err <= NEAR_DEG:
                # Approach beeps: quicker as you close in, rate-limited by bucket.
                bucket = int(err / 0.5)
                if bucket != last_beep_bucket:
                    last_beep_bucket = bucket
                    buzzer.beep(0.03, BUZZ_FREQ)
            else:
                last_beep_bucket = None
            was_on_target = on_target
        else:
            was_on_target = False
            last_beep_bucket = None

        buzzer.update()

        # --- draw at ~20 Hz (sensor/button loop runs faster for responsiveness) ---
        now = time.monotonic()
        if now - last_draw >= 0.05:
            draw(oled, angle, status, target, on_target)
            last_draw = now

        time.sleep(0.005)


main()
