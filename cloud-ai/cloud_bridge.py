#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud AI Bridge
Multi-Provider AI with Fallback (NO OpenClaw)

CONFIG: cloud-ai/cloud.env
DO NOT MIX WITH openclaw-bridge/openclaw.env
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any

# Load Cloud AI config ONLY
try:
    from dotenv import load_dotenv
    load_dotenv("cloud-ai/cloud.env")
except ImportError:
    pass

# ============================================
# CONFIG - Cloud AI Only
# ============================================
class CloudConfig:
    # Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

    # NVIDIA
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")

    # Gemini Direct
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # OpenRouter (Alternative)
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

    # Cloud Connectors
    DISCORD_WEBHOOK = os.getenv("CLOUD_DISCORD_WEBHOOK", "")
    SLACK_TOKEN = os.getenv("CLOUD_SLACK_TOKEN", "")
    WEBHOOK_URL = os.getenv("CLOUD_WEBHOOK_URL", "")

# ============================================
# CONNECTORS - Cloud Only
# ============================================
class DiscordConnector:
    """Discord Webhook (Cloud)"""
    name = "discord"

    def __init__(self):
        self.webhook_url = CloudConfig.DISCORD_WEBHOOK

    def is_connected(self) -> bool:
        return bool(self.webhook_url)

    def send(self, message: str) -> Dict[str, Any]:
        if not self.webhook_url:
            return {"error": "DISCORD_WEBHOOK not set"}
        try:
            resp = requests.post(self.webhook_url, json={"content": message}, timeout=30)
            return {"success": True} if resp.ok else {"error": f"Discord: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

class SlackConnector:
    """Slack (Cloud)"""
    name = "slack"

    def __init__(self):
        self.token = CloudConfig.SLACK_TOKEN

    def is_connected(self) -> bool:
        return bool(self.token)

    def send(self, message: str, channel: str = "general") -> Dict[str, Any]:
        if not self.token:
            return {"error": "SLACK_TOKEN not set"}
        try:
            resp = requests.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"channel": channel, "text": message},
                timeout=30
            )
            return {"success": True} if resp.json().get("ok") else {"error": "Slack error"}
        except Exception as e:
            return {"error": str(e)}

class WebhookConnector:
    """Generic Webhook (Cloud)"""
    name = "webhook"

    def __init__(self):
        self.url = CloudConfig.WEBHOOK_URL

    def is_connected(self) -> bool:
        return bool(self.url)

    def send(self, message: str) -> Dict[str, Any]:
        if not self.url:
            return {"error": "WEBHOOK_URL not set"}
        try:
            resp = requests.post(self.url, json={"message": message}, timeout=30)
            return {"success": True} if resp.ok else {"error": f"Webhook: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

# ============================================
# AI BRAIN - Multi-Provider Cloud
# ============================================
class CloudAIBrain:
    """
    Cloud AI Brain - Multi-Provider Fallback
    Priority: Groq → NVIDIA → Gemini Direct → OpenRouter
    """

    def __init__(self):
        self.providers = []
        self._setup_providers()

    def _setup_providers(self):
        """Setup all available cloud providers"""

        # 1. Groq (Fastest - FREE Tier)
        groq_key = CloudConfig.GROQ_API_KEY
        if groq_key:
            self.providers.append({
                "name": "Groq (Llama 3.3)",
                "endpoint": "https://api.groq.com/openai/v1/chat/completions",
                "model": "llama-3.3-70b-versatile",
                "headers": {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            })

        # 2. NVIDIA (High Quality)
        nvidia_key = CloudConfig.NVIDIA_API_KEY
        if nvidia_key:
            self.providers.append({
                "name": "NVIDIA (Nemotron)",
                "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
                "model": "nvidia/llama-3.1-nemotron-70b-instruct",
                "headers": {"Authorization": f"Bearer {nvidia_key}", "Content-Type": "application/json"}
            })

        # 3. Gemini Direct (Free Tier)
        gemini_key = CloudConfig.GEMINI_API_KEY
        if gemini_key:
            self.providers.append({
                "name": "Gemini 2.0 Flash",
                "endpoint": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                "model": "gemini-2.0-flash",
                "headers": {"Authorization": f"Bearer {gemini_key}", "Content-Type": "application/json"}
            })

        # 4. OpenRouter (Claude Alternative)
        openrouter_key = CloudConfig.OPENROUTER_API_KEY
        if openrouter_key:
            self.providers.append({
                "name": "OpenRouter (Claude Sonnet)",
                "endpoint": "https://openrouter.ai/api/v1/chat/completions",
                "model": "anthropic/claude-sonnet-4.6",
                "headers": {
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://sairolotech.com",
                    "X-Title": "Cloud Bridge"
                }
            })

    def query(self, message: str, system_prompt: str = "") -> Dict[str, Any]:
        if not self.providers:
            return {"error": "No API keys configured! Set GROQ_API_KEY, NVIDIA_API_KEY, or GEMINI_API_KEY"}

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        for provider in self.providers:
            try:
                payload = {"model": provider["model"], "messages": messages, "temperature": 0.7}
                resp = requests.post(provider["endpoint"], headers=provider["headers"], json=payload, timeout=60)

                if resp.ok:
                    data = resp.json()
                    return {
                        "success": True,
                        "response": data["choices"][0]["message"]["content"],
                        "model": provider["model"],
                        "provider": provider["name"]
                    }
            except Exception as e:
                continue

        return {"error": "All cloud providers failed"}

    def chat(self, message: str) -> str:
        result = self.query(message)
        return result.get("response", result.get("error", "Unknown error"))

    def list_providers(self) -> list:
        return [p["name"] for p in self.providers]

# ============================================
# CLOUD BRIDGE
# ============================================
class CloudBridge:
    """Cloud AI Bridge (No OpenClaw)"""

    def __init__(self):
        self.ai = CloudAIBrain()
        self.connectors = {}
        self._register_connectors()

    def _register_connectors(self):
        if CloudConfig.DISCORD_WEBHOOK:
            self.connectors["discord"] = DiscordConnector()
        if CloudConfig.SLACK_TOKEN:
            self.connectors["slack"] = SlackConnector()
        if CloudConfig.WEBHOOK_URL:
            self.connectors["webhook"] = WebhookConnector()

    def status(self) -> Dict[str, Any]:
        return {
            "system": "Cloud AI Bridge",
            "config": "cloud-ai/cloud.env",
            "ai": {
                "connected": bool(self.ai.providers),
                "providers": self.ai.list_providers()
            },
            "connectors": {name: conn.is_connected() for name, conn in self.connectors.items()}
        }

    def cli(self):
        print("=" * 50)
        print("Cloud AI Bridge (Separate from OpenClaw)")
        print("=" * 50)
        print(f"Config: cloud-ai/cloud.env")
        print(f"Providers: {', '.join(self.ai.list_providers()) or 'NONE'}")
        print("\nCommands: /ai, /send, /status, /quit")
        print("=" * 50)

        while True:
            try:
                cmd = input("\n> ").strip()
                if cmd == "/quit":
                    break
                elif cmd == "/status":
                    print(json.dumps(self.status(), indent=2))
                elif cmd.startswith("/ai "):
                    print(self.ai.chat(cmd[4:]))
                elif cmd.startswith("/send "):
                    parts = cmd.split(" ", 2)
                    if len(parts) >= 3 and parts[1] in self.connectors:
                        print(self.connectors[parts[1]].send(parts[2]))
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    bridge = CloudBridge()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            print("Cloud AI Bridge Test")
            print(json.dumps(bridge.status(), indent=2))
            if bridge.ai.providers:
                result = bridge.ai.query("Say 'Cloud Bridge OK!' in one line")
                print(f"AI: {result.get('response', result.get('error'))}")
                print(f"Provider: {result.get('provider', 'N/A')}")
        elif sys.argv[1] == "--cli":
            bridge.cli()
        else:
            print(bridge.ai.chat(" ".join(sys.argv[1:])))
    else:
        bridge.cli()
