# Cloud AI Bridge

**Purpose:** Multi-provider AI (Gemini, Groq, NVIDIA, OpenRouter)

**Config:** `cloud.env`

## Quick Start

```bash
python cloud-ai/cloud_bridge.py --cli
```

## Configuration (cloud.env)

| Variable | Provider | Status |
|----------|----------|--------|
| `GROQ_API_KEY` | Groq (Llama 3.3) | Get from groq.com |
| `NVIDIA_API_KEY` | NVIDIA (Nemotron) | Get from build.nvidia.com |
| `GEMINI_API_KEY` | Gemini (FREE) | Get from aistudio.google.com |
| `OPENROUTER_API_KEY` | Alternative Claude | Get from openrouter.ai |

## Commands

- `--cli` - Interactive CLI mode
- `--provider groq` - Force Groq
- `--provider gemini` - Force Gemini

## DO NOT MIX

This folder uses **Cloud AI** config. DO NOT mix with `openclaw-bridge/` folder.
