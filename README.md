
# 🌾 AgroGuard - AI Smart Farming System

> Pest detection + automatic irrigation | Hackathon Ready

---

## 🚀 Quick Start (3 steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the system
python app.py

# 3. Open browser
http://127.0.0.1:5000/live
```

---

## 📋 What It Does

| Feature | Description |
|---------|-------------|
| **Pest Detection** | AI identifies 6 pests (98-100% accuracy) |
| **Face Detection** | Ignores humans - no false alarms |
| **Auto Irrigation** | Waters plants when soil is dry |
| **Live Dashboard** | Web interface shows everything |

**Detects:** Armyworm, Aphid, Mealybugs, Stem Borers, Weevil

---

## 🔧 Hardware (Optional)

| Component | Cost |
|-----------|------|
| Arduino Uno | $20 |
| Soil Moisture Sensor | $10 |
| 5V Relay | $8 |
| Water Pump | $15 |
| USB Webcam | $25 |
| **Total** | **~$78** |

**Wiring:** Arduino A0→Sensor, D7→Relay, Relay→Pump

---

## 💻 Setup

```bash
# Clone
git clone https://github.com/muwatta/agroguard.git
cd agroguard

# Python environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run
python app.py
```

**Arduino:** Upload `agroguard_irrigation.ino` (once only)

---

## 🌐 Web Pages

| Page | URL |
|------|-----|
| Live Feed | `/live` |
| Dashboard | `/` |
| Analytics | `/analytics` |
| Hardware | `/hardware` |

---

## 🔍 Troubleshooting

| Problem | Fix |
|---------|-----|
| Camera not found | Check USB |
| Arduino not connected | Check COM port |
| Access denied | Close Arduino IDE |
| Model error | Check `model/` folder |

**Find COM port:**
```bash
python -c "import serial.tools.list_ports; [print(p.device) for p in serial.tools.list_ports.comports()]"
```

---

## 🎤 Demo (2 minutes)

1. Start: `python app.py`
2. Show pest to camera
3. Watch detection + buzzer + sprinkler

**Say:** *"AI detects pests in real-time and waters automatically."*

---

## 📁 Files

| File | Purpose |
|------|---------|
| `app.py` | Main app |
| `classifier.py` | AI model |
| `vision.py` | Motion detection |
| `hardware_controller.py` | Hardware control |
| `arduino_controller.py` | Arduino communication |
| `agroguard_irrigation.ino` | Arduino code |

---

## ⚡ Commands

```bash
python app.py                    # Start system
python arduino_controller.py     # Test Arduino
cat logs/events.json             # View detections
```

---

## ✅ Checklist

- [ ] Camera connected
- [ ] Arduino plugged in (optional)
- [ ] `python app.py` running
- [ ] Browser open to `/live`

---
