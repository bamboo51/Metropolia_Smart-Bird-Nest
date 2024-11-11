import asyncio
import threading
import pyaudio
import os
import cv2
import numpy as np
from flask import Flask, render_template, jsonify, request
from aiortc import VideoStreamTrack, AudioStreamTrack, RTCConfiguration, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling
from picamera2 import Picamera2

# Flask app setup
app = Flask(__name__)

# Initialize the PiCamera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())

# Initialize PyAudio for audio capture
audio_chunk_size = 1024
audio_format = pyaudio.paInt16
audio_channels = 1
audio_rate = 44100
p = pyaudio.PyAudio()
audio_stream = p.open(format=audio_format, channels=audio_channels, rate=audio_rate, input=True,
                      frames_per_buffer=audio_chunk_size)

# WebRTC setup
class VideoTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.picamera2 = picam2

    async def recv(self):
        frame = self.picamera2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        return frame_bytes

class AudioTrack(AudioStreamTrack):
    def __init__(self):
        super().__init__()
        self.audio_stream = audio_stream

    async def recv(self):
        audio_chunk = self.audio_stream.read(audio_chunk_size)
        return audio_chunk


# WebRTC signaling setup
async def offer(request):
    params = await request.json
    offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])
    
    pc = RTCPeerConnection(config=RTCConfiguration())
    
    pc.addTrack(VideoTrack())
    pc.addTrack(AudioTrack())

    # Create and send the answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return jsonify({
        'sdp': pc.localDescription.sdp,
        'type': pc.localDescription.type
    })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/offer', methods=["POST"])
async def handle_offer():
    return await offer(request)

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_flask())
