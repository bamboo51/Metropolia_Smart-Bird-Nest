from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime

analyzer = Analyzer()

recording = Recording(
    analyzer,
    "./recordings/audio_20241121_142031.wav",
)
recording.analyze()
print(recording.detections)