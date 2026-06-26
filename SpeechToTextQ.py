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

        # self.recorder = AudioToTextRecorder(
        #     model="small.en",  # ← upgrade
        #     language="en",
        #     input_device_index=9,
        #     sample_rate=16000,
        #     compute_type="float16",  # if GPU
        #     device="cuda",
        #     silero_sensitivity=0.4,
        #     webrtc_sensitivity=2,
        #     post_speech_silence_duration=0.5,
        #     min_length_of_recording=0.6,
        #     pre_recording_buffer_duration=1.0,
        #     normalize_audio=True,
        #     faster_whisper_vad_filter=True,
        #     beam_size=5,
        #     # enable_realtime_transcription=True,  # optional
        # )
        self.recorder = AudioToTextRecorder(
            # model="base",
            model="small",
            # model="medium.en",
            language="en",
            input_device_index=9,
            # sample_rate=TARGET_SR,
            compute_type="float32",
            # compute_type="float16",  # if GPU - tested no work
            # compute_type="int8", #not working
            # device="cuda", #not working
            silero_sensitivity=0.4,
            # webrtc_sensitivity=2,
            silero_deactivity_detection=True,
            post_speech_silence_duration=0.3,
            min_length_of_recording=0.6,
            min_gap_between_recordings=0.2,
            enable_realtime_transcription=False,
            pre_recording_buffer_duration=1.0,  # keep more context before speech starts

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
