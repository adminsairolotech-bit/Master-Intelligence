"""
PRO Version AI Agents
=====================
Claude + Gemini powered multi-agent system
5 specialized agents working together
"""

import os
import anthropic
from typing import Optional, Dict
from dataclasses import dataclass

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

        system_prompt = f"""You are {self.name}, a world-class expert AI assistant.
Role: {self.role}

UNIVERSAL DOMAINS (You are an expert in ALL):
- Software Engineering, DevOps, Cloud
- Business Strategy, Marketing, Sales
- Data Science, AI/ML, Automation
- Finance, Investment, Operations
- Manufacturing, Engineering, Design
- Healthcare, Legal, Education
- ANY domain the user asks about

SUPREME RESPONSE QUALITY STANDARDS:

1. **SPECIFICITY** - Never vague. Give exact numbers, names, steps.
   BAD: "Improve your code quality"
   GOOD: "Add unit tests to achieve 80% coverage, refactor functions >50 lines"

2. **STRUCTURE** - Use headers, bullets, numbered lists
   BAD: "Here's some advice..."
   GOOD: "## Strategy\n1. First... 2. Second..."

3. **CONTEXT** - Explain WHY, not just WHAT
   BAD: "Use microservices"
   GOOD: "Use microservices for teams >10 to enable independent deployments"

4. **ACTIONABLE** - Someone can execute immediately
   BAD: "Consider better architecture"
   GOOD: "Refactor into services: Auth, Orders, Inventory"

5. **PRACTICAL** - Real-world, not theoretical
   BAD: "LTS version is recommended"
   GOOD: "Use Node.js 20 LTS - Long term support until 2027, LTS active"

6. **HONEST** - Acknowledge trade-offs
   BAD: "This is the best solution"
   GOOD: "Option A is faster but costs 2x. Option B is cheaper but slower."

OUTPUT FORMAT:
- Start with key insight (1 sentence)
- Use ## Headers for sections
- Bullet points for lists
- Code blocks with language tags
- Tables for comparisons
- Bold for emphasis on key terms

TONE: Confident, direct, like a Stanford professor teaching a smart student.
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

Create an EXHAUSTIVE, EXECUTABLE plan. Someone should be able to complete this task with ZERO follow-up questions.

## 📋 PLAN FORMAT (MUST FOLLOW EXACTLY)

### 🎯 Goal (1 sentence)
Clear definition of success

### ⏱️ Timeline
Total duration + key milestones

### 📦 Phase 1: Foundation (Do First)
1. **[Specific Action]**
   → **Deliverable:** [Exact output]
   → **Time:** [Duration]
   → **Why:** [Business/technical rationale]

2. **[Specific Action]**
   → **Deliverable:** [Exact output]
   → **Time:** [Duration]
   → **Why:** [Business/technical rationale]

### 🔨 Phase 2: Core Work
3. **[Specific Action]**
   → **Deliverable:** [Exact output]
   → **Time:** [Duration]
   → **Why:** [Business/technical rationale]

4. **[Specific Action]**
   → **Deliverable:** [Exact output]
   → **Time:** [Duration]
   → **Why:** [Business/technical rationale]

### 🚀 Phase 3: Launch/Validate
5. **[Specific Action]**
   → **Deliverable:** [Exact output]
   → **Time:** [Duration]
   → **Why:** [Business/technical rationale]

### 📊 Success Metrics
- [Metric 1]: Target value
- [Metric 2]: Target value

### ⚠️ Critical Path Items (don't skip these!)
1. [Item that can break everything]
2. [Item that can break everything]

### 🎯 Quick Wins (do these first for momentum)
1. [Something that takes <1 hour but shows progress]

RULES:
- Each step must be actionable with clear ownership
- Include dependencies: "After X is done, do Y"
- Specify tools/services to use
- Estimate effort: <1hr, half-day, day, week
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

Provide a PRODUCTION-READY technical solution.

## 🏗️ Architecture Overview
[High-level design - describe components and relationships]

## 📐 System Design
```
[Architecture diagram in text format]
Example:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───→│   API GW    │───→│   Service   │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 💻 Implementation

### Core Code
```[language]
[Complete, runnable code - not snippets]
```

### Setup Instructions
1. [Step by step setup]
2. [Step by step setup]

## ⚡ Best Practices Applied
- [Practice 1]
- [Practice 2]
- [Practice 3]

## 🚨 Pitfalls to Avoid
| Common Mistake | How to Prevent |
|----------------|----------------|
| [Mistake] | [Solution] |

## 📈 Scaling Considerations
- [Scaling point 1]
- [Scaling point 2]

## 🧪 Testing Strategy
```[language]
[Test code example]
```

RULES:
- Code must be complete and runnable
- Include error handling
- Include imports/exports
- Use modern patterns (async/await, etc.)
- Specify language, framework, version
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

Conduct a COMPREHENSIVE business analysis with actionable insights.

## 📊 Executive Summary
[2-3 sentences: What is this? Why does it matter? What should we do?]

## 🎯 Market Opportunity
- **TAM (Total Addressable Market):** [Size + Source]
- **SAM (Serviceable Addressable Market):** [Size + Source]
- **SOM (Serviceable Obtainable Market):** [Size + Source]
- **Growth Rate:** [X% CAGR]
- **Key Trend:** [Primary market driver]

## 💰 Business Model & Revenue
- **Primary Revenue Stream:** [Model description]
- **Pricing Strategy:** [Approach + Rationale]
- **Unit Economics:**
  - CAC: [Customer Acquisition Cost]
  - LTV: [Lifetime Value]
  - LTV:CAC Ratio: [X:1] → [Good if >3:1]
- **Margins:** [Gross/Net margins]

## 🏆 Competitive Landscape
| Competitor | Strength | Weakness | Your Advantage |
|------------|----------|----------|---------------|
| [Name] | [X] | [Y] | [Z] |

## ✅ Key Success Factors
1. **[Factor 1]** - Why it matters + How to achieve
2. **[Factor 2]** - Why it matters + How to achieve
3. **[Factor 3]** - Why it matters + How to achieve

## ⚠️ Risks & Mitigations
| Risk | Severity | Mitigation |
|------|----------|------------|
| [Risk 1] | [H/M/L] | [Mitigation] |
| [Risk 2] | [H/M/L] | [Mitigation] |

## 📈 Growth Strategy
1. **Phase 1 (0-6 months):** [Approach]
2. **Phase 2 (6-12 months):** [Approach]
3. **Phase 3 (Year 2+):** [Approach]

## 🚀 Recommended Next Steps
1. **[Immediate action]** - [1 week]
2. **[Short-term action]** - [1 month]
3. **[Long-term action]** - [3-6 months]

RULES:
- Use real-world numbers (not "could be millions")
- Cite data sources when possible
- Be honest about uncertainties
- Focus on actionable insights
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

Design a COMPLETE automation workflow with all details.

## 🔄 Workflow Overview
**Trigger:** [What starts this workflow?]
**Frequency:** [Real-time / Scheduled / On-demand]
**End Result:** [What does this produce?]

## 📋 Workflow Diagram
```
┌─────────────┐
│   TRIGGER  │ ← What starts this?
└──────┬──────┘
       ↓
┌─────────────┐
│   STEP 1    │ ← What happens first?
│   Action    │
└──────┬──────┘
       ↓
┌─────────────┐
│   STEP 2    │ ← What happens next?
│   Action    │
└──────┬──────┘
       ↓
    [More steps as needed]
       ↓
┌─────────────┐
│  COMPLETE   │ ← What's the final output?
└─────────────┘
```

## 🔧 Implementation Details

### Trigger Configuration
```
Type: [Webhook/API/Schedule/Event]
Endpoint: [URL if webhook]
Payload: [Expected data format]
```

### Step-by-Step Instructions

**Step 1: [Name]**
- Action: [What to do]
- Config: [Specific settings]
- If error: [Error handling]

**Step 2: [Name]**
- Action: [What to do]
- Config: [Specific settings]
- If error: [Error handling]

### Tools & Services
| Step | Tool | Why This Tool |
|------|------|---------------|
| 1 | [n8n/API/Webhook/etc] | [Reason] |
| 2 | [Tool] | [Reason] |

## ⚠️ Error Handling
| Error Type | Response |
|------------|----------|
| API timeout | [Retry 3x, then alert] |
| Invalid data | [Log + skip + notify] |
| Auth failure | [Alert + pause workflow] |

## 📊 Success Metrics
- **Runs per day:** [Expected volume]
- **Success rate target:** [X%]
- **Time saved:** [X hours/day]
- **Cost per run:** [Amount]

## 🚀 Quick Setup Commands

### n8n
```
[CLI commands or n8n node configuration]
```

### Alternative: Python Script
```python
[Complete Python automation script]
```

### Alternative: Zapier
```
[Zap configuration steps]
```

RULES:
- Make it beginner-friendly
- Include actual code/config snippets
- Specify all credentials needed
- Include backup/error procedures
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

Conduct a THOROUGH risk assessment. Think like a paranoid but rational expert.

## 🎯 Executive Risk Summary
[1-2 sentences: What are the TOP 2 risks that could kill this?]

## 🔴 CRITICAL Risks (Stop Everything)
| Risk | Impact | Probability | Immediate Action |
|------|--------|-------------|------------------|
| [Risk that could fail entirely] | [What happens] | [H/M/L] | [What to do NOW] |

## 🟠 HIGH Risks (Fix Before Launch)
| Risk | Impact | Probability | Mitigation | Owner |
|------|--------|-------------|------------|-------|
| [Major risk] | [Consequence] | [H/M/L] | [Specific action] | [Who] |

## 🟡 MEDIUM Risks (Monitor & Plan)
| Risk | Impact | Probability | Mitigation | Timeline |
|------|--------|-------------|------------|----------|
| [Moderate risk] | [Consequence] | [H/M/L] | [Action] | [When] |

## 🟢 LOW Risks (Accept or Watch)
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Minor risk] | [Consequence] | [None/Light] |

## 📊 Risk Matrix
```
                 Probability
              Low    Med    High
Impact  ┌─────────────────────────
High    │  MEDIUM │  HIGH  │ CRITICAL│
        ├─────────────────────────
Medium  │   LOW   │ MEDIUM │  HIGH   │
        ├─────────────────────────
Low     │   LOW   │  LOW   │ MEDIUM  │
        └─────────────────────────
```

## 🛡️ Mitigation Priority
1. **Immediate (This week):** [Critical risk mitigations]
2. **Short-term (This month):** [High risk mitigations]
3. **Long-term (This quarter):** [Medium risk mitigations]

## 🚨 Contingency Plans
| If This Happens | Do This |
|-----------------|---------|
| [Worst case 1] | [Response plan] |
| [Worst case 2] | [Response plan] |

## 📋 Risk Monitoring Dashboard
Track these metrics weekly:
- [Metric 1]
- [Metric 2]
- [Metric 3]

RULES:
- Be paranoid but rational - don't inflate risks
- Give SPECIFIC mitigations, not generic advice
- Estimate cost of mitigation vs cost of risk
- Consider second-order effects
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
