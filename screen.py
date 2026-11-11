# The visitor's display. Works with either a 16x2 character LCD with an I2C
# backpack or a 128x64 OLED (SSD1306); it detects which one is wired.
# Everything shown is also printed, so the code can be tested with no display.

import time

from machine import I2C, Pin

import pins
from lcd_i2c import LcdI2c

_lcd = None
_oled = None
_on = False
_shown_at = 0
_show_for = 0
_idle_title = ""   # "" = blank the display when idle
_idle_body = ""


def _wrap(text, width, max_lines):
    # Splits text into lines of at most `width` characters, breaking at spaces where possible.
    lines = []
    rest = text.strip()
    while rest and len(lines) < max_lines:
        if len(rest) <= width:
            lines.append(rest)
            break
        cut = rest.rfind(" ", 0, width + 1)
        if cut <= 0:
            cut = width  # one very long word: cut it
        lines.append(rest[:cut])
        rest = rest[cut:].strip()
    return lines


def _unstick():
    # A display that lost power can be left stuck half-way through a message,
    # and then ignores everything. Nine clock pulses set it free.
    Pin(pins.PIN_SDA, Pin.IN, Pin.PULL_UP)
    scl = Pin(pins.PIN_SCL, Pin.OPEN_DRAIN, value=1)
    for _ in range(9):
        scl.value(0)
        time.sleep_us(500)
        scl.value(1)
        time.sleep_us(500)


def begin():
    global _lcd, _oled
    _unstick()
    i2c = I2C(0, sda=Pin(pins.PIN_SDA), scl=Pin(pins.PIN_SCL), freq=100000)
    found = i2c.scan()
    if pins.OLED_ADDR in found:
        try:
            import ssd1306
            _oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=pins.OLED_ADDR)
            print("[SCREEN] OLED found")
            return
        except ImportError:
            print("[SCREEN] OLED found, but the ssd1306 library is missing (see README)")
    for address in pins.LCD_ADDRS:
        if address in found:
            _lcd = LcdI2c(i2c, address)
            print("[SCREEN] 16x2 LCD found at 0x%02X" % address)
            return
    print("[SCREEN] no display found, continuing without it")


def _draw_oled(title, body):
    # Title, a line under it, then the body (16 characters per line).
    _oled.fill(0)
    top = 0
    if title:
        _oled.text(title[:16], 0, 0)
        _oled.hline(0, 10, 128, 1)
        top = 16
    for i, line in enumerate(_wrap(body, 16, (64 - top) // 10)):
        _oled.text(line, 0, top + i * 10)
    _oled.show()


def _draw_lcd(title, body):
    # Title + body if the body fits on one row; otherwise the body takes both rows.
    lines = _wrap(body, 16, 2) + ["", ""]
    fits_one_row = len(body) <= 16 and title
    # Set the LCD up again every time: a power dip (servo moving) can scramble it.
    _lcd.init()
    _lcd.backlight(True)
    _lcd.move_to(0, 0)
    _lcd.print(title[:16] if fits_one_row else lines[0])
    _lcd.move_to(0, 1)
    _lcd.print(body if fits_one_row else lines[1])


def _draw(title, body):
    try:
        if _oled:
            _draw_oled(title, body)
        if _lcd:
            _draw_lcd(title, body)
    except OSError as e:  # display unplugged or wiring loose: keep the doorbell running
        print("[SCREEN] display error:", e)


def show(title, body, for_ms):
    """Shows a title and body for for_ms, then goes back to the idle text.
    Pass "" as the title to show the body alone (at most 32 characters on the LCD)."""
    global _on, _shown_at, _show_for
    _on = True
    _shown_at = time.ticks_ms()
    _show_for = for_ms
    print("[SCREEN] %s | %s" % (title, body))
    _draw(title, body)


def is_on():
    """True while a show() message is up (the idle text does not count)."""
    return _on


def _draw_idle():
    if _idle_title:
        _draw(_idle_title, _idle_body)
    elif _oled:
        _oled.fill(0)
        _oled.show()
    elif _lcd:
        _lcd.clear()
        _lcd.backlight(False)


def set_idle(title, body):
    """Text to show whenever nothing else is on the display."""
    global _idle_title, _idle_body
    _idle_title = title
    _idle_body = body
    if not _on:
        _draw_idle()


def tick():
    """Call often: returns to the idle text when a message's time is up."""
    global _on
    if not _on or time.ticks_diff(time.ticks_ms(), _shown_at) < _show_for:
        return
    _on = False
    _draw_idle()
