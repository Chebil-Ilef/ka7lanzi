from typing import Any, Dict
from core.executor.strategies.base import ComputeStrategy


class CorrelationStrategy(ComputeStrategy):
    def compute(self, df, params: Dict[str, Any]):
        try:
            if "target" in params:
                target = params["target"]
                top_n = params.get("top_n", 5)

                # restrict to numeric only
                numeric_df = df.select_dtypes(include=["number"])
                if target not in numeric_df.columns:
                    return f"[ERROR] Target column '{target}' not found or not numeric"

                corr = numeric_df.corr().get(target)
                if corr is None:
                    return f"[ERROR] Target column '{target}' not found"
                s = corr.drop(labels=[target], errors="ignore").abs().sort_values(ascending=False).head(top_n)
                return s.to_dict()

            elif "columns" in params:
                # filter only numeric cols
                cols = [c for c in params["columns"] if c in df.select_dtypes(include=["number"]).columns]
                if not cols:
                    return "[ERROR] No valid numeric columns found for correlation"
                return df[cols].corr().to_dict()

            else:
                return "[ERROR] Missing 'target' or 'columns' in correlation params"

        except Exception as e:
            return f"[ERROR] compute_correlation failed: {e}"
