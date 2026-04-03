#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-opencv
sudo apt install -y libatlas-base-dev  # For TensorFlow

# Install Python packages
pip3 install tensorflow flask opencv-python numpy

# Enable camera
sudo raspi-config nonint do_camera 0

# Create systemd service for auto-start
sudo cat > /etc/systemd/system/agroguard.service << 'SERVICE'
[Unit]
Description=AgroGuard Pest Detection
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/agroguard
ExecStart=/usr/bin/python3 /home/pi/agroguard/app.py
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

# Enable service
sudo systemctl enable agroguard.service
sudo systemctl start agroguard.service

echo "✅ Production setup complete!"
echo "Web interface: http://$(hostname -I | cut -d' ' -f1):5000"
