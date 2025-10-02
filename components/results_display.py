import streamlit as st
from matplotlib.figure import Figure
from typing import List

def display_results(answer_text: str, figs: List[Figure]):
    """Display the final answer text and associated figures."""
    st.subheader("Answer")
    st.markdown(answer_text)

    if figs:
        st.subheader("Visualizations")
        for i, fig in enumerate(figs, 1):
            st.pyplot(fig, clear_figure=True)
    else:
        st.info("No visualizations generated for this query.")