from typing import Any, Dict
from core.executor.strategies.base import ComputeStrategy
import pandas as pd


class TimeSeriesAggregateStrategy(ComputeStrategy):
    def compute(self, df: pd.DataFrame, params: Dict[str, Any]):
        try:
            date_col = params.get("date_column")
            value_col = params.get("value_column")
            freq = params.get("freq")
            
            if not date_col:
                return "[ERROR] timeseries_aggregate requires 'date_column'"
            if not value_col:
                return "[ERROR] timeseries_aggregate requires 'value_column'"
            if not freq:
                return "[ERROR] timeseries_aggregate requires 'freq' (D/W/M/Q/Y)"
            
            if date_col not in df.columns:
                return f"[ERROR] Date column '{date_col}' not found"
            if value_col not in df.columns:
                return f"[ERROR] Value column '{value_col}' not found"
            
            # Convert to datetime
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col])
            
            # Set index and resample
            df_copy = df_copy.set_index(date_col)
            result = df_copy[value_col].resample(freq).sum().reset_index()
            
            return result.to_dict(orient="records")
            
        except Exception as e:
            return f"[ERROR] timeseries_aggregate failed: {e}"