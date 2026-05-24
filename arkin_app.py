"""
Arka KinetiQ — Intelligence in Motion
======================================
4-month multi-period data (Jan-26 to Apr-26).
Real escalation logic across months.

KEY FIX: Uses st.html() for CSS injection (Streamlit 1.40+ / Python 3.14 compatible).
st.markdown() with <style> tags is blocked by Streamlit Cloud security policy.
st.html() is the approved method for custom HTML/CSS.

Run: streamlit run arkin_app.py --server.port=8501 --server.address=0.0.0.0
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
DATA_DIR  = Path(__file__).parent / "arkin"
DATA_FILE = DATA_DIR / "arkin_dummy_data.xlsx"

MONTH_ORDER   = ["Jan-26", "Feb-26", "Mar-26", "Apr-26"]
CURRENT_MONTH = "Apr-26"

st.set_page_config(
    page_title="Arka KinetiQ",
    page_icon="◬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# CSS — injected via st.html() which is safe in Streamlit 1.40+ / Python 3.14
# st.markdown() with <style> is now blocked by Streamlit Cloud security policy.
# =============================================================================
def inject_css():
    st.html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
    --teal:    #0F3D3E;
    --teal2:   #1FA89A;
    --teal-bg: #E6F4F2;
    --copper:  #D4936B;
    --cop-bg:  #FDF4ED;
    --cream:   #F6F8F8;
    --white:   #FFFFFF;
    --ink1:    #0F3D3E;
    --ink2:    #2D5A5B;
    --ink3:    #6B8788;
    --line:    #E5EAEA;
    --sh-sm:   0 1px 3px rgba(15,61,62,0.06);
    --sh-md:   0 4px 12px rgba(15,61,62,0.08);
    --sh-lg:   0 12px 32px rgba(15,61,62,0.12);
}

/* Strip Streamlit chrome */
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none; }
.stApp > header { height: 0 !important; }
.block-container { padding: 0 !important; max-width: 480px !important; background: var(--cream); }
.stApp { background: var(--cream); font-family: 'Inter', sans-serif; color: var(--ink1); }
.page { padding: 14px 14px 80px; }

/* Brand bar */
.brand-bar {
    background: var(--teal); color: #fff;
    padding: 14px 16px; border-radius: 14px;
    margin-bottom: 4px; position: relative; overflow: hidden;
}
.brand-bar::after {
    content: ""; position: absolute; top: -25px; right: -25px;
    width: 80px; height: 80px; background: var(--copper);
    clip-path: polygon(50% 0%,100% 100%,0% 100%); opacity: .35;
}
.brand-bar-inner { position: relative; z-index: 2; }
.bb-logo { display: flex; align-items: baseline; gap: 6px; margin-bottom: 5px; }
.bb-arka { font-family: 'Sora', sans-serif; font-weight: 800; font-size: 17px; letter-spacing: 2px; color: #fff; }
.bb-kq   { font-family: 'Sora', sans-serif; font-weight: 500; font-size: 15px; font-style: italic; color: var(--copper); }
.bb-meta { font-family: 'Inter', sans-serif; font-size: 11px; opacity: .85; line-height: 1.5; }
.bb-chip { background: rgba(255,255,255,.15); color: #fff; padding: 2px 8px;
           border-radius: 10px; font-size: 10px; font-weight: 600; margin-left: 4px; }

/* KPI tiles */
.kpi-card { background: #fff; border-radius: 12px; padding: 12px 13px;
            border: 1px solid var(--line); box-shadow: var(--sh-sm); margin-bottom: 8px; }
.kpi-label { font-size: 10px; font-weight: 600; color: var(--ink3);
             text-transform: uppercase; letter-spacing: .6px; }
.kpi-value { font-family: 'Sora', sans-serif; font-size: 22px; font-weight: 700;
             color: var(--ink1); margin: 4px 0; line-height: 1.1; }
.kpi-sub   { font-size: 11px; color: var(--ink3); font-weight: 500; }
.kpi-up    { color: var(--teal2); font-size: 12px; }
.kpi-down  { color: #C8553D; font-size: 12px; }

/* Info cards */
.nudge-card    { background: var(--cop-bg); border-left: 3px solid var(--copper);
                 padding: 12px 14px; border-radius: 8px; margin-bottom: 8px;
                 font-size: 13px; line-height: 1.5; color: #6B3F1F; }
.announce-card { background: var(--teal-bg); border-left: 3px solid var(--teal2);
                 padding: 12px 14px; border-radius: 8px; margin-bottom: 8px;
                 font-size: 13px; line-height: 1.5; color: var(--teal); }
.action-card   { background: #FDECEA; border-left: 3px solid #C8553D;
                 padding: 12px 14px; border-radius: 8px; margin-bottom: 8px;
                 font-size: 13px; line-height: 1.5; color: #7A1F0E; }
.esc-card      { background: #fff; border-radius: 10px; border: 1px solid var(--line);
                 padding: 10px 12px; margin-bottom: 8px; box-shadow: var(--sh-sm); }

/* Status chips */
.chip-amber { background: var(--cop-bg); color: #6B3F1F;
              padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600; }
.chip-red   { background: #FDECEA; color: #7A1F0E;
              padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600; }
.chip-green { background: var(--teal-bg); color: var(--teal);
              padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600; }

/* Section heading */
.sec { font-family: 'Sora', sans-serif; font-size: 13px; font-weight: 700;
       color: var(--ink1); margin: 14px 0 8px; letter-spacing: .2px; }
.sec .dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%;
            background: var(--copper); margin-right: 8px; vertical-align: middle; }

/* Buttons */
.stButton button {
    width: 100%; background: var(--teal) !important; color: #fff !important;
    border: none !important; border-radius: 10px !important; padding: 11px 16px !important;
    font-family: 'Sora', sans-serif !important; font-weight: 600 !important;
    font-size: 14px !important; letter-spacing: .3px;
}
.stButton button:hover { background: var(--teal2) !important; }

/* Inputs */
.stTextInput input, .stSelectbox > div > div {
    border-radius: 10px !important; border: 1.5px solid var(--line) !important;
    font-family: 'Inter', sans-serif !important; font-size: 14px !important;
    padding: 10px 14px !important; background: #fff !important;
}
.stTextInput input:focus {
    border-color: var(--copper) !important;
    box-shadow: 0 0 0 3px rgba(212,147,107,.15) !important;
}
.stTextInput label, .stSelectbox label {
    font-family: 'Inter', sans-serif !important; font-size: 11px !important;
    font-weight: 600 !important; color: var(--ink2) !important;
    text-transform: uppercase; letter-spacing: .5px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: #fff; border-radius: 10px;
    padding: 4px; border: 1px solid var(--line);
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Sora', sans-serif !important; font-size: 12px !important;
    font-weight: 600 !important; color: var(--ink3) !important;
    padding: 8px 4px !important; border-radius: 8px !important;
    flex: 1; background: transparent !important; border: none !important;
}
.stTabs [aria-selected="true"] { background: var(--teal) !important; color: #fff !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 12px; }
.stTabs [data-baseweb="tab-highlight"] { display: none; }

/* Radio */
.stRadio > div {
    gap: 4px !important; background: #fff; padding: 4px;
    border-radius: 10px; border: 1px solid var(--line); display: flex !important;
}
.stRadio label { font-family: 'Inter', sans-serif; font-size: 13px; }

/* ── LOGIN — compact, single screen ────────────────────────── */
.login-outer {
    min-height: 100vh; background: var(--cream);
    position: relative; overflow: hidden;
}
.login-outer::before {
    content: ""; position: fixed; top: 0; left: 0;
    width: 88px; height: 88px; background: var(--teal);
    clip-path: polygon(0 0,100% 0,0 100%); z-index: 1;
}
.login-outer::after {
    content: ""; position: fixed; bottom: 0; right: 0;
    width: 100px; height: 100px; background: var(--copper);
    clip-path: polygon(100% 100%,100% 0,0 100%); z-index: 1; opacity: .88;
}
.login-inner {
    position: relative; z-index: 5;
    padding: 104px 22px 24px; max-width: 440px; margin: 0 auto;
}
.login-arka {
    font-family: 'Sora', sans-serif; font-weight: 800;
    font-size: 30px; color: var(--teal); letter-spacing: 2px;
}
.login-kq {
    font-family: 'Sora', sans-serif; font-weight: 500;
    font-size: 22px; color: var(--copper); font-style: italic;
    letter-spacing: .5px; margin-left: 6px;
}
.login-tag {
    font-family: 'Inter', sans-serif; font-size: 10px; font-weight: 600;
    color: var(--ink3); letter-spacing: 1.8px; text-transform: uppercase; margin-top: 6px;
}
.login-headline {
    font-family: 'Sora', sans-serif; font-size: 26px; font-weight: 700;
    line-height: 1.15; color: var(--teal); letter-spacing: -.3px; margin-top: 14px;
}
.login-accent { color: var(--copper); font-style: italic; }
.login-sub {
    font-family: 'Inter', sans-serif; font-size: 13px; color: var(--ink3);
    margin-top: 8px; line-height: 1.5;
}
.login-footer {
    margin-top: 14px; text-align: center;
    font-family: 'Inter', sans-serif; font-size: 11px; color: var(--ink3);
}
.login-footer .pw  { font-weight: 600; color: var(--ink2); }
.login-footer .grp { opacity: .7; display: block; margin-top: 2px; }

/* Captions / DataFrames */
.stCaption, [data-testid="stCaptionContainer"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--ink3) !important; font-size: 12px !important;
}
.stDataFrame { font-size: 12px; }
</style>
""")


# =============================================================================
# DATA
# =============================================================================
@st.cache_data(ttl=300)
def load_data():
    if not DATA_FILE.exists():
        st.error(f"Data file not found: {DATA_FILE}")
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
DEMO_PW   = "arkin@2026"
DEMO_HASH = hashlib.sha256(DEMO_PW.encode()).hexdigest()

def _h(pw): return hashlib.sha256(pw.encode()).hexdigest()


@st.cache_data(ttl=600)
def build_users():
    org = load_data()["org"]
    u = {}
    for _, r in org[org["Level"] == "RM"].iterrows():
        u[f"rm.{r['ID']}"] = dict(name=r["Name"], role="Sales Manager", level="RM",
            id=int(r["ID"]), product=r["Product"], zone=r["Zone"],
            region=r["Region"], pw=DEMO_HASH)
    for _, r in org[org["Level"] == "ABM"].iterrows():
        u[f"abm.{r['ID']}"] = dict(name=r["Name"], role="Area Business Manager", level="ABM",
            id=int(r["ID"]), product=r["Product"], zone=r["Zone"],
            region=r["Region"], pw=DEMO_HASH)
    for _, r in org[org["Level"] == "RBM"].iterrows():
        u[f"rbm.{r['ID']}"] = dict(name=r["Name"], role="Regional Business Manager", level="RBM",
            id=int(r["ID"]), product=r["Product"], zone=r["Zone"],
            region=r["Region"], pw=DEMO_HASH)
    for _, r in org[org["Level"] == "ZH"].iterrows():
        u[f"zh.{r['ID']}"] = dict(name=r["Name"], role="Zonal Head", level="ZH",
            id=int(r["ID"]), product=r["Product"], zone=r["Zone"],
            region="All", pw=DEMO_HASH)
    u["cxo"]     = dict(name="Chief Business Officer", role="CXO", level="CXO",
                        id="CXO001", product="SRL", zone="All", region="All", pw=DEMO_HASH)
    u["central"] = dict(name="Central Analytics Lead", role="Central Team", level="CXO",
                        id="CEN001", product="SRL", zone="All", region="All", pw=DEMO_HASH)
    u["admin"]   = dict(name="System Administrator", role="Admin", level="Admin",
                        id="ADM001", product="SRL", zone="All", region="All", pw=DEMO_HASH)
    return u


def do_login(username, password):
    users = build_users()
    u = users.get(username.strip().lower())
    if u and _h(password) == u["pw"]:
        return u
    return None


# =============================================================================
# RBAC
# =============================================================================
def scope(df, user, prod_ov=None, month_label=None):
    if df is None or df.empty:
        return df
    level = user["level"]
    prod  = prod_ov or user["product"]

    if month_label and "Month Label" in df.columns:
        df = df[df["Month Label"] == month_label]
    if prod in ("STLAP", "Wheels") and "Product" in df.columns:
        df = df[df["Product"] == prod]

    if level in ("CXO", "Admin"):  return df
    if level == "ZH"  and "ZH ID"  in df.columns: return df[df["ZH ID"]  == user["id"]]
    if level == "RBM" and "RBM ID" in df.columns: return df[df["RBM ID"] == user["id"]]
    if level == "ABM" and "ABM ID" in df.columns: return df[df["ABM ID"] == user["id"]]
    if level == "RM":
        col = "Emp ID" if "Emp ID" in df.columns else "RM ID"
        return df[df[col] == user["id"]] if col in df.columns else df
    return df.iloc[0:0]


# =============================================================================
# ESCALATION
# =============================================================================
def build_escalation_table(perf_all, user, prod_ov=None):
    prod = prod_ov or user["product"]
    df = perf_all.copy()

    if prod in ("STLAP", "Wheels") and "Product" in df.columns:
        df = df[df["Product"] == prod]

    level = user["level"]
    if level == "ZH"  and "ZH ID"  in df.columns: df = df[df["ZH ID"]  == user["id"]]
    if level == "RBM" and "RBM ID" in df.columns: df = df[df["RBM ID"] == user["id"]]
    if level == "ABM" and "ABM ID" in df.columns: df = df[df["ABM ID"] == user["id"]]

    if df.empty or "Month Label" not in df.columns:
        return pd.DataFrame()

    pivot = df.pivot_table(
        index=["Emp ID", "EMP Name", "ABM Name", "RBM Name", "ZH NAME"],
        columns="Month Label",
        values="Actual Disb #",
        aggfunc="sum"
    ).fillna(0)

    available = [m for m in MONTH_ORDER if m in pivot.columns]
    pivot = pivot[available]

    results = []
    for idx, row in pivot.iterrows():
        streak = 0
        for m in reversed(available):
            if row[m] == 0:
                streak += 1
            else:
                break
        if streak == 0:
            continue
        if   streak == 1: status, kind, visible = "Month 1 — AMBER", "amber", "Visible to ABM"
        elif streak == 2: status, kind, visible = "Month 2 — AMBER", "amber", "Escalated to RBM"
        elif streak == 3: status, kind, visible = "Month 3 — RED",   "red",   "Escalated to ZH"
        else:             status, kind, visible = "Critical — RED",   "red",   "Visible to Business Head"

        results.append({
            "RM": idx[1], "ABM": idx[2],
            "Streak": streak, "Status": status, "Kind": kind, "Visible To": visible,
            **{m: int(row[m]) for m in available},
        })

    esc = pd.DataFrame(results)
    if not esc.empty:
        esc = esc.sort_values("Streak", ascending=False)
    return esc


# =============================================================================
# UI HELPERS  — use st.html() for all custom HTML elements
# =============================================================================
def brand_bar(user, prod=None):
    p = prod or user["product"]
    st.html(f"""
    <div class="brand-bar">
      <div class="brand-bar-inner">
        <div class="bb-logo">
          <span class="bb-arka">ARKA</span><span class="bb-kq">KinetiQ</span>
        </div>
        <div class="bb-meta">{user['name']} · {user['role']} · {user.get('zone','—')}
          <span class="bb-chip">{p}</span>
        </div>
      </div>
    </div>""")


def kpi(label, value, sub="", trend=None):
    th = ""
    if trend is not None:
        cls = "kpi-up" if trend >= 0 else "kpi-down"
        th = f'<span class="{cls}"> {"▲" if trend >= 0 else "▼"} {abs(trend):.1f}%</span>'
    st.html(f"""<div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}{th}</div>
      <div class="kpi-sub">{sub}</div>
    </div>""")


def sec(title, emoji=""):
    st.html(f'<div class="sec"><span class="dot"></span>{emoji+" " if emoji else ""}{title}</div>')


def nudge_card(text):
    st.html(f'<div class="nudge-card">💡 {text}</div>')


def announce_card(text):
    st.html(f'<div class="announce-card">{text}</div>')


def action_card(text):
    st.html(f'<div class="action-card">{text}</div>')


def esc_card(rm_name, status, kind, visible_to, month_trail):
    chip_html = f'<span class="chip-{kind}">{status}</span>'
    st.html(f"""<div class="esc-card">
      <b>{rm_name}</b> &nbsp;{chip_html}<br>
      <span style="font-size:11px;color:#6B8788;">{visible_to} · {month_trail}</span>
    </div>""")


def mailto(to, subj, body, cc=None):
    return f"mailto:{to}?cc={','.join(cc or [])}&subject={quote(subj)}&body={quote(body)}"


def nudge_email_btn(label, link):
    st.html(f"""<a href="{link}" style="text-decoration:none;">
      <button style="width:100%;background:#0F3D3E;color:white;border:none;padding:12px;
        border-radius:10px;font-family:Sora,sans-serif;font-weight:600;
        font-size:14px;cursor:pointer;letter-spacing:0.3px;">
        📧 {label}
      </button></a>""")


PALETTE = ["#0F3D3E", "#1FA89A", "#D4936B", "#5BAFA8", "#E6B998", "#2D5A5B"]


def plotly_theme(fig, h=240):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Inter", size=11, color="#0F3D3E"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.2, font=dict(size=10)),
        xaxis=dict(showgrid=False, color="#6B8788"),
        yaxis=dict(gridcolor="#E5EAEA", color="#6B8788"))
    return fig


# =============================================================================
# MONTH SELECTOR
# =============================================================================
def month_selector(key="month_sel"):
    if key not in st.session_state:
        st.session_state[key] = CURRENT_MONTH
    cols = st.columns(len(MONTH_ORDER))
    for i, m in enumerate(MONTH_ORDER):
        with cols[i]:
            active = st.session_state[key] == m
            if st.button(
                f"{'✓ ' if active else ''}{m}",
                key=f"{key}_{m}",
                use_container_width=True,
                type="primary" if active else "secondary"
            ):
                st.session_state[key] = m
                st.rerun()
    return st.session_state[key]


# =============================================================================
# SALES MANAGER (RM) DASHBOARD
# =============================================================================
def rm_dashboard(user, data):
    sel = month_selector("rm_month")
    perf_m  = scope(data["perf"],  user, month_label=sel)
    port_m  = scope(data["port"],  user, month_label=sel)
    prof_m  = scope(data["prof"],  user, month_label=sel)
    notif_m = scope(data["notif"], user, month_label=sel)

    if perf_m.empty:
        st.warning("No data for this month.")
        return
    row = perf_m.iloc[0]

    t1, t2, t3 = st.tabs(["🎯 Focus", "📊 Performance", "💼 Portfolio"])

    # ── FOCUS ────────────────────────────────────────────────────────────
    with t1:
        sec("AI Nudges", "🤖")
        if not notif_m.empty:
            nrow = notif_m.iloc[0]
            for i in range(1, 6):
                n = str(nrow.get(f"Notification {i}", ""))
                if n.strip() and n != "nan":
                    nudge_card(n)

        sec("Announcements", "📢")
        announce_card("📌 Quarterly target review on 30th — submit branch numbers by EOD Friday.")
        announce_card("🎯 New TAT SLA: Login → Sanction within 5 working days from June.")

        sec("Today's Actionables", "✅")
        gap = max(0, int(row["Target Disb #"] - row["Actual Disb #"]))
        if row["Actual Disb #"] == 0:
            action_card("🚨 Zero disbursements this month — urgently review pipeline.")
        elif gap > 0:
            action_card(f"🔥 Close {gap} more disbursements to hit monthly target.")
        if row["Actual PF %"] < row["Target PF %"]:
            action_card(f"💰 PF% at {row['Actual PF %']:.2f}% vs target {row['Target PF %']:.2f}% — push fee collection.")
        if row["Actual Conversion %"] < row["Target Conversion %"]:
            action_card(f"🎯 Conversion {row['Actual Conversion %']:.1f}% below target {row['Target Conversion %']:.1f}% — reduce TAT.")

    # ── PERFORMANCE ───────────────────────────────────────────────────────
    with t2:
        sec("Funnel — Login → Sanction → Disb", "📊")
        c = st.columns(3)
        with c[0]: kpi("Logins",    f"{int(row['Actual Login #'])}",    f"Tgt {int(row['Target Login #'])}")
        with c[1]: kpi("Sanctions", f"{int(row['Actual Sanction #'])}", f"Tgt {int(row['Target Sanction #'])}")
        with c[2]: kpi("Disb",      f"{int(row['Actual Disb #'])}",     f"Tgt {int(row['Target Disb #'])}")

        fig = go.Figure(go.Funnel(
            y=["Logins", "Sanctions", "Disb"],
            x=[row["Actual Login #"], row["Actual Sanction #"], row["Actual Disb #"]],
            marker={"color": ["#1FA89A", "#0F3D3E", "#D4936B"]},
            textposition="inside", textinfo="value+percent initial"))
        st.plotly_chart(plotly_theme(fig), use_container_width=True)

        sec("Conversion & Mix", "🎯")
        c1, c2 = st.columns(2)
        with c1:
            conv_gap = row["Actual Conversion %"] - row["Target Conversion %"]
            kpi("Conversion", f"{row['Actual Conversion %']:.1f}%",
                f"Tgt {row['Target Conversion %']:.1f}%", trend=conv_gap)
            kpi("IRR Mix", f"{row['IRR Mix %']:.2f}%", "Portfolio yield")
        with c2:
            kpi("LTV", f"{row['LTV %']:.1f}%", "Loan to Value")
            kpi("Avg Ticket", f"₹{row['Avg Ticket Size (Rs L)']:.1f} L", "Per case")

        sec("Trend — All Months", "📈")
        perf_all_rm = scope(data["perf"], user)
        if not perf_all_rm.empty and "Month Label" in perf_all_rm.columns:
            trend = perf_all_rm.groupby("Month Label").agg(
                Disb=("Actual Disb #", "sum"),
                Target=("Target Disb #", "mean")
            ).reindex(MONTH_ORDER).reset_index()
            fig = go.Figure()
            fig.add_bar(x=trend["Month Label"], y=trend["Disb"],
                        name="Actual", marker_color="#1FA89A")
            fig.add_scatter(x=trend["Month Label"], y=trend["Target"],
                            name="Target", mode="lines+markers",
                            line=dict(color="#D4936B", dash="dash", width=2),
                            marker=dict(size=8))
            st.plotly_chart(plotly_theme(fig), use_container_width=True)

        sec("Achievement & Productivity", "⚡")
        c1, c2 = st.columns(2)
        with c1:
            kpi("CM Achievement", f"{row['CM Achievement %']:.1f}%", "Of monthly target")
            kpi("PF %", f"{row['Actual PF %']:.2f}%", f"Tgt {row['Target PF %']:.2f}%")
        with c2:
            kpi("Cross-sell", f"{row['Cross Sell %']:.1f}%", "Insurance + bundle")
            kpi("Productivity", f"{row['Productivity (Disb/RM)']:.1f}", "Disb/RM/month")

        fee = row["Actual Disb Amount (Rs Cr)"] * (row["Actual PF %"] + row["Actual Insurance %"]) / 100
        kpi("Fee Income", f"₹{fee:.3f} Cr", "PF + Insurance this month")

    # ── PORTFOLIO ─────────────────────────────────────────────────────────
    with t3:
        if not prof_m.empty:
            prow = prof_m.iloc[0]
            sec("Portfolio Health", "💼")
            c1, c2 = st.columns(2)
            with c1:
                kpi("AUM",      f"₹{prow['AUM (Rs Cr)']:.1f} Cr", "Acquired")
                kpi("Bounce %", f"{prow['AUM Bounce %']:.1f}%",    "Portfolio")
                kpi("30+ DPD",  f"{prow['30+ DPD %']:.1f}%",       "Delinquency")
                kpi("EMI Eff.", f"{prow['EMI Collection Efficiency %']:.1f}%", "Collection")
            with c2:
                kpi("Exit Rate",  f"{prow['Exit Rate %']:.1f}%",     "Leaving")
                kpi("Avg LTV",    f"{prow['Avg LTV %']:.1f}%",       "Portfolio")
                kpi("NPA %",      f"{prow['NPA %']:.2f}%",            "Non-perf.")
                kpi("Port. IRR",  f"{prow['Portfolio IRR %']:.2f}%", "Yield")

        if not port_m.empty:
            sec("Asset Mix", "🏷️")
            am = port_m.groupby("Asset Type")["POS (Rs Cr)"].sum().reset_index()
            fig = px.pie(am, names="Asset Type", values="POS (Rs Cr)",
                         color_discrete_sequence=PALETTE)
            st.plotly_chart(plotly_theme(fig, 260), use_container_width=True)

            sec("PAR Bucket", "📊")
            pm = port_m.groupby("PAR Bucket")["POS (Rs Cr)"].sum().reset_index()
            order = ["Current", "1-30 DPD", "31-60 DPD", "61-90 DPD", "90+ DPD"]
            pm["PAR Bucket"] = pd.Categorical(pm["PAR Bucket"], categories=order, ordered=True)
            pm = pm.sort_values("PAR Bucket")
            fig = px.bar(pm, x="PAR Bucket", y="POS (Rs Cr)", color="PAR Bucket",
                         color_discrete_sequence=["#1FA89A","#5BAFA8","#D4936B","#E6B998","#C8553D"])
            plotly_theme(fig); fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# LEADER (ABM / RBM / ZH) DASHBOARD
# =============================================================================
def leader_dashboard(user, data, prod_ov=None):
    sel = month_selector("ldr_month")
    perf_m = scope(data["perf"], user, prod_ov, month_label=sel)
    prof_m = scope(data["prof"], user, prod_ov, month_label=sel)
    port_m = scope(data["port"], user, prod_ov, month_label=sel)

    if perf_m.empty:
        st.warning("No team data for this month.")
        return

    t1, t2, t3, t4 = st.tabs(["🎯 Focus", "📊 Performance", "💼 Portfolio", "💵 Profitability"])

    # ── FOCUS ────────────────────────────────────────────────────────────
    with t1:
        sec("Escalation Tracker", "🚨")
        st.caption("RMs with consecutive zero disbursements — live escalation ladder")
        esc = build_escalation_table(data["perf"], user, prod_ov)

        if esc.empty:
            st.success("✅ No escalations active.")
        else:
            n_amber = len(esc[esc["Kind"] == "amber"])
            n_red   = len(esc[esc["Kind"] == "red"])
            c1, c2 = st.columns(2)
            with c1: kpi("Amber Alerts", f"{n_amber}", "Action needed")
            with c2: kpi("Red Alerts",   f"{n_red}",   "Urgent")

            available_m = [m for m in MONTH_ORDER if m in esc.columns]
            for _, r in esc.head(15).iterrows():
                trail = " | ".join(f"{m}: {r.get(m, '—')}" for m in available_m)
                esc_card(r["RM"], r["Status"], r["Kind"], r["Visible To"], trail)

            if len(esc) > 15:
                st.caption(f"+ {len(esc)-15} more RMs")
                st.download_button("⬇ Download full escalation list",
                    esc.to_csv(index=False).encode(),
                    file_name=f"escalations_{sel}.csv",
                    mime="text/csv", use_container_width=True)

        sec("Focus of the Month", "🎯")
        st.caption("Low performers (< 60% target)")
        low = perf_m[perf_m["Actual Disb #"] < perf_m["Target Disb #"] * 0.6][
            ["EMP Name", "Actual Disb #", "Target Disb #", "CM Achievement %"]
        ].head(10)
        if low.empty:
            st.success("✅ No low performers this month.")
        else:
            st.dataframe(low.rename(columns={"EMP Name": "RM"}),
                         use_container_width=True, hide_index=True)

        sec("Quick Nudge", "✉️")
        bottom = perf_m.sort_values("Actual Disb #").head(15)
        rm_pick = st.selectbox("Pick RM to nudge", bottom["EMP Name"].tolist(), key="nudge_sel")
        if rm_pick:
            rm_row   = bottom[bottom["EMP Name"] == rm_pick].iloc[0]
            rm_email = f"{rm_pick.lower().replace(' ', '.')}@arkafincap.com"
            body = (
                f"Hi {rm_pick},\n\nYour {sel} performance: "
                f"{int(rm_row['Actual Disb #'])} disbursements against target "
                f"{int(rm_row['Target Disb #'])}.\n\n"
                f"Please prioritise pipeline closure. Let's connect this week.\n\n"
                f"Regards,\n{user['name']}"
            )
            link = mailto(rm_email, f"Performance Nudge {sel} — {rm_pick}", body,
                          ["rbm@arkafincap.com", "zh@arkafincap.com"])
            nudge_email_btn(f"Open Email — Nudge {rm_pick}", link)

    # ── PERFORMANCE ───────────────────────────────────────────────────────
    with t2:
        sec("Team Snapshot", "👥")
        total_disb = int(perf_m["Actual Disb #"].sum())
        total_tgt  = int(perf_m["Target Disb #"].sum())
        c1, c2 = st.columns(2)
        with c1:
            kpi("RMs",      f"{perf_m['Emp ID'].nunique()}", "Active")
            kpi("Disb #",   f"{total_disb}", f"Tgt {total_tgt}",
                trend=(total_disb - total_tgt) / max(1, total_tgt) * 100)
        with c2:
            kpi("Disb Amt", f"₹{perf_m['Actual Disb Amount (Rs Cr)'].sum():.1f} Cr", "MTD")
            kpi("Avg Conv.",f"{perf_m['Actual Conversion %'].mean():.1f}%", "Login→Disb")

        sec("Leaderboard — Disbursements", "🏆")
        lb = perf_m.sort_values("Actual Disb #", ascending=False).head(10)[
            ["EMP Name", "Actual Disb #", "Target Disb #", "Actual Conversion %", "IRR Mix %"]
        ].rename(columns={"EMP Name":"RM","Actual Disb #":"Disb",
                           "Target Disb #":"Tgt","Actual Conversion %":"Conv%","IRR Mix %":"IRR%"})
        st.dataframe(lb, use_container_width=True, hide_index=True)

        sec("Leaderboard — IRR Mix", "💰")
        irr_lb = perf_m.sort_values("IRR Mix %", ascending=False).head(10)[
            ["EMP Name", "IRR Mix %", "Actual Disb #", "LTV %"]
        ].rename(columns={"EMP Name":"RM","IRR Mix %":"IRR%","Actual Disb #":"Disb"})
        st.dataframe(irr_lb, use_container_width=True, hide_index=True)

        sec("4-Month Peer Trend", "👥")
        perf_all = scope(data["perf"], user, prod_ov)
        if not perf_all.empty and "Month Label" in perf_all.columns:
            tg = perf_all.groupby(["EMP Name", "Month Label"])["Actual Disb #"].sum().reset_index()
            piv = tg.pivot(index="EMP Name", columns="Month Label", values="Actual Disb #").fillna(0)
            piv = piv.reindex(columns=[m for m in MONTH_ORDER if m in piv.columns])
            piv["Total"] = piv.sum(axis=1)
            piv["Avg/Mo"] = (piv["Total"] / max(1, len(piv.columns)-1)).round(1)
            piv = piv.sort_values("Total", ascending=False).head(15).reset_index()
            st.dataframe(piv, use_container_width=True, hide_index=True)

        if user["level"] in ("RBM", "ZH", "CXO"):
            sec("Performance by Region", "🗺️")
            reg = perf_m.groupby("Region").agg(
                Disb=("Actual Disb #","sum"), Target=("Target Disb #","sum")).reset_index()
            reg["Ach %"] = (reg["Disb"] / reg["Target"] * 100).round(1)
            st.dataframe(reg, use_container_width=True, hide_index=True)
            fig = px.bar(reg, x="Region", y=["Disb", "Target"], barmode="group",
                         color_discrete_sequence=["#1FA89A","#D4936B"])
            st.plotly_chart(plotly_theme(fig, 260), use_container_width=True)

            sec("Top & Bottom ABMs", "🏆")
            abm_p = perf_m.groupby("ABM Name").agg(
                Disb=("Actual Disb #","sum"), Target=("Target Disb #","sum")).reset_index()
            abm_p["Ach %"] = (abm_p["Disb"] / abm_p["Target"] * 100).round(1)
            st.write("**Top 5**")
            st.dataframe(abm_p.nlargest(5, "Ach %"), use_container_width=True, hide_index=True)
            st.write("**Bottom 5**")
            st.dataframe(abm_p.nsmallest(5, "Ach %"), use_container_width=True, hide_index=True)

    # ── PORTFOLIO ─────────────────────────────────────────────────────────
    with t3:
        if not prof_m.empty:
            sec("Portfolio Health — Aggregate", "💼")
            c1, c2 = st.columns(2)
            with c1:
                kpi("Total AUM",  f"₹{prof_m['AUM (Rs Cr)'].sum():.1f} Cr", "Book")
                kpi("Avg Bounce", f"{prof_m['AUM Bounce %'].mean():.1f}%",   "Avg")
                kpi("Avg 30+DPD", f"{prof_m['30+ DPD %'].mean():.1f}%",      "Avg")
                kpi("EMI Eff.",   f"{prof_m['EMI Collection Efficiency %'].mean():.1f}%", "Avg")
            with c2:
                kpi("Exit Rate",  f"{prof_m['Exit Rate %'].mean():.1f}%", "Avg")
                kpi("Avg LTV",    f"{prof_m['Avg LTV %'].mean():.1f}%",   "Avg")
                kpi("NPA %",      f"{prof_m['NPA %'].mean():.2f}%",        "Avg")
                kpi("Port. IRR",  f"{prof_m['Portfolio IRR %'].mean():.2f}%", "Avg")

        if not port_m.empty:
            sec("Asset Mix", "🏷️")
            am = port_m.groupby("Asset Type")["POS (Rs Cr)"].sum().reset_index()
            fig = px.pie(am, names="Asset Type", values="POS (Rs Cr)",
                         color_discrete_sequence=PALETTE)
            st.plotly_chart(plotly_theme(fig, 270), use_container_width=True)

    # ── PROFITABILITY ─────────────────────────────────────────────────────
    with t4:
        if not prof_m.empty:
            sec("Profitability KPIs", "💵")
            c1, c2 = st.columns(2)
            with c1:
                kpi("AUM / RM",    f"₹{prof_m['AUM/RM (Rs Cr)'].mean():.2f} Cr",  "Avg")
                kpi("Branch PAT",  f"{prof_m['PAT % (Before HO Allocation)'].mean():.2f}%", "Pre-HO")
            with c2:
                kpi("Disb / RM",   f"₹{prof_m['Disb/RM (Rs Cr)'].mean():.4f} Cr", "Avg")
                kpi("Gross Margin",f"{prof_m['Gross Margin %'].mean():.2f}%",       "Avg")

            sec("Path to 2% RoA", "🎯")
            avg_pat = prof_m["PAT % (Before HO Allocation)"].mean()
            avg_aum = prof_m["AUM/RM (Rs Cr)"].mean()
            avg_yld = prof_m["Yield %"].mean()
            avg_cst = prof_m["Branch Cost (Rs Cr)"].mean()
            if avg_pat < 2.0:
                st.markdown(f"📈 **Current PAT% is {avg_pat:.2f}%, gap to 2% RoA is {2-avg_pat:.2f}pp.**")
                if avg_aum < 12:
                    st.markdown(f"• **AUM/RM lever**: ₹{avg_aum:.1f}Cr → push to ₹15Cr (+{(15-avg_aum)*avg_yld/100:.2f}pp)")
                if avg_yld < 17:
                    st.markdown(f"• **Yield lever**: {avg_yld:.2f}% → push higher-IRR deals (+0.5–1pp)")
                if avg_cst > 1.5:
                    st.markdown(f"• **Cost lever**: ₹{avg_cst:.2f}Cr → trim 10% (+{avg_cst*0.1:.2f}pp)")
            else:
                st.success(f"✅ Already at {avg_pat:.2f}% — above 2% RoA target.")

            sec("Active Escalations Roll-up", "🚨")
            esc = build_escalation_table(data["perf"], user, prod_ov)
            if not esc.empty:
                n_amber = len(esc[esc["Kind"]=="amber"])
                n_red   = len(esc[esc["Kind"]=="red"])
                c1, c2 = st.columns(2)
                with c1: kpi("Amber Alerts", f"{n_amber}", "1st-2nd month zero")
                with c2: kpi("Red Alerts",   f"{n_red}",   "3+ month zero")
            else:
                st.success("✅ No escalations active.")


# =============================================================================
# CXO DASHBOARD
# =============================================================================
def cxo_dashboard(user, data):
    sec("Product View", "🎛️")
    pv = st.radio("Product", ["SRL", "STLAP", "Wheels"], horizontal=True,
                  label_visibility="collapsed", key="cxo_pv")
    st.caption(f"Currently viewing: **{pv}** {'(STLAP + Wheels combined)' if pv=='SRL' else ''}")
    leader_dashboard(user, data, prod_ov=pv)


# =============================================================================
# ADMIN DASHBOARD
# =============================================================================
def admin_dashboard(user, data):
    sec("Admin Console", "⚙️")
    t1, t2, t3 = st.tabs(["📤 Upload Data", "🔔 Notifications", "👤 Users"])

    with t1:
        up = st.file_uploader("Choose Excel file", type=["xlsx"])
        if up:
            (DATA_DIR / "arkin_dummy_data.xlsx").write_bytes(up.getbuffer())
            st.cache_data.clear()
            st.success("✅ Uploaded and cache cleared.")
        if DATA_FILE.exists():
            sz = DATA_FILE.stat().st_size / 1024
            mt = datetime.fromtimestamp(DATA_FILE.stat().st_mtime)
            st.info(f"📁 {DATA_FILE.name} · {sz:.1f} KB · {mt:%d-%b-%Y %H:%M}")

    with t2:
        notif = data["notif"]
        cols = ["Month Label", "RM Name", "Product", "Notification 1"]
        cols_exist = [c for c in cols if c in notif.columns]
        st.write(f"Total notifications: **{len(notif)}**")
        st.dataframe(notif[cols_exist].head(10), use_container_width=True, hide_index=True)
        st.button("🚀 Dispatch All (mock)", use_container_width=True)

    with t3:
        org = data["org"]
        st.dataframe(org.groupby(["Level", "Product"]).size().reset_index(name="Count"),
                     use_container_width=True, hide_index=True)
        lvl = st.selectbox("Filter", ["All"] + sorted(org["Level"].unique().tolist()))
        st.dataframe((org if lvl == "All" else org[org["Level"] == lvl]).head(50),
                     use_container_width=True, hide_index=True)


# =============================================================================
# LOGIN — compact single screen
# =============================================================================
def login_screen():
    st.html("""
    <div class="login-outer">
      <div class="login-inner">
        <div>
          <span class="login-arka">ARKA</span><span class="login-kq">KinetiQ</span>
        </div>
        <div class="login-tag">INTELLIGENCE IN MOTION</div>
        <div class="login-headline">
          Get ahead,<br><span class="login-accent">every day.</span>
        </div>
        <div class="login-sub">
          Your sales intelligence companion — numbers, nudges, and next steps
          crafted for the way you actually work.
        </div>
      </div>
    </div>
    """)

    with st.form("arkin_login"):
        st.text_input("Employee ID", placeholder="e.g. rm.3001", key="li_user")
        st.text_input("Password", placeholder="Demo: arkin@2026",
                      type="password", key="li_pass")
        if st.form_submit_button("Sign in →", use_container_width=True):
            u = do_login(st.session_state.li_user, st.session_state.li_pass)
            if u:
                st.session_state["user"] = u
                st.rerun()
            else:
                st.error("❌ Invalid Employee ID or password.")

    st.html("""
    <div class="login-footer">
      <span class="pw">Powered by Arka Fincap</span>
      <span class="grp">A Kirloskar Group company</span>
    </div>
    """)

    with st.expander("🧪 Demo credentials"):
        st.markdown(f"""
**Password:** `{DEMO_PW}`

| Employee ID | Role | Product |
|---|---|---|
| `rm.3001` | Sales Manager | STLAP |
| `rm.4001` | Sales Manager | Wheels |
| `abm.2001` | Area Business Manager | STLAP |
| `abm.2101` | Area Business Manager | Wheels |
| `rbm.201` | Regional Business Manager | STLAP |
| `zh.131` | Zonal Head | STLAP |
| `cxo` | CXO | SRL |
| `admin` | System Admin | — |
        """)


# =============================================================================
# MAIN
# =============================================================================
def main():
    inject_css()
    data = load_data()

    if "user" not in st.session_state:
        login_screen()
        return

    st.markdown('<div class="page">', unsafe_allow_html=True)

    user = st.session_state["user"]
    brand_bar(user)

    # Logout — always visible under brand bar
    _, _, col_logout = st.columns([3, 2, 1])
    with col_logout:
        if st.button("Sign out", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    level = user["level"]
    if   level == "RM":           rm_dashboard(user, data)
    elif level == "ABM":          leader_dashboard(user, data)
    elif level in ("RBM", "ZH"): leader_dashboard(user, data)
    elif level == "CXO":          cxo_dashboard(user, data)
    elif level == "Admin":        admin_dashboard(user, data)

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
