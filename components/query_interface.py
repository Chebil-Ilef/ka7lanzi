import streamlit as st

def query_interface(current_dataset: str, on_query):
    """
    Composant pour poser des questions sur le dataset
    `on_query` : fonction qui prend la query et retourne un résultat (str)
    """
    if not current_dataset:
        st.warning("Please upload and load a dataset first.")
        return

    query = st.text_input("Ask a question about the dataset:")
    if st.button("Submit Query"):
        if query.strip():
            result = on_query(current_dataset, query)
            st.session_state['last_query_result'] = result
            st.text(result)
        else:
            st.warning("Query is empty.")