import streamlit as st
from utils.db import (get_advisor_clients, get_client_portfolios,
                      get_portfolio_holdings, get_transactions,
                      get_all_prices, get_mf_by_symbol)
from utils.session import navigate

def calc_portfolio_stats(holdings, prices):
    total_invested = 0
    current_value = 0
    for h in holdings:
        invested = h["quantity"] * h["avg_cost"]
        p = prices.get(h["symbol"])
        cur_price = p["close"] if p else h["avg_cost"]
        current = h["quantity"] * cur_price
        total_invested += invested
        current_value += current
    pnl = current_value - total_invested
    pnl_pct = (pnl / total_invested * 100) if total_invested else 0
    return total_invested, current_value, pnl, pnl_pct

def render():
    if not st.session_state.get("user"):
        navigate("login"); return

    user = st.session_state.user
    advisor_id = user["id"]
    prices = get_all_prices()

    st.markdown('<div class="page-title">Client Portfolios</div>', unsafe_allow_html=True)

    clients = get_advisor_clients(advisor_id)
    if not clients:
        st.info("No clients linked yet.")
        if st.button("← Go Back"):
            navigate("advisor_dashboard")
        return

    # Client selector
    selected_id = st.session_state.get("selected_client_id")
    client_names = {c["id"]: (c.get("full_name") or c["username"]) for c in clients}
    default_idx = 0
    if selected_id and selected_id in client_names:
        default_idx = list(client_names.keys()).index(selected_id)

    chosen = st.selectbox(
        "Select Client",
        options=list(client_names.keys()),
        format_func=lambda x: client_names[x],
        index=default_idx
    )
    st.session_state.selected_client_id = chosen

    client_info = next(c for c in clients if c["id"] == chosen)
    portfolios = get_client_portfolios(chosen)

    # Client summary
    st.markdown(f"""
    <div class="qavi-card" style="margin-bottom:1.5rem">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
                <div class="qavi-card-title">{client_info.get('full_name') or client_info['username']}</div>
                <div class="qavi-card-sub">{client_info.get('email','No email')} · Risk: {client_info.get('risk_profile','Moderate')}</div>
            </div>
            <div style="font-size:0.85rem;color:#94A3B8">{len(portfolios)} portfolio(s)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not portfolios:
        st.info("This client has no portfolios yet.")
        return

    for pf in portfolios:
        holdings = get_portfolio_holdings(pf["id"])
        invested, current, pnl, pnl_pct = calc_portfolio_stats(holdings, prices)
        sign = "▲" if pnl >= 0 else "▼"
        pnl_col = "#22C55E" if pnl >= 0 else "#EF4444"

        with st.expander(f"📁 {pf['name']}  —  ₹{current:,.0f}", expanded=True):
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Invested", f"₹{invested:,.0f}")
            m2.metric("Current Value", f"₹{current:,.0f}")
            m3.metric("P&L", f"₹{pnl:,.0f}", f"{pnl_pct:+.2f}%")
            m4.metric("Holdings", len(holdings))

            if pf.get("goal"):
                st.markdown(f'<p style="font-size:0.82rem;color:#94A3B8">🎯 Goal: {pf["goal"]}  |  Target: ₹{pf.get("target_amount",0):,.0f}  |  By: {pf.get("target_date","—")}</p>', unsafe_allow_html=True)

            if holdings:
                st.markdown("**Holdings**")
                for h in holdings:
                    p = prices.get(h["symbol"])
                    cur_price = p["close"] if p else h["avg_cost"]
                    chg_pct = p["change_pct"] if p else 0
                    h_pnl = (cur_price - h["avg_cost"]) * h["quantity"]
                    h_pnl_pct = ((cur_price - h["avg_cost"]) / h["avg_cost"] * 100) if h["avg_cost"] else 0
                    chg_class = "change-positive" if chg_pct >= 0 else "change-negative"

                    hc1, hc2, hc3, hc4, hc5 = st.columns([2, 1.5, 1.5, 1.5, 2])
                    hc1.markdown(f"<div style='font-weight:600;color:#EDF2F7'>{h['symbol']}</div><div style='font-size:0.78rem;color:#94A3B8'>{h['asset_class']}</div>", unsafe_allow_html=True)
                    hc2.markdown(f"<div style='font-size:0.88rem'>Qty: {h['quantity']:g}</div>", unsafe_allow_html=True)
                    hc3.markdown(f"<div style='font-size:0.88rem'>Avg: ₹{h['avg_cost']:,.2f}</div>", unsafe_allow_html=True)
                    hc4.markdown(f"<div style='font-size:0.88rem'>LTP: ₹{cur_price:,.2f}</div><div class='{chg_class}' style='font-size:0.78rem'>{chg_pct:+.2f}% today</div>", unsafe_allow_html=True)
                    pnl_c = "#22C55E" if h_pnl >= 0 else "#EF4444"
                    hc5.markdown(f"<div style='color:{pnl_c};font-weight:600'>₹{h_pnl:+,.0f} ({h_pnl_pct:+.1f}%)</div>", unsafe_allow_html=True)

                st.markdown('<hr style="border:none;border-top:1px solid #2E3D55;margin:0.3rem 0"/>', unsafe_allow_html=True)

            # Transactions preview
            txns = get_transactions(pf["id"])
            if txns:
                st.markdown("**Recent Transactions**")
                for t in txns[:5]:
                    tc1, tc2, tc3, tc4 = st.columns([1.5, 2, 2, 2])
                    typ_col = "#22C55E" if t["txn_type"] == "BUY" else "#EF4444"
                    tc1.markdown(f"<span style='color:{typ_col};font-weight:600;font-size:0.82rem'>{t['txn_type']}</span>", unsafe_allow_html=True)
                    tc2.markdown(f"<span style='font-size:0.82rem'>{t['symbol']}</span>", unsafe_allow_html=True)
                    tc3.markdown(f"<span style='font-size:0.82rem'>₹{t['amount']:,.0f}</span>", unsafe_allow_html=True)
                    tc4.markdown(f"<span style='font-size:0.78rem;color:#94A3B8'>{str(t['txn_date'])[:10]}</span>", unsafe_allow_html=True)
