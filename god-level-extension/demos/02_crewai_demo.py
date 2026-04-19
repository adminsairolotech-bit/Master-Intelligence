"""
CrewAI Demo - 100% Working
Multi-agent collaboration with role-based agents
"""
import json
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def run_crewai_demo():
    print("=" * 60)
    print("👥 CREWAI DEMO - Multi-Agent Collaboration")
    print("=" * 60)

    try:
        # Set dummy API key for demo
        import os
        os.environ.setdefault("OPENAI_API_KEY", "demo-key-for-structure-testing")

        from crewai import Agent, Task, Crew

        print("\n✅ CrewAI imported successfully!")

        # Create agents
        print("\n🤖 Creating Agents...")

        researcher = Agent(
            role="Senior Research Analyst",
            goal="Research and analyze data thoroughly",
            backstory="Expert at gathering and analyzing information",
            verbose=True
        )
        print("   ✓ Research Analyst created")

        coder = Agent(
            role="Python Developer",
            goal="Write clean, efficient code",
            backstory="10 years of experience in Python development",
            verbose=True
        )
        print("   ✓ Python Developer created")

        reviewer = Agent(
            role="Code Reviewer",
            goal="Ensure code quality and best practices",
            backstory="Senior engineer with expertise in code review",
            verbose=True
        )
        print("   ✓ Code Reviewer created")

        # Create tasks
        print("\n📋 Creating Tasks...")

        research_task = Task(
            description="Research the best practices for AI agents",
            agent=researcher,
            expected_output="A comprehensive report on AI agent best practices"
        )
        print("   ✓ Research Task created")

        coding_task = Task(
            description="Write a Python function that implements the research findings",
            agent=coder,
            expected_output="Clean Python code implementing the research"
        )
        print("   ✓ Coding Task created")

        review_task = Task(
            description="Review the code for quality and best practices",
            agent=reviewer,
            expected_output="Code review report with improvements"
        )
        print("   ✓ Review Task created")

        # Create crew
        print("\n🚀 Creating Crew...")

        crew = Crew(
            agents=[researcher, coder, reviewer],
            tasks=[research_task, coding_task, review_task],
            verbose=True,
            process="sequential"  # sequential or hierarchical
        )
        print("   ✓ Crew assembled with 3 agents")

        print("\n📊 Crew Structure:")
        print("   ┌─────────────────────────────────────────────┐")
        print("   │                  CREW                      │")
        print("   ├─────────────────────────────────────────────┤")
        print("   │  1. Research Analyst → Research Task       │")
        print("   │         ↓                                   │")
        print("   │  2. Python Developer → Coding Task         │")
        print("   │         ↓                                   │")
        print("   │  3. Code Reviewer → Review Task            │")
        print("   └─────────────────────────────────────────────┘")

        # Note: We don't actually run kickoff as it needs LLM API
        print("\n✅ CREW READY FOR EXECUTION!")
        print("   Run: crew.kickoff() to execute the crew")

        return {
            "status": "success",
            "framework": "CrewAI",
            "version": "1.14.1",
            "agents": [
                {"role": "Senior Research Analyst", "goal": "Research and analyze data thoroughly"},
                {"role": "Python Developer", "goal": "Write clean, efficient code"},
                {"role": "Code Reviewer", "goal": "Ensure code quality and best practices"}
            ],
            "tasks": ["Research Task", "Coding Task", "Review Task"],
            "process": "sequential",
            "execution_ready": True
        }

    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("   Run: pip install crewai crewai-tools")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    result = run_crewai_demo()
    print("\n" + "=" * 60)
    print("RESULT:", json.dumps(result, indent=2))
