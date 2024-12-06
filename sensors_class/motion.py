import pigpio as GPIO
import time
import datetime
import threading

class MotionDetector:
    def __init__(self, camera_streamer, audio_recorder, bird_detector):
        self.camera = camera_streamer
        self.audio_recorder = audio_recorder
        self.bird_detector = bird_detector
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11, GPIO.IN)
        self.motion_timeout = 30
        self.record_duration = 10

    def _limited_audio_record(self, timestamp):
        self.audio_recorder.start_record(timestamp)
        time.sleep(self.record_duration)
        self.audio_recorder.stop_record()
        self.bird_detector.analyze_bird(timestamp)

    def detect(self):
        no_motion_duration = 0
        while True:
            if GPIO.input(11):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                print("Motion detected at: " + timestamp)

                if not self.camera.streaming_event.is_set():
                    self.camera.start_stream(timestamp)
                
                if not self.audio_recorder.recording_event.is_set():
                    self.camera.save_frame(timestamp)
                    threading.Thread(target=self._limited_audio_record, args=(timestamp,), daemon=True).start()

                no_motion_duration = 0
            else:
                if self.camera.streaming_event.is_set():
                    no_motion_duration += 1
                    if no_motion_duration > self.motion_timeout:
                        print(f"No motion detected for {self.motion_timeout} seconds")
                        self.camera.stop_stream()
                        no_motion_duration = 0
            time.sleep(1)

    def cleanup(self):
        GPIO.cleanup()
        self.camera.stop_stream()