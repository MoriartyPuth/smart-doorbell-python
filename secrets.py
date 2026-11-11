# Fill in your own values, then upload this file to the board with the others.
# Do not push this file to GitHub after putting real passwords and tokens in it.

# ---- WiFi (the ESP32 only supports 2.4 GHz networks) ----
WIFI_SSID = "your-wifi-name"
WIFI_PASSWORD = "your-wifi-password"

# ---- Telegram ----
# Token: create a bot with @BotFather.
# Chat ID: message @userinfobot (personal chat) or add the bot to a group
# and use the group's ID (starts with a minus sign). Only this chat can
# control the door.
TELEGRAM_BOT_TOKEN = "123456789:replace-me"
TELEGRAM_CHAT_ID = "123456789"

# ---- Blynk (set USE_BLYNK to True once the template is created) ----
USE_BLYNK = False
BLYNK_AUTH_TOKEN = "replace-me"
BLYNK_SERVER = "blynk.cloud"   # your region's server, e.g. "sgp1.blynk.cloud"

# ---- Web control panel (http://<main-board-ip>/) ----
# Anyone who knows these can unlock the door from the same WiFi. Change the password.
WEB_USER = "admin"
WEB_PASSWORD = "change-me"

# ---- Misc ----
TZ_OFFSET_HOURS = 7             # local time = UTC + this
CAM_HOSTNAME = "doorbell-cam"   # the ESP32-CAM announces itself as <name>.local
# If the main board cannot find the camera automatically, set its address here:
CAM_STATIC_IP = None            # e.g. "192.168.1.50"
