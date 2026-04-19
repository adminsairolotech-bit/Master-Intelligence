"""
OpenClaw Training Module - Checklist Enforcement
Auto-runs on every session to ensure rule compliance

Run: python openclaw_train.py
"""
import os

TRAINING_SCRIPT = """
# OPENCLAW CHECKLIST TRAINING

## 1. MANDATORY WORKFLOW (Har Task Pe)

STEP 1: cat .claude/memory.json   (PEHLE!)
STEP 2: cat RULES.md              (DOOSRE!)
STEP 3: cat .claude/CHECKPOINT.md (TEEJSRE!)
STEP 4: DO TASK
STEP 5: TEST
STEP 6: COMMIT + UPDATE memory.json

## 2. CHECKPOINT VALIDATION SEQUENCE

Before starting ANY task:
1. Read .claude/memory.json -> Load API status, skills
2. Read RULES.md -> Load workflow rules
3. Read .claude/CHECKPOINT.md -> Load validation keys

If error: "Checkpoint not loaded" -> Run these 3 commands first!

## 3. QA LOOP (Dev -> QA -> Cycle)

DEV -> QA -> PASS? -> YES -> DONE
            NO
         RETRY (max 3)
            FAIL
         ESCALATE

## 4. SMALL BATCHES RULE

- 5 steps per batch
- Commit after each batch
- Test before claim
- Update memory.json after every task

## 5. API KEY FALLBACK CHAIN

Primary: OpenRouter/Flash 2.0 (FREE)
    -> Fail
Fallback 1: OpenRouter/Qwen (FREE)
    -> Fail
Fallback 2: OpenRouter/Haiku (cheap)
    -> Fail
Fallback 3: OpusMax/Claude-4.6 (expensive)

## 6. SELF-REPAIR TRIGGERS

| Trigger | Auto-Action |
|---------|-------------|
| Memory not loaded | Read .claude/memory.json |
| Rules not found | Read RULES.md |
| Checkpoint failed | Read .claude/CHECKPOINT.md |
| API key blocked | Rotate to next key |
| Build failed | Invoke build-error-resolver |

## 7. LIVE TEST RULE (MANDATORY)

Har code change ke baad YE KARNA MUST:

1. Code likho
2. Browser/App open karo
3. Test karo - koi error ya behavior dekho
4. Console/Network tab check karo
5. Sirf tab "Ho gaya" mat bol - PROOF dikhao!

## 8. GIT WORKFLOW

After every 5 steps:
git add . && git commit -m "checkpoint" && git push

## 9. SKILL INTEGRATION

Use Skill tool before ANY action:
- If skill applies (even 1% chance) -> MUST invoke skill
- Don't rationalize skipping skills

## 10. ATTENTION TO INCOMPLETE ITEMS

After completing main task:
- Check if any checklist items remain
- If incomplete items found -> mention them
- Don't leave things half-done

---

## TRAINING COMPLETE

OpenClaw will now:
[CHECK] Check memory.json before every task
[CHECK] Check RULES.md before every task
[CHECK] Check CHECKPOINT.md before every task
[CHECK] Use small batches (5 steps)
[CHECK] Test before claim (LIVE TEST)
[CHECK] Commit after every batch
[CHECK] Update memory.json after tasks
[CHECK] Rotate API keys on failure
[CHECK] Use Skill tool proactively
[CHECK] Report incomplete items
"""

def run_training():
    """Train OpenClaw to follow checklist rules."""
    print("=" * 60)
    print("OPENCLAW CHECKLIST TRAINING")
    print("=" * 60)
    print()

    # Display training
    print(TRAINING_SCRIPT)

    # Save training log
    log_file = os.path.expanduser("~/.openclaw/checklist_training.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Training completed at: {__import__('datetime').datetime.now()}\n")
        f.write(TRAINING_SCRIPT)

    print()
    print("=" * 60)
    print("[OK] Training complete!")
    print(f"[OK] Log saved to: {log_file}")
    print("=" * 60)

if __name__ == "__main__":
    run_training()