import sounddevice as sd
import numpy as np
import wave
import threading

class AudioRecorder:
    def __init__(self, sample_rate:int=48000, channels:int=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.recorder = None
        self.frames = []

        self.is_recording = False
        self.lock = threading.Lock()
        self.recording_event = threading.Event()
        self.timestamp = None

    def start_record(self, filename:str):
        self.frames = []
        self.timestamp = filename
        self.full_filename = f"./recordings/audio_{filename}.wav"
        self.is_recording = True
        self.recording_event.set()
        threading.Thread(target=self._record_audio, daemon=True).start()
        print("Recording started")

    def _record_audio(self):
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, dtype='int16') as stream:
                while self.is_recording:
                    audio_chunk = stream.read(512)[0]
                    with self.lock:
                        self.frames.append(audio_chunk)
        except Exception as e:
            print(f"Error recording audio: {e}")

    def stop_record(self):
        self.is_recording = False
        self._save_audio()
        print("Recording stopped")
        self.recording_event.clear()
        
    def _save_audio(self):
        with self.lock:
            audio_data = np.concatenate(self.frames, axis=0)
            with wave.open(self.full_filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
            print(f"Audio saved to {self.full_filename}")
            return self.full_filename