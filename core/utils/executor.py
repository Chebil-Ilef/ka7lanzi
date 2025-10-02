import pandas as pd
from typing import Any, Dict, Optional, List
from core.utils.visualizer import Visualizer
import json

class Executor:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.visualizer = Visualizer()
        self.last_compute_result: Optional[pd.DataFrame] = None 

    def compute_correlation(self, params: Dict[str, Any]):
        try:
            if "target" in params:
                target = params["target"]
                top_n = params.get("top_n", 5)

                # restrict to numeric only
                numeric_df = self.df.select_dtypes(include=["number"])
                if target not in numeric_df.columns:
                    return f"[ERROR] Target column '{target}' not found or not numeric"

                corr = numeric_df.corr().get(target)
                if corr is None:
                    return f"[ERROR] Target column '{target}' not found"
                s = corr.drop(labels=[target], errors="ignore").abs().sort_values(ascending=False).head(top_n)
                return s.to_dict()

            elif "columns" in params:
                # filter only numeric cols
                cols = [c for c in params["columns"] if c in self.df.select_dtypes(include=["number"]).columns]
                if not cols:
                    return "[ERROR] No valid numeric columns found for correlation"
                return self.df[cols].corr().to_dict()

            else:
                return "[ERROR] Missing 'target' or 'columns' in correlation params"

        except Exception as e:
            return f"[ERROR] compute_correlation failed: {e}"


    def compute_groupby(self, params: Dict[str, Any]):
        try:
            by = params.get("by")
            if not by or by not in self.df.columns:
                return f"[ERROR] Invalid groupby column: {by}"
            agg = params.get("agg", "mean")
            target = params.get("target")
            if target:
                if target not in self.df.select_dtypes(include="number").columns and agg in ("mean", "median", "sum"):
                    return f"[ERROR] Target column '{target}' is not numeric for agg='{agg}'"
            return self.df.groupby(by).agg(agg).reset_index().to_dict(orient="records")
        except Exception as e:
            return f"[ERROR] compute_groupby failed: {e}"

    def compute_describe(self, params: Dict[str, Any]):
        try:
            cols = params.get("columns", self.df.columns)
            valid = [c for c in cols if c in self.df.columns]
            if not valid:
                return "[ERROR] No valid columns for describe"
            numeric_valid = [c for c in valid if c in self.df.select_dtypes(include="number").columns]
            if not numeric_valid:
                return "[ERROR] No valid numeric columns for describe"
            return self.df[numeric_valid].describe().to_dict()

        except Exception as e:
            return f"[ERROR] compute_describe failed: {e}"

    def render_results(self, exec_results: List[Dict[str, Any]]):
        """
        Convert execution results into a textual summary and plots.
        Returns (context_string, textual_parts, figs).
        """
        textual_parts = []
        figs = []

        for step in exec_results:
            if step["type"] == "compute":
                name = step["name"]
                val = step["value"]

                if isinstance(val, dict):
                    textual_parts.append(f"[{name.upper()} RESULT]\n{json.dumps(val, indent=2)}")
                else:
                    textual_parts.append(f"[{name.upper()} RESULT]\n{val}")

            elif step["type"] == "answer":
                style = step.get("params", {}).get("style", "summary")
                textual_parts.append(f"[ANSWER REQUEST: style={style}]")

            elif step["type"] == "visualize":
                fig = self._dispatch_visualization(step)
                if fig:
                    figs.append(fig)

            elif step["type"] == "error":
                textual_parts.append(f"[ERROR] {step.get('message')}")

        context = "\n\n".join(textual_parts)
        return context, textual_parts, figs

    def _dispatch_visualization(self, step: Dict[str, Any]):
        """Route visualize actions to Visualizer"""
        params = step.get("params", {})
        name = step.get("name")

        if name == "heatmap":
            cols = params.get("columns", self.df.columns)
            numeric_cols = [c for c in cols if c in self.df.select_dtypes(include="number").columns]
            return self.visualizer.heatmap(self.df, numeric_cols)

        elif name == "boxplot":
            return self.visualizer.boxplot(self.df, column=params.get("column"), by=params.get("by"))
        elif name == "scatter":
            return self.visualizer.scatter(self.df, x=params.get("x"), y=params.get("y"))
        elif name == "histogram":
            return self.visualizer.histogram(self.df, column=params.get("column"))
        return None
    
    # --- Execution ---
    def execute(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        for step in plan.get("actions", []):
            try:
                action_type = step["action"]
                params = step.get("params", {})
                name = step.get("name")

                if action_type == "compute":
                    if name == "correlation":
                        value = self.compute_correlation(params)
                    elif name == "groupby":
                        value = self.compute_groupby(params)
                    elif name == "describe":
                        value = self.compute_describe(params)
                    else:
                        value = f"[ERROR] Unsupported compute action: {name}"

                    results.append({
                        "type": "compute",
                        "name": name,
                        "value": value,
                        "meta": params
                    })

                elif action_type == "visualize":
                    results.append({
                        "type": "visualize",
                        "name": name,
                        "params": params
                    })

                elif action_type == "answer":
                    results.append({
                        "type": "answer",
                        "params": params
                    })

                else:
                    results.append({
                        "type": "error",
                        "message": f"Unsupported action type: {action_type}"
                    })

            except Exception as e:
                results.append({
                    "type": "error",
                    "step": step,
                    "message": str(e)
                })
        print("RESULTS:", results)
        return results