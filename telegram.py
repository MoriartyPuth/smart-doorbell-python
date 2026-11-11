# Telegram bot: receives commands and sends text messages.
# (Photos are sent by the ESP32-CAM, not by this board.)

import json
import time

import camera_link
import config
import door
import httpc
import screen
import secrets

_API = "https://api.telegram.org/bot" + secrets.TELEGRAM_BOT_TOKEN + "/"
_next_update = 0   # Telegram's number for the first message we have not read yet
_last_poll = 0

HELP_TEXT = "\n".join((
    "Smart doorbell commands:",
    "/photo - take a snapshot now",
    "/unlock - open the latch",
    "/lock - close the latch",
    "/msg <text> - show a message to the visitor",
    "/mute - toggle the buzzer",
    "/status - door, buzzer, visitor count",
))

# The list Telegram shows when you type "/" or tap the Menu button.
COMMAND_MENU = [
    {"command": "photo", "description": "Take a snapshot now"},
    {"command": "unlock", "description": "Open the latch"},
    {"command": "lock", "description": "Close the latch"},
    {"command": "msg", "description": "Show a message to the visitor: /msg <text>"},
    {"command": "mute", "description": "Toggle the buzzer"},
    {"command": "status", "description": "Door, buzzer, visitor count"},
    {"command": "help", "description": "List the commands"},
]


def _call(method, data, timeout=10):
    """Calls one Telegram API method. Returns its result, or None if it failed."""
    code, text = httpc.post_json(_API + method, data, timeout)
    if code != 200:
        if code:
            print("[TG] %s failed (%d): %s" % (method, code, text[:120]))
        return None
    return json.loads(text).get("result")


def _get_updates():
    global _next_update
    updates = _call("getUpdates", {"offset": _next_update, "limit": 5, "timeout": 0,
                                   "allowed_updates": ["message"]}) or []
    if updates:
        _next_update = updates[-1]["update_id"] + 1
    return updates


def begin():
    """Call after WiFi is connected. Discards commands sent while the board was off."""
    if _call("setMyCommands", {"commands": COMMAND_MENU}) is not None:
        print("[TG] command menu registered")
    else:
        print("[TG] could not register the command menu (check the bot token)")
    # Throw away old commands, so an old /unlock does not open the door on power-up.
    while _get_updates():
        pass


def notify(text, chat_id=None):
    """Sends a text message to the owner's chat (or to chat_id)."""
    # Telegram sometimes drops the first try, so try twice.
    for attempt in (1, 2):
        if _call("sendMessage", {"chat_id": chat_id or secrets.TELEGRAM_CHAT_ID, "text": text}):
            return
        print("[TG] send failed (try %d of 2)" % attempt)
    print("[TG] message NOT sent (check token, chat ID and WiFi)")


def _run_command(cmd, arg):
    # cmd is lower-case without the "@botname" part, arg is the rest.
    if cmd == "/photo":
        if not camera_link.request_photo("manual"):
            notify("Camera is offline.")
    elif cmd == "/unlock":
        door.set_locked(False)
        notify("🔓 Door unlocked.")
    elif cmd == "/lock":
        door.set_locked(True)
        notify("🔒 Door locked.")
    elif cmd == "/msg":
        if not arg:
            notify("Usage: /msg <text>")
        else:
            screen.show("", arg, config.MSG_SCREEN_MS)  # the visitor sees only the text
            notify("Shown on the display.")
    elif cmd == "/mute":
        door.set_muted(not door.state.muted)
        notify("🔇 Buzzer muted." if door.state.muted else "🔔 Buzzer on.")
    elif cmd == "/status":
        notify(door.status_text())
    else:
        notify(HELP_TEXT)


def _handle_message(chat_id, text):
    print("[TG] from %s: %s" % (chat_id, text))
    if chat_id != str(secrets.TELEGRAM_CHAT_ID):
        notify("Not authorised.", chat_id)
        return
    # Split "/msg@botname hello there" into "/msg" and "hello there".
    cmd, _, arg = text.partition(" ")
    cmd = cmd.split("@")[0].lower()
    _run_command(cmd, arg.strip())


def tick():
    """Call often: checks for new commands every TELEGRAM_POLL_MS."""
    global _last_poll
    if time.ticks_diff(time.ticks_ms(), _last_poll) < config.TELEGRAM_POLL_MS:
        return
    updates = _get_updates()
    while updates:
        for update in updates:
            message = update.get("message") or {}
            if "text" in message:
                _handle_message(str(message["chat"]["id"]), message["text"])
        updates = _get_updates()
    _last_poll = time.ticks_ms()
