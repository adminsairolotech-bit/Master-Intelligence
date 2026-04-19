#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenRouter Bridge - SAI ROLO TECH
Dedicated OpenRouter AI with Model Priority

CONFIG: openrouter.env
DO NOT MIX WITH other configs
"""

import os
import sys
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load OpenRouter config ONLY
load_dotenv("openrouter.env")


class OpenRouterConfig:
    """OpenRouter Configuration"""

    API_KEY = os.getenv("OPENROUTER_API_KEY", "")

    # MODEL PRIORITY:
    # 1. Light Tasks → Flash 2.0 (FREE)
    # 2. Heavy Tasks → Opus 4.7 (Personal Key - PAID)

    MODELS = {
        "flash": "google/gemini-2.0-flash-exp",
        "haiku": "anthropic/claude-3.5-haiku-20241022",
        "sonnet": "anthropic/claude-sonnet-4.6",
        "opus": "anthropic/opus-4.7",
    }

    ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
    TIMEOUT = 60


class OpenRouterBridge:
    """OpenRouter AI Bridge"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OpenRouterConfig.API_KEY
        self.endpoint = OpenRouterConfig.ENDPOINT

    def _get_headers(self, model: str) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sairolotech.com",
            "X-Title": "SAI ROLO TECH"
        }

    def query(
        self,
        message: str,
        system_prompt: str = "",
        model_type: str = "flash"
    ) -> Dict[str, Any]:
        """Query OpenRouter with model selection

        Args:
            message: User message
            system_prompt: Optional system prompt
            model_type: "flash" (free) or "opus" (paid/heavy)
        """
        if not self.api_key:
            return {"error": "OPENROUTER_API_KEY not set in openrouter.env"}

        model = OpenRouterConfig.MODELS.get(model_type, OpenRouterConfig.MODELS["flash"])

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7
            }
            headers = self._get_headers(model)

            resp = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=OpenRouterConfig.TIMEOUT
            )

            if resp.ok:
                data = resp.json()
                return {
                    "success": True,
                    "response": data["choices"][0]["message"]["content"],
                    "model": model,
                    "model_type": model_type
                }
            else:
                return {"error": f"OpenRouter error: {resp.status_code}", "details": resp.text}

        except Exception as e:
            return {"error": str(e)}

    def flash(self, message: str, system_prompt: str = "") -> Dict[str, Any]:
        """Light tasks - Flash 2.0 (FREE)"""
        return self.query(message, system_prompt, model_type="flash")

    def opus(self, message: str, system_prompt: str = "") -> Dict[str, Any]:
        """Heavy tasks - Opus 4.7 (PAID)"""
        return self.query(message, system_prompt, model_type="opus")

    def auto(self, message: str, system_prompt: str = "") -> Dict[str, Any]:
        """Auto-select based on task complexity"""
        # Simple heuristic: short message = light, long = heavy
        if len(message.split()) < 100:
            return self.flash(message, system_prompt)
        return self.opus(message, system_prompt)


def main():
    """CLI Interface"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenRouter Bridge - SAI ROLO TECH")
    parser.add_argument("message", help="Message to send")
    parser.add_argument("--system", "-s", default="", help="System prompt")
    parser.add_argument(
        "--model", "-m",
        choices=["flash", "haiku", "sonnet", "opus"],
        default="flash",
        help="Model type (flash=free, opus=paid)"
    )

    args = parser.parse_args()

    bridge = OpenRouterBridge()

    if args.model == "flash":
        result = bridge.flash(args.message, args.system)
    elif args.model == "opus":
        result = bridge.opus(args.message, args.system)
    else:
        result = bridge.query(args.message, args.system, args.model)

    if result.get("success"):
        print(f"\n✅ [{result['model_type'].upper()}] Response:")
        print("-" * 50)
        print(result["response"])
        print("-" * 50)
        print(f"Model: {result['model']}")
    else:
        print(f"\n❌ Error: {result.get('error')}")


if __name__ == "__main__":
    main()
