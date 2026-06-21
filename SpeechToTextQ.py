from RealtimeSTT import AudioToTextRecorder
from multiprocessing import Queue, Event
import sounddevice as sd # not used but necessary for STT

DEVICE_INDEX = 11
TARGET_SR = 48000

# TODO: always select pulseaudio device index

class SpeechToTextQ:

    def __init__(self, send_to_vci: Queue, shutdown_event: Event):
        self.send_to_vci = send_to_vci
        self.shutdown_event = shutdown_event
        self.name = "SpeechToTextQ"

        self.recorder = AudioToTextRecorder(
            model="base",
            # model="small",
            language="en",
            input_device_index=9,
            # sample_rate=TARGET_SR,
            silero_sensitivity=0.2,
            webrtc_sensitivity=1,
            post_speech_silence_duration=0.2,
            min_length_of_recording=0.4,
            min_gap_between_recordings=0.2,
            enable_realtime_transcription=False,
            compute_type="float32"
        )

    def run(self):
        while not self.shutdown_event.is_set():
            text = self.recorder.text()
            if text and text.strip():
                clean_text = text.strip().lower()
                print(f"Heard: {clean_text}")
                try:
                    self.send_to_vci.put(clean_text)
                except Exception as e:
                    print(f"[{self.name}] Error: {e}")
