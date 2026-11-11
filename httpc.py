# Outgoing web requests (to Telegram, Blynk and the camera board).
# Every function returns (status_code, text); status 0 means no answer at all.

import json

try:
    import requests
except ImportError:            # older MicroPython firmware
    import urequests as requests


def _request(method, url, body=None, headers=None, timeout=10):
    try:
        try:
            reply = requests.request(method, url, data=body, headers=headers or {}, timeout=timeout)
        except TypeError:      # older firmware has no timeout option
            reply = requests.request(method, url, data=body, headers=headers or {})
    except Exception as e:     # no WiFi, server down, timeout...
        print("[HTTP] %s failed: %s" % (url.split("?")[0][:60], e))
        return 0, ""
    try:
        return reply.status_code, reply.text
    finally:
        reply.close()          # frees the memory straight away


def get(url, timeout=10):
    return _request("GET", url, timeout=timeout)


def post_json(url, data, timeout=10):
    # Sent as bytes so the length is right for emoji and other non-English text.
    body = json.dumps(data).encode()
    return _request("POST", url, body, {"Content-Type": "application/json"}, timeout)


def quote(text):
    """Makes text safe to put in a web address (spaces become %20 and so on)."""
    safe = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.~"
    out = ""
    for byte in str(text).encode():
        ch = chr(byte)
        out += ch if ch in safe else "%%%02X" % byte
    return out
