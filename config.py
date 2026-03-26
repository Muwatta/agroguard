import os

os.environ['OPENCV_VIDEOIO_PRIORITY_BACKEND'] = 'DSHOW' 

CAPTURE_DIR = "static/captures"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "pest_model.tflite")

# Remove the space at the end!
CAMERA_URL = "http://192.168.1.50:8080/video"

VISIT_WINDOW_SEC = 300
VISIT_THRESHOLD = 2
CONF_THRESHOLD = 0.6