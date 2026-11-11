# Smart Doorbell (MicroPython version)

The main doorbell board written in **MicroPython**, so it can be edited and uploaded with
[Thonny](https://thonny.org/). It does the same job as `doorbell-main` in the C++ (PlatformIO)
repo and works with the same ESP32-CAM.

Flow: wave at the IR sensor → buzzer + pulsing blue LED + "Please wait" on the display → the
main board asks the camera for a photo → photo lands in Telegram → reply `/unlock` → the servo
opens the latch. The door can also be controlled from a web page served by the board, and
(optionally) from Blynk.

## Code map

Every file does one job and is under 200 lines. Printed log lines start with a tag
(`[TG]`, `[CAM]`, `[SCREEN]`, ...) that tells you which file printed them.

| File | Job | Log tag |
|---|---|---|
| `main.py` | starts everything and runs the main loop (runs by itself on power-up) | `[READY]` |
| `sensors.py` | IR bell sensor, PIR motion sensor | `[SENSOR]` |
| `outputs.py` | RGB LED ring, buzzer, servo latch | `[LATCH]` |
| `screen.py` | visitor display: 16x2 LCD or OLED, auto-detected | `[SCREEN]` |
| `wifi.py` | WiFi and clock | `[WiFi]` |
| `camera_link.py` | asks the ESP32-CAM for a photo | `[CAM]` |
| `door.py` | what happens on ring / lock / unlock / mute | `[DOOR]` |
| `telegram.py` | bot commands and messages | `[TG]` |
| `dashboard.py` | Blynk (off until `USE_BLYNK = True`) | `[BLYNK]` |
| `httpc.py` | outgoing web requests (used by Telegram, Blynk, camera) | `[HTTP]` |
| **`bridge/`** | **backend bridge**: the web server | `[WEB]` |
| `bridge/web_bridge.py` | login, `/api/...` routes, starts the server | |
| `bridge/http_server.py` | reads a request, sends a reply | |
| `bridge/web_files.py` | which web app file belongs to which address | |
| **`webapp/`** | **the web app itself**: `index.html`, `style.css`, `app.js` | |
| `lib/lcd_i2c.py` | driver for the 16x2 I2C LCD | |
| `pins.py` | wiring | |
| `config.py` | timings | |
| `secrets_example.py` | template for `secrets.py` (WiFi, Telegram, Blynk, web login) | |
| `hw_test.py` | hardware self-test, no WiFi needed | `[TEST]` `[IR]` `[I2C]` |

## 1. Put MicroPython on the ESP32 (once)

1. Install Thonny and plug in the ESP32 with a USB cable.
2. In Thonny: **Tools → Options → Interpreter**, choose **MicroPython (ESP32)** and the
   board's port, then click **Install or update MicroPython (esptool)**.
   Pick family **ESP32**, variant **Espressif • ESP32 / WROOM**, and install.
   (Use MicroPython **1.22 or newer**.)
3. Click **Stop/Restart** (red button). The Shell should show `>>>`.

## 2. Fill in your secrets

Copy `secrets_example.py` to `secrets.py` and fill it in:

- **WiFi**: must be a 2.4 GHz network (a phone hotspot works for demos).
- **Telegram token**: message `@BotFather`, send `/newbot`, copy the token.
- **Chat ID**: message `@userinfobot` to get your ID. For a team, create a group, add the bot,
  and use the group's ID (negative number). Only this chat can control the door.
  Send your bot any message once so it is allowed to message you.
- **Web login**: change `WEB_PASSWORD`; anyone on the WiFi who knows it can unlock the door.
- Leave `USE_BLYNK = False` until Telegram works.

`secrets.py` is git-ignored, so your tokens are never committed.

## 3. Upload the files

In Thonny: **View → Files**. In the top (computer) pane open this folder, select **everything
except** `README.md`, `.gitignore` and `secrets_example.py` — including the folders `bridge`,
`webapp` and `lib` — right-click → **Upload to /**.

The board should then have:

```
/main.py  /config.py  /pins.py  /secrets.py  /sensors.py  /outputs.py  /screen.py
/wifi.py  /httpc.py  /camera_link.py  /door.py  /telegram.py  /dashboard.py  /hw_test.py
/bridge/__init__.py  /bridge/web_bridge.py  /bridge/http_server.py  /bridge/web_files.py
/webapp/index.html  /webapp/style.css  /webapp/app.js
/lib/lcd_i2c.py
```

Press the board's **EN/RST** button (or Thonny's Stop/Restart). `main.py` runs and the Shell
shows the log. When it is ready it sends "Doorbell online" to Telegram with the web link.

- **Simulate a visitor** without the sensor: click in the Shell, type `r`, press Enter.
- **Stop the program** to edit files: press Thonny's red Stop button.
- After changing a file, upload it again (or open it from the board and save with Ctrl+S).

## 4. Hardware self-test (no WiFi)

Open `hw_test.py` in Thonny and press **Run** (F5). It cycles the LED colours, chimes the
buzzer, moves the servo and shows each step on the display, and prints a line when you wave
at the IR sensor. Press Stop to end it.

## 5. Wiring (main ESP32)

Defaults live in `pins.py`; change them there if the build differs.

| Part | Signal pin | Power | Notes |
|---|---|---|---|
| IR sensor (OUT) | GPIO 27 | 3.3V, GND | set `IR_ACTIVE_LOW = False` if the module outputs high on detect |
| PIR sensor (OUT) | not fitted | 5V, GND | set `PIN_PIR` (e.g. 33) if you add one |
| Buzzer | GPIO 26 | GND | active or passive |
| WS2812 LED ring (DIN) | GPIO 23 | 5V (VIN), GND | `LED_COUNT` in `pins.py` |
| Servo SG90 (signal) | GPIO 13 | 5V (VIN), GND | add a 470-1000 µF capacitor across its power pins |
| 16x2 I2C LCD | SDA 21, SCL 22 | **5V**, GND | address 0x27 (or 0x3F); turn the contrast screw if blank |

The ESP32 only joins **2.4 GHz** WiFi.

**OLED instead of an LCD?** It is detected automatically, but needs the `ssd1306` driver:
in Thonny, **Tools → Manage packages**, search `ssd1306`, install.

## 6. Telegram commands

| Command | Does |
|---|---|
| `/photo` | take a snapshot now |
| `/unlock` / `/lock` | open / close the latch |
| `/msg <text>` | show a message to the visitor |
| `/mute` | toggle the buzzer |
| `/status` | door, buzzer, visitor count, camera, WiFi |

## 7. Web control panel

Open `http://<board-ip>/` (the link is in the "Doorbell online" message) and log in with
`WEB_USER` / `WEB_PASSWORD`. It shows the door state, visitors and the live camera, and has
buttons for lock, unlock, mute, photo and a message for the visitor.

## 8. Camera board

The ESP32-CAM keeps its C++ firmware (`doorbell-cam` in the PlatformIO repo); MicroPython's
standard build has no camera driver. The main board finds it as `doorbell-cam.local`. If it
says "camera offline", set `CAM_STATIC_IP` in `secrets.py` to the camera's IP address.

## 9. Blynk (optional)

Create a template with datastreams **V0** visitors (integer), **V1** last visit (string),
**V2** lock (integer 0/1, switch), **V3** mute (integer 0/1, switch). Put the device's auth
token in `secrets.py`, set `BLYNK_SERVER` to your region's server, and `USE_BLYNK = True`.
The board checks the switches every 5 seconds (`BLYNK_POLL_MS` in `config.py`).

## Troubleshooting

| You see | Try |
|---|---|
| `[WiFi] connecting.....` forever | wrong name/password, or a 5 GHz network |
| `[TG] ... failed (401)` | wrong bot token |
| `[TG] message NOT sent` | wrong chat ID, or you never messaged the bot |
| `[SCREEN] no display found` | check SDA/SCL, 5V power; run `hw_test.py` to list I2C devices |
| LCD lights up but shows nothing | turn the contrast screw on its back |
| Board resets when the servo moves | add the capacitor, or power the servo separately |
| `ImportError: no module named 'secrets'` | `secrets.py` was not uploaded |
| `OSError: [Errno 12] ENOMEM` | press Stop/Restart; too many browser tabs open on the panel |
