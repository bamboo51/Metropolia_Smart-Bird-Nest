from flask import Flask, Response, render_template, send_file
from camera_stream import generate_frames, streaming_event
import os

app = Flask(__name__)

NO_STREAM_IMAGE_PATH = "./static/image.png"

def start_camera_streaming():
    if not streaming_event.is_set():
        streaming_event.set()

# Serve the HTML page with video stream
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag"""
    if streaming_event.is_set():
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        if os.path.exists(NO_STREAM_IMAGE_PATH):
            return send_file(NO_STREAM_IMAGE_PATH, mimetype='image/png')
        else:
            return "No stream available"
        
def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

