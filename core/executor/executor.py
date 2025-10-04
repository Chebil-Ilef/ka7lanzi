import pandas as pd
from typing import Any, Dict, List
from core.executor.strategies.base import ComputeStrategy
from core.interfaces.iexecutor import IExecutor

class Executor(IExecutor):
    def __init__(self, df: pd.DataFrame, strategies: Dict[str, ComputeStrategy]):
        self.df = df.copy()
        self.strategies = strategies

    def execute(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        for step in plan.get("actions", []):
            strategy = self.strategies.get(step["name"])
            value = strategy.compute(self.df, step.get("params", {})) if strategy else "[ERROR] Unsupported"
            results.append({"type": "compute", "name": step["name"], "value": value})
            
        print("RESULTS:", results)
        return results