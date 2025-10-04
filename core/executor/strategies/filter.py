from typing import Any, Dict
from core.executor.strategies.base import ComputeStrategy
import pandas as pd


class FilterStrategy(ComputeStrategy):
    def compute(self, df: pd.DataFrame, params: Dict[str, Any]):
        try:
            column = params.get("column")
            operator = params.get("operator")
            value = params.get("value")
            
            if not column:
                return "[ERROR] filter requires 'column' parameter"
            if not operator:
                return "[ERROR] filter requires 'operator' parameter"
            if value is None:
                return "[ERROR] filter requires 'value' parameter"
            
            if column not in df.columns:
                return f"[ERROR] Column '{column}' not found"
            
            # Apply filter
            if operator == ">":
                result = df[df[column] > value]
            elif operator == "<":
                result = df[df[column] < value]
            elif operator == "==":
                result = df[df[column] == value]
            elif operator == ">=":
                result = df[df[column] >= value]
            elif operator == "<=":
                result = df[df[column] <= value]
            elif operator == "!=":
                result = df[df[column] != value]
            else:
                return f"[ERROR] Unknown operator: {operator}"
            
            return {
                "filtered_count": len(result),
                "total_count": len(df),
                "sample": result.head(10).to_dict(orient="records")
            }
            
        except Exception as e:
            return f"[ERROR] filter failed: {e}"