"""
AgroGuard – Laptop Camera Streamer (Windows)
Run this on your Windows laptop during the hackathon demo.
The Pi will pull the stream from http://<your-laptop-ip>:8080/video

Usage:
    python stream_laptop_cam.py

Then on the Pi side, set in .env:
    PHONE_CAM_URL=http://<laptop-ip>:8080/video
"""

import cv2
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ── Config ───────────────────────────────────────────────────────────────────
PORT        = 8080
CAMERA_IDX  = 0        # 0 = built-in webcam, 1 = external USB cam
JPEG_QUALITY = 75
FRAME_WIDTH  = 640
FRAME_HEIGHT = 480

# ── Shared latest frame ───────────────────────────────────────────────────────
latest_frame = None
frame_lock   = threading.Lock()
cam_ok       = False


def capture_loop():
    global latest_frame, cam_ok
    cap = cv2.VideoCapture(CAMERA_IDX, cv2.CAP_DSHOW)   # CAP_DSHOW = faster on Windows
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 20)
    if not cap.isOpened():
        print("❌  Could not open camera. Try changing CAMERA_IDX to 1.")
        return
    cam_ok = True
    print(f"✅  Camera opened (index {CAMERA_IDX})")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        with frame_lock:
            latest_frame = frame


def generate_mjpeg():
    """Generator: yields MJPEG boundary frames."""
    while True:
        with frame_lock:
            frame = latest_frame
        if frame is None:
            import time; time.sleep(0.05)
            continue
        _, buf = cv2.imencode(
            ".jpg", frame,
            [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
        )
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buf.tobytes()
            + b"\r\n"
        )


class StreamHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass   # silence per-request logs

    def do_GET(self):
        if self.path == "/video":
            self.send_response(200)
            self.send_header("Content-Type",
                             "multipart/x-mixed-replace; boundary=frame")
            self.end_headers()
            try:
                for chunk in generate_mjpeg():
                    self.wfile.write(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass   # Pi disconnected — normal
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<h2>AgroGuard Laptop Cam</h2>"
                b'<img src="/video" width="640">'
            )
        else:
            self.send_response(404)
            self.end_headers()


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    print("AgroGuard Laptop Camera Streamer")
    print("=" * 38)

    # Start capture thread
    t = threading.Thread(target=capture_loop, daemon=True)
    t.start()

    # Wait for camera
    import time
    for _ in range(30):
        if cam_ok or latest_frame is not None:
            break
        time.sleep(0.1)

    ip = get_local_ip()
    print(f"\n📡  Streaming at:  http://{ip}:{PORT}/video")
    print(f"🔧  Set in .env on Pi:  PHONE_CAM_URL=http://{ip}:{PORT}/video")
    print("\nPress Ctrl+C to stop.\n")

    server = HTTPServer(("0.0.0.0", PORT), StreamHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")