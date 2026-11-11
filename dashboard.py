# Blynk dashboard, through Blynk's web API. Does nothing while USE_BLYNK is False.
#   V0 visitor count   V1 last visit time   V2 lock switch   V3 mute switch

import json
import time

import config
import door
import httpc
import secrets
import telegram

_last_poll = 0


def _url(action, query):
    return "https://%s/external/api/%s?token=%s&%s" % (
        secrets.BLYNK_SERVER, action, secrets.BLYNK_AUTH_TOKEN, query)


def _read_switches():
    """Reads V0, V2 and V3 from Blynk. Returns a dict like {"V0": 5, "V2": 1}, or None."""
    code, text = httpc.get(_url("get", "V0&V2&V3"))
    if code != 200:
        print("[BLYNK] read failed (%d)" % code)
        return None
    values = json.loads(text)
    return {pin: int(float(value)) for pin, value in values.items()}


def begin():
    if not secrets.USE_BLYNK:
        return
    values = _read_switches()
    if values and values.get("V0", 0) > door.state.visitor_count:
        door.state.visitor_count = values["V0"]  # restores the count after a reboot
        print("[BLYNK] visitor count restored:", door.state.visitor_count)
    push()


def push():
    """Sends the current door state to the dashboard."""
    if not secrets.USE_BLYNK:
        return
    s = door.state
    query = "V0=%d&V1=%s&V2=%d&V3=%d" % (
        s.visitor_count, httpc.quote(s.last_visit), int(s.locked), int(s.muted))
    code, _ = httpc.get(_url("batch/update", query))
    if code != 200:
        print("[BLYNK] update failed (%d)" % code)


def tick():
    """Call often: every BLYNK_POLL_MS, checks whether a switch was moved in the app."""
    global _last_poll
    if not secrets.USE_BLYNK:
        return
    if time.ticks_diff(time.ticks_ms(), _last_poll) < config.BLYNK_POLL_MS:
        return
    _last_poll = time.ticks_ms()
    values = _read_switches()
    if not values:
        return
    if "V2" in values and (values["V2"] == 1) != door.state.locked:
        door.set_locked(values["V2"] == 1)
        telegram.notify("🔒 Door locked from Blynk." if door.state.locked
                        else "🔓 Door unlocked from Blynk.")
    if "V3" in values and (values["V3"] == 1) != door.state.muted:
        door.set_muted(values["V3"] == 1)
