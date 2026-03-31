# AgroGuard 🌱

> AI-based smart irrigation and pest defense system for smallholder farms.

## Project Overview

AgroGuard combines a Raspberry Pi (or Windows dev setup), Arduino, and camera-based ML to:

- Automate irrigation by sensing soil moisture and controlling a water relay.
- Detect and classify key pests (armyworm, weevil, stem borer, aphid, mealybug, etc.) using a camera + TensorFlow Lite.
- Log detections in `events.json` and display actionable advisory recommendations in a web dashboard.
- Trigger defense outputs: buzzer, sprinkler, alerting.

This repository is built for early prototype and competition entries and supports both simulated (Windows) and real GPIO (Raspberry Pi) hardware modes.

## Core Capabilities

| Feature                                              | Status                                |
| ---------------------------------------------------- | ------------------------------------- |
| Soil moisture-based irrigation control (Arduino/RPi) | ✅ Implemented                        |
| Camera live feed and capture                         | ✅ Implemented                        |
| Pest classification pipeline (TFLite)                | ⚠️ Requires model runtime             |
| Dashboard (live/analytics/settings)                  | ✅ Implemented                        |
| Event logging (`events.json`)                        | ✅ Implemented                        |
| Hardware simulation for Windows                      | ✅ Implemented                        |
| GPIO control for Raspberry Pi                        | ✅ Implemented                        |
| Model training/retrain pipeline                      | ✅ Implemented (retrain_with_none.py) |

## System Components

- `app.py`: Flask server and detection loop
- `camera.py`: webcam frame capture and streaming
- `vision.py`: motion detection and image capture
- `classifier.py`: pest classification (TFLite, fallback for missing runtime)
- `tracker.py`: stays filter for persistent detection
- `advisory.py`: pest-specific advice mapping
- `storage.py`: event persistence
- `hardware_controller.py`: sprinkler/buzzer + GPIO simulation
- `arduino_controller.py`: serial interface to Arduino
- `templates/`: dashboard HTML templates
- `static/captures/`: captured images

## Quick start

```bash
git clone https://github.com/Muwatta/agroguard.git
cd agroguard
python -m venv venv
venv\Scripts\activate     # Windows
# OR source venv/bin/activate on Linux
pip install --upgrade pip
pip install -r requirements.txt
```

### TensorFlow runtime

- On Windows, install `tensorflow`:

```bash
pip install tensorflow
```

- On Raspberry Pi, use tflite-runtime wheel:

```bash
pip install tflite-runtime
```

## Run

```bash
python app.py
```

Open http://127.0.0.1:5000

## Dashboard

Current UI supports:

- Total detections
- Advanced active alerts (critical pest + confidence >= 80%)
- Captures today
- Pest diversity
- Recent activity cards with timeline + advice
- System health indicators (camera, AI model, storage, last alert)
- Pest distribution chart

## Model and data notes

- `model/pest_model.tflite` must exist for real ML classification.
- `classifier.py` fallback mode returns `none` when runtime is unavailable.
- You can retrain using `python -m retrain_with_none.py` via the dashboard `/api/retrain`.

## Next enhancements

1. Add soil moisture threshold-based auto-irrigation in the main loop.
2. Add sound/light guard for specific pests.
3. Use nuisance pest policy (bypass random face/image classification).
4. Add automatic dataset labeling and model update pipeline.

## Build/test check

- Python syntax check: `python -m py_compile *.py`
- Application runs: `python app.py`

## Deployment

- Push to GitHub, clone on Raspberry Pi
- Install dependencies and hardware packages
- Run with so-called `sudo` for GPIO on Pi

## Contact

**Abdullahi Musliudeen**

- abdullahmusliudeen@gmail.com

---

MIT License
