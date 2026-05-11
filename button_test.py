"""
button_test.py
--------------
Prints the raw GPIO state of pin 18 every 0.2s so you can
see exactly what the pin reads at rest and when pressed.

Run with:  python button_test.py
Exit with: Ctrl+C
"""

import RPi.GPIO as GPIO
import time

BUTTON_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN)   # No pull resistor — read raw state

print(f"Reading GPIO {BUTTON_PIN} — press and release the button. Ctrl+C to quit.\n")

try:
    last_state = None
    while True:
        state = GPIO.input(BUTTON_PIN)

        if state != last_state:
            label = "HIGH (1)" if state else "LOW  (0)"
            print(f"  State changed → {label}")
            last_state = state

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nDone.")

finally:
    GPIO.cleanup()
