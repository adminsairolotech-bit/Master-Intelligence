"""
ChatGPT Client - OpenAI ChatGPT API Wrapper
SAI ROLO TECH
"""

import os
from typing import Dict, List, Optional


class ChatGPTClient:
    """Wrapper for ChatGPT API calls."""

    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    def analyze(self, request: str, task_type: str) -> Dict:
        """
        ChatGPT analyzes the request and creates a plan.
        This is the 'Thinking' phase where ChatGPT understands the problem.
        """
        system_prompt = """You are an expert software architect. Analyze the user's request and create a detailed implementation plan.

For code generation tasks:
1. Break down the requirements into specific components
2. Identify dependencies and constraints
3. Define the data structures and interfaces
4. Outline the algorithm/logic flow
5. Specify verification criteria

Return your response as JSON with this structure:
{
    "plan": "Detailed implementation plan...",
    "components": ["list of files/components to create"],
    "dependencies": ["external dependencies if any"],
    "verification_criteria": ["how to verify the solution works"]
}"""

        # Simulated response for demo (replace with real API call)
        response = {
            "plan": self._generate_plan(request, task_type),
            "components": ["main.py", "models.py", "utils.py", "tests.py"],
            "dependencies": [],
            "verification_criteria": ["Unit tests pass", "Code compiles without errors"]
        }

        return response

    def verify(self, code: str, original_request: str) -> Dict:
        """
        ChatGPT verifies the generated code.
        Checks: logic correctness, security, style, completeness.
        """
        verification_prompt = """You are a senior code reviewer. Verify the generated code against the original requirements.

Check for:
1. Logic correctness - does it do what was asked?
2. Security issues - SQL injection, XSS, hardcoded secrets?
3. Error handling - are edge cases handled?
4. Code style - follows best practices?
5. Completeness - is anything missing?

Return your response as JSON:
{
    "status": "PASS | REVISE | FAIL",
    "score": 0-100,
    "issues": [
        {
            "severity": "HIGH | MEDIUM | LOW",
            "type": "security | logic | style | missing",
            "message": "Description of the issue",
            "line": 42,
            "suggestion": "How to fix it"
        }
    ],
    "verified_aspects": ["list of things that passed"],
    "summary": "Overall assessment"
}"""

        # Simulated verification for demo
        issues = []
        score = 85

        if "import" not in code and "def " not in code:
            issues.append({
                "severity": "HIGH",
                "type": "missing",
                "message": "No code content generated",
                "line": 1,
                "suggestion": "Generate actual code"
            })
            score = 0

        if len(code) < 100:
            issues.append({
                "severity": "MEDIUM",
                "type": "missing",
                "message": "Code seems incomplete",
                "line": 1,
                "suggestion": "Add more implementation"
            })
            score = 50

        status = "PASS" if score >= 70 else "REVISE"

        return {
            "status": status,
            "score": score,
            "issues": issues,
            "verified_aspects": ["Basic structure"] if score > 0 else [],
            "summary": f"Code verified with score {score}/100"
        }

    def revise_plan(self, original_plan: str, issues: List[Dict]) -> str:
        """
        ChatGPT revises the plan based on issues found during verification.
        """
        revision_prompt = f"""Revise the original plan to address these issues:

Issues found:
{json.dumps(issues, indent=2)}

Original plan:
{original_plan}

Create an improved plan that addresses all issues while maintaining the original requirements."""

        # Simulated revision
        revised = original_plan + "\n\n## Revision based on review:\n"
        for issue in issues:
            revised += f"- Fix: {issue.get('suggestion', 'Address issue')}\n"

        return revised

    def _generate_plan(self, request: str, task_type: str) -> str:
        """Generate implementation plan based on request."""
        # Simulated plans for demo
        plans = {
            "generate_feature": f"""## Implementation Plan for: {request}

### Step 1: Setup
- Create project structure
- Initialize necessary modules

### Step 2: Core Implementation
- Implement main functionality
- Add data models
- Create utility functions

### Step 3: Testing
- Write unit tests
- Verify functionality

### Step 4: Documentation
- Add docstrings
- Create README""",

            "fix_bug": f"""## Bug Fix Plan for: {request}

### Step 1: Reproduce
- Identify the bug scenario
- Create test case to reproduce

### Step 2: Analyze
- Find root cause
- Check related code

### Step 3: Fix
- Apply the fix
- Verify with tests

### Step 4: Verify
- Run full test suite
- Check for regressions""",

            "refactor": f"""## Refactoring Plan for: {request}

### Step 1: Assess
- Analyze current code structure
- Identify refactoring targets

### Step 2: Plan
- Design improved structure
- Plan migration path

### Step 3: Execute
- Refactor incrementally
- Maintain functionality

### Step 4: Verify
- Run tests after each change
- Ensure no regressions"""
        }

        return plans.get(task_type, f"## Plan for: {request}\n\nImplement the requested feature.")
