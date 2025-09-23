import pandas as pd
from config import DATA_DIR


class DatasetManager:
    _instance = None
    _datasets = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def save_dataset(self, name: str, df):
        path = DATA_DIR / name
        if path.suffix.lower() == ".csv":
            df.to_csv(path, index=False)
        elif path.suffix.lower() in [".xls", ".xlsx"]:
            df.to_excel(path, index=False)
        elif path.suffix.lower() == ".parquet":
            df.to_parquet(path)
        else:
            raise ValueError("Unsupported file type")
        self._datasets[name] = df

    def load_dataset(self, name: str):
        path = DATA_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"{name} not found")
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        elif path.suffix.lower() in [".xls", ".xlsx"]:
            df = pd.read_excel(path)
        elif path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
        self._datasets[name] = df
        return df