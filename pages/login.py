import streamlit as st
from utils.db import get_user_by_username
from utils.auth import verify_pw
from utils.session import navigate

def render():
    st.markdown('<div class="page-title">Sign In</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Welcome back to Qavi</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.5])

    with col1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", use_container_width=True)

            if submit:
                if not username or not password:
                    st.error("Please fill all fields.")
                else:
                    user = get_user_by_username(username)
                    if user and verify_pw(password, user["password"]):
                        st.session_state.user = user
                        st.session_state.page_history = []
                        if user["role"] == "advisor":
                            navigate("advisor_dashboard")
                        else:
                            navigate("client_dashboard")
                    else:
                        st.error("Invalid username or password.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to Home", key="login_back"):
            navigate("home")

        st.markdown("""
        <p style="color:#94A3B8; font-size:0.83rem; margin-top:1rem;">
            Don't have an account? <a href="#" onclick="" style="color:#3B82F6;">Register below</a>
        </p>
        """, unsafe_allow_html=True)
        if st.button("Create Account →", key="login_to_register"):
            navigate("register")
