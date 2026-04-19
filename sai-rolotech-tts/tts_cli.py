"""
SAI ROLOTECH TTS CLI - ElevenLabs Style
Voice synthesis with Hindi/English support
"""

import asyncio
import edge_tts
import argparse
import os
import sys
from pathlib import Path

# Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RED = "\033[91m"
RESET = "\033[0m"

class SaiRolotechTTS:
    def __init__(self):
        self.output_dir = Path("output/tts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def list_voices(self, lang=None):
        """List all available voices"""
        voices = await edge_tts.list_voices()
        voices_found = []

        for voice in voices:
            if lang:
                if voice["Locale"].startswith(lang.lower()):
                    voices_found.append(voice)
            else:
                voices_found.append(voice)

        print(f"\n{GREEN}Available Voices ({len(voices_found)}){RESET}\n")
        print(f"{'Name':<35} {'Language':<12} {'Gender':<8} {'Style'}")
        print("-" * 80)

        for v in voices_found:
            name = v["Name"]
            lang_code = v["Locale"]
            gender = v["FriendlyName"].split()[-1] if v["FriendlyName"] else "N/A"
            styles = ", ".join(v.get("Style", [])[:2]) or "-"
            print(f"{name:<35} {lang_code:<12} {gender:<8} {styles}")

        return voices_found

    async def generate_speech(self, text, voice=None, output=None, speed=1.0, pitch=0):
        """Generate speech from text"""
        if not voice:
            # Default Hindi female voice
            voice = "hi-IN-SwaraNeural"

        if not output:
            # Generate filename from text
            filename = text[:30].replace(" ", "_").replace(",", "").replace("?", "").replace("!", "") + ".mp3"
            output = filename

        output_path = self.output_dir / output

        print(f"\n{BLUE}Generating Speech...{RESET}")
        print(f"  Voice: {voice}")
        print(f"  Text: {text[:50]}...")
        print(f"  Speed: {speed}x")
        print(f"  Output: {output_path}")

        try:
            # Generate with rate and pitch adjustment
            rate = f"{'+' if speed > 1 else '-'}{int(abs(speed - 1) * 50)}%"
            pitch_str = f"{'+' if pitch > 0 else ''}{pitch}Hz"

            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_path))

            file_size = os.path.getsize(output_path)
            print(f"\n{GREEN}SUCCESS!{RESET}")
            print(f"  File: {output_path}")
            print(f"  Size: {file_size} bytes")

            return str(output_path)

        except Exception as e:
            print(f"\n{RED}ERROR: {e}{RESET}")
            return None

    async def generate_batch(self, texts, voice=None, output_dir=None):
        """Generate multiple speeches"""
        if not voice:
            voice = "hi-IN-SwaraNeural"

        if output_dir:
            batch_dir = Path(output_dir)
        else:
            batch_dir = self.output_dir / "batch"
        batch_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{BLUE}Batch Generation ({len(texts)} files){RESET}\n")

        for i, text in enumerate(texts, 1):
            filename = f"speech_{i:03d}.mp3"
            output_path = batch_dir / filename

            print(f"[{i}/{len(texts)}] {text[:50]}...")
            try:
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(str(output_path))
                print(f"  {GREEN}OK{RESET} - {output_path}")
            except Exception as e:
                print(f"  {RED}FAIL{RESET} - {e}")

        print(f"\n{GREEN}Batch Complete!{RESET}")
        print(f"  Output: {batch_dir}")

async def main():
    parser = argparse.ArgumentParser(description="SAI ROLOTECH TTS CLI - ElevenLabs Style")
    parser.add_argument("--text", "-t", help="Text to convert to speech")
    parser.add_argument("--voice", "-v", default="hi-IN-SwaraNeural", help="Voice ID (default: hi-IN-SwaraNeural)")
    parser.add_argument("--output", "-o", help="Output file name")
    parser.add_argument("--list", "-l", action="store_true", help="List all voices")
    parser.add_argument("--lang", help="Filter voices by language (e.g., hi-IN, en-US)")
    parser.add_argument("--speed", "-s", type=float, default=1.0, help="Speech speed (0.5-2.0)")
    parser.add_argument("--pitch", "-p", type=int, default=0, help="Pitch adjustment in Hz")
    parser.add_argument("--batch", "-b", help="Batch file (one text per line)")
    parser.add_argument("--output-dir", help="Output directory for batch")

    args = parser.parse_args()

    tts = SaiRolotechTTS()

    if args.list:
        await tts.list_voices(args.lang)
        return

    if args.batch:
        # Read batch file
        with open(args.batch, "r", encoding="utf-8") as f:
            texts = [line.strip() for line in f if line.strip()]
        await tts.generate_batch(texts, args.voice, args.output_dir)
        return

    if args.text:
        await tts.generate_speech(
            text=args.text,
            voice=args.voice,
            output=args.output,
            speed=args.speed,
            pitch=args.pitch
        )
    else:
        # Interactive mode
        print(f"\n{GREEN}╔══════════════════════════════════════════════════╗{RESET}")
        print(f"{GREEN}║     SAI ROLOTECH TTS CLI - ELEVENLABS STYLE     ║{RESET}")
        print(f"{GREEN}╠══════════════════════════════════════════════════╣{RESET}")
        print(f"{GREEN}║  Type 'quit' to exit                            ║{RESET}")
        print(f"{GREEN}║  Type 'voices' to list voices                   ║{RESET}")
        print(f"{GREEN}║  Type 'voice <name>' to change voice            ║{RESET}")
        print(f"{GREEN}╚══════════════════════════════════════════════════╝{RESET}\n")

        current_voice = args.voice
        print(f"Current voice: {current_voice}")

        while True:
            try:
                text = input("\nEnter text: ").strip()

                if text.lower() == "quit":
                    break
                elif text.lower() == "voices":
                    await tts.list_voices()
                    continue
                elif text.lower().startswith("voice "):
                    current_voice = text[6:].strip()
                    print(f"Voice changed to: {current_voice}")
                    continue
                elif not text:
                    continue

                await tts.generate_speech(text, current_voice)

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break

if __name__ == "__main__":
    asyncio.run(main())
