# AgroGuard 🌿

Smart farming system for Jos Plateau — automated irrigation + AI pest detection + live dashboard.

---

## Repo Structure

```
agroguard/
├── agroguard_irrigation.ino   # Arduino — irrigation controller
├── agroguard_pi.py            # Raspberry Pi — AI + dashboard + serial
├── stream_laptop_cam.py       # Windows laptop — streams webcam to Pi
├── download_images.py         # Download aphid & mealybug training images
├── .env.example               # Config template (copy to .env, never commit)
├── .gitignore
├── requirements_windows.txt
└── requirements_pi.txt
```

---

## Step 1 — Windows Laptop Setup

```bash
# Install dependencies
pip install -r requirements_windows.txt

# Copy config
copy .env.example .env
# (no changes needed on Windows side)
```

---

## Step 2 — Run the Laptop Camera Stream (Hackathon Demo)

```bash
python stream_laptop_cam.py
```

It will print something like:
```
📡  Streaming at:  http://192.168.1.105:8080/video
🔧  Set in .env on Pi:  PHONE_CAM_URL=http://192.168.1.105:8080/video
```

**Keep this terminal open during the demo.**

---

## Step 3 — Push to GitHub

```bash
git init
git add .
git commit -m "AgroGuard initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/agroguard.git
git push -u origin main
```

---

## Step 4 — Raspberry Pi Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/agroguard.git
cd agroguard

# Install Pi dependencies
pip3 install -r requirements_pi.txt

# Install TFLite (separate step)
pip3 install tflite-runtime --extra-index-url https://google-coral.github.io/py-repo/

# Create .env from template
cp .env.example .env
nano .env
```

In `.env` on the Pi, set:
```
PHONE_CAM_URL=http://<LAPTOP-IP>:8080/video
SERIAL_PORT=/dev/ttyUSB0    # or /dev/ttyACM0 — check with: ls /dev/tty*
```

---

## Step 5 — Run on Pi

```bash
python3 agroguard_pi.py
```

Open a browser on any device on the same Wi-Fi:
```
http://<PI-IP-ADDRESS>:5000
```

Find Pi's IP with: `hostname -I`

---

## Step 6 — Arduino

1. Open `agroguard_irrigation.ino` in Arduino IDE
2. Select board: **Arduino Uno**
3. Select port: whichever COM port appears when you plug in the Arduino
4. Click **Upload**
5. Plug Arduino into Pi via USB — it auto-connects

---

## Wiring

| Component              | Arduino Pin |
|------------------------|-------------|
| Soil Moisture Sensor   | A0, VCC→5V, GND→GND |
| Relay IN               | D7 |
| Relay VCC/GND          | 5V / GND |
| Water Pump             | Relay COM/NO (external supply) |

| Component              | Raspberry Pi GPIO |
|------------------------|-------------------|
| Buzzer / Ultrasonic IN | GPIO 17 (BCM) |
| GND                    | Any GND pin |

---

## Hackathon Demo Checklist

- [ ] Laptop running `stream_laptop_cam.py` — note the IP it prints
- [ ] Pi `.env` has `PHONE_CAM_URL=http://<laptop-ip>:8080/video`
- [ ] Arduino plugged into Pi via USB
- [ ] Pi running `python3 agroguard_pi.py`
- [ ] Open `http://<pi-ip>:5000` on your phone or laptop browser
- [ ] Touch the soil sensor to demo moisture reading
- [ ] Hold a printed pest image to the laptop camera to demo detection

---

## Training the Model (Google Colab)

1. Run `python download_images.py` to get aphid + mealybug images
2. Upload `dataset_new/` to Google Drive
3. Train MobileNetV2 on Colab (free GPU), export to `.tflite`
4. Copy `pest_model.tflite` to the Pi's `agroguard/` folder
## Model Files

The trained model files are not included in this repository due to size limitations. 
To run the application, you need:

1. **Trained model files** (pest_model.tflite and pest_model.h5) in the `model/` folder
2. **Dataset** in the `dataset_new/` folder

### Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Place the trained model files in `model/` folder
4. Run the application: `python app.py`

### Model Performance

- Validation accuracy: 87.6%
- Detection confidence: 98-100% for all 6 pest classes
- Classes: aphid, armyworm, mealybugs, stem_borers, weevil, none

