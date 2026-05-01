import cv2
import numpy as np
from config import *

class VisionSystem:
    def __init__(self, use_tflite=False):
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.use_tflite = use_tflite

        if use_tflite:
            self._init_tflite()
        else:
            self._load_templates()

    # ── Template Matching (simple, no ML needed) ──────────────────────────────

    def _load_templates(self):
        """Load reference images for each symbol from ./templates/"""
        import os
        self.templates = {}
        template_dir = "templates"
        for filename in os.listdir(template_dir):
            if filename.endswith(".png"):
                label = filename.replace(".png", "")
                img = cv2.imread(f"{template_dir}/{filename}", cv2.IMREAD_GRAYSCALE)
                self.templates[label] = img

    def _detect_template(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        best_label, best_score = "unknown", 0.0

        for label, template in self.templates.items():
            # Try multiple scales
            for scale in [0.5, 0.75, 1.0, 1.25, 1.5]:
                h, w = template.shape
                resized = cv2.resize(template, (int(w*scale), int(h*scale)))
                if resized.shape[0] > gray.shape[0] or resized.shape[1] > gray.shape[1]:
                    continue
                result = cv2.matchTemplate(gray, resized, cv2.TM_CCOEFF_NORMED)
                _, score, _, loc = cv2.minMaxLoc(result)
                if score > best_score:
                    best_score = score
                    best_label = label

        if best_score >= CONFIDENCE_THRESHOLD:
            return best_label, best_score
        return "unknown", best_score

    # ── TFLite Classifier (swap in for real symbol variety) ───────────────────

    def _init_tflite(self):
        import tflite_runtime.interpreter as tflite
        self.interpreter = tflite.Interpreter(model_path="model.tflite")
        self.interpreter.allocate_tensors()
        self.input_details  = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        # Load your label list
        with open("labels.txt") as f:
            self.labels = [l.strip() for l in f.readlines()]

    def _detect_tflite(self, frame):
        input_shape = self.input_details[0]['shape']  # e.g. [1, 224, 224, 3]
        h, w = input_shape[1], input_shape[2]
        img = cv2.resize(frame, (w, h))
        img = np.expand_dims(img.astype(np.float32) / 255.0, axis=0)

        self.interpreter.set_tensor(self.input_details[0]['index'], img)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_details[0]['index'])[0]

        idx   = int(np.argmax(output))
        score = float(output[idx])
        label = self.labels[idx] if score >= CONFIDENCE_THRESHOLD else "unknown"
        return label, score

    # ── Public API ────────────────────────────────────────────────────────────

    def capture_and_detect(self):
        ret, frame = self.cap.read()
        if not ret:
            return "unknown", 0.0, None

        if self.use_tflite:
            label, confidence = self._detect_tflite(frame)
        else:
            label, confidence = self._detect_template(frame)

        # Draw overlay for debugging
        cv2.putText(frame, f"{label} ({confidence:.2f})",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return label, confidence, frame

    def cleanup(self):
        self.cap.release()
