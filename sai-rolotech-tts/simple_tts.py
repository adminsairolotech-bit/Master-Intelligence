"""
SAIROLOTECH TTS - ALL IN ONE
100% FREE - Hindi, English, Voice Mixing
"""

import os
import sys
import io

# Fix encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
import edge_tts
import gtts

# Setup
OUTPUT_DIR = "output/tts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Available Voices
VOICES = {
    "hi_f": "hi-IN-SwaraNeural",
    "hi_m": "hi-IN-MadhurNeural",
    "en_f": "en-US-JennyNeural",
    "en_m": "en-US-GuyNeural",
    "uk_f": "en-GB-SoniaNeural",
}

async def speak(text, voice="hi_f", output=None):
    """Generate speech - async"""
    voice_id = VOICES.get(voice, VOICES["hi_f"])

    if not output:
        safe = text[:30].replace(" ", "_").replace(",", "")
        output = f"{safe}.mp3"

    path = os.path.join(OUTPUT_DIR, output)
    print(f"Speaking: {text[:50]}... [{voice}]")

    try:
        communicate = edge_tts.Communicate(text, voice_id)
        await communicate.save(path)
    except Exception as e:
        print(f"Edge failed: {e}")
        lang = "hi" if "hi" in voice else "en"
        tts = gtts.gTTS(text=text, lang=lang)
        tts.save(path)

    print(f"Saved: {path}")
    return path

def main():
    print("\n" + "="*60)
    print("SAIROLOTECH TTS - SIMPLE CLI")
    print("="*60)
    print("Voices: hi_f, hi_m, en_f, en_m, uk_f")
    print("\nExamples:")
    print("  python simple_tts.py hi_f 'Namaskar'")
    print("  python simple_tts.py en_f 'Hello world'")
    print("="*60 + "\n")

    if len(sys.argv) > 2:
        voice = sys.argv[1]
        text = sys.argv[2]
        asyncio.run(speak(text, voice))
    elif len(sys.argv) > 1 and sys.argv[1] == "--batch":
        print("Enter texts (Ctrl+C to finish):")
        try:
            i = 1
            while True:
                text = input(f"{i}. ")
                asyncio.run(speak(text))
                i += 1
        except KeyboardInterrupt:
            print("\nDone!")
    else:
        print("Demo:")
        asyncio.run(speak("Namaskar, main SAI Rolotech hoon.", "hi_f"))
        asyncio.run(speak("Hello, I am SAI Rolotech.", "en_f"))
        print("\nDone!")

if __name__ == "__main__":
    main()
