import streamlit as st
from utils.session import navigate
from utils.db import get_indices

def render():
    indices = get_indices()

    # Hero
    st.markdown("""
    <div style="text-align:center; padding: 4rem 0 2.5rem 0;">
        <div style="font-family:'DM Serif Display',serif; font-size:3.5rem; letter-spacing:-0.03em; color:#EDF2F7; line-height:1.1">
            Wealth, Managed<br><em style="color:#3B82F6;">Intelligently.</em>
        </div>
        <p style="color:#94A3B8; font-size:1.05rem; margin-top:1rem; max-width:480px; margin-left:auto; margin-right:auto;">
            Qavi gives advisors and their clients a unified view of every rupee — equities, mutual funds, ETFs, and bonds.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Market index pills
    if indices:
        cols = st.columns(len(indices[:6]))
        for i, idx in enumerate(indices[:6]):
            chg_class = "index-change-pos" if idx["change_pct"] >= 0 else "index-change-neg"
            sign = "▲" if idx["change_pct"] >= 0 else "▼"
            cols[i].markdown(f"""
            <div class="index-pill">
                <div class="index-name">{idx['name']}</div>
                <div class="index-value">{idx['value']:,.0f}</div>
                <div class="{chg_class}">{sign} {abs(idx['change_pct']):.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # CTA buttons
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if st.button("Login", use_container_width=True, key="home_login"):
            navigate("login")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Create Account", use_container_width=True, key="home_register"):
            navigate("register")

    # Features
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:1rem;">
        <div class="qavi-card">
            <div style="font-size:1.5rem; margin-bottom:0.5rem;">📊</div>
            <div class="qavi-card-title">Live Market Data</div>
            <p class="qavi-card-sub">Track Nifty 50, Sensex, mutual fund NAVs, ETFs, and bonds — all in one place.</p>
        </div>
        <div class="qavi-card">
            <div style="font-size:1.5rem; margin-bottom:0.5rem;">💼</div>
            <div class="qavi-card-title">Portfolio Analytics</div>
            <p class="qavi-card-sub">P&L, allocation, XIRR, and visual breakdowns for every client portfolio.</p>
        </div>
        <div class="qavi-card">
            <div style="font-size:1.5rem; margin-bottom:0.5rem;">👥</div>
            <div class="qavi-card-title">Advisor-Client CRM</div>
            <p class="qavi-card-sub">Manage multiple clients, their risk profiles, goals, and portfolios effortlessly.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
