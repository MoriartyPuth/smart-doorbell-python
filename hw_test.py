# Hardware self-test for the main ESP32. Needs no WiFi and no secrets.
# Open this file in Thonny and press Run (F5). Press Stop to end it.
#
# It repeats this cycle so each part can be checked by eye and ear:
#   LED ring red -> green -> blue -> pulsing blue, buzzer chime, servo unlock -> lock,
#   with the step name shown on the display.
# It also prints a line whenever the IR or PIR sensor changes.

import time

import asyncio
from machine import I2C, Pin

import outputs
import pins
import screen
import sensors

_last_ir = None
_last_pir = None


def scan_i2c():
    # Lists every I2C device that answers, so a wrong display address is easy to spot.
    found = I2C(0, sda=Pin(pins.PIN_SDA), scl=Pin(pins.PIN_SCL)).scan()
    for address in found:
        print("[I2C] device at 0x%02X" % address)
    if not found:
        print("[I2C] no devices found (check display wiring: SDA 21, SCL 22, 5V)")


async def watch_sensors(ms):
    # Waits while reporting sensor changes, so waving at the IR sensor shows up at once.
    global _last_ir, _last_pir
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < ms:
        ir = sensors.ir_level()
        pir = 1 if sensors.motion_detected() else 0
        if ir != _last_ir:
            print("[IR] pin reads", ir)
            _last_ir = ir
        if pir != _last_pir and pins.PIN_PIR is not None:
            print("[PIR] pin reads", pir)
            _last_pir = pir
        await asyncio.sleep_ms(20)


async def step(name, ms):
    print("[TEST]", name)
    screen.show("Self-test", name, ms)
    await watch_sensors(ms)


async def main():
    scan_i2c()
    outputs.begin()
    asyncio.create_task(outputs.led_task())
    screen.begin()
    sensors.begin()
    while True:
        outputs.set_led(outputs.RED)
        await step("LED red", 1500)
        outputs.set_led(outputs.GREEN)
        await step("LED green", 1500)
        outputs.set_led(outputs.BLUE)
        await step("LED blue", 1500)
        outputs.set_led(outputs.BLUE, pulse=True)
        await step("LED pulse", 3000)
        outputs.set_led(outputs.OFF)
        await step("Buzzer", 200)
        outputs.chime()
        await step("Servo unlock", 200)
        outputs.move_latch(False)
        await step("Servo lock", 1000)
        outputs.move_latch(True)
        await step("Wave at IR", 3000)


asyncio.run(main())
