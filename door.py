# The doorbell's behaviour: what happens on a ring, lock, unlock and mute.
# Telegram, Blynk and the web app all call these functions, so the logic lives in one place.

import time

import camera_link
import config
import dashboard
import outputs
import screen
import telegram
import wifi


class State:
    locked = True
    muted = False
    waiting = False        # a visitor rang and nobody has answered yet
    waiting_since = 0
    visitor_count = 0
    last_visit = "never"


state = State()
_last_ring = None
_boot_ms = time.ticks_ms()


def _update_led():
    # Pulsing blue = visitor waiting, red = locked, green = unlocked.
    if state.waiting:
        outputs.set_led(outputs.BLUE, pulse=True)
    elif state.locked:
        outputs.set_led(outputs.RED)
    else:
        outputs.set_led(outputs.GREEN)


def begin():
    _update_led()


def ring():
    """A visitor waved at the sensor."""
    global _last_ring
    now = time.ticks_ms()
    if _last_ring is not None and time.ticks_diff(now, _last_ring) < config.RING_COOLDOWN_MS:
        return  # same visitor waving again
    _last_ring = now

    state.visitor_count += 1
    state.last_visit = wifi.now_string()
    state.waiting = True
    state.waiting_since = now
    print("[DOOR] ring, visitor #%d" % state.visitor_count)

    _update_led()
    screen.show("Doorbell", "Please wait...", config.WAIT_SCREEN_MS)
    if not state.muted:
        outputs.chime()
    if not camera_link.request_photo("bell"):
        telegram.notify("🔔 Someone is at the door! (camera offline, no photo)")
    dashboard.push()


def set_locked(locked):
    state.locked = locked
    state.waiting = False
    outputs.move_latch(locked)
    _update_led()
    screen.show("Door", "Locked" if locked else "Unlocked. Come in!", config.DOOR_SCREEN_MS)
    dashboard.push()


def set_muted(muted):
    state.muted = muted
    print("[DOOR] buzzer", "muted" if muted else "on")
    dashboard.push()


def uptime_min():
    return time.ticks_diff(time.ticks_ms(), _boot_ms) // 60000


def status_text():
    """Multi-line summary for /status."""
    cam = camera_link.url()
    return "\n".join((
        "Door: " + ("locked 🔒" if state.locked else "unlocked 🔓"),
        "Buzzer: " + ("muted" if state.muted else "on"),
        "Visitors: %d" % state.visitor_count,
        "Last visit: " + state.last_visit,
        "Camera: " + (cam or "offline"),
        "WiFi: %d dBm" % wifi.rssi(),
        "Uptime: %d min" % uptime_min(),
    ))


def tick():
    """Call often: stops "waiting" if nobody answers in time."""
    if state.waiting and time.ticks_diff(time.ticks_ms(), state.waiting_since) > config.WAIT_SCREEN_MS:
        state.waiting = False
        _update_led()
