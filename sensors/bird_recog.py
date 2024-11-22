from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import sqlite3
import os

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
    print(recording.detections)
    
    try:
        if recording.detections and recording.detections[0]['confidence'] > 0.4:
            species = recording.detections[0]['common_name']
            print(f"Detected bird: {species}")
            image_path = f"./recordings/image_{timestamp}.jpg"
            save_to_database(timestamp, species, audio_path, image_path)
        else:
            os.remove(f"./recordings/image_{timestamp}.jpg")
            os.remove(f"./recordings/audio_{timestamp}.wav")
            print("No bird detected in the recording")
    except IndexError:
        print("Error: No valid detections found")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    '''
    if recording.detections is not None:
        species = recording.detections[0]['common_name']
    

    print(f"Detected bird {species}")
    image_path = f"./recordings/image_{timestamp}.jpg"

    save_to_database(timestamp, species, audio_path, image_path)
    '''

