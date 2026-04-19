"""
PRO Version AI Agents
=====================
Claude + Gemini powered multi-agent system
5 specialized agents working together
"""

import os
import json
import anthropic
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# API Keys from environment
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Model configurations
CLAUDE_MODEL = "claude-sonnet-4-6"
FREE_MODELS = [
    "google/gemini-2.0-flash-exp",
    "deepseek/deepseek-chat-v3",
    "meta-llama/llama-3.3-70b-instruct",
]

@dataclass
class AgentResponse:
    """Response from an AI agent"""
    agent_name: str
    response: str
    success: bool
    model_used: str
    tokens_used: int = 0
    error: Optional[str] = None

class BaseAgent:
    """Base class for all AI agents"""

    def __init__(self, name: str, role: str, model: str = CLAUDE_MODEL):
        self.name = name
        self.role = role
        self.model = model
        self.client = None

        if ANTHROPIC_API_KEY:
            self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def think(self, prompt: str, context: str = "") -> AgentResponse:
        """Send prompt to AI and get response"""

        system_prompt = f"""You are {self.name}, a specialized AI agent.
Role: {self.role}

Always provide clear, actionable, and specific responses.
Be technical but practical.
"""

        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        # Try Claude first
        if self.client:
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    system=system_prompt,
                    messages=[{"role": "user", "content": full_prompt}]
                )

                return AgentResponse(
                    agent_name=self.name,
                    response=response.content[0].text,
                    success=True,
                    model_used=self.model,
                    tokens_used=response.usage.output_tokens
                )
            except Exception as e:
                return AgentResponse(
                    agent_name=self.name,
                    response="",
                    success=False,
                    model_used=self.model,
                    error=str(e)
                )

        # Fallback to OpenRouter
        if OPENROUTER_API_KEY:
            return self._openrouter_call(system_prompt, full_prompt)

        return AgentResponse(
            agent_name=self.name,
            response="No AI provider configured",
            success=False,
            model_used="none",
            error="Missing API keys"
        )

    def _openrouter_call(self, system: str, prompt: str) -> AgentResponse:
        """Fallback to OpenRouter API"""
        try:
            import requests

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 2048
                }
            )

            if response.status_code == 200:
                data = response.json()
                return AgentResponse(
                    agent_name=self.name,
                    response=data["choices"][0]["message"]["content"],
                    success=True,
                    model_used=data["model"]
                )
            else:
                return AgentResponse(
                    agent_name=self.name,
                    response="",
                    success=False,
                    model_used="openrouter",
                    error=f"HTTP {response.status_code}"
                )
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                response="",
                success=False,
                model_used="openrouter",
                error=str(e)
            )


# ==================== SPECIALIZED AGENTS ====================

class PlannerAgent(BaseAgent):
    """
    PLANNER AGENT
    Breaks down complex tasks into step-by-step plans
    """

    def __init__(self):
        super().__init__(
            name="Planner",
            role="Strategic planning and task decomposition specialist"
        )

    def plan(self, task: str, context: str = "") -> AgentResponse:
        """Create a detailed plan for the given task"""

        prompt = f"""Task: {task}

Create a step-by-step plan to accomplish this task.

Format your response as:
1. **Step 1**: [Description] - [Why this matters]
2. **Step 2**: [Description] - [Why this matters]
...

Be specific and actionable. Each step should be clear enough to execute directly.
"""

        return self.think(prompt, context)


class TechnicalAgent(BaseAgent):
    """
    TECHNICAL AGENT
    Provides technical solutions and code
    """

    def __init__(self):
        super().__init__(
            name="Technical",
            role="Software engineering and technical architecture specialist"
        )

    def solve(self, problem: str, context: str = "") -> AgentResponse:
        """Provide technical solution to the problem"""

        prompt = f"""Problem: {problem}

Provide a comprehensive technical solution.

Include:
- Architecture approach
- Code examples (if applicable)
- Best practices
- Potential pitfalls to avoid

Be practical and production-ready.
"""

        return self.think(prompt, context)


class BusinessAgent(BaseAgent):
    """
    BUSINESS AGENT
    Analyzes business models and strategy
    """

    def __init__(self):
        super().__init__(
            name="Business",
            role="Business analysis and strategy specialist"
        )

    def analyze(self, topic: str, context: str = "") -> AgentResponse:
        """Analyze business aspects of the topic"""

        prompt = f"""Topic: {topic}

Provide a business analysis including:

- Market opportunity
- Revenue model
- Key success factors
- Risks and mitigations
- Growth potential

Be concise but insightful.
"""

        return self.think(prompt, context)


class AutomationAgent(BaseAgent):
    """
    AUTOMATION AGENT
    Designs automation workflows and integrations
    """

    def __init__(self):
        super().__init__(
            name="Automation",
            role="Workflow automation and system integration specialist"
        )

    def design_workflow(self, goal: str, context: str = "") -> AgentResponse:
        """Design automation workflow for the given goal"""

        prompt = f"""Goal: {goal}

Design an automation workflow to achieve this goal.

Include:
- Trigger conditions
- Step-by-step process
- Tools/services to use
- Error handling
- Success metrics

Think about: n8n, Zapier, webhooks, APIs, scheduled tasks
"""

        return self.think(prompt, context)


class RiskAgent(BaseAgent):
    """
    RISK AGENT
    Identifies risks and provides mitigation strategies
    """

    def __init__(self):
        super().__init__(
            name="Risk",
            role="Risk assessment and mitigation planning specialist"
        )

    def assess(self, plan: str, context: str = "") -> AgentResponse:
        """Assess risks in the given plan or approach"""

        prompt = f"""Plan/Approach: {plan}

Conduct a risk assessment:

For each risk identify:
- Risk Type: [Technical/Financial/Operational/External]
- Severity: [Critical/High/Medium/Low]
- Likelihood: [Probable/Possible/Unlikely]
- Mitigation Strategy

Format as a prioritized list.
"""

        return self.think(prompt, context)


# ==================== MASTER ORCHESTRATOR ====================

class AIAgentOrchestrator:
    """
    Master orchestrator for all AI agents
    Runs agents in parallel and combines results
    """

    def __init__(self):
        self.agents = {
            "planner": PlannerAgent(),
            "technical": TechnicalAgent(),
            "business": BusinessAgent(),
            "automation": AutomationAgent(),
            "risk": RiskAgent()
        }

    def run_all(self, command: str, context: str = "") -> Dict[str, AgentResponse]:
        """Run all 5 agents in parallel"""

        results = {}

        for name, agent in self.agents.items():
            try:
                if name == "planner":
                    results[name] = agent.plan(command, context)
                elif name == "technical":
                    results[name] = agent.solve(command, context)
                elif name == "business":
                    results[name] = agent.analyze(command, context)
                elif name == "automation":
                    results[name] = agent.design_workflow(command, context)
                elif name == "risk":
                    results[name] = agent.assess(command, context)
            except Exception as e:
                results[name] = AgentResponse(
                    agent_name=name,
                    response="",
                    success=False,
                    model_used="unknown",
                    error=str(e)
                )

        return results

    def run_single(self, agent_name: str, prompt: str, context: str = "") -> AgentResponse:
        """Run a single agent"""

        if agent_name not in self.agents:
            return AgentResponse(
                agent_name=agent_name,
                response=f"Unknown agent: {agent_name}",
                success=False,
                model_used="none",
                error="Agent not found"
            )

        agent = self.agents[agent_name]

        try:
            if agent_name == "planner":
                return agent.plan(prompt, context)
            elif agent_name == "technical":
                return agent.solve(prompt, context)
            elif agent_name == "business":
                return agent.analyze(prompt, context)
            elif agent_name == "automation":
                return agent.design_workflow(prompt, context)
            elif agent_name == "risk":
                return agent.assess(prompt, context)
        except Exception as e:
            return AgentResponse(
                agent_name=agent_name,
                response="",
                success=False,
                model_used="unknown",
                error=str(e)
            )

    def format_results(self, results: Dict[str, AgentResponse]) -> str:
        """Format all agent results into a unified response"""

        output = []
        output.append("=" * 60)
        output.append("🔮 MASTER AI RESPONSE - 5 Agents Analyzed Your Request")
        output.append("=" * 60)

        agent_icons = {
            "planner": "📋",
            "technical": "💻",
            "business": "📊",
            "automation": "⚡",
            "risk": "⚠️"
        }

        for name, result in results.items():
            icon = agent_icons.get(name, "🤖")
            status = "✅" if result.success else "❌"

            output.append(f"\n{icon} {result.agent_name.upper()} AGENT {status}")
            output.append("-" * 40)

            if result.success:
                output.append(result.response)
                if result.tokens_used:
                    output.append(f"\n[Model: {result.model_used} | Tokens: {result.tokens_used}]")
            else:
                output.append(f"Error: {result.error}")

        output.append("\n" + "=" * 60)
        return "\n".join(output)


# Singleton instance
orchestrator = AIAgentOrchestrator()


# Convenience functions
def ai_call(prompt: str, context: str = "") -> str:
    """Single AI call using default agent"""
    return orchestrator.run_single("technical", prompt, context).response

def planner_ai(task: str, context: str = "") -> str:
    """Get step-by-step plan"""
    return orchestrator.run_single("planner", task, context).response

def technical_ai(problem: str, context: str = "") -> str:
    """Get technical solution"""
    return orchestrator.run_single("technical", problem, context).response

def business_ai(topic: str, context: str = "") -> str:
    """Get business analysis"""
    return orchestrator.run_single("business", topic, context).response

def automation_ai(goal: str, context: str = "") -> str:
    """Design automation workflow"""
    return orchestrator.run_single("automation", goal, context).response

def risk_ai(plan: str, context: str = "") -> str:
    """Assess risks"""
    return orchestrator.run_single("risk", plan, context).response

def run_all_agents(command: str, context: str = "") -> str:
    """Run all 5 agents and return combined response"""
    results = orchestrator.run_all(command, context)
    return orchestrator.format_results(results)


if __name__ == "__main__":
    print("🤖 PRO AI Agents Test\n")

    # Test single agent
    print("Testing PLANNER agent...")
    plan = planner_ai("Build a CRM system for my business")
    print(plan[:500])

    print("\n" + "=" * 60)

    # Test all agents
    print("\nTesting ALL 5 AGENTS...")
    result = run_all_agents("Design an AI-powered customer service system")
    print(result)
