"""
SAI Rolotech AI Hub - Master Router
Hermes Brain with 5 Powers:
1. Intent Detection
2. Tool Selection
3. Model Selection
4. Policy Check
5. Response Generation
"""

from dotenv import load_dotenv
load_dotenv()

import os
import json
import re
from typing import Dict, Optional, Tuple
from datetime import datetime

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.models.anthropic import Claude
from agno.models.groq import Groq

from apps.interpreter_service.policies.policy_engine import policy
from shared.schemas.database import User, Memory, Task, Lead, get_session
from shared.utils.logging import log_action, log


class MasterRouter:
    """
    Hermes Master Router
    Controls all AI operations
    """

    def __init__(self):
        self.session = get_session()

        # Tool definitions
        self.tools = {
            "crm": {
                "keywords": ["lead", "client", "deal", "crm", "contact", "customer", "prospect", "enquiry"],
                "endpoint": os.getenv("CRM_API_URL", "http://localhost:8510"),
                "requires_approval": False
            },
            "interpreter": {
                "keywords": ["open", "run", "click", "app", "file", "chrome", "notepad", "code", "execute", "browse", "website", "launch"],
                "endpoint": os.getenv("INTERPRETER_API_URL", "http://localhost:8507"),
                "requires_approval": True,
                "risky_keywords": ["delete", "remove", "format", "install", "shutdown", "registry", "sudo"]
            },
            "n8n": {
                "keywords": ["daily", "schedule", "remind", "tomorrow", "every", "repeat", "automation", "workflow", "task", "reminder"],
                "endpoint": os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook"),
                "requires_approval": False
            },
            "hermes": {
                "keywords": [],
                "description": "Default - General chat"
            }
        }

        # Model selection rules
        self.model_rules = {
            "code": {
                "keywords": ["code", "python", "bug", "script", "function", "class", "debug", "programming"],
                "model": "deepseek",
                "reason": "Best for coding tasks"
            },
            "analysis": {
                "keywords": ["analysis", "report", "strategy", "business", "market", "research", "study"],
                "model": "claude",
                "reason": "Best for complex reasoning"
            },
            "fast": {
                "keywords": ["fast", "quick", "simple", "fastest", "urgent", "hurry"],
                "model": "groq",
                "reason": "Fastest response"
            },
            "heavy": {
                "keywords": ["complex", "detailed", "architecture", "design", "explain deeply"],
                "model": "claude",
                "reason": "Most capable"
            }
        }

        self.default_model = "gemini"

    def process(self, user_id: int, message: str) -> Dict:
        """
        Main processing pipeline
        Returns: {response, tool, model, action, status}
        """
        result = {
            "user_id": user_id,
            "message": message,
            "intent": None,
            "tool": None,
            "model": None,
            "action": None,
            "requires_approval": False,
            "response": None,
            "status": "success"
        }

        # 1. INTENT DETECTION
        intent = self.detect_intent(message)
        result["intent"] = intent["type"]
        result["tool"] = intent["tool"]
        result["action"] = intent["action"]

        # 2. POLICY CHECK
        if intent["tool"] == "interpreter":
            needs_approval = self.require_approval(message)
            result["requires_approval"] = needs_approval
            if needs_approval:
                result["response"] = f"⚠️ This action requires approval:\n{message}\n\nReply 'yes' to confirm."
                return result

        # 3. MODEL SELECTION
        model = self.select_model(message)
        result["model"] = model

        # 4. TOOL EXECUTION
        try:
            if intent["tool"] == "hermes":
                result["response"] = self._hermes_chat(user_id, message, model)
            elif intent["tool"] == "crm":
                result["response"] = self._crm_action(message)
            elif intent["tool"] == "interpreter":
                result["response"] = self._interpreter_action(message)
            elif intent["tool"] == "n8n":
                result["response"] = self._n8n_action(message)
            else:
                result["response"] = self._hermes_chat(user_id, message, model)

        except Exception as e:
            result["status"] = "error"
            result["response"] = f"Error: {str(e)[:200]}"
            log.error(f"Router error: {e}")

        # Log task
        self._log_task(user_id, message, result)

        return result

    def detect_intent(self, message: str) -> Dict:
        """1. Detect user intent"""
        msg_lower = message.lower()

        # Check each tool
        for tool_name, tool_info in self.tools.items():
            if tool_name == "hermes":
                continue
            for keyword in tool_info.get("keywords", []):
                if keyword in msg_lower:
                    return {
                        "type": keyword,
                        "tool": tool_name,
                        "action": self._extract_action(message, keyword)
                    }

        # Default to hermes
        return {
            "type": "chat",
            "tool": "hermes",
            "action": "respond"
        }

    def _extract_action(self, message: str, keyword: str) -> str:
        """Extract specific action from message"""
        # Lead actions
        if keyword in ["lead", "crm"]:
            if "add" in message.lower():
                return "create_lead"
            elif "list" in message.lower():
                return "list_leads"
            elif "update" in message.lower():
                return "update_lead"
            return "query"

        # Interpreter actions
        if keyword in ["open", "launch"]:
            return "open_app"
        elif keyword in ["run", "execute"]:
            return "run_command"
        elif keyword in ["click"]:
            return "desktop_action"

        # n8n actions
        if keyword in ["schedule", "remind", "task"]:
            return "schedule_task"
        elif keyword in ["daily", "every"]:
            return "recurring"

        return "execute"

    def require_approval(self, message: str) -> bool:
        """2. Check if action requires approval"""
        risky_words = ["delete", "remove", "format", "install", "shutdown", "registry", "sudo", "del /", "rm -rf"]
        return any(word in message.lower() for word in risky_words)

    def select_model(self, message: str) -> str:
        """3. Select best model for task"""
        msg_lower = message.lower()

        for rule_name, rule in self.model_rules.items():
            for keyword in rule["keywords"]:
                if keyword in msg_lower:
                    return rule["model"]

        return self.default_model

    def _create_agent(self, model_name: str) -> Agent:
        """Create AI agent with specified model"""
        models = {
            "gemini": "google/gemini-2.5-flash",
            "deepseek": "deepseek/deepseek-chat-v3",
            "groq": "llama-3.3-70b-versatile",
            "claude": "claude-sonnet-4-6"
        }

        model_id = models.get(model_name, models["gemini"])

        if model_name == "groq":
            return Agent(name="Hermes", model=Groq(id="llama-3.3-70b-versatile"))
        elif model_name == "claude":
            return Agent(name="Hermes", model=Claude(id=model_id))
        else:
            return Agent(name="Hermes", model=OpenRouter(id=model_id))

    def _hermes_chat(self, user_id: int, message: str, model: str) -> str:
        """Chat with Hermes AI"""
        # Get user context
        memories = self.session.query(Memory).filter(Memory.user_id == user_id).all()
        context = "\n".join([f"{m.key}: {m.value}" for m in memories[-5:]])

        system_prompt = f"""You are Hermes, SAI Rolotech AI assistant.
Memory context: {context or 'No previous context'}
Be helpful, concise, and remember user preferences."""

        agent = self._create_agent(model)
        response = agent.run(message)
        return response.content

    def _crm_action(self, message: str) -> str:
        """Execute CRM action"""
        msg_lower = message.lower()

        if "add" in msg_lower or "new lead" in msg_lower:
            # Parse lead info
            parts = message.split()
            name = "Unknown"
            mobile = None

            # Simple parsing
            for i, word in enumerate(parts):
                if word.isdigit() and len(word) >= 10:
                    mobile = word
                if word[0].isupper() and len(word) > 2:
                    name = word

            return f"📊 Creating lead:\nName: {name}\nMobile: {mobile or 'N/A'}\n\nUse CRM API to save."

        elif "list" in msg_lower:
            return "📋 Fetching leads...\n\nUse CRM API endpoint: /crm/leads"

        else:
            return "📊 CRM Action\n\nAvailable: /lead add, /lead list, /lead update"

    def _interpreter_action(self, message: str) -> str:
        """Execute interpreter action"""
        msg_lower = message.lower()

        # Check policy first
        is_safe, reason = policy.check_command(message)
        if not is_safe:
            return f"❌ Policy denied: {reason}"

        # Parse command
        if "chrome" in msg_lower or "browser" in msg_lower:
            return "🌐 Opening Chrome...\n\nCommand: start chrome"

        elif "notepad" in msg_lower:
            return "📝 Opening Notepad...\n\nCommand: start notepad"

        elif "code" in msg_lower or "vscode" in msg_lower:
            return "💻 Opening VS Code...\n\nCommand: code"

        else:
            return f"💻 Executing:\n{message}\n\nUse Interpreter API: POST /run"

    def _n8n_action(self, message: str) -> str:
        """Trigger n8n workflow"""
        msg_lower = message.lower()

        if "daily" in msg_lower or "report" in msg_lower:
            return "📊 Setting up daily report...\n\nWebhook: POST /webhook/daily-report"

        elif "remind" in msg_lower or "schedule" in msg_lower:
            return "⏰ Scheduling reminder...\n\nWebhook: POST /webhook/reminder"

        elif "task" in msg_lower:
            return "📋 Creating scheduled task...\n\nWebhook: POST /webhook/task"

        else:
            return "🔄 Triggering automation...\n\nWebhook: POST /webhook/generic"

    def _log_task(self, user_id: int, message: str, result: Dict):
        """Log task to database"""
        try:
            task = Task(
                user_id=user_id,
                source="telegram",
                intent=message[:100],
                target_tool=result["tool"],
                status="completed" if result["status"] == "success" else "failed",
                output_payload=result.get("response", "")[:500]
            )
            self.session.add(task)
            self.session.commit()
        except Exception as e:
            log.error(f"Task logging failed: {e}")


# Singleton
master_router = MasterRouter()
