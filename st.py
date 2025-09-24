import streamlit as st
from components.file_uploader import upload_dataset
from components.data_viewer import display_dataset_head
from components.query_interface import query_interface
from components.results_display import display_results

from core.agent import WorkflowAgent

st.set_page_config(page_title="Dataset Analyzer", layout="wide")
st.title("📊 Dataset Analyzer")

# --- Init agent in session_state ---
if "agent" not in st.session_state:
    st.session_state["agent"] = WorkflowAgent()

agent: WorkflowAgent = st.session_state["agent"]

# --- Step 1: Upload dataset ---
st.sidebar.header("Step 1: Upload Dataset")
current_dataset = upload_dataset()
if current_dataset:
    st.session_state["current_dataset"] = current_dataset
    df = agent.load_dataset(current_dataset)  # load into agent
    st.success(f"✅ Dataset loaded with shape {df.shape}")

# Use previous dataset if exists
if "current_dataset" in st.session_state:
    current_dataset = st.session_state["current_dataset"]

# --- Step 2: Preview dataset ---
st.sidebar.header("Step 2: Preview Dataset")
if current_dataset:
    display_dataset_head(current_dataset, n=5)

# --- Step 3: Query interface ---
st.sidebar.header("Step 3: Ask a Question")
def on_query(dataset_name: str, query: str):
    if not dataset_name:
        return "⚠️ No dataset loaded"
    res = agent.ask(query)
    # Save results for Step 4
    st.session_state["last_answer"] = res["answer"]
    st.session_state["last_figs"] = res["figs"]
    return res["answer"]

query_interface(current_dataset, on_query)

# --- Step 4: Display results ---
st.sidebar.header("Step 4: Query Result")
if "last_answer" in st.session_state:
    display_results(
        st.session_state["last_answer"],
        st.session_state.get("last_figs", [])
    )