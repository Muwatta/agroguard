#!/bin/bash
# ============================================
# AGROGUARD - Raspberry Pi 4/B Setup
# Run this ONE file to setup everything
# ============================================

echo "========================================="
echo "AgroGuard Raspberry Pi Setup"
echo "========================================="

# 1. Update system
echo "[1/6] Updating system..."
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
echo "[2/6] Installing dependencies..."
sudo apt install -y python3-pip python3-opencv python3-venv

# 3. Clone your repo (replace with your GitHub URL)
echo "[3/6] Cloning repository..."
git clone https://github.com/muwatta/agroguard.git
cd agroguard

# 4. Setup Python environment
echo "[4/6] Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install flask opencv-python numpy tensorflow
pip install tflite-runtime --extra-index-url https://google-coral.github.io/py-repo/

# 5. Configure camera URL
echo "[5/6] Configuring camera..."
echo "Enter your laptop's IP address (from stream_laptop_cam.py):"
read LAPTOP_IP
echo "PHONE_CAM_URL=http://$LAPTOP_IP:8080/video" > .env

# 6. Enable camera and serial
echo "[6/6] Enabling hardware interfaces..."
sudo raspi-config nonint do_camera 0
sudo raspi-config nonint do_serial 0

# Create auto-start service
sudo tee /etc/systemd/system/agroguard.service << SERVICE
[Unit]
Description=AgroGuard Pest Detection
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/agroguard
ExecStart=/home/pi/agroguard/venv/bin/python /home/pi/agroguard/app.py
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl enable agroguard.service

echo "========================================="
echo "✅ SETUP COMPLETE!"
echo "========================================="
echo ""
echo "To start manually:"
echo "  cd agroguard && source venv/bin/activate && python app.py"
echo ""
echo "To start automatically:"
echo "  sudo systemctl start agroguard"
echo ""
echo "Web interface: http://$(hostname -I | cut -d' ' -f1):5000"
echo ""
echo "========================================="
