# Cloud Code Extension Project

## Project Overview

This is a monorepo containing multiple AI/automation projects:

| Folder | Purpose |
|--------|---------|
| `prompt-builder-vscode/` | VS Code extension for building structured prompts |
| `agno-multiagent/` | Multi-agent AI system |
| `sai-rolotech-ai-hub/` | Central AI hub with Hermes agent |
| `Agentfy/` | Social media agent collection |
| `design-tool/` | Design automation tool |

## Quick Start

### Prompt Builder VS Code Extension

```bash
cd prompt-builder-vscode
# Install to VS Code/Antigravity:
copy extension.js %USERPROFILE%/.vscode/extensions/prompt-builder-chat/
copy package.json %USERPROFILE%/.vscode/extensions/prompt-builder-chat/
```

**Features:**
- Chat box UI with user/bot messages
- Smart prompt generation with role detection
- ON/OFF toggle for chatbot
- Copy prompt button
- Supports Hindi/English input

**Skill Detection:**
- Education, Software Engineering, Debugging
- Code Review, Content Writing, DevOps
- Security, Data Analytics, Business Strategy

### Agno Multi-Agent

```bash
cd agno-multiagent
python main_menu.py
```

## Project Rules

1. **Small batches** - 5 steps, commit after each
2. **Test before claim** - Browser/App test required
3. **Memory update** - After every task
4. **Super rules first** - Read SUPER_RULES.md

## Important Commands

| Action | Command |
|--------|---------|
| Test extension | Copy to .vscode/extensions/ then reload |
| Check syntax | node --check extension.js |
| View in browser | Open Antigravity → Prompt Builder |
