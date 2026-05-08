"""
arrow_detector.py
-----------------
Detects an arrow in a frame and returns its direction.
Uses contour shape analysis + convexity defects.

Returns: "left", "right", "forward", "backward", or None
"""

import cv2
import numpy as np


class ArrowDetector:
    def __init__(self, debug=False):
        self.debug = debug

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def detect(self, frame):
        """
        Main entry point.
        Returns (direction, annotated_frame).
        direction is 'left' | 'right' | 'forward' | 'backward' | None
        """
        processed = self._preprocess(frame)
        contours  = self._find_contours(processed)
        direction = None

        for cnt in contours:
            direction = self._classify_arrow(cnt)
            if direction:
                if self.debug:
                    self._draw_debug(frame, cnt, direction)
                break   # take the largest valid arrow found

        return direction, frame

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _preprocess(self, frame):
        gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Adaptive threshold handles varying lighting conditions
        thresh  = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            blockSize=11, C=2
        )
        # Clean up noise
        kernel  = np.ones((3, 3), np.uint8)
        thresh  = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        return thresh

    def _find_contours(self, binary):
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        # Sort largest-first so we pick the dominant arrow
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        return contours

    def _classify_arrow(self, cnt):
        area = cv2.contourArea(cnt)
        if area < 1000:          # too small — skip noise
            return None

        # Approximate the contour to a polygon
        peri   = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

        # Arrows typically have 7-10 vertices
        if not (6 <= len(approx) <= 12):
            return None

        # Use convexity defects to find the arrow's "notch"
        hull      = cv2.convexHull(cnt, returnPoints=False)
        if len(hull) < 3:
            return None

        try:
            defects = cv2.convexityDefects(cnt, hull)
        except cv2.error:
            return None

        if defects is None:
            return None

        # Find the deepest defect — that's the arrow's tail notch
        max_depth   = 0
        notch_point = None
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            depth = d / 256.0
            if depth > max_depth:
                max_depth   = depth
                notch_point = tuple(cnt[f][0])

        if max_depth < 10:      # not deep enough to be an arrow
            return None

        # The arrowhead centroid sits opposite the notch
        M  = cv2.moments(cnt)
        if M["m00"] == 0:
            return None

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        # Vector from centroid → notch tells us direction arrow points
        dx = notch_point[0] - cx
        dy = notch_point[1] - cy     # positive = downward in image coords

        direction = self._vector_to_direction(dx, dy)
        return direction

    @staticmethod
    def _vector_to_direction(dx, dy):
        """
        Convert a 2-D vector to a cardinal direction.
        The notch-to-centroid vector points in the arrow direction.
        """
        angle = np.degrees(np.arctan2(-dy, dx))  # flip y for screen coords

        if   -45  <= angle <  45:   return "right"
        elif  45  <= angle < 135:   return "forward"
        elif angle >= 135 or angle < -135: return "left"
        else:                        return "backward"

    def _draw_debug(self, frame, cnt, direction):
        cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
        M  = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(frame, direction, (cx - 30, cy - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
