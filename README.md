# Smart Doorbell (MicroPython)

Code for the main doorbell board (ESP32), to be run with [Thonny](https://thonny.org/).

Wave at the IR sensor → buzzer, blue LED and "Please wait" on the display → the camera's photo
goes to Telegram → send `/unlock` → the servo opens the latch. The door can also be controlled
from a web page served by the board.

## How to run it

1. **Put MicroPython on the ESP32 (once).** Plug in the board. In Thonny, go to **Tools →
   Options → Interpreter**, choose **MicroPython (ESP32)** and the board's port, then click
   **Install or update MicroPython**. Pick **ESP32 / WROOM** (version 1.22 or newer).
2. **Fill in `secrets.py`**: WiFi name and password (2.4 GHz only), Telegram bot token and
   chat ID, and a web password.
3. **Upload everything.** In Thonny, open **View → Files**, open this folder in the top pane,
   select all the files and folders, right-click → **Upload to /**.
4. **Run it.** Press Thonny's red **Stop/Restart** button. The board runs `main.py` and
   prints its progress in the Shell. From then on it also starts by itself whenever it
   is powered on.

To fake a visitor, type `r` in the Shell and press Enter. To change something, press Stop,
edit the file, save it to the board (Ctrl+S), then press Stop/Restart.

## Telegram commands

`/photo` snapshot · `/unlock` · `/lock` · `/msg <text>` show text to the visitor ·
`/mute` toggle the buzzer · `/status`

The web control panel is at `http://<board-ip>/` (the link is sent to Telegram when the board
starts). Log in with `WEB_USER` / `WEB_PASSWORD` from `secrets.py`.

## Folders

- `main.py` starts everything. Each other `.py` file does one job (sensors, outputs, screen,
  wifi, door, telegram, ...).
- `webapp/` is the web page.
- `bridge/` is the backend web server that serves the page and its `/api/...` buttons.
- `pins.py` has the wiring and `config.py` the timings.

## Wiring

| Part | Pin | Power |
|---|---|---|
| IR sensor OUT | GPIO 27 | 3.3V |
| Buzzer | GPIO 26 | GND |
| WS2812 LED ring DIN | GPIO 23 | 5V |
| Servo signal | GPIO 13 | 5V |
| 16x2 I2C LCD | SDA 21, SCL 22 | 5V |

If the LCD lights up but shows nothing, turn the contrast screw on its back. The camera
board (ESP32-CAM) uses its own C++ code; set `CAM_STATIC_IP` in `secrets.py` if the main
board says "camera offline".
