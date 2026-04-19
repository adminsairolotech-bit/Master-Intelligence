"""Test script - Run agents directly"""
import asyncio
from agent_system import coder, analyst

async def test():
    print("🧪 Testing AI Agents...\n")

    # Test Coder
    print("1️⃣ Testing Coder Agent...")
    code_response = await coder.arun("Write a Python function to calculate fibonacci numbers")
    print(f"Coder: {code_response}\n")

    # Test Analyst
    print("2️⃣ Testing Analyst Agent...")
    analysis = await analyst.arun("What are the top 3 AI trends in 2026?")
    print(f"Analyst: {analysis}\n")

    print("✅ All agents working!")

if __name__ == "__main__":
    asyncio.run(test())
