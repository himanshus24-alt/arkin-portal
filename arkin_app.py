"""
Arkin Sales Performance Portal — Mobile-First Streamlit App
===========================================================
Personas (with product scoping):
  - Sales Manager (RM) ............... sees self only, one product only
  - Team Leader (ABM) ................ sees own team, one product only
  - Senior Leadership (RBM/ZH) ....... sees own scope, one product only
  - CXO / Central Team ............... sees BOTH products across full org
  - Admin ............................ uploads data, dispatches notifications

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
    page_title="Arkin Sales Portal",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---- Mobile-first CSS ------------------------------------------------------
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 4rem; max-width: 480px;}

    .brand-bar {
        background: linear-gradient(135deg, #1F4E79 0%, #2E75B6 100%);
        color: white; padding: 14px 16px; border-radius: 12px;
        margin-bottom: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    }
    .brand-bar h2 {margin: 0; font-size: 18px;}
    .brand-bar p {margin: 2px 0 0 0; font-size: 11px; opacity: 0.85;}

    .kpi-card {
        background: white; border-radius: 12px; padding: 12px;
        border: 1px solid #E5E7EB; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 8px;
    }
    .kpi-label {font-size: 11px; color: #6B7280; text-transform: uppercase; letter-spacing: 0.4px;}
    .kpi-value {font-size: 22px; font-weight: 700; color: #1F2937; margin: 4px 0;}
    .kpi-sub {font-size: 11px; color: #6B7280;}
    .kpi-up {color: #059669;}
    .kpi-down {color: #DC2626;}

    .nudge-card {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border-left: 4px solid #F59E0B; padding: 12px 14px;
        border-radius: 8px; margin-bottom: 8px; font-size: 13px; color: #78350F;
    }
    .announce-card {
        background: #DBEAFE; border-left: 4px solid #2563EB;
        padding: 10px 14px; border-radius: 8px; margin-bottom: 8px;
        font-size: 13px; color: #1E3A8A;
    }
    .action-card {
        background: #FEE2E2; border-left: 4px solid #DC2626;
        padding: 10px 14px; border-radius: 8px; margin-bottom: 8px;
        font-size: 13px; color: #7F1D1D;
    }

    .chip-amber {background:#FEF3C7; color:#92400E; padding:2px 8px;
                 border-radius:10px; font-size:10px; font-weight:600;}
    .chip-red   {background:#FEE2E2; color:#991B1B; padding:2px 8px;
                 border-radius:10px; font-size:10px; font-weight:600;}
    .chip-green {background:#D1FAE5; color:#065F46; padding:2px 8px;
                 border-radius:10px; font-size:10px; font-weight:600;}
    .chip-stlap {background:#DBEAFE; color:#1E40AF; padding:2px 8px;
                 border-radius:10px; font-size:10px; font-weight:600;}
    .chip-wheels{background:#F3E8FF; color:#6B21A8; padding:2px 8px;
                 border-radius:10px; font-size:10px; font-weight:600;}

    .section-title {font-size: 14px; font-weight: 700; color: #1F2937;
                    margin: 16px 0 8px 0; display: flex; align-items: center;}

    .stButton button {width: 100%; border-radius: 8px; font-size: 13px;
                      padding: 8px 12px; font-weight: 600;}
    .stDataFrame {font-size: 12px;}
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

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

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
            "name": r["Name"], "role": "Team Leader (ABM)", "level": "ABM",
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

    users["cxo"] = {
        "name": "Chief Business Officer", "role": "CXO", "level": "CXO",
        "id": "CXO001", "product": "Both", "zone": "All", "region": "All",
        "pw_hash": DEMO_PW_HASH,
    }
    users["central"] = {
        "name": "Central Analytics Lead", "role": "Central Team", "level": "CXO",
        "id": "CEN001", "product": "Both", "zone": "All", "region": "All",
        "pw_hash": DEMO_PW_HASH,
    }
    users["admin"] = {
        "name": "System Administrator", "role": "Admin", "level": "Admin",
        "id": "ADM001", "product": "Both", "zone": "All", "region": "All",
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
def scope_data(df, user):
    if df is None or df.empty:
        return df
    level = user["level"]
    prod = user["product"]

    if prod != "Both" and "Product" in df.columns:
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
def brand_bar(user):
    prod_chip = ""
    if user["product"] == "STLAP":
        prod_chip = '<span class="chip-stlap">STLAP</span>'
    elif user["product"] == "Wheels":
        prod_chip = '<span class="chip-wheels">WHEELS</span>'
    elif user["product"] == "Both":
        prod_chip = '<span class="chip-stlap">STLAP</span> <span class="chip-wheels">WHEELS</span>'
    st.markdown(f"""
    <div class="brand-bar">
      <h2>🏦 Arkin Sales Portal</h2>
      <p>{user['name']} · {user['role']} · {user.get('zone','—')} &nbsp; {prod_chip}</p>
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
    st.markdown(f'<div class="section-title">{emoji} {title}</div>',
                unsafe_allow_html=True)


def mailto_link(to_email, subject, body, cc_list=None):
    cc = ",".join(cc_list) if cc_list else ""
    return f"mailto:{to_email}?cc={cc}&subject={quote(subject)}&body={quote(body)}"


def status_chip(text, kind="green"):
    return f'<span class="chip-{kind}">{text}</span>'


# =============================================================================
# DASHBOARDS
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

    section("Performance Imperatives — Funnel", "📊")
    c = st.columns(3)
    with c[0]: kpi_tile("Logins", f"{int(row['Actual Login #'])}", f"Tgt {int(row['Target Login #'])}")
    with c[1]: kpi_tile("Sanctions", f"{int(row['Actual Sanction #'])}", f"Tgt {int(row['Target Sanction #'])}")
    with c[2]: kpi_tile("Disb", f"{int(row['Actual Disb #'])}", f"Tgt {int(row['Target Disb #'])}")

    fig = go.Figure(go.Funnel(
        y=["Logins", "Sanctions", "Disbursements"],
        x=[row["Actual Login #"], row["Actual Sanction #"], row["Actual Disb #"]],
        marker={"color": ["#2E75B6", "#1F4E79", "#0F2A47"]},
        textposition="inside", textinfo="value+percent initial",
    ))
    fig.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=10))
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

    section("Disbursement Trend (Last 3 + Current)", "📈")
    trend_df = pd.DataFrame({
        "Month": ["M-3", "M-2", "M-1", "Current"],
        "Disb #": [row["M-3 Disb #"], row["M-2 Disb #"], row["M-1 Disb #"], row["Actual Disb #"]],
        "Target": [row["Target Disb #"]] * 4,
    })
    fig = go.Figure()
    fig.add_bar(x=trend_df["Month"], y=trend_df["Disb #"], name="Actual", marker_color="#2E75B6")
    fig.add_scatter(x=trend_df["Month"], y=trend_df["Target"], name="Target",
                    mode="lines+markers", line=dict(color="#DC2626", dash="dash"))
    fig.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, use_container_width=True)

    section("Achievement & Productivity", "⚡")
    c1, c2 = st.columns(2)
    with c1:
        kpi_tile("CM Achievement", f"{row['CM Achievement %']:.1f}%", "Of monthly target")
        kpi_tile("PF %", f"{row['Actual PF %']:.2f}%", f"Tgt {row['Target PF %']:.2f}%")
    with c2:
        kpi_tile("Cross-sell", f"{row['Cross Sell %']:.1f}%", "Insurance + bundle")
        kpi_tile("Productivity", f"{row['Productivity (Disb/RM)']:.1f}", "Disb / RM / month")

    fee_income = (row["Actual Disb Amount (Rs Cr)"] * row["Actual PF %"] / 100 +
                  row["Actual Disb Amount (Rs Cr)"] * row["Actual Insurance %"] / 100)
    kpi_tile("Fee Income (PF + Ins)", f"₹{fee_income:.3f} Cr", "This month")

    section("Portfolio Imperatives", "💼")
    if not prof.empty:
        prow = prof.iloc[0]
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
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10),
                          legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig, use_container_width=True)


def render_team_leader(user, data):
    perf = scope_data(data["perf"], user)
    prof = scope_data(data["prof"], user)
    port = scope_data(data["port"], user)

    if perf.empty:
        st.warning("No team data found for your profile.")
        return

    section(f"My Team — {user['product']} Snapshot", "👥")
    n_rms = perf["Emp ID"].nunique()
    total_disb = int(perf["Actual Disb #"].sum())
    total_tgt = int(perf["Target Disb #"].sum())
    aum_total = prof["AUM (Rs Cr)"].sum() if not prof.empty else 0

    c1, c2 = st.columns(2)
    with c1:
        kpi_tile("RMs Reporting", f"{n_rms}", "Active")
        kpi_tile("Team Disb #", f"{total_disb}", f"Tgt {total_tgt}",
                 trend=(total_disb - total_tgt) / max(1, total_tgt) * 100)
    with c2:
        kpi_tile("Team AUM", f"₹{aum_total:.1f} Cr", "Total book")
        kpi_tile("Avg Conv.", f"{perf['Actual Conversion %'].mean():.1f}%", "Login→Disb")

    section("Focus of the Month", "🎯")
    st.caption("Low-performing RMs with vintage > 3 months — need attention")
    low_perf = perf[
        (perf["Actual Disb #"] < perf["Target Disb #"] * 0.6) &
        (perf["M-3 Disb #"] > 0)
    ][["EMP Name", "Actual Disb #", "Target Disb #", "M-1 Disb #", "M-2 Disb #", "M-3 Disb #"]].head(10)
    if low_perf.empty:
        st.success("✅ No low performers flagged this month.")
    else:
        low_perf = low_perf.rename(columns={"EMP Name": "RM"})
        st.dataframe(low_perf, use_container_width=True, hide_index=True)

    section("Escalation Tracker", "🚨")
    st.caption("RMs (vintage > 3M) with zero disbursement — auto-escalation")
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
        for _, r in zero_disb.head(8).iterrows():
            chip = status_chip(r["Status"], r["Kind"])
            st.markdown(
                f'<div class="kpi-card" style="padding:8px 12px;">'
                f'<b>{r["EMP Name"]}</b> {chip}<br>'
                f'<span class="kpi-sub">{r["Visible To"]} · '
                f'M-1: {int(r["M-1 Disb #"])} | M-2: {int(r["M-2 Disb #"])} | '
                f'M-3: {int(r["M-3 Disb #"])}</span></div>',
                unsafe_allow_html=True)
    else:
        st.success("✅ All RMs have disbursed this month.")

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

    section("Nudge an RM", "✉️")
    bottom = perf.sort_values("Actual Disb #").head(15)
    rm_pick = st.selectbox("Pick RM to nudge", bottom["EMP Name"].tolist(), key="nudge_pick")
    if rm_pick:
        rm_row = bottom[bottom["EMP Name"] == rm_pick].iloc[0]
        rm_email = f"{rm_pick.lower().replace(' ', '.')}@arkin.com"
        body = (
            f"Hi {rm_pick},\n\n"
            f"Your current month performance shows {int(rm_row['Actual Disb #'])} "
            f"disbursements against a target of {int(rm_row['Target Disb #'])}. "
            f"Your conversion stands at {rm_row['Actual Conversion %']:.1f}% "
            f"vs target {rm_row['Target Conversion %']:.1f}%.\n\n"
            f"Please prioritise pipeline closure this week. Let's discuss in our next 1:1.\n\n"
            f"Regards,\n{user['name']}"
        )
        cc = [f"rbm.{user['region'].lower().replace(' ', '')}@arkin.com",
              f"zh.{user['zone'].lower()}@arkin.com"]
        link = mailto_link(rm_email, f"Performance Nudge — {rm_pick}", body, cc)
        st.markdown(f'<a href="{link}"><button style="width:100%;'
                    f'background:#1F4E79;color:white;border:none;padding:10px;'
                    f'border-radius:8px;font-weight:600;cursor:pointer;">'
                    f'📧 Open Email to Nudge {rm_pick}</button></a>',
                    unsafe_allow_html=True)

    if len(perf) >= 2:
        section("Peer Leaderboard", "👥")
        st.caption("Disbursement, 3-month avg, and IRR — peer comparison")
        peer = perf.copy()
        peer["3M Avg Disb"] = (peer["M-1 Disb #"] + peer["M-2 Disb #"] + peer["M-3 Disb #"]) / 3
        peer = peer.sort_values("Actual Disb #", ascending=False)
        show = peer[["EMP Name", "Actual Disb #", "3M Avg Disb", "IRR Mix %"]].head(15)
        show = show.rename(columns={"EMP Name": "RM", "Actual Disb #": "Disb", "IRR Mix %": "IRR%"})
        show["3M Avg Disb"] = show["3M Avg Disb"].round(1)
        st.dataframe(show, use_container_width=True, hide_index=True)


def render_senior_leadership(user, data):
    perf = scope_data(data["perf"], user)
    prof = scope_data(data["prof"], user)
    port = scope_data(data["port"], user)

    if perf.empty:
        st.warning("No data for your scope.")
        return

    if user["level"] == "CXO":
        prod_filter = st.radio("Product View", ["Both", "STLAP", "Wheels"],
                               horizontal=True, key="prod_filter")
        if prod_filter != "Both":
            perf = perf[perf["Product"] == prod_filter]
            prof = prof[prof["Product"] == prod_filter]
            port = port[port["Product"] == prod_filter]

    scope_label = user["product"] if user["product"] != "Both" else "All Products"

    section(f"Business Snapshot — {scope_label}", "🏢")
    c1, c2 = st.columns(2)
    with c1:
        kpi_tile("Total RMs", f"{perf['Emp ID'].nunique()}", "Active")
        kpi_tile("Total Disb #", f"{int(perf['Actual Disb #'].sum())}",
                 f"Tgt {int(perf['Target Disb #'].sum())}")
        kpi_tile("Disb Amount", f"₹{perf['Actual Disb Amount (Rs Cr)'].sum():.0f} Cr", "MTD")
    with c2:
        kpi_tile("Total AUM", f"₹{prof['AUM (Rs Cr)'].sum():.0f} Cr", "Book size")
        kpi_tile("Avg Yield", f"{prof['Yield %'].mean():.2f}%", "Portfolio")
        kpi_tile("NPA %", f"{prof['NPA %'].mean():.2f}%", "Avg")

    section("Profitability — Branch & Above", "💵")
    c1, c2 = st.columns(2)
    with c1:
        kpi_tile("AUM / RM", f"₹{prof['AUM/RM (Rs Cr)'].mean():.2f} Cr", "Avg")
        kpi_tile("Branch PAT %", f"{prof['PAT % (Before HO Allocation)'].mean():.2f}%", "Before HO alloc.")
    with c2:
        kpi_tile("Disb / RM", f"₹{prof['Disb/RM (Rs Cr)'].mean():.2f} Cr", "Avg")
        kpi_tile("Gross Margin", f"{prof['Gross Margin %'].mean():.2f}%", "Avg")

    section("Path to 2% RoA — Recommendation", "🎯")
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

    if user["level"] in ("ZH", "CXO"):
        section("Performance by Region", "🗺️")
        region_perf = perf.groupby("Region").agg(
            Disb=("Actual Disb #", "sum"),
            Target=("Target Disb #", "sum"),
            DisbAmt=("Actual Disb Amount (Rs Cr)", "sum"),
        ).reset_index()
        region_perf["Achievement %"] = (region_perf["Disb"] / region_perf["Target"] * 100).round(1)
        st.dataframe(region_perf, use_container_width=True, hide_index=True)
        fig = px.bar(region_perf, x="Region", y=["Disb", "Target"], barmode="group",
                     color_discrete_sequence=["#2E75B6", "#94A3B8"])
        fig.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10),
                          legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)

    section("Top & Bottom ABMs", "🏆")
    abm_perf = perf.groupby(["ABM Name"]).agg(
        Disb=("Actual Disb #", "sum"),
        Target=("Target Disb #", "sum"),
        AUM=("Actual Disb Amount (Rs Cr)", "sum"),
    ).reset_index()
    abm_perf["Ach %"] = (abm_perf["Disb"] / abm_perf["Target"] * 100).round(1)
    st.write("**Top 5**")
    st.dataframe(abm_perf.nlargest(5, "Ach %"), use_container_width=True, hide_index=True)
    st.write("**Bottom 5**")
    st.dataframe(abm_perf.nsmallest(5, "Ach %"), use_container_width=True, hide_index=True)

    section("Active Escalations", "🚨")
    zero = perf[perf["Actual Disb #"] == 0]
    n_amber = len(zero[zero["M-1 Disb #"] > 0])
    n_red = len(zero[(zero["M-1 Disb #"] == 0) & (zero["M-2 Disb #"] == 0)])
    c1, c2 = st.columns(2)
    with c1:
        kpi_tile("Amber Alerts", f"{n_amber}", "1st-2nd month zero disb")
    with c2:
        kpi_tile("Red Alerts", f"{n_red}", "3+ month zero disb")


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
    <div class="brand-bar">
      <h2>🏦 Arkin Sales Portal</h2>
      <p>Mobile-first performance dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        st.markdown("### Sign in")
        username = st.text_input("Username", placeholder="e.g. rm.3001")
        password = st.text_input("Password", type="password",
                                 placeholder="Demo password: arkin@2026")
        submitted = st.form_submit_button("Sign in", use_container_width=True)
        if submitted:
            u = authenticate(username, password)
            if u:
                st.session_state["user"] = u
                st.session_state["username"] = username.strip().lower()
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

    with st.expander("🧪 Demo credentials"):
        st.markdown(f"""
**Password for all demo accounts:** `{DEMO_PASSWORD}`

| Username | Role | Product |
|---|---|---|
| `rm.3001` | Sales Manager | STLAP |
| `rm.4001` | Sales Manager | Wheels |
| `abm.2001` | Team Leader (ABM) | STLAP |
| `abm.2101` | Team Leader (ABM) | Wheels |
| `rbm.201` | Regional Business Manager | STLAP |
| `rbm.216` | Regional Business Manager | Wheels |
| `zh.131` | Zonal Head | STLAP |
| `zh.135` | Zonal Head | Wheels |
| `cxo` | CXO | Both |
| `central` | Central Team | Both |
| `admin` | System Admin | — |
        """)


# =============================================================================
# MAIN
# =============================================================================
def main():
    data = load_data()

    if "user" not in st.session_state:
        login_screen()
        return

    user = st.session_state["user"]
    brand_bar(user)

    with st.sidebar:
        st.write(f"**{user['name']}**")
        st.caption(user["role"])
        st.caption(f"Product: {user['product']}")
        if st.button("Sign out", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    level = user["level"]
    if level == "RM":
        render_sales_manager(user, data)
    elif level == "ABM":
        render_team_leader(user, data)
    elif level in ("RBM", "ZH", "CXO"):
        render_senior_leadership(user, data)
    elif level == "Admin":
        render_admin(user, data)


if __name__ == "__main__":
    main()
