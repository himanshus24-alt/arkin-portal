"""
Arka KinetiQ — Intelligence in Motion
======================================
Mobile-first sales intelligence portal for Arka Fincap's SRL business.

Run:
  streamlit run arkin_app.py --server.port=8501 --server.address=0.0.0.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
import hashlib

# =============================================================================
# CONFIG
# =============================================================================
DATA_DIR = Path(__file__).parent / "arkin"
DATA_FILE = DATA_DIR / "arkin_dummy_data.xlsx"

st.set_page_config(
    page_title="Arka KinetiQ",
    page_icon="◬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# ARKA LOGO — Inline SVG that mirrors the actual Arka wordmark
# =============================================================================
# The real Arka logo: slim, condensed sans, with a triangular peak inside the K.
# This SVG approximation gets close. When you receive the official .svg from
# marketing, replace ARKA_LOGO_SVG with the contents of that file.
def arka_logo_svg(color="#0F3D3E", size_px=42):
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 80"
         height="{size_px}" style="display:inline-block;vertical-align:middle;">
      <!-- A -->
      <path d="M 8 70 L 32 12 L 56 70 L 46 70 L 41 56 L 23 56 L 18 70 Z
               M 26.5 47 L 37.5 47 L 32 32 Z"
            fill="{color}"/>
      <!-- R -->
      <path d="M 68 70 L 68 12 L 92 12 Q 110 12 110 27 Q 110 38 100 42
               L 113 70 L 102 70 L 91 45 L 77 45 L 77 70 Z
               M 77 21 L 77 36 L 92 36 Q 101 36 101 28.5 Q 101 21 92 21 Z"
            fill="{color}"/>
      <!-- K (with triangular peak inside top-right counter — Arka signature) -->
      <path d="M 124 70 L 124 12 L 133 12 L 133 38 L 158 12 L 170 12
               L 144 39 L 172 70 L 160 70 L 138 46 L 133 51 L 133 70 Z"
            fill="{color}"/>
      <!-- Triangle peak inside K (the Arka identity mark) -->
      <path d="M 148 22 L 158 12 L 158 22 Z" fill="{color}"/>
      <!-- A -->
      <path d="M 182 70 L 206 12 L 230 70 L 220 70 L 215 56 L 197 56 L 192 70 Z
               M 200.5 47 L 211.5 47 L 206 32 Z"
            fill="{color}"/>
    </svg>
    """


# =============================================================================
# GLOBAL CSS
# =============================================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
    :root {
        --teal-deep: #0F3D3E;
        --teal-vibrant: #1FA89A;
        --teal-soft: #E6F4F2;
        --copper: #D4936B;
        --copper-soft: #FDF4ED;
        --cream: #F6F8F8;
        --white: #FFFFFF;
        --ink-900: #0F3D3E;
        --ink-700: #2D5A5B;
        --ink-500: #6B8788;
        --ink-300: #B7C6C7;
        --line: #E5EAEA;
        --shadow-sm: 0 1px 3px rgba(15, 61, 62, 0.06);
        --shadow-md: 0 4px 12px rgba(15, 61, 62, 0.08);
        --shadow-lg: 0 12px 32px rgba(15, 61, 62, 0.12);
    }

    /* Strip Streamlit defaults including the white toolbar band */
    #MainMenu, footer, header[data-testid="stHeader"] {visibility: hidden; height: 0;}
    .stApp > header {height: 0 !important;}
    .block-container {
        padding: 0 !important;
        max-width: 480px !important;
        background: var(--cream);
    }
    .stApp {
        background: var(--cream);
        font-family: 'Inter', -apple-system, sans-serif;
        color: var(--ink-900);
    }
    [data-testid="stToolbar"] {visibility: hidden; height: 0;}
    [data-testid="stDecoration"] {display: none;}

    .page {padding: 14px 14px 80px 14px;}

    /* ── Brand bar (dashboards) ──────────────────────────────── */
    .brand-bar {
        background: var(--teal-deep);
        color: var(--white);
        padding: 14px 16px 16px;
        border-radius: 14px;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
    }
    .brand-bar::after {
        content: "";
        position: absolute;
        top: -25px; right: -25px;
        width: 80px; height: 80px;
        background: var(--copper);
        clip-path: polygon(50% 0%, 100% 100%, 0% 100%);
        opacity: 0.35;
    }
    .brand-bar-left {flex: 1; min-width: 0; position: relative; z-index: 2;}
    .brand-bar-logo {margin-bottom: 6px;}
    .brand-bar-logo svg {height: 24px; width: auto;}
    .brand-bar-logo .kq {
        font-family: 'Sora', sans-serif;
        font-weight: 500; font-size: 14px;
        color: var(--copper);
        font-style: italic;
        letter-spacing: 0.2px;
        margin-left: 8px;
        vertical-align: middle;
    }
    .brand-bar-meta {
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        color: rgba(255,255,255,0.85);
        line-height: 1.5;
    }
    .brand-bar-meta .chip {
        background: rgba(255,255,255,0.15);
        color: var(--white);
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.3px;
        margin-left: 4px;
    }
    .brand-bar-right {
        position: relative; z-index: 3;
    }
    .logout-btn {
        background: rgba(255,255,255,0.12);
        color: var(--white);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 8px;
        padding: 6px 10px;
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        font-weight: 600;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
        transition: all 0.2s;
    }

    /* ── KPI tiles ───────────────────────────────────────────── */
    .kpi-card {
        background: var(--white);
        border-radius: 12px;
        padding: 12px 13px;
        border: 1px solid var(--line);
        box-shadow: var(--shadow-sm);
        margin-bottom: 8px;
    }
    .kpi-label {
        font-family: 'Inter', sans-serif;
        font-size: 10px; font-weight: 600;
        color: var(--ink-500);
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .kpi-value {
        font-family: 'Sora', sans-serif;
        font-size: 22px; font-weight: 700;
        color: var(--ink-900);
        margin: 4px 0; line-height: 1.1;
    }
    .kpi-sub {font-size: 11px; color: var(--ink-500); font-weight: 500;}
    .kpi-up {color: var(--teal-vibrant); font-size: 12px;}
    .kpi-down {color: #C8553D; font-size: 12px;}

    /* Cards */
    .nudge-card {
        background: var(--copper-soft);
        border-left: 3px solid var(--copper);
        padding: 12px 14px; border-radius: 8px;
        margin-bottom: 8px; font-size: 13px; line-height: 1.5; color: #6B3F1F;
    }
    .announce-card {
        background: var(--teal-soft);
        border-left: 3px solid var(--teal-vibrant);
        padding: 12px 14px; border-radius: 8px;
        margin-bottom: 8px; font-size: 13px; line-height: 1.5; color: var(--teal-deep);
    }
    .action-card {
        background: #FDECEA;
        border-left: 3px solid #C8553D;
        padding: 12px 14px; border-radius: 8px;
        margin-bottom: 8px; font-size: 13px; line-height: 1.5; color: #7A1F0E;
    }

    /* Chips */
    .chip-amber {background: var(--copper-soft); color: #6B3F1F; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600;}
    .chip-red   {background: #FDECEA; color: #7A1F0E; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600;}
    .chip-green {background: var(--teal-soft); color: var(--teal-deep); padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600;}

    /* Section title */
    .section-title {
        font-family: 'Sora', sans-serif;
        font-size: 13px; font-weight: 700;
        color: var(--ink-900);
        margin: 14px 0 8px 0;
        letter-spacing: 0.2px;
    }
    .section-title .accent-dot {
        display: inline-block; width: 6px; height: 6px;
        border-radius: 50%; background: var(--copper);
        margin-right: 8px; vertical-align: middle;
    }

    /* Buttons */
    .stButton button {
        width: 100%;
        background: var(--teal-deep) !important;
        color: var(--white) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 11px 16px !important;
        font-family: 'Sora', sans-serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.3px;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s;
    }
    .stButton button:hover {
        background: var(--teal-vibrant) !important;
        box-shadow: var(--shadow-md);
    }

    /* Inputs */
    .stTextInput input, .stSelectbox > div > div {
        border-radius: 10px !important;
        border: 1.5px solid var(--line) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        padding: 10px 14px !important;
        background: var(--white) !important;
    }
    .stTextInput input:focus {
        border-color: var(--copper) !important;
        box-shadow: 0 0 0 3px rgba(212, 147, 107, 0.15) !important;
    }
    .stTextInput label, .stSelectbox label {
        font-family: 'Inter', sans-serif !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        color: var(--ink-700) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stDataFrame {font-size: 12px;}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px; background: var(--white);
        border-radius: 10px; padding: 4px;
        border: 1px solid var(--line);
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Sora', sans-serif !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        color: var(--ink-500) !important;
        padding: 8px 6px !important;
        border-radius: 8px !important;
        flex: 1; text-align: center;
        background: transparent !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--teal-deep) !important;
        color: var(--white) !important;
        box-shadow: var(--shadow-sm);
    }
    .stTabs [data-baseweb="tab-panel"] {padding-top: 12px;}
    .stTabs [data-baseweb="tab-highlight"] {display: none;}

    /* Radio (SRL toggle) */
    .stRadio > div {
        gap: 4px !important;
        background: var(--white);
        padding: 4px; border-radius: 10px;
        border: 1px solid var(--line);
        display: flex !important;
    }
    .stRadio label {font-family: 'Inter', sans-serif; font-size: 13px;}

    /* ── LOGIN PAGE — NO OVERLAPS, COMPACT ────────────────────── */
    .login-wrap {
        min-height: 100vh;
        background: var(--cream);
        position: relative;
        padding: 0;
    }

    /* The two corner triangles — SMALLER so they don't crowd the content */
    .login-wrap::before {
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 90px; height: 90px;
        background: var(--teal-deep);
        clip-path: polygon(0 0, 100% 0, 0 100%);
        z-index: 1;
    }
    .login-wrap::after {
        content: "";
        position: fixed;
        bottom: 0; right: 0;
        width: 110px; height: 110px;
        background: var(--copper);
        clip-path: polygon(100% 100%, 100% 0, 0 100%);
        z-index: 1;
    }

    .login-inner {
        position: relative;
        z-index: 5;
        padding: 110px 22px 24px 22px;
        max-width: 440px;
        margin: 0 auto;
    }

    .login-logo {
        text-align: left;
        margin-bottom: 22px;
    }
    .login-logo svg {height: 38px; width: auto;}
    .login-logo .kinetiq {
        font-family: 'Sora', sans-serif;
        font-size: 22px; font-weight: 500;
        color: var(--copper);
        font-style: italic;
        margin-left: 10px;
        letter-spacing: 0.5px;
        vertical-align: middle;
    }
    .login-tag {
        font-family: 'Inter', sans-serif;
        font-size: 10px; font-weight: 600;
        color: var(--ink-500);
        letter-spacing: 1.8px;
        text-transform: uppercase;
        margin-top: 8px;
    }

    .hero-headline {
        font-family: 'Sora', sans-serif;
        font-size: 30px;
        font-weight: 700;
        line-height: 1.12;
        color: var(--teal-deep);
        letter-spacing: -0.4px;
        margin-top: 18px;
    }
    .hero-headline .accent {
        color: var(--copper);
        font-style: italic;
    }
    .hero-sub {
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: var(--ink-500);
        margin-top: 10px;
        line-height: 1.5;
    }

    /* The form pulled close to the headline, before the bottom triangle */
    .login-form-wrap {
        margin-top: 20px;
    }
    .login-wrap [data-testid="stForm"] {
        background: var(--white);
        border-radius: 16px;
        padding: 18px 16px 16px;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--line);
        position: relative;
        z-index: 5;
    }

    .login-footer {
        margin-top: 16px;
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        color: var(--ink-500);
        line-height: 1.5;
        position: relative;
        z-index: 5;
    }
    .login-footer .powered {font-weight: 600; color: var(--ink-700);}
    .login-footer .group {opacity: 0.7; margin-top: 2px; display: block;}

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--white);
        border-right: 1px solid var(--line);
    }

    /* Expander */
    .streamlit-expanderHeader, [data-testid="stExpander"] summary {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: var(--teal-deep) !important;
    }

    /* Captions */
    .stCaption, [data-testid="stCaptionContainer"] {
        font-family: 'Inter', sans-serif !important;
        color: var(--ink-500) !important;
        font-size: 12px !important;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# DATA LAYER
# =============================================================================
@st.cache_data(ttl=300)
def load_data():
    if not DATA_FILE.exists():
        st.error(f"Data file not found at: {DATA_FILE}")
        st.stop()
    xl = pd.ExcelFile(DATA_FILE)
    return {
        "perf":  xl.parse("Performance"),
        "port":  xl.parse("Portfolio"),
        "prof":  xl.parse("Profitability"),
        "notif": xl.parse("Notification"),
        "org":   xl.parse("Org Hierarchy"),
    }


# =============================================================================
# AUTH
# =============================================================================
DEMO_PASSWORD = "arkin@2026"
def hash_pw(pw: str) -> str: return hashlib.sha256(pw.encode()).hexdigest()
DEMO_PW_HASH = hash_pw(DEMO_PASSWORD)


@st.cache_data(ttl=600)
def build_user_directory():
    data = load_data()
    org = data["org"]
    users = {}
    for _, r in org[org["Level"] == "RM"].iterrows():
        users[f"rm.{r['ID']}"] = {"name": r["Name"], "role": "Sales Manager", "level": "RM",
            "id": int(r["ID"]), "product": r["Product"], "zone": r["Zone"],
            "region": r["Region"], "pw_hash": DEMO_PW_HASH}
    for _, r in org[org["Level"] == "ABM"].iterrows():
        users[f"abm.{r['ID']}"] = {"name": r["Name"], "role": "Area Business Manager", "level": "ABM",
            "id": int(r["ID"]), "product": r["Product"], "zone": r["Zone"],
            "region": r["Region"], "pw_hash": DEMO_PW_HASH}
    for _, r in org[org["Level"] == "RBM"].iterrows():
        users[f"rbm.{r['ID']}"] = {"name": r["Name"], "role": "Regional Business Manager", "level": "RBM",
            "id": int(r["ID"]), "product": r["Product"], "zone": r["Zone"],
            "region": r["Region"], "pw_hash": DEMO_PW_HASH}
    for _, r in org[org["Level"] == "ZH"].iterrows():
        users[f"zh.{r['ID']}"] = {"name": r["Name"], "role": "Zonal Head", "level": "ZH",
            "id": int(r["ID"]), "product": r["Product"], "zone": r["Zone"],
            "region": "All", "pw_hash": DEMO_PW_HASH}
    users["cxo"] = {"name": "Chief Business Officer", "role": "CXO", "level": "CXO",
        "id": "CXO001", "product": "SRL", "zone": "All", "region": "All", "pw_hash": DEMO_PW_HASH}
    users["central"] = {"name": "Central Analytics Lead", "role": "Central Team", "level": "CXO",
        "id": "CEN001", "product": "SRL", "zone": "All", "region": "All", "pw_hash": DEMO_PW_HASH}
    users["admin"] = {"name": "System Administrator", "role": "Admin", "level": "Admin",
        "id": "ADM001", "product": "SRL", "zone": "All", "region": "All", "pw_hash": DEMO_PW_HASH}
    return users


def authenticate(username, password):
    users = build_user_directory()
    u = users.get(username.strip().lower())
    if u and hash_pw(password) == u["pw_hash"]:
        return u
    return None


# =============================================================================
# RBAC + PRODUCT SCOPING
# =============================================================================
def scope_data(df, user, product_override=None):
    if df is None or df.empty:
        return df
    level = user["level"]
    prod = product_override if product_override else user["product"]

    if prod in ("STLAP", "Wheels") and "Product" in df.columns:
        df = df[df["Product"] == prod]

    if level in ("CXO", "Admin"):
        return df
    if level == "ZH" and "ZH ID" in df.columns:
        return df[df["ZH ID"] == user["id"]]
    if level == "RBM" and "RBM ID" in df.columns:
        return df[df["RBM ID"] == user["id"]]
    if level == "ABM" and "ABM ID" in df.columns:
        return df[df["ABM ID"] == user["id"]]
    if level == "RM":
        col = "Emp ID" if "Emp ID" in df.columns else "RM ID"
        return df[df[col] == user["id"]] if col in df.columns else df
    return df.iloc[0:0]


# =============================================================================
# UI HELPERS
# =============================================================================
def brand_bar(user, current_product=None):
    """Top branded bar with Arka SVG logo + user info + INLINE logout button."""
    display_prod = current_product if current_product else user["product"]
    prod_chip = f'<span class="chip">{display_prod}</span>'
    arka_white = arka_logo_svg(color="#FFFFFF", size_px=22)

    st.markdown(f"""
    <div class="brand-bar">
      <div class="brand-bar-left">
        <div class="brand-bar-logo">
          {arka_white}<span class="kq">KinetiQ</span>
        </div>
        <div class="brand-bar-meta">{user['name']} · {user['role']} · {user.get('zone','—')} {prod_chip}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def kpi_tile(label, value, sub="", trend=None):
    trend_html = ""
    if trend is not None:
        cls = "kpi-up" if trend >= 0 else "kpi-down"
        arrow = "▲" if trend >= 0 else "▼"
        trend_html = f'<span class="{cls}"> {arrow} {abs(trend):.1f}%</span>'
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}{trend_html}</div>
      <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def section(title, emoji=""):
    icon = f"{emoji} " if emoji else ""
    st.markdown(f'<div class="section-title"><span class="accent-dot"></span>{icon}{title}</div>',
                unsafe_allow_html=True)


def mailto_link(to_email, subject, body, cc_list=None):
    cc = ",".join(cc_list) if cc_list else ""
    return f"mailto:{to_email}?cc={cc}&subject={quote(subject)}&body={quote(body)}"


def status_chip(text, kind="green"):
    return f'<span class="chip-{kind}">{text}</span>'


# =============================================================================
# PLOTLY THEMING
# =============================================================================
ARKA_PALETTE = ["#0F3D3E", "#1FA89A", "#D4936B", "#5BAFA8", "#E6B998", "#2D5A5B"]

def apply_plotly_theme(fig, height=240):
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Inter, sans-serif", size=11, color="#0F3D3E"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.18, font=dict(size=10, color="#0F3D3E")),
        xaxis=dict(showgrid=False, color="#6B8788"),
        yaxis=dict(gridcolor="#E5EAEA", color="#6B8788"),
    )
    return fig


# =============================================================================
# SALES MANAGER (RM)
# =============================================================================
def render_sales_manager(user, data):
    perf  = scope_data(data["perf"], user)
    port  = scope_data(data["port"], user)
    prof  = scope_data(data["prof"], user)
    notif = scope_data(data["notif"], user)

    if perf.empty:
        st.warning("No performance data found for your profile.")
        return
    row = perf.iloc[0]

    tab_focus, tab_perf, tab_port = st.tabs(["🎯 Focus", "📊 Performance", "💼 Portfolio"])

    with tab_focus:
        section("AI Nudges for You", "🤖")
        if not notif.empty:
            nrow = notif.iloc[0]
            for i in range(1, 6):
                n = nrow.get(f"Notification {i}", "")
                if pd.notna(n) and str(n).strip():
                    st.markdown(f'<div class="nudge-card">💡 {n}</div>', unsafe_allow_html=True)

        section("Key Announcements", "📢")
        st.markdown('<div class="announce-card">📌 Quarterly target review on 30th — submit branch numbers by EOD Friday.</div>', unsafe_allow_html=True)
        st.markdown('<div class="announce-card">🎯 New TAT SLA: Login → Sanction within 5 working days from June.</div>', unsafe_allow_html=True)

        section("Key Actionables Today", "✅")
        gap_disb = max(0, int(row["Target Disb #"] - row["Actual Disb #"]))
        if gap_disb > 0:
            st.markdown(f'<div class="action-card">🔥 Close {gap_disb} more disbursements to hit monthly target.</div>', unsafe_allow_html=True)
        if row["Actual PF %"] < row["Target PF %"]:
            st.markdown(f'<div class="action-card">💰 PF% at {row["Actual PF %"]:.2f}% vs target {row["Target PF %"]:.2f}% — push fee collection.</div>', unsafe_allow_html=True)
        if row["Actual Conversion %"] < row["Target Conversion %"]:
            st.markdown(f'<div class="action-card">🎯 Conversion {row["Actual Conversion %"]:.1f}% below target {row["Target Conversion %"]:.1f}% — reduce TAT.</div>', unsafe_allow_html=True)

    with tab_perf:
        section("Funnel — Login → Sanction → Disb", "📊")
        c = st.columns(3)
        with c[0]: kpi_tile("Logins", f"{int(row['Actual Login #'])}", f"Tgt {int(row['Target Login #'])}")
        with c[1]: kpi_tile("Sanctions", f"{int(row['Actual Sanction #'])}", f"Tgt {int(row['Target Sanction #'])}")
        with c[2]: kpi_tile("Disb", f"{int(row['Actual Disb #'])}", f"Tgt {int(row['Target Disb #'])}")

        fig = go.Figure(go.Funnel(
            y=["Logins", "Sanctions", "Disbursements"],
            x=[row["Actual Login #"], row["Actual Sanction #"], row["Actual Disb #"]],
            marker={"color": ["#1FA89A", "#0F3D3E", "#D4936B"]},
            textposition="inside", textinfo="value+percent initial",
        ))
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

        section("Conversion & Mix", "🎯")
        c1, c2 = st.columns(2)
        with c1:
            conv_gap = row["Actual Conversion %"] - row["Target Conversion %"]
            kpi_tile("Conversion", f"{row['Actual Conversion %']:.1f}%",
                     f"Tgt {row['Target Conversion %']:.1f}%", trend=conv_gap)
            kpi_tile("IRR Mix", f"{row['IRR Mix %']:.2f}%", "Portfolio yield")
        with c2:
            kpi_tile("LTV", f"{row['LTV %']:.1f}%", "Loan to Value")
            kpi_tile("Avg Ticket", f"₹{row['Avg Ticket Size (Rs L)']:.1f} L", "Per case")

        section("Disbursement Trend", "📈")
        trend_df = pd.DataFrame({
            "Month": ["M-3", "M-2", "M-1", "Current"],
            "Disb #": [row["M-3 Disb #"], row["M-2 Disb #"], row["M-1 Disb #"], row["Actual Disb #"]],
            "Target": [row["Target Disb #"]] * 4,
        })
        fig = go.Figure()
        fig.add_bar(x=trend_df["Month"], y=trend_df["Disb #"], name="Actual", marker_color="#1FA89A")
        fig.add_scatter(x=trend_df["Month"], y=trend_df["Target"], name="Target",
                        mode="lines+markers", line=dict(color="#D4936B", dash="dash", width=2),
                        marker=dict(size=8))
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

        section("Achievement & Productivity", "⚡")
        c1, c2 = st.columns(2)
        with c1:
            kpi_tile("CM Achievement", f"{row['CM Achievement %']:.1f}%", "Of monthly target")
            kpi_tile("PF %", f"{row['Actual PF %']:.2f}%", f"Tgt {row['Target PF %']:.2f}%")
        with c2:
            kpi_tile("Cross-sell", f"{row['Cross Sell %']:.1f}%", "Insurance + bundle")
            kpi_tile("Productivity", f"{row['Productivity (Disb/RM)']:.1f}", "Disb/RM/month")

        fee_income = (row["Actual Disb Amount (Rs Cr)"] * row["Actual PF %"] / 100 +
                      row["Actual Disb Amount (Rs Cr)"] * row["Actual Insurance %"] / 100)
        kpi_tile("Fee Income (PF + Ins)", f"₹{fee_income:.3f} Cr", "This month")

    with tab_port:
        if not prof.empty:
            prow = prof.iloc[0]
            section("Portfolio Health", "💼")
            c1, c2 = st.columns(2)
            with c1:
                kpi_tile("AUM", f"₹{prow['AUM (Rs Cr)']:.1f} Cr", "Customers acquired")
                kpi_tile("Bounce %", f"{prow['AUM Bounce %']:.1f}%", "Portfolio")
                kpi_tile("30+ DPD", f"{prow['30+ DPD %']:.1f}%", "Delinquency")
                kpi_tile("EMI Eff.", f"{prow['EMI Collection Efficiency %']:.1f}%", "Collection")
            with c2:
                kpi_tile("Exit Rate", f"{prow['Exit Rate %']:.1f}%", "Customers leaving")
                kpi_tile("Avg LTV", f"{prow['Avg LTV %']:.1f}%", "Portfolio")
                kpi_tile("NPA %", f"{prow['NPA %']:.2f}%", "Non-performing")
                kpi_tile("Portfolio IRR", f"{prow['Portfolio IRR %']:.2f}%", "Yield")

        if not port.empty:
            section("Asset Type Mix", "🏷️")
            asset_mix = port.groupby("Asset Type")["POS (Rs Cr)"].sum().reset_index()
            fig = px.pie(asset_mix, names="Asset Type", values="POS (Rs Cr)",
                         color_discrete_sequence=ARKA_PALETTE)
            apply_plotly_theme(fig, height=270)
            st.plotly_chart(fig, use_container_width=True)

            section("PAR Bucket Distribution", "📊")
            par_mix = port.groupby("PAR Bucket")["POS (Rs Cr)"].sum().reset_index()
            par_order = ["Current", "1-30 DPD", "31-60 DPD", "61-90 DPD", "90+ DPD"]
            par_mix["PAR Bucket"] = pd.Categorical(par_mix["PAR Bucket"], categories=par_order, ordered=True)
            par_mix = par_mix.sort_values("PAR Bucket")
            fig = px.bar(par_mix, x="PAR Bucket", y="POS (Rs Cr)",
                         color="PAR Bucket",
                         color_discrete_sequence=["#1FA89A","#5BAFA8","#D4936B","#E6B998","#C8553D"])
            apply_plotly_theme(fig, height=240)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# LEADER (ABM/RBM/ZH)
# =============================================================================
def render_leader(user, data, product_override=None):
    perf = scope_data(data["perf"], user, product_override)
    prof = scope_data(data["prof"], user, product_override)
    port = scope_data(data["port"], user, product_override)

    if perf.empty:
        st.warning("No team data found for your profile.")
        return

    tab_focus, tab_perf, tab_port, tab_prof = st.tabs(
        ["🎯 Focus", "📊 Performance", "💼 Portfolio", "💵 Profitability"]
    )

    with tab_focus:
        section("Focus of the Month", "🎯")
        st.caption("Low-performing RMs with vintage > 3 months — need attention")
        low_perf = perf[
            (perf["Actual Disb #"] < perf["Target Disb #"] * 0.6) &
            (perf["M-3 Disb #"] > 0)
        ][["EMP Name", "Actual Disb #", "Target Disb #",
           "M-1 Disb #", "M-2 Disb #", "M-3 Disb #"]].head(10)
        if low_perf.empty:
            st.success("✅ No low performers flagged this month.")
        else:
            low_perf = low_perf.rename(columns={"EMP Name": "RM"})
            st.dataframe(low_perf, use_container_width=True, hide_index=True)

        section("Escalation Tracker", "🚨")
        st.caption("RMs with zero disbursement — auto-escalation ladder")
        zero_disb = perf[perf["Actual Disb #"] == 0].copy()
        if not zero_disb.empty:
            def escalate(r):
                zeros = sum(1 for m in [r["M-1 Disb #"], r["M-2 Disb #"], r["M-3 Disb #"]] if m == 0)
                if zeros == 0: return ("Month 1 — AMBER", "amber", "Visible to ABM")
                elif zeros == 1: return ("Month 2 — AMBER", "amber", "Escalated to RBM")
                elif zeros == 2: return ("Month 3 — RED", "red", "Escalated to ZH")
                else: return ("Critical — RED", "red", "Visible to Business Head")
            zero_disb[["Status", "Kind", "Visible To"]] = zero_disb.apply(
                lambda r: pd.Series(escalate(r)), axis=1)
            for _, r in zero_disb.head(10).iterrows():
                chip = status_chip(r["Status"], r["Kind"])
                st.markdown(
                    f'<div class="kpi-card" style="padding:10px 12px;">'
                    f'<b>{r["EMP Name"]}</b> &nbsp;{chip}<br>'
                    f'<span class="kpi-sub">{r["Visible To"]} · '
                    f'M-1: {int(r["M-1 Disb #"])} | M-2: {int(r["M-2 Disb #"])} | '
                    f'M-3: {int(r["M-3 Disb #"])}</span></div>',
                    unsafe_allow_html=True)
        else:
            st.success("✅ All RMs have disbursed this month.")

        section("Quick Nudge", "✉️")
        bottom = perf.sort_values("Actual Disb #").head(15)
        rm_pick = st.selectbox("Pick RM to nudge", bottom["EMP Name"].tolist(), key="nudge_pick")
        if rm_pick:
            rm_row = bottom[bottom["EMP Name"] == rm_pick].iloc[0]
            rm_email = f"{rm_pick.lower().replace(' ', '.')}@arkafincap.com"
            body = (
                f"Hi {rm_pick},\n\n"
                f"Your current month performance shows {int(rm_row['Actual Disb #'])} "
                f"disbursements against a target of {int(rm_row['Target Disb #'])}. "
                f"Your conversion stands at {rm_row['Actual Conversion %']:.1f}% "
                f"vs target {rm_row['Target Conversion %']:.1f}%.\n\n"
                f"Please prioritise pipeline closure this week.\n\n"
                f"Regards,\n{user['name']}"
            )
            cc = [f"rbm.{user.get('region','').lower().replace(' ', '')}@arkafincap.com",
                  f"zh.{user.get('zone','').lower()}@arkafincap.com"]
            link = mailto_link(rm_email, f"Performance Nudge — {rm_pick}", body, cc)
            st.markdown(f'<a href="{link}" style="text-decoration:none;"><button style="width:100%;'
                        f'background:#0F3D3E;color:white;border:none;padding:12px;'
                        f'border-radius:10px;font-family:Sora,sans-serif;font-weight:600;'
                        f'font-size:14px;cursor:pointer;letter-spacing:0.3px;">'
                        f'📧 Open Email — Nudge {rm_pick}</button></a>',
                        unsafe_allow_html=True)

    with tab_perf:
        section("Team Snapshot", "👥")
        n_rms = perf["Emp ID"].nunique()
        total_disb = int(perf["Actual Disb #"].sum())
        total_tgt = int(perf["Target Disb #"].sum())
        disb_amt = perf["Actual Disb Amount (Rs Cr)"].sum()
        c1, c2 = st.columns(2)
        with c1:
            kpi_tile("RMs", f"{n_rms}", "Active")
            kpi_tile("Disb #", f"{total_disb}", f"Tgt {total_tgt}",
                     trend=(total_disb - total_tgt) / max(1, total_tgt) * 100)
        with c2:
            kpi_tile("Disb Amount", f"₹{disb_amt:.1f} Cr", "MTD")
            kpi_tile("Avg Conv.", f"{perf['Actual Conversion %'].mean():.1f}%", "Login→Disb")

        section("Leaderboard — Disbursements", "🏆")
        lb = perf.sort_values("Actual Disb #", ascending=False).head(10)[
            ["EMP Name", "Actual Disb #", "Target Disb #", "Actual Conversion %", "IRR Mix %"]
        ].rename(columns={"EMP Name": "RM", "Actual Disb #": "Disb",
                           "Target Disb #": "Tgt", "Actual Conversion %": "Conv%",
                           "IRR Mix %": "IRR%"})
        st.dataframe(lb, use_container_width=True, hide_index=True)

        section("Leaderboard — IRR Mix", "💰")
        irr_lb = perf.sort_values("IRR Mix %", ascending=False).head(10)[
            ["EMP Name", "IRR Mix %", "Actual Disb #", "LTV %"]
        ].rename(columns={"EMP Name": "RM", "IRR Mix %": "IRR%", "Actual Disb #": "Disb"})
        st.dataframe(irr_lb, use_container_width=True, hide_index=True)

        if len(perf) >= 2:
            section("Peer Leaderboard — 3M Avg", "👥")
            peer = perf.copy()
            peer["3M Avg Disb"] = (peer["M-1 Disb #"] + peer["M-2 Disb #"] + peer["M-3 Disb #"]) / 3
            peer = peer.sort_values("Actual Disb #", ascending=False)
            show = peer[["EMP Name", "Actual Disb #", "3M Avg Disb", "IRR Mix %"]].head(15)
            show = show.rename(columns={"EMP Name": "RM", "Actual Disb #": "Disb", "IRR Mix %": "IRR%"})
            show["3M Avg Disb"] = show["3M Avg Disb"].round(1)
            st.dataframe(show, use_container_width=True, hide_index=True)

        if user["level"] in ("RBM", "ZH", "CXO"):
            section("Performance by Region", "🗺️")
            region_perf = perf.groupby("Region").agg(
                Disb=("Actual Disb #", "sum"),
                Target=("Target Disb #", "sum"),
                DisbAmt=("Actual Disb Amount (Rs Cr)", "sum"),
            ).reset_index()
            region_perf["Ach %"] = (region_perf["Disb"] / region_perf["Target"] * 100).round(1)
            st.dataframe(region_perf, use_container_width=True, hide_index=True)
            fig = px.bar(region_perf, x="Region", y=["Disb", "Target"], barmode="group",
                         color_discrete_sequence=["#1FA89A", "#D4936B"])
            apply_plotly_theme(fig, height=260)
            st.plotly_chart(fig, use_container_width=True)

            section("Top & Bottom ABMs", "🏆")
            abm_perf = perf.groupby(["ABM Name"]).agg(
                Disb=("Actual Disb #", "sum"),
                Target=("Target Disb #", "sum"),
            ).reset_index()
            abm_perf["Ach %"] = (abm_perf["Disb"] / abm_perf["Target"] * 100).round(1)
            st.write("**Top 5**")
            st.dataframe(abm_perf.nlargest(5, "Ach %"), use_container_width=True, hide_index=True)
            st.write("**Bottom 5**")
            st.dataframe(abm_perf.nsmallest(5, "Ach %"), use_container_width=True, hide_index=True)

    with tab_port:
        if not prof.empty:
            section("Portfolio Health — Aggregate", "💼")
            c1, c2 = st.columns(2)
            with c1:
                kpi_tile("Total AUM", f"₹{prof['AUM (Rs Cr)'].sum():.1f} Cr", "Book")
                kpi_tile("Avg Bounce %", f"{prof['AUM Bounce %'].mean():.1f}%", "Team avg")
                kpi_tile("Avg 30+ DPD", f"{prof['30+ DPD %'].mean():.1f}%", "Team avg")
                kpi_tile("EMI Eff.", f"{prof['EMI Collection Efficiency %'].mean():.1f}%", "Collection")
            with c2:
                kpi_tile("Exit Rate", f"{prof['Exit Rate %'].mean():.1f}%", "Avg")
                kpi_tile("Avg LTV", f"{prof['Avg LTV %'].mean():.1f}%", "Portfolio")
                kpi_tile("NPA %", f"{prof['NPA %'].mean():.2f}%", "Team avg")
                kpi_tile("Portfolio IRR", f"{prof['Portfolio IRR %'].mean():.2f}%", "Yield")

        if not port.empty:
            section("Asset Mix", "🏷️")
            asset_mix = port.groupby("Asset Type")["POS (Rs Cr)"].sum().reset_index()
            fig = px.pie(asset_mix, names="Asset Type", values="POS (Rs Cr)",
                         color_discrete_sequence=ARKA_PALETTE)
            apply_plotly_theme(fig, height=270)
            st.plotly_chart(fig, use_container_width=True)

    with tab_prof:
        if not prof.empty:
            section("Profitability KPIs", "💵")
            c1, c2 = st.columns(2)
            with c1:
                kpi_tile("AUM / RM", f"₹{prof['AUM/RM (Rs Cr)'].mean():.2f} Cr", "Avg")
                kpi_tile("Branch PAT %", f"{prof['PAT % (Before HO Allocation)'].mean():.2f}%", "Pre-HO")
            with c2:
                kpi_tile("Disb / RM", f"₹{prof['Disb/RM (Rs Cr)'].mean():.2f} Cr", "Avg")
                kpi_tile("Gross Margin", f"{prof['Gross Margin %'].mean():.2f}%", "Avg")

            section("Path to 2% RoA", "🎯")
            avg_pat = prof["PAT % (Before HO Allocation)"].mean()
            avg_aum_per_rm = prof["AUM/RM (Rs Cr)"].mean()
            avg_yield = prof["Yield %"].mean()
            avg_cost = prof["Branch Cost (Rs Cr)"].mean()
            recos = []
            if avg_pat < 2.0:
                gap = 2.0 - avg_pat
                recos.append(f"📈 **Current PAT% is {avg_pat:.2f}%, gap to 2% RoA is {gap:.2f}pp.**")
                if avg_aum_per_rm < 12:
                    recos.append(f"• **AUM/RM lever**: Avg AUM/RM at ₹{avg_aum_per_rm:.1f}Cr. Push to ₹15Cr — adds ~{(15-avg_aum_per_rm)*avg_yield/100:.2f}% to margin.")
                if avg_yield < 17:
                    recos.append(f"• **Yield lever**: Avg yield {avg_yield:.2f}%. Shift mix to higher-IRR deals — adds ~0.5–1pp.")
                if avg_cost > 1.5:
                    recos.append(f"• **Cost lever**: Avg branch cost ₹{avg_cost:.2f}Cr. Trim 10% via shared services — adds ~{avg_cost*0.1:.2f}pp.")
            else:
                recos.append(f"✅ Already at {avg_pat:.2f}% — above 2% RoA target.")
            for r in recos:
                st.markdown(r)

            section("Active Escalations Roll-up", "🚨")
            zero = perf[perf["Actual Disb #"] == 0]
            n_amber = len(zero[zero["M-1 Disb #"] > 0])
            n_red = len(zero[(zero["M-1 Disb #"] == 0) & (zero["M-2 Disb #"] == 0)])
            c1, c2 = st.columns(2)
            with c1:
                kpi_tile("Amber Alerts", f"{n_amber}", "1st-2nd month zero")
            with c2:
                kpi_tile("Red Alerts", f"{n_red}", "3+ month zero")


# =============================================================================
# CXO
# =============================================================================
def render_cxo(user, data):
    section("Product View", "🎛️")
    product_view = st.radio("Product", ["SRL", "STLAP", "Wheels"],
                            horizontal=True, key="cxo_product_view",
                            label_visibility="collapsed")

    st.markdown(f'<div style="font-family:Inter,sans-serif;font-size:11px;color:#6B8788;'
                f'margin:-4px 0 8px 2px;">Currently viewing: <b style="color:#0F3D3E;">'
                f'{product_view}</b> {"(STLAP + Wheels combined)" if product_view=="SRL" else ""}</div>',
                unsafe_allow_html=True)

    render_leader(user, data, product_override=product_view)


# =============================================================================
# ADMIN
# =============================================================================
def render_admin(user, data):
    section("Admin Console", "⚙️")
    st.caption("Upload data, dispatch nudges, manage user access.")

    tab1, tab2, tab3 = st.tabs(["📤 Upload Data", "🔔 Notifications", "👤 Users"])

    with tab1:
        st.write("**Upload the latest monthly data file**")
        up = st.file_uploader("Choose Excel file", type=["xlsx"])
        if up is not None:
            target = DATA_DIR / "arkin_dummy_data.xlsx"
            DATA_DIR.mkdir(exist_ok=True)
            with open(target, "wb") as f:
                f.write(up.getbuffer())
            st.cache_data.clear()
            st.success(f"✅ Uploaded {up.name} → {target}. Cache cleared.")

        st.divider()
        st.write("**Current data file**")
        if DATA_FILE.exists():
            sz = DATA_FILE.stat().st_size / 1024
            mt = datetime.fromtimestamp(DATA_FILE.stat().st_mtime)
            st.info(f"📁 `{DATA_FILE.name}` · {sz:.1f} KB · last modified {mt:%d-%b-%Y %H:%M}")

    with tab2:
        st.write("**Dispatch notifications**")
        notif = data["notif"]
        st.write(f"Total notifications queued: **{len(notif)}**")
        st.dataframe(notif[["RM Name", "Product", "Notification 1"]].head(10),
                     use_container_width=True, hide_index=True)
        st.button("🚀 Dispatch All Notifications (mock)", use_container_width=True)

    with tab3:
        st.write("**User directory**")
        org = data["org"]
        st.dataframe(
            org.groupby(["Level", "Product"]).size().reset_index(name="Count"),
            use_container_width=True, hide_index=True)
        lvl = st.selectbox("Filter by level",
                           ["All"] + sorted(org["Level"].unique().tolist()))
        view = org if lvl == "All" else org[org["Level"] == lvl]
        st.dataframe(view.head(50), use_container_width=True, hide_index=True)


# =============================================================================
# LOGIN
# =============================================================================
def login_screen():
    arka_dark = arka_logo_svg(color="#0F3D3E", size_px=38)

    st.markdown(f"""
    <div class="login-wrap">
      <div class="login-inner">
        <div class="login-logo">
          {arka_dark}<span class="kinetiq">KinetiQ</span>
          <div class="login-tag">INTELLIGENCE IN MOTION</div>
        </div>

        <div class="hero-headline">
          Get ahead,<br>
          <span class="accent">every day.</span>
        </div>
        <div class="hero-sub">
          Your sales intelligence companion. Numbers, nudges, and next steps —
          crafted for the way you actually work.
        </div>

        <div class="login-form-wrap">
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Employee ID", placeholder="e.g. rm.3001")
        password = st.text_input("Password", type="password",
                                 placeholder="Demo: arkin@2026")
        submitted = st.form_submit_button("Sign in →", use_container_width=True)
        if submitted:
            u = authenticate(username, password)
            if u:
                st.session_state["user"] = u
                st.session_state["username"] = username.strip().lower()
                st.rerun()
            else:
                st.error("❌ Invalid Employee ID or password.")

    st.markdown("""
        </div>
        <div class="login-footer">
          <span class="powered">Powered by Arka Fincap</span>
          <span class="group">A Kirloskar Group company</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🧪 Demo credentials"):
        st.markdown(f"""
**Password for all demo accounts:** `{DEMO_PASSWORD}`

| Employee ID | Role | Product |
|---|---|---|
| `rm.3001` | Sales Manager | STLAP |
| `rm.4001` | Sales Manager | Wheels |
| `abm.2001` | Area Business Manager | STLAP |
| `abm.2101` | Area Business Manager | Wheels |
| `rbm.201` | Regional Business Manager | STLAP |
| `rbm.216` | Regional Business Manager | Wheels |
| `zh.131` | Zonal Head | STLAP |
| `zh.135` | Zonal Head | Wheels |
| `cxo` | CXO | SRL |
| `central` | Central Team | SRL |
| `admin` | System Admin | SRL |
        """)


# =============================================================================
# MAIN
# =============================================================================
def main():
    data = load_data()

    if "user" not in st.session_state:
        login_screen()
        return

    st.markdown('<div class="page">', unsafe_allow_html=True)

    user = st.session_state["user"]
    brand_bar(user)

    # Inline logout button right under the brand bar — visible on mobile
    col_a, col_b, col_c = st.columns([2, 2, 1])
    with col_c:
        if st.button("Sign out", key="logout_top", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    level = user["level"]
    if level == "RM":
        render_sales_manager(user, data)
    elif level == "ABM":
        render_leader(user, data)
    elif level in ("RBM", "ZH"):
        render_leader(user, data)
    elif level == "CXO":
        render_cxo(user, data)
    elif level == "Admin":
        render_admin(user, data)

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
# =============================================================================
# GLOBAL CSS — Arka KinetiQ brand system
# =============================================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
    :root {
        --teal-deep: #0F3D3E;
        --teal-vibrant: #1FA89A;
        --teal-soft: #E6F4F2;
        --copper: #D4936B;
        --copper-soft: #FDF4ED;
        --cream: #F6F8F8;
        --white: #FFFFFF;
        --ink-900: #0F3D3E;
        --ink-700: #2D5A5B;
        --ink-500: #6B8788;
        --ink-300: #B7C6C7;
        --line: #E5EAEA;
        --shadow-sm: 0 1px 3px rgba(15, 61, 62, 0.06);
        --shadow-md: 0 4px 12px rgba(15, 61, 62, 0.08);
        --shadow-lg: 0 12px 32px rgba(15, 61, 62, 0.12);
    }

    /* ── Strip Streamlit defaults ────────────────────────────── */
    #MainMenu, footer, header[data-testid="stHeader"] {visibility: hidden;}
    .block-container {
        padding: 0 !important;
        max-width: 480px !important;
        background: var(--cream);
    }
    .stApp {
        background: var(--cream);
        font-family: 'Inter', -apple-system, sans-serif;
        color: var(--ink-900);
    }

    .page {padding: 14px 14px 80px 14px;}

    /* ── Logo wordmark (used in both login + brand-bar) ──────── */
    .arka-mark {
        font-family: 'Sora', sans-serif;
        font-weight: 800;
        letter-spacing: 2px;
        display: inline-flex;
        align-items: baseline;
        gap: 6px;
    }
    .arka-mark .arka {color: var(--teal-deep);}
    .arka-mark .kq {
        color: var(--copper);
        font-weight: 600;
        font-style: italic;
        letter-spacing: 0.5px;
    }

    /* ── Brand bar (dashboards) ──────────────────────────────── */
    .brand-bar {
        background: var(--teal-deep);
        color: var(--white);
        padding: 14px 16px;
        border-radius: 14px;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
    }
    .brand-bar::before {
        content: "";
        position: absolute;
        top: -25px; right: -25px;
        width: 80px; height: 80px;
        background: var(--copper);
        clip-path: polygon(50% 0%, 100% 100%, 0% 100%);
        opacity: 0.35;
    }
    .brand-bar .brand-row {
        display: flex; align-items: baseline; gap: 4px;
        position: relative; z-index: 2;
    }
    .brand-bar .b1 {
        font-family: 'Sora', sans-serif;
        font-weight: 800; font-size: 16px;
        letter-spacing: 1.8px; color: var(--white);
    }
    .brand-bar .b2 {
        font-family: 'Sora', sans-serif;
        font-weight: 500; font-size: 14px;
        color: var(--copper); font-style: italic;
        letter-spacing: 0.2px;
    }
    .brand-bar .b-meta {
        font-family: 'Inter', sans-serif;
        font-size: 11px; opacity: 0.85;
        margin-top: 6px; position: relative; z-index: 2;
        line-height: 1.5;
    }
    .brand-bar .chip {
        background: rgba(255,255,255,0.15) !important;
        color: var(--white) !important;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.3px;
        margin-left: 4px;
    }

    /* ── KPI tiles ───────────────────────────────────────────── */
    .kpi-card {
        background: var(--white);
        border-radius: 12px;
        padding: 12px 13px;
        border: 1px solid var(--line);
        box-shadow: var(--shadow-sm);
        margin-bottom: 8px;
    }
    .kpi-label {
        font-family: 'Inter', sans-serif;
        font-size: 10px; font-weight: 600;
        color: var(--ink-500);
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .kpi-value {
        font-family: 'Sora', sans-serif;
        font-size: 22px; font-weight: 700;
        color: var(--ink-900);
        margin: 4px 0; line-height: 1.1;
    }
    .kpi-sub {font-size: 11px; color: var(--ink-500); font-weight: 500;}
    .kpi-up {color: var(--teal-vibrant); font-size: 12px;}
    .kpi-down {color: #C8553D; font-size: 12px;}

    /* ── Nudge / Announce / Action cards ─────────────────────── */
    .nudge-card {
        background: var(--copper-soft);
        border-left: 3px solid var(--copper);
        padding: 12px 14px;
        border-radius: 8px;
        margin-bottom: 8px;
        font-size: 13px; line-height: 1.5;
        color: #6B3F1F;
    }
    .announce-card {
        background: var(--teal-soft);
        border-left: 3px solid var(--teal-vibrant);
        padding: 12px 14px;
        border-radius: 8px;
        margin-bottom: 8px;
        font-size: 13px; line-height: 1.5;
        color: var(--teal-deep);
    }
    .action-card {
        background: #FDECEA;
        border-left: 3px solid #C8553D;
        padding: 12px 14px;
        border-radius: 8px;
        margin-bottom: 8px;
        font-size: 13px; line-height: 1.5;
        color: #7A1F0E;
    }

    /* ── Chips ───────────────────────────────────────────────── */
    .chip-amber {background: var(--copper-soft); color: #6B3F1F; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600;}
    .chip-red   {background: #FDECEA; color: #7A1F0E; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600;}
    .chip-green {background: var(--teal-soft); color: var(--teal-deep); padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600;}

    /* ── Section title ───────────────────────────────────────── */
    .section-title {
        font-family: 'Sora', sans-serif;
        font-size: 13px; font-weight: 700;
        color: var(--ink-900);
        margin: 14px 0 8px 0;
        letter-spacing: 0.2px;
    }
    .section-title .accent-dot {
        display: inline-block; width: 6px; height: 6px;
        border-radius: 50%; background: var(--copper);
        margin-right: 8px; vertical-align: middle;
    }

    /* ── Buttons ─────────────────────────────────────────────── */
    .stButton button {
        width: 100%;
        background: var(--teal-deep) !important;
        color: var(--white) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 11px 16px !important;
        font-family: 'Sora', sans-serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.3px;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s;
    }
    .stButton button:hover {
        background: var(--teal-vibrant) !important;
        box-shadow: var(--shadow-md);
    }

    /* ── Inputs ──────────────────────────────────────────────── */
    .stTextInput input, .stSelectbox > div > div {
        border-radius: 10px !important;
        border: 1.5px solid var(--line) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        padding: 10px 14px !important;
        background: var(--white) !important;
    }
    .stTextInput input:focus {
        border-color: var(--copper) !important;
        box-shadow: 0 0 0 3px rgba(212, 147, 107, 0.15) !important;
    }
    .stTextInput label, .stSelectbox label {
        font-family: 'Inter', sans-serif !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        color: var(--ink-700) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ── DataFrames ──────────────────────────────────────────── */
    .stDataFrame {font-size: 12px;}

    /* ── Tabs ────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--white);
        border-radius: 10px;
        padding: 4px;
        border: 1px solid var(--line);
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Sora', sans-serif !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        color: var(--ink-500) !important;
        padding: 8px 6px !important;
        border-radius: 8px !important;
        flex: 1;
        text-align: center;
        background: transparent !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--teal-deep) !important;
        color: var(--white) !important;
        box-shadow: var(--shadow-sm);
    }
    .stTabs [data-baseweb="tab-panel"] {padding-top: 12px;}
    .stTabs [data-baseweb="tab-highlight"] {display: none;}

    /* ── Radio (SRL sub-toggle) ──────────────────────────────── */
    .stRadio > div {
        gap: 4px !important;
        background: var(--white);
        padding: 4px;
        border-radius: 10px;
        border: 1px solid var(--line);
        display: flex !important;
    }
    .stRadio > div > label {
        flex: 1;
        text-align: center;
        padding: 6px 0 !important;
        font-family: 'Sora', sans-serif !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        border-radius: 8px;
        cursor: pointer;
    }
    .stRadio input[type="radio"]:checked + div {
        background: var(--teal-vibrant);
        color: var(--white);
    }
    .stRadio label {font-family: 'Inter', sans-serif; font-size: 13px;}

    /* ── LOGIN PAGE — COMPACT, NO-SCROLL ──────────────────────── */
    .login-page {
        min-height: 100vh;
        background: var(--cream);
        position: relative;
        padding: 22px 18px 18px;
    }

    /* ONLY top-left & bottom-right triangles per feedback */
    .login-page::before {
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 110px; height: 110px;
        background: var(--teal-deep);
        opacity: 0.95;
        clip-path: polygon(0 0, 100% 0, 0 100%);
    }
    .login-page::after {
        content: "";
        position: absolute;
        bottom: 0; right: 0;
        width: 130px; height: 130px;
        background: var(--copper);
        opacity: 0.85;
        clip-path: polygon(100% 100%, 100% 0, 0 100%);
    }

    /* Logo block */
    .logo-block {
        position: relative; z-index: 5;
        padding-top: 36px;
        padding-left: 2px;
    }
    .logo-wordmark {
        font-family: 'Sora', sans-serif;
        font-size: 30px; font-weight: 800;
        color: var(--teal-deep);
        letter-spacing: 2px;
        line-height: 1;
    }
    .logo-wordmark .kinetiq {
        color: var(--copper);
        font-weight: 600;
        font-style: italic;
        margin-left: 4px;
        letter-spacing: 0.5px;
    }
    .logo-tag {
        font-family: 'Inter', sans-serif;
        font-size: 10px; font-weight: 500;
        color: var(--ink-500);
        letter-spacing: 1.8px;
        text-transform: uppercase;
        margin-top: 6px;
    }

    /* Hero headline */
    .hero-headline {
        position: relative; z-index: 5;
        margin-top: 24px;
        font-family: 'Sora', sans-serif;
        font-size: 28px;
        font-weight: 700;
        line-height: 1.15;
        color: var(--teal-deep);
        letter-spacing: -0.4px;
    }
    .hero-headline .accent {
        color: var(--copper);
        font-style: italic;
    }
    .hero-sub {
        position: relative; z-index: 5;
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: var(--ink-500);
        margin-top: 8px;
        line-height: 1.5;
        max-width: 320px;
    }

    /* Login form: pulled up, compact */
    .login-card-wrapper {
        position: relative; z-index: 5;
        margin-top: 22px;
    }
    .login-page [data-testid="stForm"] {
        background: var(--white);
        border-radius: 16px;
        padding: 18px 16px 16px;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--line);
    }

    .login-footer {
        position: relative; z-index: 5;
        margin-top: 14px;
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        color: var(--ink-500);
        line-height: 1.5;
    }
    .login-footer .powered {font-weight: 600; color: var(--ink-700);}
    .login-footer .group {opacity: 0.7; margin-top: 2px; display: block;}

    /* ── Sidebar ─────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: var(--white);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] .stMarkdown {
        font-family: 'Inter', sans-serif;
        color: var(--ink-900);
    }

    /* Expander */
    .streamlit-expanderHeader, [data-testid="stExpander"] summary {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: var(--teal-deep) !important;
    }

    /* Captions */
    .stCaption, [data-testid="stCaptionContainer"] {
        font-family: 'Inter', sans-serif !important;
        color: var(--ink-500) !important;
        font-size: 12px !important;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# DATA LAYER
# =============================================================================
@st.cache_data(ttl=300)
def load_data():
    if not DATA_FILE.exists():
        st.error(f"Data file not found at: {DATA_FILE}")
        st.stop()
    xl = pd.ExcelFile(DATA_FILE)
    return {
        "perf":  xl.parse("Performance"),
        "port":  xl.parse("Portfolio"),
        "prof":  xl.parse("Profitability"),
        "notif": xl.parse("Notification"),
        "org":   xl.parse("Org Hierarchy"),
    }


# =============================================================================
# AUTH
# =============================================================================
DEMO_PASSWORD = "arkin@2026"
def hash_pw(pw: str) -> str: return hashlib.sha256(pw.encode()).hexdigest()
DEMO_PW_HASH = hash_pw(DEMO_PASSWORD)


@st.cache_data(ttl=600)
def build_user_directory():
    data = load_data()
    org = data["org"]
    users = {}

    for _, r in org[org["Level"] == "RM"].iterrows():
        users[f"rm.{r['ID']}"] = {
            "name": r["Name"], "role": "Sales Manager", "level": "RM",
            "id": int(r["ID"]), "product": r["Product"],
            "zone": r["Zone"], "region": r["Region"], "pw_hash": DEMO_PW_HASH,
        }
    for _, r in org[org["Level"] == "ABM"].iterrows():
        users[f"abm.{r['ID']}"] = {
            "name": r["Name"], "role": "Area Business Manager", "level": "ABM",
            "id": int(r["ID"]), "product": r["Product"],
            "zone": r["Zone"], "region": r["Region"], "pw_hash": DEMO_PW_HASH,
        }
    for _, r in org[org["Level"] == "RBM"].iterrows():
        users[f"rbm.{r['ID']}"] = {
            "name": r["Name"], "role": "Regional Business Manager", "level": "RBM",
            "id": int(r["ID"]), "product": r["Product"],
            "zone": r["Zone"], "region": r["Region"], "pw_hash": DEMO_PW_HASH,
        }
    for _, r in org[org["Level"] == "ZH"].iterrows():
        users[f"zh.{r['ID']}"] = {
            "name": r["Name"], "role": "Zonal Head", "level": "ZH",
            "id": int(r["ID"]), "product": r["Product"],
            "zone": r["Zone"], "region": "All", "pw_hash": DEMO_PW_HASH,
        }

    # CXO / Central / Admin — see SRL
    users["cxo"] = {
        "name": "Chief Business Officer", "role": "CXO", "level": "CXO",
        "id": "CXO001", "product": "SRL", "zone": "All", "region": "All",
        "pw_hash": DEMO_PW_HASH,
    }
    users["central"] = {
        "name": "Central Analytics Lead", "role": "Central Team", "level": "CXO",
        "id": "CEN001", "product": "SRL", "zone": "All", "region": "All",
        "pw_hash": DEMO_PW_HASH,
    }
    users["admin"] = {
        "name": "System Administrator", "role": "Admin", "level": "Admin",
        "id": "ADM001", "product": "SRL", "zone": "All", "region": "All",
        "pw_hash": DEMO_PW_HASH,
    }
    return users


def authenticate(username, password):
    users = build_user_directory()
    u = users.get(username.strip().lower())
    if u and hash_pw(password) == u["pw_hash"]:
        return u
    return None


# =============================================================================
# RBAC + PRODUCT SCOPING
# =============================================================================
def scope_data(df, user, product_override=None):
    """Filter df by user's org level and product.
    product_override: for CXO/Central — pass 'STLAP', 'Wheels', or 'SRL'
                      to switch the view in real time.
    """
    if df is None or df.empty:
        return df
    level = user["level"]
    prod = product_override if product_override else user["product"]

    # Product filter: SRL means both, anything else is single-product
    if prod in ("STLAP", "Wheels") and "Product" in df.columns:
        df = df[df["Product"] == prod]
    # If prod == "SRL", don't filter — show both STLAP + Wheels

    # Org-level filter
    if level in ("CXO", "Admin"):
        return df
    if level == "ZH" and "ZH ID" in df.columns:
        return df[df["ZH ID"] == user["id"]]
    if level == "RBM" and "RBM ID" in df.columns:
        return df[df["RBM ID"] == user["id"]]
    if level == "ABM" and "ABM ID" in df.columns:
        return df[df["ABM ID"] == user["id"]]
    if level == "RM":
        col = "Emp ID" if "Emp ID" in df.columns else "RM ID"
        return df[df[col] == user["id"]] if col in df.columns else df
    return df.iloc[0:0]


# =============================================================================
# UI HELPERS
# =============================================================================
def brand_bar(user, current_product=None):
    """Top branded bar with logo + user info + product chip."""
    display_prod = current_product if current_product else user["product"]
    prod_chip = f'<span class="chip">{display_prod}</span>'

    st.markdown(f"""
    <div class="brand-bar">
      <div class="brand-row">
        <span class="b1">ARKA</span><span class="b2">KinetiQ</span>
      </div>
      <div class="b-meta">{user['name']} · {user['role']} · {user.get('zone','—')} {prod_chip}</div>
    </div>
    """, unsafe_allow_html=True)


def kpi_tile(label, value, sub="", trend=None):
    trend_html = ""
    if trend is not None:
        cls = "kpi-up" if trend >= 0 else "kpi-down"
        arrow = "▲" if trend >= 0 else "▼"
        trend_html = f'<span class="{cls}"> {arrow} {abs(trend):.1f}%</span>'
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}{trend_html}</div>
      <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def section(title, emoji=""):
    icon = f"{emoji} " if emoji else ""
    st.markdown(f'<div class="section-title"><span class="accent-dot"></span>{icon}{title}</div>',
                unsafe_allow_html=True)


def mailto_link(to_email, subject, body, cc_list=None):
    cc = ",".join(cc_list) if cc_list else ""
    return f"mailto:{to_email}?cc={cc}&subject={quote(subject)}&body={quote(body)}"


def status_chip(text, kind="green"):
    return f'<span class="chip-{kind}">{text}</span>'


# =============================================================================
# PLOTLY THEMING
# =============================================================================
ARKA_PALETTE = ["#0F3D3E", "#1FA89A", "#D4936B", "#5BAFA8", "#E6B998", "#2D5A5B"]


def apply_plotly_theme(fig, height=240):
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Inter, sans-serif", size=11, color="#0F3D3E"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.18, font=dict(size=10, color="#0F3D3E")),
        xaxis=dict(showgrid=False, color="#6B8788"),
        yaxis=dict(gridcolor="#E5EAEA", color="#6B8788"),
    )
    return fig


# =============================================================================
# SALES MANAGER (RM) — TABBED
# =============================================================================
def render_sales_manager(user, data):
    perf  = scope_data(data["perf"], user)
    port  = scope_data(data["port"], user)
    prof  = scope_data(data["prof"], user)
    notif = scope_data(data["notif"], user)

    if perf.empty:
        st.warning("No performance data found for your profile.")
        return
    row = perf.iloc[0]

    tab_focus, tab_perf, tab_port = st.tabs(["🎯 Focus", "📊 Performance", "💼 Portfolio"])

    # ─── FOCUS TAB ────────────────────────────────────────────────────────
    with tab_focus:
        section("AI Nudges for You", "🤖")
        if not notif.empty:
            nrow = notif.iloc[0]
            for i in range(1, 6):
                n = nrow.get(f"Notification {i}", "")
                if pd.notna(n) and str(n).strip():
                    st.markdown(f'<div class="nudge-card">💡 {n}</div>', unsafe_allow_html=True)

        section("Key Announcements", "📢")
        st.markdown('<div class="announce-card">📌 Quarterly target review on 30th — submit branch numbers by EOD Friday.</div>', unsafe_allow_html=True)
        st.markdown('<div class="announce-card">🎯 New TAT SLA: Login → Sanction within 5 working days from June.</div>', unsafe_allow_html=True)

        section("Key Actionables Today", "✅")
        gap_disb = max(0, int(row["Target Disb #"] - row["Actual Disb #"]))
        if gap_disb > 0:
            st.markdown(f'<div class="action-card">🔥 Close {gap_disb} more disbursements to hit monthly target.</div>', unsafe_allow_html=True)
        if row["Actual PF %"] < row["Target PF %"]:
            st.markdown(f'<div class="action-card">💰 PF% at {row["Actual PF %"]:.2f}% vs target {row["Target PF %"]:.2f}% — push fee collection.</div>', unsafe_allow_html=True)
        if row["Actual Conversion %"] < row["Target Conversion %"]:
            st.markdown(f'<div class="action-card">🎯 Conversion {row["Actual Conversion %"]:.1f}% below target {row["Target Conversion %"]:.1f}% — reduce TAT.</div>', unsafe_allow_html=True)

    # ─── PERFORMANCE TAB ──────────────────────────────────────────────────
    with tab_perf:
        section("Funnel — Login → Sanction → Disb", "📊")
        c = st.columns(3)
        with c[0]: kpi_tile("Logins", f"{int(row['Actual Login #'])}", f"Tgt {int(row['Target Login #'])}")
        with c[1]: kpi_tile("Sanctions", f"{int(row['Actual Sanction #'])}", f"Tgt {int(row['Target Sanction #'])}")
        with c[2]: kpi_tile("Disb", f"{int(row['Actual Disb #'])}", f"Tgt {int(row['Target Disb #'])}")

        fig = go.Figure(go.Funnel(
            y=["Logins", "Sanctions", "Disbursements"],
            x=[row["Actual Login #"], row["Actual Sanction #"], row["Actual Disb #"]],
            marker={"color": ["#1FA89A", "#0F3D3E", "#D4936B"]},
            textposition="inside", textinfo="value+percent initial",
        ))
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

        section("Conversion & Mix", "🎯")
        c1, c2 = st.columns(2)
        with c1:
            conv_gap = row["Actual Conversion %"] - row["Target Conversion %"]
            kpi_tile("Conversion", f"{row['Actual Conversion %']:.1f}%",
                     f"Tgt {row['Target Conversion %']:.1f}%", trend=conv_gap)
            kpi_tile("IRR Mix", f"{row['IRR Mix %']:.2f}%", "Portfolio yield")
        with c2:
            kpi_tile("LTV", f"{row['LTV %']:.1f}%", "Loan to Value")
            kpi_tile("Avg Ticket", f"₹{row['Avg Ticket Size (Rs L)']:.1f} L", "Per case")

        section("Disbursement Trend", "📈")
        trend_df = pd.DataFrame({
            "Month": ["M-3", "M-2", "M-1", "Current"],
            "Disb #": [row["M-3 Disb #"], row["M-2 Disb #"], row["M-1 Disb #"], row["Actual Disb #"]],
            "Target": [row["Target Disb #"]] * 4,
        })
        fig = go.Figure()
        fig.add_bar(x=trend_df["Month"], y=trend_df["Disb #"], name="Actual", marker_color="#1FA89A")
        fig.add_scatter(x=trend_df["Month"], y=trend_df["Target"], name="Target",
                        mode="lines+markers", line=dict(color="#D4936B", dash="dash", width=2),
                        marker=dict(size=8))
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

        section("Achievement & Productivity", "⚡")
        c1, c2 = st.columns(2)
        with c1:
            kpi_tile("CM Achievement", f"{row['CM Achievement %']:.1f}%", "Of monthly target")
            kpi_tile("PF %", f"{row['Actual PF %']:.2f}%", f"Tgt {row['Target PF %']:.2f}%")
        with c2:
            kpi_tile("Cross-sell", f"{row['Cross Sell %']:.1f}%", "Insurance + bundle")
            kpi_tile("Productivity", f"{row['Productivity (Disb/RM)']:.1f}", "Disb/RM/month")

        fee_income = (row["Actual Disb Amount (Rs Cr)"] * row["Actual PF %"] / 100 +
                      row["Actual Disb Amount (Rs Cr)"] * row["Actual Insurance %"] / 100)
        kpi_tile("Fee Income (PF + Ins)", f"₹{fee_income:.3f} Cr", "This month")

    # ─── PORTFOLIO TAB ────────────────────────────────────────────────────
    with tab_port:
        if not prof.empty:
            prow = prof.iloc[0]
            section("Portfolio Health", "💼")
            c1, c2 = st.columns(2)
            with c1:
                kpi_tile("AUM", f"₹{prow['AUM (Rs Cr)']:.1f} Cr", "Customers acquired")
                kpi_tile("Bounce %", f"{prow['AUM Bounce %']:.1f}%", "Portfolio")
                kpi_tile("30+ DPD", f"{prow['30+ DPD %']:.1f}%", "Delinquency")
                kpi_tile("EMI Eff.", f"{prow['EMI Collection Efficiency %']:.1f}%", "Collection")
            with c2:
                kpi_tile("Exit Rate", f"{prow['Exit Rate %']:.1f}%", "Customers leaving")
                kpi_tile("Avg LTV", f"{prow['Avg LTV %']:.1f}%", "Portfolio")
                kpi_tile("NPA %", f"{prow['NPA %']:.2f}%", "Non-performing")
                kpi_tile("Portfolio IRR", f"{prow['Portfolio IRR %']:.2f}%", "Yield")

        if not port.empty:
            section("Asset Type Mix", "🏷️")
            asset_mix = port.groupby("Asset Type")["POS (Rs Cr)"].sum().reset_index()
            fig = px.pie(asset_mix, names="Asset Type", values="POS (Rs Cr)",
                         color_discrete_sequence=ARKA_PALETTE)
            apply_plotly_theme(fig, height=270)
            st.plotly_chart(fig, use_container_width=True)

            section("PAR Bucket Distribution", "📊")
            par_mix = port.groupby("PAR Bucket")["POS (Rs Cr)"].sum().reset_index()
            par_order = ["Current", "1-30 DPD", "31-60 DPD", "61-90 DPD", "90+ DPD"]
            par_mix["PAR Bucket"] = pd.Categorical(par_mix["PAR Bucket"], categories=par_order, ordered=True)
            par_mix = par_mix.sort_values("PAR Bucket")
            fig = px.bar(par_mix, x="PAR Bucket", y="POS (Rs Cr)",
                         color="PAR Bucket",
                         color_discrete_sequence=["#1FA89A","#5BAFA8","#D4936B","#E6B998","#C8553D"])
            apply_plotly_theme(fig, height=240)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# TEAM LEADER (ABM) and SENIOR LEADERSHIP (RBM/ZH/BH) — same structure
# =============================================================================
def render_leader(user, data, product_override=None):
    perf = scope_data(data["perf"], user, product_override)
    prof = scope_data(data["prof"], user, product_override)
    port = scope_data(data["port"], user, product_override)

    if perf.empty:
        st.warning("No team data found for your profile.")
        return

    tab_focus, tab_perf, tab_port, tab_prof = st.tabs(
        ["🎯 Focus", "📊 Performance", "💼 Portfolio", "💵 Profitability"]
    )

    # ─── FOCUS TAB — escalations + low performers ────────────────────────
    with tab_focus:
        section("Focus of the Month", "🎯")
        st.caption("Low-performing RMs with vintage > 3 months — need attention")
        low_perf = perf[
            (perf["Actual Disb #"] < perf["Target Disb #"] * 0.6) &
            (perf["M-3 Disb #"] > 0)
        ][["EMP Name", "Actual Disb #", "Target Disb #",
           "M-1 Disb #", "M-2 Disb #", "M-3 Disb #"]].head(10)
        if low_perf.empty:
            st.success("✅ No low performers flagged this month.")
        else:
            low_perf = low_perf.rename(columns={"EMP Name": "RM"})
            st.dataframe(low_perf, use_container_width=True, hide_index=True)

        section("Escalation Tracker", "🚨")
        st.caption("RMs with zero disbursement — auto-escalation ladder")
        zero_disb = perf[perf["Actual Disb #"] == 0].copy()
        if not zero_disb.empty:
            def escalate(r):
                zeros = sum(1 for m in [r["M-1 Disb #"], r["M-2 Disb #"], r["M-3 Disb #"]] if m == 0)
                if zeros == 0: return ("Month 1 — AMBER", "amber", "Visible to ABM")
                elif zeros == 1: return ("Month 2 — AMBER", "amber", "Escalated to RBM")
                elif zeros == 2: return ("Month 3 — RED", "red", "Escalated to ZH")
                else: return ("Critical — RED", "red", "Visible to Business Head")
            zero_disb[["Status", "Kind", "Visible To"]] = zero_disb.apply(
                lambda r: pd.Series(escalate(r)), axis=1)
            for _, r in zero_disb.head(10).iterrows():
                chip = status_chip(r["Status"], r["Kind"])
                st.markdown(
                    f'<div class="kpi-card" style="padding:10px 12px;">'
                    f'<b>{r["EMP Name"]}</b> &nbsp;{chip}<br>'
                    f'<span class="kpi-sub">{r["Visible To"]} · '
                    f'M-1: {int(r["M-1 Disb #"])} | M-2: {int(r["M-2 Disb #"])} | '
                    f'M-3: {int(r["M-3 Disb #"])}</span></div>',
                    unsafe_allow_html=True)
        else:
            st.success("✅ All RMs have disbursed this month.")

        section("Quick Nudge", "✉️")
        bottom = perf.sort_values("Actual Disb #").head(15)
        rm_pick = st.selectbox("Pick RM to nudge", bottom["EMP Name"].tolist(), key="nudge_pick")
        if rm_pick:
            rm_row = bottom[bottom["EMP Name"] == rm_pick].iloc[0]
            rm_email = f"{rm_pick.lower().replace(' ', '.')}@arkafincap.com"
            body = (
                f"Hi {rm_pick},\n\n"
                f"Your current month performance shows {int(rm_row['Actual Disb #'])} "
                f"disbursements against a target of {int(rm_row['Target Disb #'])}. "
                f"Your conversion stands at {rm_row['Actual Conversion %']:.1f}% "
                f"vs target {rm_row['Target Conversion %']:.1f}%.\n\n"
                f"Please prioritise pipeline closure this week. Let's discuss in our next 1:1.\n\n"
                f"Regards,\n{user['name']}"
            )
            cc = [f"rbm.{user.get('region','').lower().replace(' ', '')}@arkafincap.com",
                  f"zh.{user.get('zone','').lower()}@arkafincap.com"]
            link = mailto_link(rm_email, f"Performance Nudge — {rm_pick}", body, cc)
            st.markdown(f'<a href="{link}" style="text-decoration:none;"><button style="width:100%;'
                        f'background:#0F3D3E;color:white;border:none;padding:12px;'
                        f'border-radius:10px;font-family:Sora,sans-serif;font-weight:600;'
                        f'font-size:14px;cursor:pointer;letter-spacing:0.3px;">'
                        f'📧 Open Email — Nudge {rm_pick}</button></a>',
                        unsafe_allow_html=True)

    # ─── PERFORMANCE TAB ──────────────────────────────────────────────────
    with tab_perf:
        section("Team Snapshot", "👥")
        n_rms = perf["Emp ID"].nunique()
        total_disb = int(perf["Actual Disb #"].sum())
        total_tgt = int(perf["Target Disb #"].sum())
        disb_amt = perf["Actual Disb Amount (Rs Cr)"].sum()

        c1, c2 = st.columns(2)
        with c1:
            kpi_tile("RMs", f"{n_rms}", "Active")
            kpi_tile("Disb #", f"{total_disb}", f"Tgt {total_tgt}",
                     trend=(total_disb - total_tgt) / max(1, total_tgt) * 100)
        with c2:
            kpi_tile("Disb Amount", f"₹{disb_amt:.1f} Cr", "MTD")
            kpi_tile("Avg Conv.", f"{perf['Actual Conversion %'].mean():.1f}%", "Login→Disb")

        section("Leaderboard — Disbursements", "🏆")
        lb = perf.sort_values("Actual Disb #", ascending=False).head(10)[
            ["EMP Name", "Actual Disb #", "Target Disb #", "Actual Conversion %", "IRR Mix %"]
        ].rename(columns={"EMP Name": "RM", "Actual Disb #": "Disb",
                           "Target Disb #": "Tgt", "Actual Conversion %": "Conv%",
                           "IRR Mix %": "IRR%"})
        st.dataframe(lb, use_container_width=True, hide_index=True)

        section("Leaderboard — IRR Mix", "💰")
        irr_lb = perf.sort_values("IRR Mix %", ascending=False).head(10)[
            ["EMP Name", "IRR Mix %", "Actual Disb #", "LTV %"]
        ].rename(columns={"EMP Name": "RM", "IRR Mix %": "IRR%",
                           "Actual Disb #": "Disb"})
        st.dataframe(irr_lb, use_container_width=True, hide_index=True)

        if len(perf) >= 2:
            section("Peer Leaderboard — 3M Avg", "👥")
            peer = perf.copy()
            peer["3M Avg Disb"] = (peer["M-1 Disb #"] + peer["M-2 Disb #"] + peer["M-3 Disb #"]) / 3
            peer = peer.sort_values("Actual Disb #", ascending=False)
            show = peer[["EMP Name", "Actual Disb #", "3M Avg Disb", "IRR Mix %"]].head(15)
            show = show.rename(columns={"EMP Name": "RM", "Actual Disb #": "Disb", "IRR Mix %": "IRR%"})
            show["3M Avg Disb"] = show["3M Avg Disb"].round(1)
            st.dataframe(show, use_container_width=True, hide_index=True)

        # Region/Zone breakdown for senior leadership
        if user["level"] in ("RBM", "ZH", "CXO"):
            section("Performance by Region", "🗺️")
            region_perf = perf.groupby("Region").agg(
                Disb=("Actual Disb #", "sum"),
                Target=("Target Disb #", "sum"),
                DisbAmt=("Actual Disb Amount (Rs Cr)", "sum"),
            ).reset_index()
            region_perf["Ach %"] = (region_perf["Disb"] / region_perf["Target"] * 100).round(1)
            st.dataframe(region_perf, use_container_width=True, hide_index=True)
            fig = px.bar(region_perf, x="Region", y=["Disb", "Target"], barmode="group",
                         color_discrete_sequence=["#1FA89A", "#D4936B"])
            apply_plotly_theme(fig, height=260)
            st.plotly_chart(fig, use_container_width=True)

            section("Top & Bottom ABMs", "🏆")
            abm_perf = perf.groupby(["ABM Name"]).agg(
                Disb=("Actual Disb #", "sum"),
                Target=("Target Disb #", "sum"),
            ).reset_index()
            abm_perf["Ach %"] = (abm_perf["Disb"] / abm_perf["Target"] * 100).round(1)
            st.write("**Top 5**")
            st.dataframe(abm_perf.nlargest(5, "Ach %"), use_container_width=True, hide_index=True)
            st.write("**Bottom 5**")
            st.dataframe(abm_perf.nsmallest(5, "Ach %"), use_container_width=True, hide_index=True)

    # ─── PORTFOLIO TAB ────────────────────────────────────────────────────
    with tab_port:
        if not prof.empty:
            section("Portfolio Health — Aggregate", "💼")
            c1, c2 = st.columns(2)
            with c1:
                kpi_tile("Total AUM", f"₹{prof['AUM (Rs Cr)'].sum():.1f} Cr", "Book")
                kpi_tile("Avg Bounce %", f"{prof['AUM Bounce %'].mean():.1f}%", "Team avg")
                kpi_tile("Avg 30+ DPD", f"{prof['30+ DPD %'].mean():.1f}%", "Team avg")
                kpi_tile("EMI Eff.", f"{prof['EMI Collection Efficiency %'].mean():.1f}%", "Collection")
            with c2:
                kpi_tile("Exit Rate", f"{prof['Exit Rate %'].mean():.1f}%", "Avg")
                kpi_tile("Avg LTV", f"{prof['Avg LTV %'].mean():.1f}%", "Portfolio")
                kpi_tile("NPA %", f"{prof['NPA %'].mean():.2f}%", "Team avg")
                kpi_tile("Portfolio IRR", f"{prof['Portfolio IRR %'].mean():.2f}%", "Yield")

        if not port.empty:
            section("Asset Mix", "🏷️")
            asset_mix = port.groupby("Asset Type")["POS (Rs Cr)"].sum().reset_index()
            fig = px.pie(asset_mix, names="Asset Type", values="POS (Rs Cr)",
                         color_discrete_sequence=ARKA_PALETTE)
            apply_plotly_theme(fig, height=270)
            st.plotly_chart(fig, use_container_width=True)

    # ─── PROFITABILITY TAB ────────────────────────────────────────────────
    with tab_prof:
        if not prof.empty:
            section("Profitability KPIs", "💵")
            c1, c2 = st.columns(2)
            with c1:
                kpi_tile("AUM / RM", f"₹{prof['AUM/RM (Rs Cr)'].mean():.2f} Cr", "Avg")
                kpi_tile("Branch PAT %", f"{prof['PAT % (Before HO Allocation)'].mean():.2f}%", "Pre-HO")
            with c2:
                kpi_tile("Disb / RM", f"₹{prof['Disb/RM (Rs Cr)'].mean():.2f} Cr", "Avg")
                kpi_tile("Gross Margin", f"{prof['Gross Margin %'].mean():.2f}%", "Avg")

            section("Path to 2% RoA", "🎯")
            avg_pat = prof["PAT % (Before HO Allocation)"].mean()
            avg_aum_per_rm = prof["AUM/RM (Rs Cr)"].mean()
            avg_yield = prof["Yield %"].mean()
            avg_cost = prof["Branch Cost (Rs Cr)"].mean()
            recos = []
            if avg_pat < 2.0:
                gap = 2.0 - avg_pat
                recos.append(f"📈 **Current PAT% is {avg_pat:.2f}%, gap to 2% RoA is {gap:.2f}pp.**")
                if avg_aum_per_rm < 12:
                    recos.append(f"• **AUM/RM lever**: Avg AUM/RM at ₹{avg_aum_per_rm:.1f}Cr. Push to ₹15Cr — adds ~{(15-avg_aum_per_rm)*avg_yield/100:.2f}% to margin.")
                if avg_yield < 15:
                    recos.append(f"• **Yield lever**: Avg yield {avg_yield:.2f}%. Shift mix to higher-IRR products — adds ~0.5–1pp.")
                if avg_cost > 1.5:
                    recos.append(f"• **Cost lever**: Avg branch cost ₹{avg_cost:.2f}Cr. Trim 10% via shared services — adds ~{avg_cost*0.1:.2f}pp.")
            else:
                recos.append(f"✅ Already at {avg_pat:.2f}% — above 2% RoA target.")
            for r in recos:
                st.markdown(r)

            section("Active Escalations Roll-up", "🚨")
            zero = perf[perf["Actual Disb #"] == 0]
            n_amber = len(zero[zero["M-1 Disb #"] > 0])
            n_red = len(zero[(zero["M-1 Disb #"] == 0) & (zero["M-2 Disb #"] == 0)])
            c1, c2 = st.columns(2)
            with c1:
                kpi_tile("Amber Alerts", f"{n_amber}", "1st-2nd month zero")
            with c2:
                kpi_tile("Red Alerts", f"{n_red}", "3+ month zero")


# =============================================================================
# CXO / CENTRAL — SRL view with STLAP / Wheels sub-toggle
# =============================================================================
def render_cxo(user, data):
    # SRL sub-toggle at the top
    section("Product View", "🎛️")
    product_view = st.radio(
        "Product",
        ["SRL", "STLAP", "Wheels"],
        horizontal=True,
        key="cxo_product_view",
        label_visibility="collapsed",
    )

    # Update brand bar chip — but we've already rendered it.
    # Workaround: render small status line indicating current view
    st.markdown(f'<div style="font-family:Inter,sans-serif;font-size:11px;color:#6B8788;'
                f'margin:-4px 0 8px 2px;">Currently viewing: <b style="color:#0F3D3E;">'
                f'{product_view}</b> {"(STLAP + Wheels combined)" if product_view=="SRL" else ""}</div>',
                unsafe_allow_html=True)

    # Reuse the leader layout with product_override
    render_leader(user, data, product_override=product_view)


# =============================================================================
# ADMIN
# =============================================================================
def render_admin(user, data):
    section("Admin Console", "⚙️")
    st.caption("Upload data, dispatch nudges, manage user access.")

    tab1, tab2, tab3 = st.tabs(["📤 Upload Data", "🔔 Notifications", "👤 Users"])

    with tab1:
        st.write("**Upload the latest monthly data file**")
        up = st.file_uploader("Choose Excel file", type=["xlsx"])
        if up is not None:
            target = DATA_DIR / "arkin_dummy_data.xlsx"
            DATA_DIR.mkdir(exist_ok=True)
            with open(target, "wb") as f:
                f.write(up.getbuffer())
            st.cache_data.clear()
            st.success(f"✅ Uploaded {up.name} → {target}. Cache cleared.")

        st.divider()
        st.write("**Current data file**")
        if DATA_FILE.exists():
            sz = DATA_FILE.stat().st_size / 1024
            mt = datetime.fromtimestamp(DATA_FILE.stat().st_mtime)
            st.info(f"📁 `{DATA_FILE.name}` · {sz:.1f} KB · last modified {mt:%d-%b-%Y %H:%M}")

    with tab2:
        st.write("**Dispatch notifications**")
        notif = data["notif"]
        st.write(f"Total notifications queued: **{len(notif)}**")
        st.dataframe(notif[["RM Name", "Product", "Notification 1"]].head(10),
                     use_container_width=True, hide_index=True)
        st.button("🚀 Dispatch All Notifications (mock)", use_container_width=True)

    with tab3:
        st.write("**User directory**")
        org = data["org"]
        st.dataframe(
            org.groupby(["Level", "Product"]).size().reset_index(name="Count"),
            use_container_width=True, hide_index=True)
        lvl = st.selectbox("Filter by level",
                           ["All"] + sorted(org["Level"].unique().tolist()))
        view = org if lvl == "All" else org[org["Level"] == lvl]
        st.dataframe(view.head(50), use_container_width=True, hide_index=True)


# =============================================================================
# LOGIN
# =============================================================================
def login_screen():
    st.markdown("""
    <div class="login-page">
      <div class="logo-block">
        <div class="logo-wordmark">ARKA<span class="kinetiq">KinetiQ</span></div>
        <div class="logo-tag">INTELLIGENCE IN MOTION</div>
      </div>

      <div class="hero-headline">
        Get ahead,<br>
        <span class="accent">every day.</span>
      </div>
      <div class="hero-sub">
        Your sales intelligence companion. Numbers, nudges, and next steps —
        crafted for the way you actually work.
      </div>

      <div class="login-card-wrapper">
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Employee ID", placeholder="e.g. rm.3001",
                                 label_visibility="visible")
        password = st.text_input("Password", type="password",
                                 placeholder="Demo: arkin@2026",
                                 label_visibility="visible")
        submitted = st.form_submit_button("Sign in →", use_container_width=True)
        if submitted:
            u = authenticate(username, password)
            if u:
                st.session_state["user"] = u
                st.session_state["username"] = username.strip().lower()
                st.rerun()
            else:
                st.error("❌ Invalid Employee ID or password.")

    st.markdown("""
      </div>

      <div class="login-footer">
        <span class="powered">Powered by Arka Fincap</span>
        <span class="group">A Kirloskar Group company</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🧪 Demo credentials"):
        st.markdown(f"""
**Password for all demo accounts:** `{DEMO_PASSWORD}`

| Employee ID | Role | Product |
|---|---|---|
| `rm.3001` | Sales Manager | STLAP |
| `rm.4001` | Sales Manager | Wheels |
| `abm.2001` | Area Business Manager | STLAP |
| `abm.2101` | Area Business Manager | Wheels |
| `rbm.201` | Regional Business Manager | STLAP |
| `rbm.216` | Regional Business Manager | Wheels |
| `zh.131` | Zonal Head | STLAP |
| `zh.135` | Zonal Head | Wheels |
| `cxo` | CXO | SRL (STLAP + Wheels) |
| `central` | Central Team | SRL |
| `admin` | System Admin | SRL |
        """)


# =============================================================================
# MAIN
# =============================================================================
def main():
    data = load_data()

    if "user" not in st.session_state:
        login_screen()
        return

    st.markdown('<div class="page">', unsafe_allow_html=True)

    user = st.session_state["user"]
    brand_bar(user)

    with st.sidebar:
        st.markdown(f"### {user['name']}")
        st.caption(user["role"])
        st.caption(f"Product: {user['product']}")
        st.caption(f"Zone: {user.get('zone', '—')}")
        st.divider()
        if st.button("Sign out", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    level = user["level"]
    if level == "RM":
        render_sales_manager(user, data)
    elif level == "ABM":
        render_leader(user, data)
    elif level in ("RBM", "ZH"):
        render_leader(user, data)
    elif level == "CXO":
        render_cxo(user, data)
    elif level == "Admin":
        render_admin(user, data)

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
