import streamlit as st
import pandas as pd
from core.managers.dataset_manager import DatasetManager
from core.preview import TOOLS 

manager = DatasetManager()

def _sanitize_for_streamlit(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all object columns are safe for serialization."""
    df = df.copy()
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str)
    return df

def display_dataset_head(dataset_name: str, n: int = 5):
    """
    Display the first `n` rows of a dataset in a clean table.
    """
    if not dataset_name:
        st.warning("No dataset selected yet.")
        return

    df_head = TOOLS["head"].fn(dataset_name=dataset_name, n=n)
    df_head = _sanitize_for_streamlit(df_head)

    st.subheader(f"Preview")
    st.dataframe(df_head, width="stretch")

def display_dataset_description(dataset_name: str):
    """
    Display dataset statistics (numeric summary) in a clean table.
    """
    if not dataset_name:
        st.warning("No dataset selected yet.")
        return

    df_desc = TOOLS["describe"].fn(dataset_name=dataset_name) 
    df_desc = _sanitize_for_streamlit(df_desc)

    st.subheader(f"Description")
    st.dataframe(df_desc, width="stretch")