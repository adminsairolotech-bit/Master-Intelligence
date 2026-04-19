"""
Fix Bug Workflow
SAI ROLO TECH
"""

from __future__ import annotations
from typing import Dict


class FixBugWorkflow:
    """Workflow for fixing bugs."""

    def __init__(self, loop: ChatGPTCodexLoop):
        self.loop = loop

    def execute(self, bug_description: str) -> Dict:
        """Execute the bug fix workflow."""
        context = SessionContext(
            task_type="fix_bug",
            original_request=bug_description
        )

        # Step 1: ChatGPT analyzes the bug
        print("\n🐛 [STEP 1] ChatGPT analyzing bug...")
        chatgpt_response = self.loop.chatgpt.analyze(bug_description, "fix_bug")
        context.chatgpt_plan = chatgpt_response['plan']
        print(f"   ✅ Analysis complete")

        # Step 2: Codex proposes fix
        print("\n🔧 [STEP 2] Codex generating fix...")
        codex_response = self.loop.codex.generate(
            plan=context.chatgpt_plan,
            context=bug_description
        )
        context.codex_code = codex_response['code']
        print(f"   ✅ Fix generated")

        # Step 3: ChatGPT tests the fix
        print("\n🧪 [STEP 3] ChatGPT testing fix...")
        verification = self.loop.chatgpt.verify(
            code=context.codex_code,
            original_request=bug_description
        )
        context.verification_result = verification
        print(f"   ✅ Test result: {verification['status']}")

        if verification['status'] == 'PASS':
            print("\n✅ Bug fixed!")
            context.status = "completed"
        elif context.iteration < context.max_iterations:
            return self._handle_revision(context, verification)
        else:
            print("\n⚠️ Max iterations reached, escalating...")
            context.status = "escalated"

        return self.loop._format_result(context)

    def _handle_revision(self, context, verification) -> Dict:
        """Handle revision for bug fix."""
        while context.iteration < context.max_iterations:
            context.iteration += 1
            print(f"\n🔄 [ITERATION {context.iteration}] Retrying fix...")

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
                print("\n✅ Bug fixed!")
                break

        if context.status != "completed":
            context.status = "escalated"
            print("\n⚠️ Max iterations reached, escalating...")

        return self.loop._format_result(context)
