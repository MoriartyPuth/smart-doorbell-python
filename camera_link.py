# Talks to the ESP32-CAM over WiFi. The camera board finds itself on the
# network as doorbell-cam.local (or use CAM_STATIC_IP in secrets.py).

import socket
import time

import config
import httpc
import secrets

_cam_ip = None        # None until the camera is found
_last_search = 0


def _find_camera():
    """Looks for the camera on the network. Takes a few seconds if it is not there."""
    global _cam_ip, _last_search
    if _cam_ip:
        return True
    _last_search = time.ticks_ms()
    if getattr(secrets, "CAM_STATIC_IP", None):
        _cam_ip = secrets.CAM_STATIC_IP
    else:
        try:
            _cam_ip = socket.getaddrinfo(secrets.CAM_HOSTNAME + ".local", 80)[0][-1][0]
        except (OSError, IndexError):
            _cam_ip = None
    if not _cam_ip:
        print("[CAM] not found on the network")
        return False
    print("[CAM] found at", _cam_ip)
    return True


def request_photo(reason):
    """Asks the camera to take a photo and send it to Telegram.
    reason is "bell" (a visitor rang) or "manual" (the /photo command).
    Returns False if the camera cannot be reached."""
    global _cam_ip
    if not _find_camera():
        return False
    code, _ = httpc.get("http://%s/snap?reason=%s" % (_cam_ip, reason), timeout=5)
    if code != 200:
        print("[CAM] /snap failed (%d)" % code)
        _cam_ip = None  # look it up again next time, its IP may have changed
        return False
    print("[CAM] photo requested (%s)" % reason)
    return True


def url():
    """Address of the live-view page, or "" if the camera cannot be found (may search)."""
    _find_camera()
    return known_url()


def known_url():
    """Same as url(), but never searches."""
    return "http://%s/" % _cam_ip if _cam_ip else ""


def tick():
    """Call often: while the camera is unknown, searches for it now and then."""
    if _cam_ip or time.ticks_diff(time.ticks_ms(), _last_search) < config.CAMERA_SEARCH_EVERY_MS:
        return
    _find_camera()
