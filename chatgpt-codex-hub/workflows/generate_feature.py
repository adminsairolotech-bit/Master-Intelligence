"""
Generate Feature Workflow
SAI ROLO TECH
"""

from typing import Dict
from chatgpt_codex_loop import ChatGPTCodexLoop, SessionContext


class GenerateFeatureWorkflow:
    """Workflow for generating new features."""

    def __init__(self, loop: ChatGPTCodexLoop):
        self.loop = loop

    def execute(self, request: str) -> Dict:
        """Execute the feature generation workflow."""
        context = SessionContext(
            task_type="generate_feature",
            original_request=request
        )

        # Step 1: ChatGPT analyzes and creates plan
        print("\n📋 [STEP 1] ChatGPT analyzing requirements...")
        chatgpt_response = self.loop.chatgpt.analyze(request, "generate_feature")
        context.chatgpt_plan = chatgpt_response['plan']
        print(f"   ✅ Plan created with {len(chatgpt_response.get('components', []))} components")

        # Step 2: Codex generates code
        print("\n💻 [STEP 2] Codex generating code...")
        codex_response = self.loop.codex.generate(
            plan=context.chatgpt_plan,
            context=request
        )
        context.codex_code = codex_response['code']
        print(f"   ✅ Generated {len(codex_response.get('files', []))} files")

        # Step 3: ChatGPT verifies
        print("\n🔍 [STEP 3] ChatGPT verifying code...")
        verification = self.loop.chatgpt.verify(
            code=context.codex_code,
            original_request=request
        )
        context.verification_result = verification
        print(f"   ✅ Verification: {verification['status']} (score: {verification['score']})")

        # Step 4: Check result
        if verification['status'] == 'PASS':
            print("\n🎉 Feature generation complete!")
            context.status = "completed"
        elif context.iteration < context.max_iterations:
            print("\n🔄 Revision needed...")
            return self._handle_revision(context, verification)
        else:
            print("\n⚠️ Max iterations reached, escalating...")
            context.status = "escalated"

        return self.loop._format_result(context)

    def _handle_revision(self, context, verification) -> Dict:
        """Handle revision loop."""
        while context.iteration < context.max_iterations:
            context.iteration += 1
            print(f"\n🔄 [ITERATION {context.iteration}] Addressing issues...")

            # Get revised plan from ChatGPT
            revised_plan = self.loop.chatgpt.revise_plan(
                original_plan=context.chatgpt_plan,
                issues=verification['issues']
            )
            context.chatgpt_plan = revised_plan

            # Regenerate code with Codex
            codex_response = self.loop.codex.generate(
                plan=revised_plan,
                context=context.original_request,
                feedback=verification['issues']
            )
            context.codex_code = codex_response['code']

            # Re-verify
            verification = self.loop.chatgpt.verify(
                code=context.codex_code,
                original_request=context.original_request
            )
            context.verification_result = verification

            if verification['status'] == 'PASS':
                context.status = "completed"
                print("\n🎉 Feature generation complete after revision!")
                break

        if context.status != "completed":
            context.status = "escalated"
            print("\n⚠️ Max iterations reached, escalating...")

        return self.loop._format_result(context)
