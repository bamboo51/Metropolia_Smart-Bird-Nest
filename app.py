from flask import Flask, Response, render_template
import cv2
import pyaudio
import threading
import subprocess as sp
import numpy as np
import time
from picamera2 import Picamera2
import shlex

app = Flask(__name__)

# Audio/Video Configuration
FRAME_RATE = 30
AUDIO_RATE = 44100
AUDIO_CHANNELS = 1
WIDTH = 640
HEIGHT = 480
RTSP_PORT = 8554
STREAM_URL = f'rtsp://0.0.0.0:{RTSP_PORT}/stream'

# Initialize PiCamera
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(
    main={"size": (WIDTH, HEIGHT)},
    controls={"FrameDurationLimits": (33333, 33333)}
)
picam2.configure(camera_config)
picam2.start()

class RTSPStreamer:
    def __init__(self):
        self.running = False
        self.process = None
        
        # FFmpeg command for combined streaming
        self.command = [
            'ffmpeg',
            # Input video options (from pipe)
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', f'{WIDTH}x{HEIGHT}',
            '-r', str(FRAME_RATE),
            '-i', 'pipe:0',
            # Input audio options (from pipe)
            '-f', 'f32le',
            '-ar', str(AUDIO_RATE),
            '-ac', str(AUDIO_CHANNELS),
            '-i', 'pipe:1',
            # Output options
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-c:a', 'aac',
            '-ar', str(AUDIO_RATE),
            '-b:a', '128k',
            '-flags', 'low_delay',
            '-f', 'rtsp',
            '-rtsp_transport', 'tcp',
            STREAM_URL
        ]
    
    def start(self):
        """Start the RTSP streaming process"""
        self.running = True
        self.process = sp.Popen(
            self.command,
            stdin=sp.PIPE,
            stdout=sp.DEVNULL,
            stderr=sp.DEVNULL
        )
        
        # Start capture threads
        self.video_thread = threading.Thread(target=self._capture_video)
        self.audio_thread = threading.Thread(target=self._capture_audio)
        
        self.video_thread.daemon = True
        self.audio_thread.daemon = True
        
        self.video_thread.start()
        self.audio_thread.start()
    
    def stop(self):
        """Stop the streaming process"""
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait()
    
    def _capture_video(self):
        """Capture and pipe video frames to FFmpeg"""
        while self.running:
            try:
                frame = picam2.capture_array()
                self.process.stdin.write(frame.tobytes())
            except Exception as e:
                print(f"Video capture error: {e}")
                break
    
    def _capture_audio(self):
        """Capture and pipe audio to FFmpeg"""
        CHUNK = 1024
        audio = pyaudio.PyAudio()
        
        stream = audio.open(
            format=pyaudio.paFloat32,
            channels=AUDIO_CHANNELS,
            rate=AUDIO_RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        while self.running:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                self.process.stdin.write(data)
            except Exception as e:
                print(f"Audio capture error: {e}")
                break
        
        stream.stop_stream()
        stream.close()
        audio.terminate()

# Global streamer instance
streamer = RTSPStreamer()

@app.route('/')
def index():
    """Streaming page"""
    return render_template('index.html', stream_url=STREAM_URL)

@app.route('/start')
def start_stream():
    """Start streaming"""
    if not streamer.running:
        streamer.start()
    return {'status': 'started'}

@app.route('/stop')
def stop_stream():
    """Stop streaming"""
    if streamer.running:
        streamer.stop()
    return {'status': 'stopped'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)