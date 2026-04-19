"""
SAI Rolotech AI Hub - Main API
FastAPI Application
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import asyncio

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

class TTSRequest(BaseModel):
    text: str
    voice: str = "hi_f"  # hi_f, hi_m, en_f, en_m, uk_f
    output_file: Optional[str] = None

# ==================== TTS FUNCTIONS ====================

VOICES = {
    "hi_f": "hi-IN-SwaraNeural",
    "hi_m": "hi-IN-MadhurNeural",
    "en_f": "en-US-JennyNeural",
    "en_m": "en-US-GuyNeural",
    "uk_f": "en-GB-SoniaNeural",
}

async def generate_speech(text: str, voice: str = "hi_f", output_file: str = None):
    """Generate speech with edge-tts"""
    import edge_tts

    voice_id = VOICES.get(voice, VOICES["hi_f"])

    if not output_file:
        safe = text[:30].replace(" ", "_").replace(",", "").replace("?", "")
        output_file = f"{safe}.mp3"

    output_dir = os.path.join("output", "tts")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)

    communicate = edge_tts.Communicate(text, voice_id)
    await communicate.save(output_path)

    return output_path

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

# ==================== TTS ENDPOINTS ====================

@app.get("/tts/voices")
async def list_tts_voices():
    """List available TTS voices"""
    return {
        "voices": [
            {"id": "hi_f", "name": "Swara (Hindi Female)", "language": "hi"},
            {"id": "hi_m", "name": "Madhur (Hindi Male)", "language": "hi"},
            {"id": "en_f", "name": "Jenny (English Female)", "language": "en"},
            {"id": "en_m", "name": "Guy (English Male)", "language": "en"},
            {"id": "uk_f", "name": "Sonia (UK Female)", "language": "en-GB"},
        ]
    }

@app.post("/tts/speak")
async def tts_speak(request: TTSRequest):
    """Generate speech - returns file path"""
    try:
        output_path = await generate_speech(request.text, request.voice, request.output_file)
        return {
            "success": True,
            "file": output_path,
            "text": request.text,
            "voice": request.voice
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tts/stream/{filename}")
async def tts_stream(filename: str):
    """Stream audio file"""
    output_dir = os.path.join("output", "tts")
    file_path = os.path.join(output_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="audio/mpeg")

@app.get("/tts/download/{filename}")
async def tts_download(filename: str):
    """Download audio file"""
    output_dir = os.path.join("output", "tts")
    file_path = os.path.join(output_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename
    )

@app.post("/tts/chat-speak")
async def tts_chat_speak(request: TTSRequest):
    """Chat + TTS - generates response and speaks it"""
    from apps.hermes_agent.core.hermes_core import hermes

    # Get AI response
    response = hermes.think(user_id=0, message=request.text, model="gemini")

    # Generate speech
    try:
        output_path = await generate_speech(response, request.voice, request.output_file)
        return {
            "success": True,
            "text": request.text,
            "response": response,
            "audio_file": output_path,
            "voice": request.voice
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MAIN ====================

if __name__ == "__main__":
    port = int(os.getenv("PORT_HERMES", "8505"))
    log.info(f"Starting SAI Rolotech AI Hub on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
