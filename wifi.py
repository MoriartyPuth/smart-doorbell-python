# WiFi connection and clock.

import time

import network
import ntptime

import secrets

_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

_wlan = network.WLAN(network.STA_IF)


def begin():
    """Blocks until WiFi is connected, then sets the clock from the internet."""
    try:
        network.hostname("doorbell-main")
    except (AttributeError, ValueError):
        pass  # older MicroPython: keeps its default name
    _wlan.active(True)
    _wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    print("[WiFi] connecting", end="")
    while not _wlan.isconnected():
        time.sleep_ms(500)
        print(".", end="")
    # Lower radio power: plenty for indoor use, and it leaves more current for
    # the servo so the board does not reset when the latch moves.
    try:
        _wlan.config(txpower=11)
    except (ValueError, OSError):
        pass
    print("\n[WiFi] connected, IP", ip())

    for _ in range(3):
        try:
            ntptime.settime()  # sets the clock to UTC
            print("[WiFi] clock set:", now_string())
            return
        except OSError:
            time.sleep_ms(1000)
    print("[WiFi] could not set the clock, times will show 'time unknown'")


def ip():
    return _wlan.ifconfig()[0]


def rssi():
    """Signal strength in dBm (closer to 0 is stronger)."""
    try:
        return _wlan.status("rssi")
    except (ValueError, OSError):
        return 0


def now_string():
    """Local time such as '10 Nov 14:32', or 'time unknown' before the clock is set."""
    t = time.localtime(time.time() + secrets.TZ_OFFSET_HOURS * 3600)
    if t[0] < 2024:
        return "time unknown"
    return "%02d %s %02d:%02d" % (t[2], _MONTHS[t[1] - 1], t[3], t[4])
