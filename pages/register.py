import streamlit as st
from utils.db import create_user
from utils.auth import hash_pw
from utils.session import navigate

def render():
    st.markdown('<div class="page-title">Create Account</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Join Qavi as an advisor or a client</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.5])

    with col1:
        with st.form("register_form"):
            role = st.selectbox("Account Type", ["advisor", "client"],
                                format_func=lambda x: "📋 Financial Advisor" if x == "advisor" else "👤 Client / Investor")
            full_name = st.text_input("Full Name")
            username = st.text_input("Username")
            email = st.text_input("Email (optional)")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")

            submit = st.form_submit_button("Create Account", use_container_width=True)

            if submit:
                if not username or not password or not full_name:
                    st.error("Username, full name, and password are required.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    ok = create_user(username, hash_pw(password), role, full_name, email)
                    if ok:
                        st.success("Account created! Please sign in.")
                    else:
                        st.error("Username already taken.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to Home", key="reg_back"):
            navigate("home")

        if st.button("Already have an account? Sign In", key="reg_to_login"):
            navigate("login")
