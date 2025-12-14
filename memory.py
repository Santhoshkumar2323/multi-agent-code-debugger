from datetime import datetime
from typing import List, Dict, Any, Optional


class Memory:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def add(self, agent_name: str, phase: str, status: str,
            summary: str, extra: Optional[Dict[str, Any]] = None) -> None:
        entry = {
            "agent": agent_name,
            "phase": phase,
            "status": status,
            "summary": summary,
            "extra": extra or {},
            "timestamp": datetime.now().isoformat(),
        }
        self.history.append(entry)

    def get_full_history(self) -> List[Dict[str, Any]]:
        return self.history.copy()

    def clear(self) -> None:
        self.history = []
