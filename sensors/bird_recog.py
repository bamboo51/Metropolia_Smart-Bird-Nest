from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import sqlite3

analyzer = Analyzer()

db_path = "./database/bird_species.db"

def save_to_database(timestamp, bird_species, audio_path, image_path=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bird_species (timestamp, species, image_path, audio_path)
        VALUES (?, ?, ?, ?)
    """, (timestamp, bird_species, image_path, audio_path))
    conn.commit()
    conn.close()

def analyze_bird_sound(audio_path, timestamp):
    recording = Recording(analyzer, audio_path)
    recording.analyze()
    
    species = recording.detections[0]['common_name']
    print(f"Detected bird {species}")
    image_path = f"./recordings/image_{timestamp}.jpg"

    save_to_database(timestamp, species, audio_path, image_path)

