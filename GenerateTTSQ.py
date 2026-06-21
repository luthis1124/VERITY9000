import os
from pocket_tts import TTSModel, export_model_state
import asyncio
import sounddevice as sd
import numpy as np
import resampy
from multiprocessing import Process, Queue, Event

class GenerateTTSQ:

    def __init__(self,  to_tts: Queue, shutdown_event: Event):
        self.to_tts = to_tts
        self.shutdown_event = shutdown_event
        self.name = "GenerateTTSQ"
        self.output_dir = "my_tts_outputs"
        self.playing = False

        self.tts_model = TTSModel.load_model()
        voice_embedding_path = "./covas.safetensors"  # Choose a good name

        if not os.path.exists(voice_embedding_path):
            print("Exporting voice embedding for the first time... (this may take a few seconds)")
            voice_state = self.tts_model.get_state_for_audio_prompt(audio_conditioning="covas.wav")
            export_model_state(voice_state, voice_embedding_path)

        self.voice_state = self.tts_model.get_state_for_audio_prompt(voice_embedding_path)

    def run(self):
        try:
            while not self.shutdown_event.is_set():
                try:
                    request = self.to_tts.get(timeout=0.5)
                    print(f"[{self.name}] Received request: {request}")
                    if request:
                        asyncio.run(self.play_tts_stream_async(request))
                except Exception as e:
                    pass

        except Exception as e:
            print(f"[{self.name}] Error: {e}")

    async def play_tts_stream_async(self, text: str):
        await asyncio.to_thread(self.play_tts_stream, text)
        # how to:
        #         asyncio.run(self.voice.play_tts_stream_async(ai_to_say))

    def play_tts_stream(self, text: str):
        if not text or not text.strip():
            return

        model_sr = 24000
        device_sr = 48000

        try:
            with sd.OutputStream(
                    samplerate=device_sr,
                    channels=1,
                    dtype='float32',
                    # device=self.device_index,
                    device=9,
                    # device='HD 450BT',
                    latency='high',  # 'low' can be unstable on Linux/PulseAudio
                    blocksize=1024  # let PortAudio choose optimal size
            ) as stream:
                for chunk in self.tts_model.generate_audio_stream(self.voice_state, text):
                    self.playing = True

                    if chunk is None or chunk.numel() == 0:
                        continue

                    # Process chunk
                    audio_np = chunk.numpy().astype(np.float32).squeeze()
                    if audio_np.ndim != 1:
                        audio_np = audio_np.reshape(-1)

                    # Resample
                    if model_sr != device_sr:
                        audio_np = resampy.resample(
                            audio_np, model_sr, device_sr, filter='kaiser_best'
                        )
                        audio_np = np.clip(audio_np, -1.0, 1.0).astype(np.float32)

                    # Make sure it's C-contiguous and correct shape for sounddevice
                    audio_np = np.ascontiguousarray(audio_np.reshape(-1, 1))
                    # Write to the continuous stream
                    stream.write(audio_np)

                sd.wait()
                self.playing = False

        except Exception as e:
            print(f"Stream error: {e}")
