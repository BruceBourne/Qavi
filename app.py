import streamlit as st
st.set_page_config(
    page_title="Qavi Wealth",
    page_icon="₹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from utils.db import init_databases
from utils.session import init_session
from utils.styles import inject_styles
import pages.home as home
import pages.login as login
import pages.register as register
import pages.advisor_dashboard as advisor_dash
import pages.advisor_clients as advisor_clients
import pages.advisor_portfolio_view as advisor_portfolio_view
import pages.client_dashboard as client_dashboard
import pages.client_portfolios as client_portfolios
import pages.client_holdings as client_holdings
import pages.market_overview as market_overview
import pages.profile as profile

# Boot
init_databases()
init_session()
inject_styles()

# Navigation bar (shown when logged in)
if st.session_state.get("user"):
    user = st.session_state.user
    role = user["role"]

    with st.container():
        nav_cols = st.columns([2, 1, 1, 1, 1, 1, 0.8])
        nav_cols[0].markdown('<span class="nav-brand">◈ Qavi</span>', unsafe_allow_html=True)

        if nav_cols[1].button("🏠 Home", key="nav_home", use_container_width=True):
            st.session_state.page = "advisor_dashboard" if role == "advisor" else "client_dashboard"
            st.rerun()

        if nav_cols[2].button("📊 Markets", key="nav_markets", use_container_width=True):
            st.session_state.page = "market_overview"
            st.rerun()

        if role == "advisor":
            if nav_cols[3].button("👥 Clients", key="nav_clients", use_container_width=True):
                st.session_state.page = "advisor_clients"
                st.rerun()
        else:
            if nav_cols[3].button("💼 Portfolios", key="nav_portfolios", use_container_width=True):
                st.session_state.page = "client_portfolios"
                st.rerun()

        if nav_cols[4].button("👤 Profile", key="nav_profile", use_container_width=True):
            st.session_state.page = "profile"
            st.rerun()

        if nav_cols[5].button("⬅ Back", key="nav_back", use_container_width=True):
            if st.session_state.get("page_history"):
                st.session_state.page_history.pop()
                if st.session_state.page_history:
                    st.session_state.page = st.session_state.page_history[-1]
                else:
                    st.session_state.page = "advisor_dashboard" if role == "advisor" else "client_dashboard"
                st.rerun()

        if nav_cols[6].button("Logout", key="nav_logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "home"
            st.session_state.page_history = []
            st.rerun()

        st.markdown('<hr class="nav-divider"/>', unsafe_allow_html=True)

# Router
page = st.session_state.get("page", "home")

PAGES = {
    "home": home,
    "login": login,
    "register": register,
    "advisor_dashboard": advisor_dash,
    "advisor_clients": advisor_clients,
    "advisor_portfolio_view": advisor_portfolio_view,
    "client_dashboard": client_dashboard,
    "client_portfolios": client_portfolios,
    "client_holdings": client_holdings,
    "market_overview": market_overview,
    "profile": profile,
}

module = PAGES.get(page, home)
module.render()
