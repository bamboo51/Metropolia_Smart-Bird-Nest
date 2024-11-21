from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime

analyzer = Analyzer()

recording = Recording(
    analyzer,
    "audio_20241121_122443.wav",
)
recording.analyze()
print(recording.detections)