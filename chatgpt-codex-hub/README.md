# ChatGPT + Codex Hub - SAI ROLO TECH

## Concept

A collaborative coding loop where **ChatGPT** and **Codex** work together:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHATGPT ↔ CODEX LOOP                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐                                               │
│   │  CHATGPT    │  ← Receives prompt from user                 │
│   │  (Thinking) │    or system request                         │
│   └──────┬──────┘                                               │
│          │                                                      │
│          ▼  "Here's the plan..."                               │
│   ┌─────────────┐                                               │
│   │   CODEX     │  ← Receives plan from ChatGPT                 │
│   │  (Coding)   │    generates code                            │
│   └──────┬──────┘                                               │
│          │                                                      │
│          ▼  "Here's the code..."                               │
│   ┌─────────────┐                                               │
│   │  CHATGPT    │  ← Verifies code                             │
│   │ (Verifier)  │    checks logic, security, style            │
│   └──────┬──────┘                                               │
│          │                                                      │
│    ┌─────┴─────┐                                                │
│    ▼           ▼                                                │
│  PASS         FAIL                                               │
│    │           │                                                │
│    ▼           ▼                                                │
│  DONE    ← Send back to Codex for revision                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## System Architecture

```
chatgpt-codex-hub/
├── chatgpt_codex_loop.py    # Main orchestration
├── models/
│   ├── chatgpt_client.py    # ChatGPT API wrapper
│   └── codex_client.py      # Codex API wrapper
├── validators/
│   ├── code_validator.py    # Code quality checks
│   ├── security_checker.py  # Security analysis
│   └── style_checker.py     # Code style checks
├── workflows/
│   ├── generate_feature.py  # Feature generation workflow
│   ├── fix_bug.py          # Bug fix workflow
│   └── refactor_code.py     # Refactoring workflow
├── scenarios/
│   ├── demo_scenario.py     # Working demo
│   └── test_scenario.py    # Test scenarios
└── logs/
    └── session_logs.py     # Session tracking
```

## Workflows

### 1. Generate Feature
```
User → ChatGPT (spec) → Codex (code) → ChatGPT (verify) → [PASS/REVISE]
```

### 2. Fix Bug
```
User → ChatGPT (bug) → Codex (fix) → ChatGPT (test) → [PASS/REVISE]
```

### 3. Refactor Code
```
User → ChatGPT (goals) → Codex (refactor) → ChatGPT (compare) → [PASS/REVISE]
```

## Communication Protocol

### ChatGPT → Codex Message Format
```json
{
  "task": "generate_feature",
  "context": {
    "language": "python",
    "framework": "fastapi",
    "requirements": ["REST API", "JWT auth"]
  },
  "specification": "Build a user authentication system...",
  "constraints": ["Use Python 3.8+", "No external DB"],
  "verification_criteria": ["Unit tests pass", "No security issues"]
}
```

### Codex → ChatGPT Response Format
```json
{
  "code": "import FastAPI...",
  "files_created": ["auth.py", "models.py"],
  "tests": "test_auth.py",
  "documentation": "README updated"
}
```

### ChatGPT → Verification Result
```json
{
  "status": "PASS | REVISE | FAIL",
  "issues": [
    {
      "severity": "HIGH | MEDIUM | LOW",
      "type": "security | logic | style",
      "message": "SQL injection vulnerability in line 42",
      "line": 42,
      "suggestion": "Use parameterized query"
    }
  ],
  "verified_aspects": ["Functionality", "Security"],
  "score": 85
}
```

## Max Retries: 3
After 3 failures → Escalate to human review

---

**Created:** 2026-04-19
**Version:** 0.1.0
