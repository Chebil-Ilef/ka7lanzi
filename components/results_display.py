import streamlit as st
from matplotlib.figure import Figure
import pandas as pd
from typing import List

def display_results(answer_text: str, figs: List[Figure|pd.DataFrame]):
    """Display the final answer text and associated figures."""
    if answer_text: 
        st.subheader("📝 Answer") 
        st.write(answer_text)

    if figs:
        st.subheader("📊 Visualizations")
        for i, fig in enumerate(figs, 1):
            if isinstance(fig, Figure):
                st.pyplot(fig, clear_figure=True, width=700)
            elif isinstance(fig, pd.DataFrame):
                st.dataframe(fig)
    else:
        st.info("No visualizations generated for this query.")