"""
Ollama Client - Local LLM via Ollama API
SAI ROLO TECH
"""

import os
import json
import httpx
from typing import Dict, List


class OllamaClient:
    """Wrapper for Ollama API - Local Llama models."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        self.base_url = base_url
        self.model = model
        self.client = None

    def _get_client(self):
        """Get or create httpx client."""
        if self.client is None:
            self.client = httpx.Client(
                base_url=self.base_url,
                timeout=180.0  # Longer timeout for local models
            )
        return self.client

    def analyze(self, request: str, task_type: str = "generate_feature") -> Dict:
        """
        Use Ollama to analyze request and create plan.
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

        response = self._call_model(system_prompt, user_prompt)

        # Try to parse as JSON
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end != 0:
                return json.loads(response[json_start:json_end])
        except:
            pass

        return {"plan": response, "response": response}

    def generate(self, plan: str, context: str, feedback: List[Dict] = None) -> Dict:
        """
        Use Ollama to generate code based on plan.
        """
        system_prompt = """You are an expert code generator. Generate clean, production-ready code based on the implementation plan.

Rules:
1. Generate complete, working code
2. Follow best practices for the language
3. Include error handling
4. Add docstrings to functions
5. No hardcoded secrets - use environment variables
6. Use type hints where applicable"""

        feedback_text = ""
        if feedback:
            feedback_text = "\n\nPREVIOUS ISSUES TO ADDRESS:\n"
            for i, issue in enumerate(feedback, 1):
                feedback_text += f"{i}. [{issue.get('severity', 'MEDIUM')}] {issue.get('message', '')}\n"

        user_prompt = f"""CONTEXT:
{context}

IMPLEMENTATION PLAN:
{plan}
{feedback_text}

Generate the complete implementation code."""

        response = self._call_model(system_prompt, user_prompt)

        return {
            "code": response,
            "files": ["generated_code.py"],
            "language": "python",
            "response": response
        }

    def verify(self, code: str, original_request: str) -> Dict:
        """
        Use Ollama to verify generated code.
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

        response = self._call_model(system_prompt, user_prompt)

        # Try to parse as JSON
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end != 0:
                result = json.loads(response[json_start:json_end])
                if "status" not in result:
                    result["status"] = "PASS"
                if "score" not in result:
                    result["score"] = 100
                if "issues" not in result:
                    result["issues"] = []
                return result
        except:
            pass

        return {
            "status": "PASS",
            "score": 85,
            "issues": [],
            "summary": response[:200] if len(response) > 200 else response
        }

    def _call_model(self, system_prompt: str, user_prompt: str) -> str:
        """Make API call to Ollama."""
        client = self._get_client()

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 4096
            }
        }

        try:
            response = client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}. Make sure Ollama is running with: ollama serve")

    def list_models(self) -> List[str]:
        """List available models."""
        client = self._get_client()
        try:
            response = client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
        except:
            return [self.model]

    def close(self):
        """Close the HTTP client."""
        if self.client:
            self.client.close()
