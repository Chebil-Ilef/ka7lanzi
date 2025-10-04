import pandas as pd
from typing import Dict, Any


class ComputeStrategy:
    def compute(self, df: pd.DataFrame, params: Dict[str, Any]):
        raise NotImplementedError