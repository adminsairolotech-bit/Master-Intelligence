"""
Multi-Mode Config - SAI ROLO TECH
GitHub Hunting Mode - AI Collaboration
"""

# Unique Repos from your GitHub (adminsairolotech-bit)
UNIQUE_REPOS = {
    "everything-claude_code": {
        "name": "Everything Claude Code",
        "url": "https://github.com/adminsairolotech-bit/everything-claude-code",
        "description": "Agent harness optimization system - Skills, instincts, memory, security",
        "category": "agent-harness",
        "icon": "⚡",
        "features": ["Skills system", "Instincts", "Memory", "Security"]
    },
    "open_multi_agent": {
        "name": "Open Multi-Agent",
        "url": "https://github.com/adminsairolotech-bit/open-multi-agent",
        "description": "TypeScript multi-agent framework - one runTeam() call from goal to result",
        "category": "multi-agent",
        "icon": "🤖",
        "features": ["Task decomposition", "Parallel execution", "3 dependencies"]
    },
    "reposcope": {
        "name": "RepoScope",
        "url": "https://github.com/adminsairolotech-bit/reposcope-app",
        "description": "GitHub Repository Intelligence Platform with AI analysis",
        "category": "intelligence",
        "icon": "🔍",
        "features": ["Repo analysis", "Buddy AI", "Code synthesis"]
    },
    "claude_mem": {
        "name": "Claude Memory",
        "url": "https://github.com/adminsairolotech-bit/claude-mem",
        "description": "Claude Code plugin - captures everything Claude does during sessions",
        "category": "memory",
        "icon": "🧠",
        "features": ["Session capture", "Context compression", "AI injection"]
    },
    "computer_agent": {
        "name": "Computer Agent",
        "url": "https://github.com/adminsairolotech-bit/computer-agent",
        "description": "Desktop app to control computer with AI - terminal, browser, mouse",
        "category": "computer-use",
        "icon": "🖥️",
        "features": ["Terminal control", "Browser automation", "Mouse/Keyboard"]
    },
    "openclaw": {
        "name": "OpenClaw",
        "url": "https://github.com/adminsairolotech-bit/openclaw.ai-NEW-",
        "description": "Personal AI assistant - Any OS, Any Platform, The lobster way 🦞",
        "category": "ai-assistant",
        "icon": "🦞",
        "features": ["Cross-platform", "AI orchestration", "Gateway ready"]
    },
    "second_brain": {
        "name": "Second Brain Skills",
        "url": "https://github.com/adminsairolotech-bit/second-brain-skills",
        "description": "Claude Skills to turn Claude Code into a Second Brain",
        "category": "skills",
        "icon": "🧬",
        "features": ["Knowledge management", "Context retention", "Learning"]
    },
    "system_prompts": {
        "name": "System Prompts Leaks",
        "url": "https://github.com/adminsairolotech-bit/multi-ai-system_prompts_leaks",
        "description": "Extracted prompts from ChatGPT, Claude, Gemini, Grok, Perplexity",
        "category": "prompts",
        "icon": "📜",
        "features": ["GPT-5.4/5.3", "Claude Opus 4.6", "Gemini 3.1", "Grok 4.2"]
    },
    "oh_my_codex": {
        "name": "Oh My Codex",
        "url": "https://github.com/adminsairolotech-bit/oh-my-codex",
        "description": "OmX - Add hooks, agent teams, HUDs to Codex",
        "category": "codex-ext",
        "icon": "📦",
        "features": ["Hooks system", "Agent teams", "HUD interface"]
    },
    "buddy_auto_mode": {
        "name": "Buddy Auto Mode",
        "url": "https://github.com/adminsairolotech-bit/BUDDY-AUTO-MODE",
        "description": "Secure OpenClaw-style assistant with auto mode",
        "category": "automation",
        "icon": "🎯",
        "features": ["Auto mode", "Security focused", "OpenClaw compatible"]
    },
    "pro_ai": {
        "name": "PRO AI Engine",
        "url": "https://github.com/adminsairolotech-bit/sai-rolotech-pro-ai",
        "description": "5 specialized agents for professional AI workflows",
        "category": "engine",
        "icon": "🚀",
        "features": ["5 Agents", "Specialized tasks", "Production ready"]
    },
    "autocad_bridge": {
        "name": "AutoCAD Bridge",
        "url": "https://github.com/adminsairolotech-bit/sai-rolotech-autocad",
        "description": "SCR Generator for roll-forming machines",
        "category": "cad",
        "icon": "🏗️",
        "features": ["SCR generation", "Roll forming", "Dynamo integration"]
    }
}


# Mode Categories
MODES = {
    "hunting": {
        "name": "🎯 Hunting Mode",
        "description": "Search and analyze GitHub repos with AI",
        "icon": "🔍",
        "color": "#9333ea",
        "repos": ["reposcope", "system_prompts", "everything_claude_code"]
    },
    "multi_agent": {
        "name": "🤖 Multi-Agent",
        "description": "Run multiple AI agents in parallel",
        "icon": "🔄",
        "color": "#10a37f",
        "repos": ["open_multi_agent", "pro_ai", "claude_mem"]
    },
    "computer_use": {
        "name": "🖥️ Computer Use",
        "description": "Control computer with AI",
        "icon": "🎮",
        "color": "#f7df1e",
        "repos": ["computer_agent", "openclaw", "buddy_auto_mode"]
    },
    "knowledge": {
        "name": "🧠 Knowledge",
        "description": "Build and query knowledge bases",
        "icon": "📚",
        "color": "#3b82f6",
        "repos": ["second_brain", "system_prompts", "claude_mem"]
    },
    "coding": {
        "name": "💻 Coding",
        "description": "Code generation and analysis",
        "icon": "⚡",
        "color": "#ef4444",
        "repos": ["everything_claude_code", "oh_my_codex", "open_multi_agent"]
    },
    "automation": {
        "name": "⚙️ Automation",
        "description": "Automate workflows and tasks",
        "icon": "🔧",
        "color": "#f97316",
        "repos": ["buddy_auto_mode", "reposcope", "openclaw"]
    }
}


def get_mode_repos(mode_name: str) -> list:
    """Get repos for a specific mode."""
    mode = MODES.get(mode_name, {})
    repo_keys = mode.get("repos", [])
    return [UNIQUE_REPOS.get(key) for key in repo_keys if key in UNIQUE_REPOS]


def search_repos(query: str) -> list:
    """Search repos by query."""
    results = []
    query_lower = query.lower()

    for key, repo in UNIQUE_REPOS.items():
        if (query_lower in repo["name"].lower() or
            query_lower in repo["description"].lower() or
            query_lower in repo["category"].lower() or
            any(query_lower in feature.lower() for feature in repo.get("features", []))):
            results.append(repo)

    return results
