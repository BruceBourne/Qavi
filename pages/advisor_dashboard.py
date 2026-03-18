import streamlit as st
from utils.db import get_advisor_clients, get_client_portfolios, get_portfolio_holdings, get_all_prices, get_indices
from utils.session import navigate

def render():
    if not st.session_state.get("user"):
        navigate("login"); return
    if st.session_state.user["role"] != "advisor":
        navigate("client_dashboard"); return

    user = st.session_state.user
    name = user.get("full_name") or user["username"]

    # Header
    st.markdown(f'<div class="page-title">Good day, {name.split()[0]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Advisor Overview</div>', unsafe_allow_html=True)

    clients = get_advisor_clients(user["id"])
    prices = get_all_prices()
    indices = get_indices()

    # Top KPIs
    total_aum = 0
    for cl in clients:
        for pf in get_client_portfolios(cl["id"]):
            for h in get_portfolio_holdings(pf["id"]):
                p = prices.get(h["symbol"])
                if p:
                    total_aum += h["quantity"] * p["close"]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Clients", len(clients))
    k2.metric("AUM Under Management", f"₹{total_aum:,.0f}")

    total_pf = sum(len(get_client_portfolios(c["id"])) for c in clients)
    k3.metric("Portfolios", total_pf)

    nifty = next((i for i in indices if i["symbol"] == "NIFTY50"), None)
    if nifty:
        delta_str = f"{nifty['change_pct']:+.2f}%"
        k4.metric("Nifty 50", f"{nifty['value']:,.0f}", delta_str)

    st.markdown("<br>", unsafe_allow_html=True)

    # Index strip
    if indices:
        idx_cols = st.columns(len(indices[:6]))
        for i, idx in enumerate(indices[:6]):
            sign = "▲" if idx["change_pct"] >= 0 else "▼"
            chg_class = "index-change-pos" if idx["change_pct"] >= 0 else "index-change-neg"
            idx_cols[i].markdown(f"""
            <div class="index-pill">
                <div class="index-name">{idx['name']}</div>
                <div class="index-value">{idx['value']:,.0f}</div>
                <div class="{chg_class}">{sign} {abs(idx['change_pct']):.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick actions
    col1, col2, col3 = st.columns(3)
    if col1.button("👥 Manage Clients", use_container_width=True, key="dash_clients"):
        navigate("advisor_clients")
    if col2.button("📁 View Portfolios", use_container_width=True, key="dash_portfolios"):
        navigate("advisor_portfolio_view")
    if col3.button("📊 Market Overview", use_container_width=True, key="dash_market"):
        navigate("market_overview")

    st.markdown("<br>", unsafe_allow_html=True)

    # Client list preview
    if clients:
        st.markdown("### Recent Clients")
        for cl in clients[:5]:
            cl_portfolios = get_client_portfolios(cl["id"])
            cl_aum = 0
            for pf in cl_portfolios:
                for h in get_portfolio_holdings(pf["id"]):
                    p = prices.get(h["symbol"])
                    if p:
                        cl_aum += h["quantity"] * p["close"]

            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            c1.markdown(f"""
            <div>
                <div style="font-weight:600; color:#EDF2F7">{cl.get('full_name') or cl['username']}</div>
                <div style="font-size:0.8rem; color:#94A3B8">@{cl['username']} · {cl.get('risk_profile','Moderate')}</div>
            </div>
            """, unsafe_allow_html=True)
            c2.markdown(f"<div style='padding-top:0.4rem; font-size:0.9rem; color:#94A3B8'>{len(cl_portfolios)} portfolio(s)</div>", unsafe_allow_html=True)
            c3.markdown(f"<div style='padding-top:0.4rem; font-weight:600; color:#EDF2F7'>₹{cl_aum:,.0f}</div>", unsafe_allow_html=True)
            if c4.button("View", key=f"view_cl_{cl['id']}"):
                st.session_state.selected_client_id = cl["id"]
                navigate("advisor_portfolio_view")
    else:
        st.info("No clients yet. Go to **Manage Clients** to add your first client.")
