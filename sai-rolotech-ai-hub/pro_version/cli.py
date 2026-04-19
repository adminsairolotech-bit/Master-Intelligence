#!/usr/bin/env python
"""
PRO Version CLI
==============

Command-line interface for the PRO Engine
Usage: python cli.py
"""

import os
import sys
import json
from datetime import datetime

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pro_version.engine import run_engine, full_analysis, engine
from pro_version.memory import get_memory, get_context
from pro_version.automation import automation

def print_header():
    """Print ASCII header"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     🧠 LIFE COMMAND AI - PRO ENGINE v1.0              ║
    ║                                                          ║
    ║     Memory + AI Agents + Automation                     ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

def print_help():
    """Print help message"""
    print("""
    COMMANDS:
    ──────────────────────────────────────────────────────────
    /help          Show this help
    /exit          Exit the program
    /clear         Clear screen
    /memory        Show recent memory
    /context       Show current context
    /stats         Show system statistics
    /agents        Show available agents
    /full <msg>    Run full 5-agent analysis
    /quick <msg>   Run quick single-agent response
    /auto          Show automation queue & history

    EXAMPLES:
    ──────────────────────────────────────────────────────────
    > build a CRM for my business
    > analyze market for construction industry
    > plan a product launch for new profile
    > automate lead follow-up with n8n
    > design C-Channel roll forming system
    """)

def print_response(response, agents=None):
    """Format and print AI response"""
    print("\n" + "─" * 60)

    if agents:
        print("🤖 AGENTS: " + ", ".join([f"**{a}**" for a in agents]))

    print(response)
    print("─" * 60 + "\n")

def run_cli():
    """Main CLI loop"""
    print_header()
    print_help()

    while True:
        try:
            user_input = input("\n🎯 You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ['/exit', '/quit', '/q']:
                print("\n👋 Goodbye!\n")
                break

            elif user_input.lower() == '/help':
                print_help()
                continue

            elif user_input.lower() == '/clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                print_header()
                continue

            elif user_input.lower() == '/memory':
                print("\n🧠 Recent Memory:")
                memories = get_memory(limit=5)
                if memories:
                    for i, mem in enumerate(memories, 1):
                        print(f"  {i}. {mem['command'][:50]}...")
                else:
                    print("  No memories yet.")
                continue

            elif user_input.lower() == '/context':
                print("\n📝 Current Context:")
                context = get_context(limit=3)
                print(context if context else "  No context available.")
                continue

            elif user_input.lower() == '/stats':
                print("\n📊 System Statistics:")
                stats = engine.get_stats()
                print(json.dumps(stats, indent=2))
                continue

            elif user_input.lower() == '/agents':
                print("\n🤖 Available AI Agents:")
                agents = [
                    ("📋 Planner", "Strategic planning & task decomposition"),
                    ("💻 Technical", "Software engineering & code solutions"),
                    ("📊 Business", "Business analysis & strategy"),
                    ("⚡ Automation", "Workflow design & n8n integration"),
                    ("⚠️ Risk", "Risk assessment & mitigation"),
                ]
                for name, desc in agents:
                    print(f"  {name}: {desc}")
                continue

            elif user_input.lower().startswith('/full '):
                command = user_input[5:].strip()
                print("\n⚡ Running FULL 5-AGENT ANALYSIS...")
                result = full_analysis(command)
                print_response(result, result.agents_used if hasattr(result, 'agents_used') else ['all'])

            elif user_input.lower().startswith('/quick '):
                command = user_input[6:].strip()
                print("\n⚡ Running QUICK ANALYSIS...")
                result = run_engine(command, use_context=True, use_all_agents=False)
                print_response(result.final_response, result.agents_used)

            elif user_input.lower() == '/auto':
                print("\n⚡ Automation Status:")
                print(f"  Queue: {len(automation.action_queue)} pending")
                print(f"  History: {len(automation.execution_history)} executions")
                stats = automation.get_stats()
                print(f"  Success Rate: {stats['success_rate']}")
                continue

            else:
                # Default: Run through PRO engine
                print("\n⚡ Processing through PRO Engine...")
                result = run_engine(user_input, use_context=True, use_all_agents=False)
                print_response(result.final_response, result.agents_used)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    run_cli()
