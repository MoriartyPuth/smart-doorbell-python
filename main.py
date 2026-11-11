# Smart doorbell - main ESP32 (MicroPython). Runs by itself when the board powers on.
#
# Where things live:
#   sensors      IR "bell" sensor and PIR motion sensor
#   outputs      RGB LED ring, buzzer, servo latch
#   screen       visitor display (16x2 LCD or OLED)
#   wifi         WiFi and clock
#   camera_link  asks the ESP32-CAM for photos
#   door         what happens on ring / lock / unlock / mute
#   telegram     bot commands and messages
#   dashboard    Blynk
#   bridge/      web server: serves the web app (webapp/ folder) and its API
# Pins are in pins.py, timings in config.py, passwords in secrets.py.

import machine

import config

# The servo makes the supply voltage dip when it moves, and the ESP32's
# "brownout detector" answers a dip by rebooting. Turning the detector off
# lets the board ride through short dips. The proper fix is in hardware:
# a 470-1000 uF capacitor across the servo's power pins, or a separate 5V supply.
if config.DISABLE_BROWNOUT_RESET:
    machine.mem32[0x3FF480D4] = 0  # RTC_CNTL_BROWN_OUT_REG on the ESP32

import time

import asyncio

import camera_link
import dashboard
import door
import outputs
import screen
import sensors
import telegram
import wifi
from bridge import web_bridge

_last_pir_prompt = None


def greet_on_motion():
    # Someone walks up: wake the display with a hint.
    global _last_pir_prompt
    if screen.is_on() or not sensors.motion_detected():
        return
    now = time.ticks_ms()
    if _last_pir_prompt is not None and \
            time.ticks_diff(now, _last_pir_prompt) < config.PIR_PROMPT_COOLDOWN_MS:
        return
    _last_pir_prompt = now
    screen.show("Hello!", "Wave to ring", config.PIR_PROMPT_MS)


async def main():
    outputs.begin()  # latch starts locked
    asyncio.create_task(outputs.led_task())
    screen.begin()
    screen.set_idle("Smart Doorbell", "Wave to ring")  # shown whenever nothing else is
    door.begin()

    screen.show("Starting", "WiFi...", 60000)
    wifi.begin()
    telegram.begin()
    dashboard.begin()
    await web_bridge.start()
    sensors.begin()

    telegram.notify("🚪 Doorbell online. Send /status or /help.\n"
                    "Control panel: http://%s/" % wifi.ip())
    screen.show("Ready", "Wave to ring", 5000)
    print("[READY] type r and press Enter in the Shell to simulate a ring")

    while True:
        if sensors.bell_triggered():
            door.ring()
        greet_on_motion()

        door.tick()
        screen.tick()
        telegram.tick()
        dashboard.tick()
        camera_link.tick()
        await asyncio.sleep_ms(20)  # lets the web server and the LED ring run


asyncio.run(main())
