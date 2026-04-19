"""
Codex Client - Real OpenAI Codex/GPT-4 API
SAI ROLO TECH
"""

import os
import json
import httpx
from typing import Dict, List


class CodexClient:
    """Wrapper for OpenAI Codex/GPT-4 API calls for code generation."""

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
                timeout=120.0
            )
        return self.client

    def generate(self, plan: str, context: str, feedback: List[Dict] = None) -> Dict:
        """
        Codex generates code based on the plan from ChatGPT.
        """
        system_prompt = """You are an expert code generator. Generate clean, production-ready code based on the implementation plan.

Rules:
1. Generate complete, working code
2. Follow best practices for the language
3. Include error handling
4. Add docstrings to functions
5. No hardcoded secrets - use environment variables
6. Use type hints where applicable

Return your response as JSON:
{
    "code": "the complete generated code",
    "files": ["list of file names created"],
    "language": "programming language used",
    "explanation": "brief explanation of the code"
}"""

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

Generate the complete implementation code. Return valid JSON with the code."""

        return self._call_api(system_prompt, user_prompt)

    def _call_api(self, system_prompt: str, user_prompt: str) -> Dict:
        """Make API call to Codex/GPT-4."""
        if not self.api_key:
            raise ValueError("API key required. Set OPENAI_API_KEY environment variable.")

        client = self._get_client()

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,  # Lower temp for more consistent code
            "max_tokens": 8000
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
                return {
                    "code": content,
                    "files": ["generated_code.py"],
                    "language": "python",
                    "explanation": "Code generated"
                }
        except json.JSONDecodeError:
            return {
                "code": content,
                "files": ["generated_code.py"],
                "language": "python",
                "explanation": "Code generated"
            }

    def close(self):
        """Close the HTTP client."""
        if self.client:
            self.client.close()
