from typing import Any, Dict
from core.executor.strategies.base import ComputeStrategy
import pandas as pd


class GroupByStrategy(ComputeStrategy):
    def compute(self, df: pd.DataFrame, params: Dict[str, Any]):
        try:
            by = params.get("by")
            if not by or by not in df.columns:
                return f"[ERROR] Invalid groupby column: {by}"
            agg = params.get("agg", "mean")
            target = params.get("target")

            # Only use numeric columns for mean/median/sum if target not specified
            if agg in ("mean", "median", "sum"):
                if target:
                    if target not in df.select_dtypes(include="number").columns:
                        return f"[ERROR] Target column '{target}' is not numeric for agg='{agg}'"
                    group_df = df.groupby(by)[target].agg(agg).reset_index()
                else:
                    numeric_cols = df.select_dtypes(include="number").columns
                    group_df = df.groupby(by)[numeric_cols].agg(agg).reset_index()
            else:
                group_df = df.groupby(by).agg(agg).reset_index()

            return group_df.to_dict(orient="records")
        except Exception as e:
            return f"[ERROR] compute_groupby failed: {e}"