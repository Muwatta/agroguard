import os

os.environ['OPENCV_VIDEOIO_PRIORITY_BACKEND'] = 'DSHOW'  # Use DirectShow

CAPTURE_DIR = "static/captures"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "pest_model.tflite")


CAMERA_URL = "http://10.18.128.170:8080/video"
VISIT_WINDOW_SEC = 300
VISIT_THRESHOLD = 2
CONF_THRESHOLD = 0.6