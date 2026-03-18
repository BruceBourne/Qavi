import streamlit as st
from utils.db import get_all_assets, get_all_prices, get_all_mfs, get_indices
from utils.session import navigate

def render():
    st.markdown('<div class="page-title">Market Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Live prices across all asset classes · India</div>', unsafe_allow_html=True)

    indices = get_indices()
    prices = get_all_prices()
    assets = get_all_assets()
    mfs = get_all_mfs()

    # Index strip
    if indices:
        st.markdown("#### Indices")
        idx_cols = st.columns(min(len(indices), 8))
        for i, idx in enumerate(indices[:8]):
            sign = "▲" if idx["change_pct"] >= 0 else "▼"
            chg_class = "index-change-pos" if idx["change_pct"] >= 0 else "index-change-neg"
            idx_cols[i].markdown(f"""
            <div class="index-pill">
                <div class="index-name">{idx['name']}</div>
                <div class="index-value">{idx['value']:,.2f}</div>
                <div class="{chg_class}">{sign} {abs(idx['change_pct']):.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["  📈 Equities  ", "  🏦 Mutual Funds  ", "  💛 ETFs  ", "  📄 Bonds  "])

    def _price_row(sym, name, asset_class, sector=""):
        p = prices.get(sym, {})
        close = p.get("close", 0)
        chg = p.get("change_pct", 0)
        chg_col = "#22C55E" if chg >= 0 else "#EF4444"
        sign = "▲" if chg >= 0 else "▼"
        open_ = p.get("open", 0)
        high = p.get("high", 0)
        low = p.get("low", 0)

        cols = st.columns([2.5, 2, 1.5, 1.5, 1.5, 1.8, 1.5])
        cols[0].markdown(f"<div style='font-weight:600;color:#EDF2F7;font-size:0.9rem'>{sym}</div><div style='font-size:0.75rem;color:#94A3B8'>{name}</div>", unsafe_allow_html=True)
        cols[1].markdown(f"<div style='font-size:0.78rem;color:#94A3B8'>{sector}</div>", unsafe_allow_html=True)
        cols[2].markdown(f"<div style='font-size:0.88rem'>₹{open_:,.2f}</div><div style='font-size:0.73rem;color:#94A3B8'>Open</div>", unsafe_allow_html=True)
        cols[3].markdown(f"<div style='font-size:0.88rem;color:#22C55E'>₹{high:,.2f}</div><div style='font-size:0.73rem;color:#94A3B8'>High</div>", unsafe_allow_html=True)
        cols[4].markdown(f"<div style='font-size:0.88rem;color:#EF4444'>₹{low:,.2f}</div><div style='font-size:0.73rem;color:#94A3B8'>Low</div>", unsafe_allow_html=True)
        cols[5].markdown(f"<div style='font-size:1rem;font-weight:700;color:#EDF2F7'>₹{close:,.2f}</div>", unsafe_allow_html=True)
        cols[6].markdown(f"<div style='color:{chg_col};font-weight:700;font-size:0.9rem'>{sign} {abs(chg):.2f}%</div>", unsafe_allow_html=True)
        st.markdown('<hr style="border:none;border-top:1px solid #1A2030;margin:0.1rem 0"/>', unsafe_allow_html=True)

    with tab1:
        equities = [a for a in assets if a["asset_class"] == "Equity"]
        # Header
        h_cols = st.columns([2.5, 2, 1.5, 1.5, 1.5, 1.8, 1.5])
        for col, lbl in zip(h_cols, ["Symbol", "Sector", "Open", "High", "Low", "LTP", "Change"]):
            col.markdown(f"<div style='font-size:0.75rem;color:#94A3B8;font-weight:600;padding:0.3rem 0'>{lbl}</div>", unsafe_allow_html=True)
        st.markdown('<hr style="border:none;border-top:1px solid #2E3D55;margin:0 0 0.3rem 0"/>', unsafe_allow_html=True)
        for a in equities:
            _price_row(a["symbol"], a["name"], a["asset_class"], a.get("sector",""))

    with tab2:
        # Header
        mf_cols = st.columns([3, 2, 1.5, 1.5, 1.5, 1.8])
        for col, lbl in zip(mf_cols, ["Fund", "Category", "Sub-Category", "Fund House", "NAV", "Change"]):
            col.markdown(f"<div style='font-size:0.75rem;color:#94A3B8;font-weight:600;padding:0.3rem 0'>{lbl}</div>", unsafe_allow_html=True)
        st.markdown('<hr style="border:none;border-top:1px solid #2E3D55;margin:0 0 0.3rem 0"/>', unsafe_allow_html=True)

        for mf in mfs:
            chg = mf.get("change_pct", 0)
            chg_col = "#22C55E" if chg >= 0 else "#EF4444"
            sign = "▲" if chg >= 0 else "▼"
            c = st.columns([3, 2, 1.5, 1.5, 1.8, 1.5])
            c[0].markdown(f"<div style='font-weight:600;color:#EDF2F7;font-size:0.88rem'>{mf['name']}</div>", unsafe_allow_html=True)
            c[1].markdown(f"<span class='badge badge-mf'>{mf.get('category','—')}</span>", unsafe_allow_html=True)
            c[2].markdown(f"<div style='font-size:0.78rem;color:#94A3B8'>{mf.get('sub_category','—')}</div>", unsafe_allow_html=True)
            c[3].markdown(f"<div style='font-size:0.78rem;color:#94A3B8'>{mf.get('fund_house','—')}</div>", unsafe_allow_html=True)
            c[4].markdown(f"<div style='font-size:0.95rem;font-weight:700;color:#EDF2F7'>₹{mf.get('nav',0):,.2f}</div>", unsafe_allow_html=True)
            c[5].markdown(f"<div style='color:{chg_col};font-weight:700;font-size:0.9rem'>{sign} {abs(chg):.2f}%</div>", unsafe_allow_html=True)
            st.markdown('<hr style="border:none;border-top:1px solid #1A2030;margin:0.1rem 0"/>', unsafe_allow_html=True)

    with tab3:
        etfs = [a for a in assets if a["asset_class"] == "ETF"]
        h_cols = st.columns([2.5, 2, 1.5, 1.5, 1.5, 1.8, 1.5])
        for col, lbl in zip(h_cols, ["Symbol", "Type", "Open", "High", "Low", "LTP", "Change"]):
            col.markdown(f"<div style='font-size:0.75rem;color:#94A3B8;font-weight:600;padding:0.3rem 0'>{lbl}</div>", unsafe_allow_html=True)
        st.markdown('<hr style="border:none;border-top:1px solid #2E3D55;margin:0 0 0.3rem 0"/>', unsafe_allow_html=True)
        for a in etfs:
            _price_row(a["symbol"], a["name"], a["asset_class"], a.get("sector",""))

    with tab4:
        bonds = [a for a in assets if a["asset_class"] == "Bond"]
        h_cols = st.columns([2.5, 2, 1.5, 1.5, 1.5, 1.8, 1.5])
        for col, lbl in zip(h_cols, ["Symbol", "Type", "Open", "High", "Low", "Price", "Change"]):
            col.markdown(f"<div style='font-size:0.75rem;color:#94A3B8;font-weight:600;padding:0.3rem 0'>{lbl}</div>", unsafe_allow_html=True)
        st.markdown('<hr style="border:none;border-top:1px solid #2E3D55;margin:0 0 0.3rem 0"/>', unsafe_allow_html=True)
        for a in bonds:
            _price_row(a["symbol"], a["name"], a["asset_class"], a.get("sector",""))
