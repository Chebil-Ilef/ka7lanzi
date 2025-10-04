from typing import Protocol, Dict

class IPlanner(Protocol):
    def plan(self, question: str, dataset_summary: str, columns: list) -> Dict: ...