import streamlit as st
import threading
import asyncio
import time
import traceback

from components.file_uploader import upload_dataset
from components.data_viewer import display_dataset_head, display_dataset_description
from components.query_interface import query_interface
from components.results_display import display_results

from core.agent import WorkflowAgent

st.set_page_config(page_title="Dataset Analyzer", layout="wide")
st.title("📊 Dataset Analyzer")


def _start_agent_init_in_thread(agent: WorkflowAgent):
    if getattr(agent, "_init_started", False):
        return

    def target():
        try:
            asyncio.run(agent.async_init())
        except Exception:
            agent._init_error = traceback.format_exc()
        finally:
            agent._init_finished = True

    agent._init_started = True
    t = threading.Thread(target=target, daemon=True)
    agent._init_thread = t
    t.start()


# --- Ensure agent in session state ---
if "agent" not in st.session_state:
    st.session_state["agent"] = WorkflowAgent()

agent: WorkflowAgent = st.session_state["agent"]

# --- Step 1: Upload dataset ---
st.sidebar.header("Step 1: Upload Dataset")
uploaded_name = upload_dataset()
if uploaded_name:
    st.session_state["current_dataset"] = uploaded_name


current_dataset = st.session_state.get("current_dataset", None)

# Only start heavy AI initialization AFTER the dataset has been loaded into agent
# (this prevents LLM from starting as soon as the app opens)
if current_dataset and not agent.is_ready() and not getattr(agent, "_init_started", False):
    _start_agent_init_in_thread(agent)

# --- Step 2: Preview dataset ---
st.sidebar.header("Step 2: Preview Dataset")
if current_dataset:
    display_dataset_head(current_dataset, n=5)
    display_dataset_description(current_dataset)
else:
    st.info("Upload a dataset to preview it here.")

# --- Wait for AI components if they are initializing ---
if current_dataset and not agent.is_ready():
    if getattr(agent, "_init_started", False):
        with st.spinner("Initializing AI components ..."):
            # Poll until the worker thread finishes (agent.ready will be True on success)
            # Small sleep keeps the UI responsive and keeps spinner animated.
            # This loop blocks the script while showing the spinner, but dataset preview has already been rendered above.
            while not agent.is_ready() and not getattr(agent, "_init_finished", False):
                time.sleep(0.2)

        # if an error occurred during init, show it and allow retry
        if getattr(agent, "_init_error", None):
            st.error("AI initialization failed. See details below.")
            st.text(agent._init_error)
            if st.button("Retry initialization"):
                # reset flags and restart
                agent._init_started = False
                agent._init_finished = False
                agent._init_error = None
                _start_agent_init_in_thread(agent)
            st.stop()

    else:
        st.info("AI components will be initialized after dataset selection.")
        st.stop()

# --- Step 3: Query interface ---
st.sidebar.header("Step 3: Ask a Question")

def on_query(dataset_name: str, query: str):
    if not dataset_name:
        return "⚠️ No dataset loaded"
    try:
        res = agent.ask(query)
    except Exception as e:
        st.error(f"Error while processing query: {e}")
        return f"Error: {e}"
    # Save results for Step 4
    st.session_state["last_answer"] = res["answer"]
    st.session_state["last_figs"] = res["figs"]
    return res["answer"]

# Only show the query UI when we have a dataset loaded.
# If the agent is not ready yet, we already blocked above with spinner until it is ready.
if current_dataset:
    query_interface(current_dataset, on_query)
else:
    st.info("Please upload a dataset to enable the query interface.")

# --- Step 4: Display results ---
st.sidebar.header("Step 4: Query Result")
if "last_answer" in st.session_state:
    display_results(
        st.session_state["last_answer"],
        st.session_state.get("last_figs", [])
    )