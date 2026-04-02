# config.py - AgroGuard Configuration
import cv2

# Camera Settings
CAMERA_URL = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Detection Settings
MOTION_MIN_AREA = 500
MOTION_HISTORY = 3

# Classification Settings - OPTIMIZED for 59% average confidence
# Set to 0.55 to catch most detections while avoiding false positives
CONF_THRESHOLD = 0.55
MODEL_PATH = "model/pest_model.tflite"

# Pest Tracking Settings
VISIT_WINDOW_SEC = 60
VISIT_THRESHOLD = 2  # Requires 2 detections in 60 seconds

# Pest Classification Lists
CRITICAL_PESTS = ["armyworm", "aphid", "mealybugs", "stem_borers", "weevil"]

# Hardware Settings
SPRINKLER_COOLDOWN = 30
BUZZER_DURATION = 1

# Face Detection Settings
ENABLE_FACE_DETECTION = True
FACE_MIN_SIZE = (50, 50)
FACE_SCALE_FACTOR = 1.1
FACE_MIN_NEIGHBORS = 5

# Storage Settings
CAPTURE_DIR = "static/captures"
EVENTS_FILE = "logs/events.json"

# Web Interface Settings
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True
