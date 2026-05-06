#!/usr/bin/env bash
# Run this on the Raspberry Pi (not on your Windows dev machine):
#   chmod +x camera_setup.sh && ./camera_setup.sh
# Then reboot before camera_test.py

set -euo pipefail

# 1. Update package list
echo "[1/5] Updating packages..."
sudo apt-get update -y

# 2. Install OpenCV + camera utilities
echo "[2/5] Installing OpenCV and v4l2 tools..."
sudo apt-get install -y \
    python3-opencv \
    python3-picamera2 \
    libcamera-apps \
    v4l2-utils \
    libcap-dev

# 3. Install Python deps
echo "[3/5] Installing Python packages..."
pip3 install opencv-python RPi.GPIO --break-system-packages

# 4. Enable the camera via raspi-config (non-interactive)
echo "[4/5] Enabling camera interface..."
sudo raspi-config nonint do_camera 0

# 5. Add v4l2 kernel module so OpenCV can see /dev/video0
echo "[5/5] Loading v4l2 kernel module..."
if ! grep -q "bcm2835-v4l2" /etc/modules; then
    echo "bcm2835-v4l2" | sudo tee -a /etc/modules
fi
sudo modprobe bcm2835-v4l2 2>/dev/null || true

echo ""
echo "======================================="
echo " Done! Please REBOOT now:"
echo "   sudo reboot"
echo ""
echo " After reboot, test the camera with:"
echo "   python3 camera_test.py"
echo "======================================="
