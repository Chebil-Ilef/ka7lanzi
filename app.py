import streamlit as st

from components.file_uploader import upload_dataset
from components.data_viewer import display_dataset_head, display_dataset_description
from components.query_interface import query_interface
from components.results_display import display_results

from services.init import Init
from services.query import QueryService

st.set_page_config(page_title="Dataset Analyzer", layout="wide")
st.title("📊 Dataset Analyzer")


if "init" not in st.session_state:
    st.session_state["init"] = Init()
init: Init = st.session_state["init"]

# --- Upload dataset ---
st.sidebar.header("Step 1: Upload Dataset")
uploaded_name = upload_dataset()
if uploaded_name:
    df = init.load_dataset(uploaded_name)
    st.session_state["current_dataset"] = uploaded_name
    st.session_state["df"] = df
current_dataset = st.session_state.get("current_dataset", None)
df = st.session_state.get("df", None)

# --- Start heavy AI initialization ---
if current_dataset and not init.agent.is_ready():
    init.start_agent_init()
    with st.spinner("Initializing AI components ..."):
        try:
            init.wait_for_agent_ready()
        except RuntimeError as e:
            st.error("AI initialization failed")
            st.text(str(e))
            st.stop()

# --- Preview dataset ---
st.sidebar.header("Step 2: Preview Dataset")
if current_dataset and df is not None:
    display_dataset_head(current_dataset, n=5)
    display_dataset_description(current_dataset)
else:
    st.info("Upload a dataset to preview it here.")

# --- Query interface ---
st.sidebar.header("Step 3: Ask a Question")
if current_dataset:
    q = QueryService(init)
    query_interface(current_dataset, q.handle_query)

# --- Display results ---
st.sidebar.header("Step 4: Query Result")
if "last_answer" in st.session_state:
    answer_text = st.session_state["last_answer"]
    figs = st.session_state.get("last_figs", [])
    display_results(answer_text, figs)