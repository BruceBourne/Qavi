import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

    :root {
        --bg: #0C0F13;
        --bg2: #13181F;
        --bg3: #1A2030;
        --surface: #1E2738;
        --surface2: #253044;
        --border: #2E3D55;
        --text: #EDF2F7;
        --text2: #94A3B8;
        --accent: #3B82F6;
        --accent2: #60A5FA;
        --green: #22C55E;
        --red: #EF4444;
        --gold: #F59E0B;
        --purple: #A855F7;
        --radius: 12px;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background: var(--bg) !important;
        color: var(--text) !important;
    }

    h1, h2, h3 { font-family: 'DM Serif Display', serif !important; }

    /* Streamlit overrides */
    .stApp { background: var(--bg) !important; }
    .block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1400px; }

    .stButton > button {
        background: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        padding: 0.45rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: var(--accent) !important;
        border-color: var(--accent) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(59,130,246,0.3) !important;
    }

    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(59,130,246,0.2) !important;
    }

    .stDataFrame { border-radius: var(--radius); overflow: hidden; }
    .stDataFrame table { background: var(--surface) !important; }

    .stAlert {
        border-radius: var(--radius) !important;
        border-left-width: 3px !important;
    }

    div[data-testid="metric-container"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 1rem !important;
    }

    .stForm {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 1.2rem !important;
    }

    .stTab [data-baseweb="tab"] {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        color: var(--text2) !important;
    }
    .stTab [aria-selected="true"] {
        color: var(--accent) !important;
    }

    /* Custom nav */
    .nav-brand {
        font-family: 'DM Serif Display', serif;
        font-size: 1.6rem;
        color: var(--text);
        letter-spacing: -0.02em;
    }
    .nav-divider {
        border: none;
        border-top: 1px solid var(--border);
        margin: 0.4rem 0 1.2rem 0;
    }

    /* Cards */
    .qavi-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.4rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s;
    }
    .qavi-card:hover { border-color: var(--accent); }

    .qavi-card-title {
        font-family: 'DM Serif Display', serif;
        font-size: 1.1rem;
        color: var(--text);
        margin: 0 0 0.4rem 0;
    }

    .qavi-card-sub {
        font-size: 0.83rem;
        color: var(--text2);
        margin: 0;
    }

    .badge {
        display: inline-block;
        padding: 0.18rem 0.6rem;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-equity { background: rgba(59,130,246,0.15); color: #60A5FA; }
    .badge-mf { background: rgba(168,85,247,0.15); color: #C084FC; }
    .badge-etf { background: rgba(245,158,11,0.15); color: #FCD34D; }
    .badge-bond { background: rgba(34,197,94,0.15); color: #4ADE80; }

    .change-positive { color: var(--green); font-weight: 600; }
    .change-negative { color: var(--red); font-weight: 600; }
    .change-neutral { color: var(--text2); }

    .index-pill {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 0.8rem 1.2rem;
        text-align: center;
    }
    .index-name { font-size: 0.78rem; color: var(--text2); margin-bottom: 0.2rem; }
    .index-value { font-size: 1.2rem; font-weight: 600; color: var(--text); }
    .index-change-pos { font-size: 0.82rem; color: var(--green); }
    .index-change-neg { font-size: 0.82rem; color: var(--red); }

    .page-title {
        font-family: 'DM Serif Display', serif;
        font-size: 2rem;
        color: var(--text);
        margin-bottom: 0.2rem;
    }
    .page-sub {
        font-size: 0.9rem;
        color: var(--text2);
        margin-bottom: 1.5rem;
    }

    /* Hide streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
    </style>
    """, unsafe_allow_html=True)
