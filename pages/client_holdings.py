import streamlit as st
from utils.db import (get_client_portfolios, get_portfolio_holdings,
                      add_holding, remove_holding, get_transactions,
                      get_all_assets, get_all_mfs, get_all_prices,
                      get_price, get_mf_by_symbol)
from utils.session import navigate

ASSET_CLASSES = ["Equity", "ETF", "Bond", "Mutual Fund"]

def render():
    if not st.session_state.get("user"):
        navigate("login"); return

    user = st.session_state.user
    client_id = user["id"]
    prices = get_all_prices()

    portfolios = get_client_portfolios(client_id)
    if not portfolios:
        st.warning("No portfolios found.")
        if st.button("Create a Portfolio"):
            navigate("client_portfolios")
        return

    # Portfolio selector
    pf_map = {pf["id"]: pf["name"] for pf in portfolios}
    selected_id = st.session_state.get("selected_portfolio_id")
    default_idx = 0
    if selected_id and selected_id in pf_map:
        default_idx = list(pf_map.keys()).index(selected_id)

    portfolio_id = st.selectbox(
        "Portfolio",
        options=list(pf_map.keys()),
        format_func=lambda x: pf_map[x],
        index=default_idx
    )
    st.session_state.selected_portfolio_id = portfolio_id
    pf_info = next(p for p in portfolios if p["id"] == portfolio_id)

    st.markdown(f'<div class="page-title">📁 {pf_info["name"]}</div>', unsafe_allow_html=True)
    if pf_info.get("goal"):
        st.markdown(f'<div class="page-sub">🎯 Goal: {pf_info["goal"]}  ·  Target: ₹{pf_info.get("target_amount",0):,.0f}  ·  By {pf_info.get("target_date","—")}</div>', unsafe_allow_html=True)

    holdings = get_portfolio_holdings(portfolio_id)

    # Summary
    total_invested = sum(h["quantity"] * h["avg_cost"] for h in holdings)
    total_current = sum(
        h["quantity"] * (prices[h["symbol"]]["close"] if h["symbol"] in prices else h["avg_cost"])
        for h in holdings
    )
    total_pnl = total_current - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Invested", f"₹{total_invested:,.0f}")
    m2.metric("Current Value", f"₹{total_current:,.0f}")
    m3.metric("P&L", f"₹{total_pnl:,.0f}", f"{total_pnl_pct:+.2f}%")
    m4.metric("Holdings Count", len(holdings))

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["  📋 Holdings  ", "  ➕ Add Asset  ", "  📜 Transactions  "])

    with tab1:
        if not holdings:
            st.info("No holdings yet. Use 'Add Asset' to start building this portfolio.")
        else:
            # Allocation by asset class
            from collections import defaultdict
            class_totals = defaultdict(float)
            for h in holdings:
                p = prices.get(h["symbol"])
                cur = p["close"] if p else h["avg_cost"]
                class_totals[h["asset_class"]] += h["quantity"] * cur

            if class_totals:
                st.markdown("**Allocation by Asset Class**")
                alloc_cols = st.columns(len(class_totals))
                for i, (cls, val) in enumerate(class_totals.items()):
                    pct = (val / total_current * 100) if total_current else 0
                    alloc_cols[i].markdown(f"""
                    <div style="text-align:center;padding:0.6rem;background:#1E2738;border:1px solid #2E3D55;border-radius:8px">
                        <div style="font-size:0.75rem;color:#94A3B8">{cls}</div>
                        <div style="font-size:1.1rem;font-weight:600;color:#EDF2F7">{pct:.1f}%</div>
                        <div style="font-size:0.78rem;color:#94A3B8">₹{val:,.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>**Holdings Detail**", unsafe_allow_html=True)
            st.markdown('<div style="background:#1E2738;border:1px solid #2E3D55;border-radius:12px;overflow:hidden">', unsafe_allow_html=True)

            header_cols = st.columns([2.5, 1.2, 1.5, 1.5, 1.5, 2, 0.6])
            for col, label in zip(header_cols, ["Symbol", "Asset", "Qty", "Avg Cost", "LTP", "P&L", "Del"]):
                col.markdown(f"<div style='font-size:0.75rem;color:#94A3B8;font-weight:600;padding:0.5rem 0'>{label}</div>", unsafe_allow_html=True)
            st.markdown('<hr style="border:none;border-top:1px solid #2E3D55;margin:0"/>', unsafe_allow_html=True)

            for h in holdings:
                p = prices.get(h["symbol"])
                cur_price = p["close"] if p else h["avg_cost"]
                chg_pct = p["change_pct"] if p else 0
                h_pnl = (cur_price - h["avg_cost"]) * h["quantity"]
                h_pnl_pct = ((cur_price - h["avg_cost"]) / h["avg_cost"] * 100) if h["avg_cost"] else 0
                pnl_col = "#22C55E" if h_pnl >= 0 else "#EF4444"
                chg_col = "#22C55E" if chg_pct >= 0 else "#EF4444"

                hc = st.columns([2.5, 1.2, 1.5, 1.5, 1.5, 2, 0.6])
                hc[0].markdown(f"<div style='font-weight:600;color:#EDF2F7;font-size:0.9rem'>{h['symbol']}</div>", unsafe_allow_html=True)
                hc[1].markdown(f"<span class='badge badge-{h['asset_class'].lower().replace(' ','')[:6]}'>{h['asset_class'][:3].upper()}</span>", unsafe_allow_html=True)
                hc[2].markdown(f"<div style='font-size:0.88rem'>{h['quantity']:g}</div>", unsafe_allow_html=True)
                hc[3].markdown(f"<div style='font-size:0.88rem'>₹{h['avg_cost']:,.2f}</div>", unsafe_allow_html=True)
                hc[4].markdown(f"<div style='font-size:0.88rem'>₹{cur_price:,.2f}</div><div style='font-size:0.75rem;color:{chg_col}'>{chg_pct:+.2f}%</div>", unsafe_allow_html=True)
                hc[5].markdown(f"<div style='color:{pnl_col};font-weight:600;font-size:0.88rem'>₹{h_pnl:+,.0f}</div><div style='color:{pnl_col};font-size:0.75rem'>{h_pnl_pct:+.1f}%</div>", unsafe_allow_html=True)
                if hc[6].button("🗑", key=f"del_h_{h['id']}"):
                    remove_holding(h["id"])
                    st.rerun()

                st.markdown('<hr style="border:none;border-top:1px solid #1A2030;margin:0"/>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        assets = get_all_assets()
        mfs = get_all_mfs()

        asset_class = st.selectbox("Asset Class", ASSET_CLASSES)

        if asset_class == "Mutual Fund":
            symbols = [m["symbol"] for m in mfs]
            names = {m["symbol"]: f"{m['name']} ({m['fund_house']})" for m in mfs}
        else:
            filtered_assets = [a for a in assets if a["asset_class"] == asset_class]
            symbols = [a["symbol"] for a in filtered_assets]
            names = {a["symbol"]: a["name"] for a in filtered_assets}

        if not symbols:
            st.warning(f"No {asset_class} assets found in database.")
        else:
            with st.form("add_holding_form"):
                symbol = st.selectbox(
                    "Select Asset",
                    symbols,
                    format_func=lambda x: f"{x} — {names.get(x, x)}"
                )
                quantity = st.number_input("Quantity / Units", min_value=0.001, step=0.001, format="%.3f")
                avg_cost = st.number_input("Average Buy Price (₹)", min_value=0.01, step=0.01, format="%.2f")

                # Show current price hint
                if asset_class == "Mutual Fund":
                    mf = get_mf_by_symbol(symbol)
                    if mf and mf["nav"]:
                        st.info(f"Current NAV: ₹{mf['nav']:.2f}  (prev: ₹{mf['prev_nav']:.2f}, {mf['change_pct']:+.2f}%)")
                else:
                    px = prices.get(symbol)
                    if px:
                        st.info(f"Current Price: ₹{px['close']:.2f}  (change today: {px['change_pct']:+.2f}%)")

                submit = st.form_submit_button("Add to Portfolio", use_container_width=True)
                if submit:
                    if quantity <= 0 or avg_cost <= 0:
                        st.error("Quantity and price must be positive.")
                    else:
                        add_holding(portfolio_id, symbol, asset_class, quantity, avg_cost)
                        st.success(f"Added {quantity:g} units of {symbol} at ₹{avg_cost:.2f}")
                        st.rerun()

    with tab3:
        txns = get_transactions(portfolio_id)
        if not txns:
            st.info("No transactions yet.")
        else:
            for t in txns:
                typ_col = "#22C55E" if t["txn_type"] == "BUY" else "#EF4444"
                tc = st.columns([1, 2, 1.5, 1.5, 1.5, 2])
                tc[0].markdown(f"<span style='color:{typ_col};font-weight:600;font-size:0.82rem'>{t['txn_type']}</span>", unsafe_allow_html=True)
                tc[1].markdown(f"<span style='font-size:0.85rem;font-weight:600'>{t['symbol']}</span>", unsafe_allow_html=True)
                tc[2].markdown(f"<span style='font-size:0.82rem'>{t['quantity']:g} units</span>", unsafe_allow_html=True)
                tc[3].markdown(f"<span style='font-size:0.82rem'>@ ₹{t['price']:,.2f}</span>", unsafe_allow_html=True)
                tc[4].markdown(f"<span style='font-size:0.82rem;font-weight:600'>₹{t['amount']:,.0f}</span>", unsafe_allow_html=True)
                tc[5].markdown(f"<span style='font-size:0.78rem;color:#94A3B8'>{str(t['txn_date'])[:16]}</span>", unsafe_allow_html=True)
                st.markdown('<hr style="border:none;border-top:1px solid #2E3D55;margin:0.2rem 0"/>', unsafe_allow_html=True)
