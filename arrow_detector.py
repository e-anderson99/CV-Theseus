"""
arrow_detector.py
-----------------
Detects black arrows drawn on white paper using contour analysis
and convexity defects.
 
Usage:
    from arrow_detector import detect_arrows, draw_arrows
 
Returns a list of arrow dicts:
    {
        "contour":   np.ndarray,   # raw contour points
        "tip":       (x, y),       # arrow tip point
        "centroid":  (x, y),       # shape centroid
        "direction": str,          # "UP" | "DOWN" | "LEFT" | "RIGHT"
        "angle_deg": float,        # raw angle in degrees
        "area":      float,        # contour area in px²
    }
"""
 
import cv2
import numpy as np
 
 
# ── Tuning knobs ──────────────────────────────────────────────────────────────
 
# Minimum contour area to consider (filters out noise/smudges)
MIN_AREA = 1_500
 
# Convexity-defect depth threshold in pixels.
# Larger → only deep "armpit" notches count; smaller → more sensitive.
DEFECT_DEPTH_PX = 12
 
# How many significant defects we expect for an arrow shape.
# A clean drawn arrow has exactly 2 (the two armpit notches at the head).
EXPECTED_DEFECTS = 2
 
# Binary threshold for separating black ink from white paper (0-255).
# Decrease if the arrow looks grey; increase if background is noisy.
THRESH_VALUE = 100
 
 
# ── Core helpers ──────────────────────────────────────────────────────────────
 
def _preprocess(frame: np.ndarray) -> np.ndarray:
    """Convert frame to a binary mask where black ink = white (255)."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # THRESH_BINARY_INV: dark pixels → 255 (foreground)
    _, thresh = cv2.threshold(blur, THRESH_VALUE, 255, cv2.THRESH_BINARY_INV)
    # Small morphological close to fill pen gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    return thresh
 
 
def _angle_to_direction(angle_deg: float) -> str:
    """Convert a heading angle (degrees, standard math convention) to a
    cardinal direction string."""
    # Normalise to [0, 360)
    a = angle_deg % 360
    if 315 <= a or a < 45:
        return "RIGHT"
    elif 45 <= a < 135:
        return "UP"
    elif 135 <= a < 225:
        return "LEFT"
    else:
        return "DOWN"
 
 
# ── Public API ────────────────────────────────────────────────────────────────
 
def detect_arrows(frame: np.ndarray) -> list[dict]:
    """
    Analyse *frame* and return a list of detected arrow dicts.
 
    Parameters
    ----------
    frame : np.ndarray
        BGR image (e.g. from cv2.VideoCapture.read()).
 
    Returns
    -------
    list[dict]  – may be empty if no arrows found.
    """
    thresh = _preprocess(frame)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
 
    arrows = []
 
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_AREA:
            continue
 
        # Need enough points for convexity analysis
        if len(cnt) < 5:
            continue
 
        hull_idx = cv2.convexHull(cnt, returnPoints=False)
        if len(hull_idx) < 3:
            continue
 
        try:
            defects = cv2.convexityDefects(cnt, hull_idx)
        except cv2.error:
            continue
 
        if defects is None:
            continue
 
        # ── Count significant defects ──────────────────────────────────────
        sig_defect_pts = []
        for i in range(defects.shape[0]):
            _s, _e, far_idx, depth_fixed = defects[i, 0]
            depth_px = depth_fixed / 256.0
            if depth_px > DEFECT_DEPTH_PX:
                sig_defect_pts.append(tuple(cnt[far_idx][0]))
 
        if len(sig_defect_pts) != EXPECTED_DEFECTS:
            continue
 
        # ── Centroid ───────────────────────────────────────────────────────
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        centroid = (cx, cy)
 
        # ── Arrow tip = hull point farthest from centroid ──────────────────
        hull_pts = cv2.convexHull(cnt, returnPoints=True).reshape(-1, 2)
        dists = np.linalg.norm(hull_pts - np.array([cx, cy]), axis=1)
        tip = tuple(hull_pts[int(np.argmax(dists))].tolist())
 
        # ── Direction ──────────────────────────────────────────────────────
        dx = tip[0] - cx
        dy = tip[1] - cy           # screen y increases downward
        angle_deg = float(np.degrees(np.arctan2(-dy, dx)))  # flip y for math convention
        direction = _angle_to_direction(angle_deg)
 
        arrows.append(
            dict(
                contour=cnt,
                tip=tip,
                centroid=centroid,
                direction=direction,
                angle_deg=angle_deg,
                area=area,
            )
        )
 
    return arrows
 
 
def draw_arrows(frame: np.ndarray, arrows: list[dict]) -> np.ndarray:
    """
    Draw detection overlays on *frame* (in-place copy).
 
    Overlays drawn
    --------------
    • Contour outline  – green
    • Arrow tip dot    – red
    • Centroid dot     – blue
    • Direction vector – yellow line from centroid → tip
    • Direction label  – white text near tip
    """
    out = frame.copy()
 
    for arrow in arrows:
        cnt       = arrow["contour"]
        tip       = arrow["tip"]
        centroid  = arrow["centroid"]
        direction = arrow["direction"]
 
        # Contour
        cv2.drawContours(out, [cnt], -1, (0, 220, 0), 2)
 
        # Direction line
        cv2.arrowedLine(out, centroid, tip, (0, 220, 220), 3, tipLength=0.3)
 
        # Key points
        cv2.circle(out, tip,      8, (0,   0, 255), -1)   # red  – tip
        cv2.circle(out, centroid, 6, (255, 0,   0), -1)   # blue – centroid
 
        # Label
        lx = tip[0] + 12
        ly = tip[1] - 12
        cv2.putText(
            out, direction,
            (lx, ly),
            cv2.FONT_HERSHEY_SIMPLEX, 0.9,
            (255, 255, 255), 2, cv2.LINE_AA,
        )
 
    return out
