"""
SAI Rolotech AI Hub - Main API
FastAPI Application
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os

from apps.hermes_agent.core.hermes_core import hermes
from apps.interpreter_service.policies.policy_engine import policy
from shared.schemas.database import init_db, Lead, User, Memory, get_session
from shared.utils.logging import log_action, log

# ==================== APP SETUP ====================

app = FastAPI(
    title="SAI Rolotech AI Hub",
    description="Production AI Hub - Hermes Brain, Interpreter, CRM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = init_db()

# ==================== REQUEST/RESPONSE MODELS ====================

class ChatRequest(BaseModel):
    user_id: int
    message: str
    model: Optional[str] = "gemini"

class MemoryRequest(BaseModel):
    user_id: int
    key: str
    value: str

class CodeRequest(BaseModel):
    code: str
    language: str = "shell"

class LeadRequest(BaseModel):
    name: str
    mobile: Optional[str] = None
    email: Optional[str] = None
    source: Optional[str] = "telegram"

# ==================== HERMES ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "name": "SAI Rolotech AI Hub",
        "version": "1.0.0",
        "status": "running",
        "services": {
            "hermes": "/chat",
            "memory": "/memory",
            "interpreter": "/run",
            "crm": "/crm"
        }
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat with Hermes AI"""
    log_action(request.user_id, "chat", "hermes", request.message[:50])

    response = hermes.think(
        user_id=request.user_id,
        message=request.message,
        model=request.model
    )

    return {
        "response": response,
        "model": request.model,
        "user_id": request.user_id
    }

@app.get("/memory/{user_id}")
async def get_memories(user_id: int):
    """Get all user memories"""
    memories = hermes.get_all_memories(user_id)
    return {"memories": memories}

@app.post("/memory")
async def save_memory(request: MemoryRequest):
    """Save a memory"""
    result = hermes.remember(request.user_id, request.key, request.value)
    return {"result": result}

# ==================== INTERPRETER ENDPOINTS ====================

@app.post("/run")
async def run_code(request: CodeRequest):
    """Run code with policy enforcement"""
    log_action(0, "code_run", "interpreter", request.code[:50])

    result = policy.execute(request.code, request.language)
    return result

# ==================== CRM ENDPOINTS ====================

@app.post("/crm/lead")
async def create_lead(request: LeadRequest):
    """Create a new lead"""
    session = get_session()

    lead = Lead(
        name=request.name,
        mobile=request.mobile,
        email=request.email,
        source=request.source,
        stage="new"
    )

    session.add(lead)
    session.commit()
    session.refresh(lead)

    log_action(0, "lead_create", "crm", request.name)

    return {"lead": lead.to_dict()}

@app.get("/crm/leads")
async def list_leads(stage: Optional[str] = None):
    """List all leads"""
    session = get_session()

    query = session.query(Lead)
    if stage:
        query = query.filter(Lead.stage == stage)

    leads = query.order_by(Lead.created_at.desc()).all()

    return {"leads": [l.to_dict() for l in leads]}

@app.get("/crm/lead/{lead_id}")
async def get_lead(lead_id: int):
    """Get lead by ID"""
    session = get_session()
    lead = session.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return {"lead": lead.to_dict()}

@app.put("/crm/lead/{lead_id}")
async def update_lead(lead_id: int, request: LeadRequest):
    """Update a lead"""
    session = get_session()
    lead = session.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.name = request.name
    lead.mobile = request.mobile
    lead.email = request.email
    session.commit()

    return {"lead": lead.to_dict()}

@app.get("/crm/stats")
async def get_stats():
    """Get CRM statistics"""
    session = get_session()

    total = session.query(Lead).count()
    new_leads = session.query(Lead).filter(Lead.stage == "new").count()
    contacted = session.query(Lead).filter(Lead.stage == "contacted").count()
    won = session.query(Lead).filter(Lead.stage == "won").count()

    return {
        "total_leads": total,
        "new": new_leads,
        "contacted": contacted,
        "won": won
    }

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ai-hub"}


# ==================== MAIN ====================

if __name__ == "__main__":
    port = int(os.getenv("PORT_HERMES", "8505"))
    log.info(f"Starting SAI Rolotech AI Hub on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
