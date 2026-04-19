# SAI ROLO TECH - OpenRouter Bridge

Dedicated OpenRouter AI Bridge with **FREE → PAID** model priority.

## Quick Start

```bash
cd sai-rolotech-openrouter

# Copy env template
cp openrouter.env.example openrouter.env

# Add your OpenRouter API key to openrouter.env
# Get from: https://openrouter.ai/keys

# Run CLI
python openrouter_bridge.py "Hello AI" --model flash
```

## Model Priority

| Task Type | Model | Cost |
|----------|-------|------|
| Light (<100 words) | Flash 2.0 | FREE |
| Heavy (>100 words) | Opus 4.7 | PAID |

## Usage

```bash
# Light task (FREE - Flash 2.0)
python openrouter_bridge.py "Summarize this text..."

# Heavy task (PAID - Opus 4.7)
python openrouter_bridge.py "Write a complex Python script..." --model opus

# Auto-select based on message length
python openrouter_bridge.py "Your message here..."
```

## Available Models

| Type | Model | Use Case |
|------|-------|----------|
| `flash` | google/gemini-2.0-flash-exp | Fast, FREE |
| `haiku` | anthropic/claude-3.5-haiku | Fast, paid |
| `sonnet` | anthropic/claude-sonnet-4.6 | Balanced |
| `opus` | anthropic/opus-4.7 | Most capable, PAID |

## Python API

```python
from openrouter_bridge import OpenRouterBridge

bridge = OpenRouterBridge()

# Light task - FREE
result = bridge.flash("Quick question?")

# Heavy task - PAID
result = bridge.opus("Complex coding task...")

# Auto-select
result = bridge.auto("Your message...")
```

## Files

| File | Purpose |
|------|---------|
| `openrouter_bridge.py` | Main bridge code |
| `openrouter.env.example` | Env template |
| `openrouter.env` | Your API keys (NOT committed) |
