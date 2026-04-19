"""
╔══════════════════════════════════════════════════════════════════╗
║          SAIROLOTECH TTS - ALL IN ONE                      ║
║          100% FREE - Hindi, English, Voice Mixing          ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import asyncio
import edge_tts
import gtts

# Setup
OUTPUT_DIR = "output/tts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Available Voices
VOICES = {
    "hi_f": "hi-IN-SwaraNeural",    # Hindi Female
    "hi_m": "hi-IN-MadhurNeural",    # Hindi Male
    "en_f": "en-US-JennyNeural",     # English Female
    "en_m": "en-US-GuyNeural",       # English Male
    "uk_f": "en-GB-SoniaNeural",     # UK Female
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
        # Try edge-tts first
        communicate = edge_tts.Communicate(text, voice_id)
        await communicate.save(path)
    except:
        # Fallback to gTTS
        lang = "hi" if "hi" in voice else "en"
        tts = gtts.gTTS(text=text, lang=lang)
        tts.save(path)

    print(f"Saved: {path}")
    return path

def mix_voices(text1, text2, output="mixed.mp3"):
    """Simulated voice mixing - alternate between 2 voices"""
    path = os.path.join(OUTPUT_DIR, output)

    # Generate both
    f1 = f"{text1[:20].replace(' ', '_')}.mp3"
    f2 = f"{text2[:20].replace(' ', '_')}.mp3"

    asyncio.run(speak(text1, "hi_f", f1))
    asyncio.run(speak(text2, "hi_m", f2))

    # Simple concatenation with pydub
    try:
        from pydub import AudioSegment
        audio1 = AudioSegment.from_mp3(os.path.join(OUTPUT_DIR, f1))
        audio2 = AudioSegment.from_mp3(os.path.join(OUTPUT_DIR, f2))
        mixed = audio1 + audio2
        mixed.export(path, format="mp3")
        print(f"Mixed saved: {path}")
        return path
    except:
        print("pip install pydub for mixing")
        return os.path.join(OUTPUT_DIR, f1)

# CLI
if __name__ == "__main__":
    import sys

    print("""
╔══════════════════════════════════════════════════════════════════╗
║          SAIROLOTECH TTS - SIMPLE CLI                      ║
║          100% FREE                                            ║
╠══════════════════════════════════════════════════════════════════╣
║  Voices: hi_f, hi_m, en_f, en_m, uk_f                      ║
║                                                                  ║
║  Examples:                                                     ║
║    python simple_tts.py hi_f "नमस्ते"                        ║
║    python simple_tts.py en_f "Hello world"                   ║
║    python simple_tts.py --batch                              ║
╚══════════════════════════════════════════════════════════════════╝
    """)

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
        # Demo
        print("Demo:")
        asyncio.run(speak("नमस्ते, मैं साई रोलोटेक हूं।", "hi_f"))
        asyncio.run(speak("Hello, I am SAI Rolotech.", "en_f"))
        print("Done!")
