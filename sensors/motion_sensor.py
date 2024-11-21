import RPi.GPIO as GPIO
import threading
import time
from sensors.camera_stream import start_streaming, stop_streaming, streaming_event, save_frame
from sensors.audio_record import start_record, stop_record, record_audio_chunk
from datetime import datetime

def motion_detection():
    # Setup GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN)  # PIR motion sensor input

    no_motion_duration = 0  # Duration without motion
    motion_timeout = 5  # Seconds before stopping stream

    def audio_record_thread():
        while streaming_event.is_set():
            record_audio_chunk()

    while True:
        motion_detected = GPIO.input(11)
        
        if motion_detected == 1:  # Motion detected
            print("Intruder detected")
            if not streaming_event.is_set():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                start_streaming(timestamp)  # Start streaming when motion is detected
                save_frame(timestamp)
                start_record(timestamp)
                threading.Thread(target=audio_record_thread, daemon=True).start()
            no_motion_duration = 0  # Reset duration
        else:
            if streaming_event.is_set():
                no_motion_duration += 1
                if no_motion_duration >= motion_timeout:
                    print("No motion detected for 30 seconds. Stopping stream.")
                    stop_streaming()  # Stop streaming if no motion for a while
                    stop_record()
                    time.sleep(1)
                    # combine_av(timestamp)

        time.sleep(1)  # Brief pause

def stop_all():
    GPIO.cleanup()  # Ensure GPIO is cleaned up on exit
    stop_streaming()  # Stop the camera
