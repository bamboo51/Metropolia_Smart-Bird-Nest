import sounddevice as sd
import numpy as np
import wave
import threading
from sensors.bird_recog import analyze_bird_sound

sample_rate = 48000
channels = 1
frames = []
filename = None
is_recording = False
lock = threading.Lock()
recording_event = threading.Event()
timestamp = None

def start_record(file_name: str):
    global frames, filename, is_recording, timestamp, recording_event
    frames = []  # Reset frames for new recording
    timestamp = file_name
    filename = f"./recordings/audio_{file_name}.wav"
    is_recording = True

    # Start recording in a separate thread
    recording_event.set()
    threading.Thread(target=record_audio_stream, daemon=True).start()
    print("Audio recording started.")

def record_audio_stream():
    global frames, is_recording
    try:
        with sd.InputStream(samplerate=sample_rate, channels=channels, dtype='int16') as stream:
            while is_recording:
                audio_chunk = stream.read(512)[0]  # Read 512 frames
                with lock:
                    frames.append(audio_chunk)
    except Exception as e:
        print(f"Error during recording: {e}")

def stop_record():
    global is_recording, recording_event
    is_recording = False
    save_record()
    print("Audio recording stopped.")
    recording_event.clear()

def save_record():
    global frames, filename, timestamp
    with lock:
        # Combine all recorded chunks into a single NumPy array
        audio_data = np.concatenate(frames, axis=0)

    # Save audio data to a WAV file
    with wave.open(filename, 'w') as f:
        f.setnchannels(channels)
        f.setsampwidth(2)  # 2 bytes per sample (int16)
        f.setframerate(sample_rate)
        f.writeframes(audio_data.tobytes())
    print(f"Audio file saved as {filename}")
    analyze_bird_sound(filename, timestamp)