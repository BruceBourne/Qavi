import sqlite3
import os
import pandas as pd
import requests
from datetime import datetime, date
import threading

USER_DB = "qavi_users.db"
MARKET_DB = "qavi_market.db"

# Thread-local connections
_local = threading.local()

def get_user_conn():
    if not hasattr(_local, "user_conn") or _local.user_conn is None:
        _local.user_conn = sqlite3.connect(USER_DB, check_same_thread=False)
        _local.user_conn.row_factory = sqlite3.Row
    return _local.user_conn

def get_market_conn():
    if not hasattr(_local, "market_conn") or _local.market_conn is None:
        _local.market_conn = sqlite3.connect(MARKET_DB, check_same_thread=False)
        _local.market_conn.row_factory = sqlite3.Row
    return _local.market_conn

# -------------------------------------------------------
# SCHEMA SETUP
# -------------------------------------------------------

def init_databases():
    _init_user_db()
    _init_market_db()
    _seed_market_data()

def _init_user_db():
    conn = get_user_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('advisor','client')),
        full_name TEXT DEFAULT '',
        email TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        pan TEXT DEFAULT '',
        risk_profile TEXT DEFAULT 'Moderate',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS advisor_clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        advisor_id INTEGER NOT NULL,
        client_id INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(advisor_id) REFERENCES users(id),
        FOREIGN KEY(client_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS portfolios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        goal TEXT DEFAULT '',
        target_amount REAL DEFAULT 0,
        target_date TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(client_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS holdings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        portfolio_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        asset_class TEXT NOT NULL,
        quantity REAL NOT NULL,
        avg_cost REAL DEFAULT 0,
        buy_date TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(portfolio_id) REFERENCES portfolios(id)
    );

    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        portfolio_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        txn_type TEXT NOT NULL CHECK(txn_type IN ('BUY','SELL','DIVIDEND','SIP')),
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        amount REAL NOT NULL,
        txn_date TEXT DEFAULT CURRENT_TIMESTAMP,
        notes TEXT DEFAULT '',
        FOREIGN KEY(portfolio_id) REFERENCES portfolios(id)
    );
    """)
    conn.commit()

def _init_market_db():
    conn = get_market_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        asset_class TEXT NOT NULL,
        sector TEXT DEFAULT '',
        exchange TEXT DEFAULT 'NSE',
        isin TEXT DEFAULT '',
        face_value REAL DEFAULT 10,
        last_updated TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        price DATE DEFAULT CURRENT_DATE,
        open REAL DEFAULT 0,
        high REAL DEFAULT 0,
        low REAL DEFAULT 0,
        close REAL NOT NULL,
        prev_close REAL DEFAULT 0,
        change_pct REAL DEFAULT 0,
        volume INTEGER DEFAULT 0,
        market_cap REAL DEFAULT 0,
        last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(symbol, price)
    );

    CREATE TABLE IF NOT EXISTS mutual_funds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_code TEXT UNIQUE NOT NULL,
        symbol TEXT NOT NULL,
        name TEXT NOT NULL,
        fund_house TEXT DEFAULT '',
        category TEXT DEFAULT '',
        sub_category TEXT DEFAULT '',
        nav REAL DEFAULT 0,
        prev_nav REAL DEFAULT 0,
        change_pct REAL DEFAULT 0,
        aum REAL DEFAULT 0,
        expense_ratio REAL DEFAULT 0,
        last_updated TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS indices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        value REAL DEFAULT 0,
        prev_value REAL DEFAULT 0,
        change_pct REAL DEFAULT 0,
        last_updated TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()

# -------------------------------------------------------
# SEED STATIC MARKET DATA (fallback / demo)
# -------------------------------------------------------

SEED_EQUITIES = [
    # Large Cap
    ("RELIANCE","Reliance Industries","Equity","Energy","NSE"),
    ("INFY","Infosys Ltd","Equity","IT","NSE"),
    ("TCS","Tata Consultancy Services","Equity","IT","NSE"),
    ("HDFCBANK","HDFC Bank Ltd","Equity","Banking","NSE"),
    ("ICICIBANK","ICICI Bank Ltd","Equity","Banking","NSE"),
    ("KOTAKBANK","Kotak Mahindra Bank","Equity","Banking","NSE"),
    ("HINDUNILVR","Hindustan Unilever","Equity","FMCG","NSE"),
    ("ITC","ITC Ltd","Equity","FMCG","NSE"),
    ("BHARTIARTL","Bharti Airtel","Equity","Telecom","NSE"),
    ("AXISBANK","Axis Bank Ltd","Equity","Banking","NSE"),
    ("LT","Larsen & Toubro","Equity","Capital Goods","NSE"),
    ("WIPRO","Wipro Ltd","Equity","IT","NSE"),
    ("BAJFINANCE","Bajaj Finance","Equity","NBFC","NSE"),
    ("MARUTI","Maruti Suzuki","Equity","Auto","NSE"),
    ("TITAN","Titan Company","Equity","Consumer","NSE"),
    ("ASIANPAINT","Asian Paints","Equity","Paint","NSE"),
    ("NESTLEIND","Nestle India","Equity","FMCG","NSE"),
    ("ULTRACEMCO","UltraTech Cement","Equity","Cement","NSE"),
    ("SUNPHARMA","Sun Pharmaceutical","Equity","Pharma","NSE"),
    ("DRREDDY","Dr Reddy's Labs","Equity","Pharma","NSE"),
]

SEED_ETFS = [
    ("NIFTYBEES","Nippon Nifty BeES","ETF","Index ETF","NSE"),
    ("GOLDBEES","Nippon Gold BeES","ETF","Gold ETF","NSE"),
    ("BANKBEES","Nippon Bank BeES","ETF","Sectoral ETF","NSE"),
    ("JUNIORBEES","Nippon Junior BeES","ETF","Index ETF","NSE"),
    ("ICICIB22","ICICI Bharat 22 ETF","ETF","Index ETF","NSE"),
    ("LIQUIDBEES","Nippon Liquid BeES","ETF","Liquid ETF","NSE"),
    ("ITBEES","Nippon IT BeES","ETF","Sectoral ETF","NSE"),
    ("SETFNIF50","SBI ETF Nifty 50","ETF","Index ETF","NSE"),
    ("MOM100","Motilal Nifty Midcap 100","ETF","Index ETF","NSE"),
    ("SILVERBEES","Nippon Silver BeES","ETF","Commodity ETF","NSE"),
]

SEED_BONDS = [
    ("GSEC_10Y","10-Year G-Sec Bond","Bond","Government","BSE"),
    ("GSEC_5Y","5-Year G-Sec Bond","Bond","Government","BSE"),
    ("NHAI_BOND","NHAI Infrastructure Bond","Bond","PSU","BSE"),
    ("REC_BOND","REC Tax-Free Bond","Bond","PSU","BSE"),
    ("HDFC_NCD","HDFC NCD Series","Bond","Corporate","BSE"),
    ("BAJAJ_NCD","Bajaj Finance NCD","Bond","Corporate","BSE"),
    ("TATA_NCD","Tata Capital NCD","Bond","Corporate","BSE"),
    ("SGB_2028","Sovereign Gold Bond 2028","Bond","Gold Bond","BSE"),
    ("SGB_2030","Sovereign Gold Bond 2030","Bond","Gold Bond","BSE"),
    ("IRFC_BOND","IRFC Tax-Free Bond","Bond","PSU","BSE"),
]

SEED_MFS = [
    ("120503","HDFC_TOP100","HDFC Top 100 Fund","HDFC AMC","Equity","Large Cap"),
    ("100119","SBI_BLUECHIP","SBI Bluechip Fund","SBI MF","Equity","Large Cap"),
    ("118989","AXIS_MIDCAP","Axis Midcap Fund","Axis MF","Equity","Mid Cap"),
    ("100341","MIRAE_EMERGING","Mirae Emerging Bluechip","Mirae Asset","Equity","Large & Mid Cap"),
    ("122639","PARAG_FLEXI","Parag Parikh Flexi Cap","PPFAS MF","Equity","Flexi Cap"),
    ("119598","ICICI_BLUECHIP","ICICI Pru Bluechip","ICICI MF","Equity","Large Cap"),
    ("119062","KOTAK_SMALLCAP","Kotak Small Cap Fund","Kotak MF","Equity","Small Cap"),
    ("100444","DSP_MIDCAP","DSP Midcap Fund","DSP MF","Equity","Mid Cap"),
    ("106655","NIPPON_SMALLCAP","Nippon Small Cap Fund","Nippon MF","Equity","Small Cap"),
    ("100270","FRANKLIN_PRIMA","Franklin India Prima Fund","Franklin MF","Equity","Mid Cap"),
    ("120505","HDFC_LIQUID","HDFC Liquid Fund","HDFC AMC","Debt","Liquid"),
    ("119551","ICICI_LIQUID","ICICI Pru Liquid Fund","ICICI MF","Debt","Liquid"),
    ("100595","AXIS_ELSS","Axis Long Term Equity","Axis MF","ELSS","Tax Saver"),
    ("100122","SBI_ELSS","SBI Long Term Equity","SBI MF","ELSS","Tax Saver"),
    ("135781","ICICI_BALANCED","ICICI Pru Balanced Advantage","ICICI MF","Hybrid","BAF"),
]

SEED_INDICES = [
    ("NIFTY50","Nifty 50",22500,22100),
    ("SENSEX","BSE Sensex",74000,72800),
    ("NIFTYBANK","Nifty Bank",48000,47200),
    ("NIFTYMIDCAP","Nifty Midcap 100",52000,51200),
    ("NIFTYSMALLCAP","Nifty Smallcap 100",15000,14700),
    ("NIFTYIT","Nifty IT",34000,33500),
    ("NIFTYPHARMA","Nifty Pharma",18500,18200),
    ("INDIA_VIX","India VIX",14.5,15.2),
]

# Demo prices for equities
DEMO_PRICES = {
    "RELIANCE": (2940, 2910, 2880, 2930, 2900),
    "INFY": (1820, 1800, 1780, 1815, 1790),
    "TCS": (4220, 4180, 4160, 4210, 4170),
    "HDFCBANK": (1680, 1660, 1645, 1675, 1658),
    "ICICIBANK": (1250, 1235, 1220, 1248, 1232),
    "KOTAKBANK": (1760, 1740, 1720, 1755, 1738),
    "HINDUNILVR": (2720, 2695, 2680, 2715, 2692),
    "ITC": (475, 470, 465, 474, 469),
    "BHARTIARTL": (1580, 1560, 1545, 1575, 1558),
    "AXISBANK": (1155, 1140, 1125, 1150, 1138),
    "LT": (3620, 3590, 3565, 3615, 3588),
    "WIPRO": (562, 556, 550, 560, 554),
    "BAJFINANCE": (6820, 6760, 6710, 6810, 6752),
    "MARUTI": (12500, 12380, 12280, 12480, 12360),
    "TITAN": (3580, 3545, 3515, 3572, 3540),
    "ASIANPAINT": (2840, 2810, 2785, 2835, 2805),
    "NESTLEIND": (2480, 2455, 2435, 2475, 2450),
    "ULTRACEMCO": (10850, 10720, 10620, 10830, 10700),
    "SUNPHARMA": (1680, 1660, 1643, 1676, 1657),
    "DRREDDY": (1320, 1305, 1290, 1316, 1302),
    "NIFTYBEES": (248, 245, 242, 247, 244),
    "GOLDBEES": (56.8, 56.2, 55.8, 56.6, 56.1),
    "BANKBEES": (485, 480, 474, 483, 478),
    "JUNIORBEES": (752, 744, 737, 749, 742),
    "ICICIB22": (98.5, 97.8, 97.1, 98.3, 97.6),
    "LIQUIDBEES": (1000, 1000, 1000, 1000, 1000),
    "ITBEES": (340, 336, 332, 339, 335),
    "SETFNIF50": (248, 245, 242, 247, 244),
    "MOM100": (81, 80, 79, 81, 80),
    "SILVERBEES": (87, 86, 85, 87, 86),
    "GSEC_10Y": (100.5, 100.3, 100.1, 100.4, 100.2),
    "GSEC_5Y": (101.2, 101.0, 100.8, 101.1, 100.9),
    "NHAI_BOND": (1050, 1048, 1046, 1049, 1047),
    "REC_BOND": (1080, 1078, 1075, 1079, 1077),
    "HDFC_NCD": (1005, 1003, 1001, 1004, 1002),
    "BAJAJ_NCD": (1010, 1008, 1006, 1009, 1007),
    "TATA_NCD": (1008, 1006, 1004, 1007, 1005),
    "SGB_2028": (7250, 7200, 7160, 7240, 7190),
    "SGB_2030": (7450, 7400, 7360, 7440, 7390),
    "IRFC_BOND": (1020, 1018, 1016, 1019, 1017),
}

DEMO_NAV = {
    "HDFC_TOP100": (850, 842),
    "SBI_BLUECHIP": (72, 71.2),
    "AXIS_MIDCAP": (95, 93.8),
    "MIRAE_EMERGING": (115, 113.5),
    "PARAG_FLEXI": (68, 67.1),
    "ICICI_BLUECHIP": (88, 87.2),
    "KOTAK_SMALLCAP": (220, 217),
    "DSP_MIDCAP": (118, 116.5),
    "NIPPON_SMALLCAP": (165, 162.5),
    "FRANKLIN_PRIMA": (1850, 1825),
    "HDFC_LIQUID": (4250, 4248),
    "ICICI_LIQUID": (380, 379.8),
    "AXIS_ELSS": (92, 90.8),
    "SBI_ELSS": (310, 305.5),
    "ICICI_BALANCED": (62, 61.2),
}

def _seed_market_data():
    conn = get_market_conn()
    c = conn.cursor()
    today = str(date.today())

    # Assets
    for sym, name, cls, sector, exch in SEED_EQUITIES + SEED_ETFS + SEED_BONDS:
        c.execute("""
            INSERT OR IGNORE INTO assets(symbol,name,asset_class,sector,exchange)
            VALUES(?,?,?,?,?)
        """, (sym, name, cls, sector, exch))

    # Prices
    for sym, (open_, high, low, close, prev) in DEMO_PRICES.items():
        chg = round(((close - prev) / prev) * 100, 2)
        c.execute("""
            INSERT OR REPLACE INTO prices(symbol,price,open,high,low,close,prev_close,change_pct,last_updated)
            VALUES(?,?,?,?,?,?,?,?,?)
        """, (sym, today, open_, high, low, close, prev, chg, datetime.now().isoformat()))

    # Mutual Funds
    for code, sym, name, house, cat, subcat in SEED_MFS:
        c.execute("""
            INSERT OR IGNORE INTO mutual_funds(scheme_code,symbol,name,fund_house,category,sub_category)
            VALUES(?,?,?,?,?,?)
        """, (code, sym, name, house, cat, subcat))
        if sym in DEMO_NAV:
            nav, prev_nav = DEMO_NAV[sym]
            chg = round(((nav - prev_nav) / prev_nav) * 100, 2)
            c.execute("""
                UPDATE mutual_funds SET nav=?, prev_nav=?, change_pct=?, last_updated=?
                WHERE symbol=?
            """, (nav, prev_nav, chg, datetime.now().isoformat(), sym))

    # Indices
    for sym, name, val, prev in SEED_INDICES:
        chg = round(((val - prev) / prev) * 100, 2)
        c.execute("""
            INSERT OR REPLACE INTO indices(symbol,name,value,prev_value,change_pct,last_updated)
            VALUES(?,?,?,?,?,?)
        """, (sym, name, val, prev, chg, datetime.now().isoformat()))

    conn.commit()

# -------------------------------------------------------
# HELPER QUERIES
# -------------------------------------------------------

def get_user_by_username(username):
    conn = get_user_conn()
    row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    return dict(row) if row else None

def get_user_by_id(uid):
    conn = get_user_conn()
    row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    return dict(row) if row else None

def create_user(username, password, role, full_name="", email=""):
    conn = get_user_conn()
    try:
        conn.execute("""
            INSERT INTO users(username,password,role,full_name,email)
            VALUES(?,?,?,?,?)
        """, (username, password, role, full_name, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def update_user_profile(uid, full_name, email, phone, pan, risk_profile):
    conn = get_user_conn()
    conn.execute("""
        UPDATE users SET full_name=?, email=?, phone=?, pan=?, risk_profile=?
        WHERE id=?
    """, (full_name, email, phone, pan, risk_profile, uid))
    conn.commit()

def get_advisor_clients(advisor_id):
    conn = get_user_conn()
    rows = conn.execute("""
        SELECT u.id, u.username, u.full_name, u.email, u.risk_profile, ac.created_at
        FROM advisor_clients ac
        JOIN users u ON ac.client_id = u.id
        WHERE ac.advisor_id=?
    """, (advisor_id,)).fetchall()
    return [dict(r) for r in rows]

def link_client(advisor_id, client_id):
    conn = get_user_conn()
    try:
        conn.execute("INSERT INTO advisor_clients(advisor_id,client_id) VALUES(?,?)",
                     (advisor_id, client_id))
        conn.commit()
        return True
    except:
        return False

def get_client_portfolios(client_id):
    conn = get_user_conn()
    rows = conn.execute("SELECT * FROM portfolios WHERE client_id=?", (client_id,)).fetchall()
    return [dict(r) for r in rows]

def create_portfolio(client_id, name, description="", goal="", target_amount=0, target_date=""):
    conn = get_user_conn()
    conn.execute("""
        INSERT INTO portfolios(client_id,name,description,goal,target_amount,target_date)
        VALUES(?,?,?,?,?,?)
    """, (client_id, name, description, goal, target_amount, target_date))
    conn.commit()

def get_portfolio_holdings(portfolio_id):
    conn = get_user_conn()
    rows = conn.execute("SELECT * FROM holdings WHERE portfolio_id=?", (portfolio_id,)).fetchall()
    return [dict(r) for r in rows]

def add_holding(portfolio_id, symbol, asset_class, quantity, avg_cost):
    conn = get_user_conn()
    # Check if holding exists — update quantity
    existing = conn.execute(
        "SELECT id, quantity, avg_cost FROM holdings WHERE portfolio_id=? AND symbol=?",
        (portfolio_id, symbol)
    ).fetchone()
    if existing:
        old_qty = existing["quantity"]
        old_cost = existing["avg_cost"]
        new_qty = old_qty + quantity
        new_avg = ((old_qty * old_cost) + (quantity * avg_cost)) / new_qty
        conn.execute(
            "UPDATE holdings SET quantity=?, avg_cost=? WHERE id=?",
            (new_qty, new_avg, existing["id"])
        )
    else:
        conn.execute("""
            INSERT INTO holdings(portfolio_id,symbol,asset_class,quantity,avg_cost)
            VALUES(?,?,?,?,?)
        """, (portfolio_id, symbol, asset_class, quantity, avg_cost))
    # Log transaction
    conn.execute("""
        INSERT INTO transactions(portfolio_id,symbol,txn_type,quantity,price,amount)
        VALUES(?,?,?,?,?,?)
    """, (portfolio_id, symbol, "BUY", quantity, avg_cost, quantity * avg_cost))
    conn.commit()

def remove_holding(holding_id):
    conn = get_user_conn()
    conn.execute("DELETE FROM holdings WHERE id=?", (holding_id,))
    conn.commit()

def get_transactions(portfolio_id):
    conn = get_user_conn()
    rows = conn.execute(
        "SELECT * FROM transactions WHERE portfolio_id=? ORDER BY txn_date DESC",
        (portfolio_id,)
    ).fetchall()
    return [dict(r) for r in rows]

# Market helpers
def get_all_assets():
    conn = get_market_conn()
    rows = conn.execute("SELECT a.*, p.close, p.change_pct FROM assets a LEFT JOIN prices p ON a.symbol=p.symbol").fetchall()
    return [dict(r) for r in rows]

def get_price(symbol):
    conn = get_market_conn()
    row = conn.execute("SELECT * FROM prices WHERE symbol=? ORDER BY price DESC LIMIT 1", (symbol,)).fetchone()
    return dict(row) if row else None

def get_all_prices():
    conn = get_market_conn()
    rows = conn.execute("SELECT * FROM prices").fetchall()
    return {r["symbol"]: dict(r) for r in rows}

def get_all_mfs():
    conn = get_market_conn()
    rows = conn.execute("SELECT * FROM mutual_funds").fetchall()
    return [dict(r) for r in rows]

def get_mf_by_symbol(symbol):
    conn = get_market_conn()
    row = conn.execute("SELECT * FROM mutual_funds WHERE symbol=?", (symbol,)).fetchone()
    return dict(row) if row else None

def get_indices():
    conn = get_market_conn()
    rows = conn.execute("SELECT * FROM indices").fetchall()
    return [dict(r) for r in rows]
