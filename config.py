# Timings for the main board, all in milliseconds. Tweak here.

RING_COOLDOWN_MS = 10000        # ignore repeat waves for this long
WAIT_SCREEN_MS = 30000          # how long "Please wait" stays up
MSG_SCREEN_MS = 20000           # how long a /msg stays up
DOOR_SCREEN_MS = 8000           # how long "Locked"/"Unlocked" stays up
PIR_PROMPT_MS = 10000           # how long the "Wave to ring" hint stays up
PIR_PROMPT_COOLDOWN_MS = 15000  # gap between two hints
TELEGRAM_POLL_MS = 2000         # how often to check for commands
BLYNK_POLL_MS = 5000            # how often to read the Blynk switches (only if USE_BLYNK)
SERVO_STEP_MS = 20              # pause per degree of servo travel (slower = gentler on power)
CAMERA_SEARCH_EVERY_MS = 60000  # how often to look for the camera while it is offline
LED_PULSE_MS = 1200             # one fade in + out of the "visitor waiting" alert

# Doorbell chime notes, in hertz (pitch).
BUZZER_DING_HZ = 2000
BUZZER_DONG_HZ = 1500

# True = do not reboot on short power dips (see main.py). Set to False once
# the servo has its own capacitor or power supply.
DISABLE_BROWNOUT_RESET = True
