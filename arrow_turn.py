"""
arrow_turn.py
-------------
Opens the camera, looks for a LEFT or RIGHT arrow, then turns accordingly.
"""

import cv2
from arrow_detector import detect_arrows
from motor_control import MotorController
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, TURN_DURATION

MAX_ATTEMPTS = 100   # max frames to scan before giving up


def find_and_turn():
    mc = MotorController()
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("ERROR: Could not open camera.")
        mc.cleanup()
        return

    print("Searching for arrow...")

    try:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Failed to read frame.")
                break

            arrows = detect_arrows(frame)

            # Only care about LEFT / RIGHT
            lr_arrows = [a for a in arrows if a["direction"] in ("LEFT", "RIGHT")]

            if lr_arrows:
                # Use the largest arrow if more than one is detected
                arrow = max(lr_arrows, key=lambda a: a["area"])
                direction = arrow["direction"]
                print(f"Arrow detected: {direction}  (attempt {attempt})")

                if direction == "LEFT":
                    mc.turn_left(TURN_DURATION)
                else:
                    mc.turn_right(TURN_DURATION)

                print("Turn complete.")
                return

            print(f"  No arrow yet... ({attempt}/{MAX_ATTEMPTS})")

        print("No arrow detected within the attempt limit.")

    finally:
        cap.release()
        mc.cleanup()


if __name__ == "__main__":
    find_and_turn()
