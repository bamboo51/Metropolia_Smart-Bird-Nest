from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import sqlite3

analyzer = Analyzer()

db_path = "./database/bird_species.db"

def analyze_bird_sound(audio_path, image_path=None):
    recording = Recording(analyzer, audio_path)
    recording.analyze()
    
    for detection in recording.detections:
        bird_species = detection["species"]
        confidence = detection["confidence"]
        timestamp = 

