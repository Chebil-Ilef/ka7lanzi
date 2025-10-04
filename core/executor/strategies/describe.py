from typing import Any, Dict
from core.executor.strategies.base import ComputeStrategy


class DescribeStrategy(ComputeStrategy):
    def compute(self, df, params: Dict[str, Any]):
        try:
            cols = params.get("columns", df.columns)
            valid = [c for c in cols if c in df.columns]
            if not valid:
                return "[ERROR] No valid columns for describe"
            numeric_valid = [c for c in valid if c in df.select_dtypes(include="number").columns]
            if not numeric_valid:
                return "[ERROR] No valid numeric columns for describe"
            return df[numeric_valid].describe().to_dict()

        except Exception as e:
            return f"[ERROR] compute_describe failed: {e}"