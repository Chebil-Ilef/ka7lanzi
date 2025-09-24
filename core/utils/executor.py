import pandas as pd
from typing import Any, Dict

class Executor:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def compute_correlation(self, target: str, top_n: int = 5):
        corr = self.df.corr().get(target)
        if corr is None:
            return None
        s = corr.drop(labels=[target], errors='ignore').abs().sort_values(ascending=False).head(top_n)
        return s

    def compute_groupby(self, column: str, agg: str = "mean", target: str = None):
        if target:
            return self.df.groupby(column)[target].agg(agg).reset_index()
        return self.df.groupby(column).agg(agg).reset_index()

    def execute(self, plan: Dict[str, Any]):
        results = []
        for step in plan.get("actions", []):
            a = step["action"]
            if a == "compute":
                name = step["name"]
                params = step.get("params", {})
                if name == "correlation":
                    r = self.compute_correlation(params["target"], params.get("top_n", 5))
                    results.append({"type":"compute", "name":"correlation", "value": r, "meta": params})
                elif name == "groupby":
                    r = self.compute_groupby(params["by"], params.get("agg","mean"), params.get("target"))
                    results.append({"type":"compute","name":"groupby","value":r,"meta":params})
            elif a == "visualize":
                results.append({"type":"visualize","name":step["name"], "params": step.get("params",{})})
            elif a == "answer":
                results.append({"type":"answer","params":step.get("params",{})})
        return results