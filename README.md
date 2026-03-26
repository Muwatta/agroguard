# AgroGuard 🌱

> An AI-powered autonomous crop protection and smart irrigation system — computer vision for disease detection, ML-based classification, growth tracking, and advisory generation, all in Python.

**Python 97%**

---

## 🟢 Status

| Component | Status |
|---|---|
| Disease Classifier | ⚠️ Dummy Mode (needs real model) |
| Computer Vision Pipeline | ✅ Complete |
| Growth Tracker | ✅ Complete |
| Advisory Engine | ✅ Complete |
| Storage Layer | ✅ Complete |
| Web Interface | ✅ Complete |
| Live Video Streaming | ✅ Complete |
| Mobile Access | ✅ Complete |

---

## 🏗️ Architecture

```
agroguard/
├── app.py              # Entry point — Flask/web app
├── vision.py           # Computer vision pipeline (image capture + preprocessing)
├── classifier.py       # ML model inference — crop disease classification
├── tracker.py          # Growth history tracking over time
├── advisory.py         # AI-generated crop advisory based on detections
├── storage.py          # Data persistence layer
├── config.py           # Environment + app configuration
├── growth_history.json # Time-series growth data store
├── ai/                 # Model assets and AI utilities
├── backend/            # Backend logic and API routes
├── model/              # Trained ML model files
├── scripts/            # Utility and automation scripts
└── templates/          # HTML templates (web UI)
```

---

## ⚙️ Tech Stack

| Layer | Tech |
|---|---|
| Language | Python |
| Computer Vision | OpenCV / vision pipeline (`vision.py`) |
| ML Classification | Trained model (`model/`) + `classifier.py` |
| Advisory Engine | AI-driven recommendations (`advisory.py`) |
| Web Interface | Flask + Jinja2 templates |
| Config | `python-dotenv` |

---

## ✅ Core Features

- **Crop disease detection** — computer vision pipeline captures and preprocesses images for inference
- **ML classification** — identifies disease type from visual input using a trained model
- **Growth tracking** — logs and monitors crop growth over time via `growth_history.json`
- **Smart advisory** — generates actionable crop protection and irrigation recommendations
- **Persistent storage** — structured data layer for detections, history, and reports
- **Web interface** — browser-accessible dashboard for monitoring and advisory output

---

## 🚀 Local Development

```bash
git clone https://github.com/Muwatta/agroguard.git
cd agroguard

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Set up environment variables:**

```bash
cp .env .env.local
# Edit .env with your config values
```

**Run the app:**

```bash
python app.py
```

---

## 🗺️ Roadmap

| Phase | Feature |
|---|---|
| Now | Stable detection + advisory pipeline |
| Next | REST API exposure for mobile/IoT integration |
| V2 | Real-time camera feed + edge deployment |
| V3 | Irrigation hardware integration (GPIO/Raspberry Pi) |

---

## 📬 Contact

**Abdullahi Musliudeen**
[LinkedIn](https://www.linkedin.com/in/abdullahi-musliudeen-64435a239/) · abdullahmusliudeen@gmail.com

---

MIT License
