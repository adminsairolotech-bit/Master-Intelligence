"""
ChatGPT + Codex Loop - Main Orchestration
SAI ROLO TECH
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from models.chatgpt_client import ChatGPTClient
from models.codex_client import CodexClient
from validators.code_validator import CodeValidator
from workflows.generate_feature import GenerateFeatureWorkflow
from workflows.fix_bug import FixBugWorkflow
from workflows.refactor_code import RefactorCodeWorkflow


class TaskType(Enum):
    GENERATE_FEATURE = "generate_feature"
    FIX_BUG = "fix_bug"
    REFACTOR = "refactor"
    CUSTOM = "custom"


@dataclass
class SessionContext:
    """Tracks the state of a ChatGPT ↔ Codex session."""
    task_type: TaskType
    original_request: str
    chatgpt_plan: Optional[str] = None
    codex_code: Optional[str] = None
    verification_result: Optional[Dict] = None
    iteration: int = 0
    max_iterations: int = 3
    status: str = "pending"
    logs: List[Dict] = field(default_factory=list)

    def add_log(self, message: str, source: str = "system"):
        self.logs.append({
            "iteration": self.iteration,
            "source": source,
            "message": message
        })


class ChatGPTCodexLoop:
    """Orchestrates the ChatGPT ↔ Codex collaboration loop."""

    def __init__(self, chatgpt_api_key: str = None, openai_api_key: str = None):
        self.chatgpt = ChatGPTClient(api_key=chatgpt_api_key)
        self.codex = CodexClient(api_key=openai_api_key)
        self.validator = CodeValidator()

        # Workflows
        self.workflows = {
            TaskType.GENERATE_FEATURE: GenerateFeatureWorkflow(self),
            TaskType.FIX_BUG: FixBugWorkflow(self),
            TaskType.REFACTOR: RefactorCodeWorkflow(self),
        }

    def run(self, request: str, task_type: TaskType = TaskType.CUSTOM) -> Dict:
        """Run the complete loop."""
        context = SessionContext(
            task_type=task_type,
            original_request=request
        )

        context.add_log(f"Starting {task_type.value} task", "system")

        # Get ChatGPT's plan/analysis
        chatgpt_response = self.chatgpt.analyze(request, task_type)
        context.chatgpt_plan = chatgpt_response['plan']
        context.add_log("ChatGPT plan generated", "chatgpt")

        # Generate code with Codex
        codex_response = self.codex.generate(
            plan=context.chatgpt_plan,
            context=request
        )
        context.codex_code = codex_response['code']
        context.add_log(f"Codex generated {len(codex_response.get('files', []))} files", "codex")

        # Verify with ChatGPT
        verification = self.chatgpt.verify(
            code=context.codex_code,
            original_request=request
        )
        context.verification_result = verification
        context.add_log(f"Verification: {verification['status']}", "chatgpt")

        # Check result
        if verification['status'] == 'PASS':
            context.status = "completed"
            context.add_log("Task completed successfully!", "system")
        elif verification['status'] == 'REVISE' and context.iteration < context.max_iterations:
            context.iteration += 1
            context.add_log(f"Revision needed, iteration {context.iteration}", "system")
            # Continue loop with feedback
            return self._continue_loop(context, verification['issues'])
        else:
            context.status = "escalated"
            context.add_log("Max iterations reached, escalating", "system")

        return self._format_result(context)

    def _continue_loop(self, context: SessionContext, issues: List[Dict]) -> Dict:
        """Continue the loop with feedback from verification."""
        # Generate revised code with issues as context
        revised_plan = self.chatgpt.revise_plan(
            original_plan=context.chatgpt_plan,
            issues=issues
        )

        codex_response = self.codex.generate(
            plan=revised_plan,
            context=context.original_request,
            feedback=issues
        )

        # Re-verify
        verification = self.chatgpt.verify(
            code=codex_response['code'],
            original_request=context.original_request
        )

        context.iteration += 1
        context.codex_code = codex_response['code']
        context.verification_result = verification

        if verification['status'] == 'PASS':
            context.status = "completed"
        elif context.iteration >= context.max_iterations:
            context.status = "escalated"
        else:
            return self._continue_loop(context, verification.get('issues', []))

        return self._format_result(context)

    def _format_result(self, context: SessionContext) -> Dict:
        """Format the final result."""
        return {
            "status": context.status,
            "iterations": context.iteration,
            "code": context.codex_code,
            "verification": context.verification_result,
            "logs": context.logs
        }

    def run_scenario(self, scenario_name: str) -> Dict:
        """Run a predefined demo scenario."""
        from scenarios.demo_scenario import DEMO_SCENARIOS

        scenario = DEMO_SCENARIOS.get(scenario_name)
        if not scenario:
            return {"error": f"Scenario '{scenario_name}' not found"}

        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"{'='*60}")
        print(f"\n📋 Original Request:")
        print(scenario['request'])

        result = self.run(scenario['request'], TaskType(scenario['task_type']))

        print(f"\n{'='*60}")
        print(f"RESULT: {result['status'].upper()}")
        print(f"Iterations: {result['iterations']}")
        print(f"{'='*60}")

        return result
