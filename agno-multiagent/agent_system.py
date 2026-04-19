"""
SAI Rolotech - Multi-Agent AI System
Best FREE + Claude 4.7 Opus for Heavy Tasks
"""

from dotenv import load_dotenv
load_dotenv()

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.models.groq import Groq
from agno.models.anthropic import Claude

# ==================== FALLBACK CHAIN ====================

class SmartAgent:
    """Agent with automatic fallback"""

    def __init__(self, name, models, description):
        self.name = name
        self.models = models  # List of (model_id, provider) tuples
        self.description = description
        self.current_model = None

    def _create_agent(self, model_id, provider="openrouter"):
        if provider == "groq":
            return Agent(name=self.name, model=Groq(id=model_id), description=self.description)
        elif provider == "claude":
            return Agent(name=self.name, model=Claude(id=model_id), description=self.description)
        return Agent(name=self.name, model=OpenRouter(id=model_id), description=self.description)

    def ask(self, prompt):
        errors = []
        for model_id, provider in self.models:
            try:
                agent = self._create_agent(model_id, provider)
                print(f"📡 Trying: {model_id}...")
                response = agent.run(prompt)
                self.current_model = model_id
                return response.content
            except Exception as e:
                error_msg = str(e)[:80]
                errors.append(f"{model_id}: {error_msg}")
                print(f"⚠️ {model_id} failed: {error_msg}")
                continue
        return f"❌ All models failed:\n" + "\n".join(errors)

    def print_response(self, prompt):
        print(f"\n🤖 {self.name}")
        print("=" * 50)
        response = self.ask(prompt)
        print(response)
        print(f"\n✅ Used: {self.current_model}")
        return response


# ==================== SMART AGENTS ====================

# 1. FASTEST - Groq first
fast_agent = SmartAgent(
    name="FASTEST",
    description="Speed priority",
    models=[
        ("llama-3.3-70b-versatile", "groq"),
        ("google/gemini-2.5-flash", "openrouter"),
    ]
)

# 2. GEMINI - Google's free model
gemini_agent = SmartAgent(
    name="GEMINI",
    description="Google's Gemini 2.5 Flash",
    models=[
        ("google/gemini-2.5-flash", "openrouter"),
        ("google/gemini-2.0-flash-exp", "openrouter"),
    ]
)

# 3. DEEPSEEK - Best reasoning (FREE)
deepseek_agent = SmartAgent(
    name="DEEPSEEK",
    description="Best reasoning - FREE",
    models=[
        ("deepseek/deepseek-chat-v3", "openrouter"),
        ("deepseek/deepseek-coder-v2", "openrouter"),
    ]
)

# 4. HEAVY - Claude 4.7 Opus for complex tasks
heavy_agent = SmartAgent(
    name="HEAVY (Claude Opus)",
    description="Anthropic Claude 4.7 Opus - Most capable",
    models=[
        ("claude-opus-4-7", "claude"),      # Claude 4.7 Opus - BEST
        ("claude-sonnet-4-6", "claude"),     # Fallback to Sonnet
        ("deepseek/deepseek-chat-v3", "openrouter"),  # Final fallback
    ]
)

# 5. BALANCED - Mix
balanced_agent = SmartAgent(
    name="BALANCED",
    description="Mix of all",
    models=[
        ("google/gemini-2.5-flash", "openrouter"),
        ("deepseek/deepseek-chat-v3", "openrouter"),
        ("llama-3.3-70b-versatile", "groq"),
        ("claude-opus-4-7", "claude"),
    ]
)


if __name__ == "__main__":
    print("=" * 60)
    print("SAI ROLOTECH AI - CLAUDE 4.7 OPUS + FREE MODELS")
    print("=" * 60)
    print("5 SMART AGENTS:")
    print("  1. FASTEST     - Groq Llama (FAST)")
    print("  2. GEMINI      - Gemini 2.5 Flash (FREE)")
    print("  3. DEEPSEEK    - DeepSeek V3 (FREE)")
    print("  4. HEAVY       - Claude 4.7 Opus (BEST)")
    print("  5. BALANCED    - Mix of all")
    print("=" * 60)
    print("\nUSAGE:")
    print("  from agent_system import heavy_agent, deepseek_agent")
    print("  heavy_agent.print_response('Complex coding task')")
    print("=" * 60)
