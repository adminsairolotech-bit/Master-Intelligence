#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw + Claude Bridge via OpenRouter
Connect OpenClaw agents to Claude Opus via OpenRouter
"""

import os
import json
import requests
from datetime import datetime

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
OPENCLAW_URL = "http://localhost:18789"

class OpenClawClaudeBridge:
    """Bridge between OpenClaw and Claude Opus via OpenRouter"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.conversation_history = []

    def set_api_key(self, api_key):
        """Set OpenRouter API key"""
        self.api_key = api_key
        print("[OK] OpenRouter API key set")

    def query_claude(self, message, model="anthropic/claude-opus-4.6", system_prompt=None):
        """Send message to Claude Opus via OpenRouter"""
        if not self.api_key:
            return {"error": "OpenRouter API key not set. Use set_api_key()"}

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
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
                OPENROUTER_ENDPOINT,
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

    def query_openclaw(self, message, agent="main"):
        """Send message to OpenClaw agent"""
        try:
            endpoint = f"{OPENCLAW_URL}/api/chat"
            response = requests.post(
                endpoint,
                json={"message": message, "agent": agent},
                timeout=30
            )
            if response.ok:
                return response.json().get("response", "No response")
            return f"OpenClaw error: {response.status_code}"
        except Exception as e:
            return f"OpenClaw connection error: {e}"

    def route_through_openclaw(self, message):
        """Route Claude query through OpenClaw agent"""
        openclaw_response = self.query_openclaw(message)

        enhanced = self.query_claude(
            f"Based on this OpenClaw response:\n{openclaw_response}\n\n"
            f"Provide additional insights:\n{message}"
        )

        return {
            "openclaw": openclaw_response,
            "claude_enhancement": enhanced,
            "timestamp": datetime.now().isoformat()
        }

    def claude_with_openclaw_context(self, message, context=None):
        """Claude with OpenClaw context awareness"""
        system_prompt = """You are an AI assistant with access to OpenClaw automation capabilities.
You can help with:
- Writing and debugging code
- Automating browser tasks
- File operations
- System administration
- General AI assistance

Use OpenClaw when user asks for browser automation or system tasks."""

        if context:
            message = f"Context from OpenClaw: {context}\n\nUser: {message}"

        return self.query_claude(message, system_prompt=system_prompt)


def demo():
    """Demo the bridge"""
    print("=" * 60)
    print("OpenClaw + Claude Opus Bridge")
    print("=" * 60)

    bridge = OpenClawClaudeBridge()

    # Check if API key is available
    if OPENROUTER_API_KEY:
        print("[OK] OpenRouter API key found")
        bridge.set_api_key(OPENROUTER_API_KEY)

        # Test Claude Opus query
        print("\n--- Testing Claude Opus via OpenRouter ---")
        result = bridge.query_claude("Explain Python decorators in 2 sentences")
        if result.get("success"):
            print(f"Claude Opus: {result['response'][:200]}...")
        else:
            print(f"Error: {result.get('error')}")
    else:
        print("[WARN] OpenRouter API key not found in environment")
        print("Set OPENROUTER_API_KEY or use bridge.set_api_key()")

    # Test OpenClaw connection
    print("\n--- Testing OpenClaw Connection ---")
    response = bridge.query_openclaw("Hello, are you there?")
    print(f"OpenClaw: {response[:200] if len(response) > 200 else response}...")

    print("\n" + "=" * 60)
    print("Bridge Ready!")
    print("=" * 60)
    print("""
Usage:
  bridge = OpenClawClaudeBridge()

  # Set API key
  bridge.set_api_key("your-openrouter-key")

  # Query Claude Opus
  result = bridge.query_claude("your question")
  print(result["response"])

  # Query OpenClaw
  response = bridge.query_openclaw("your command")

  # Combined (route through OpenClaw to Claude)
  result = bridge.route_through_openclaw("your question")
    """)


if __name__ == "__main__":
    demo()
