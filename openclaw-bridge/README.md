# OpenClaw Bridge

**Purpose:** Connect to OpenClaw Gateway via Claude Opus (OpenRouter)

**Config:** `openclaw.env`

## Quick Start

```bash
python openclaw-bridge/openclaw_bridge.py --cli
```

## Configuration (openclaw.env)

| Variable | Description |
|----------|-------------|
| `OPENCLAW_URL` | Gateway URL (default: http://localhost:18789) |
| `OPENCLAW_TOKEN` | Gateway auth token |
| `OPENROUTER_API_KEY` | OpenRouter key for Claude Opus |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |

## Commands

- `--cli` - Interactive CLI mode
- `--telegram` - Telegram bot mode
- `--webhook` - Webhook server mode

## DO NOT MIX

This folder uses **OpenClaw** config. DO NOT mix with `cloud-ai/` folder.
