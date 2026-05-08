"""
arrow_test.py
-------------
Live test for black-arrow detection on white paper.

Controls
--------
  Q  – quit
  S  – save a snapshot of the current frame to  arrow_snapshot.jpg
  T  – toggle the binary threshold view (debug)

Pass : coloured overlay appears around the arrow with a direction label.
Fail : no overlay, check lighting / THRESH_VALUE in arrow_detector.py.

Tips for a clean detection
--------------------------
• Draw a solid black arrow on plain white paper (no shadows).
• Fill the arrowhead completely – open outlines confuse the contour.
• Hold the paper flat under even light; avoid strong directional shadows.
• If detection is flaky, tweak  THRESH_VALUE / DEFECT_DEPTH_PX
  at the top of arrow_detector.py.
"""

import cv2
from arrow_detector import detect_arrows, draw_arrows


print("=" * 55)
print("Arrow Detection Test")
print("  Q = quit   S = save snapshot   T = toggle threshold view")
print("=" * 55)

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("\n[ERROR] Could not open camera on /dev/video0")
    print("  Fix: run camera_setup.sh, reboot, then retry.")
    raise SystemExit(1)

ret, probe = camera.read()
if not ret:
    print("\n[ERROR] Camera opened but could not read a frame.")
    raise SystemExit(1)

h, w = probe.shape[:2]
print(f"Camera ready  –  {w}×{h} px\n")

cv2.namedWindow("Arrow Detection",  cv2.WINDOW_NORMAL)
cv2.namedWindow("Threshold (debug)", cv2.WINDOW_NORMAL)

show_thresh = False
last_directions = []

while True:
    ret, frame = camera.read()
    if not ret:
        print("[WARNING] Dropped frame – retrying …")
        continue

    # ── Detect ────────────────────────────────────────────────────────────
    arrows = detect_arrows(frame)
    output = draw_arrows(frame, arrows)

    # ── Console feedback (only when result changes) ────────────────────
    current_dirs = [a["direction"] for a in arrows]
    if current_dirs != last_directions:
        if arrows:
            for a in arrows:
                print(f"  Arrow detected  →  {a['direction']:5s}  "
                      f"(angle {a['angle_deg']:+.1f}°,  area {a['area']:.0f} px²)")
        else:
            print("  No arrow detected.")
        last_directions = current_dirs

    # ── Status overlay ────────────────────────────────────────────────────
    status = f"Arrows: {len(arrows)}"
    cv2.putText(
        output, status, (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 1.0,
        (0, 255, 0) if arrows else (0, 0, 200),
        2, cv2.LINE_AA,
    )

    cv2.imshow("Arrow Detection", output)

    # ── Optional threshold view ───────────────────────────────────────────
    if show_thresh:
        import numpy as np, cv2 as _cv2
        gray = _cv2.cvtColor(frame, _cv2.COLOR_BGR2GRAY)
        blur = _cv2.GaussianBlur(gray, (5, 5), 0)
        _, thr = _cv2.threshold(blur, 100, 255, _cv2.THRESH_BINARY_INV)
        cv2.imshow("Threshold (debug)", thr)

    # ── Key handling ──────────────────────────────────────────────────────
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        print("\nQuitting.")
        break

    elif key == ord("s"):
        fname = "arrow_snapshot.jpg"
        cv2.imwrite(fname, output)
        print(f"  Snapshot saved → {fname}")

    elif key == ord("t"):
        show_thresh = not show_thresh
        if not show_thresh:
            cv2.destroyWindow("Threshold (debug)")
        print(f"  Threshold view {'ON' if show_thresh else 'OFF'}")


camera.release()
cv2.destroyAllWindows()
print("Arrow test complete.")
