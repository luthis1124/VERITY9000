import threading
import sounddevice as sd
import soundfile as sf
import samplerate
import numpy as np
import random

TARGET_SR = 48000  # PipeWire/PulseAudio native rate
# DEVICE_INDEX = 13        # ← your JACK device
device_name = "sink-sunshine-stereo"

class PlayAudioFile:

    def __init__(self):
        self._lock = threading.Lock()  # optional: prevent overlapping sounds
        self.device_index = self.get_hd450_device_index()
        # print(str(self.device_index))

    def get_hd450_device_index(self):
        """Automatically find the Razer Seiren Mini device index"""
        try:
            devices = sd.query_devices()

            for i, device in enumerate(devices):
                name = device['name'].lower()
                # print(name)
                if "hd 450bt" in name:
                    # print(f"✅ HD 450BT index: {i}")
                    # print(f"   Name: {device['name']}")
                    return i

                if device_name in name:
                    # print(f"✅ HD 450BT index: {i}")
                    # print(f"   Name: {device['name']}")
                    return i

            # print("Available output devices:")
            # for i, device in enumerate(devices):
                # if device['max_output_channels'] > 0:
                #     print(f"   {i}: {device['name']}")
            return None

        except Exception as e:
            print(f"Error detecting devices: {e}")
            return None

    def play_status(self):
        is_playing = False
        return is_playing

    def play_voiceack(self, audio_file: str):
        threading.Thread(
            target=self._play_voiceack_sync,
            args=(audio_file,),
            daemon=True
        ).start()

    def _play_voiceack_sync(self, audio_file: str):
        with self._lock:
            self.play_wav(audio_file, delay_seconds=1.0)

    def fuel_alert(self):
        self.play_voiceack('./voiceacks/fuel_alert.wav')

    def welcome_home(self):
        self.play_voiceack('./voiceacks/welcomehome.wav')

    def major_fuel_alert(self):
        self.play_voiceack('./voiceacks/major_fuel_alert.wav')

    def poi_message(self):
        self.play_voiceack('./voiceacks/poi_message.wav')

    def multiple_poi_message(self):
        self.play_voiceack('./voiceacks/multiple_poi_message.wav')

    def unable_service(self):
        self.play_voiceack('./voiceacks/unable_service.wav')

    def no_record(self):
        self.play_voiceack('./voiceacks/no_record.wav')

    def high_threat(self):
        self.play_voiceack('./voiceacks/high_threat.wav')

    def repeat_command(self):
        self.play_voiceack('./voiceacks/repeat_command.wav')

    def heat_alert(self):
        self.play_voiceack('./voiceacks/heat_alert.wav')

    # def fuel_alert(self):
    #     threading.Thread(target=self.fuel_alert_sync, daemon=True).start()
    #
    # def fuel_alert_sync(self):
    #     with self._lock:  # prevent multiple sounds at once if desired
    #         audio_file = './voiceacks/fuel_alert.wav'
    #         self.play_wav(audio_file, delay_seconds=1.0)
    #
    # def welcome_home(self):
    #     threading.Thread(target=self.welcome_home_sync, daemon=True).start()
    #
    # def welcome_home_sync(self):
    #     with self._lock:  # prevent multiple sounds at once if desired
    #         audio_file = './voiceacks/welcomehome.wav'
    #         self.play_wav(audio_file, delay_seconds=1.0)

    def get_random_acknowledgement(self):
        """Returns a random acknowledgement string from a predefined list."""
        options = [
            './voiceacks/yescommander.wav',
            './voiceacks/understoodcommander.wav',
            './voiceacks/commandreceived.wav',
            './voiceacks/affirmative.wav',
            './voiceacks/copythat.wav'
        ]
        return random.choice(options)

    def affirmative(self):
        threading.Thread(target=self.affirmative_sync, daemon=True).start()

    def affirmative_sync(self):
        with self._lock:  # prevent multiple sounds at once if desired
            # audio_file = './voiceacks/yescommander.wav'
            audio_file = self.get_random_acknowledgement()
            self.play_wav(audio_file, delay_seconds=1.0)

    def play_wav(self, path: str, delay_seconds: float = 2.0, block: bool = True):
        threading.Thread(target=self.play_wav_sync, args=(path, delay_seconds, block), daemon=True).start()

    def play_wav_sync(self, path: str, delay_seconds: float = 2.0, block: bool = True):
        with self._lock:
            try:
                data, sr = sf.read(path, dtype="float32")
                print("now playing")
                # Ensure 2D array
                if data.ndim == 1:  # mono
                    data = np.column_stack((data, data))  # duplicate to both channels

                # Resample to target sample rate
                if sr != TARGET_SR:
                    data = samplerate.resample(data, TARGET_SR / sr, "sinc_best")

                # Create silence (now always matching 2 channels)
                silence_samples = int(delay_seconds * TARGET_SR)
                silence = np.zeros((silence_samples, data.shape[1]), dtype="float32")

                # Prepend silence
                data = np.vstack([silence, data])

                # Play
                sd.play(data, TARGET_SR, device=self.device_index, blocking=block)

                if block:
                    sd.wait()
            except Exception as e:
                print("Playback error:", e)



#
# import sounddevice as sd
# import soundfile as sf
# import numpy as np
# import samplerate
# import time
#
#
# class AudioPlayer:
#     def __init__(self):
#         self.is_playing = False  # Track playback state
#         self.last_play_time = 0
#
#     def is_audio_playing(self) -> bool:
#         """Check if any audio is currently playing."""
#         try:
#             # Method 1: Check sounddevice status
#             status = sd.get_status()
#             if status.output_underflow or status.output_overflow:
#                 return False
#             # Alternative: Check if there's an active stream
#             return sd.get_stream() is not None
#         except:
#             # Fallback to internal flag
#             return self.is_playing
#
#     def play_wav(self, path: str, delay_seconds: float = 2.0, block: bool = True):
#         """
#         Play a wav file with optional delay and blocking.
#         Prevents overlapping if audio is already playing.
#         """
#         # Check if audio is currently playing
#         if self.is_audio_playing():
#             print(f"⏳ Audio is currently playing. Skipping: {path}")
#             return False
#
#         try:
#             self.is_playing = True
#             self.last_play_time = time.time()
#
#             data, sr = sf.read(path, dtype="float32")
#
#             # Ensure 2D array (stereo)
#             if data.ndim == 1:
#                 data = np.column_stack((data, data))
#
#             # Resample if needed
#             if sr != TARGET_SR:
#                 data = samplerate.resample(data, TARGET_SR / sr, "sinc_best")
#
#             # Add silence at the beginning
#             silence_samples = int(delay_seconds * TARGET_SR)
#             silence = np.zeros((silence_samples, data.shape[1]), dtype="float32")
#             data = np.vstack([silence, data])
#
#             print(f"▶ Playing: {path}")
#
#             # Play the audio
#             sd.play(data, TARGET_SR, device=DEVICE_INDEX, blocking=block)
#
#             # If non-blocking, wait a bit then reset flag
#             if not block:
#                 time.sleep(len(data) / TARGET_SR)  # Wait for audio to finish
#
#             self.is_playing = False
#             return True
#
#         except Exception as e:
#             print(f"❌ Error playing audio: {e}")
#             self.is_playing = False
#             return False
#
# player = AudioPlayer()
#
# # Safe way to play
# player.play_wav("sounds/alert.wav", delay_seconds=1.5, block=False)
#
# # You can also manually check before playing
# if not player.is_audio_playing():
#     player.play_wav("sounds/scan_complete.wav")
# else:
#     print("Audio is busy, waiting...")