import RPi.GPIO as GPIO
import time
from camera_stream import start_streaming, stop_streaming, streaming_event

def motion_detection():
    # Setup GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN)  # PIR motion sensor input

    no_motion_duration = 0  # Duration without motion
    motion_timeout = 30  # Seconds before stopping stream

    while True:
        motion_detected = GPIO.input(11)
        
        if motion_detected == 1:  # Motion detected
            print("Intruder detected")
            if not streaming_event.is_set():
                start_streaming()  # Start streaming when motion is detected
            no_motion_duration = 0  # Reset duration
        else:
            if streaming_event.is_set():
                no_motion_duration += 1
                if no_motion_duration >= motion_timeout:
                    print("No motion detected for 5 seconds. Stopping stream.")
                    stop_streaming()  # Stop streaming if no motion for a while

        time.sleep(1)  # Brief pause

def stop_all():
    GPIO.cleanup()  # Ensure GPIO is cleaned up on exit
    stop_streaming()  # Stop the camera
