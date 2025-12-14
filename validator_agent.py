from base_agent import BaseAgent
import json


class ValidatorAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You validate Python code fixes.\n"
            "Respond ONLY with valid JSON:\n\n"
            "{\n"
            "  \"validation\": \"VALID\" or \"INVALID\",\n"
            "  \"reason\": \"short reason\",\n"
            "  \"remaining_issues\": [list of issues],\n"
            "  \"confidence\": \"High/Medium/Low\"\n"
            "}\n"
        )
        super().__init__("Expert Code Validator", system_prompt)

    def validate(self, original_code: str, fixed_code: str, execution_result: dict) -> str:
        payload = (
            "Assess whether this code is fixed correctly.\n"
            "Return ONLY JSON.\n\n"
            f"Original Code:\n{original_code}\n\n"
            f"Fixed Code:\n{fixed_code}\n\n"
            f"Execution Result:\n{execution_result}\n"
        )
        return self.think(payload)

    def is_valid(self, validation_response: str) -> bool:
        cleaned = (
            validation_response.replace("```json", "")
            .replace("```", "")
            .strip()
        )
        try:
            data = json.loads(cleaned)
            return data.get("validation", "").upper() == "VALID"
        except Exception:
            return False

    def parse_json(self, validation_response: str):
        cleaned = (
            validation_response.replace("```json", "")
            .replace("```", "")
            .strip()
        )
        try:
            return json.loads(cleaned)
        except Exception:
            return None
