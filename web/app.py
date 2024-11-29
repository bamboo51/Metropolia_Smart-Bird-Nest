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
# Define parent directory path
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORDINGS_DIR = os.path.join(PARENT_DIR, 'recordings')
bootstrap = Bootstrap5(app)

NO_STREAM_IMAGE_PATH = "./static/image.png"
        
# Serve the HTML page with video stream
@app.route('/recordings/<path:filename>')
def serve_recording(filename):
    try:
        return send_file(os.path.join(RECORDINGS_DIR, filename))
    except Exception as e:
        print(f"Error serving file {filename}: {e}")
        return "File not found", 404

@app.route('/')
def index():
    components = [
        {
            'icon': 'cpu-fill',
            'title': 'Raspberry Pi',
            'description': 'High-performance Microcontroller'
        },
        {
            'icon': 'wifi',
            'title': 'Motion Sensor',
            'description': 'Detects movement and triggers actions'
        },
        {
            'icon': 'brightness-high-fill',
            'title': 'Light Sensor',
            'description': 'Measure ambient light levels'
        },
        {
            'icon': 'thermometer-half',
            'title': 'Temperature Sensor',
            'description': 'Measure ambient temperature'
        },
        {
            'icon': 'droplet-fill',
            'title': 'Humidity Sensor',
            'description': 'Measure ambient humidity'
        }
    ]

    features = [
        
    ]
    return render_template('index.html', components=components, features=features)

@app.route('/streaming')
def streaming():
    return render_template('streaming.html')

@app.route('/records')
def show_records():
    return render_template('record.html')
    
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
    try:
        db_path = os.path.join(PARENT_DIR, 'database', 'bird_species.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, species, image_path, audio_path
            FROM bird_species
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        latest_bird_detections = cursor.fetchall()
        
        records = []
        for record in latest_bird_detections:
            # Convert file paths to web URLs
            image_path = f"/recordings/{os.path.basename(record[2])}"
            audio_path = f"/recordings/{os.path.basename(record[3])}"
            
            records.append({
                'timestamp': record[0],
                'bird_name': record[1],
                'image_path': image_path,
                'audio_path': audio_path
            })
        
        conn.close()
        return jsonify(records)
    except Exception as e:
        print(f"Error fetching bird detections: {e}")
        return jsonify({"error": str(e)}), 500

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

