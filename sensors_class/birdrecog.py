from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import sqlite3
import os

class BirdDetector:
    def __init__(self):
        self.analyzer = Analyzer()
        self.db_path = "./database/bird_species.db"

    def save_to_database(self, timestamp, bird_species, audio_path=None, image_path=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bird_species (timestamp, bird_species, audio_path, image_path)
            VALUES (?, ?, ?, ?)
        """, (timestamp, bird_species, audio_path, image_path))
        conn.commit()
        conn.close()

    def analyze_bird(self, timestamp):
        try:
            audio_path = f"./recordings/audio_{timestamp}.wav"
            recording = Recording(self.analyzer, audio_path)
            recording.analyze()

            if recording.detections:
                best_detection = max(recording.detections, key=lambda x: x.get("confidence", 0))
                if best_detection["confidence"] > 0.6:
                    species = best_detection["common_name"]
                    print(f"Detected bird species: {species} with confidence {best_detection['confidence']}")
                    image_path = f"./recordings/image_{timestamp}.jpg"
                    self.save_to_database(timestamp, species, audio_path, image_path)
                else:
                    self._cleanup_files(timestamp)
                    print("No bird detected with sufficient confidence")
            else:
                self._cleanup_files(timestamp)
                print("No bird detected")
        except Exception as e:
            print(f"Error analyzing bird: {e}")

    def _cleanup_files(self, timestamp):
        audio_path = f"./recordings/audio_{timestamp}.wav"
        image_path = f"./recordings/image_{timestamp}.jpg"
        try:
            os.remove(audio_path)
            os.remove(image_path)
        except Exception as e:
            print(f"Error cleaning up files: {e}")