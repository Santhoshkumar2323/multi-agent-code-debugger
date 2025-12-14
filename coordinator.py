import json
import re
from analyzer_agent import AnalyzerAgent
from fixer_agent import FixerAgent
from validator_agent import ValidatorAgent
from code_executor import CodeExecutor
from memory import Memory


class Coordinator:
    def __init__(self, max_retries: int = 2):
        self.analyzer = AnalyzerAgent()
        self.fixer = FixerAgent()
        self.validator = ValidatorAgent()
        self.memory = Memory()
        self.max_retries = max_retries

        # Persistent executor so imports survive across attempts
        self.executor = CodeExecutor(timeout=5)

    def debug_code(self, buggy_code: str):
        self.memory.clear()

        # Phase 1: Analyze
        analysis = self.analyzer.analyze(buggy_code)
        self.memory.add(
            agent_name="Analyzer",
            phase="Analysis",
            status="Success",
            summary=analysis[:200],
            extra={"code": buggy_code},
        )

        current_context = analysis
        last_fixed = ""
        exec_result = {
            "success": False,
            "output": "",
            "error": None,
            "error_type": None,
        }
        validation_raw = ""

        # Phase 2: Fix + (minimal) retry
        for attempt in range(1, self.max_retries + 1):
            fixed = self.fixer.fix(current_context, buggy_code)
            code = self._clean_code(fixed)
            last_fixed = code

            self.memory.add(
                agent_name="Fixer",
                phase=f"Fix Attempt {attempt}",
                status="Generated" if code else "Empty",
                summary=fixed[:200],
                extra={"code": code},
            )

            # Basic structural sanity check before executing
            if not self._has_required_structure(buggy_code, code):
                exec_result = {
                    "success": False,
                    "output": "",
                    "error": "Invalid structure in fixed code (empty, error text, or missing imports).",
                    "error_type": "InvalidStructure",
                }

                self.memory.add(
                    agent_name="Executor",
                    phase=f"Execution Attempt {attempt}",
                    status="Skipped",
                    summary="Skipped due to invalid structure.",
                    extra={"reason": exec_result["error"]},
                )

                if attempt < self.max_retries:
                    current_context = (
                        "Previous attempt produced structurally invalid code "
                        "(e.g., empty code, removed imports, or agent error text). "
                        "Return a complete, runnable Python script that preserves imports."
                    )
                    continue
                else:
                    break

            # Execute
            exec_result = self.executor.execute(code)

            exec_status = "Success" if exec_result["success"] else "Failed"
            self.memory.add(
                agent_name="Executor",
                phase=f"Execution Attempt {attempt}",
                status=exec_status,
                summary=f"Output: {exec_result.get('output', '')[:100]}",
                extra={
                    "error": exec_result.get("error"),
                    "error_type": exec_result.get("error_type"),
                },
            )

            # If it doesn't run and we still have retries left – try again
            if not exec_result["success"] and attempt < self.max_retries:
                current_context = (
                    f"Previous attempt failed at execution.\n"
                    f"Execution result: {exec_result}\n"
                    "Fix the issues and try again.\n"
                )
                continue

            # Validator (single call per attempt)
            validation_raw = self.validator.validate(buggy_code, code, exec_result)
            is_valid = self.validator.is_valid(validation_raw)

            self.memory.add(
                agent_name="Validator",
                phase=f"Validation Attempt {attempt}",
                status="Valid" if is_valid else "Invalid",
                summary=validation_raw[:200],
                extra={"raw": validation_raw},
            )

            # Success condition: code is structurally OK, runs, and validator agrees
            if is_valid and exec_result["success"] and self._has_required_structure(
                buggy_code, code
            ):
                return {
                    "success": True,
                    "analysis": analysis,
                    "fixed_code": code,
                    "attempts": attempt,
                    "execution_result": exec_result,
                    "validation": validation_raw,
                    "history": self.memory.get_full_history(),
                }

            # Prepare context for retry
            current_context = (
                f"Previous attempt failed.\n"
                f"Execution: {exec_result}\n"
                f"Validation: {validation_raw}\n"
                "Try a better fix.\n"
            )

        # Failure result after retries
        return {
            "success": False,
            "analysis": analysis,
            "fixed_code": last_fixed,
            "attempts": self.max_retries,
            "execution_result": exec_result,
            "validation": validation_raw,
            "history": self.memory.get_full_history(),
        }

    def _clean_code(self, response: str) -> str:
        if not response:
            return ""

        # If the model wrapped code in ```python ... ``` blocks, extract the inner part
        blocks = re.findall(r"```(?:python)?(.*?)```", response, re.S | re.IGNORECASE)
        if blocks:
            return blocks[-1].strip()

        # Otherwise, just strip stray backticks and language labels
        response = response.replace("```", "").replace("`", "")
        response = re.sub(r"^\s*(python|py)\s*", "", response.strip(), flags=re.IGNORECASE)

        return response.strip()

    def _has_required_structure(self, original_code: str, fixed_code: str) -> bool:
        """
        Local sanity checks before trusting execution or validator:
        - Code cannot be empty
        - Code cannot be an AGENT ERROR string
        - If original had imports, fixed must keep at least one import
        """
        if not fixed_code or not fixed_code.strip():
            return False

        if "AGENT ERROR" in fixed_code:
            return False

        if "import " in original_code and "import " not in fixed_code:
            return False

        return True
