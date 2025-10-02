from pathlib import Path
import pandas as pd
from typing import Optional

class DatasetManager:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.path: Optional[Path] = None

    def load(self, path: str) -> pd.DataFrame:
        p = Path(path)
        ext = p.suffix.lower()
        if ext == ".csv":
            df = pd.read_csv(p)
        elif ext in [".json"]:
            df = pd.read_json(p)
        elif ext in [".parquet"]:
            df = pd.read_parquet(p)
        elif ext in [".xls", ".xlsx"]:
            df = pd.read_excel(p)
        else:
            raise ValueError(f"Unsupported extension {ext}")
        
        self.df = df
        self.path = p
        return df

    def basic_stats_text(self) -> str:
        df = self.df
        if df is None:
            return ""
        lines = [f"Dataset with {len(df)} rows and {len(df.columns)} columns."]
        for c in df.columns:
            lines.append(f"- {c}: {str(df[c].dtype)}, missing={int(df[c].isna().sum())}")
        return "\n".join(lines)