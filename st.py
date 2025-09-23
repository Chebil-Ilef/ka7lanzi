import streamlit as st
from components.file_uploader import upload_dataset
from components.data_viewer import display_dataset_head, display_dataset_description
from components.query_interface import query_interface
from components.results_display import display_results

st.set_page_config(page_title="Dataset Analyzer", layout="wide")
st.title("📊 Dataset Analyzer")

# --- Step 1: Upload dataset ---
st.sidebar.header("Step 1: Upload Dataset")
current_dataset = upload_dataset()
if current_dataset:
    st.session_state["current_dataset"] = current_dataset

# Use previous dataset if exists
if "current_dataset" in st.session_state:
    current_dataset = st.session_state["current_dataset"]
else:
    current_dataset = None

# --- Step 2: Preview dataset ---
st.sidebar.header("Step 2: Preview Dataset")
if current_dataset:
    display_dataset_head(current_dataset, n=5)
    display_dataset_description(current_dataset)

# --- Step 3: Query interface ---
st.sidebar.header("Step 3: Ask a Question")
def on_query(dataset_name: str, query: str) -> str:
    """
    Simple wrapper around query_tool for prototyping.
    Later replace with DatasetAgent query.
    """
    return "hello from query tool"

query_interface(current_dataset, on_query)

# --- Step 4: Display results ---
st.sidebar.header("Step 4: Query Result")
display_results()