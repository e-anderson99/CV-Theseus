"""
arrow_turn.py
-------------
Waits for a button press on GPIO 18, then looks for a LEFT or RIGHT arrow
and turns accordingly.
"""

import cv2
import RPi.GPIO as GPIO
from arrow_detector import detect_arrows
from motor_control import MotorController
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, TURN_DURATION, BUTTON_PIN

MAX_ATTEMPTS = 100


def find_and_turn(mc):
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("ERROR: Could not open camera.")
        cap.release()
        return

    print("Searching for arrow...")

    try:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Failed to read frame.")
                break

            arrows = detect_arrows(frame)
            lr_arrows = [a for a in arrows if a["direction"] in ("LEFT", "RIGHT")]

            if lr_arrows:
                arrow = max(lr_arrows, key=lambda a: a["area"])
                direction = arrow["direction"]
                print(f"Arrow detected: {direction}  (attempt {attempt})")

                if direction == "LEFT":
                    mc.turn_left(TURN_DURATION)
                else:
                    mc.turn_right(TURN_DURATION)

                print("Turn complete. Waiting for next button press...\n")
                return

            print(f"  No arrow yet... ({attempt}/{MAX_ATTEMPTS})")

        print("No arrow detected within the attempt limit.\n")

    finally:
        cap.release()


def main():
    # Button setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    mc = MotorController()

    print("Ready. Press the button to scan for an arrow.")

    try:
        while True:
            # Wait for button press (LOW = pressed, since pull-up resistor)
            GPIO.wait_for_edge(BUTTON_PIN, GPIO.FALLING)
            print("Button pressed!")
            find_and_turn(mc)

    except KeyboardInterrupt:
        print("\nExiting.")

    finally:
        mc.cleanup()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
