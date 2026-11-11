# Small driver for a 16x2 character LCD with a PCF8574 I2C "backpack".
# Only what the doorbell needs: clear, move the cursor, print, backlight.

import time

_RS = 0x01         # 1 = sending a character, 0 = sending a command
_ENABLE = 0x04     # the LCD reads the data when this pin pulses
_BACKLIGHT = 0x08


class LcdI2c:
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address
        self.light = _BACKLIGHT
        self.init()

    def _write4(self, bits, rs):
        # Sends the top 4 bits of `bits` (the LCD runs in 4-bit mode).
        out = (bits & 0xF0) | self.light | rs
        self.i2c.writeto(self.address, bytes([out | _ENABLE]))
        self.i2c.writeto(self.address, bytes([out]))

    def _send(self, value, rs=0):
        self._write4(value, rs)
        self._write4(value << 4, rs)

    def init(self):
        # The official wake-up sequence. Safe to run again after a power dip.
        time.sleep_ms(50)
        for _ in range(3):
            self._write4(0x30, 0)
            time.sleep_ms(5)
        self._write4(0x20, 0)  # switch to 4-bit mode
        self._send(0x28)       # 2 rows, 5x8 font
        self._send(0x0C)       # display on, no cursor
        self._send(0x06)       # move right after each character
        self.clear()

    def clear(self):
        self._send(0x01)
        time.sleep_ms(2)

    def backlight(self, on):
        self.light = _BACKLIGHT if on else 0
        self.i2c.writeto(self.address, bytes([self.light]))

    def move_to(self, column, row):
        self._send(0x80 | (column + (0x40 if row else 0)))

    def print(self, text):
        for ch in text:
            code = ord(ch)
            self._send(code if code < 128 else ord("?"), _RS)  # the LCD has no emoji
