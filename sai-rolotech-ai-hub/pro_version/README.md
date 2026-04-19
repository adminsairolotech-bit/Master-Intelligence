# 🧠 Life Command AI - PRO ENGINE

## 🚀 Overview

**Life Command AI PRO** is a universal AI-powered system that transforms simple commands into powerful, multi-agent powered outputs. Works with any software via copy-paste automation.

```
ANY SOFTWARE → Text Select → CTRL+SHIFT+A → AI Processing → Smart Output
```

---

## 🎯 What It Does

| Feature | Description |
|---------|-------------|
| **🧠 Memory System** | Persistent SQLite storage, remembers past commands |
| **🤖 5 AI Agents** | Planner, Technical, Business, Automation, Risk |
| **⚡ PRO Engine** | Unifies memory + agents into one brain |
| **🔗 Automation** | n8n triggers for workflows (lead creation, notifications) |
| **💻 Multi-UI** | Web dashboard, CLI, API |

---

## 🧩 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   USER COMMAND                                               │
│        ↓                                                     │
│   ┌─────────────┐                                           │
│   │   MEMORY    │ ← Stores context & history                 │
│   └─────────────┘                                           │
│        ↓                                                     │
│   ┌─────────────────────────────────────────┐               │
│   │            PRO ENGINE                    │               │
│   │  ┌─────────┐  ┌──────────────────────┐  │               │
│   │  │ PARSER │→ │ AI AGENTS (5)        │  │               │
│   │  └─────────┘  │ 📋 Planner          │  │               │
│   │               │ 💻 Technical        │  │               │
│   │               │ 📊 Business       │  │               │
│   │               │ ⚡ Automation     │  │               │
│   │               │ ⚠️ Risk          │  │               │
│   │               └──────────────────────┘  │               │
│   └─────────────────────────────────────────┘               │
│        ↓                                                     │
│   ┌─────────────┐                                           │
│   │ AUTOMATION │ → n8n webhooks, notifications              │
│   └─────────────┘                                           │
│        ↓                                                     │
│   SMART OUTPUT                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Installation

```bash
cd sai-rolotech-ai-hub

# Install dependencies
pip install anthropic requests

# Run the API server
python main.py

# OR run the CLI
python pro_version/cli.py

# OR open in browser
# http://localhost:8505/api/pro/
```

---

## 🔧 Configuration

Create `.env` file:

```env
# AI Providers
ANTHROPIC_API_KEY=sk-ant-xxxxx      # Claude (recommended)
OPENROUTER_API_KEY=sk-or-xxxxx       # Fallback
GEMINI_API_KEY=AIzaSyxxxxx           # Free tier

# n8n Automation
N8N_WEBHOOK_URL=http://localhost:5678/webhook

# Messaging
TELEGRAM_BOT_TOKEN=xxxxx
WHATSAPP_API=xxxxx
```

---

## 🎮 Usage Modes

### 1. Quick Mode (Single Agent)
```python
from pro_version import quick_response

result = quick_response("build a CRM for my business")
print(result)
```

### 2. Full Analysis (5 Agents)
```python
from pro_version import full_analysis

result = full_analysis("design an automation workflow for lead follow-up")
print(result)
```

### 3. CLI
```bash
$ python pro_version/cli.py

🎯 You: build a CRM for my business
⚡ Processing through PRO Engine...

══════════════════════════════════════════════════════
🤖 PLANNER AGENT ✅
───────────────────────────────────────
1. **Step 1**: Define core entities (Leads, Contacts, Deals)
2. **Step 2**: Design database schema
...

══════════════════════════════════════════════════════
🤖 TECHNICAL AGENT ✅
───────────────────────────────────────
Architecture: REST API with FastAPI
Database: SQLite (simple) / PostgreSQL (production)
...
```

### 4. Web Dashboard
```
http://localhost:8505/api/pro/
```
- Modern cyberpunk UI
- Real-time chat
- Agent badges showing which agents responded
- Memory sidebar
- Statistics panel

---

## 🤖 The 5 AI Agents

| Agent | Icon | Role | When Used |
|-------|------|------|-----------|
| **Planner** | 📋 | Strategic planning, task breakdown | "plan a launch" |
| **Technical** | 💻 | Code, architecture, solutions | "build a system" |
| **Business** | 📊 | Strategy, market analysis | "analyze market" |
| **Automation** | ⚡ | Workflow design, n8n | "automate this" |
| **Risk** | ⚠️ | Risk assessment, mitigations | "what could go wrong" |

---

## 🔄 Command → Output Flow

```
1. USER TYPES COMMAND
   "build a CRM for my business"

2. PRO ENGINE PARSES
   → Detects intent: "build"
   → Selects agents: [planner, technical, business]

3. MEMORY CHECKS CONTEXT
   → Retrieves last 5 commands
   → Builds context string for AI

4. AI AGENTS RUN (parallel)
   → Planner: Creates step-by-step plan
   → Technical: Provides architecture
   → Business: Analyzes market fit

5. RESULTS COMBINED
   → Formatted into unified response
   → Saved to memory

6. AUTOMATION TRIGGERS (if detected)
   → "create lead" → n8n webhook
   → "send email" → email workflow
```

---

## 📋 Example Commands

### Roll Forming
```bash
> What is the best C-channel profile for industrial sheds?
> Calculate material for Z-purlin roof system
> Design a 7-station roll forming line
```

### Business
```bash
> Analyze market demand for pre-engineered buildings
> Create pricing strategy for custom profiles
> What are growth opportunities in construction?
```

### Automation
```bash
> Automate lead capture from website to CRM
> Set up WhatsApp notifications for new orders
> Create daily sales report workflow
```

### CAD
```bash
> Generate AutoCAD script for C-150 profile
> Draw shaft detail for 50mm diameter
> Create 2D layout for roll assembly
```

---

## 🔗 n8n Integration

The automation system automatically detects workflow opportunities:

| Trigger | Action | n8n Webhook |
|---------|--------|-------------|
| "new lead" | Create CRM entry | `/webhook/lead-create` |
| "send email" | Email workflow | `/webhook/email` |
| "schedule" | Calendar reminder | `/webhook/schedule` |
| "whatsapp" | Send message | `/webhook/whatsapp` |

---

## 📁 Project Structure

```
sai-rolotech-ai-hub/
├── pro_version/
│   ├── __init__.py          # Package exports
│   ├── memory.py             # SQLite memory system
│   ├── agents.py             # 5 AI agents (Claude/OpenRouter)
│   ├── engine.py              # PRO brain (memory + agents)
│   ├── automation.py          # n8n triggers
│   ├── api.py                 # FastAPI routes
│   ├── cli.py                 # Command-line interface
│   └── index.html             # Web dashboard
├── main.py                    # Main FastAPI app
└── dashboard.py              # Streamlit dashboard
```

---

## 🔐 API Reference

### POST /api/pro/chat
```json
{
    "message": "build a CRM for my business",
    "full_analysis": true,
    "use_context": true
}
```

### GET /api/pro/context
Get recent context for AI prompts.

### GET /api/pro/memory
Get memory history.

### GET /api/pro/stats
Get system statistics.

### POST /api/pro/automation/process
Process AI response for automation triggers.

---

## 🚀 Deployment

### Local
```bash
python main.py
# → API at http://localhost:8505
# → PRO UI at http://localhost:8505/api/pro/
```

### Production
```bash
# Use gunicorn for production
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Docker (optional)
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

---

## 🎯 Keyboard Shortcut Tool

For universal copy-paste automation:

```python
# computer_use.py integration
from computer_use import ComputerUse

c = ComputerUse()

# In any software:
# 1. Select text
# 2. Press CTRL+SHIFT+A
# 3. AI processes and auto-pastes result
```

---

## ⚠️ Limitations

- Internet required for AI calls
- API costs apply (Claude is paid, OpenRouter/Gemini have free tiers)
- Copy-paste based (not direct software control)
- Rate limits on free AI tiers

---

## 🚀 Future Upgrades

- [ ] Voice command input
- [ ] Floating AI button overlay
- [ ] AutoCAD direct integration
- [ ] WhatsApp bot
- [ ] Multi-user support
- [ ] Scheduled tasks

---

## 📜 License

MIT - SAI Rolotech

---

**Built with ❤️ for maximum AI power**
