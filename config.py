import os
os.environ['OPENCV_VIDEOIO_PRIORITY_BACKEND'] = 'DSHOW'

CAPTURE_DIR = "static/captures"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "pest_model.tflite")

CAMERA_URL = 0
RELAY_PIN = 17
BUZZER_PIN = 27

VISIT_WINDOW_SEC = 300
VISIT_THRESHOLD = 2
CONF_THRESHOLD = 0.6
