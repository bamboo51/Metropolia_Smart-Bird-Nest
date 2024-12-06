from picamera2 import Picamera2
import threading
import cv2

class CameraStreamer:
    def __init__(self):
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration())
        self.streaming_event = threading.Event()
        self.filename = None

    def start_stream(self, filename:str):
        if not self.streaming_event.is_set():
            self.filename = filename
            self.picam2.start()
            self.streaming_event.set()
            print("Streaming started")

    def stop_stream(self):
        if self.streaming_event.is_set():
            self.picam2.stop()
            self.streaming_event.clear()
            print("Streaming stopped")
    
    def save_frame(self, filename:str):
        frame = self.picam2.capture_array()
        image_path = f'./recordings/image_{filename}.jpg'
        cv2.imwrite(image_path, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        print(f"Image saved to {image_path}")
        return image_path
    
    def generate_frames(self):
        while self.streaming_event.is_set():
            frame = cv2.cvtColor(self.picam2.capture_array(), cv2.COLOR_BGR2RGB)
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
