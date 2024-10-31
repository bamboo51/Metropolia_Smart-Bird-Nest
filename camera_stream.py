import threading
from picamera2 import Picamera2
import cv2


picam2 = Picamera2()
streaming_event = threading.Event()

picam2.configure(picam2.create_preview_configuration())

def start_streaming():
    if not streaming_event.is_set():
        picam2.start()
        streaming_event.set()
        print("Streaming started.")

def stop_streaming():
    if streaming_event.is_set():
        picam2.stop()
        streaming_event.clear()
        print("Streaming stopped.")

def generate_frames():
    """Generator function that yields camera frames to be displayed as a video stream."""
    while streaming_event.is_set():
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')  # Yield frame as an MJPEG stream
