#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw + Claude + Telegram Bridge
Connect OpenClaw (via Telegram) to Claude Opus via OpenRouter
"""

import os
import requests
from datetime import datetime

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

class OpenClawBridge:
    """Bridge between OpenClaw (via Telegram) and Claude Opus"""

    def __init__(self):
        self.claude_key = os.getenv("OPENROUTER_API_KEY", "")
        self.telegram_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID

    def send_to_openclaw(self, message):
        """Send message to OpenClaw via Telegram"""
        if not self.telegram_token:
            return {"error": "Telegram bot token not set", "hint": "Set TELEGRAM_BOT_TOKEN"}

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.ok:
                data = response.json()
                return {
                    "success": True,
                    "message_id": data.get("result", {}).get("message_id"),
                    "sent_to": "OpenClaw via Telegram"
                }
            return {"error": f"Telegram error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def query_claude_opus(self, message, model="anthropic/claude-opus-4.6", system_prompt=None):
        """Send message to Claude Opus via OpenRouter"""
        if not self.claude_key:
            return {"error": "Claude API key not set", "hint": "Set OPENROUTER_API_KEY"}

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.claude_key}",
            "HTTP-Referer": "https://sairolotech.com",
            "X-Title": "OpenClaw Claude Bridge"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return {
                "success": True,
                "response": data["choices"][0]["message"]["content"],
                "model": model
            }
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def smart_route(self, message):
        """Smart routing: OpenClaw + Claude Opus combined"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "input": message
        }

        # Try Claude Opus
        if self.claude_key:
            claude_result = self.query_claude_opus(message)
            results["claude_opus"] = claude_result

            # If response is code/technical, also send to OpenClaw
            if any(kw in message.lower() for kw in ["code", "function", "script", "automate", "browser"]):
                openclaw_result = self.send_to_openclaw(
                    f"Claude Opus suggested:\n{claude_result.get('response', '')[:500]}"
                )
                results["openclaw"] = openclaw_result
                results["routed_to"] = "Claude Opus + OpenClaw (code detected)"
            else:
                results["routed_to"] = "Claude Opus"

        # Try OpenClaw
        if self.telegram_token:
            openclaw_result = self.send_to_openclaw(message)
            results["openclaw"] = openclaw_result
            if not results.get("routed_to"):
                results["routed_to"] = "OpenClaw (via Telegram)"

        return results

    def get_updates(self, limit=5):
        """Get recent messages from Telegram (to see OpenClaw responses)"""
        if not self.telegram_token:
            return {"error": "Telegram bot token not set"}

        url = f"https://api.telegram.org/bot{self.telegram_token}/getUpdates"
        params = {"limit": limit, "timeout": 0}

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.ok:
                data = response.json()
                messages = []
                for update in data.get("result", []):
                    msg = update.get("message", {})
                    if msg.get("chat", {}).get("id") == int(self.chat_id) if self.chat_id else True:
                        messages.append({
                            "text": msg.get("text", ""),
                            "date": msg.get("date", "")
                        })
                return {"success": True, "messages": messages}
            return {"error": f"Telegram error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}


def setup_instructions():
    """Show setup instructions"""
    print("""
============================================================
         OpenClaw + Claude Opus Bridge Setup
============================================================

STEP 1: Configure Environment Variables
----------------------------------------
Set these in your environment or .env file:

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
OPENROUTER_API_KEY=your_openrouter_api_key

STEP 2: Connect OpenClaw to Telegram
----------------------------------------
1. Open OpenClaw: http://localhost:18789
2. Go to Channels -> Telegram
3. Link your Telegram bot
4. Start chatting with your bot

STEP 3: Run Bridge
----------------------------------------
python openclaw_chatgpt_telegram.py

STEP 4: Use Smart Routing
----------------------------------------
bridge.smart_route("your message")
-> Automatically routes to Claude Opus and/or OpenClaw

============================================================
    """)


def demo():
    """Demo the bridge"""
    print("=" * 60)
    print("OpenClaw + Claude Opus + Telegram Bridge")
    print("=" * 60)

    bridge = OpenClawBridge()

    # Check configuration
    print("\nConfiguration Status:")
    print(f"  Claude Opus API: {'OK' if bridge.claude_key else 'NOT SET'}")
    print(f"  Telegram Bot: {'OK' if bridge.telegram_token else 'NOT SET'}")
    print(f"  Telegram Chat: {'OK' if bridge.chat_id else 'NOT SET'}")

    if not bridge.claude_key or not bridge.telegram_token:
        print("\n" + "=" * 60)
        setup_instructions()
    else:
        # Test Claude Opus
        print("\n--- Testing Claude Opus ---")
        result = bridge.query_claude_opus("What is 2+2?")
        if result.get("success"):
            print(f"Claude Opus: {result['response']}")
        else:
            print(f"Error: {result.get('error')}")

        # Test Smart Route
        print("\n--- Testing Smart Route ---")
        result = bridge.smart_route("Write a Python hello world function")
        print(f"Routed to: {result.get('routed_to', 'unknown')}")
        if result.get("claude_opus", {}).get("response"):
            print(f"Response: {result['claude_opus']['response'][:150]}...")

    print("\n" + "=" * 60)
    print("Bridge Ready!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
