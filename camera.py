import cv2
import threading
import time
import numpy as np

class Camera:
    def __init__(self, source=0):
        """Initialize camera with source (0 for webcam, or URL for IP camera)"""
        self.source = source
        
        # Try different backends for Windows
        if isinstance(source, int):
            # Try DirectShow first (more stable on Windows)
            self.camera = cv2.VideoCapture(source, cv2.CAP_DSHOW)
            if not self.camera.isOpened():
                # Fallback to default
                self.camera = cv2.VideoCapture(source)
        else:
            # URL for IP camera
            self.camera = cv2.VideoCapture(source)
        
        # Set resolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.frame = None
        self.running = False
        self.lock = threading.Lock()
        self.error_count = 0
        
    def start(self):
        """Start the background thread to read frames"""
        if not self.running:
            self.running = True
            threading.Thread(target=self._update, daemon=True).start()
            
    def _update(self):
        """Continuously read frames from camera"""
        while self.running:
            try:
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    with self.lock:
                        self.frame = frame
                    self.error_count = 0
                else:
                    self.error_count += 1
                    if self.error_count > 10:
                        print("Camera: Too many errors, trying to reconnect...")
                        self._reconnect()
            except Exception as e:
                print(f"Camera error: {e}")
                time.sleep(0.1)
            time.sleep(0.033)  # ~30 FPS
            
    def _reconnect(self):
        """Try to reconnect to camera"""
        self.camera.release()
        time.sleep(1)
        if isinstance(self.source, int):
            self.camera = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
        else:
            self.camera = cv2.VideoCapture(self.source)
        self.error_count = 0
            
    def get_frame(self):
        """Get current frame as JPEG bytes"""
        with self.lock:
            if self.frame is None:
                # Return a blank frame if no camera
                blank = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(blank, "No Camera", (200, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                ret, jpeg = cv2.imencode('.jpg', blank)
                return jpeg.tobytes() if ret else None
            
            ret, jpeg = cv2.imencode('.jpg', self.frame, 
                                    [int(cv2.IMWRITE_JPEG_QUALITY), 85])
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