from base_agent import BaseAgent


class AnalyzerAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are an expert Python code analyzer.\n\n"
            "CRITICAL RULES:\n"
            "• Output ONLY plain text.\n"
            "• NO markdown formatting.\n"
            "• NO backticks.\n"
            "• NO code blocks.\n"
            "• Structure must follow this format EXACTLY:\n\n"
            "BUG ANALYSIS:\n"
            "Syntax Issues:\n"
            "- [issue or 'None']\n"
            "Logic Issues:\n"
            "- [issue or 'None']\n"
            "Runtime Issues:\n"
            "- [issue or 'None']\n"
            "Severity: [High/Medium/Low]\n"
        )
        super().__init__("Expert Code Analyzer", system_prompt)

    def analyze(self, code: str) -> str:
        task = (
            "Analyze the following Python code and describe ALL bugs.\n"
            "Follow the required format strictly.\n\n"
            f"Code to analyze:\n{code}"
        )
        return self.think(task)
