from llama_index.core.tools import FunctionTool
from core.managers.dataset_manager import DatasetManager

manager = DatasetManager()

def show_head(dataset_name: str, n: int = 5):
    """Return the first n rows of the dataset."""
    try:
        df = manager.get_dataset(dataset_name)
        if df is None:
            return f"❌ No dataset named '{dataset_name}' loaded."
        return df.head(n)
    except Exception as e:
        return f"❌ Error displaying head: {str(e)}"

def describe_dataset(dataset_name: str):
    """Return basic statistics of the dataset."""
    try:
        df = manager.get_dataset(dataset_name)
        if df is None:
            return f"❌ No dataset named '{dataset_name}' loaded."
        return df.describe(include="all")
    except Exception as e:
        return f"❌ Error describing dataset: {str(e)}"

TOOLS = {
    "head": FunctionTool.from_defaults(fn=show_head),
    "describe": FunctionTool.from_defaults(fn=describe_dataset),
}