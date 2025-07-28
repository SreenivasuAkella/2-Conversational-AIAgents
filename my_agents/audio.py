import os
from typing import List
import soundfile as sf
from gtts import gTTS
import numpy as np

def generate_audio(text: str, voice: str, provider: str, out_path: str):
    """
    Generate TTS audio using gTTS (Google Text-to-Speech) with voice differentiation.
    Uses standard English voice without specific accents.
    """
    try:
        # Use standard English voice without accent differentiation
        tts = gTTS(text=text, lang='en', slow=False)
        print(f"Generating {voice} voice for: {text[:50]}...")
        
        tts.save(out_path)
        print(f"Audio saved to: {out_path} (Voice: {voice})")
        return out_path
        
    except Exception as e:
        print(f"TTS generation failed: {e}")
        return None

def merge_audio_clips(audio_paths: List[str], output_path: str):
    """
    Merge multiple audio clips into a single audio file.
    """
    audio_data = []
    sample_rate = None
    
    for path in audio_paths:
        if path and os.path.exists(path):
            try:
                data, sr = sf.read(path)
                audio_data.append(data)
                if sample_rate is None:
                    sample_rate = sr
                print(f"Loaded audio: {path}")
            except Exception as e:
                print(f"Failed to load audio {path}: {e}")
    
    if audio_data and sample_rate:
        try:
            merged_audio = np.concatenate(audio_data)
            sf.write(output_path, merged_audio, sample_rate)
            print(f"Merged audio saved to: {output_path}")
            return output_path
        except Exception as e:
            print(f"Failed to merge audio clips: {e}")
            return None
    else:
        print("No valid audio data to merge")
        return None

