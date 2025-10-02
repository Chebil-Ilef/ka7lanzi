from services.init import Init
import streamlit as st

class QueryService:
    def __init__(self, init: Init):
        self.init = init

    def handle_query(self, dataset_name: str, query: str):
        """Process a query and store results in session state."""
        if not dataset_name:
            return "⚠️ No dataset loaded"

        try:
            res = self.init.ask(query)
        except Exception as e:
            st.error(f"Error while processing query: {e}")
            st.session_state["last_answer"] = ""
            st.session_state["last_figs"] = []
            return ""

        # Store results in session state
        st.session_state["last_answer"] = res.get("answer", "")
        st.session_state["last_figs"] = res.get("figs", [])
        return st.session_state["last_answer"]