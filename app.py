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
        self.FORMAT = pyaudio.paInt16  # Changed to Int16 for better compatibility
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
        self.output_container = av.open('output.mp4', mode='w')
        
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

    def create_audio_frame(self, audio_data):
        """Convert audio data to a format suitable for PyAV"""
        # Convert bytes to numpy array
        samples = np.frombuffer(audio_data, dtype=np.int16)
        
        # Create audio frame
        frame = av.AudioFrame.from_ndarray(
            samples,
            format='s16',  # signed 16-bit
            layout='mono'  # single channel
        )
        frame.rate = self.RATE
        
        return frame

    def combine_streams(self):
        # Add streams to output container
        video_stream = self.output_container.add_stream('h264', rate=self.FPS)
        video_stream.width = self.WIDTH
        video_stream.height = self.HEIGHT
        video_stream.pix_fmt = 'yuv420p'
        
        audio_stream = self.output_container.add_stream('aac', rate=self.RATE)
        audio_stream.channels = self.CHANNELS

        pts = 0
        audio_pts = 0
        
        while self.running:
            # Process video
            try:
                video_frame = self.video_queue.get(timeout=1)
                av_frame = av.VideoFrame.from_ndarray(video_frame, format='bgr24')
                av_frame.pts = pts
                pts += 1
                
                for packet in video_stream.encode(av_frame):
                    self.output_container.mux(packet)
            except queue.Empty:
                continue

            # Process audio
            try:
                audio_data = self.audio_queue.get(timeout=1)
                audio_frame = self.create_audio_frame(audio_data)
                audio_frame.pts = audio_pts
                audio_pts += audio_frame.samples
                
                for packet in audio_stream.encode(audio_frame):
                    self.output_container.mux(packet)
            except queue.Empty:
                continue

            # Control frame rate
            time.sleep(1/self.FPS)

    def get_stream(self):
        return self.output_container

    def cleanup(self):
        self.running = False
        if hasattr(self, 'video_thread'):
            self.video_thread.join()
        if hasattr(self, 'audio_thread'):
            self.audio_thread.join()
        if hasattr(self, 'combine_thread'):
            self.combine_thread.join()
            
        # Flush streams
        if hasattr(self, 'output_container'):
            self.output_container.close()
            
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream_feed():
    global stream
    if stream is None:
        stream = CombinedStream()

    def generate():
        try:
            while True:
                data = stream.get_stream().read(1024)
                if not data:
                    break
                yield (b'--frame\r\n'
                       b'Content-Type: video/mp4\r\n\r\n' + data + b'\r\n')
        except Exception as e:
            print(f"Streaming error: {e}")
        finally:
            if stream:
                stream.cleanup()

    return Response(
        generate(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        if stream:
            stream.cleanup()