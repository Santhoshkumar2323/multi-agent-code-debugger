import os
from typing import Optional, List

import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BaseAgent:
    def __init__(self, role: str, system_prompt: str):
        self.role = role
        self.system_prompt = system_prompt
        self.memory: List[dict] = []

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in environment variables or .env!")

        # Configure Gemini API
        genai.configure(api_key=api_key)

        # Stable, non-live model (your logs already show quota for this)
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite")

    def think(self, user_input: str, context: Optional[str] = None) -> str:
        """
        Build a single text prompt and call Gemini safely.
        """

        prompt_parts = [
            f"You are a {self.role}.",
            "",
            "SYSTEM INSTRUCTIONS:",
            self.system_prompt.strip(),
            "",
        ]

        if context:
            prompt_parts.extend([
                "CONTEXT:",
                context.strip(),
                "",
            ])

        if self.memory:
            prompt_parts.append("RECENT MEMORY:")
            for i, item in enumerate(self.memory[-3:], start=1):
                content = item.get("content", "")
                prompt_parts.append(f"- [{i}] {content[:200]}")
            prompt_parts.append("")

        prompt_parts.extend([
            "TASK:",
            user_input.strip()
        ])

        full_prompt = "\n".join(prompt_parts)

        try:
            response = self.model.generate_content(full_prompt)

            result = ""
            if hasattr(response, "candidates") and response.candidates:
                first = response.candidates[0]
                if hasattr(first, "content") and hasattr(first.content, "parts"):
                    for part in first.content.parts:
                        if hasattr(part, "text") and part.text:
                            result += part.text

            result = result.strip()
            if result:
                self.memory.append({"content": result})

            return result or "AGENT ERROR: Empty response"

        except Exception as e:
            return f"AGENT ERROR: {e}"

    def reset_memory(self):
        self.memory.clear()
