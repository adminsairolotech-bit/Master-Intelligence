"""
SAIROLOTECH TTS - SILERO VOICE CLONING
100% FREE - No API keys, High quality
"""

import os
import torch
import urllib.request
from pathlib import Path

class SileroTTS:
    """Silero TTS - Free offline voice synthesis"""

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        self.model = None
        self.speaker = None
        self._load_model()

    def _load_model(self):
        """Load Silero model"""
        print("Loading Silero TTS model...")

        try:
            # Import torch hpss
            from torch import hub

            # Download model directly
            model_url = "https://models.silero.ai/models/tts/hi/v3_1_gujarati Hi.zip"

            # Use torch hub - Silero provides this
            self.model, example_text = torch.hub.load(
                repo_or_dir='snakers4/silero-v models',
                model='silero_tts',
                source='github'
            )

            print("Silero model loaded!")
            self.speaker = "hi"
            return True

        except Exception as e:
            print(f"Error loading Silero: {e}")
            return False

    def speak(self, text: str, output_file: str = "output.wav",
              speaker: str = "hi_0", language: str = "hi") -> str:
        """Generate speech with Silero"""

        if not self.model:
            print("Model not loaded!")
            return None

        print(f"Generating: {text[:50]}...")

        # Set speaker
        if hasattr(self.model, 'set_default_speaker'):
            self.model.set_default_speaker(speaker)

        # Generate audio
        audio = self.model.apply_tts(
            text=text,
            speaker=speaker,
            language=language,
            sample_rate=48000
        )

        # Save
        import scipy.io.wavfile as wav
        output_path = os.path.join("output", "tts", output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Convert tensor to numpy
        if hasattr(audio, 'cpu'):
            audio = audio.cpu().numpy()
        elif isinstance(audio, torch.Tensor):
            audio = audio.numpy()

        wav.write(output_path, 48000, audio)
        print(f"Saved: {output_path}")
        return output_path

    def list_languages(self):
        """List available languages"""
        if hasattr(self.model, 'list_languages'):
            return self.model.list_languages()
        return ["hi", "en", "ta", "te", "mr", "bn", "gu", "kn", "ml"]

    def list_speakers(self, language: str = "hi"):
        """List speakers for a language"""
        if hasattr(self.model, 'list_speakers'):
            return self.model.list_speakers(language)
        return ["female", "male"]


def quick_speak(text: str, output_file: str = "silero_output.wav"):
    """Quick speak without class instantiation"""

    try:
        # Direct Silero download
        import urllib.request
        import zipfile

        print("Downloading Silero model...")
        model_dir = Path.home() / ".cache" / "silero"
        model_dir.mkdir(parents=True, exist_ok=True)

        # Load torch
        import torch
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Try loading via torch hub
        model = torch.hub.load(
            'snakers4/silero-v Models',
            'silero_tts',
            trust_repo=True
        )

        # Generate
        audio = model.apply_tts(
            text=text,
            speaker='hindi_female',
            language='hi'
        )

        # Save
        import scipy.io.wavfile as wav
        output_path = os.path.join("output", "tts", output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if hasattr(audio, 'cpu'):
            audio_np = audio.cpu().numpy()
        else:
            audio_np = audio

        wav.write(output_path, 48000, audio_np)
        print(f"SUCCESS: {output_path}")
        return output_path

    except Exception as e:
        print(f"Silero failed: {e}")
        return None


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║            SAIROLOTECH SILERO TTS                              ║
║            100% FREE - Offline voice synthesis                 ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Test
    result = quick_speak("नमस्ते, मैं साई रोलोटेक हूं।", "test_silero.wav")

    if result:
        print("Silero TTS working!")
    else:
        print("Silero failed - use edge-tts or gTTS instead")
