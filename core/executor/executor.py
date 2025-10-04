import pandas as pd
from typing import Any, Dict, List
from core.executor.strategies.base import ComputeStrategy
from core.interfaces.iexecutor import IExecutor
from core.interfaces.ivisualizer import IVisualizer

class Executor(IExecutor):
    def __init__(self, df: pd.DataFrame, strategies: Dict[str, ComputeStrategy], visualizer: IVisualizer):
        self.df = df.copy()
        self.strategies = strategies
        self.visualizer = visualizer

    def execute(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        
        for idx, action in enumerate(plan.get("actions", [])):
            action_type = action.get("type")
            try:
                if action_type == "compute":
                    strategy_name = action.get("name")
                    strategy = self.strategies.get(strategy_name)
                    if strategy:
                        params = {k: v for k, v in action.items() if k not in ["type", "name"]}
                        value = strategy.compute(self.df, params)
                        results.append({
                            "type": "compute",
                            "name": strategy_name,
                            "value": value
                        })
                    else:
                        results.append({
                            "type": "error",
                            "message": f"[ERROR] Unsupported compute strategy '{strategy_name}'"
                        })
                elif action_type == "answer":
                    style = action.get("style", "detailed")
                    text = action.get("text", "Answer not generated :(")
                    results.append({
                        "type": "answer",
                        "style": style,
                        "text": text
                    })
                elif action_type == "visualize":
                    fig = self.visualizer.dispatch(self.df, action)
                    results.append({ "type": "visualize", "name": action.get("name"), "figure": fig })
                else:
                    results.append({"type": "error", "message":f"Unsupported action: type {action_type}"})
                
            except Exception as e:
                print(f"[EXECUTOR ERROR] Action {idx} failed: {e}")
        
        print("HERE ARE RESULTS OF EXECUTION", results)
        return results