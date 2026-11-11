# Wiring for the main ESP32 board (30-pin).
# HARDWARE TEAM: if you wire something differently, change it here only.

# Sensors
PIN_IR = 27            # IR obstacle sensor OUT (the "doorbell button")
IR_ACTIVE_LOW = True   # most IR modules pull OUT low when they see a hand
PIN_PIR = None         # PIR motion sensor OUT; None = not fitted. If you add one, use a free pin (e.g. 33)

# Outputs
PIN_BUZZER = 26        # buzzer, active or passive (driven with a tone)
PIN_LED = 23           # WS2812 RGB LED ring, DIN pin (power from VIN 5V)
LED_COUNT = 24         # LEDs on the ring; a number larger than the real ring is harmless
LED_BRIGHTNESS = 40    # 0-255; keep low, a full ring draws a lot of current
PIN_SERVO = 13         # SG90 servo signal (power from VIN 5V, not 3.3V)

# Display on I2C: a 16x2 LCD or a 128x64 OLED, detected automatically
PIN_SDA = 21
PIN_SCL = 22
OLED_ADDR = 0x3C          # SSD1306 OLED
LCD_ADDRS = (0x27, 0x3F)  # 16x2 LCD with I2C backpack (some use 0x3F)

# Servo positions in degrees
SERVO_LOCKED_ANGLE = 0
SERVO_UNLOCKED_ANGLE = 90
