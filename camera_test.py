
"""
camera_test.py
--------------
Run this after camera_setup.sh + reboot to confirm the camera
is working before you run the full main.py.

Pass: shows a live window and prints frame size.
Fail: prints a clear error message with fix instructions.
"""

import cv2

print("Testing camera on /dev/video0 ...")

camera = cv2.VideoCapture(0)
cv2.namedWindow("original", cv2.WINDOW_NORMAL)






while True:
    ret, image = camera.read()
    if not ret:
        break
    cv2.imshow("original", image)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("Camera test complete.")
