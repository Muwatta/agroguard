#!/bin/bash
# ============================================
# AGROGUARD - Raspberry Pi 4/B Setup
# ============================================

echo "========================================="
echo "AgroGuard Raspberry Pi Setup"
echo "========================================="

# 1. Update system
echo "[1/6] Updating system..."
sudo apt update && sudo apt upgrade -y

# 2. Install system dependencies
echo "[2/6] Installing system packages..."
sudo apt install -y python3-pip python3-opencv python3-venv git

# 3. Clone or pull repository
if [ -d "agroguard" ]; then
    echo "[3/6] Updating repository..."
    cd agroguard && git pull
else
    echo "[3/6] Cloning repository..."
    git clone https://github.com/muwatta/agroguard.git
    cd agroguard
fi

# 4. Setup Python environment
echo "[4/6] Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install from Pi-specific requirements
pip install -r requirements_pi.txt

# Install TFLite runtime (required for AI)
pip install tflite-runtime --extra-index-url https://google-coral.github.io/py-repo/

# 5. Configure camera
echo "[5/6] Configuring camera..."
sed -i 's/CAMERA_URL = .*/CAMERA_URL = 0/' config.py

# 6. Enable hardware interfaces
echo "[6/6] Enabling hardware..."
sudo raspi-config nonint do_camera 0
sudo raspi-config nonint do_serial 0
sudo usermod -a -G dialout $USER

echo "========================================="
echo "✅ SETUP COMPLETE!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Copy model file: scp laptop:~/agroguard/model/pest_model.tflite ~/agroguard/model/"
echo "2. Run: source venv/bin/activate && python app.py"
echo ""
echo "Web interface: http://$(hostname -I | cut -d' ' -f1):5000"
echo "========================================="