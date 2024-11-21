from flask import Flask, Response, render_template, send_file, jsonify
from flask_bootstrap import Bootstrap5
import sys
sys.path.append("../")
from sensors.camera_stream import generate_frames, streaming_event
import os
from sensors.light_sensor import read_light_sensor
from sensors.temperature import readDHT22
import sqlite3

app = Flask(__name__)
bootstrap = Bootstrap5(app)

NO_STREAM_IMAGE_PATH = "./static/image.png"
        
# Serve the HTML page with video stream
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/streaming')
def streaming():
    return render_template('streaming.html')

@app.route('/light_sensor_status')
def light_sensor_status():
    light_level = read_light_sensor()
    if light_level is not None:
        return jsonify({"light_level": light_level})
    else:
        return jsonify({"light_level": "Error"}), 500


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
        
@app.route('/temp_humd_status')
def temp_humd_status():
    humidity, temperature = readDHT22()
    if humidity is not None and temperature is not None:
        return jsonify({"temperature": temperature, "humidity": humidity})
    else:
        return jsonify({"temperature": "Error", "humidity": "Error"}), 500
    
@app.route('/get_latest')
def get_latest_bird_detections():
    conn = sqlite3.connect('./database/bird_species.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, species, image_path, audio_path
        FROM bird_species
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    latest_bird_detections = cursor.fetchall()

    records = [
        {
            'timestamp': record[0],
            'bird_name': record[1],
            'audio_path': record[2],
            'image_path': record[3]
        } for record in latest_bird_detections
    ]

    conn.close()
    return jsonify(records)

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

