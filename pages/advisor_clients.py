import streamlit as st
from utils.db import get_advisor_clients, get_user_by_username, link_client
from utils.session import navigate

def render():
    if not st.session_state.get("user"):
        navigate("login"); return

    user = st.session_state.user
    advisor_id = user["id"]

    st.markdown('<div class="page-title">Clients</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Manage your client relationships</div>', unsafe_allow_html=True)

    clients = get_advisor_clients(advisor_id)

    tab1, tab2 = st.tabs(["  👥 Client List  ", "  ➕ Add Client  "])

    with tab1:
        if not clients:
            st.info("No clients linked yet. Use the 'Add Client' tab to add one.")
        else:
            # Search
            search = st.text_input("🔍 Search clients", placeholder="Name or username...")
            filtered = [c for c in clients if
                        search.lower() in (c.get("full_name") or "").lower()
                        or search.lower() in c["username"].lower()] if search else clients

            for cl in filtered:
                with st.container():
                    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
                    risk = cl.get("risk_profile", "Moderate")
                    risk_colors = {"Conservative": "#22C55E", "Moderate": "#F59E0B", "Aggressive": "#EF4444"}
                    rc = risk_colors.get(risk, "#94A3B8")

                    c1.markdown(f"""
                    <div>
                        <div style="font-weight:600;color:#EDF2F7">{cl.get('full_name') or cl['username']}</div>
                        <div style="font-size:0.8rem;color:#94A3B8">@{cl['username']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    c2.markdown(f"<div style='padding-top:0.5rem;font-size:0.85rem;color:#94A3B8'>{cl.get('email','—')}</div>", unsafe_allow_html=True)
                    c3.markdown(f"<div style='padding-top:0.5rem'><span style='color:{rc};font-size:0.82rem;font-weight:600'>{risk}</span></div>", unsafe_allow_html=True)
                    c4.markdown(f"<div style='padding-top:0.5rem;font-size:0.8rem;color:#94A3B8'>Since {cl.get('created_at','')[:10]}</div>", unsafe_allow_html=True)
                    if c5.button("→", key=f"go_cl_{cl['id']}", help="View Portfolios"):
                        st.session_state.selected_client_id = cl["id"]
                        navigate("advisor_portfolio_view")

                    st.markdown('<hr style="border:none;border-top:1px solid #2E3D55;margin:0.4rem 0"/>', unsafe_allow_html=True)

    with tab2:
        st.markdown("#### Link an Existing Client Account")
        st.markdown('<p style="color:#94A3B8;font-size:0.85rem">Ask your client to register with role \'Client\', then link them here using their username.</p>', unsafe_allow_html=True)

        with st.form("link_client_form"):
            client_username = st.text_input("Client Username")
            submit = st.form_submit_button("Link Client", use_container_width=True)
            if submit:
                if not client_username:
                    st.error("Enter a username.")
                else:
                    target = get_user_by_username(client_username)
                    if not target:
                        st.error("No user found with that username.")
                    elif target["role"] != "client":
                        st.error("That user is not a client account.")
                    elif target["id"] == advisor_id:
                        st.error("You cannot link yourself.")
                    else:
                        ok = link_client(advisor_id, target["id"])
                        if ok:
                            st.success(f"Linked {target.get('full_name') or target['username']} successfully!")
                            st.rerun()
                        else:
                            st.error("Client already linked or an error occurred.")
