import streamlit as st
from utils.db import get_client_portfolios, get_portfolio_holdings, get_all_prices, get_indices
from utils.session import navigate

def render():
    if not st.session_state.get("user"):
        navigate("login"); return
    if st.session_state.user["role"] != "client":
        navigate("advisor_dashboard"); return

    user = st.session_state.user
    name = user.get("full_name") or user["username"]
    prices = get_all_prices()
    indices = get_indices()
    portfolios = get_client_portfolios(user["id"])

    st.markdown(f'<div class="page-title">Hello, {name.split()[0]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Your investment overview</div>', unsafe_allow_html=True)

    # Aggregate
    total_invested = 0
    total_current = 0
    total_holdings = 0
    for pf in portfolios:
        for h in get_portfolio_holdings(pf["id"]):
            p = prices.get(h["symbol"])
            cur = p["close"] if p else h["avg_cost"]
            total_invested += h["quantity"] * h["avg_cost"]
            total_current += h["quantity"] * cur
            total_holdings += 1

    total_pnl = total_current - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested else 0
    pnl_delta = f"{total_pnl_pct:+.2f}%"

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Invested", f"₹{total_invested:,.0f}")
    k2.metric("Portfolio Value", f"₹{total_current:,.0f}")
    k3.metric("Overall P&L", f"₹{total_pnl:,.0f}", pnl_delta)
    k4.metric("Portfolios", len(portfolios))

    st.markdown("<br>", unsafe_allow_html=True)

    # Index pills
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

    col1, col2, col3 = st.columns(3)
    if col1.button("💼 My Portfolios", use_container_width=True, key="cd_pf"):
        navigate("client_portfolios")
    if col2.button("📊 Market Overview", use_container_width=True, key="cd_mkt"):
        navigate("market_overview")
    if col3.button("👤 My Profile", use_container_width=True, key="cd_profile"):
        navigate("profile")

    st.markdown("<br>", unsafe_allow_html=True)

    # Portfolio summary cards
    if portfolios:
        st.markdown("### Your Portfolios")
        for pf in portfolios:
            holdings = get_portfolio_holdings(pf["id"])
            pf_invested = 0
            pf_current = 0
            for h in holdings:
                p = prices.get(h["symbol"])
                cur = p["close"] if p else h["avg_cost"]
                pf_invested += h["quantity"] * h["avg_cost"]
                pf_current += h["quantity"] * cur
            pf_pnl = pf_current - pf_invested
            pf_pnl_pct = (pf_pnl / pf_invested * 100) if pf_invested else 0
            pnl_col = "#22C55E" if pf_pnl >= 0 else "#EF4444"

            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            c1.markdown(f"""
            <div>
                <div style="font-weight:600;color:#EDF2F7">📁 {pf['name']}</div>
                <div style="font-size:0.78rem;color:#94A3B8">{len(holdings)} holding(s){(' · 🎯 ' + pf['goal']) if pf.get('goal') else ''}</div>
            </div>
            """, unsafe_allow_html=True)
            c2.markdown(f"<div style='padding-top:0.4rem;font-size:0.9rem'>₹{pf_current:,.0f}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div style='padding-top:0.4rem;color:{pnl_col};font-weight:600'>₹{pf_pnl:+,.0f} ({pf_pnl_pct:+.1f}%)</div>", unsafe_allow_html=True)
            if c4.button("→", key=f"go_pf_{pf['id']}"):
                st.session_state.selected_portfolio_id = pf["id"]
                navigate("client_holdings")

            st.markdown('<hr style="border:none;border-top:1px solid #2E3D55;margin:0.3rem 0"/>', unsafe_allow_html=True)
    else:
        st.info("No portfolios yet. Head to **My Portfolios** to create one.")
