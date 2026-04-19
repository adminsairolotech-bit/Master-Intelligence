#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Opus Bridge
Simple bridge to Claude Opus via OpenRouter
No Telegram or OpenClaw required!
"""

import os
import requests
from datetime import datetime

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv("openclaw_bridge.env")
except ImportError:
    pass

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENCLAW_URL = os.getenv("OPENCLAW_URL", "http://localhost:18789")

class ClaudeBridge:
    """Simple bridge to Claude Opus via OpenRouter"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")

    def set_api_key(self, api_key):
        """Set OpenRouter API key"""
        self.api_key = api_key
        print("[OK] OpenRouter API key set")

    def query(self, message, model="anthropic/claude-opus-4.6", system_prompt=None):
        """Send message to Claude Opus via OpenRouter"""
        if not self.api_key:
            return {"error": "OpenRouter API key not set"}

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://sairolotech.com",
            "X-Title": "Claude Bridge"
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

    def chat(self, message):
        """Simple chat with Claude Opus"""
        result = self.query(message)
        if result.get("success"):
            return result["response"]
        return f"Error: {result.get('error')}"

    def code_review(self, code, language="python"):
        """Code review with Claude Opus"""
        prompt = f"""Review this {language} code and provide feedback:
1. Issues/bugs
2. Improvements
3. Best practices

Code:
```{language}
{code}
```"""
        return self.query(prompt)

    def explain_code(self, code, language="python"):
        """Explain code in detail"""
        prompt = f"""Explain this {language} code line by line:

```{language}
{code}
```"""
        return self.query(prompt)


def demo():
    """Demo the bridge"""
    print("=" * 60)
    print("Claude Opus Bridge (OpenRouter)")
    print("=" * 60)

    bridge = ClaudeBridge()

    # Check API key
    if not OPENROUTER_API_KEY:
        print("\n[WARN] OpenRouter API key not found!")
        print("Set OPENROUTER_API_KEY in openclaw_bridge.env")
        print("Or set it directly: bridge.set_api_key('your-key')")
        return

    print(f"[OK] OpenRouter API key found")
    bridge.set_api_key(OPENROUTER_API_KEY)

    # Test query
    print("\n--- Testing Claude Opus ---")
    result = bridge.query("What is 2+2? Answer in one sentence.")
    if result.get("success"):
        print(f"Claude Opus: {result['response']}")
        print(f"Model: {result['model']}")
    else:
        print(f"Error: {result.get('error')}")

    print("\n" + "=" * 60)
    print("Bridge Ready!")
    print("=" * 60)
    print("""
Usage:
  bridge = ClaudeBridge()

  # Simple chat
  print(bridge.chat("Hello!"))

  # Code review
  review = bridge.code_review("print('hello')", "python")
  print(review)

  # Explain code
  explanation = bridge.explain_code("x = [1, 2, 3]", "python")
  print(explanation)
    """)


if __name__ == "__main__":
    demo()
