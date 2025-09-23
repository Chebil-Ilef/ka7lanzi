import pandas as pd
from pathlib import Path
from llama_index.core.tools import FunctionTool
from core.dataset_manager import DatasetManager

manager = DatasetManager()

def load_dataset(file_path: str) -> str:
    """
    Load a dataset (CSV, Excel, JSON, Parquet) into memory.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"File not found: {file_path}"

        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        elif path.suffix.lower() in [".xls", ".xlsx"]:
            df = pd.read_excel(path)
        elif path.suffix.lower() == ".json":
            df = pd.read_json(path)
        elif path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
        else:
            return f"Unsupported file type: {path.suffix}"
        
        manager.save_dataset(path.name, df)
        return f"✅ Dataset '{path.name}' loaded with {df.shape[0]} rows and {df.shape[1]} columns."

    except Exception as e:
        return f"❌ Error loading dataset: {str(e)}"

def show_head(dataset_name: str, n: int = 5) -> str:
    """Return the first n rows of the dataset."""
    try:
        df = manager.get_dataset(dataset_name)
        if df is None:
            return f"❌ No dataset named '{dataset_name}' loaded."
        return str(df.head(n))
    except Exception as e:
        return f"❌ Error displaying head: {str(e)}"

def describe_data(dataset_name: str) -> str:
    """Return basic statistics of the dataset."""
    try:
        df = manager.get_dataset(dataset_name)
        if df is None:
            return f"❌ No dataset named '{dataset_name}' loaded."
        return str(df.describe(include="all"))
    except Exception as e:
        return f"❌ Error describing dataset: {str(e)}"

# Wrappers en FunctionTool
load_dataset_tool = FunctionTool.from_defaults(fn=load_dataset)
show_head_tool = FunctionTool.from_defaults(fn=show_head)
describe_tool = FunctionTool.from_defaults(fn=describe_data)