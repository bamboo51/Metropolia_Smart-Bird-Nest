import threading
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
import subprocess
import cv2
import os

picam2 = Picamera2()
streaming_event = threading.Event()

picam2.configure(picam2.create_preview_configuration())
encoder = H264Encoder(10000000)

filename = None

def start_streaming(file_name:str):
    global filename
    if not streaming_event.is_set():
        filename = file_name
        picam2.start()
        streaming_event.set()
        picam2.start_recording(encoder, f'./recordings/video_{filename}.h264')
        print("Streaming started.")

def stop_streaming():
    if streaming_event.is_set():
        picam2.stop_recording()
        picam2.stop()
        streaming_event.clear()

def generate_frames():
    """Generator function that yields camera frames to be displayed as a video stream."""
    while streaming_event.is_set():
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')  # Yield frame as an MJPEG stream
