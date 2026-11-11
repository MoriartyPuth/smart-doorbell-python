# Backend bridge between the web app (webapp/ folder) and the doorbell.
#
# Addresses it answers (all need the login from secrets.py):
#   GET  /  /style.css  /app.js      the web app's files (see web_files.py)
#   GET  /api/status                 door state as JSON, read every 2 s by app.js
#   POST /api/lock  /api/unlock  /api/mute  /api/photo
#   POST /api/msg                    request body = text to show the visitor
#
# A button press is answered with "ok" straight away and carried out just
# after, so the browser never waits for the servo or for Telegram.

import json

import asyncio
import binascii

import camera_link
import config
import door
import screen
import secrets
import telegram
import wifi
from bridge import http_server as http
from bridge import web_files

MAX_MESSAGE_BYTES = 96

_expected_login = ""   # the "Authorization" header a logged-in browser sends


# ---- what each button does ----

def _lock(text):
    print("[WEB] lock")
    door.set_locked(True)
    telegram.notify("🔒 Door locked from the web app.")


def _unlock(text):
    print("[WEB] unlock")
    door.set_locked(False)
    telegram.notify("🔓 Door unlocked from the web app.")


def _mute(text):
    print("[WEB] toggle mute")
    door.set_muted(not door.state.muted)


def _photo(text):
    print("[WEB] photo")
    if not camera_link.request_photo("manual"):
        telegram.notify("Camera is offline.")


def _message(text):
    print("[WEB] message:", text)
    screen.show("", text, config.MSG_SCREEN_MS)  # the visitor sees only the text


ACTIONS = {"lock": _lock, "unlock": _unlock, "mute": _mute, "photo": _photo, "msg": _message}


# ---- answering the browser ----

def _status():
    s = door.state
    return {"locked": s.locked, "muted": s.muted, "waiting": s.waiting,
            "visitors": s.visitor_count, "lastVisit": s.last_visit,
            "camera": camera_link.known_url(), "rssi": wifi.rssi(),
            "uptimeMin": door.uptime_min()}


async def _answer(req, writer):
    """Sends the reply. Returns a function to run afterwards (a button press), or None."""
    if req.headers.get("authorization") != _expected_login:
        await http.send(writer, "401 Unauthorized", "text/plain", "Login required",
                        'WWW-Authenticate: Basic realm="Smart Doorbell"\r\n')
        return None

    if req.method == "GET" and req.path == "/api/status":
        await http.send(writer, "200 OK", "application/json", json.dumps(_status()))
        return None

    file = web_files.find(req.path) if req.method == "GET" else None
    if file:
        await http.send_file(writer, *file)
        return None

    name = req.path[len("/api/"):] if req.path.startswith("/api/") else ""
    if req.method == "POST" and name in ACTIONS:
        text = ""
        if name == "msg":  # the request body is the message text
            text = req.body.decode().strip()
            if req.too_big or not text or len(req.body) > MAX_MESSAGE_BYTES:
                await http.send(writer, "400 Bad Request", "text/plain",
                                "Message is empty or too long")
                return None
        await http.send(writer, "200 OK", "text/plain", "ok")
        return lambda: ACTIONS[name](text)

    await http.send(writer, "404 Not Found", "text/plain", "Not found")
    return None


async def _handle(reader, writer):
    # Runs once for every request a browser makes.
    action = None
    try:
        req = await http.read_request(reader)
        if req:
            action = await _answer(req, writer)
    except Exception as e:
        print("[WEB] request failed:", e)
    try:
        writer.close()
        await writer.wait_closed()
    except Exception:
        pass
    if action:
        action()


async def start():
    """Starts the web server in the background. Call after WiFi is connected."""
    global _expected_login
    login = ("%s:%s" % (secrets.WEB_USER, secrets.WEB_PASSWORD)).encode()
    _expected_login = "Basic " + binascii.b2a_base64(login).decode().strip()
    await asyncio.start_server(_handle, "0.0.0.0", 80)
    print("[WEB] control panel at http://%s/" % wifi.ip())
