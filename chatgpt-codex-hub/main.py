"""
ChatGPT + Codex Hub - Main Entry Point
SAI ROLO TECH
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from chatgpt_codex_hub import ChatGPTCodexLoop, TaskType
from scenarios.demo_scenario import DEMO_SCENARIOS, run_demo_scenario


def main():
    parser = argparse.ArgumentParser(
        description="ChatGPT + Codex Hub - Collaborative Coding Loop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py run "Create a calculator"
  python main.py demo calculator
  python main.py demo rest_api
  python main.py list
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a task")
    run_parser.add_argument("request", help="The task/request description")
    run_parser.add_argument("--type", "-t", choices=["generate", "fix", "refactor"],
                           default="generate", help="Task type")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run a demo scenario")
    demo_parser.add_argument("scenario", nargs="?", help="Demo scenario name")

    # List scenarios
    subparsers.add_parser("list", help="List available scenarios")

    # Interactive mode
    subparsers.add_parser("interactive", help="Start interactive mode",
                         description="Interactive loop mode")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print("\n\n" + "="*60)
        print("CHATGPT + CODEX HUB - Quick Start")
        print("="*60)
        print("\n1. List scenarios:")
        print("   python main.py list")
        print("\n2. Run a demo:")
        print("   python main.py demo calculator")
        print("\n3. Run a custom task:")
        print("   python main.py run 'Create a REST API'")
        return

    if args.command == "list":
        print("\nAvailable Scenarios:")
        print("=" * 50)
        for key, scenario in DEMO_SCENARIOS.items():
            print(f"\n{key}:")
            print(f"  Name: {scenario['name']}")
            print(f"  Type: {scenario['task_type']}")
            print(f"  {scenario['description']}")

    elif args.command == "demo":
        run_demo_scenario(args.scenario)

    elif args.command == "run":
        loop = ChatGPTCodexLoop()

        task_map = {
            "generate": TaskType.GENERATE_FEATURE,
            "fix": TaskType.FIX_BUG,
            "refactor": TaskType.REFACTOR
        }

        print(f"\n{'='*60}")
        print(f"CHATGPT + CODEX LOOP")
        print(f"{'='*60}")
        print(f"\nRequest: {args.request}")
        print(f"Type: {args.type}")

        result = loop.run(args.request, task_map[args.type])

        print(f"\n{'='*60}")
        print("RESULT")
        print(f"{'='*60}")
        print(f"Status: {result['status'].upper()}")
        print(f"Iterations: {result['iterations']}")

        if result.get('code'):
            print(f"\nGenerated code saved.")

    elif args.command == "interactive":
        print("\n" + "="*60)
        print("INTERACTIVE MODE - ChatGPT + Codex Loop")
        print("="*60)
        print("\nType your request and press Enter.")
        print("Type 'quit' or 'exit' to stop.")
        print("Type 'status' to see current session.")
        print("-" * 60)

        loop = ChatGPTCodexLoop()
        session_active = True

        while session_active:
            try:
                request = input("\n>>> ").strip()

                if request.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    session_active = False
                    continue

                if not request:
                    continue

                result = loop.run(request)
                print(f"\nResult: {result['status']}")
                print(f"Iterations: {result['iterations']}")

            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                session_active = False
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
