"""
Demo Scenarios - Working demonstrations of ChatGPT ↔ Codex loop
SAI ROLO TECH
"""

DEMO_SCENARIOS = {
    "calculator": {
        "name": "Generate Calculator",
        "request": "Create a Python calculator with add, subtract, multiply, divide functions",
        "task_type": "generate_feature",
        "description": "Simple demo showing the full loop: ChatGPT plans → Codex codes → ChatGPT verifies"
    },

    "rest_api": {
        "name": "Generate REST API",
        "request": "Create a FastAPI REST API with CRUD operations for items",
        "task_type": "generate_feature",
        "description": "More complex demo with real-world API structure"
    },

    "bug_fix": {
        "name": "Fix Bug Scenario",
        "request": "Fix a bug where the login function allows any password",
        "task_type": "fix_bug",
        "description": "Shows the fix verification loop"
    },

    "refactor": {
        "name": "Refactor Legacy Code",
        "request": "Refactor this code to use modern Python patterns and type hints",
        "task_type": "refactor",
        "description": "Shows the comparison and verification loop"
    }
}


def run_demo_scenario(scenario_name: str = None):
    """
    Run a demo scenario showing the ChatGPT ↔ Codex loop in action.

    This demonstrates:
    1. How ChatGPT analyzes the request and creates a plan
    2. How Codex generates code based on the plan
    3. How ChatGPT verifies the code
    4. The revision loop if verification fails
    """
    if scenario_name is None:
        print("\nAvailable Demo Scenarios:")
        print("=" * 50)
        for key, scenario in DEMO_SCENARIOS.items():
            print(f"\n{key}: {scenario['name']}")
            print(f"  {scenario['description']}")
        print("\n" + "=" * 50)
        print("\nRun with: run_demo_scenario('calculator')")
        return

    scenario = DEMO_SCENARIOS.get(scenario_name)
    if not scenario:
        print(f"Scenario '{scenario_name}' not found!")
        print("Available: " + ", ".join(DEMO_SCENARIOS.keys()))
        return

    print(f"\n{'#'*60}")
    print(f"# DEMO: {scenario['name']}")
    print(f"{'#'*60}")
    print(f"\n📋 Original Request:")
    print(f"   {scenario['request']}")
    print(f"\n📝 Task Type: {scenario['task_type']}")

    # Import here to avoid circular import
    from chatgpt_codex_loop import ChatGPTCodexLoop, TaskType

    # Create the loop (using demo mode - no real API keys needed)
    loop = ChatGPTCodexLoop()

    # Run the workflow
    result = loop.run(
        request=scenario['request'],
        task_type=TaskType(scenario['task_type'])
    )

    # Display results
    print(f"\n{'='*60}")
    print("RESULT")
    print(f"{'='*60}")
    print(f"\nStatus: {result['status'].upper()}")
    print(f"Iterations: {result['iterations']}")
    print(f"Score: {result.get('verification', {}).get('score', 'N/A')}/100")

    if result.get('verification', {}).get('issues'):
        print(f"\nIssues found: {len(result['verification']['issues'])}")
        for issue in result['verification']['issues']:
            print(f"  [{issue['severity']}] {issue['message']}")

    print(f"\n{'='*60}")
    print("GENERATED CODE PREVIEW")
    print(f"{'='*60}")
    code = result.get('code', '')
    if code:
        # Show first 50 lines
        lines = code.split('\n')[:50]
        for line in lines:
            print(line)
        if len(code.split('\n')) > 50:
            print(f"\n... ({len(code.split('\n')) - 50} more lines)")
    else:
        print("No code generated")

    return result


if __name__ == "__main__":
    # List available scenarios
    run_demo_scenario()
