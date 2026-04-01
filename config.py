# config.py
import cv2

# Camera settings
CAMERA_URL = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Detection settings
MOTION_MIN_AREA = 500
MOTION_HISTORY = 3

# Classification settings
CONF_THRESHOLD = 0.75  # Keep at 0.75 for now
MODEL_PATH = "model/pest_model.tflite"

# Pest classification - note: "mealybugs" (plural) vs "mealybug" in your code# config.py
import cv2

# ============================================
# Camera Settings
# ============================================
CAMERA_URL = 0  # 0 for webcam, or IP camera URL like "http://192.168.1.100/video"
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# ============================================
# Motion Detection Settings
# ============================================
MOTION_MIN_AREA = 500  # Minimum area to consider as motion (pixels)
MOTION_HISTORY = 3  # Number of frames to track for persistent motion

# ============================================
# Classification Settings
# ============================================
CONF_THRESHOLD = 0.75  # Minimum confidence to accept classification
MODEL_PATH = "model/pest_model.tflite"  # Path to TFLite model

# ============================================
# Pest Tracking Settings
# ============================================
VISIT_WINDOW_SEC = 60  # Time window for considering repeated visits (seconds)
VISIT_THRESHOLD = 2  # Number of visits required within window to trigger alert

# ============================================
# Pest Classification Lists
# ============================================
CRITICAL_PESTS = ["armyworm", "aphid", "mealybugs", "stem_borers", "weevil"]

# ============================================
# Hardware Settings
# ============================================
SPRINKLER_COOLDOWN = 30  # seconds between sprinkler activations
BUZZER_DURATION = 1  # seconds to buzz

# ============================================
# Face Detection Settings
# ============================================
ENABLE_FACE_DETECTION = True
FACE_MIN_SIZE = (50, 50)  # Minimum face size to detect
FACE_SCALE_FACTOR = 1.1
FACE_MIN_NEIGHBORS = 5

# ============================================
# Storage Settings
# ============================================
CAPTURE_DIR = "static/captures"
EVENTS_FILE = "events.json"

# ============================================
# Web Interface Settings
# ============================================
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True
# You may need to update this based on your class names
CRITICAL_PESTS = ["armyworm", "aphid", "mealybugs", "stem_borers", "weevil"]

# Hardware settings
SPRINKLER_COOLDOWN = 30
BUZZER_DURATION = 1

# Face detection
ENABLE_FACE_DETECTION = True