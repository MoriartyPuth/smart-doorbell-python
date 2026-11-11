# Things the board drives directly: RGB LED ring, buzzer and the servo latch.

import time

import asyncio
import neopixel
from machine import PWM, Pin

import config
import pins

OFF, RED, GREEN, BLUE = 0, 1, 2, 3

_ring = None
_buzzer = None
_latch = None
_angle = None      # None = latch position unknown (just powered on)

# What the ring should show. set_led() only changes these two values; led_task()
# below does the drawing, so the pulse keeps going on its own.
_colour = OFF
_pulse = False

# ---------------------------------------------------------------- LED ring


def _pulse_level():
    # Brightness 0-255 for a slow fade in and out (one cycle per LED_PULSE_MS).
    t = time.ticks_ms() % config.LED_PULSE_MS
    half = config.LED_PULSE_MS // 2
    ramp = t if t < half else config.LED_PULSE_MS - t  # 0 -> half -> 0
    return 25 + (230 * ramp) // half                    # never fully dark


def _draw_ring():
    level = _pulse_level() if _pulse else 255
    level = level * pins.LED_BRIGHTNESS // 255
    rgb = (0, 0, 0)
    if _colour == RED:
        rgb = (level, 0, 0)
    elif _colour == GREEN:
        rgb = (0, level, 0)
    elif _colour == BLUE:
        rgb = (0, 0, level)
    _ring.fill(rgb)
    _ring.write()


async def led_task():
    """Runs forever in the background and redraws the ring about 30 times a second.
    The pulse pauses for a moment while the board waits on Telegram; that is normal."""
    while True:
        _draw_ring()
        await asyncio.sleep_ms(33)


def set_led(colour, pulse=False):
    """Lights the whole ring in one colour. pulse=True fades it in and out."""
    global _colour, _pulse
    _colour = colour
    _pulse = pulse

# ---------------------------------------------------------------- buzzer


def _beep(frequency_hz, duration_ms):
    # A tone works with both kinds of buzzer: a passive one needs it,
    # an active one just sounds a little rougher.
    _buzzer.freq(frequency_hz)
    _buzzer.duty_u16(32768)
    time.sleep_ms(duration_ms)
    _buzzer.duty_u16(0)  # silence


def chime():
    """'Ding-dong', takes about 0.7 seconds."""
    _beep(config.BUZZER_DING_HZ, 250)
    time.sleep_ms(80)
    _beep(config.BUZZER_DONG_HZ, 400)

# ---------------------------------------------------------------- latch


def _write_angle(angle):
    # SG90: 0.5 ms pulse = 0 degrees, 2.4 ms pulse = 180 degrees.
    _latch.duty_ns(500000 + angle * 1900000 // 180)


def move_latch(locked):
    global _angle
    target = pins.SERVO_LOCKED_ANGLE if locked else pins.SERVO_UNLOCKED_ANGLE
    # Move one degree at a time. A servo that jumps at full speed pulls enough
    # current to dip the 5V line and reset the ESP32 ("brownout").
    while _angle is not None and _angle != target:
        _angle += 1 if target > _angle else -1
        _write_angle(_angle)
        time.sleep_ms(config.SERVO_STEP_MS)
    _angle = target
    _write_angle(_angle)
    print("[LATCH]", "locked" if locked else "unlocked")

# ---------------------------------------------------------------- start-up


def begin():
    """Starts with the latch locked and the LEDs off. Call led_task() afterwards."""
    global _ring, _buzzer, _latch
    _ring = neopixel.NeoPixel(Pin(pins.PIN_LED), pins.LED_COUNT)
    _draw_ring()
    _latch = PWM(Pin(pins.PIN_SERVO), freq=50)
    move_latch(True)
    _buzzer = PWM(Pin(pins.PIN_BUZZER), freq=config.BUZZER_DING_HZ, duty_u16=0)
