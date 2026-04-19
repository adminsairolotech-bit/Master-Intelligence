#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram AI Bridge
Automate Instagram with Claude AI

CONFIG: instagram-ai/instagram.env
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv("instagram-ai/instagram.env")
except ImportError:
    pass

try:
    from instagrapi import Client
    from instagrapi.types import Media, Story, UserShort
    INSTAGRAPI_AVAILABLE = True
except ImportError:
    INSTAGRAPI_AVAILABLE = False

# ============================================
# CONFIG
# ============================================
class InstagramConfig:
    USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
    PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
    SESSION_FILE = os.getenv("INSTAGRAM_SESSION_FILE", "instagram-ai/session.json")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENCLAW_URL = os.getenv("OPENCLAW_URL", "http://localhost:18789")

# ============================================
# AI CONTENT GENERATOR
# ============================================
class ContentAI:
    """Generate Instagram content using Gemini"""

    def __init__(self):
        self.api_key = InstagramConfig.GEMINI_API_KEY

    def generate_caption(self, topic: str, style: str = "engaging") -> str:
        """Generate Instagram caption"""
        if not self.api_key:
            return f"Check out {topic}! #trending"

        prompt = f"""Create an engaging Instagram caption for: {topic}
Style: {style}
Include relevant hashtags (max 10)
Keep it under 2200 characters
Make it catchy and engaging"""

        try:
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": "gemini-2.0-flash",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500
                },
                timeout=30
            )
            if response.ok:
                return response.json()["choices"][0]["message"]["content"]
        except:
            pass
        return f"Amazing {topic}! Check out our profile. #instagram #viral"

    def generate_story_text(self, message: str) -> str:
        """Generate story text"""
        if not self.api_key:
            return message
        return message[:100] + "..."

# ============================================
# INSTAGRAM CLIENT
# ============================================
class InstagramBridge:
    """Instagram automation bridge"""

    def __init__(self):
        self.config = InstagramConfig()
        self.client = None
        self.ai = ContentAI()
        self._logged_in = False

        if INSTAGRAPI_AVAILABLE:
            self._init_client()

    def _init_client(self):
        """Initialize Instagram client"""
        self.client = Client()

        # Try to load session
        if os.path.exists(self.config.SESSION_FILE):
            try:
                session = json.load(open(self.config.SESSION_FILE))
                self.client.set_settings(session)
                self._logged_in = True
                return
            except:
                pass

        # Login with credentials
        if self.config.USERNAME and self.config.PASSWORD:
            try:
                session = self.client.login(self.config.USERNAME, self.config.PASSWORD)
                json.dump(self.client.get_settings(), open(self.config.SESSION_FILE, "w"))
                self._logged_in = True
            except Exception as e:
                print(f"[!] Login failed: {e}")

    def is_logged_in(self) -> bool:
        return self._logged_in

    # === POSTS ===
    def upload_photo(self, photo_path: str, caption: str = "") -> Dict[str, Any]:
        """Upload photo to Instagram"""
        if not self._logged_in:
            return {"error": "Not logged in"}

        try:
            media = self.client.photo_upload(photo_path, caption)
            return {"success": True, "media_id": media.id}
        except Exception as e:
            return {"error": str(e)}

    def upload_story(self, photo_path: str, caption: str = "") -> Dict[str, Any]:
        """Upload story"""
        if not self._logged_in:
            return {"error": "Not logged in"}

        try:
            media = self.client.photo_upload_to_story(photo_path, caption)
            return {"success": True, "media_id": media.id}
        except Exception as e:
            return {"error": str(e)}

    # === CONTENT ===
    def auto_post(self, photo_path: str, topic: str, style: str = "engaging") -> Dict[str, Any]:
        """Auto-generate caption and post"""
        caption = self.ai.generate_caption(topic, style)
        return self.upload_photo(photo_path, caption)

    # === ACCOUNT INFO ===
    def get_profile(self) -> Dict[str, Any]:
        """Get account info"""
        if not self._logged_in:
            return {"error": "Not logged in"}

        try:
            user = self.client.user_info_by_username(self.config.USERNAME)
            return {
                "username": user.username,
                "followers": user.follower_count,
                "following": user.following_count,
                "posts": user.media_count,
                "bio": user.biography
            }
        except Exception as e:
            return {"error": str(e)}

    def get_followers(self, amount: int = 20) -> list:
        """Get followers"""
        if not self._logged_in:
            return []

        try:
            user_id = self.client.user_id_from_username(self.config.USERNAME)
            followers = self.client.user_followers(user_id, amount)
            return [{"pk": f.pk, "username": f.username} for f in followers.values()]
        except:
            return []

    def get_feed(self, amount: int = 10) -> list:
        """Get feed"""
        if not self._logged_in:
            return []

        try:
            posts = self.client.with_ctx(self.client.user_feed)(self.client.user_id_from_username(self.config.USERNAME))
            return [{"id": p.id, "likes": p.like_count, "comments": p.comment_count} for p in posts[:amount]]
        except:
            return []

    # === INTERACTIONS ===
    def like_post(self, media_id: str) -> Dict[str, Any]:
        """Like a post"""
        if not self._logged_in:
            return {"error": "Not logged in"}

        try:
            self.client.media_like(media_id)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    def follow_user(self, username: str) -> Dict[str, Any]:
        """Follow a user"""
        if not self._logged_in:
            return {"error": "Not logged in"}

        try:
            user_id = self.client.user_id_from_username(username)
            self.client.user_follow(user_id)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    def send_dm(self, username: str, message: str) -> Dict[str, Any]:
        """Send DM"""
        if not self._logged_in:
            return {"error": "Not logged in"}

        try:
            user_id = self.client.user_id_from_username(username)
            self.client.direct_send(message, [user_id])
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    # === AI CONTENT ===
    def generate_and_post(self, topic: str, photo_path: str, style: str = "engaging") -> Dict[str, Any]:
        """AI generates caption and posts to Instagram"""
        caption = self.ai.generate_caption(topic, style)
        return self.upload_photo(photo_path, caption)

    # === STATUS ===
    def status(self) -> Dict[str, Any]:
        return {
            "system": "Instagram AI Bridge",
            "config": "instagram-ai/instagram.env",
            "logged_in": self._logged_in,
            "instagrapi": INSTAGRAPI_AVAILABLE,
            "ai": bool(self.config.GEMINI_API_KEY)
        }

# ============================================
# CLI
# ============================================
def cli():
    bridge = InstagramBridge()

    print("=" * 50)
    print("Instagram AI Bridge")
    print("=" * 50)
    print(f"Logged In: {'Yes' if bridge.is_logged_in() else 'No'}")
    print(f"AI Caption: {'Yes' if bridge.ai.api_key else 'No'}")
    print()
    print("Commands:")
    print("  /status    - Show status")
    print("  /profile   - Get profile info")
    print("  /followers - Get followers")
    print("  /upload <path> <caption> - Upload photo")
    print("  /ai-post <path> <topic> - AI generate & post")
    print("  /quit      - Exit")
    print("=" * 50)

    while True:
        try:
            cmd = input("\n> ").strip()
            if cmd == "/quit":
                break
            elif cmd == "/status":
                print(json.dumps(bridge.status(), indent=2))
            elif cmd == "/profile":
                print(json.dumps(bridge.get_profile(), indent=2))
            elif cmd == "/followers":
                print(bridge.get_followers())
            elif cmd.startswith("/upload "):
                parts = cmd.split(" ", 2)
                if len(parts) >= 3:
                    print(bridge.upload_photo(parts[1], parts[2]))
                else:
                    print("Usage: /upload <path> <caption>")
            elif cmd.startswith("/ai-post "):
                parts = cmd.split(" ", 2)
                if len(parts) >= 3:
                    print(bridge.auto_post(parts[1], parts[2]))
                else:
                    print("Usage: /ai-post <path> <topic>")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    bridge = InstagramBridge()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            print("Instagram AI Bridge Test")
            print(json.dumps(bridge.status(), indent=2))
        elif sys.argv[1] == "--cli":
            cli()
        elif sys.argv[1] == "--profile":
            print(json.dumps(bridge.get_profile(), indent=2))
    else:
        cli()
