import streamlit as st

def display_results(answer: str = None, figs: list = None):
    """
    Affiche le dernier résultat de query
    """
    if 'last_query_result' in st.session_state:
        if answer:
            st.subheader("💡 Agent's Answer")
            st.write(answer)
        if figs:
            st.subheader("📈 Visualizations")
            for fig in figs:
                st.pyplot(fig)
    else:
        st.info("No query results yet.")
