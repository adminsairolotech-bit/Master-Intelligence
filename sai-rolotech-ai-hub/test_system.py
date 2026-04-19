"""
Test SAI Rolotech AI Hub
"""
import os
import sys

# Fix encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

print("=" * 60)
print("SAI ROLOTECH AI HUB - SYSTEM TEST")
print("=" * 60)

# 1. Test Database
print("\n[1] Database Models...")
try:
    from shared.schemas.database import init_db, User, Lead, Memory, Task
    print("    OK: All models imported")
    db = init_db()
    print("    OK: Database initialized")
except Exception as e:
    print(f"    FAIL: {e}")

# 2. Test Policy Engine
print("\n[2] Policy Engine...")
try:
    from apps.interpreter_service.policies.policy_engine import policy

    tests = [
        ("open chrome", True),
        ("python script.py", True),
        ("ls -la", True),
        ("rm -rf /", False),
        ("del /f /s", False),
        ("format c:", False),
    ]

    for cmd, expected_safe in tests:
        safe, reason = policy.check_command(cmd)
        status = "OK" if safe == expected_safe else "FAIL"
        print(f"    {status}: '{cmd}' => safe={safe} (expected={expected_safe})")

except Exception as e:
    print(f"    FAIL: {e}")

# 3. Test Hermes Router
print("\n[3] Hermes Master Router...")
try:
    from apps.hermes_agent.core.master_router import MasterRouter
    router = MasterRouter()

    tests = [
        ("add lead Ramesh 9876543210", "crm"),
        ("open chrome", "interpreter"),
        ("run python script", "interpreter"),
        ("schedule reminder tomorrow", "n8n"),
        ("daily report", "n8n"),
        ("hello how are you", "hermes"),
        ("what is my name", "hermes"),
    ]

    for msg, expected_tool in tests:
        result = router.detect_intent(msg)
        status = "OK" if result["tool"] == expected_tool else "FAIL"
        print(f"    {status}: '{msg}' => tool={result['tool']} (expected={expected_tool})")

except Exception as e:
    print(f"    FAIL: {e}")

# 4. Test Model Selection
print("\n[4] Model Selection...")
try:
    tests = [
        ("write python code", "deepseek"),
        ("fix this bug", "deepseek"),
        ("business analysis", "claude"),
        ("market research report", "claude"),
        ("quick answer", "groq"),
        ("urgent reply", "groq"),
        ("explain something", "gemini"),
    ]

    for msg, expected_model in tests:
        model = router.select_model(msg)
        status = "OK" if model == expected_model else "NOTE"
        print(f"    {status}: '{msg}' => model={model}")

except Exception as e:
    print(f"    FAIL: {e}")

# 5. Test Approval Check
print("\n[5] Approval Check (Risky Actions)...")
try:
    tests = [
        ("delete all files", True),
        ("format drive c", True),
        ("install new software", True),
        ("open notepad", False),
        ("show my leads", False),
    ]

    for msg, expect_approval in tests:
        needs = router.require_approval(msg)
        status = "OK" if needs == expect_approval else "FAIL"
        print(f"    {status}: '{msg}' => needs_approval={needs} (expected={expect_approval})")

except Exception as e:
    print(f"    FAIL: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
