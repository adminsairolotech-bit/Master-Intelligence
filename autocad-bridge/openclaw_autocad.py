#!/usr/bin/env python3
"""
OpenClaw AutoCAD Bridge - Telegram to AutoCAD
Connects OpenClaw chat to AutoCAD drawing generation
"""
import os
import sys
import json
import subprocess
from datetime import datetime

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(__file__))

from autocad_scr_generator import RollFormingSCRGenerator
from autocad_config import C_CHANNEL_SIZES

SCR_DIR = os.path.dirname(__file__)
TELEGRAM_BOT_TOKEN = "8654705929:AAFYXxRbZvrL__ZCFIKlhmLjdW37DWQH7Sw"

def get_c_channel_config(size_name: str) -> dict:
    """Get C-Channel config from list"""
    for cfg in C_CHANNEL_SIZES:
        if cfg["name"] == size_name:
            return cfg
    return C_CHANNEL_SIZES[3]  # Default C-150

def parse_drawing_request(text: str) -> dict:
    """Parse natural language request into drawing parameters"""
    text = text.lower()

    # C-Channel patterns
    if "c-channel" in text or "c channel" in text or "c100" in text or "c-100" in text:
        size = "C-100"
        if any(x in text for x in ["150", "c150", "c-150"]):
            size = "C-150"
        elif any(x in text for x in ["250", "c250", "c-250"]):
            size = "C-250"
        elif any(x in text for x in ["75", "c75", "c-75"]):
            size = "C-75"

        cfg = get_c_channel_config(size)
        return {
            "type": "c-channel",
            "web": cfg["web"],
            "flange": cfg["flange"],
            "lip": cfg["lip"],
            "thickness": cfg["thickness"],
            "scale": 1
        }

    # Z-Purlin patterns
    elif "z-purlin" in text or "z purlin" in text or "z100" in text:
        return {"type": "z-purlin", "web": 100, "flange": 50, "lip": 15, "thickness": 2}

    # Shaft patterns
    elif "shaft" in text or "axle" in text:
        import re

        # Extract diameter first - look for "50mm" or "50 mm"
        diameter_match = re.search(r'(\d+)\s*mm', text)
        if diameter_match:
            diameter = int(diameter_match.group(1))
        else:
            diameter = 50  # Default

        # Extract length - look for "length 350" or just a number after diameter
        length_match = re.search(r'length[:\s]+(\d+)', text)
        if length_match:
            length = int(length_match.group(1))
        else:
            # Try to find second number if diameter already extracted
            all_numbers = re.findall(r'\d+', text)
            if len(all_numbers) > 1:
                length = int(all_numbers[1])
            else:
                length = 350  # Default

        return {"type": "shaft", "diameter": diameter, "length": length}

    # Bearing patterns
    elif "bearing" in text:
        return {"type": "bearing", "model": "6310"}

    # Roll patterns
    elif "roll" in text and "die" in text:
        return {"type": "rolls", "stations": 8}

    # Flower pattern
    elif "flower" in text:
        stations = 8
        import re
        match = re.search(r'(\d+)', text)
        if match:
            stations = int(match.group(1))
        return {"type": "flower", "stations": stations}

    # All drawings
    elif "all" in text or "complete" in text:
        return {"type": "all"}

    # Default to C-Channel
    return {"type": "c-channel", "web": 150, "flange": 50, "lip": 15, "thickness": 2}

def generate_scr(params: dict) -> str:
    """Generate SCR file content"""
    gen = RollFormingSCRGenerator()

    drawing_type = params.get("type", "c-channel")

    if drawing_type == "c-channel":
        gen.c_channel(
            web=params.get("web", 150),
            flange=params.get("flange", 50),
            lip=params.get("lip", 15),
            thickness=params.get("thickness", 2),
            scale=params.get("scale", 1)
        )
    elif drawing_type == "z-purlin":
        gen.z_purlin(
            web=params.get("web", 100),
            flange=params.get("flange", 50),
            lip=params.get("lip", 15),
            thickness=params.get("thickness", 2)
        )
    elif drawing_type == "shaft":
        gen.shaft_side_view(
            diameter=params.get("diameter", 50),
            length=params.get("length", 350)
        )
        gen.shaft_front_view(diameter=params.get("diameter", 50))
    elif drawing_type == "bearing":
        gen.bearing_detail(bearing=params.get("model", "6310"))
    elif drawing_type == "flower":
        gen.flower_pattern(num_passes=params.get("stations", 8))
    elif drawing_type == "rolls":
        gen.roll_assembly(num_passes=params.get("stations", 8))
    else:
        gen.c_channel(web=150, flange=50, lip=15, thickness=2)

    return gen.generate()

def save_and_execute(content: str, filename: str) -> bool:
    """Save SCR file and execute in AutoCAD"""
    filepath = os.path.join(SCR_DIR, filename)

    # Write SCR file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[OK] Saved: {filepath}")

    # Execute in AutoCAD via batch
    autocad_script = os.path.join(SCR_DIR, "run_autocad.bat")
    with open(autocad_script, 'w') as f:
        f.write(f'@echo off\n')
        f.write(f'echo Running {filename} in AutoCAD...\n')
        f.write(f'script "{filepath}"\n')
        f.write(f'echo DONE\n')
        f.write(f'pause\n')

    # Try to execute
    try:
        # Check if AutoCAD is available
        result = subprocess.run(
            ['where', 'acad'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            acad_path = result.stdout.strip().split('\n')[0]
            print(f"[INFO] AutoCAD found: {acad_path}")
            # Would launch: subprocess.Popen([acad_path, '/b', filepath])
            return True
        else:
            print("[INFO] AutoCAD not in PATH - SCR file ready for manual execution")
            return True
    except Exception as e:
        print(f"[WARN] Could not launch AutoCAD: {e}")
        return True

def process_telegram_message(_chat_id: int, text: str) -> str:
    """Process incoming Telegram message"""
    print(f"\n{'='*50}")
    print(f"[MSG] {text}")
    print(f"{'='*50}")

    # Parse request
    params = parse_drawing_request(text)
    print(f"[PARSE] {json.dumps(params)}")

    # Generate SCR
    content = generate_scr(params)

    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rollform_{params['type']}_{timestamp}.scr"

    # Save and execute
    success = save_and_execute(content, filename)

    if success:
        return f"Drawing created!\n\nType: {params['type'].upper()}\nFile: {filename}\n\nOpen AutoCAD and run:\nSCRIPT → {filename}"
    else:
        return "Error generating drawing. Please try again."

# CLI Mode
if __name__ == "__main__":
    print("+" + "="*50 + "+")
    print("|  OpenClaw AutoCAD Bridge - Roll Forming  |")
    print("+" + "="*50 + "+")
    print()

    # Interactive mode
    print("Enter drawing request (or 'quit' to exit):")
    print("Examples:")
    print("  • Draw C-Channel C-150 profile")
    print("  • Generate shaft 50mm length 350")
    print("  • Create flower pattern 10 stations")
    print("  • Draw bearing 6310")
    print()

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not user_input:
                continue

            response = process_telegram_message(chat_id=0, text=user_input)
            print(f"\nBot: {response}")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")

# Telegram webhook handler
def telegram_webhook(request):
    """Cloud Function / Webhook handler for Telegram"""
    update = request.get_json()

    if 'message' not in update:
        return {"ok": True}

    chat_id = update['message']['chat']['id']
    text = update['message'].get('text', '')

    response = process_telegram_message(chat_id, text)

    # Send reply (requires telegram library or API call)
    return {"ok": True, "sent": response}
