from pvrecorder import PvRecorder
import struct
import numpy as np
import wave

sample_rate = 44100
channels = 1
frames = []
recorder = None
filename = None

def start_record(file_name: str):
    global recorder, frames, filename
    frames = []  # Reset frames for new recording
    filename = f"./recordings/audio_{file_name}.wav"
    
    recorder = PvRecorder(frame_length=512, device_index=0)
    recorder.start()
    print("Audio recording started.")

def record_audio_chunk():
    global frames, recorder
    if recorder is not None:
        audio_chunk = recorder.read()
        frames.extend(audio_chunk)
    else:
        print("Recorder not initialized.")

def stop_record():
    global recorder
    if recorder is not None:
        recorder.stop()
        recorder.delete()
        save_record()
        print("Audio recording stopped.")

def save_record():
    global frames, filename

    with wave.open(f'{filename}', 'w') as f:
        f.setparams((1, 2, 16000, 4096, "NONE", "NONE"))
        f.writeframes(struct.pack("h" * len(frames), *frames))
    print(f"Audio file saved as {filename}")