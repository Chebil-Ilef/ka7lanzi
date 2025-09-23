import streamlit as st
from core.tools import load_dataset_tool
from config import DATA_DIR, ALLOWED_EXTENSIONS


def upload_dataset() -> str:
    """
    Composant pour uploader un dataset (CSV, Excel, JSON, Parquet)
    """
    uploaded_file = st.file_uploader("Upload your dataset")
    if uploaded_file is not None:
        file_ext = uploaded_file.name.lower().rsplit(".", 1)[-1]
        file_ext = f".{file_ext}"
        if file_ext not in ALLOWED_EXTENSIONS:
            st.error("Invalid file type. Please upload a CSV, Excel, JSON, or Parquet file.")
            return ""
        save_path = DATA_DIR / uploaded_file.name
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Load into DatasetManager
        response = load_dataset_tool(str(save_path))
        st.success(response)
        return uploaded_file.name  # dataset name
    return ""