from base_agent import BaseAgent


class FixerAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are an EXPERT Python code fixer.\n\n"
            "CRITICAL RULES:\n"
            "• Output ONLY valid Python code.\n"
            "• Code MUST be fully runnable.\n"
            "• Put ALL explanation inside comments at the TOP of the code.\n"
            "• NO text before or after the code.\n"
            "• NO markdown backticks in the output.\n"
            "• Maintain original intent of the code.\n"
        )
        super().__init__("Expert Code Fixer", system_prompt)

    def fix(self, analysis: str, original_code: str) -> str:
        task = (
            "Fix the code based on the bug report.\n"
            "Return ONLY clean Python code.\n\n"
            "BUG ANALYSIS:\n"
            f"{analysis}\n\n"
            "ORIGINAL CODE:\n"
            f"{original_code}\n\n"
            "Start your output with:\n"
            "# Fixed code\n"
        )
        return self.think(task)
