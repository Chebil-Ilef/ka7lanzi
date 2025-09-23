import streamlit as st
from core.tools import show_head_tool, describe_tool
from core.dataset_manager import DatasetManager

manager = DatasetManager()

def display_dataset_head(dataset_name: str, n: int = 5):
    """
    Affiche les premières lignes d'un dataset
    """
    if not dataset_name or manager.load_dataset(dataset_name) is None:
        st.warning("No dataset loaded yet.")
        return

    st.subheader(f"Preview of '{dataset_name}'")
    head_str = show_head_tool(dataset_name, n)
    st.text(head_str)


def display_dataset_description(dataset_name: str):
    """
    Affiche les statistiques du dataset
    """
    if not dataset_name or manager.load_dataset(dataset_name) is None:
        st.warning("No dataset loaded yet.")
        return

    st.subheader(f"Description of '{dataset_name}'")
    desc_str = describe_tool(dataset_name)
    st.text(desc_str)