"""
Arka KinetiQ — Intelligence in Motion  (v2)
Hierarchy : RM -> BBM -> ABM -> RBM -> ZBM -> CXO
Products  : SBL (Secured Business Loan) + Wheels
Period    : Apr-26 / May-26 / Jun-26  (FY26-27 to-date; Jun-26 is live)
Streamlit Cloud + GitHub deployment.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from urllib.parse import quote
from datetime import datetime, date
import hashlib
import streamlit.components.v1 as components

# =============================================================================
# CONFIG
# =============================================================================
def _find_data_file():
    """Locate the workbook whether it sits next to the app or in an arkin/ subfolder."""
    here = Path(__file__).parent
    for cand in (here / "arkin_dummy_data.xlsx",
                 here / "arkin" / "arkin_dummy_data.xlsx",
                 Path("arkin_dummy_data.xlsx")):
        if cand.exists():
            return cand
    return here / "arkin_dummy_data.xlsx"   # default path for a clear error message

DATA_FILE = _find_data_file()

MONTH_ORDER   = ["Apr-26", "May-26", "Jun-26"]
CURRENT_MONTH = "Jun-26"
CURRENT_DATE  = date(2026, 6, 22)          # live-as-of date (drives day nudges)

RANK = {"RM": 0, "BBM": 1, "ABM": 2, "RBM": 3, "ZBM": 4, "CXO": 5, "Admin": 9}

# day-based nudge thresholds
NODISB_BRANCH_DAYS = 4      # RBM / ZBM
NODISB_BRANCH_CXO  = 7      # CXO
NOLOGIN_RM_DAYS    = 4
SBL_OTC_THRESHOLD  = 30
WHL_PDD_THRESHOLD  = 60

# flow vs stock vs rate aggregation behaviour for P&L / peer roll-ups
FLOW_COLS = {
    "PF Income (Rs Cr)", "Cross Sell Income (Rs Cr)", "Other Income (Rs Cr)",
    "Emp Cost (Rs Cr)", "Other Cost (Rs Cr)", "Credit Cost (Rs Cr)",
    "PBHO (Rs Cr)", "Disb/RM (Rs Cr)",
}
STOCK_COLS = {"AUM (Rs Cr)", "Avg AUM (Rs Cr)"}
# everything else treated as a rate -> simple mean

st.set_page_config(
    page_title="Arka KinetiQ",
    page_icon="◬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# CSS — ALL via st.markdown so it reaches the real DOM
# =============================================================================
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

header[data-testid="stHeader"]  { display: none !important; height: 0 !important; }
.stAppHeader                    { display: none !important; height: 0 !important; }
[data-testid="stToolbar"]       { display: none !important; }
[data-testid="stDecoration"]    { display: none !important; }
#MainMenu                       { display: none !important; }
footer                          { display: none !important; }
.stMainBlockContainer {
    padding-top: 0 !important; padding-bottom: 0 !important;
    padding-left: 0 !important; padding-right: 0 !important;
    max-width: 480px !important;
}
[data-testid="stAppViewContainer"] { padding-top: 0 !important; }
section[data-testid="stMain"]      { padding-top: 0 !important; }
.main .block-container             { padding-top: 0 !important; }

:root {
    --teal:#0F3D3E; --teal2:#1FA89A; --teal-bg:#E6F4F2;
    --copper:#D4936B; --cop-bg:#FDF4ED; --cream:#F6F8F8;
    --ink1:#0F3D3E; --ink2:#2D5A5B; --ink3:#6B8788; --line:#E5EAEA;
    --sh-sm:0 1px 3px rgba(15,61,62,.06);
    --sh-md:0 4px 12px rgba(15,61,62,.08);
    --sh-lg:0 12px 32px rgba(15,61,62,.12);
}
.stApp {
    background: linear-gradient(180deg,#0F3D3E 0%,#12504f 6%,#1a7e7d 14%,#6bbfbe 24%,
        #b8e4e3 33%,#daf0ef 42%,#edf8f7 54%,#F6F8F8 68%,#F6F8F8 100%) !important;
    background-attachment: fixed !important;
    font-family:'Inter',sans-serif; color:var(--ink1);
}
.block-container,[data-testid="stMainBlockContainer"],
section[data-testid="stMain"],[data-testid="stAppViewContainer"] { background: transparent !important; }
.page { padding: 0 14px 80px; }

[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],button[kind="header"] { display: none !important; }

/* brand bar handled via components.html (isolated) */

/* sign-out red button beside month selector */
[data-testid="stHorizontalBlock"]:nth-of-type(1)
  [data-testid="stColumn"]:last-child .stButton button {
    background:#FDECEA !important; color:#7A1F0E !important; border:1.5px solid #f5c6c0 !important;
    font-size:13px !important; font-weight:600 !important; padding:10px 8px !important;
}
[data-testid="stHorizontalBlock"]:nth-of-type(1)
  [data-testid="stColumn"]:last-child .stButton button:hover {
    background:#C8553D !important; color:#fff !important; border-color:#C8553D !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] {
    background:rgba(255,255,255,0.92) !important; backdrop-filter:blur(8px) !important;
    border-radius:10px !important; border:1.5px solid rgba(255,255,255,0.6) !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] div { color:#0F3D3E !important; }
[data-testid="stSelectbox"] label {
    font-size:11px !important; font-weight:600 !important; color:#2D5A5B !important;
    text-transform:uppercase; letter-spacing:.5px;
}

.kpi-card  { background:rgba(255,255,255,0.82); backdrop-filter:blur(10px); border-radius:12px;
    padding:12px 13px; border:1px solid rgba(255,255,255,0.6); box-shadow:0 2px 12px rgba(15,61,62,0.10); margin-bottom:8px; }
.kpi-label { font-size:10px; font-weight:600; color:var(--ink3); text-transform:uppercase; letter-spacing:.6px; }
.kpi-value { font-family:'Sora',sans-serif; font-size:21px; font-weight:700; color:var(--ink1); margin:4px 0; line-height:1.1; }
.kpi-sub   { font-size:11px; color:var(--ink3); font-weight:500; }
.kpi-up    { color:var(--teal2); font-size:12px; }
.kpi-down  { color:#C8553D; font-size:12px; }

.nudge-card    { background:rgba(253,244,237,0.9); border-left:3px solid var(--copper); padding:11px 13px;
    border-radius:8px; margin-bottom:7px; font-size:12.5px; line-height:1.5; color:#6B3F1F; }
.inc-card      { background:rgba(232,247,239,0.95); border-left:3px solid #1FA89A; padding:11px 13px;
    border-radius:8px; margin-bottom:7px; font-size:12.5px; line-height:1.5; color:#0F3D3E; }
.announce-card { background:rgba(230,244,242,0.9); border-left:3px solid var(--teal2); padding:11px 13px;
    border-radius:8px; margin-bottom:7px; font-size:12.5px; line-height:1.5; color:var(--teal); }
.action-card   { background:rgba(253,236,234,0.9); border-left:3px solid #C8553D; padding:11px 13px;
    border-radius:8px; margin-bottom:7px; font-size:12.5px; line-height:1.5; color:#7A1F0E; }
.wall-card     { background:rgba(255,255,255,0.85); border-radius:10px; border:1px solid rgba(255,255,255,0.6);
    padding:9px 12px; margin-bottom:7px; box-shadow:0 2px 10px rgba(15,61,62,0.08); font-size:12.5px; color:var(--ink1); }

.chip-amber { background:var(--cop-bg); color:#6B3F1F; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600; }
.chip-red   { background:#FDECEA; color:#7A1F0E; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600; }
.chip-green { background:var(--teal-bg); color:var(--teal); padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600; }

.sec      { font-family:'Sora',sans-serif; font-size:13px; font-weight:700; color:var(--ink1); margin:14px 0 8px; letter-spacing:.2px; }
.sec .dot { display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--copper); margin-right:8px; vertical-align:middle; }

.stButton button {
    width:100%; background:var(--teal) !important; color:#fff !important; border:none !important;
    border-radius:10px !important; padding:11px 16px !important; font-family:'Sora',sans-serif !important;
    font-weight:600 !important; font-size:14px !important;
}
.stButton button:hover { background:var(--teal2) !important; }

.stTextInput input {
    border-radius:10px !important; border:1.5px solid var(--line) !important; font-family:'Inter',sans-serif !important;
    font-size:14px !important; padding:10px 14px !important; background:#fff !important; color:var(--ink1) !important;
}
.stTextInput input:focus { border-color:var(--copper) !important; box-shadow:0 0 0 3px rgba(212,147,107,.15) !important; }
.stTextInput label, .stTextArea label {
    font-family:'Inter',sans-serif !important; font-size:11px !important; font-weight:600 !important;
    color:var(--ink2) !important; text-transform:uppercase; letter-spacing:.5px;
}

.stTabs [data-baseweb="tab-list"] { gap:3px; background:rgba(255,255,255,0.82); backdrop-filter:blur(10px);
    border-radius:10px; padding:4px; border:1px solid rgba(255,255,255,0.55); }
.stTabs [data-baseweb="tab"] {
    font-family:'Sora',sans-serif !important; font-size:11.5px !important; font-weight:600 !important;
    color:var(--ink3) !important; padding:8px 3px !important; border-radius:8px !important;
    flex:1; background:transparent !important; border:none !important;
}
.stTabs [aria-selected="true"] { background:var(--teal) !important; color:#fff !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top:12px; }
.stTabs [data-baseweb="tab-highlight"] { display:none; }

.stRadio > div { gap:4px !important; background:rgba(255,255,255,0.82); padding:4px; border-radius:10px;
    border:1px solid rgba(255,255,255,0.55); display:flex !important; }
.stRadio label { font-family:'Inter',sans-serif; font-size:13px; }

.login-outer::before { content:""; position:fixed; top:0; left:0; width:88px; height:88px; background:var(--teal); clip-path:polygon(0 0,100% 0,0 100%); z-index:1; }
.login-outer::after  { content:""; position:fixed; bottom:0; right:0; width:100px; height:100px; background:var(--copper); clip-path:polygon(100% 100%,100% 0,0 100%); z-index:1; opacity:.88; }
.login-inner { position:relative; z-index:5; padding:90px 22px 0; max-width:440px; margin:0 auto; }
.login-arka  { font-family:'Sora',sans-serif; font-weight:800; font-size:30px; color:var(--teal); letter-spacing:2px; }
.login-kq    { font-family:'Sora',sans-serif; font-weight:500; font-size:22px; color:var(--copper); font-style:italic; letter-spacing:.5px; margin-left:6px; }
.login-tag   { font-family:'Inter',sans-serif; font-size:10px; font-weight:600; color:var(--ink3); letter-spacing:1.8px; text-transform:uppercase; margin-top:6px; }
.login-headline { font-family:'Sora',sans-serif; font-size:26px; font-weight:700; line-height:1.15; color:var(--teal); letter-spacing:-.3px; margin-top:12px; }
.login-accent { color:var(--copper); font-style:italic; }
.login-sub   { font-family:'Inter',sans-serif; font-size:13px; color:var(--ink3); margin-top:6px; line-height:1.5; }
[data-testid="stForm"] { background:#fff; border-radius:16px; padding:18px 16px 16px; box-shadow:var(--sh-lg); border:1px solid var(--line); margin:0 22px; }
.login-footer { margin-top:12px; text-align:center; font-family:'Inter',sans-serif; font-size:11px; color:var(--ink3); padding-bottom:80px; }
.login-footer .pw  { font-weight:600; color:var(--ink2); }
.login-footer .grp { opacity:.7; display:block; margin-top:2px; }

.stCaption,[data-testid="stCaptionContainer"] { font-family:'Inter',sans-serif !important; color:var(--ink3) !important; font-size:12px !important; }
.stDataFrame { font-size:12px; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# DATA
# =============================================================================
@st.cache_data(ttl=300)
def load_data():
    if not DATA_FILE.exists():
        st.error(f"Data file not found: {DATA_FILE}")
        st.stop()
    xl = pd.ExcelFile(DATA_FILE)
    d = {
        "perf": xl.parse("Performance"),
        "prof": xl.parse("Profitability"),
        "port": xl.parse("Portfolio"),
        "attr": xl.parse("Attrition"),
        "ann":  xl.parse("Announcements"),
        "grid": xl.parse("Incentive Grid"),
        "org":  xl.parse("Org Hierarchy"),
    }
    return d


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
    # RMs
    for _, r in org.iterrows():
        u[f"rm.{int(r['RM ID'])}"] = dict(
            name=r["RM Name"], role="Relationship Manager", level="RM", id=int(r["RM ID"]),
            product=r["Product"], zone=r["Zone"], state=r["State"], region=r["Region"], area=r["Area"],
            branch=r["Branch Name"], pw=DEMO_HASH)
    # managers — one entry per unique id
    def add_mgr(level, idcol, namecol, role):
        seen = {}
        for _, r in org.iterrows():
            mid = int(r[idcol])
            if mid in seen:
                continue
            seen[mid] = True
            u[f"{level.lower()}.{mid}"] = dict(
                name=r[namecol], role=role, level=level, id=mid, product=r["Product"],
                zone=r["Zone"], state=r["State"], region=r["Region"], area=r["Area"],
                branch=r["Branch Name"], pw=DEMO_HASH)
    add_mgr("BBM", "BBM ID", "BBM Name", "Branch Business Manager")
    add_mgr("ABM", "ABM ID", "ABM Name", "Area Business Manager")
    add_mgr("RBM", "RBM ID", "RBM Name", "Regional Business Manager")
    add_mgr("ZBM", "ZBM ID", "ZBM Name", "Zonal Business Manager")
    u["cxo"]   = dict(name="Chief Business Officer", role="CXO", level="CXO", id="CXO001",
                      product="SRL", zone="All", state="All", region="All", area="All", branch="All", pw=DEMO_HASH)
    u["admin"] = dict(name="System Administrator", role="Admin", level="Admin", id="ADM001",
                      product="SRL", zone="All", state="All", region="All", area="All", branch="All", pw=DEMO_HASH)
    return u


def do_login(username, password):
    users = build_users()
    usr = users.get(username.strip().lower())
    if usr and _h(password) == usr["pw"]:
        return usr
    return None


# =============================================================================
# RBAC  — scope any sheet to a user's subtree
# =============================================================================
def ytd_window(sel):
    return MONTH_ORDER[: MONTH_ORDER.index(sel) + 1]

def _id_col(df, level):
    if level == "RM":
        return "Emp ID" if "Emp ID" in df.columns else "RM ID"
    return f"{level} ID"

def scope(df, user, prod_ov=None, month_label=None, ytd=False):
    if df is None or df.empty:
        return df
    out = df
    prod = prod_ov if prod_ov is not None else user.get("product")
    # month filter
    if "Month Label" in out.columns:
        if ytd and month_label:
            out = out[out["Month Label"].isin(ytd_window(month_label))]
        elif month_label:
            out = out[out["Month Label"] == month_label]
    # product filter
    if prod in ("SBL", "Wheels") and "Product" in out.columns:
        out = out[out["Product"] == prod]
    # subtree filter
    level = user["level"]
    if level in ("CXO", "Admin"):
        return out
    col = _id_col(out, level)
    if col in out.columns:
        return out[out[col] == user["id"]]
    return out.iloc[0:0]


# =============================================================================
# INCENTIVE ENGINE
# =============================================================================
@st.cache_data(ttl=600)
def incentive_grid_dict():
    g = load_data()["grid"]
    GRID = {}
    for _, r in g.iterrows():
        GRID.setdefault(r["Component"], {"metric": r["Metric"], "dir": r["Direction"], "tiers": []})
        GRID[r["Component"]]["tiers"].append((float(r["Lower"]), float(r["Upper"]), float(r["Payout (Rs)"])))
    for c in GRID:
        GRID[c]["tiers"].sort(key=lambda t: t[0])
    return GRID

def _tier_payout(spec, value):
    for lo, hi, pay in spec["tiers"]:
        if lo <= value < hi:
            return pay
    return spec["tiers"][-1][2]

def _metric_values(prow, profrow):
    disb_ach = prow["Actual Disb Amount (Rs Cr)"] / max(prow["Target Disb Amount (Rs Cr)"], 1e-9) * 100
    pf_ach   = prow["Actual PF %"] / max(prow["Target PF %"], 1e-9) * 100
    roi_ach  = prow["Actual ROI %"] / max(prow["Target ROI %"], 1e-9) * 100
    dpd30    = profrow["30+ DPD %"] if profrow is not None else 5.0
    return {
        "disb_ach_pct": disb_ach,
        "xsell_pct":    prow["Actual Cross Sell %"],
        "pf_ach_pct":   pf_ach,
        "dpd30_pct":    dpd30,
        "roi_ach_pct":  roi_ach,
    }

def compute_incentive(prow, profrow):
    """returns earned, max, components[list], nudges[list] for one RM."""
    GRID = incentive_grid_dict()
    vals = _metric_values(prow, profrow)
    earned = 0.0; mx = 0.0; comps = []; nudges = []
    for comp, spec in GRID.items():
        val = vals[spec["metric"]]
        pay = _tier_payout(spec, val)
        best = max(t[2] for t in spec["tiers"])
        earned += pay; mx += best
        comps.append({"name": comp, "value": val, "earned": pay, "max": best, "metric": spec["metric"]})
        # next-tier nudge (only meaningful for 'higher' metrics)
        if spec["dir"] == "higher" and pay < best:
            higher = [(lo, hi, p) for lo, hi, p in spec["tiers"] if p > pay and lo > val]
            if higher:
                lo, hi, p = min(higher, key=lambda t: t[0])
                gap = lo - val
                nudges.append({"comp": comp, "metric": spec["metric"], "gap": gap,
                               "need": lo, "cur": val, "delta": p - pay})
    return {"earned": earned, "max": mx, "comps": comps, "nudges": nudges}

def incentive_nudge_text(prow, inc):
    """craft the single most-reachable incentive nudge for an RM, or None."""
    if not inc["nudges"]:
        return None
    # prefer disbursement (actionable) then smallest gap
    nd = sorted(inc["nudges"],
                key=lambda x: (0 if x["metric"] == "disb_ach_pct" else 1, x["gap"]))[0]
    if nd["metric"] == "disb_ach_pct":
        tkt = prow["Avg Ticket Size (Rs L)"] or 14
        tgt_amt = prow["Target Disb Amount (Rs Cr)"]
        need_amt = nd["need"]/100 * tgt_amt - prow["Actual Disb Amount (Rs Cr)"]
        cases = max(1, int(np.ceil(need_amt * 100 / max(tkt, 1))))
        return (f"₹{nd['delta']:,.0f} extra incentive within reach — you're at "
                f"{nd['cur']:.0f}% of disb target. Close ~{cases} more case(s) "
                f"(₹{max(need_amt,0):.2f} Cr) to cross {nd['need']:.0f}% and unlock the next slab.")
    if nd["metric"] == "xsell_pct":
        return (f"₹{nd['delta']:,.0f} extra incentive within reach — cross-sell at "
                f"{nd['cur']:.1f}%; push to {nd['need']:.0f}% to unlock the next slab.")
    if nd["metric"] == "pf_ach_pct":
        return (f"₹{nd['delta']:,.0f} extra incentive within reach — PF at {nd['cur']:.0f}% of "
                f"target; reach {nd['need']:.0f}% to unlock the next slab.")
    if nd["metric"] == "roi_ach_pct":
        return (f"₹{nd['delta']:,.0f} extra incentive within reach — hold ROI at "
                f"{nd['need']:.0f}%+ of target to unlock the yield bonus.")
    return None


# =============================================================================
# AGGREGATION HELPERS (P&L / peer roll-ups)
# =============================================================================
def _how(col):
    if col in FLOW_COLS:  return "flow"
    if col in STOCK_COLS: return "stock"
    return "rate"

def agg_value(window_df, col):
    """aggregate a single prof column over a (possibly multi-month, multi-RM) window."""
    if window_df.empty or col not in window_df.columns:
        return 0.0
    how = _how(col)
    if how == "flow":
        return float(window_df[col].sum())
    if how == "stock":
        per_month = window_df.groupby("Month Label")[col].sum()
        return float(per_month.mean()) if len(per_month) else 0.0
    return float(window_df[col].mean())


# P&L line items used across BBM+ (label, column, good-direction)
PNL_METRICS = [
    ("AuM",              "AUM (Rs Cr)",            "high"),
    ("Avg AuM",          "Avg AUM (Rs Cr)",        "high"),
    ("ROI",              "ROI %",                  "high"),
    ("NIM",              "NIM %",                  "high"),
    ("Cross-Sell Income","Cross Sell Income (Rs Cr)","high"),
    ("Other Income",     "Other Income (Rs Cr)",   "high"),
    ("Emp Cost",         "Emp Cost (Rs Cr)",       "low"),
    ("Other Cost",       "Other Cost (Rs Cr)",     "low"),
    ("Credit Cost",      "Credit Cost (Rs Cr)",    "low"),
    ("PBHO",             "PBHO (Rs Cr)",           "high"),
]


def peer_benchmark(prof_univ, entity_col, my_entity, sel, top_n):
    """Compare my_entity against top-N peers (by YTD PBHO) on PNL_METRICS.
       Returns a DataFrame for display + (my, peer) PBHO for an indicator."""
    ytd = ytd_window(sel)
    month_df = prof_univ[prof_univ["Month Label"] == sel]
    ytd_df   = prof_univ[prof_univ["Month Label"].isin(ytd)]

    # rank entities by YTD PBHO
    rank = (ytd_df.groupby(entity_col)
            .apply(lambda g: agg_value(g, "PBHO (Rs Cr)"), include_groups=False)
            .sort_values(ascending=False))
    peers = rank.head(top_n).index.tolist()

    def col_for(df, ent, col):
        return agg_value(df[df[entity_col] == ent], col)

    rows = []
    for label, col, good in PNL_METRICS:
        my_m  = col_for(month_df, my_entity, col)
        my_y  = col_for(ytd_df,   my_entity, col)
        pr_m  = np.mean([col_for(month_df, e, col) for e in peers]) if peers else 0.0
        pr_y  = np.mean([col_for(ytd_df,   e, col) for e in peers]) if peers else 0.0
        # remark vs peer YTD
        if pr_y == 0:
            remark = "—"
        else:
            diff = (my_y - pr_y) / abs(pr_y) * 100
            ahead = (diff >= 0) if good == "high" else (diff <= 0)
            remark = (f"✓ ahead {abs(diff):.0f}%" if ahead else f"↑ improve {abs(diff):.0f}%")
        pct_y = (my_y / pr_y * 100) if pr_y else 0.0
        rows.append({"Metric": label,
                     "Mine (Mo)": round(my_m, 3), "Peer (Mo)": round(pr_m, 3),
                     "Mine (YTD)": round(my_y, 3), "Peer (YTD)": round(pr_y, 3),
                     "vs Peer %": round(pct_y, 0), "Remark": remark})
    out = pd.DataFrame(rows)
    my_pbho  = col_for(ytd_df, my_entity, "PBHO (Rs Cr)")
    peer_pbho= np.mean([col_for(ytd_df, e, "PBHO (Rs Cr)") for e in peers]) if peers else 0.0
    return out, my_pbho, peer_pbho, peers


# =============================================================================
# UI HELPERS
# =============================================================================
def kpi(label, value, sub="", trend=None):
    th = ""
    if trend is not None:
        cls = "kpi-up" if trend >= 0 else "kpi-down"
        th  = f'<span class="{cls}"> {"▲" if trend >= 0 else "▼"} {abs(trend):.1f}%</span>'
    st.markdown(f"""<div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}{th}</div>
      <div class="kpi-sub">{sub}</div></div>""", unsafe_allow_html=True)

def sec(title, emoji=""):
    st.markdown(f'<div class="sec"><span class="dot"></span>{emoji+" " if emoji else ""}{title}</div>',
                unsafe_allow_html=True)

def nudge_card(t):    st.markdown(f'<div class="nudge-card">💡 {t}</div>', unsafe_allow_html=True)
def inc_card(t):      st.markdown(f'<div class="inc-card">💸 {t}</div>', unsafe_allow_html=True)
def announce_card(t): st.markdown(f'<div class="announce-card">{t}</div>', unsafe_allow_html=True)
def action_card(t):   st.markdown(f'<div class="action-card">{t}</div>', unsafe_allow_html=True)
def wall_card(t):     st.markdown(f'<div class="wall-card">{t}</div>', unsafe_allow_html=True)

PALETTE = ["#0F3D3E","#1FA89A","#D4936B","#5BAFA8","#E6B998","#2D5A5B"]

def plotly_theme(fig, h=240):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Inter", size=11, color="#0F3D3E"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.2, font=dict(size=10)),
        xaxis=dict(showgrid=False, color="#6B8788"),
        yaxis=dict(gridcolor="#E5EAEA", color="#6B8788"))
    return fig

def brand_bar(user, prod=None):
    p = prod or user.get("product", "—")
    html = f"""<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
html,body{{background:transparent!important;height:72px;overflow:hidden;width:100%}}
.bar{{background:#0F3D3E;color:#fff;padding:13px 14px;border-radius:14px;position:relative;overflow:hidden;font-family:'Inter',sans-serif;height:70px;width:100%}}
.bar::after{{content:"";position:absolute;top:-25px;right:-25px;width:80px;height:80px;background:#D4936B;clip-path:polygon(50% 0%,100% 100%,0% 100%);opacity:.35}}
.inner{{position:relative;z-index:2}}
.logo{{display:flex;align-items:baseline;gap:6px;margin-bottom:4px}}
.arka{{font-family:'Sora',sans-serif;font-weight:800;font-size:17px;letter-spacing:2px}}
.kq{{font-family:'Sora',sans-serif;font-weight:500;font-size:14px;font-style:italic;color:#D4936B}}
.meta{{font-size:10.5px;opacity:.85;line-height:1.45}}
.chip{{background:rgba(255,255,255,.15);padding:2px 7px;border-radius:10px;font-size:9px;font-weight:600;margin-left:4px}}
</style></head><body>
<div class="bar"><div class="inner">
  <div class="logo"><span class="arka">ARKA</span><span class="kq">KinetiQ</span></div>
  <div class="meta">{user['name']} · {user['role']} · {user.get('zone','—')}<span class="chip">{p}</span></div>
</div></div></body></html>"""
    components.html(html, height=74, scrolling=False)

def month_selector(key="month_sel"):
    cur = st.session_state.get(key, CURRENT_MONTH)
    if cur not in MONTH_ORDER:
        cur = CURRENT_MONTH
    col_m, col_b = st.columns([3, 1])
    with col_m:
        sel = st.selectbox("📅 Viewing month (FY26-27 · YTD updates daily)",
                           MONTH_ORDER, index=MONTH_ORDER.index(cur), key=key)
    with col_b:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sign out", key="signout_btn", use_container_width=True):
            st.session_state.clear(); st.rerun()
    return sel


# =============================================================================
# small shared helpers for dashboards
# =============================================================================
def order_months(df):
    if df is None or df.empty:
        return df
    df = df.copy()
    df["__o"] = df["Month Label"].map({m: i for i, m in enumerate(MONTH_ORDER)})
    return df.sort_values("__o")

def kpi_grid(items, ncol=2):
    """items = list of (label, value, sub). renders in ncol grid."""
    for i in range(0, len(items), ncol):
        cols = st.columns(ncol)
        for c, it in zip(cols, items[i:i + ncol]):
            with c:
                lbl, val, sub = (it + ("",))[:3]
                kpi(lbl, val, sub)

def mix_chart(port_scope, value_col="POS (Rs Cr)"):
    if port_scope is None or port_scope.empty:
        st.caption("No portfolio data for this selection.")
        return
    g = port_scope.groupby("Asset Type")[value_col].sum().sort_values(ascending=False)
    fig = go.Figure(go.Pie(labels=g.index, values=g.values, hole=.55,
                           marker=dict(colors=PALETTE)))
    fig.update_traces(textinfo="percent", textfont_size=11)
    plotly_theme(fig, 230)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def incentive_donut(inc):
    labels = [c["name"] for c in inc["comps"] if c["earned"] > 0]
    values = [c["earned"] for c in inc["comps"] if c["earned"] > 0]
    gap = inc["max"] - inc["earned"]
    if gap > 0:
        labels.append("Untapped"); values.append(gap)
    colors = PALETTE[:len(values) - (1 if gap > 0 else 0)] + (["#E5EAEA"] if gap > 0 else [])
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=.62,
                           marker=dict(colors=colors), sort=False))
    fig.update_traces(textinfo="none")
    fig.add_annotation(text=f"<b>₹{inc['earned']:,.0f}</b><br><span style='font-size:10px'>of ₹{inc['max']:,.0f}</span>",
                       showarrow=False, font=dict(family="Sora", size=15, color="#0F3D3E"))
    plotly_theme(fig, 240)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# =============================================================================
# RM DASHBOARD
# =============================================================================
def rm_dashboard(user, data):
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    brand_bar(user)
    sel = month_selector()
    prod = user["product"]

    perf_all = order_months(scope(data["perf"], user, prod, None))
    prof_all = order_months(scope(data["prof"], user, prod, None))
    prow_df  = perf_all[perf_all["Month Label"] == sel]
    if prow_df.empty:
        st.warning("No data for the selected month."); return
    prow  = prow_df.iloc[0]
    profr = prof_all[prof_all["Month Label"] == sel]
    profr = profr.iloc[0] if not profr.empty else None
    port_m = scope(data["port"], user, prod, sel)

    t_focus, t_perf, t_trend = st.tabs(["🎯 Focus", "📊 Performance", "📈 Trends"])

    # ---------------- FOCUS ----------------
    with t_focus:
        inc = compute_incentive(prow, profr)
        sec("Your nudges this month", "💡")
        nudges = []

        # below-target funnel (units + value)
        if prow["Actual Login #"] < prow["Target Login #"] or \
           prow["Actual Login Amount (Rs Cr)"] < prow["Target Login Amount (Rs Cr)"]:
            nudges.append(f"Logins behind target: {int(prow['Actual Login #'])}/{int(prow['Target Login #'])} cases · "
                          f"₹{prow['Actual Login Amount (Rs Cr)']:.2f}/{prow['Target Login Amount (Rs Cr)']:.2f} Cr.")
        if prow["Actual Disb #"] < prow["Target Disb #"] or \
           prow["Actual Disb Amount (Rs Cr)"] < prow["Target Disb Amount (Rs Cr)"]:
            nudges.append(f"Disbursal behind target: {int(prow['Actual Disb #'])}/{int(prow['Target Disb #'])} cases · "
                          f"₹{prow['Actual Disb Amount (Rs Cr)']:.2f}/{prow['Target Disb Amount (Rs Cr)']:.2f} Cr.")
        if prow["Actual ROI %"] < prow["Target ROI %"]:
            nudges.append(f"ROI below target: {prow['Actual ROI %']:.2f}% vs {prow['Target ROI %']:.2f}% — protect yield on new bookings.")
        if prow["Actual Cross Sell %"] < prow["Target Cross Sell %"]:
            nudges.append(f"Cross-sell below target: {prow['Actual Cross Sell %']:.1f}% vs {prow['Target Cross Sell %']:.0f}%.")
        if prow["Actual PF %"] < prow["Target PF %"]:
            nudges.append(f"PF below target: {prow['Actual PF %']:.2f}% vs {prow['Target PF %']:.2f}%.")
        if profr is not None and profr["AUM Bounce %"] > 8:
            nudges.append(f"Bounce rate elevated at {profr['AUM Bounce %']:.1f}% — follow up on EMI clearances.")

        # recency (current month only)
        if sel == CURRENT_MONTH:
            if prow["Days Since Last Login"] > NOLOGIN_RM_DAYS:
                nudges.append(f"No login logged in {int(prow['Days Since Last Login'])} days — get a fresh file in today.")
            if prow["Days Since Last Disb"] > NODISB_BRANCH_DAYS:
                nudges.append(f"No disbursal in {int(prow['Days Since Last Disb'])} days — push a sanctioned case to disbursal.")

        # portfolio aging
        if port_m is not None and not port_m.empty:
            if prod == "SBL":
                otc = pd.to_numeric(port_m["OTC Days"], errors="coerce")
                n = int((otc > SBL_OTC_THRESHOLD).sum())
                if n: nudges.append(f"{n} case(s) with OTC &gt; {SBL_OTC_THRESHOLD} days — clear pending conditions to close.")
            else:
                pdd = pd.to_numeric(port_m["PDD Days"], errors="coerce")
                n = int((pdd > WHL_PDD_THRESHOLD).sum())
                if n: nudges.append(f"{n} case(s) with PDD &gt; {WHL_PDD_THRESHOLD} days — collect post-disbursal documents.")

        for t in nudges:
            nudge_card(t)
        if not nudges:
            st.markdown('<div class="inc-card">✅ You\'re tracking at or above target across the board. Keep it up!</div>',
                        unsafe_allow_html=True)

        # incentive nudge (the highlight feature)
        itx = incentive_nudge_text(prow, inc)
        if itx:
            sec("Incentive within reach", "💸")
            inc_card(itx)

        # 0+ cases with names
        if port_m is not None and not port_m.empty:
            zero_plus = port_m[pd.to_numeric(port_m["DPD Days"], errors="coerce") > 0] \
                .sort_values("DPD Days", ascending=False)
            if not zero_plus.empty:
                sec(f"0+ cases to action ({len(zero_plus)})", "⚠️")
                for _, c in zero_plus.head(6).iterrows():
                    action_card(f"<b>{c['Customer Name']}</b> · {c['LAN ID']} · {int(c['DPD Days'])} DPD · "
                                f"POS ₹{c['POS (Rs Cr)']:.2f} Cr · {c['Asset Type']}")

        # announcements
        ann = data["ann"]
        ann = ann[ann["Product"].isin([prod, "All"]) & ann["Scope"].isin(["RM", "All"])]
        if not ann.empty:
            sec("Announcements & contests", "📣")
            for _, a in ann.iterrows():
                tag = "🏆" if a["Type"] == "Contest" else "📌"
                announce_card(f"{tag} <b>{a['Title']}</b> ({a['Date']})<br>{a['Detail']}")

    # ---------------- PERFORMANCE ----------------
    with t_perf:
        sec("Funnel — units & value", "📊")
        kpi_grid([
            ("Logins", f"{int(prow['Actual Login #'])}", f"₹{prow['Actual Login Amount (Rs Cr)']:.2f} Cr · tgt {int(prow['Target Login #'])}"),
            ("Sanctions", f"{int(prow['Actual Sanction #'])}", f"₹{prow['Actual Sanction Amount (Rs Cr)']:.2f} Cr · tgt {int(prow['Target Sanction #'])}"),
            ("Disbursals", f"{int(prow['Actual Disb #'])}", f"₹{prow['Actual Disb Amount (Rs Cr)']:.2f} Cr · tgt {int(prow['Target Disb #'])}"),
            ("Login→Sanction", f"{prow['Login to Sanction %']:.0f}%", "conversion ratio"),
        ])
        sec("Quality & yield", "🎯")
        kpi_grid([
            ("PF %", f"{prow['Actual PF %']:.2f}%", f"tgt {prow['Target PF %']:.2f}%"),
            ("ROI %", f"{prow['Actual ROI %']:.2f}%", f"tgt {prow['Target ROI %']:.2f}%"),
            ("Cross-Sell %", f"{prow['Actual Cross Sell %']:.1f}%", f"tgt {prow['Target Cross Sell %']:.0f}%"),
            ("Avg Ticket", f"₹{prow['Avg Ticket Size (Rs L)']:.1f} L", "per case"),
        ])
        sec("Incentive — earned vs achievable", "💸")
        incentive_donut(inc)
        comp_rows = [{"Component": c["name"], "Value": round(c["value"], 1),
                      "Earned ₹": int(c["earned"]), "Max ₹": int(c["max"])} for c in inc["comps"]]
        st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)
        itx = incentive_nudge_text(prow, inc)
        if itx: inc_card(itx)

        sec("Channels", "🔗")
        kpi_grid([
            ("Onboarded", f"{int(prow['Channels Onboarded'])}", "DSAs / dealers"),
            ("Active", f"{int(prow['Channels Active'])}", f"{prow['Channels Active']/max(prow['Channels Onboarded'],1)*100:.0f}% utilisation"),
        ])

    # ---------------- TRENDS ----------------
    with t_trend:
        sec("Disbursal trend", "📈")
        g = perf_all.groupby("Month Label", sort=False).agg(
            Disb_Cr=("Actual Disb Amount (Rs Cr)", "sum"),
            Disb_U=("Actual Disb #", "sum")).reindex(MONTH_ORDER).reset_index()
        fig = go.Figure()
        fig.add_bar(x=g["Month Label"], y=g["Disb_Cr"], marker_color="#1FA89A", name="Disb ₹Cr")
        fig.add_trace(go.Scatter(x=g["Month Label"], y=g["Disb_U"], yaxis="y2", mode="lines+markers",
                                 line=dict(color="#D4936B", width=3), name="Disb units"))
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False, color="#6B8788"))
        plotly_theme(fig, 250)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        sec("ROI & cross-sell trend", "📈")
        g2 = perf_all.groupby("Month Label", sort=False).agg(
            ROI=("Actual ROI %", "mean"), XS=("Actual Cross Sell %", "mean")).reindex(MONTH_ORDER).reset_index()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=g2["Month Label"], y=g2["ROI"], mode="lines+markers",
                                  line=dict(color="#0F3D3E", width=3), name="ROI %"))
        fig2.add_trace(go.Scatter(x=g2["Month Label"], y=g2["XS"], mode="lines+markers",
                                  line=dict(color="#D4936B", width=3), name="Cross-Sell %"))
        plotly_theme(fig2, 220)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        sec(("Property mix" if prod == "SBL" else "Vehicle mix"), "🏷️")
        mix_chart(port_m)

        sec(("OTC ageing (SBL)" if prod == "SBL" else "PDD ageing (Wheels)"), "⏳")
        if port_m is not None and not port_m.empty:
            col = "OTC Days" if prod == "SBL" else "PDD Days"
            days = pd.to_numeric(port_m[col], errors="coerce").fillna(0)
            buckets = pd.cut(days, [-1, 0, 30, 60, 9999],
                             labels=["0", "1-30", "31-60", "60+"]).value_counts().reindex(["0", "1-30", "31-60", "60+"])
            fig3 = go.Figure(go.Bar(x=buckets.index, y=buckets.values, marker_color="#5BAFA8"))
            plotly_theme(fig3, 200)
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

        sec("Productivity (disb units / month)", "⚙️")
        st.caption(f"Latest: {int(prow['Productivity (Disb/RM)'])} cases · avg ticket ₹{prow['Avg Ticket Size (Rs L)']:.1f} L")


# =============================================================================
# MANAGER-LEVEL SHARED BLOCKS
# =============================================================================
def indicator_bar(my, peer, l1="Mine", l2="Peer"):
    fig = go.Figure(go.Bar(x=[l1, l2], y=[my, peer], marker_color=["#1FA89A", "#D4936B"],
                           text=[f"₹{my:.2f}", f"₹{peer:.2f}"], textposition="outside"))
    plotly_theme(fig, 190)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def leaderboard(window, by):
    if window is None or window.empty:
        st.caption("No data."); return
    rows = []
    for key, g in window.groupby(by):
        rows.append({by: key, "PBHO (Cr)": round(agg_value(g, "PBHO (Rs Cr)"), 2),
                     "AuM (Cr)": round(agg_value(g, "AUM (Rs Cr)"), 2),
                     "ROI %": round(agg_value(g, "ROI %"), 2)})
    df = pd.DataFrame(rows).sort_values("PBHO (Cr)", ascending=False).head(10)
    st.dataframe(df, use_container_width=True, hide_index=True)

def pnl_cards(window):
    if window is None or window.empty:
        st.caption("No P&L data for this selection."); return
    items = [
        ("AuM",            f"₹{agg_value(window,'AUM (Rs Cr)'):.2f} Cr", "book size"),
        ("PBHO",           f"₹{agg_value(window,'PBHO (Rs Cr)'):.2f} Cr", "before HO alloc"),
        ("ROI",            f"{agg_value(window,'ROI %'):.2f}%", "yield"),
        ("NIM",            f"{agg_value(window,'NIM %'):.2f}%", "net interest margin"),
        ("Cross-Sell Inc", f"₹{agg_value(window,'Cross Sell Income (Rs Cr)'):.2f} Cr", "fee income"),
        ("Credit Cost",    f"₹{agg_value(window,'Credit Cost (Rs Cr)'):.2f} Cr", "provisions"),
    ]
    kpi_grid(items)

def pnl_breakdown(window, by):
    if window is None or window.empty:
        st.caption("No data."); return
    rows = []
    for key, g in window.groupby(by):
        rows.append({by: key,
                     "AuM (Cr)": round(agg_value(g, "AUM (Rs Cr)"), 2),
                     "PBHO (Cr)": round(agg_value(g, "PBHO (Rs Cr)"), 2),
                     "ROI %": round(agg_value(g, "ROI %"), 2),
                     "30+ DPD %": round(agg_value(g, "30+ DPD %"), 2)})
    df = pd.DataFrame(rows).sort_values("PBHO (Cr)", ascending=False)
    st.dataframe(df, use_container_width=True, hide_index=True)

def team_incentive(perf_m, prof_m):
    if perf_m is None or perf_m.empty:
        return
    prof_idx = prof_m.drop_duplicates("RM ID").set_index("RM ID")
    rows = []; tot_e = 0.0; tot_m = 0.0
    for _, pr in perf_m.iterrows():
        rid = pr["Emp ID"]
        profrow = prof_idx.loc[rid] if rid in prof_idx.index else None
        inc = compute_incentive(pr, profrow)
        tot_e += inc["earned"]; tot_m += inc["max"]
        if inc["nudges"] and inc["earned"] < inc["max"]:
            nd = sorted(inc["nudges"],
                        key=lambda x: (0 if x["metric"] == "disb_ach_pct" else 1, x["gap"]))[0]
            if nd["gap"] <= 8:
                rows.append((pr["RM Name"], pr["Branch Name"], round(nd["cur"], 0),
                             nd["need"], int(nd["delta"])))
    kpi_grid([("Team incentive (mo)", f"₹{tot_e:,.0f}", f"of ₹{tot_m:,.0f} achievable"),
              ("Headroom", f"₹{tot_m - tot_e:,.0f}", "untapped this month")])
    rows = sorted(rows, key=lambda r: r[4], reverse=True)
    if rows:
        sec(f"RMs one push from a higher incentive slab ({len(rows)})", "💸")
        for r in rows[:8]:
            inc_card(f"<b>{r[0]}</b> · {r[1]} — at {int(r[2])}% disb; reach {int(r[3])}% to add +₹{r[4]:,}")

def day_nudges(perf_m, sel, branch_days):
    if sel != CURRENT_MONTH:
        st.caption("Day-based alerts are shown for the live month (Jun-26)."); return
    br = perf_m.groupby("Branch Name").agg(gap=("Days Since Last Disb", "min")).reset_index()
    cold = br[br["gap"] > branch_days].sort_values("gap", ascending=False)
    sec(f"Branches with no disbursal in last {branch_days} days ({len(cold)})", "🥶")
    if cold.empty:
        st.caption("None — all branches active.")
    for _, c in cold.head(12).iterrows():
        action_card(f"<b>{c['Branch Name']}</b> · {int(c['gap'])} days since last disbursal")
    nl = perf_m[perf_m["Days Since Last Login"] > NOLOGIN_RM_DAYS] \
        .sort_values("Days Since Last Login", ascending=False)
    sec(f"RMs with zero logins in last {NOLOGIN_RM_DAYS} days ({nl['Emp ID'].nunique()})", "😴")
    if nl.empty:
        st.caption("None — every RM has logged in.")
    for _, c in nl.head(12).iterrows():
        action_card(f"<b>{c['RM Name']}</b> · {c['Branch Name']} · {int(c['Days Since Last Login'])} days")

def pip_list(perf_m):
    pip = perf_m[perf_m["PIP Flag"] == "Yes"]
    sec(f"PIP RMs ({pip['Emp ID'].nunique()})", "🚩")
    if pip.empty:
        st.caption("No PIP-flagged RMs in scope."); return
    t = pip.groupby(["Branch Name", "RM Name"]).agg(
        Disb_Cr=("Actual Disb Amount (Rs Cr)", "sum")).reset_index().round(2)
    st.dataframe(t, use_container_width=True, hide_index=True)

def zero_rms(perf_m):
    z = perf_m[perf_m["Actual Disb #"] == 0]
    sec(f"RMs sitting at zero disbursal ({z['Emp ID'].nunique()})", "⭕")
    if z.empty:
        st.caption("None — every RM has disbursed."); return
    for _, c in z.drop_duplicates("Emp ID").head(15).iterrows():
        action_card(f"<b>{c['RM Name']}</b> · {c['Branch Name']}")

def poor_branches(prof_m):
    g = prof_m.groupby("Branch Name").agg(
        PBHO=("PBHO (Rs Cr)", "sum"), DPD=("30+ DPD %", "mean")).reset_index().sort_values("PBHO").round(2)
    sec("Branches needing attention (lowest PBHO)", "🔻")
    st.dataframe(g.head(10), use_container_width=True, hide_index=True)

def nonproductive(perf_m):
    rz = perf_m[perf_m["Actual Disb #"] == 0].drop_duplicates("Emp ID")
    sec(f"Non-productive RMs ({rz['Emp ID'].nunique()})", "🚫")
    st.caption(", ".join(rz["RM Name"].head(25)) if not rz.empty else "None")
    bz = perf_m.groupby(["Branch Name", "BBM Name"]).agg(d=("Actual Disb #", "sum")).reset_index()
    bz = bz[bz["d"] == 0]
    sec(f"Branches / BBMs with zero disbursal ({len(bz)})", "🚫")
    st.caption(", ".join((bz["Branch Name"] + " (" + bz["BBM Name"] + ")").head(20)) if not bz.empty else "None")

def attrition_block(user, data, prod, sel):
    a_m   = scope(data["attr"], user, prod, sel)
    a_ytd = scope(data["attr"], user, prod, sel, ytd=True)
    if a_ytd is None or a_ytd.empty:
        st.caption("No attrition data in scope."); return
    kpi_grid([
        ("RM attrition (YTD)", f"{a_ytd['RM Attrition %'].mean():.1f}%",
         f"{int(a_ytd['RM Exits'].sum())} exits · {int(a_ytd['RM Joiners'].sum())} joiners"),
        ("BBM attrition (YTD)", f"{a_ytd['BBM Attrition %'].mean():.1f}%",
         f"{int(a_ytd['BBM Exits'].sum())} exits"),
    ])
    g = a_ytd.groupby("Area").agg(RM_Exits=("RM Exits", "sum"), RM_Join=("RM Joiners", "sum"),
                                  Attr=("RM Attrition %", "mean")).reset_index().round(1)
    st.dataframe(g, use_container_width=True, hide_index=True)

def branch_category(user, data, prod):
    o = scope(data["org"], user, prod)
    if o is None or o.empty:
        st.caption("No branches in scope."); return
    if prod == "Wheels":
        cols = ["Branch Cat Wheels"]
    elif prod == "SBL":
        cols = ["Branch Cat SBL"]
    else:
        cols = ["Branch Cat SBL", "Branch Cat Wheels"]
    brs = o.drop_duplicates("Branch ID")
    for col in cols:
        lbl = "SBL" if "SBL" in col else "Wheels"
        vc = brs[col].value_counts().reindex(["Platinum", "Gold", "Silver", "Bronze"]).fillna(0).astype(int)
        sec(f"Branch category — {lbl}", "🏷️")
        st.caption(" · ".join(f"{k}: {v}" for k, v in vc.items()))

def spot_award_widget(user, data, prod, eligible_levels, key):
    st.session_state.setdefault("spot_awards", [])
    o = scope(data["org"], user, prod)
    name_col = {"RM": "RM Name", "BBM": "BBM Name", "ABM": "ABM Name"}
    candidates = []
    for lv in eligible_levels:
        if o is not None and not o.empty and name_col[lv] in o.columns:
            candidates += [(f"{lv} · {n}") for n in sorted(o[name_col[lv]].dropna().unique())]
    sec("🏆 Spot Award — All-India recognition", "")
    st.caption("Recognise standout performers. (Mock: this wall persists for your current session only.)")
    with st.form(key=f"spot_form_{key}", clear_on_submit=True):
        pick = st.selectbox("Recognise", candidates if candidates else ["—"], key=f"spot_pick_{key}")
        reason = st.text_input("Reason / citation", key=f"spot_reason_{key}",
                               placeholder="e.g. Highest June disbursal in zone")
        if st.form_submit_button("Give Spot Award ⭐") and candidates and reason.strip():
            st.session_state["spot_awards"].insert(0, {
                "who": pick, "reason": reason.strip(), "by": user["name"],
                "level": user["level"], "when": CURRENT_DATE.strftime("%d-%b-%Y")})
            st.success("Spot Award recorded on the recognition wall.")
    wall = st.session_state["spot_awards"]
    if wall:
        sec(f"Recognition wall ({len(wall)})", "🌟")
        for w in wall[:12]:
            wall_card(f"⭐ <b>{w['who']}</b> — {w['reason']}<br>"
                      f"<span style='font-size:10px;color:#6B8788'>by {w['by']} ({w['level']}) · {w['when']}</span>")


# =============================================================================
# MANAGER DASHBOARD  (BBM -> CXO, feature-gated by rank)
# =============================================================================
def manager_dashboard(user, data, prod_ov=None):
    level = user["level"]; rank = RANK[level]
    prod = prod_ov if prod_ov is not None else user["product"]

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    brand_bar(user, prod)
    sel = month_selector()

    perf_m   = scope(data["perf"], user, prod, sel)
    prof_m   = scope(data["prof"], user, prod, sel)
    port_m   = scope(data["port"], user, prod, sel)
    perf_all = order_months(scope(data["perf"], user, prod, None))

    if perf_m is None or perf_m.empty:
        st.warning("No data for this selection."); return

    t_focus, t_perf, t_team, t_peer, t_pnl = st.tabs(
        ["🎯 Focus", "📊 Performance", "👥 Team", "🏆 Peer Set", "💵 P&L"])

    # ---------------- FOCUS ----------------
    with t_focus:
        n_rm = perf_m["Emp ID"].nunique()
        n_br = perf_m["Branch ID"].nunique()
        disb_v = perf_m["Actual Disb Amount (Rs Cr)"].sum()
        tgt_v  = perf_m["Target Disb Amount (Rs Cr)"].sum()
        ach = disb_v / tgt_v * 100 if tgt_v else 0
        kpi_grid([
            ("Team size", f"{n_rm} RMs", f"{n_br} branch(es)"),
            ("Disb achievement", f"{ach:.0f}%", f"₹{disb_v:.1f} / {tgt_v:.1f} Cr"),
        ])

        zero_rms(perf_m)                                   # names of RMs at zero
        sec("Portfolio quality", "🩺")
        kpi_grid([
            ("30+ DPD", f"{prof_m['30+ DPD %'].mean():.2f}%", "scope avg"),
            ("90+ DPD", f"{prof_m['90+ DPD %'].mean():.2f}%", "scope avg"),
        ])
        team_incentive(perf_m, prof_m)                     # incentive nudges for the team

        if rank >= 3:                                      # RBM onwards
            day_nudges(perf_m, sel, NODISB_BRANCH_DAYS)
            pip_list(perf_m)
        if rank >= 4:                                      # ZBM onwards
            poor_branches(prof_m)
            nonproductive(perf_m)
            spot_award_widget(user, data, prod, ["RM", "BBM"], key=f"zbm_{user['id']}")
        if rank == 5:                                      # CXO
            sec("CXO watch — branches dark 7+ days", "🛰️")
            day_nudges(perf_m, sel, NODISB_BRANCH_CXO)
            spot_award_widget(user, data, prod, ["ABM"], key="cxo")

        ann = data["ann"]
        ann = ann[ann["Product"].isin([prod, "All", "SRL"])]
        if not ann.empty:
            sec("Announcements & contests", "📣")
            for _, a in ann.iterrows():
                tag = "🏆" if a["Type"] == "Contest" else "📌"
                announce_card(f"{tag} <b>{a['Title']}</b> ({a['Date']})<br>{a['Detail']}")

    # ---------------- PERFORMANCE ----------------
    with t_perf:
        sec("Team funnel — units & value", "📊")
        kpi_grid([
            ("Logins", f"{int(perf_m['Actual Login #'].sum())}",
             f"₹{perf_m['Actual Login Amount (Rs Cr)'].sum():.1f} Cr"),
            ("Sanctions", f"{int(perf_m['Actual Sanction #'].sum())}",
             f"₹{perf_m['Actual Sanction Amount (Rs Cr)'].sum():.1f} Cr"),
            ("Disbursals", f"{int(perf_m['Actual Disb #'].sum())}",
             f"₹{perf_m['Actual Disb Amount (Rs Cr)'].sum():.1f} Cr"),
            ("Avg ROI", f"{perf_m['Actual ROI %'].mean():.2f}%",
             f"X-sell {perf_m['Actual Cross Sell %'].mean():.1f}%"),
        ])
        sec("Disbursal trend", "📈")
        g = perf_all.groupby("Month Label", sort=False)["Actual Disb Amount (Rs Cr)"].sum().reindex(MONTH_ORDER)
        fig = go.Figure(go.Bar(x=g.index, y=g.values, marker_color="#1FA89A"))
        plotly_theme(fig, 220)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        sec(("Collateral mix" if prod == "SBL" else "Vehicle mix" if prod == "Wheels" else "Asset mix"), "🏷️")
        mix_chart(port_m)
        sec("Sourcing — direct vs channel", "🔗")
        kpi_grid([("Direct business", f"{perf_m['Direct Business %'].mean():.0f}%", "self-sourced"),
                  ("Productivity", f"{perf_m['Actual Disb #'].sum()/max(perf_m['Emp ID'].nunique(),1):.1f}",
                   "disb cases / RM")])

    # ---------------- TEAM ----------------
    with t_team:
        sec("Team snapshot", "👥")
        kpi_grid([
            ("RMs", f"{perf_m['Emp ID'].nunique()}", "active in scope"),
            ("Branches", f"{perf_m['Branch ID'].nunique()}", "in scope"),
            ("AuM", f"₹{agg_value(prof_m,'AUM (Rs Cr)'):.0f} Cr", "book"),
            ("PBHO (mo)", f"₹{prof_m['PBHO (Rs Cr)'].sum():.1f} Cr", "before HO"),
        ])
        sec("RM-wise productivity", "⚙️")
        branch_filter = "All branches"
        if rank >= 2:
            branches = ["All branches"] + sorted(perf_m["Branch Name"].unique().tolist())
            branch_filter = st.selectbox("Drill into branch", branches, key=f"team_branch_{level}")
        dfp = perf_m if branch_filter == "All branches" else perf_m[perf_m["Branch Name"] == branch_filter]
        prod_tbl = dfp.groupby(["Branch Name", "RM Name"]).agg(
            Disb_Units=("Actual Disb #", "sum"),
            Disb_Cr=("Actual Disb Amount (Rs Cr)", "sum"),
            ROI=("Actual ROI %", "mean")).reset_index().sort_values("Disb_Cr", ascending=False).round(2)
        st.dataframe(prod_tbl, use_container_width=True, hide_index=True)

        if rank >= 2:
            sec("Attrition (RM & BBM)", "📉")
            attrition_block(user, data, prod, sel)
            branch_category(user, data, prod)

    # ---------------- PEER SET ----------------
    with t_peer:
        prof_univ = data["prof"]
        if prod in ("SBL", "Wheels"):
            prof_univ = prof_univ[prof_univ["Product"] == prod]
        if rank == 1:
            sec("Peer set — top 10 branches (YTD PBHO)", "🏆")
            tbl, my, peer, _ = peer_benchmark(prof_univ, "Branch Name", user["branch"], sel, 10)
            st.dataframe(tbl, use_container_width=True, hide_index=True)
            sec("Your branch vs peer-set PBHO (YTD)", "")
            indicator_bar(my, peer, "My branch", "Peer avg")
        elif rank == 2:
            sec("Peer set — top 5 areas (YTD PBHO)", "🏆")
            tbl, my, peer, _ = peer_benchmark(prof_univ, "Area", user["area"], sel, 5)
            st.dataframe(tbl, use_container_width=True, hide_index=True)
            sec("Your area vs peer-set PBHO (YTD)", "")
            indicator_bar(my, peer, "My area", "Peer avg")
        else:
            scope_prof = scope(data["prof"], user, prod, None)
            scope_prof = scope_prof[scope_prof["Month Label"].isin(ytd_window(sel))]
            sec("Top areas in your scope (YTD PBHO)", "🏆")
            leaderboard(scope_prof, "Area")
            sec("Top branches in your scope (YTD PBHO)", "🏅")
            leaderboard(scope_prof, "Branch Name")

    # ---------------- P&L ----------------
    with t_pnl:
        prof_scope_all = scope(data["prof"], user, prod, None)
        mode = st.radio("View", ["YTD", "Month"], horizontal=True, key=f"pnl_mode_{level}")
        window = (prof_scope_all[prof_scope_all["Month Label"].isin(ytd_window(sel))]
                  if mode == "YTD" else prof_scope_all[prof_scope_all["Month Label"] == sel])
        work = window
        if rank >= 4:
            sec("State P&L", "🗺️")
            states = ["All"] + sorted(window["State"].unique().tolist())
            ssel = st.selectbox("State", states, key=f"pnl_state_{level}")
            if ssel != "All":
                work = work[work["State"] == ssel]
        if rank >= 3:
            areas = ["All"] + sorted(work["Area"].unique().tolist())
            asel = st.selectbox("Area", areas, key=f"pnl_area_{level}")
            if asel != "All":
                work = work[work["Area"] == asel]
        if rank >= 2:
            brs = ["All"] + sorted(work["Branch Name"].unique().tolist())
            bsel = st.selectbox("Branch", brs, key=f"pnl_branch_{level}")
            if bsel != "All":
                work = work[work["Branch Name"] == bsel]

        sec(f"P&L — {mode}", "💵")
        pnl_cards(work)
        by = ("State" if rank >= 4 else "Area" if rank >= 3 else "Branch Name" if rank >= 2 else "RM Name")
        # if drilled down to a single branch, break out by RM
        if rank >= 2 and work["Branch Name"].nunique() == 1:
            by = "RM Name"
        sec(f"Breakdown by {by}", "")
        pnl_breakdown(work, by)

        if rank == 1:
            st.caption("📌 Phase 2: daily projection entry for your branch will appear here.")


# =============================================================================
# CXO + ADMIN
# =============================================================================
def cxo_dashboard(user, data):
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    pick = st.radio("Product view", ["All (SRL)", "SBL", "Wheels"], horizontal=True, key="cxo_prod")
    prod_ov = None if pick.startswith("All") else pick
    manager_dashboard(user, data, prod_ov=prod_ov)

def admin_dashboard(user, data):
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    brand_bar(user)
    month_selector()
    sec("System overview", "🛠️")
    perf = data["perf"]; jun = perf[perf["Month Label"] == CURRENT_MONTH]
    kpi_grid([
        ("Total RMs", f"{perf['Emp ID'].nunique()}", "SBL + Wheels"),
        ("Branches", f"{perf['Branch ID'].nunique()}", "across products"),
        ("Zero-disb RMs (Jun)", f"{(jun['Actual Disb #'] == 0).sum()}", "needs attention"),
        ("PIP RMs", f"{(jun['PIP Flag'] == 'Yes').sum()}", "flagged"),
    ])
    sec("Data sheets loaded", "📄")
    for k, df in data.items():
        st.caption(f"• {k}: {df.shape[0]:,} rows × {df.shape[1]} cols")
    st.info("Upload a refreshed workbook to `arkin/arkin_dummy_data.xlsx` to update all dashboards.")


# =============================================================================
# LOGIN
# =============================================================================
def login_screen():
    st.markdown('<div class="login-outer"></div>', unsafe_allow_html=True)
    st.markdown("""<div class="login-inner">
      <div><span class="login-arka">ARKA</span><span class="login-kq">KinetiQ</span></div>
      <div class="login-tag">Intelligence in Motion</div>
      <div class="login-headline">Performance,<br><span class="login-accent">in real time.</span></div>
      <div class="login-sub">Secured Retail Lending · SBL & Wheels · FY26-27 to-date</div>
    </div>""", unsafe_allow_html=True)

    with st.form("arkin_login"):
        u = st.text_input("User ID", placeholder="e.g. rm.30001")
        p = st.text_input("Password", type="password", placeholder="••••••••")
        ok = st.form_submit_button("Sign in →")
        if ok:
            usr = do_login(u, p)
            if usr:
                st.session_state["user"] = usr
                st.rerun()
            else:
                st.error("Invalid credentials. Try a demo login below.")

    st.markdown("""<div class="login-footer">
      Demo password for every role: <span class="pw">arkin@2026</span>
      <span class="grp">RM rm.30001 (SBL) / rm.40001 (Wheels) · BBM bbm.6001 / bbm.7001</span>
      <span class="grp">ABM abm.2001 / abm.2501 · RBM rbm.201 / rbm.251 · ZBM zbm.101 / zbm.151</span>
      <span class="grp">CXO cxo · Admin admin</span>
      <span class="grp">Arka Fincap · Kirloskar Group</span>
    </div>""", unsafe_allow_html=True)


# =============================================================================
# MAIN
# =============================================================================
def main():
    inject_css()
    user = st.session_state.get("user")
    if not user:
        login_screen()
        return
    data = load_data()
    lvl = user["level"]
    if lvl == "RM":
        rm_dashboard(user, data)
    elif lvl in ("BBM", "ABM", "RBM", "ZBM"):
        manager_dashboard(user, data)
    elif lvl == "CXO":
        cxo_dashboard(user, data)
    else:
        admin_dashboard(user, data)


if __name__ == "__main__":
    main()
