"""
PRO Version Engine
=================
Combines Memory + AI Agents into a unified system
The brain of the PRO version
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Import our modules
from .memory import MemoryStore, memory_store, save_memory, get_context
from .agents import (
    AIAgentOrchestrator,
    orchestrator,
    run_all_agents,
    planner_ai,
    technical_ai,
    business_ai,
    automation_ai,
    risk_ai
)

@dataclass
class CommandResult:
    """Result of a command execution"""
    command: str
    final_response: str
    agents_used: List[str]
    context_used: bool
    automation_triggered: bool
    execution_time_ms: int
    success: bool
    error: Optional[str] = None

class ProEngine:
    """
    PRO ENGINE - The Brain
    ======================

    Combines:
    1. Memory System - Stores context and history
    2. AI Agents - 5 specialized agents
    3. Automation - n8n trigger system
    4. Execution - Command parsing and routing
    """

    def __init__(self, user_id: int = 1):
        self.user_id = user_id
        self.memory = memory_store
        self.orchestrator = AIAgentOrchestrator()

        # Command patterns
        self.patterns = {
            "plan": r"(?:plan|schedule|breakdown|step|how to|steps?)",
            "build": r"(?:build|create|make|develop|design|code)",
            "analyze": r"(?:analyze|analysis|market|business|strategy)",
            "automate": r"(?:automate|automation|workflow|n8n|zapier|trigger)",
            "risk": r"(?:risk|danger|problem|issue|concern|threat)",
            "learn": r"(?:learn|teach|explain|what is|how does)",
            "roll_forming": r"(?:roll forming|c-channel|z-purlin|machine|profile)",
            "cad": r"(?:cad|autocad|drawing|design|dxf|2d|3d)",
            "crm": r"(?:crm|lead|customer|contact|quote|sale)",
        }

    def parse_command(self, command: str) -> Dict[str, Any]:
        """
        Parse command and determine which agents to use
        Returns: {primary_agent, secondary_agents, intent, entities}
        """

        command_lower = command.lower()

        # Detect intent
        intents = []
        for intent, pattern in self.patterns.items():
            if re.search(pattern, command_lower):
                intents.append(intent)

        # Default to "build" if no intent detected
        if not intents:
            intents = ["build"]

        # Map intents to agents
        agent_mapping = {
            "plan": "planner",
            "build": "technical",
            "analyze": "business",
            "automate": "automation",
            "risk": "risk",
            "learn": "technical",
            "roll_forming": "technical",
            "cad": "technical",
            "crm": "business",
        }

        agents = []
        for intent in intents:
            agent = agent_mapping.get(intent)
            if agent and agent not in agents:
                agents.append(agent)

        # Always add planner for complex commands
        if len(command.split()) > 10:
            if "planner" not in agents:
                agents.insert(0, "planner")

        return {
            "primary_agent": agents[0] if agents else "technical",
            "agents": agents,
            "intents": intents,
            "raw_command": command
        }

    def run(self, command: str, use_context: bool = True,
            use_all_agents: bool = False) -> CommandResult:
        """
        Execute a command through the PRO engine

        Args:
            command: The user's command
            use_context: Whether to include recent memory context
            use_all_agents: Whether to run all 5 agents

        Returns:
            CommandResult with full execution details
        """

        start_time = datetime.now()

        try:
            # Parse command
            parsed = self.parse_command(command)

            # Get context from memory
            context = ""
            context_used = False

            if use_context:
                context = get_context(limit=3)
                context_used = True

            # Build full prompt
            full_prompt = f"""User Command: {command}

{context if context else "(No previous context)"}"""

            # Execute agents
            if use_all_agents:
                # Run all 5 agents
                results = self.orchestrator.run_all(command, context)
                final_response = self.orchestrator.format_results(results)
                agents_used = list(results.keys())
            else:
                # Run primary agent only
                primary = parsed["primary_agent"]

                if primary == "planner":
                    response = planner_ai(command, context)
                elif primary == "technical":
                    response = technical_ai(command, context)
                elif primary == "business":
                    response = business_ai(command, context)
                elif primary == "automation":
                    response = automation_ai(command, context)
                elif primary == "risk":
                    response = risk_ai(command, context)
                else:
                    response = technical_ai(command, context)

                agents_used = [primary]
                final_response = f"🤖 **{primary.upper()} AGENT**\n\n{response}"

            # Save to memory
            save_memory(command, final_response[:500], {
                "agents": agents_used,
                "intents": parsed["intents"]
            })

            # Check for automation triggers
            automation_triggered = self._check_automation(command)

            # Calculate execution time
            exec_time = int((datetime.now() - start_time).total_seconds() * 1000)

            return CommandResult(
                command=command,
                final_response=final_response,
                agents_used=agents_used,
                context_used=context_used,
                automation_triggered=automation_triggered,
                execution_time_ms=exec_time,
                success=True
            )

        except Exception as e:
            exec_time = int((datetime.now() - start_time).total_seconds() * 1000)
            return CommandResult(
                command=command,
                final_response=f"❌ Error: {str(e)}",
                agents_used=[],
                context_used=False,
                automation_triggered=False,
                execution_time_ms=exec_time,
                success=False,
                error=str(e)
            )

    def _check_automation(self, command: str) -> bool:
        """Check if command should trigger automation"""

        automation_keywords = [
            "create lead", "add customer", "send email",
            "schedule", "remind", "notify", "whatsapp",
            "telegram", "n8n", "webhook"
        ]

        command_lower = command.lower()
        return any(keyword in command_lower for keyword in automation_keywords)

    def get_suggestions(self, partial: str) -> List[str]:
        """Get command suggestions based on partial input"""

        suggestions = [
            "build a CRM system for my business",
            "analyze market for roll forming machines",
            "plan a new product launch",
            "automate lead follow-up with n8n",
            "design C-Channel profile in AutoCAD",
            "create quotation for customer",
            "assess risks of this project",
            "learn about roll forming process",
            "build a chatbot for my website",
            "analyze competitor pricing",
        ]

        partial_lower = partial.lower()
        matching = [s for s in suggestions if partial_lower in s.lower()]

        return matching[:5] if matching else suggestions[:3]

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""

        return {
            "memory_stats": self.memory.get_stats(self.user_id),
            "available_agents": list(self.orchestrator.agents.keys()),
            "engine_version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
engine = ProEngine()


# Convenience functions
def run_engine(command: str, use_context: bool = True,
               use_all_agents: bool = False) -> CommandResult:
    """Run command through PRO engine"""
    return engine.run(command, use_context, use_all_agents)

def quick_response(command: str) -> str:
    """Quick single-agent response"""
    result = run_engine(command, use_context=True, use_all_agents=False)
    return result.final_response

def full_analysis(command: str) -> str:
    """Full 5-agent analysis"""
    result = run_engine(command, use_context=True, use_all_agents=True)
    return result.final_response


# Example prompts the engine handles
EXAMPLE_PROMPTS = {
    "roll_forming": [
        "What is the best C-channel profile for industrial sheds?",
        "Calculate material for Z-purlin roof system",
        "Design a 7-station roll forming line",
    ],
    "business": [
        "Analyze market demand for pre-engineered buildings",
        "Create pricing strategy for custom profiles",
        "What are growth opportunities in construction?",
    ],
    "automation": [
        "Automate lead capture from website to CRM",
        "Set up WhatsApp notifications for new orders",
        "Create daily sales report workflow",
    ],
    "cad": [
        "Generate AutoCAD script for C-150 profile",
        "Draw shaft detail for 50mm diameter",
        "Create 2D layout for roll assembly",
    ]
}


if __name__ == "__main__":
    print("🚀 PRO ENGINE TEST\n")
    print("=" * 60)

    # Test command parsing
    print("\n📋 Command Parsing Test:")
    test_commands = [
        "build a CRM system",
        "analyze market for roll forming",
        "plan a new product launch",
        "automate lead follow-up",
        "what are the risks of this approach?",
    ]

    for cmd in test_commands:
        parsed = engine.parse_command(cmd)
        print(f"  '{cmd}'")
        print(f"    → Agents: {parsed['agents']}, Intents: {parsed['intents']}\n")

    # Test execution
    print("\n" + "=" * 60)
    print("\n⚡ Execution Test:")

    result = run_engine("How do I build a customer service chatbot?", use_all_agents=False)
    print(f"\nCommand: {result.command}")
    print(f"Agents Used: {result.agents_used}")
    print(f"Context Used: {result.context_used}")
    print(f"Execution Time: {result.execution_time_ms}ms")
    print(f"\nResponse:\n{result.final_response[:300]}...")

    # Stats
    print("\n" + "=" * 60)
    stats = engine.get_stats()
    print(f"\n📊 System Stats:")
    print(json.dumps(stats, indent=2))
