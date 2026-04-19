"""
Hermes Agent - Core Brain
Routes tasks to correct tools
"""

from dotenv import load_dotenv
load_dotenv()

import os
import json
from typing import Dict, Optional
from datetime import datetime

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.models.anthropic import Claude
from agno.models.groq import Groq

from shared.schemas.database import User, Memory, Task, get_session
from shared.utils.logging import log_action


class HermesCore:
    """
    Hermes - The AI Brain
    Role: Think, Remember, Route
    """

    def __init__(self):
        self.models = {
            "fast": "groq/llama-3.3-70b-versatile",
            "gemini": "google/gemini-2.5-flash",
            "deepseek": "deepseek/deepseek-chat-v3",
            "claude": "claude-opus-4-7",
        }

        self.tool_definitions = {
            "crm": {
                "description": "Lead management, customer data, business info",
                "endpoint": os.getenv("CRM_API_URL", "http://localhost:8510"),
                "actions": ["add_lead", "get_lead", "list_leads", "update_lead"]
            },
            "interpreter": {
                "description": "Run code, open apps, system commands",
                "endpoint": os.getenv("INTERPRETER_API_URL", "http://localhost:8507"),
                "actions": ["run_code", "open_app", "run_command"]
            },
            "n8n": {
                "description": "Workflows, automation, scheduled tasks",
                "endpoint": os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook"),
                "actions": ["trigger_workflow", "schedule_task"]
            },
            "hermes": {
                "description": "Memory, context, general AI",
                "actions": ["remember", "recall", "learn"]
            }
        }

    def create_agent(self, model: str = "gemini") -> Agent:
        """Create AI agent with specified model"""
        model_id = self.models.get(model, self.models["gemini"])

        if "groq" in model_id:
            return Agent(name="Hermes", model=Groq(id=model_id.split("/")[-1]))
        elif "claude" in model_id:
            return Agent(name="Hermes", model=Claude(id=model_id))
        else:
            return Agent(name="Hermes", model=OpenRouter(id=model_id))

    def route_intent(self, message: str) -> Dict:
        """
        Route user intent to correct tool
        Returns: {tool, action, params}
        """
        routing_prompt = f"""
You are a task router. Analyze this message and decide the best tool.

Available Tools:
- crm: Lead management, customer data, business info
- interpreter: Run code, open apps, system commands
- n8n: Workflows, automation, scheduled tasks
- hermes: Memory, context, general AI (default)

Message: {message}

Respond ONLY with JSON:
{{"tool": "tool_name", "action": "action_name", "params": {{"key": "value"}}}}
"""

        try:
            agent = self.create_agent("gemini")
            response = agent.run(routing_prompt)
            result = json.loads(response.content.strip())
            return result
        except:
            # Default to hermes for general chat
            return {"tool": "hermes", "action": "chat", "params": {}}

    def think(self, user_id: int, message: str, model: str = "gemini") -> str:
        """
        Main thinking function
        1. Get user context from memory
        2. Route to correct tool
        3. Execute and respond
        """
        session = get_session()

        # Get user
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, name=f"User_{user_id}")
            session.add(user)
            session.commit()

        # Get memory context
        memories = session.query(Memory).filter(Memory.user_id == user_id).all()
        context = "\n".join([f"{m.key}: {m.value}" for m in memories[-10:]])

        # Route intent
        route = self.route_intent(message)
        tool = route.get("tool", "hermes")

        # Log task
        task = Task(
            user_id=user_id,
            source="telegram",
            intent=message[:100],
            target_tool=tool,
            status="running"
        )
        session.add(task)
        session.commit()

        # Execute based on tool
        try:
            if tool == "hermes":
                response = self._hermes_think(message, context, model)
            elif tool == "crm":
                response = self._crm_action(message, route.get("action"))
            elif tool == "interpreter":
                response = self._interpreter_action(message)
            elif tool == "n8n":
                response = self._n8n_trigger(message)
            else:
                response = self._hermes_think(message, context, model)

            # Update task
            task.status = "completed"
            task.output_payload = response[:1000]
            session.commit()

            return response

        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)[:500]
            session.commit()
            return f"Error: {str(e)[:200]}"

    def _hermes_think(self, message: str, context: str, model: str) -> str:
        """Hermes thinks directly"""
        system_prompt = f"""You are Hermes, SAI Rolotech AI assistant.
You have persistent memory. Use it to provide personalized responses.

Known context:
{context}

Be helpful, concise, and remember previous conversations."""

        agent = self.create_agent(model)
        agent.system_prompt = system_prompt
        response = agent.run(message)
        return response.content

    def _crm_action(self, message: str, action: str) -> str:
        """Route to CRM service"""
        return f"📊 CRM Action: {action}\n\nUse CRM API at: {self.tool_definitions['crm']['endpoint']}"

    def _interpreter_action(self, message: str) -> str:
        """Route to Interpreter service"""
        return f"💻 Interpreter Action\n\nUse Interpreter API at: {self.tool_definitions['interpreter']['endpoint']}"

    def _n8n_trigger(self, message: str) -> str:
        """Trigger n8n workflow"""
        return f"🔄 n8n Workflow Trigger\n\nWebhook: {self.tool_definitions['n8n']['endpoint']}"

    def remember(self, user_id: int, key: str, value: str) -> str:
        """Store a memory"""
        session = get_session()
        memory = Memory(user_id=user_id, key=key, value=value)
        session.add(memory)
        session.commit()
        log_action(user_id, "memory_save", "hermes", f"{key}: {value[:50]}")
        return f"🧠 Remembered: {key}"

    def recall(self, user_id: int, key: str) -> Optional[str]:
        """Recall a memory"""
        session = get_session()
        memory = session.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.key == key
        ).first()
        return memory.value if memory else None

    def get_all_memories(self, user_id: int) -> list:
        """Get all user memories"""
        session = get_session()
        memories = session.query(Memory).filter(Memory.user_id == user_id).all()
        return [m.to_dict() for m in memories]


# Singleton instance
hermes = HermesCore()
