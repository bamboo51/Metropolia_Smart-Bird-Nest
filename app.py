from flask import Flask, Response, render_template
import cv2
import numpy as np
import pyaudio
import threading
import time
from picamera2 import Picamera2
import queue
import io
from PIL import Image

class CombinedStream:
    def __init__(self):
        # Initialize audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        
        # Initialize video settings
        self.WIDTH = 1280
        self.HEIGHT = 720
        self.FPS = 30
        
        # Initialize queues
        self.frame_queue = queue.Queue(maxsize=10)
        self.audio_queue = queue.Queue(maxsize=10)
        
        # Setup devices
        self.setup_camera()
        self.setup_audio()
        
        # Start capture threads
        self.running = True
        self.start_capture_threads()

    def setup_camera(self):
        self.picam = Picamera2()
        video_config = self.picam.create_video_configuration(
            main={"size": (self.WIDTH, self.HEIGHT), "format": "RGB888"}
        )
        self.picam.configure(video_config)
        self.picam.start()

    def setup_audio(self):
        self.audio = pyaudio.PyAudio()
        self.audio_stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )

    def start_capture_threads(self):
        self.video_thread = threading.Thread(target=self.capture_video)
        self.video_thread.daemon = True
        self.video_thread.start()

        self.audio_thread = threading.Thread(target=self.capture_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()

    def capture_video(self):
        while self.running:
            frame = self.picam.capture_array()
            # Convert to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Convert to JPEG for web streaming
            success, jpeg = cv2.imencode('.jpg', frame)
            if success:
                try:
                    self.frame_queue.put(jpeg.tobytes(), timeout=1)
                except queue.Full:
                    try:
                        self.frame_queue.get_nowait()  # Remove oldest frame
                        self.frame_queue.put(jpeg.tobytes())
                    except queue.Empty:
                        pass

    def capture_audio(self):
        while self.running:
            try:
                audio_data = self.audio_stream.read(self.CHUNK)
                self.audio_queue.put(audio_data)
            except queue.Full:
                try:
                    self.audio_queue.get_nowait()  # Remove oldest audio chunk
                    self.audio_queue.put(audio_data)
                except queue.Empty:
                    pass

    def get_frame(self):
        try:
            return self.frame_queue.get(timeout=1)
        except queue.Empty:
            return None

    def get_audio(self):
        try:
            return self.audio_queue.get(timeout=1)
        except queue.Empty:
            return None

    def cleanup(self):
        self.running = False
        if hasattr(self, 'picam'):
            self.picam.close()
        if hasattr(self, 'audio_stream'):
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if hasattr(self, 'audio'):
            self.audio.terminate()

# Flask application
app = Flask(__name__)
stream = None

def get_stream():
    global stream
    if stream is None:
        stream = CombinedStream()
    return stream

@app.route('/')
def index():
    return render_template('index.html')

def generate_video():
    stream = get_stream()
    while True:
        frame = stream.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(1/30)

def generate_audio():
    stream = get_stream()
    while True:
        audio_data = stream.get_audio()
        if audio_data is not None:
            yield audio_data
        else:
            time.sleep(0.01)

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/audio_feed')
def audio_feed():
    return Response(generate_audio(),
                    mimetype='audio/wav')

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        if stream:
            stream.cleanup()