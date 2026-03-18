import streamlit as st
from utils.db import update_user_profile, get_user_by_id
from utils.session import navigate

def render():
    if not st.session_state.get("user"):
        navigate("login"); return

    user = st.session_state.user

    st.markdown('<div class="page-title">My Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Manage your account information</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown(f"""
        <div class="qavi-card" style="text-align:center;padding:2rem">
            <div style="width:64px;height:64px;border-radius:50%;background:#253044;border:2px solid #3B82F6;display:flex;align-items:center;justify-content:center;font-size:1.6rem;margin:0 auto 1rem auto">
                {'📋' if user['role'] == 'advisor' else '👤'}
            </div>
            <div style="font-family:'DM Serif Display',serif;font-size:1.3rem;color:#EDF2F7">{user.get('full_name') or user['username']}</div>
            <div style="font-size:0.82rem;color:#94A3B8;margin-top:0.3rem">@{user['username']}</div>
            <div style="margin-top:0.8rem">
                <span class="badge badge-{'equity' if user['role'] == 'advisor' else 'mf'}" style="font-size:0.8rem">
                    {'Financial Advisor' if user['role'] == 'advisor' else 'Investor'}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### Edit Profile")
        with st.form("profile_form"):
            full_name = st.text_input("Full Name", value=user.get("full_name",""))
            email = st.text_input("Email", value=user.get("email",""))
            phone = st.text_input("Phone", value=user.get("phone",""))
            pan = st.text_input("PAN Number", value=user.get("pan",""))
            risk_profile = st.selectbox(
                "Risk Profile",
                ["Conservative", "Moderate", "Aggressive"],
                index=["Conservative","Moderate","Aggressive"].index(user.get("risk_profile","Moderate"))
            )
            submit = st.form_submit_button("Save Changes", use_container_width=True)

            if submit:
                update_user_profile(user["id"], full_name, email, phone, pan, risk_profile)
                # Refresh session
                updated = get_user_by_id(user["id"])
                st.session_state.user = updated
                st.success("Profile updated successfully!")
                st.rerun()

    # Account info
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Account Info")
    ic1, ic2, ic3 = st.columns(3)
    ic1.markdown(f"""
    <div class="qavi-card">
        <div class="qavi-card-sub">Username</div>
        <div style="font-weight:600;color:#EDF2F7;margin-top:0.3rem">{user['username']}</div>
    </div>
    """, unsafe_allow_html=True)
    ic2.markdown(f"""
    <div class="qavi-card">
        <div class="qavi-card-sub">Account Type</div>
        <div style="font-weight:600;color:#EDF2F7;margin-top:0.3rem">{'Financial Advisor' if user['role'] == 'advisor' else 'Client / Investor'}</div>
    </div>
    """, unsafe_allow_html=True)
    ic3.markdown(f"""
    <div class="qavi-card">
        <div class="qavi-card-sub">Member Since</div>
        <div style="font-weight:600;color:#EDF2F7;margin-top:0.3rem">{str(user.get('created_at',''))[:10]}</div>
    </div>
    """, unsafe_allow_html=True)
