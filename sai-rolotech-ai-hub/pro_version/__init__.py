"""
PRO Version - SAI Rolotech AI Hub
================================

A powerful AI system combining:
- Memory System (persistent SQLite storage)
- AI Agents (5 specialized Claude-powered agents)
- Engine (unified brain combining memory + agents)
- Automation (n8n workflow triggers)

Usage:
    from pro_version.engine import run_engine, full_analysis

    # Quick response
    result = run_engine("build a CRM system")

    # Full 5-agent analysis
    result = full_analysis("design an automation workflow")
"""

from .memory import MemoryStore, memory_store, save_memory, get_context
from .agents import (
    AIAgentOrchestrator,
    orchestrator,
    ai_call,
    planner_ai,
    technical_ai,
    business_ai,
    automation_ai,
    risk_ai,
    run_all_agents
)
from .engine import (
    ProEngine,
    engine,
    run_engine,
    quick_response,
    full_analysis,
    CommandResult
)
from .automation import (
    AutomationTrigger,
    automation,
    trigger_automation,
    queue_action,
    execute_queue,
    ActionType
)

__version__ = "1.0.0"
__all__ = [
    # Memory
    "MemoryStore",
    "memory_store",
    "save_memory",
    "get_context",
    # Agents
    "AIAgentOrchestrator",
    "orchestrator",
    "ai_call",
    "planner_ai",
    "technical_ai",
    "business_ai",
    "automation_ai",
    "risk_ai",
    "run_all_agents",
    # Engine
    "ProEngine",
    "engine",
    "run_engine",
    "quick_response",
    "full_analysis",
    "CommandResult",
    # Automation
    "AutomationTrigger",
    "automation",
    "trigger_automation",
    "queue_action",
    "execute_queue",
    "ActionType",
]
