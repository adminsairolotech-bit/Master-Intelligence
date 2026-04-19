# Universal OpenClaw Bridge

Connect any app to OpenClaw + Claude Opus

## Quick Start

```bash
cd "c:\Users\Sai Rolotech\New folder\cloud-code-extension"

# Interactive CLI
python universal_bridge.py --cli

# Direct query
python universal_bridge.py "Hello!"

# Check status
python universal_bridge.py --status

# Test all
python universal_bridge.py --test
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Universal Bridge                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │              AI BRAIN                        │   │
│  │           Claude Opus 4.6                    │   │
│  │         (via OpenRouter)                     │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │              CONNECTORS                       │   │
│  ├──────────────────────────────────────────────┤   │
│  │  ✅ OpenClaw    - Browser/App automation   │   │
│  │  ✅ Claude Opus - AI responses              │   │
│  │  ⚠️  Telegram   - Messaging (setup needed)   │   │
│  │  ⚠️  WhatsApp  - Messaging (setup needed)   │   │
│  │  ⚠️  Slack     - Team communication          │   │
│  │  ⚠️  Discord   - Community chat              │   │
│  │  ⚠️  Webhook   - Custom integrations         │   │
│  │  ⚠️  API       - HTTP server                │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Connectors Status

| Connector | Status | Setup Required |
|-----------|--------|---------------|
| **Claude Opus 4.6** | ✅ Connected | OPENROUTER_API_KEY |
| **OpenClaw** | ✅ Connected | Running on port 18789 |
| **Telegram** | ⚠️ Ready | TELEGRAM_BOT_TOKEN |
| **WhatsApp** | ⚠️ Ready | ULTRAMSG_TOKEN, ULTRAMSG_INSTANCE |
| **Slack** | ⚠️ Ready | SLACK_BOT_TOKEN |
| **Discord** | ⚠️ Ready | DISCORD_WEBHOOK_URL |
| **Webhook** | ⚠️ Ready | BRIDGE_WEBHOOK_URL |
| **API** | ⚠️ Ready | None |

## Environment Variables

Create `.env` file or set in system:

```bash
# Required for AI
OPENROUTER_API_KEY=sk-or-v1-xxx

# OpenClaw (auto-detected)
OPENCLAW_URL=http://localhost:18789
OPENCLAW_TOKEN=your-token

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# WhatsApp (Ultramsg)
ULTRAMSG_TOKEN=your-token
ULTRAMSG_INSTANCE=your-instance-id
WHATSAPP_PHONE=+1234567890

# Slack
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL=#general

# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx

# Generic Webhook
BRIDGE_WEBHOOK_URL=https://your-webhook-endpoint.com
```

## Smart Routing

Messages are automatically routed:

| Message Type | Routes To |
|--------------|-----------|
| Code/Automation | Claude Opus + OpenClaw |
| General queries | Claude Opus only |
| Broadcast | All connected apps |

## CLI Commands

```
/status              - Show bridge status
/send <app> <msg>   - Send to specific app
/broadcast <msg>    - Send to all apps
/ai <prompt>         - Query Claude Opus
/route <prompt>      - Smart route
/list                - List all connectors
/quit                - Exit CLI
```

## Python API

```python
from universal_bridge import UniversalBridge

bridge = UniversalBridge()

# Status
print(bridge.status())

# Query AI
result = bridge.ai.chat("Hello!")

# Smart route
result = bridge.route("Write Python code")

# Send to all
bridge.send_to_all("Hello from Universal Bridge!")

# Add custom connector
class MyConnector(Connector):
    name = "myapp"
    def send(self, message): return {"success": True}
    def receive(self): return None
    def is_connected(self): return True

bridge.add_connector("myapp", MyConnector())
```

## Files

| File | Description |
|------|-------------|
| `universal_bridge.py` | Main bridge module |
| `claude_bridge.py` | Simple Claude-only bridge |
| `bridge.cmd` | Windows launcher |
| `bridge` | Unix launcher |
| `openclaw_bridge.env` | Configuration template |

## Start OpenClaw Gateway

```powershell
cd 'C:\Users\Sai Rolotech\AppData\Roaming\npm'
.\openclaw.cmd gateway --bind loopback
```

## Available Models

Default: `anthropic/claude-opus-4.6`

Other options via OpenRouter:
- `anthropic/claude-sonnet-4.6`
- `openai/gpt-4o`
- `google/gemini-pro`

Change in code:
```python
bridge.ai.set_model("anthropic/claude-sonnet-4.6")
```
