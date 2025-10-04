from typing import Protocol, Dict, Any, List

class IExecutor(Protocol):
    def execute(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]: ...