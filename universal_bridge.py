#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal OpenClaw Bridge
Connect any app to OpenClaw + Claude Opus
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any

# ============================================
# CONFIGURATION
# ============================================
def get_openclaw_config():
    """Get Telegram token from OpenClaw config"""
    openclaw_config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    try:
        if os.path.exists(openclaw_config_path):
            with open(openclaw_config_path, 'r') as f:
                config = json.load(f)
                telegram = config.get("channels", {}).get("telegram", {})
                if telegram.get("botToken"):
                    return telegram.get("botToken")
    except:
        pass
    return ""

class Config:
    # OpenClaw
    OPENCLAW_URL = os.getenv("OPENCLAW_URL", "http://localhost:18789")
    OPENCLAW_TOKEN = os.getenv("OPENCLAW_TOKEN", "")

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # WhatsApp
    WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "")
    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
    WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "")

    # Slack
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "")

    # Discord
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
    DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID", "")

    # WhatsApp Business API (Ultramsg)
    ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN", "")
    ULTRAMSG_INSTANCE = os.getenv("ULTRAMSG_INSTANCE", "")

    # OpenRouter (Claude Opus)
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

    # Bridge settings
    DEFAULT_MODEL = "anthropic/claude-opus-4.6"
    TIMEOUT = 60

# ============================================
# CONNECTORS - App Integration Layer
# ============================================
class Connector:
    """Base connector class"""
    name = "base"

    def send(self, message: str) -> Dict[str, Any]:
        raise NotImplementedError

    def receive(self) -> Optional[str]:
        raise NotImplementedError

    def is_connected(self) -> bool:
        raise NotImplementedError

class TelegramConnector(Connector):
    """Connect via Telegram bot"""
    name = "telegram"

    def __init__(self, bot_token: str = "", chat_id: str = ""):
        self.bot_token = bot_token or get_openclaw_config()
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else ""
        self._last_update_id = 0

    def is_connected(self) -> bool:
        if not self.bot_token:
            return False
        try:
            resp = requests.get(f"{self.base_url}/getMe", timeout=5)
            return resp.ok
        except:
            return False

    def send(self, message: str, chat_id: str = "") -> Dict[str, Any]:
        target_chat = chat_id or self.chat_id
        if not self.bot_token:
            return {"error": "Telegram bot token not set"}
        if not target_chat:
            return {"error": "TELEGRAM_CHAT_ID not set - Message the bot first to get your Chat ID"}

        try:
            resp = requests.post(
                f"{self.base_url}/sendMessage",
                json={"chat_id": int(target_chat), "text": message},
                timeout=30
            )
            if resp.ok:
                return {"success": True, "data": resp.json()}
            return {"error": f"Telegram error: {resp.status_code} - {resp.text}"}
        except Exception as e:
            return {"error": str(e)}

    def receive(self) -> Optional[str]:
        """Get recent messages (skip if OpenClaw is using Telegram)"""
        # Note: If OpenClaw is running, it handles Telegram polling
        # This method returns None to avoid conflicts
        return None

    def get_chat_id(self) -> Optional[str]:
        """Get chat ID from recent messages"""
        try:
            resp = requests.get(
                f"{self.base_url}/getUpdates",
                params={"limit": 5, "offset": self._last_update_id + 1},
                timeout=5
            )
            if resp.ok:
                data = resp.json()
                updates = data.get("result", [])
                if updates:
                    update = updates[-1]
                    self._last_update_id = update.get("update_id", 0)
                    msg = update.get("message", {})
                    return str(msg.get("chat", {}).get("id", ""))
        except:
            pass
        return None

class OpenClawConnector(Connector):
    """Connect via OpenClaw gateway"""
    name = "openclaw"

    def __init__(self, url: str = "", token: str = ""):
        self.url = url or Config.OPENCLAW_URL
        self.token = token or Config.OPENCLAW_TOKEN

    def is_connected(self) -> bool:
        try:
            resp = requests.get(f"{self.url}/health", timeout=5)
            return resp.ok
        except:
            return False

    def send(self, message: str) -> Dict[str, Any]:
        try:
            headers = {"Content-Type": "application/json"}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"

            resp = requests.post(
                f"{self.url}/api/chat",
                headers=headers,
                json={"message": message, "agent": "main"},
                timeout=30
            )
            if resp.ok:
                return {"success": True, "data": resp.json()}
            return {"error": f"OpenClaw error: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def receive(self) -> Optional[str]:
        return None  # OpenClaw handles this internally

class APConnector(Connector):
    """Local HTTP API connector"""
    name = "api"

    def __init__(self, port: int = 8080):
        self.port = port
        self.base_url = f"http://localhost:{port}"

    def is_connected(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            return resp.ok
        except:
            return False

    def send(self, message: str) -> Dict[str, Any]:
        try:
            resp = requests.post(
                f"{self.base_url}/webhook",
                json={"message": message},
                timeout=30
            )
            if resp.ok:
                return {"success": True, "data": resp.json()}
            return {"error": f"API error: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def receive(self) -> Optional[str]:
        return None

class WhatsAppConnector(Connector):
    """Connect via WhatsApp (Ultramsg API)"""
    name = "whatsapp"

    def __init__(self, token: str = "", instance: str = ""):
        self.token = token or Config.ULTRAMSG_TOKEN
        self.instance = instance or Config.ULTRAMSG_INSTANCE
        self.base_url = f"https://api.ultramsg.com/{self.instance}"

    def is_connected(self) -> bool:
        if not self.token or not self.instance:
            return False
        try:
            resp = requests.get(f"{self.base_url}/instance/connect", timeout=5)
            return resp.ok
        except:
            return False

    def send(self, message: str, to: str = "") -> Dict[str, Any]:
        if not self.token or not self.instance:
            return {"error": "Ultramsg token/instance not set"}

        target = to or Config.WHATSAPP_PHONE
        if not target:
            return {"error": "WHATSAPP_PHONE not set"}

        try:
            resp = requests.post(
                f"{self.base_url}/messages/chat",
                data={
                    "token": self.token,
                    "to": target,
                    "body": message
                },
                timeout=30
            )
            if resp.ok:
                return {"success": True, "data": resp.json()}
            return {"error": f"WhatsApp error: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def receive(self) -> Optional[str]:
        return None

class SlackConnector(Connector):
    """Connect via Slack"""
    name = "slack"

    def __init__(self, token: str = "", channel: str = ""):
        self.token = token or Config.SLACK_BOT_TOKEN
        self.channel = channel or Config.SLACK_CHANNEL
        self.base_url = "https://slack.com/api"

    def is_connected(self) -> bool:
        if not self.token:
            return False
        try:
            resp = requests.get(
                f"{self.base_url}/auth.test",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            return resp.ok and resp.json().get("ok", False)
        except:
            return False

    def send(self, message: str, channel: str = "") -> Dict[str, Any]:
        if not self.token:
            return {"error": "SLACK_BOT_TOKEN not set"}

        target = channel or self.channel
        if not target:
            return {"error": "SLACK_CHANNEL not set"}

        try:
            resp = requests.post(
                f"{self.base_url}/chat.postMessage",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"channel": target, "text": message},
                timeout=30
            )
            if resp.ok and resp.json().get("ok"):
                return {"success": True}
            return {"error": f"Slack error: {resp.json().get('error', 'Unknown')}"}
        except Exception as e:
            return {"error": str(e)}

    def receive(self) -> Optional[str]:
        return None

class DiscordConnector(Connector):
    """Connect via Discord Webhook"""
    name = "discord"

    def __init__(self, webhook_url: str = ""):
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL", "")

    def is_connected(self) -> bool:
        if not self.webhook_url:
            return False
        try:
            resp = requests.get(self.webhook_url.rsplit('/', 1)[0] + "/webhooks", timeout=5)
            return True  # Webhook URLs don't have a health check
        except:
            return bool(self.webhook_url)

    def send(self, message: str) -> Dict[str, Any]:
        if not self.webhook_url:
            return {"error": "DISCORD_WEBHOOK_URL not set"}

        try:
            resp = requests.post(
                self.webhook_url,
                json={"content": message},
                timeout=30
            )
            if resp.ok:
                return {"success": True}
            return {"error": f"Discord error: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def receive(self) -> Optional[str]:
        return None

class WebhookConnector(Connector):
    """Generic webhook connector"""
    name = "webhook"

    def __init__(self, url: str = ""):
        self.url = url or os.getenv("BRIDGE_WEBHOOK_URL", "")

    def is_connected(self) -> bool:
        return bool(self.url)

    def send(self, message: str) -> Dict[str, Any]:
        if not self.url:
            return {"error": "BRIDGE_WEBHOOK_URL not set"}

        try:
            resp = requests.post(
                self.url,
                json={"message": message, "timestamp": datetime.now().isoformat()},
                timeout=30
            )
            if resp.ok:
                return {"success": True, "data": resp.json()}
            return {"error": f"Webhook error: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def receive(self) -> Optional[str]:
        return None

# ============================================
# AI BRAIN - Multi-Provider with Fallback
# ============================================
class AIBrain:
    """
    AI Brain with automatic fallback:
    1. Claude Opus via OpenRouter
    2. Groq (Llama/Mixtral)
    3. NVIDIA (Llama/Nemotron)
    4. Gemini via OpenRouter-compatible endpoint
    """

    def __init__(self, api_key: str = ""):
        self.config = Config()
        self.providers = []
        self._setup_providers()

    @property
    def api_key(self) -> str:
        """For backward compatibility"""
        return self.providers[0]["key"] if self.providers else ""

    def _setup_providers(self):
        """Setup all available providers with fallback order"""
        # 1. OpenRouter (Claude Opus 4.6)
        openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
        if openrouter_key and openrouter_key != "your_openrouter_api_key_here":
            self.providers.append({
                "name": "OpenRouter (Claude Opus 4.6)",
                "key": openrouter_key,
                "endpoint": "https://openrouter.ai/api/v1/chat/completions",
                "model": "anthropic/claude-opus-4.6",
                "fallback_model": "anthropic/claude-sonnet-4.6",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openrouter_key}",
                    "HTTP-Referer": "https://sairolotech.com",
                    "X-Title": "Universal Bridge"
                }
            })

        # 2. Groq Direct (Fast Llama/Mixtral)
        groq_key = os.getenv("GROQ_API_KEY", "")
        if groq_key and groq_key != "your_groq_api_key_here":
            self.providers.append({
                "name": "Groq (Llama 3.3)",
                "key": groq_key,
                "endpoint": "https://api.groq.com/openai/v1/chat/completions",
                "model": "llama-3.3-70b-versatile",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {groq_key}"
                }
            })
        elif openrouter_key:
            # Groq via OpenRouter
            self.providers.append({
                "name": "Groq (Llama 3.3)",
                "key": openrouter_key,
                "endpoint": "https://openrouter.ai/api/v1/chat/completions",
                "model": "groq/llama-3.3-70b-versatile",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openrouter_key}",
                    "HTTP-Referer": "https://sairolotech.com",
                    "X-Title": "Universal Bridge"
                }
            })

        # 3. NVIDIA Direct
        nvidia_key = os.getenv("NVIDIA_API_KEY", "")
        if nvidia_key and nvidia_key != "your_nvidia_api_key_here":
            self.providers.append({
                "name": "NVIDIA (Nemotron)",
                "key": nvidia_key,
                "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
                "model": "nvidia/llama-3.1-nemotron-70b-instruct",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {nvidia_key}"
                }
            })
        elif openrouter_key:
            # NVIDIA via OpenRouter
            self.providers.append({
                "name": "NVIDIA (Nemotron)",
                "key": openrouter_key,
                "endpoint": "https://openrouter.ai/api/v1/chat/completions",
                "model": "nvidia/llama-3.1-nemotron-70b-instruct",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openrouter_key}",
                    "HTTP-Referer": "https://sairolotech.com",
                    "X-Title": "Universal Bridge"
                }
            })

        # 3. NVIDIA (Nemotron/Llama)
        nvidia_key = os.getenv("NVIDIA_API_KEY", "")
        if nvidia_key and nvidia_key != "your_nvidia_api_key_here":
            self.providers.append({
                "name": "NVIDIA (Nemotron)",
                "key": nvidia_key,
                "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
                "model": "nvidia/llama-3.1-nemotron-70b-instruct",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {nvidia_key}"
                }
            })

        # 4. Gemini Direct (Free tier available)
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            self.providers.append({
                "name": "Gemini 2.0 Flash (Direct)",
                "key": gemini_key,
                "endpoint": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                "model": "gemini-2.0-flash",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {gemini_key}"
                }
            })
        elif openrouter_key:
            # Gemini via OpenRouter
            self.providers.append({
                "name": "Gemini 2.0 Flash",
                "key": openrouter_key,
                "endpoint": "https://openrouter.ai/api/v1/chat/completions",
                "model": "google/gemini-2.0-flash-exp",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openrouter_key}",
                    "HTTP-Referer": "https://sairolotech.com",
                    "X-Title": "Universal Bridge"
                }
            })

    def query(self, message: str, system_prompt: str = "") -> Dict[str, Any]:
        """Query AI with automatic fallback"""
        if not self.providers:
            return {"error": "No API keys configured! Set OPENROUTER_API_KEY, GROQ_API_KEY, or NVIDIA_API_KEY"}

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        errors = []

        for i, provider in enumerate(self.providers):
            try:
                payload = {
                    "model": provider["model"],
                    "messages": messages,
                    "temperature": 0.7
                }

                resp = requests.post(
                    provider["endpoint"],
                    headers=provider["headers"],
                    json=payload,
                    timeout=60
                )

                if resp.ok:
                    data = resp.json()
                    return {
                        "success": True,
                        "response": data["choices"][0]["message"]["content"],
                        "model": provider["model"],
                        "provider": provider["name"]
                    }
                else:
                    err = f"{provider['name']}: {resp.status_code}"
                    errors.append(err)

            except Exception as e:
                errors.append(f"{provider['name']}: {str(e)}")

        # All providers failed
        return {
            "error": f"All AI providers failed. Errors: {' | '.join(errors)}",
            "errors": errors
        }

    def chat(self, message: str) -> str:
        result = self.query(message)
        return result.get("response", result.get("error", "Unknown error"))

    def list_providers(self) -> list:
        """List all configured providers"""
        return [p["name"] for p in self.providers]

    @property
    def api_key(self) -> str:
        """For backward compatibility"""
        return self.providers[0]["key"] if self.providers else ""

# ============================================
# UNIVERSAL BRIDGE - Main Class
# ============================================
class UniversalBridge:
    """
    Universal Bridge - Connect any app to OpenClaw + Claude Opus

    Features:
    - Multiple connectors (Telegram, OpenClaw, API)
    - Claude Opus AI brain
    - Smart routing
    - Extensible architecture
    """

    def __init__(self):
        # AI Brain
        self.ai = AIBrain()

        # Connectors
        self.connectors: Dict[str, Connector] = {}
        self._register_default_connectors()

    def _register_default_connectors(self):
        """Register default connectors"""
        # Claude Opus AI (always available if key set)
        # OpenClaw
        self.connectors["openclaw"] = OpenClawConnector()

        # Telegram (check env OR OpenClaw config)
        if Config.TELEGRAM_BOT_TOKEN or get_openclaw_config():
            self.connectors["telegram"] = TelegramConnector()

        # WhatsApp (Ultramsg)
        if Config.ULTRAMSG_TOKEN:
            self.connectors["whatsapp"] = WhatsAppConnector()

        # Slack
        if Config.SLACK_BOT_TOKEN:
            self.connectors["slack"] = SlackConnector()

        # Discord
        if os.getenv("DISCORD_WEBHOOK_URL"):
            self.connectors["discord"] = DiscordConnector()

        # Webhook (generic)
        if os.getenv("BRIDGE_WEBHOOK_URL"):
            self.connectors["webhook"] = WebhookConnector()

        # API
        self.connectors["api"] = APConnector()

    def add_connector(self, name: str, connector: Connector):
        """Add custom connector"""
        self.connectors[name] = connector

    def status(self) -> Dict[str, Any]:
        """Get bridge status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "ai": {
                "connected": bool(self.ai.providers),
                "providers": self.ai.list_providers()
            },
            "connectors": {
                name: {"connected": conn.is_connected(), "name": conn.name}
                for name, conn in self.connectors.items()
            }
        }

    def send_to_all(self, message: str) -> Dict[str, Any]:
        """Send message to all connected apps"""
        results = {}
        for name, conn in self.connectors.items():
            if conn.is_connected():
                result = conn.send(message)
                results[name] = result
        return results

    def route(self, message: str, use_ai: bool = True) -> Dict[str, Any]:
        """
        Smart route message:
        1. Send to AI for response
        2. Route to connected apps based on content
        """
        results = {"timestamp": datetime.now().isoformat(), "input": message}

        # AI processing
        if use_ai and self.ai.api_key:
            ai_result = self.ai.query(message)
            results["ai"] = ai_result

            # Route to appropriate connectors
            if any(kw in message.lower() for kw in ["browser", "click", "type", "open", "automation"]):
                # Browser/app automation -> OpenClaw
                if "openclaw" in self.connectors:
                    oc_result = self.connectors["openclaw"].send(ai_result.get("response", "")[:1000])
                    results["openclaw"] = oc_result
                    results["routed_to"] = "Claude Opus + OpenClaw"
            else:
                # General query -> Telegram/other
                for name, conn in self.connectors.items():
                    if name != "openclaw" and conn.is_connected():
                        conn.send(ai_result.get("response", ""))
                results["routed_to"] = "Claude Opus"
        else:
            # No AI, just route to connectors
            results["routed_to"] = self.send_to_all(message)

        return results

    def cli(self):
        """Interactive CLI mode"""
        print("=" * 60)
        print("Universal OpenClaw Bridge")
        print("=" * 60)
        print(f"\nAI: {'Connected' if self.ai.api_key else 'NOT SET'}")
        print("\nConnectors:")
        for name, conn in self.connectors.items():
            status = "OK" if conn.is_connected() else "OFFLINE"
            print(f"  [{status}] {name}")
        print("\nCommands:")
        print("  /status     - Show status")
        print("  /send <app> <msg> - Send to specific app")
        print("  /broadcast <msg>  - Send to all apps")
        print("  /ai <prompt>     - Query AI")
        print("  /route <prompt>  - Smart route")
        print("  /telegram        - Setup Telegram chat ID")
        print("  /quit            - Exit")
        print("=" * 60)

        while True:
            try:
                cmd = input("\n> ").strip()
                if not cmd:
                    continue

                if cmd == "/quit":
                    break
                elif cmd == "/status":
                    print(json.dumps(self.status(), indent=2))
                elif cmd.startswith("/send "):
                    parts = cmd.split(" ", 2)
                    if len(parts) >= 3:
                        _, app, msg = parts
                        if app in self.connectors:
                            print(self.connectors[app].send(msg))
                        else:
                            print(f"Unknown app: {app}")
                elif cmd.startswith("/broadcast "):
                    msg = cmd[11:]
                    print(self.send_to_all(msg))
                elif cmd.startswith("/ai "):
                    prompt = cmd[4:]
                    print(self.ai.chat(prompt))
                elif cmd.startswith("/route "):
                    prompt = cmd[7:]
                    result = self.route(prompt)
                    print(f"Routed to: {result.get('routed_to')}")
                    if result.get("ai", {}).get("response"):
                        print(f"AI: {result['ai']['response'][:200]}...")
                elif cmd == "/telegram":
                    print("\nTelegram Setup:")
                    print("1. Open Telegram and message @sairolotech_ai_bot")
                    print("2. Type any message (e.g., 'hello')")
                    print("3. Press Enter here...")
                    input()
                    if "telegram" in self.connectors:
                        chat_id = self.connectors["telegram"].get_chat_id()
                        if chat_id:
                            print(f"[OK] Chat ID found: {chat_id}")
                            print(f"Set in openclaw_bridge.env: TELEGRAM_CHAT_ID={chat_id}")
                            self.connectors["telegram"].chat_id = chat_id
                        else:
                            print("[!] No messages found. Make sure you messaged the bot first.")
                    else:
                        print("[!] Telegram not configured")
                else:
                    # Default: smart route
                    result = self.route(cmd)
                    if result.get("ai", {}).get("response"):
                        print(result["ai"]["response"])
                    else:
                        print("No AI response. Check API key.")
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


# ============================================
# MAIN
# ============================================
def main():
    bridge = UniversalBridge()

    if len(sys.argv) > 1:
        # CLI mode
        if sys.argv[1] == "--cli":
            bridge.cli()
        elif sys.argv[1] == "--status":
            print(json.dumps(bridge.status(), indent=2))
        elif sys.argv[1] == "--test":
            # Test mode
            print("Testing Universal Bridge...\n")
            status = bridge.status()
            print(f"AI Connected: {status['ai']['connected']}")
            print(f"Providers: {', '.join(status['ai']['providers'])}")
            print("\nConnector Status:")
            for name, info in status["connectors"].items():
                print(f"  [{info['connected']}] {name}")

            if bridge.ai.providers:
                print("\n--- AI Test ---")
                result = bridge.ai.query("Say 'Hello from Universal Bridge!' in one line")
                if result.get("success"):
                    print(f"AI: {result['response']}")
                    print(f"Provider: {result.get('provider', 'N/A')}")
        else:
            # Direct query
            result = bridge.route(" ".join(sys.argv[1:]))
            if result.get("ai", {}).get("response"):
                print(result["ai"]["response"])
    else:
        # Auto mode
        bridge.cli()


if __name__ == "__main__":
    main()
