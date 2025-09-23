import streamlit as st

def display_results():
    """
    Affiche le dernier résultat de query
    """
    if 'last_query_result' in st.session_state:
        st.subheader("Query Result")
        st.text(st.session_state['last_query_result'])
    else:
        st.info("No query results yet.")
