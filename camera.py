import cv2
import threading
import time

class Camera:
    def __init__(self, source=0):
        """Initialize camera with source (0 for webcam, or URL for IP camera)"""
        self.source = source
        self.camera = cv2.VideoCapture(source)
        
        # Set resolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.frame = None
        self.running = False
        self.lock = threading.Lock()
        
    def start(self):
        """Start the background thread to read frames"""
        if not self.running:
            self.running = True
            threading.Thread(target=self._update, daemon=True).start()
            
    def _update(self):
        """Continuously read frames from camera"""
        while self.running:
            success, frame = self.camera.read()
            if success:
                with self.lock:
                    self.frame = frame
            time.sleep(0.033)  # ~30 FPS
            
    def get_frame(self):
        """Get current frame as JPEG bytes"""
        with self.lock:
            if self.frame is None:
                return None
            # Encode frame as JPEG
            ret, jpeg = cv2.imencode('.jpg', self.frame)
            return jpeg.tobytes() if ret else None
            
    def stop(self):
        """Stop the camera"""
        self.running = False
        self.camera.release()
        
    def __del__(self):
        self.stop()

def gen_frames(camera):
    """Generator function for streaming frames"""
    while True:
        frame = camera.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.033)  # ~30 FPS