#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Bridge
Connect Claude Opus to OpenClaw Gateway + Telegram

CONFIG: openclaw-bridge/openclaw.env
DO NOT MIX WITH cloud-ai/cloud.env
"""

import os
import sys
import json
import requests
from typing import Optional, Dict, Any

# Load OpenClaw config ONLY
try:
    from dotenv import load_dotenv
    load_dotenv("openclaw-bridge/openclaw.env")
except ImportError:
    pass

# ============================================
# CONFIG - OpenClaw Only
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

class OpenClawConfig:
    OPENCLAW_URL = os.getenv("OPENCLAW_URL", "http://localhost:18789")
    OPENCLAW_TOKEN = os.getenv("OPENCLAW_TOKEN", "")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "") or get_openclaw_config()
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

    # MODEL PRIORITY:
    # - LIGHT tasks (small): Gemini 2.0 Flash (FREE)
    # - HEAVY tasks: Opus 4.7 (Personal API key - Antigravity)
    LIGHT_MODEL = "google/gemini-2.0-flash-exp"  # Free - chhote kaam
    HEAVY_MODEL = "anthropic/opus-4.7"  # Personal key - bade kaam
    DEFAULT_MODEL = LIGHT_MODEL  # Default: Flash 2.0
    TIMEOUT = 60

# ============================================
# CONNECTORS - OpenClaw Only
# ============================================
class OpenClawConnector:
    """Connect via OpenClaw gateway"""
    name = "openclaw"

    def __init__(self):
        self.url = OpenClawConfig.OPENCLAW_URL
        self.token = OpenClawConfig.OPENCLAW_TOKEN

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

class TelegramConnector:
    """Telegram via OpenClaw bot"""
    name = "telegram"

    def __init__(self):
        self.bot_token = OpenClawConfig.TELEGRAM_BOT_TOKEN or get_openclaw_config()
        self.chat_id = OpenClawConfig.TELEGRAM_CHAT_ID
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
            return {"error": "TELEGRAM_CHAT_ID not set"}

        try:
            resp = requests.post(
                f"{self.base_url}/sendMessage",
                json={"chat_id": int(target_chat), "text": message},
                timeout=30
            )
            if resp.ok:
                return {"success": True}
            return {"error": f"Telegram error: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

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

# ============================================
# AI BRAIN - Smart Cascade System
# 1. Gemini 2.0 Flash (FREE) - Light tasks
# 2. Groq Llama 3.3 (FREE) - Medium tasks (auto when Flash limit ends)
# 3. Opus 4.7 (PAID) - Heavy tasks only
# ============================================
class AIBrain:
    """Smart AI cascade: Flash → Groq → Opus (heaviest)"""

    def __init__(self):
        self.providers = {
            "gemini": {
                "key": os.getenv("GEMINI_API_KEY", ""),
                "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent",
                "model": "gemini-2.0-flash-exp",
                "free": True,
                "priority": 1
            },
            "groq": {
                "key": os.getenv("GROQ_API_KEY", ""),
                "endpoint": "https://api.groq.com/openai/v1/chat/completions",
                "model": "llama-3.3-70b-versatile",
                "free": True,
                "priority": 2
            },
            "opus": {
                "key": os.getenv("OPENROUTER_API_KEY", ""),
                "endpoint": "https://openrouter.ai/api/v1/chat/completions",
                "model": "anthropic/claude-opus-4.7",
                "free": False,
                "priority": 3
            }
        }

    def query(self, message: str, system_prompt: str = "", task: str = "light") -> Dict[str, Any]:
        """
        Smart cascade based on task type:
        - light: Gemini → Groq → Opus
        - medium: Groq → Gemini → Opus
        - heavy: Opus → Groq → Gemini
        """
        if task == "heavy":
            priority_order = ["opus", "groq", "gemini"]
        elif task == "medium":
            priority_order = ["groq", "gemini", "opus"]
        else:
            priority_order = ["gemini", "groq", "opus"]

        errors = []
        for name in priority_order:
            cfg = self.providers[name]
            if not cfg["key"]:
                continue

            try:
                headers = {"Content-Type": "application/json"}
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": message})

                if name == "gemini":
                    payload = {
                        "contents": [{"parts": [{"text": m["content"]} for m in messages]}],
                        "generationConfig": {"temperature": 0.7}
                    }
                    resp = requests.post(f"{cfg['endpoint']}?key={cfg['key']}", headers=headers, json=payload, timeout=60)
                else:
                    headers["Authorization"] = f"Bearer {cfg['key']}"
                    if name == "opus":
                        headers["HTTP-Referer"] = "https://sairolotech.com"
                        headers["X-Title"] = "OpenClaw Bridge"
                    payload = {"model": cfg["model"], "messages": messages, "temperature": 0.7}
                    resp = requests.post(cfg["endpoint"], headers=headers, json=payload, timeout=60)

                if resp.ok:
                    data = resp.json()
                    if name == "gemini":
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        text = data["choices"][0]["message"]["content"]
                    return {"success": True, "response": text, "model": cfg["model"], "provider": name}
                else:
                    # Auto-fallback on quota/limit
                    if resp.status_code == 429 or "quota" in resp.text.lower():
                        errors.append(f"{name}: QUOTA - trying next")
                        continue
                    errors.append(f"{name}: {resp.status_code}")
            except Exception as e:
                errors.append(f"{name}: {str(e)[:50]}")

        return {"error": f"All failed: {'; '.join(errors)}"}

    def chat(self, message: str, task: str = "light") -> str:
        """Chat with smart cascade - default light tasks use Gemini Flash"""
        result = self.query(message, task=task)
        if result.get("success"):
            provider = result.get('provider', 'AI')
            emoji = {"gemini": "⚡", "groq": "🚀", "opus": "🧠"}.get(provider, "")
            return f"{emoji}[{provider.upper()}] {result.get('response', '')}"
        return f"[ERROR] {result.get('error', 'Unknown')}"

    def available_providers(self) -> list:
        """List configured providers"""
        return [name for name, cfg in self.providers.items() if cfg["key"]]

class MemoryManager:
    """Manage OpenClaw vector memory"""

    def __init__(self):
        self.memory_db = os.path.expanduser("~/.openclaw/memory/main.sqlite")

    def status(self) -> dict:
        """Check memory system status"""
        if not os.path.exists(self.memory_db):
            return {"status": "locked", "reason": "Memory DB not found"}

        try:
            import sqlite3
            conn = sqlite3.connect(self.memory_db)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM chunks")
            chunks = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM files")
            files = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM embedding_cache")
            embeddings = cursor.fetchone()[0]

            conn.close()

            return {
                "status": "unlocked" if chunks > 0 else "empty",
                "database": self.memory_db,
                "records": {
                    "chunks": chunks,
                    "files": files,
                    "embeddings": embeddings
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def unlock(self) -> dict:
        """Unlock/activate vector memory"""
        if not os.path.exists(self.memory_db):
            return {"error": "Memory database not found at ~/.openclaw/memory/main.sqlite"}

        try:
            import sqlite3
            conn = sqlite3.connect(self.memory_db)
            cursor = conn.cursor()

            # Enable write mode and create initial schema if empty
            cursor.execute("SELECT COUNT(*) FROM chunks")
            chunks = cursor.fetchone()[0]

            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cursor.fetchall()]

            conn.close()

            return {
                "success": True,
                "message": "Vector memory unlocked",
                "tables": tables,
                "chunks_loaded": chunks,
                "memory_path": self.memory_db
            }
        except Exception as e:
            return {"error": f"Failed to unlock memory: {str(e)}"}

    def add_memory(self, text: str, source: str = "manual") -> dict:
        """Add a memory entry"""
        if not os.path.exists(self.memory_db):
            return {"error": "Memory DB not found"}

        try:
            import sqlite3
            import hashlib
            import time

            conn = sqlite3.connect(self.memory_db)
            cursor = conn.cursor()

            # Generate hash and timestamp
            hash_val = hashlib.sha256(text.encode()).hexdigest()
            timestamp = int(time.time() * 1000)

            # Insert chunk (embedding will be generated on query)
            cursor.execute("""
                INSERT INTO chunks (id, path, source, start_line, end_line, hash, model, text, embedding, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (hash_val, f"memory://{source}", source, 1, 1, hash_val, "manual", text, "", timestamp))

            conn.commit()
            conn.close()

            return {"success": True, "id": hash_val}
        except Exception as e:
            return {"error": str(e)}

    def search(self, query: str) -> dict:
        """Search memories"""
        if not os.path.exists(self.memory_db):
            return {"error": "Memory DB not found"}

        try:
            import sqlite3
            conn = sqlite3.connect(self.memory_db)
            cursor = conn.cursor()

            # Simple search by text
            cursor.execute("""
                SELECT id, text, source, updated_at
                FROM chunks
                WHERE text LIKE ?
                LIMIT 10
            """, (f"%{query}%",))

            results = cursor.fetchall()
            conn.close()

            return {
                "success": True,
                "results": [{"id": r[0], "text": r[1], "source": r[2], "updated_at": r[3]} for r in results]
            }
        except Exception as e:
            return {"error": str(e)}


# ============================================
# OPENCLAW BRIDGE
# ============================================
class OpenClawBridge:
    """OpenClaw-only Bridge"""

    def __init__(self):
        self.ai = AIBrain()
        self.memory = MemoryManager()
        self.connectors = {}
        self._register_connectors()

    def _register_connectors(self):
        self.connectors["openclaw"] = OpenClawConnector()
        if OpenClawConfig.TELEGRAM_BOT_TOKEN or get_openclaw_config():
            self.connectors["telegram"] = TelegramConnector()

    def status(self) -> Dict[str, Any]:
        providers = self.ai.available_providers()
        return {
            "system": "OpenClaw Bridge",
            "config": "openclaw-bridge/openclaw.env",
            "ai": {"connected": len(providers) > 0, "providers": providers},
            "memory": self.memory.status(),
            "connectors": {name: conn.is_connected() for name, conn in self.connectors.items()}
        }

    def cli(self):
        print("=" * 60)
        print("OpenClaw Bridge - Smart AI Cascade")
        print("=" * 60)
        print("Config: openclaw-bridge/openclaw.env")
        print("\nAI Cascade:")
        print("  ⚡ Gemini 2.0 Flash (FREE)  - Light tasks (default)")
        print("  🚀 Groq Llama 3.3 (FREE)   - Medium tasks")
        print("  🧠 Opus 4.7 (PAID)         - Heavy/Complex tasks")
        print("\nCommands:")
        print("  /ai <msg>          - Chat (light - Gemini Flash)")
        print("  /ai heavy <msg>    - Chat (heavy - Opus 4.7)")
        print("  /ai medium <msg>   - Chat (medium - Groq)")
        print("  /memory status     - Check vector memory")
        print("  /memory unlock     - Unlock vector memory")
        print("  /memory add <txt>  - Add memory entry")
        print("  /memory search <q> - Search memories")
        print("  /status            - Full system status")
        print("  /quit              - Exit")
        print("=" * 60)

        while True:
            try:
                cmd = input("\n> ").strip()
                if cmd == "/quit":
                    break
                elif cmd == "/status":
                    print(json.dumps(self.status(), indent=2))
                elif cmd.startswith("/memory"):
                    self._handle_memory_cmd(cmd[8:])
                elif cmd.startswith("/ai "):
                    msg = cmd[4:]
                    task = "light"
                    if msg.startswith("heavy "):
                        task = "heavy"
                        msg = msg[6:]
                    elif msg.startswith("medium "):
                        task = "medium"
                        msg = msg[7:]
                    print(self.ai.chat(msg, task=task))
                elif cmd == "/telegram":
                    print("\n1. Message @sairolotech_ai_bot on Telegram")
                    print("2. Press Enter here...")
                    input()
                    if "telegram" in self.connectors:
                        chat_id = self.connectors["telegram"].get_chat_id()
                        if chat_id:
                            print(f"[OK] Chat ID: {chat_id}")
                            self.connectors["telegram"].chat_id = chat_id
                        else:
                            print("[!] No messages found")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

    def _handle_memory_cmd(self, args: str):
        """Handle memory commands"""
        parts = args.strip().split(None, 1)
        action = parts[0] if parts else ""

        if action == "status":
            print(json.dumps(self.memory.status(), indent=2))
        elif action == "unlock":
            result = self.memory.unlock()
            print(json.dumps(result, indent=2))
        elif action == "add" and len(parts) > 1:
            result = self.memory.add_memory(parts[1])
            print(json.dumps(result, indent=2))
        elif action == "search" and len(parts) > 1:
            result = self.memory.search(parts[1])
            print(json.dumps(result, indent=2))
        else:
            print("Memory commands: status, unlock, add <text>, search <query>")

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    bridge = OpenClawBridge()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            print("OpenClaw Bridge Test")
            print(json.dumps(bridge.status(), indent=2))
            result = bridge.ai.query("Say 'OpenClaw Bridge OK!' in one line")
            print(f"AI: {result.get('response', result.get('error'))}")
        elif sys.argv[1] == "--cli":
            bridge.cli()
        else:
            print(bridge.ai.chat(" ".join(sys.argv[1:])))
    else:
        bridge.cli()
