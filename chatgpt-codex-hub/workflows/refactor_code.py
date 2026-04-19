"""
Refactor Code Workflow
SAI ROLO TECH
"""

from __future__ import annotations
from typing import Dict


class RefactorCodeWorkflow:
    """Workflow for refactoring code."""

    def __init__(self, loop: ChatGPTCodexLoop):
        self.loop = loop

    def execute(self, refactor_request: str) -> Dict:
        """Execute the refactoring workflow."""
        context = SessionContext(
            task_type="refactor",
            original_request=refactor_request
        )

        # Step 1: ChatGPT assesses the code
        print("\n📊 [STEP 1] ChatGPT assessing code...")
        chatgpt_response = self.loop.chatgpt.analyze(refactor_request, "refactor")
        context.chatgpt_plan = chatgpt_response['plan']
        print(f"   ✅ Assessment complete")

        # Step 2: Codex refactors
        print("\n🔄 [STEP 2] Codex refactoring...")
        codex_response = self.loop.codex.generate(
            plan=context.chatgpt_plan,
            context=refactor_request
        )
        context.codex_code = codex_response['code']
        print(f"   ✅ Refactoring complete")

        # Step 3: ChatGPT compares old vs new
        print("\n⚖️ [STEP 3] ChatGPT comparing...")
        verification = self.loop.chatgpt.verify(
            code=context.codex_code,
            original_request=refactor_request
        )
        context.verification_result = verification
        print(f"   ✅ Comparison: {verification['status']}")

        if verification['status'] == 'PASS':
            print("\n✅ Refactoring complete!")
            context.status = "completed"
        elif context.iteration < context.max_iterations:
            return self._handle_revision(context, verification)
        else:
            print("\n⚠️ Max iterations reached, escalating...")
            context.status = "escalated"

        return self.loop._format_result(context)

    def _handle_revision(self, context, verification) -> Dict:
        """Handle revision for refactoring."""
        while context.iteration < context.max_iterations:
            context.iteration += 1
            print(f"\n🔄 [ITERATION {context.iteration}] Refining...")

            revised_plan = self.loop.chatgpt.revise_plan(
                original_plan=context.chatgpt_plan,
                issues=verification['issues']
            )
            context.chatgpt_plan = revised_plan

            codex_response = self.loop.codex.generate(
                plan=revised_plan,
                context=context.original_request,
                feedback=verification['issues']
            )
            context.codex_code = codex_response['code']

            verification = self.loop.chatgpt.verify(
                code=context.codex_code,
                original_request=context.original_request
            )
            context.verification_result = verification

            if verification['status'] == 'PASS':
                context.status = "completed"
                print("\n✅ Refactoring complete!")
                break

        if context.status != "completed":
            context.status = "escalated"

        return self.loop._format_result(context)
