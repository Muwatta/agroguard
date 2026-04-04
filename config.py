# config.py - Hackathon Configuration
import cv2

CAMERA_URL = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
MOTION_MIN_AREA = 500
MOTION_HISTORY = 3

# VERY LOW THRESHOLD FOR HACKATHON
CONF_THRESHOLD = 0.85
MODEL_PATH = "model/pest_model.tflite"

VISIT_WINDOW_SEC = 30  # Shorter window for faster alerts
VISIT_THRESHOLD = 3    # Alert on first detection
CRITICAL_PESTS = ["armyworm", "aphid", "mealybugs", "stem_borers", "weevil"]

SPRINKLER_COOLDOWN = 30
BUZZER_DURATION = 1
ENABLE_FACE_DETECTION = True

CAPTURE_DIR = "static/captures"
EVENTS_FILE = "logs/events.json"
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True
