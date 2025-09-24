import streamlit as st
import pandas as pd
from core.managers.dataset_manager import DatasetManager
from core.preview import TOOLS 

manager = DatasetManager()

def display_dataset_head(dataset_name: str, n: int = 5):
    """
    Display the first `n` rows of a dataset in a clean table.
    """
    if not dataset_name:
        st.warning("No dataset selected yet.")
        return

    df_head = TOOLS["head"].fn(df=dataset_name, n=n)

    st.subheader(f"Preview of '{dataset_name}'")
    st.dataframe(df_head, use_container_width=True)


def display_dataset_description(dataset_name: str):
    """
    Display dataset statistics (numeric summary) in a clean table.
    """
    if not dataset_name:
        st.warning("No dataset selected yet.")
        return

    df_desc = TOOLS["describe"].fn(df=dataset_name) 

    st.subheader(f"Description of '{dataset_name}'")
    st.dataframe(df_desc, use_container_width=True)