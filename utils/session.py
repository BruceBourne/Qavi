import streamlit as st

def init_session():
    defaults = {
        "page": "home",
        "user": None,
        "page_history": [],
        "selected_client_id": None,
        "selected_portfolio_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def navigate(page):
    if st.session_state.get("page") != page:
        if "page_history" not in st.session_state:
            st.session_state.page_history = []
        st.session_state.page_history.append(st.session_state.get("page", "home"))
    st.session_state.page = page
    st.rerun()
