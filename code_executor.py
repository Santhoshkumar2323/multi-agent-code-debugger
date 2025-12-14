import io
import contextlib
from typing import Dict, Any


class CodeExecutor:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        # Persistent execution environment so imports + functions survive between calls
        self.env: Dict[str, Any] = {
    "__builtins__": __builtins__,
    "__name__": "__main__",   # ← NEW
}


    def execute(self, code: str) -> Dict[str, Any]:
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        result = {
            "success": False,
            "output": "",
            "error": None,
            "error_type": None,
        }

        try:
            with contextlib.redirect_stdout(stdout_buffer):
                with contextlib.redirect_stderr(stderr_buffer):
                    exec(code, self.env, self.env)

            result["success"] = True
            # Combine stdout + stderr
            out = stdout_buffer.getvalue()
            err = stderr_buffer.getvalue()
            result["output"] = (out + ("\n" + err if err else "")).strip()

        except SyntaxError as e:
            result["error"] = f"Syntax Error: {str(e)}"
            result["error_type"] = "SyntaxError"
            result["output"] = stdout_buffer.getvalue()

        except NameError as e:
            result["error"] = f"Name Error: {str(e)}"
            result["error_type"] = "NameError"
            result["output"] = stdout_buffer.getvalue()

        except TypeError as e:
            result["error"] = f"Type Error: {str(e)}"
            result["error_type"] = "TypeError"
            result["output"] = stdout_buffer.getvalue()

        except ZeroDivisionError as e:
            result["error"] = f"Zero Division Error: {str(e)}"
            result["error_type"] = "ZeroDivisionError"
            result["output"] = stdout_buffer.getvalue()

        except Exception as e:
            result["error"] = f"{type(e).__name__}: {str(e)}"
            result["error_type"] = type(e).__name__
            result["output"] = stdout_buffer.getvalue()

        return result


def execute_code(code: str, timeout: int = 5) -> Dict[str, Any]:
    # Legacy helper – NOT used by Coordinator anymore
    executor = CodeExecutor(timeout=timeout)
    return executor.execute(code)
