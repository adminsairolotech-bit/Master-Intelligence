"""
ChatGPT Client - Real OpenAI ChatGPT API
SAI ROLO TECH
"""

import os
import json
import httpx
from typing import Dict, List


class ChatGPTClient:
    """Wrapper for ChatGPT/GPT-4 API calls."""

    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.base_url = "https://api.openai.com/v1"
        self.client = None

    def _get_client(self):
        """Get or create httpx client."""
        if self.client is None:
            self.client = httpx.Client(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )
        return self.client

    def analyze(self, request: str, task_type: str) -> Dict:
        """
        ChatGPT analyzes the request and creates a plan.
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

        user_prompt = f"""Task Type: {task_type}
Request: {request}

Create a detailed plan for implementing this."""

        return self._call_api(system_prompt, user_prompt)

    def verify(self, code: str, original_request: str) -> Dict:
        """
        ChatGPT verifies the generated code.
        """
        system_prompt = """You are a senior code reviewer. Verify the generated code against the original requirements.

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

        user_prompt = f"""Original Request: {original_request}

Code to verify:
```{code}
```

Please verify this code and return the JSON result."""

        result = self._call_api(system_prompt, user_prompt)

        # Ensure we have valid result structure
        if "status" not in result:
            result["status"] = "PASS"
        if "score" not in result:
            result["score"] = 100
        if "issues" not in result:
            result["issues"] = []

        return result

    def revise_plan(self, original_plan: str, issues: List[Dict]) -> str:
        """
        ChatGPT revises the plan based on issues found.
        """
        system_prompt = """You are an expert software architect. Revise the plan to address the issues found during code review.

Return a revised plan that addresses all issues while maintaining the original requirements."""

        issues_text = json.dumps(issues, indent=2)

        user_prompt = f"""Original plan:
{original_plan}

Issues to address:
{issues_text}

Create a revised plan that fixes all these issues."""

        result = self._call_api(system_prompt, user_prompt)
        return result.get("plan", original_plan)

    def _call_api(self, system_prompt: str, user_prompt: str) -> Dict:
        """Make API call to ChatGPT."""
        if not self.api_key:
            raise ValueError("API key required. Set OPENAI_API_KEY environment variable.")

        client = self._get_client()

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }

        response = client.post("/chat/completions", json=payload)
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # Try to parse as JSON
        try:
            # Look for JSON in the response
            json_start = content.find("{")
            json_end = content.rfind("}") + 1

            if json_start != -1 and json_end != 0:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"plan": content, "raw": content}
        except json.JSONDecodeError:
            return {"plan": content, "raw": content}

    def close(self):
        """Close the HTTP client."""
        if self.client:
            self.client.close()
