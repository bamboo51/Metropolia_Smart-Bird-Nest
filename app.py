from flask import Flask, Response, render_template
import cv2
import numpy as np
import pyaudio
import threading
import time
import av
import io
from picamera2 import Picamera2
import queue

class CombinedStream:
    def __init__(self):
        # Initialize audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        
        # Initialize video settings
        self.WIDTH = 1280
        self.HEIGHT = 720
        self.FPS = 30
        
        # Initialize queues for audio and video frames
        self.video_queue = queue.Queue(maxsize=10)
        self.audio_queue = queue.Queue(maxsize=10)
        
        # Setup camera
        self.setup_camera()
        
        # Setup audio
        self.setup_audio()
        
        # Create container for combined stream
        self.output_container = io.BytesIO()
        self.combined_stream = None
        
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
        # Start video capture thread
        self.video_thread = threading.Thread(target=self.capture_video)
        self.video_thread.daemon = True
        self.video_thread.start()

        # Start audio capture thread
        self.audio_thread = threading.Thread(target=self.capture_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()

        # Start stream combination thread
        self.combine_thread = threading.Thread(target=self.combine_streams)
        self.combine_thread.daemon = True
        self.combine_thread.start()

    def capture_video(self):
        while self.running:
            frame = self.picam.capture_array()
            # Convert to BGR for OpenCV compatibility
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            try:
                self.video_queue.put(frame, timeout=1)
            except queue.Full:
                self.video_queue.get()  # Remove oldest frame
                self.video_queue.put(frame)

    def capture_audio(self):
        while self.running:
            audio_data = self.audio_stream.read(self.CHUNK)
            try:
                self.audio_queue.put(audio_data, timeout=1)
            except queue.Full:
                self.audio_queue.get()  # Remove oldest chunk
                self.audio_queue.put(audio_data)

    def combine_streams(self):
        # Create output container
        output = av.open('rtsp://0.0.0.0:8554/stream', mode='w', format='rtsp')
        
        # Add streams
        video_stream = output.add_stream('h264', rate=self.FPS)
        video_stream.width = self.WIDTH
        video_stream.height = self.HEIGHT
        video_stream.pix_fmt = 'yuv420p'
        
        audio_stream = output.add_stream('aac', rate=self.RATE)
        audio_stream.channels = self.CHANNELS

        frame_count = 0
        start_time = time.time()

        while self.running:
            # Get video frame
            try:
                video_frame = self.video_queue.get(timeout=1)
                # Convert to PyAV frame
                frame = av.VideoFrame.from_ndarray(video_frame, format='bgr24')
                packet = video_stream.encode(frame)
                if packet:
                    output.mux(packet)
            except queue.Empty:
                continue

            # Get audio chunks
            try:
                audio_data = self.audio_queue.get(timeout=1)
                # Convert to PyAV frame
                audio_frame = av.AudioFrame.from_ndarray(
                    np.frombuffer(audio_data, dtype=np.float32),
                    layout='mono',
                    rate=self.RATE
                )
                packet = audio_stream.encode(audio_frame)
                if packet:
                    output.mux(packet)
            except queue.Empty:
                continue

            frame_count += 1
            
            # Maintain FPS
            elapsed_time = time.time() - start_time
            expected_frame_count = int(elapsed_time * self.FPS)
            if frame_count > expected_frame_count:
                time.sleep(1/self.FPS)

    def get_stream(self):
        return self.output_container.getvalue()

    def cleanup(self):
        self.running = False
        self.video_thread.join()
        self.audio_thread.join()
        self.combine_thread.join()
        self.picam.close()
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.audio.terminate()

# Flask application
app = Flask(__name__)
stream = CombinedStream()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream_feed():
    def generate():
        while True:
            yield stream.get_stream()
            time.sleep(1/30)  # Control frame rate

    return Response(
        generate(),
        mimetype='application/x-rtsp-tunnelled'
    )

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        stream.cleanup()