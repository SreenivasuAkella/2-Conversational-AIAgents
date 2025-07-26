import os
from typing import List
import soundfile as sf
from gtts import gTTS
import numpy as np

def generate_audio(text: str, voice: str, provider: str, out_path: str):
    """
    Placeholder TTS function. Swap with Coqui, ElevenLabs, gTTS.
    """
    try:
        tts = gTTS(text)
        tts.save(out_path)
        return out_path
    except Exception as e:
        print(f"TTS generation failed: {e}")
        return None

def merge_audio_clips(audio_paths: List[str], output_path: str):
    audio_data = []
    sample_rate = None
    for path in audio_paths:
        if path and os.path.exists(path):
            data, sr = sf.read(path)
            audio_data.append(data)
            sample_rate = sr
    if audio_data and sample_rate:
        sf.write(output_path, np.concatenate(audio_data), sample_rate)

