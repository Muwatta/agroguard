#!/bin/bash
# Auto-start script for mobile farm

cd /home/pi/agroguard
source venv/bin/activate
python3 app.py --host=0.0.0.0 --port=5000
