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

## Claude Code Slash Commands - USE THESE

| Command | Purpose | When |
|---------|---------|-------|
| **/ghost** | Human-like writing | Content, posts |
| **/artifacts** | Build apps/games in chat | Interactive demos |
| **/OODA** | Military decision framework | Strategic planning |
| **/L99** | Expert level mode | High-quality answers |
| **/godmode** | Comprehensive response | Deep analysis |
| **/human** | Natural writing | Content creation |
| **/EL5/EL10** | Simple explanations | Complex topics |
| **/deepthink** | Deep reasoning | Technical problems |

## Self-Repair System (OpenClaw Patterns)

Claude Code auto-repairs these:

| Trigger | Auto-Action |
|---------|-------------|
| Memory not loaded | Read .claude/memory.json |
| Rules not found | Read RULES.md |
| Checkpoint failed | Read .claude/CHECKPOINT.md |
| API key blocked | Rotate to next key |
| Build failed | Invoke build-error-resolver |

### Fallback Chain

```
Primary: OpenRouter/Flash 2.0 (FREE)
    ↓ Fail
Fallback 1: OpenRouter/Qwen (FREE)
    ↓ Fail
Fallback 2: OpenRouter/Haiku (cheap)
    ↓ Fail
Fallback 3: OpusMax/Claude-4.6 (expensive)
```

## QA Loop Pattern (Dev ↔ QA Cycle)

```
DEV → QA → PASS? → YES → DONE
            ↓ NO
         RETRY (max 3)
            ↓ FAIL
         ESCALATE
```

## Health Check Commands

```bash
# Check all systems
cat .claude/memory.json | grep -i "api\|status"
ls ~/.claude/skills/ | wc -l
curl -s http://localhost:18789 2>/dev/null
```

## Instagram Agents (NEW)

6 specialized agents:
| Agent | Purpose |
|-------|---------|
| ig-content | Content quality scoring (100-point) |
| ig-creative | Visual/format compliance |
| ig-engagement | Engagement pattern analysis |
| ig-growth | Follower dynamics |
| ig-competitor | Competitive benchmarking |
| ig-compliance | Quality gate, disclosure |

## Skill Upgrade System (CODEX 10 PATTERNS)

```bash
# Upgrade single skill
python ~/.claude/skills/scripts/upgrade_skill.py <skill-folder>

# Generate proactive triggers
python ~/.claude/skills/scripts/proactive_triggers_generator.py <domain>

# Generate output artifacts
python ~/.claude/skills/scripts/output_artifacts_generator.py <skill-type>
```

---

Last Updated: 2026-04-19
Version: 4.6 (OpenClaw Patterns)
