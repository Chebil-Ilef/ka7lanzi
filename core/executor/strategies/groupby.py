from typing import Any, Dict
from core.executor.strategies.base import ComputeStrategy


class GroupByStrategy(ComputeStrategy):
    def compute(self, df, params: Dict[str, Any]):
        try:
            by = params.get("by")
            if not by or by not in df.columns:
                return f"[ERROR] Invalid groupby column: {by}"
            agg = params.get("agg", "mean")
            target = params.get("target")
            if target:
                if target not in df.select_dtypes(include="number").columns and agg in ("mean", "median", "sum"):
                    return f"[ERROR] Target column '{target}' is not numeric for agg='{agg}'"
            return df.groupby(by).agg(agg).reset_index().to_dict(orient="records")
        except Exception as e:
            return f"[ERROR] compute_groupby failed: {e}"