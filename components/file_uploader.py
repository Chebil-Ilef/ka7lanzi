import streamlit as st
from config import DATA_DIR, ALLOWED_EXTENSIONS
from core.managers.dataset_manager import DatasetManager

# Initialize dataset manager
manager = DatasetManager()

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

        try:
            df = manager.load(uploaded_file.name)
            if df is None:
                st.error("Failed to load dataset. Please check the file format.")
                return ""
            st.success(f"Dataset '{uploaded_file.name}' uploaded and loaded successfully! ✅")
        except Exception as e:
            st.error(f"Error loading dataset: {str(e)}")
            return ""

        return uploaded_file.name

    return ""