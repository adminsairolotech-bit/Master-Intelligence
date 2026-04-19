# SAI Rolotech AI Hub - Production Ready

## 🤖 Full Auto AI System

```
Telegram → OpenClaw → Hermes (Brain) → Policy Check → Tool → Result → Reply
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER (Telegram/WhatsApp)                 │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OPENCLAW (Entry Layer)                      │
│                   Telegram Bot + Message Handler                 │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      HERMES (Master Router)                     │
│                                                                     │
│   1. Intent Detection    → What does user want?                   │
│   2. Tool Selection     → Which tool to use?                    │
│   3. Model Selection     → Which AI model?                       │
│   4. Policy Check        → Is action safe?                        │
│   5. Response Generation → Format reply                          │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
              ┌─────────┐   ┌─────────┐   ┌─────────┐
              │   CRM   │   │INTERPRETER│   │   n8n   │
              │ Store  │   │  Act    │   │ Automate│
              └────┬────┘   └────┬────┘   └────┬────┘
                   │             │             │
                   └─────────────┴─────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RESPONSE BACK TO USER                      │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### 1. Hermes Master Router
- **File:** `apps/hermes-agent/core/master_router.py`
- **Role:** Brain of the system
- **Powers:**
  - Intent Detection
  - Tool Selection
  - Model Selection
  - Policy Check
  - Response Generation

### 2. OpenClaw Command Parser
- **File:** `apps/openclaw-bot/command_parser.py`
- **Role:** Entry/Exit layer
- **Maps:** Telegram commands → Hermes actions

### 3. Interpreter Policy Engine
- **File:** `apps/interpreter-service/policies/policy_engine.py`
- **Role:** Security guard for code execution
- **Rules:**
  - Allowed commands whitelist
  - Blocked dangerous patterns
  - Approval for risky actions

### 4. n8n Workflows
- **Location:** `workflows/n8n/`
- **Workflows:**
  1. `lead_create.json` - Lead creation flow
  2. `daily_report.json` - Morning report
  3. `followup_reminder.json` - Follow-up automation
  4. `task_scheduler.json` - Scheduled tasks

## 📊 Database Schema

```
users ─────┬──── memories
           │
           ├──── tasks
           │
           ├──── leads
           │
           └──── audit_logs
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
cd sai-rolotech-ai-hub
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start Services
```bash
# Terminal 1: Main API
python main.py

# Terminal 2: n8n (automation)
n8n start

# Terminal 3: OpenClaw (telegram)
openclaw start
```

### 3. Access
- **API:** http://localhost:8505
- **Dashboard:** http://localhost:8504
- **Hermes:** http://localhost:8502
- **n8n:** http://localhost:5678
- **OpenClaw:** http://localhost:18789

## 📱 Telegram Commands

| Command | Action |
|---------|--------|
| `/lead add Name 9876543210` | Add new lead |
| `/lead list` | List all leads |
| `/open chrome` | Open Chrome |
| `/task create [task]` | Schedule task |
| `/remind [message]` | Set reminder |
| `/report` | Daily report |
| `/stats` | Business stats |
| `/help` | Show help |

## 🔒 Security Model

```
User Message
     ↓
Policy Check
     ↓
┌────────────────────────────────┐
│     ALLOWED → Execute          │
│     BLOCKED → Reject           │
│     RISKY → Require Approval   │
└────────────────────────────────┘
```

## 💰 Cost Analysis

| Component | Cost |
|-----------|------|
| AI Models (Gemini, DeepSeek, Groq) | FREE |
| Claude (Heavy tasks) | ~$0.01/req |
| n8n, OpenClaw, Hermes | FREE |
| **Total** | **~$5/month** |

## 📁 Project Structure

```
sai-rolotech-ai-hub/
├── apps/
│   ├── hermes-agent/
│   │   └── core/
│   │       ├── hermes_core.py
│   │       └── master_router.py
│   ├── interpreter-service/
│   │   └── policies/
│   │       └── policy_engine.py
│   └── openclaw-bot/
│       └── command_parser.py
├── workflows/
│   └── n8n/
│       ├── lead_create.json
│       ├── daily_report.json
│       ├── followup_reminder.json
│       └── task_scheduler.json
├── shared/
│   ├── schemas/
│   │   └── database.py
│   └── utils/
│       └── logging.py
├── data/
│   ├── memory/
│   └── backups/
├── main.py
├── .env.example
└── README.md
```

## 🎯 Use Cases

### 1. Lead Management
```
User: /lead add Ramesh 9876543210 Facebook
Bot: ✅ Lead Created!
     Name: Ramesh
     Mobile: 9876543210
```

### 2. Desktop Action
```
User: /open chrome
Bot: 🌐 Opening Chrome...
     (Hermes routes to Interpreter)
     Chrome launches!
```

### 3. Scheduled Task
```
User: /task create Follow up Ramesh tomorrow 10am
Bot: ⏰ Task scheduled!
     (n8n automation triggers next day)
     Telegram reminder sent!
```

### 4. Daily Report
```
User: /report
Bot: 📊 Daily Report

New Leads: 5
Contacted: 12
Proposals: 3
Won: 1
```

## 🔗 Integration Points

### n8n Webhooks
- `POST /webhook/lead-create`
- `POST /webhook/followup-trigger`
- `POST /webhook/task-schedule`
- `POST /webhook/daily-report`

### Hermes API
- `POST /chat` - Chat with AI
- `GET /memory/{user_id}` - Get memories
- `POST /memory` - Save memory
- `POST /run` - Run code (with policy)

### CRM API
- `POST /crm/lead` - Create lead
- `GET /crm/leads` - List leads
- `GET /crm/lead/{id}` - Get lead
- `PUT /crm/lead/{id}` - Update lead
- `GET /crm/stats` - Get stats

## 🛡️ Policy Rules

### Allowed Commands
```python
python, node, git, curl, pip, npm
open, start, code, notepad
ls, dir, cat, type, echo
```

### Blocked Patterns
```python
rm -rf /          # Delete root
del /f /s         # Windows delete
format c:          # Format drive
curl | sh         # Pipe install
nc -e             # Netcat shell
```

### Risky (Require Approval)
```python
delete, remove, install
shutdown, registry
```

## 📈 Performance

| Metric | Value |
|--------|-------|
| Response Time | < 2s |
| Model Selection | < 100ms |
| Policy Check | < 10ms |
| Memory Lookup | < 50ms |

## 🎓 Learning Resources

- Agno: https://docs.agno.ai
- LangGraph: https://langchain-ai.github.io/langgraph/
- CrewAI: https://docs.crewai.com
- OpenClaw: https://docs.openclaw.ai
- n8n: https://docs.n8n.io

## 📞 Support

For issues or questions, check:
1. Logs: `./logs/ai-hub.log`
2. n8n executions
3. Hermes memory

---

**Built with ❤️ by SAI Rolotech**
