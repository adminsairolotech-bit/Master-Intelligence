"""
PRO Version API Routes
=====================

FastAPI routes for the PRO Engine system
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Import PRO engine
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pro_version.engine import run_engine, engine
from pro_version.automation import automation, trigger_automation
from pro_version.memory import get_memory, get_context

# Router
router = APIRouter(prefix="/api/pro", tags=["PRO Engine"])

# Request Models
class ProChatRequest(BaseModel):
    message: str
    user_id: int = 1
    full_analysis: bool = False
    use_context: bool = True

class MemoryRequest(BaseModel):
    user_id: int = 1
    limit: int = 10

class AutomationRequest(BaseModel):
    command: str
    response: str
    auto_execute: bool = True

# Routes
@router.post("/chat")
async def pro_chat(request: ProChatRequest):
    """
    Chat with the PRO Engine

    Set full_analysis=true for 5-agent analysis
    """

    try:
        result = run_engine(
            command=request.message,
            use_context=request.use_context,
            use_all_agents=request.full_analysis
        )

        return {
            "response": result.final_response,
            "agents": result.agents_used,
            "context_used": result.context_used,
            "automation_triggered": result.automation_triggered,
            "execution_time_ms": result.execution_time_ms,
            "success": result.success,
            "error": result.error
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context")
async def get_pro_context(user_id: int = 1, limit: int = 5):
    """Get recent context for AI prompts"""

    context = get_context(limit=limit)
    return {"context": context}


@router.get("/memory")
async def get_pro_memory(request: MemoryRequest):
    """Get memory history"""

    memories = get_memory(limit=request.limit)

    # Convert context JSON strings
    for mem in memories:
        if mem.get('context'):
            import json
            try:
                mem['context'] = json.loads(mem['context'])
            except:
                pass

    return {"memories": memories}


@router.get("/stats")
async def get_pro_stats():
    """Get PRO engine statistics"""

    engine_stats = engine.get_stats()
    auto_stats = automation.get_stats()

    return {
        "engine": engine_stats,
        "automation": auto_stats,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/automation/process")
async def process_automation(request: AutomationRequest):
    """
    Process AI response for automation triggers
    """

    results = trigger_automation(
        command=request.command,
        response=request.response,
        auto_execute=request.auto_execute
    )

    return {
        "detected_actions": len(results),
        "results": [
            {
                "action_type": r.action.action_type.value,
                "success": r.success,
                "error": r.error,
                "execution_time_ms": r.execution_time_ms
            }
            for r in results
        ]
    }


@router.get("/automation/queue")
async def get_automation_queue():
    """Get pending automation actions"""

    return {"queue": automation.get_queue()}


@router.get("/automation/history")
async def get_automation_history(limit: int = 20):
    """Get automation execution history"""

    return {"history": automation.get_history(limit)}


@router.post("/automation/execute-queue")
async def execute_automation_queue():
    """Execute all queued automation actions"""

    results = automation.execute_queue()

    return {
        "executed": len(results),
        "results": [
            {
                "action_type": r.action.action_type.value,
                "success": r.success,
                "error": r.error
            }
            for r in results
        ]
    }


# Serve HTML
@router.get("/")
async def pro_ui():
    """Serve the PRO version HTML interface"""

    html_path = os.path.join(os.path.dirname(__file__), "index.html")

    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise HTTPException(status_code=404, detail="UI not found")
