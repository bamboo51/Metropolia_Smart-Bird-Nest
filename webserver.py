import RPi.GPIO as GPIO
import time
import threading
from picamera2 import Picamera2
from flask import Flask, Response, render_template, send_file
import cv2
import os

# Initialize Flask app
app = Flask(__name__)

# Initialize variables
picam2 = Picamera2()
streaming_event = threading.Event()

# Setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)  # PIR motion sensor input
GPIO.setup(13, GPIO.OUT)  # LED output pin

# Start camera configuration
picam2.configure(picam2.create_preview_configuration())

# Path to the placeholder "No Streaming" image
NO_STREAM_IMAGE_PATH = "./static/image.jpg"

def motion_detection():
    no_motion_duration = 0  # Duration without motion
    motion_timeout = 5  # Seconds before stopping stream

    while True:
        motion_detected = GPIO.input(11)
        
        if motion_detected == 1:  # Motion detected
            print("Intruder detected")
            if not streaming_event.is_set():
                start_streaming()  # Start streaming when motion is detected
            GPIO.output(13, 1)  # Turn ON LED
            no_motion_duration = 0  # Reset duration
        else:
            if streaming_event.is_set():
                no_motion_duration += 1
                if no_motion_duration >= motion_timeout:
                    print("No motion detected for 5 seconds. Stopping stream.")
                    stop_streaming()  # Stop streaming if no motion for a while
            GPIO.output(13, 0)  # Turn OFF LED

        time.sleep(1)  # Brief pause

def start_streaming():
    if not streaming_event.is_set():
        picam2.start()  # Start the camera
        streaming_event.set()  # Signal that streaming has started
        print("Streaming started.")

def stop_streaming():
    if streaming_event.is_set():
        picam2.stop()  # Stop the camera
        streaming_event.clear()  # Signal that streaming has stopped
        print("Streaming stopped.")

def generate_frames():
    """Generator function that yields camera frames to be displayed as a video stream."""
    while streaming_event.is_set():
        frame = picam2.capture_array()  # Capture frame
        _, buffer = cv2.imencode('.jpg', frame)  # Convert the frame to JPEG format
        frame_bytes = buffer.tobytes()  # Convert frame to bytes
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')  # Yield frame as an MJPEG stream

# Serve the HTML page with the video stream
@app.route('/')
def index():
    """Serve the HTML page with the video stream."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    if streaming_event.is_set():
        # If streaming is active, return the video feed
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        # If streaming is stopped, return the placeholder "No Streaming" image
        if os.path.exists(NO_STREAM_IMAGE_PATH):
            return send_file(NO_STREAM_IMAGE_PATH, mimetype='image/jpeg')
        else:
            # If the placeholder image is not found, return a simple text message
            return "No streaming available at the moment."

def run_flask():
    """Run the Flask app."""
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

try:
    # Start the motion detection in a separate thread
    motion_thread = threading.Thread(target=motion_detection)
    motion_thread.daemon = True  # Ensure thread exits when main program does
    motion_thread.start()

    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Keep the main program running
    while True:
        time.sleep(0.1)  # Prevent busy waiting

except KeyboardInterrupt:
    print("Exiting on user interrupt.")

finally:
    GPIO.cleanup()  # Ensure GPIO is cleaned up on exit
    stop_streaming()  # Stop the camera
    print("GPIO cleaned up and program exited.")
