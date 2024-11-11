from flask import Flask, render_template, request, jsonify
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, AudioStreamTrack
from aiortc.contrib.media import MediaRelay
import pyaudio
import asyncio
from picamera2 import Picamera2
import cv2
from av import VideoFrame

app = Flask(__name__)
relay = MediaRelay()
pc = None

# Video track class for PiCamera2
class CameraVideoTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_video_configuration())
        self.camera.start()

    async def recv(self):
        frame = self.camera.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts, video_frame.time_base = self.time_base()
        return video_frame

# Audio track class for microphone using PyAudio
class MicrophoneAudioTrack(AudioStreamTrack):
    def __init__(self):
        super().__init__()
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    async def recv(self):
        audio_data = self.stream.read(1024)
        frame = AudioStreamTrack.AudioFrame.from_ndarray(audio_data, format="s16")
        return frame

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/offer", methods=["POST"])
async def offer():
    global pc
    pc = RTCPeerConnection()

    # Parse offer SDP from client
    data = await request.get_json()
    offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
    await pc.setRemoteDescription(offer)

    # Add video and audio tracks
    video_track = CameraVideoTrack()
    audio_track = MicrophoneAudioTrack()
    pc.addTrack(video_track)
    pc.addTrack(audio_track)

    # Create and return an answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return jsonify({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
