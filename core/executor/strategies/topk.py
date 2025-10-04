from typing import Any, Dict
from core.executor.strategies.base import ComputeStrategy
import pandas as pd


class TopKStrategy(ComputeStrategy):
    def compute(self, df: pd.DataFrame, params: Dict[str, Any]):
        try:
            column = params.get("column")
            k = params.get("k")
            ascending = params.get("ascending", False)
            
            if not column:
                return "[ERROR] topk requires 'column' parameter"
            if not k:
                return "[ERROR] topk requires 'k' parameter"
            
            if column not in df.columns:
                return f"[ERROR] Column '{column}' not found"
            
            if not isinstance(k, int) or k <= 0:
                return f"[ERROR] 'k' must be a positive integer, got {k}"
            
            # Sort and get top K
            result = df.nlargest(k, column) if not ascending else df.nsmallest(k, column)
            
            return result.to_dict(orient="records")
            
        except Exception as e:
            return f"[ERROR] topk failed: {e}"