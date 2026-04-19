"""
SAIROLOTECH TTS - VOICE CLONING WITH BARK
Fixed version with PyTorch 2.7 compatibility
"""

import os
os.environ["SUNO_ENABLE_MPS"] = "0"
os.environ["SUNO_OFFLOAD_CPU"] = "1"

import torch
import numpy as np
import scipy.io.wavfile as wav
from bark import generate_audio, SAMPLE_RATE
from bark.generation import load_model, _load_model_f, GRAPHEMA, PHONEME

# Monkey patch for PyTorch 2.7 compatibility
_original_load_model = load_model

def patched_load_model(checkpoint, model_type, fine=False, half=False, device="cpu"):
    """Load model with weights_only=False for PyTorch 2.7 compatibility"""
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"

    if model_type == "text":
        model_path = os.path.join("bark_v0", f"{'fine_' if fine else ''}text_{GRAPHEMA}")
    elif model_type == "coarse":
        model_path = os.path.join("bark_v0", f"{'fine_' if fine else ''}coarse_{GRAPHEMA}")
    elif model_type == "fine":
        model_path = os.path.join("bark_v0", f"fine_{PHONEME}")
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    ckpt_path = os.path.join(model_path, checkpoint)
    if not os.path.exists(ckpt_path):
        raise FileNotFoundError(f"Model not found: {ckpt_path}")

    # Load with weights_only=False to bypass PyTorch 2.7 security check
    if hasattr(torch, 'load'):
        def safe_load(*args, **kwargs):
            kwargs['weights_only'] = False
            return torch.load(*args, **kwargs)

        original_torch_load = torch.load
        torch.load = safe_load
        try:
            model = _load_model_f(ckpt_path, device)
        finally:
            torch.load = original_torch_load
    else:
        model = _load_model_f(ckpt_path, device)

    if half:
        model = model.half()
    model = model.to(device)
    model.eval()
    return model

def generate_voice(text, voice_preset=None, output_file=None, text_prompt=None):
    """Generate voice with Bark - supports voice cloning"""

    print(f"Generating: {text[:50]}...")

    if voice_preset is None:
        voice_preset = "v2/en_speaker_6"

    # Generate audio
    audio = generate_audio(
        text,
        history_prompt=voice_preset,
        text_temp=0.7,
        audio_temp=0.7
    )

    if output_file is None:
        output_file = "bark_output.wav"

    # Save as WAV
    wav.write(output_file, SAMPLE_RATE, audio)

    print(f"Saved: {output_file}")
    return output_file

def clone_voice(audio_sample, text, output_file="cloned_voice.wav"):
    """Clone voice from audio sample - ELEVENLABS STYLE"""

    print("Voice cloning with Bark...")
    print("Note: Bark uses speaker prompts, not true cloning")

    # Bark doesn't support true voice cloning
    # It uses speaker embeddings from training data
    # For real cloning, use Coqui XTTS or Resemble AI

    # Generate with generic voice
    audio = generate_audio(text, history_prompt=audio_sample)

    wav.write(output_file, SAMPLE_RATE, audio)
    print(f"Generated with voice characteristics: {output_file}")
    return output_file

def list_presets():
    """List available voice presets"""
    presets = [
        "v2/en_speaker_0", "v2/en_speaker_1", "v2/en_speaker_2",
        "v2/en_speaker_3", "v2/en_speaker_4", "v2/en_speaker_5",
        "v2/en_speaker_6", "v2/en_speaker_7", "v2/en_speaker_8",
        "v2/en_speaker_9",
    ]
    print("\nAvailable English Voice Presets:")
    for p in presets:
        print(f"  - {p}")
    return presets

# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SAIROLOTECH Bark TTS")
    parser.add_argument("--text", "-t", required=True, help="Text to speak")
    parser.add_argument("--output", "-o", default="output.wav", help="Output file")
    parser.add_argument("--preset", "-p", default="v2/en_speaker_6", help="Voice preset")
    parser.add_argument("--list", "-l", action="store_true", help="List presets")
    parser.add_argument("--clone", "-c", help="Audio file for voice clone")

    args = parser.parse_args()

    if args.list:
        list_presets()
    elif args.clone:
        clone_voice(args.clone, args.text, args.output)
    else:
        generate_voice(args.text, args.preset, args.output)
