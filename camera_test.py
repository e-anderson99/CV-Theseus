
"""
camera_test.py
--------------
Run this after camera_setup.sh + reboot to confirm the camera
is working before you run the full main.py.

Pass: shows a live window and prints frame size.
Fail: prints a clear error message with fix instructions.
"""

import cv2
import sys

print("Testing camera on /dev/video0 ...")

cap = (
    cv2.VideoCapture(0, cv2.CAP_V4L2)
    if sys.platform.startswith("linux")
    else cv2.VideoCapture(0)
)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("\n[FAIL] Camera not detected.")
    print("  1. Check the ribbon cable is seated firmly at BOTH ends.")
    print("  2. Make sure you ran:  bash camera_setup.sh  and rebooted.")
    print("  3. Run:  ls /dev/video*  — you should see /dev/video0")
    print("  4. Run:  v4l2-ctl --list-devices  to see what's connected.")
    sys.exit(1)

# Some V4L2 bridges return black frames until the pipeline warms up.
for _ in range(15):
    cap.read()

ret, frame = cap.read()
if not ret or frame is None:
    print("\n[FAIL] Camera opened but could not read a frame.")
    print("  Try:  libcamera-hello  in the terminal to check the camera works at OS level.")
    cap.release()
    sys.exit(1)

# All-black frames usually mean wrong /dev/video* node or a dead bridge; OpenCV may still say "opened".
mean_px = float(frame.mean())
if mean_px < 1.5:
    print("\n[WARN] First frames are nearly all black (mean pixel {:.1f}).".format(mean_px))
    print("  - Run:  libcamera-hello   — if preview is OK but OpenCV is black, try VideoCapture(1) above.")
    print("  - Run:  v4l2-ctl --list-devices   — pick the node that corresponds to your CSI camera.")
    print("  - Check lens cover, lighting, and ribbon cable seating at both ends.")

h, w = frame.shape[:2]
print(f"\n[PASS] Camera working!  Frame size: {w}x{h}")
print("Showing live feed — press Q to quit.\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("Camera Test — press Q to quit", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("Camera test complete.")
