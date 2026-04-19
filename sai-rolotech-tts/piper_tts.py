"""
SAIROLOTECH TTS - PIPER OFFLINE TTS
100% FREE - Download voices, no API needed
"""

import os
import sys
import io
import struct
import wave

# Fix encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def download_voice():
    """Download a Piper voice model"""
    import urllib.request
    import zipfile

    voice_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "piper", "voices")
    os.makedirs(voice_dir, exist_ok=True)

    # Hindi voice
    voice_url = "https://github.com/rhasspy/piper-voices/raw/main/hi/hi_XX/low/hi_XX_low.onnx"
    model_path = os.path.join(voice_dir, "hi_XX_low.onnx")

    if not os.path.exists(model_path):
        print("Downloading Hindi voice model...")
        # Try different mirrors
        mirrors = [
            "https://github.com/rhasspy/piper-voices/raw/main/hi/hi_XX/low/hi_XX_low.onnx",
        ]

        for url in mirrors:
            try:
                print(f"Trying: {url}")
                urllib.request.urlretrieve(url, model_path)
                print(f"Downloaded: {model_path}")
                break
            except Exception as e:
                print(f"Failed: {e}")
                continue
    else:
        print(f"Voice already exists: {model_path}")

    return model_path

def speak(text, output_file="piper_output.wav", voice_path=None):
    """Generate speech with Piper"""

    from piper.voice import PiperVoice
    import numpy as np

    if voice_path is None:
        voice_path = download_voice()

    print(f"Loading voice: {voice_path}")

    try:
        with open(voice_path, 'rb') as f:
            voice = PiperVoice.load(f)

        print(f"Speaking: {text[:50]}...")

        # Generate audio
        audio_stream = voice.synthesize(text)

        # Convert to WAV
        output_path = os.path.join("output", "tts", output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with wave.open(output_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(voice.sample_rate)

            for audio_bytes in audio_stream:
                # Convert bytes to numpy array
                int_data = np.frombuffer(audio_bytes, dtype=np.int16)
                wav_file.writeframes(int_data.tobytes())

        print(f"Saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"Error: {e}")
        return None

def quick_test():
    """Quick test without downloading model"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          SAIROLOTECH PIPER TTS                                ║
║          100% FREE - Offline voices                          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Piper provides high-quality ONNX-based TTS models:           ║
║                                                                  ║
║  VOICES AVAILABLE:                                             ║
║  - Hindi (hi_XX_low)                                           ║
║  - English (en_US)                                              ║
║  - Spanish (es_ES)                                              ║
║  - French (fr_FR)                                               ║
║  - German (de_DE)                                               ║
║  - Many more...                                                 ║
║                                                                  ║
║  USAGE:                                                         ║
║  1. Download voice model first                                  ║
║  2. python piper_tts.py --download                              ║
║  3. python piper_tts.py --speak "Hello world"                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SAIROLOTECH Piper TTS")
    parser.add_argument("--download", action="store_true", help="Download Hindi voice")
    parser.add_argument("--speak", type=str, help="Text to speak")
    parser.add_argument("--output", type=str, default="output.wav", help="Output file")

    args = parser.parse_args()

    if args.download:
        download_voice()
    elif args.speak:
        speak(args.speak, args.output)
    else:
        quick_test()
