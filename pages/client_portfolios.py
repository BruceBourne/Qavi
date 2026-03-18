import streamlit as st
from utils.db import get_client_portfolios, create_portfolio, get_portfolio_holdings, get_all_prices
from utils.session import navigate
from datetime import date

def render():
    if not st.session_state.get("user"):
        navigate("login"); return

    user = st.session_state.user
    client_id = user["id"]
    prices = get_all_prices()

    st.markdown('<div class="page-title">My Portfolios</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Track and manage your investments</div>', unsafe_allow_html=True)

    portfolios = get_client_portfolios(client_id)

    tab1, tab2 = st.tabs(["  📁 All Portfolios  ", "  ➕ New Portfolio  "])

    with tab1:
        if not portfolios:
            st.info("No portfolios yet. Use the 'New Portfolio' tab to create one.")
        else:
            for pf in portfolios:
                holdings = get_portfolio_holdings(pf["id"])
                pf_invested = sum(h["quantity"] * h["avg_cost"] for h in holdings)
                pf_current = sum(
                    h["quantity"] * (prices[h["symbol"]]["close"] if h["symbol"] in prices else h["avg_cost"])
                    for h in holdings
                )
                pf_pnl = pf_current - pf_invested
                pf_pnl_pct = (pf_pnl / pf_invested * 100) if pf_invested else 0
                pnl_col = "#22C55E" if pf_pnl >= 0 else "#EF4444"

                with st.container():
                    st.markdown(f"""
                    <div class="qavi-card">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start">
                            <div>
                                <div class="qavi-card-title">📁 {pf['name']}</div>
                                <div class="qavi-card-sub">{pf.get('description','')}{(' · 🎯 ' + pf['goal']) if pf.get('goal') else ''}</div>
                            </div>
                            <div style="text-align:right">
                                <div style="font-size:1.1rem;font-weight:600;color:#EDF2F7">₹{pf_current:,.0f}</div>
                                <div style="color:{pnl_col};font-size:0.85rem;font-weight:600">P&L: ₹{pf_pnl:+,.0f} ({pf_pnl_pct:+.1f}%)</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Invested", f"₹{pf_invested:,.0f}")
                    m2.metric("Current Value", f"₹{pf_current:,.0f}")
                    m3.metric("Holdings", len(holdings))
                    if pf.get("target_amount"):
                        progress = min(pf_current / pf["target_amount"], 1.0)
                        m4.metric("Goal Progress", f"{progress*100:.1f}%")
                    else:
                        m4.metric("Created", str(pf.get("created_at",""))[:10])

                    if st.button(f"Open Portfolio →", key=f"open_pf_{pf['id']}", use_container_width=True):
                        st.session_state.selected_portfolio_id = pf["id"]
                        navigate("client_holdings")

    with tab2:
        st.markdown("#### Create a New Portfolio")
        with st.form("new_portfolio_form"):
            name = st.text_input("Portfolio Name *", placeholder="e.g. Retirement Fund, Emergency Corpus")
            description = st.text_input("Description (optional)", placeholder="Brief description")
            goal = st.text_input("Goal (optional)", placeholder="e.g. Retirement by 2045")
            c1, c2 = st.columns(2)
            target_amount = c1.number_input("Target Amount (₹)", min_value=0.0, step=10000.0)
            target_date = c2.date_input("Target Date", value=date.today().replace(year=date.today().year + 10))
            submit = st.form_submit_button("Create Portfolio", use_container_width=True)

            if submit:
                if not name:
                    st.error("Portfolio name is required.")
                else:
                    create_portfolio(
                        client_id, name, description, goal,
                        target_amount, str(target_date)
                    )
                    st.success(f"Portfolio '{name}' created!")
                    st.rerun()
