"""
SAI Rolotech - Hermes-Style Persistent Agent
Memory + Self-Improving + Long-Running
Built with LangGraph + LangChain
"""

from dotenv import load_dotenv
load_dotenv()

import json
import os
from datetime import datetime
from typing import Optional

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# ==================== MEMORY STORE ====================

class PersistentMemory:
    """Hermes-style persistent memory"""

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.memory_file = f"memory_{user_id}.json"
        self.conversation_history = ChatMessageHistory()
        self.facts = self._load_facts()
        self.preferences = self._load_preferences()

    def _load_facts(self) -> dict:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                return {"learned": [], "facts": {}}
        return {"learned": [], "facts": {}}

    def _save_facts(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.facts, f, indent=2)

    def _load_preferences(self) -> dict:
        pref_file = f"prefs_{self.user_id}.json"
        if os.path.exists(pref_file):
            try:
                with open(pref_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def remember(self, key: str, value: str):
        """Store a fact"""
        self.facts["facts"][key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        self._save_facts()

    def recall(self, key: str) -> Optional[str]:
        """Recall a fact"""
        return self.facts["facts"].get(key, {}).get("value")

    def learn(self, text: str):
        """Learn from conversation"""
        self.facts["learned"].append({
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.facts["learned"]) > 100:
            self.facts["learned"] = self.facts["learned"][-100:]
        self._save_facts()

    def get_context(self) -> str:
        """Get all memory context"""
        context = "\n--- KNOWN FACTS ---\n"
        for key, val in self.facts["facts"].items():
            context += f"{key}: {val['value']}\n"
        if self.facts["learned"]:
            context += "\n--- RECENT LEARNINGS ---\n"
            for item in self.facts["learned"][-5:]:
                context += f"- {item['text']}\n"
        return context

    def add_message(self, role: str, content: str):
        """Add to conversation history"""
        if role == "human":
            self.conversation_history.add_user_message(content)
        else:
            self.conversation_history.add_ai_message(content)

    def get_history(self, limit: int = 10):
        """Get recent conversation"""
        return self.conversation_history.messages[-limit:]


# ==================== HERMES AGENT ====================

class HermesAgent:
    """
    Hermes-style agent:
    - Persistent memory
    - Self-improving (learns from conversations)
    - Context-aware
    - Multi-model support
    """

    def __init__(self, name: str = "Hermes", user_id: str = "default"):
        self.name = name
        self.user_id = user_id
        self.memory = PersistentMemory(user_id)

        # Model selection
        self.models = {
            "fast": "groq/llama-3.3-70b-versatile",
            "smart": "deepseek/deepseek-chat-v3",
            "heavy": "claude-3-5-sonnet-20241022",
            "gemini": "google/gemini-2.5-flash",
        }
        self.current_model = "gemini"

        # Memory tool
        self.tools = [
            Tool(
                name="remember",
                func=lambda key, value: self.memory.remember(key, value) or "Saved!",
                description="Remember something. Usage: remember(key, value)"
            ),
            Tool(
                name="recall",
                func=lambda key: self.memory.recall(key) or "Not found",
                description="Recall a fact. Usage: recall(key)"
            ),
            Tool(
                name="get_context",
                func=lambda x: self.memory.get_context(),
                description="Get all remembered facts and learnings"
            ),
            Tool(
                name="learn",
                func=lambda x: self.memory.learn(x) or "Learned!",
                description="Learn from text. Usage: learn(text)"
            ),
        ]

    def think(self, prompt: str, model: str = None) -> str:
        """Think with memory context"""
        context = self.memory.get_context()

        full_prompt = f"""
{context}

--- USER REQUEST ---
{prompt}

Remember to use the remember/recall/learn tools to store important information.
"""

        # Use OpenRouter compatible model
        try:
            from agno.agent import Agent
            from agno.models.anthropic import Claude

            agent_model = model or self.current_model

            if agent_model == "heavy":
                llm = Claude(id="claude-sonnet-4-6")
            else:
                # Use Gemini via OpenRouter
                from agno.models.openrouter import OpenRouter
                llm = OpenRouter(id="google/gemini-2.5-flash")

            agent = Agent(
                model=llm,
                tools=self.tools,
                system_prompt=f"""You are {self.name}, a helpful AI assistant with persistent memory.
You have access to memory tools: remember, recall, get_context, learn
Always remember important user preferences and facts."""
            )

            response = agent.run(full_prompt)
            return response.content

        except Exception as e:
            return f"Error: {str(e)[:200]}"

    def chat(self, message: str, model: str = None) -> str:
        """Main chat method"""
        self.memory.add_message("human", message)

        response = self.think(message, model)

        self.memory.add_message("assistant", response)
        return response

    def set_preference(self, key: str, value: str):
        """Set user preference"""
        self.memory.facts["preferences"] = self.memory.facts.get("preferences", {})
        self.memory.facts["preferences"][key] = value
        self.memory._save_facts()

    def get_preference(self, key: str) -> Optional[str]:
        """Get user preference"""
        return self.memory.facts.get("preferences", {}).get(key)


# ==================== QUICK START ====================

if __name__ == "__main__":
    # Create Hermes agent
    hermes = HermesAgent(name="Hermes", user_id="sai")

    print("=" * 60)
    print("🤖 HERMES AGENT - PERSISTENT MEMORY AI")
    print("=" * 60)
    print("Features:")
    print("  • Persistent memory across sessions")
    print("  • Learns from conversations")
    print("  • Remembers your preferences")
    print("  • Multiple AI models")
    print("=" * 60)
    print("\nUSAGE:")
    print("  from hermes_agent import HermesAgent")
    print("  hermes = HermesAgent()")
    print("  hermes.chat('My name is Sai')")
    print("  hermes.chat('What is my name?')  # Remembers!")
    print("=" * 60)
