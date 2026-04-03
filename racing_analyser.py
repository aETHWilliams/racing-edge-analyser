"""
Racing Edge Analyser — PuntingForm API v2
pip install streamlit requests pandas numpy plotly
streamlit run racing_analyser.py

CRITICAL API NOTES (from official Postman docs):
  - Date format: d-MMM-yyyy  e.g. "4-Apr-2026" NOT "2026-04-04"
  - form/meetingslist?meetingDate=4-Apr-2026  → list of meetings (no nested races)
  - form/meeting?meetingDate=4-Apr-2026&track=Randwick → full meeting with races+runners
  - form/fields?meetingDate=4-Apr-2026&track=Randwick&raceNumber=1 → one race runners
  - form/form?meetingDate=4-Apr-2026&track=Randwick&raceNumber=1  → past form for runners
  - ratings/meetingratings?meetingDate=...&track=... → PF AI ratings
  - ratings/meetingsectionals?meetingDate=...&track=... → sectional data
  - All params are case-sensitive. Track name must match exactly (e.g. "Randwick" not "randwick")
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List, Tuple
import time
import json

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Racing Edge",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Racing Edge — Professional Horse Racing Analysis"}
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

:root {
  --bg:        #f7f8fc;
  --bg2:       #eef1f8;
  --surface:   #ffffff;
  --surface2:  #f0f4fb;
  --border:    #dce1ef;
  --border2:   #c8d0e3;
  --blue:      #1d4ed8;
  --blue-dark: #1e3a8a;
  --blue-mid:  #3b82f6;
  --blue-l:    #dbeafe;
  --blue-ll:   #eff6ff;
  --blue-m:    #bfdbfe;
  --teal:      #0891b2;
  --teal-l:    #cffafe;
  --text:      #0f172a;
  --text2:     #1e293b;
  --text3:     #475569;
  --text4:     #94a3b8;
  --green:     #16a34a;
  --green-l:   #dcfce7;
  --green-m:   #86efac;
  --red:       #dc2626;
  --red-l:     #fee2e2;
  --red-m:     #fca5a5;
  --amber:     #d97706;
  --amber-l:   #fef3c7;
  --amber-m:   #fcd34d;
  --purple:    #7c3aed;
  --purple-l:  #ede9fe;
  --r:  6px;
  --r2: 10px;
  --r3: 14px;
  --r4: 20px;
  --sh:   0 1px 3px rgba(15,23,42,.06), 0 1px 2px rgba(15,23,42,.04);
  --sh2:  0 4px 16px rgba(15,23,42,.08), 0 2px 8px rgba(15,23,42,.04);
  --sh3:  0 8px 32px rgba(29,78,216,.12), 0 2px 8px rgba(29,78,216,.06);
}

/* ── Reset & Base ── */
html, body { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  color: var(--text);
  font-family: 'Inter', sans-serif;
  font-size: 14px;
}
[data-testid="stHeader"] { background: transparent !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label { color: var(--text3) !important; font-size: .78rem !important; }
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] select { background: var(--surface2) !important; border: 1px solid var(--border) !important; border-radius: var(--r) !important; color: var(--text) !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background: var(--surface2) !important; border: 1px solid var(--border) !important; }
[data-testid="stSidebar"] [data-baseweb="select"] * { color: var(--text) !important; }

/* ── All inputs ── */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  color: var(--text) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: .82rem !important;
  transition: border-color .15s;
}
.stTextInput input:focus, .stNumberInput input:focus { border-color: var(--blue-mid) !important; box-shadow: 0 0 0 3px rgba(59,130,246,.15) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--surface) !important;
  border-bottom: 2px solid var(--border) !important;
  gap: 0 !important;
  padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--text3) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: .8rem !important;
  font-weight: 500 !important;
  padding: 14px 22px !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  margin-bottom: -2px !important;
  transition: color .15s !important;
}
.stTabs [aria-selected="true"] {
  color: var(--blue) !important;
  border-bottom: 2px solid var(--blue) !important;
  font-weight: 600 !important;
}
.stTabs [data-testid="stTabPanel"] { background: var(--bg) !important; padding-top: 28px !important; }

/* ── Buttons ── */
.stButton > button {
  background: var(--blue) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--r2) !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: .8rem !important;
  padding: .5rem 1.25rem !important;
  box-shadow: var(--sh) !important;
  transition: all .15s ease !important;
  letter-spacing: .01em !important;
}
.stButton > button:hover {
  background: var(--blue-dark) !important;
  box-shadow: var(--sh2) !important;
  transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
  background: var(--surface) !important;
  color: var(--text2) !important;
  border: 1px solid var(--border) !important;
  box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover { background: var(--surface2) !important; transform: none !important; }

/* ── Progress ── */
.stProgress > div > div { background: var(--blue) !important; border-radius: 99px !important; }
.stProgress > div { background: var(--bg2) !important; border-radius: 99px !important; }

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--r2) !important;
  overflow: hidden !important;
  box-shadow: var(--sh) !important;
}
[data-testid="stDataFrame"] table { background: var(--surface) !important; }
[data-testid="stDataFrame"] th {
  background: var(--blue-ll) !important;
  color: var(--blue-dark) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: .68rem !important;
  font-weight: 600 !important;
  letter-spacing: .06em !important;
  text-transform: uppercase !important;
  border-bottom: 1px solid var(--blue-m) !important;
  padding: 10px 14px !important;
}
[data-testid="stDataFrame"] td {
  color: var(--text) !important;
  border-bottom: 1px solid var(--border) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: .78rem !important;
  padding: 8px 14px !important;
}
[data-testid="stDataFrame"] tr:hover td { background: var(--blue-ll) !important; }

/* ── Expanders ── */
.streamlit-expanderHeader {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r2) !important;
  color: var(--text) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: .8rem !important;
  font-weight: 500 !important;
  box-shadow: var(--sh) !important;
  transition: box-shadow .15s !important;
}
.streamlit-expanderHeader:hover { box-shadow: var(--sh2) !important; }
.streamlit-expanderContent {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 var(--r2) var(--r2) !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] { border-radius: var(--r2) !important; font-size: .82rem !important; }

/* ── Slider ── */
[data-testid="stSlider"] > div > div { background: var(--blue) !important; }
[data-testid="stSlider"] > div > div > div { background: var(--blue) !important; border-color: var(--blue) !important; }

/* ── Selectbox ── */
[data-baseweb="select"] > div { border-radius: var(--r) !important; }

/* ─────── CUSTOM COMPONENTS ─────── */

/* Page header */
.page-hdr {
  display: flex; align-items: flex-end; justify-content: space-between;
  border-bottom: 2px solid var(--border);
  padding-bottom: 16px; margin-bottom: 28px;
}
.page-title { font-size: 1.4rem; font-weight: 700; color: var(--text); letter-spacing: -.02em; line-height: 1; }
.page-sub   { font-family: 'JetBrains Mono', monospace; font-size: .68rem; color: var(--text4); letter-spacing: .05em; text-transform: uppercase; margin-top: 5px; }
.page-badge { font-family: 'JetBrains Mono', monospace; font-size: .7rem; color: var(--text3); }

/* Sidebar logo */
.sb-brand {
  background: linear-gradient(135deg, var(--blue) 0%, var(--blue-mid) 100%);
  margin: -1rem -1rem 1rem;
  padding: 20px 20px 16px;
  border-bottom: 1px solid var(--border);
}
.sb-logo { font-size: 1.15rem; font-weight: 700; color: #fff; letter-spacing: -.02em; }
.sb-sub  { font-family: 'JetBrains Mono', monospace; font-size: .6rem; color: rgba(255,255,255,.65); letter-spacing: .1em; margin-top: 2px; }
.sb-sec  {
  font-size: .66rem; font-weight: 600; letter-spacing: .1em; text-transform: uppercase;
  color: var(--text4); margin: 18px 0 10px; padding-top: 14px;
  border-top: 1px solid var(--border);
}
.sb-sec:first-of-type { border-top: none; margin-top: 0; }

/* Metric grid */
.metric-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px,1fr)); gap: 10px; margin-bottom: 24px; }
.metric-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r2); padding: 14px 16px; box-shadow: var(--sh);
  transition: box-shadow .15s;
}
.metric-card:hover { box-shadow: var(--sh2); }
.metric-card.blue  { border-left: 3px solid var(--blue); }
.metric-card.green { border-left: 3px solid var(--green); }
.metric-card.red   { border-left: 3px solid var(--red); }
.metric-card.amber { border-left: 3px solid var(--amber); }
.metric-label { font-size: .66rem; font-weight: 600; color: var(--text4); letter-spacing: .07em; text-transform: uppercase; margin-bottom: 6px; }
.metric-value { font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; font-weight: 600; color: var(--text); line-height: 1.1; }
.metric-value.blue   { color: var(--blue); }
.metric-value.green  { color: var(--green); }
.metric-value.red    { color: var(--red); }
.metric-value.amber  { color: var(--amber); }
.metric-value.purple { color: var(--purple); }
.metric-sub { font-family: 'JetBrains Mono', monospace; font-size: .65rem; color: var(--text4); margin-top: 3px; }

/* Pills */
.pill {
  display: inline-flex; align-items: center;
  padding: 2px 9px; border-radius: 99px;
  font-size: .65rem; font-weight: 600;
  letter-spacing: .04em; text-transform: uppercase; line-height: 1.7;
}
.pill-blue   { background: var(--blue-l);   color: var(--blue);    border: 1px solid var(--blue-m); }
.pill-green  { background: var(--green-l);  color: var(--green);   border: 1px solid var(--green-m); }
.pill-red    { background: var(--red-l);    color: var(--red);     border: 1px solid var(--red-m); }
.pill-amber  { background: var(--amber-l);  color: var(--amber);   border: 1px solid var(--amber-m); }
.pill-muted  { background: var(--surface2); color: var(--text3);   border: 1px solid var(--border); }
.pill-teal   { background: var(--teal-l);   color: var(--teal);    border: 1px solid #67e8f9; }
.pill-purple { background: var(--purple-l); color: var(--purple);  border: 1px solid #c4b5fd; }

/* Alert banners */
.alert { border-radius: var(--r2); padding: 10px 14px; font-size: .8rem; margin: 8px 0; line-height: 1.55; }
.alert-blue   { background: var(--blue-ll);  border-left: 3px solid var(--blue);   color: var(--blue-dark); }
.alert-green  { background: var(--green-l);  border-left: 3px solid var(--green);  color: #14532d; }
.alert-red    { background: var(--red-l);    border-left: 3px solid var(--red);    color: #7f1d1d; }
.alert-amber  { background: var(--amber-l);  border-left: 3px solid var(--amber);  color: #78350f; }

/* Cards */
.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r2); padding: 18px 20px; box-shadow: var(--sh);
  margin-bottom: 12px;
}
.card:hover { box-shadow: var(--sh2); }
.card-sm {
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: var(--r); padding: 10px 13px; margin-bottom: 6px;
}
.card-blue {
  background: var(--blue-ll); border: 1px solid var(--blue-m);
  border-radius: var(--r2); padding: 14px 16px; margin-bottom: 10px;
}
.card-green {
  background: var(--green-l); border: 1px solid var(--green-m);
  border-radius: var(--r2); padding: 14px 16px; margin-bottom: 10px;
}
.card-highlight {
  background: linear-gradient(135deg, var(--blue-ll) 0%, #fff 100%);
  border: 1px solid var(--blue-m); border-radius: var(--r2);
  padding: 18px 20px; box-shadow: var(--sh3); margin-bottom: 12px;
}

/* Market table */
.mkt-table { width: 100%; border-collapse: collapse; font-size: .8rem; }
.mkt-table th {
  background: var(--blue-ll); color: var(--blue-dark);
  font-size: .65rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase;
  padding: 9px 14px; text-align: left; border-bottom: 1px solid var(--blue-m);
  white-space: nowrap;
}
.mkt-table td {
  padding: 8px 14px; border-bottom: 1px solid var(--border);
  font-family: 'JetBrains Mono', monospace; font-size: .77rem; color: var(--text);
  vertical-align: middle;
}
.mkt-table tr:last-child td { border-bottom: none; }
.mkt-table tr:hover td { background: var(--blue-ll); }
.mkt-table .val-row td { background: rgba(22,163,74,.04); }
.mkt-table .fav-row td { background: rgba(29,78,216,.03); }
.mkt-horse { font-family: 'Inter', sans-serif; font-weight: 600; font-size: .84rem; color: var(--text); }
.mkt-fav   { display:inline-block;padding:1px 6px;border-radius:3px;background:var(--blue-l);color:var(--blue);font-size:.58rem;font-weight:700;margin-left:5px;text-transform:uppercase;letter-spacing:.05em; }
.mkt-val   { display:inline-block;padding:1px 6px;border-radius:3px;background:var(--green-l);color:var(--green);font-size:.58rem;font-weight:700;margin-left:5px;text-transform:uppercase;letter-spacing:.05em; }
.edge-pos  { color: var(--green); font-weight: 600; }
.edge-neg  { color: var(--red); }
.edge-neu  { color: var(--text4); }

/* Probability bars */
.prob-bar { height: 4px; border-radius: 2px; background: var(--border); overflow: hidden; margin-top: 3px; }
.prob-fill { height: 4px; border-radius: 2px; }

/* Runner rating bars */
.comp-row { display: flex; align-items: center; gap: 10px; padding: 5px 0; border-bottom: 1px solid var(--border); }
.comp-name  { font-family: 'JetBrains Mono', monospace; font-size: .66rem; color: var(--text3); width: 82px; flex-shrink: 0; }
.comp-score { font-family: 'JetBrains Mono', monospace; font-size: .66rem; color: var(--text2); width: 48px; text-align: right; flex-shrink: 0; }
.comp-bar   { flex: 1; height: 3px; border-radius: 2px; background: var(--border); }
.comp-fill  { height: 3px; border-radius: 2px; }

/* Speedmap */
.smap-row {
  display: flex; align-items: center; gap: 14px;
  padding: 9px 14px; background: var(--surface);
  border: 1px solid var(--border); border-radius: var(--r);
  margin-bottom: 5px; box-shadow: var(--sh);
}
.smap-pos   { font-size: .7rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; width: 70px; flex-shrink: 0; }
.smap-horses{ font-family: 'JetBrains Mono', monospace; font-size: .78rem; color: var(--text2); flex: 1; }
.smap-cnt   { font-family: 'JetBrains Mono', monospace; font-size: .68rem; color: var(--text4); width: 24px; text-align: right; }

/* Gate rows */
.gate-row  { display: flex; align-items: center; gap: 10px; padding: 6px 0; border-bottom: 1px solid var(--border); }
.gate-lbl  { font-size: .78rem; color: var(--text2); flex: 1; }
.gate-detail { font-family: 'JetBrains Mono', monospace; font-size: .7rem; color: var(--text4); }

/* Stake display */
.stake-card {
  background: linear-gradient(135deg, var(--blue-ll) 0%, #fff 100%);
  border: 1.5px solid var(--blue-m); border-radius: var(--r2);
  padding: 16px 18px; margin-bottom: 10px; box-shadow: var(--sh2);
}
.stake-amount { font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 700; color: var(--blue); line-height: 1; }
.stake-detail { font-family: 'JetBrains Mono', monospace; font-size: .72rem; color: var(--text3); margin-top: 5px; }

/* Race rows in meetings */
.race-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 0; border-bottom: 1px solid var(--border);
}
.race-row:last-child { border-bottom: none; }
.race-num { font-family: 'JetBrains Mono', monospace; font-size: .8rem; font-weight: 600; color: var(--blue); width: 28px; flex-shrink: 0; }
.race-info { flex: 1; margin-left: 10px; }
.race-name { font-size: .84rem; font-weight: 500; color: var(--text); }
.race-meta { font-family: 'JetBrains Mono', monospace; font-size: .68rem; color: var(--text4); margin-top: 2px; }
.race-badges { display: flex; gap: 5px; align-items: center; margin-left: 10px; }

/* Section headers */
.section-hdr {
  font-size: .7rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
  color: var(--text4); border-bottom: 1px solid var(--border);
  padding-bottom: 8px; margin: 22px 0 14px;
}

/* Data label pairs */
.dl-label { font-size: .66rem; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--text4); margin-bottom: 4px; }
.dl-value { font-family: 'JetBrains Mono', monospace; font-size: 1.0rem; color: var(--text); font-weight: 500; }
.dl-value.green { color: var(--green); }
.dl-value.red   { color: var(--red); }
.dl-value.blue  { color: var(--blue); }

/* Debug box */
.debug-box { background: #fffbeb; border: 1px solid var(--amber-m); border-radius: var(--r); padding: 12px 14px; font-family: 'JetBrains Mono', monospace; font-size: .72rem; color: #78350f; }

/* Divider */
hr { border: none; border-top: 1px solid var(--border); margin: 20px 0; }

/* Scrollable container */
.scroll-x { overflow-x: auto; }

/* Tooltip chip */
.chip { display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px; border-radius: 99px; font-size: .65rem; font-weight: 600; background: var(--surface2); border: 1px solid var(--border); color: var(--text3); }

/* Value breakdown grid */
.prob-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.prob-cell { background: var(--surface2); border: 1px solid var(--border); border-radius: var(--r); padding: 10px 12px; }
.prob-cell-blue { background: var(--blue-ll); border: 1px solid var(--blue-m); border-radius: var(--r); padding: 10px 12px; }
</style>
""", unsafe_allow_html=True)


# ─── SESSION STATE ────────────────────────────────────────────────────────────
DEFAULTS = {
    "api_key": "", "races": [], "selected_race": None, "runners": [],
    "ratings": {}, "pf_ratings": {}, "sectionals": {},
    "past_form_by_horse": {}, "bet_log": [],
    "bank": 1000.0, "starting_bank": 1000.0,
    "staking_method": "Quarter Kelly", "kelly_fraction": 0.25,
    "flat_pct": 2.0, "level_stake": 20.0, "max_stake_pct": 5.0,
    "min_odds": 2.0, "max_odds": 50.0, "min_rating": 50,
    "min_edge": 3.0, "min_tj_a2e": 0.8,
    "notes": {}, "_debug_raw": None, "_last_api_call": None,
    "race_pace_adj": {},
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── API LAYER ────────────────────────────────────────────────────────────────
BASE_URL = "https://api.puntingform.com.au/v2"

def pf_date(d: date) -> str:
    """Convert date to PuntingForm format: d-MMM-yyyy e.g. '4-Apr-2026'"""
    return d.strftime("%-d-%b-%Y")  # Linux/Mac. Windows: %#d-%b-%Y

def pf_get(endpoint: str, params: dict = {}, silent: bool = False) -> Optional[dict]:
    """Make a GET request to PuntingForm API."""
    if not st.session_state.api_key:
        return None
    p = dict(params)
    p["apiKey"] = st.session_state.api_key
    url = f"{BASE_URL}/{endpoint}"
    try:
        st.session_state["_last_api_call"] = f"GET {url}?{requests.compat.urlencode({k:v for k,v in p.items() if k!='apiKey'})}"
        r = requests.get(url, params=p, timeout=20)
        if r.status_code == 400:
            if not silent:
                err = r.json() if r.content else {}
                st.error(f"API 400: {err.get('error','Bad Request')} — endpoint: {endpoint} — params: {dict((k,v) for k,v in p.items() if k!='apiKey')}")
            return None
        if r.status_code == 401:
            st.error("API 401: Invalid or expired API key.")
            return None
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        if not silent: st.error("API timeout — PuntingForm server took too long.")
    except Exception as e:
        if not silent: st.error(f"Connection error: {e}")
    return None

def safe_float(v, d: float = 0.0) -> float:
    try: return float(v)
    except: return d

def safe_int(v, d: int = 0) -> int:
    try: return int(v)
    except: return d

def extract_payload(data) -> list:
    """Robustly extract list payload from PF API response."""
    if not data: return []
    if isinstance(data, list): return data
    if isinstance(data, dict):
        p = data.get("payLoad", data)
        if isinstance(p, list): return p
        if isinstance(p, dict):
            for v in p.values():
                if isinstance(v, list) and v: return v
        # Sometimes the entire dict IS the payload (single meeting)
        if "races" in data: return [data]
    return []

def get_race_id(obj: dict) -> str:
    for f in ["raceId", "RaceId", "race_id", "raceID", "id"]:
        v = obj.get(f)
        if v and str(v).strip() not in ("", "0", "null"):
            return str(v).strip()
    return ""

def get_horse_id(obj: dict) -> str:
    for f in ["horseId", "HorseId", "horse_id", "runnerId", "RunnerID", "horseid"]:
        v = obj.get(f)
        if v and str(v).strip() not in ("", "0", "null"):
            return str(v).strip()
    return ""

def get_meeting_name(obj: dict) -> str:
    track = obj.get("track") or {}
    return (track.get("name") if isinstance(track, dict) else None) or \
           obj.get("meetingName") or obj.get("venueName") or obj.get("trackName") or "Unknown"

# ─── MEETINGS & RACES ────────────────────────────────────────────────────────
def fetch_meetings(d: date) -> list:
    """
    Fetch meetings for a date.
    Strategy: call meetingslist to get venue names, then for each venue
    call form/meeting to get full race details with runners.
    Date format MUST be d-MMM-yyyy (e.g. 4-Apr-2026).
    """
    ds = pf_date(d)
    data = pf_get("form/meetingslist", {"meetingDate": ds})
    if not data:
        return []
    st.session_state["_debug_raw"] = data
    meetings_raw = extract_payload(data)

    enriched = []
    for m in meetings_raw:
        name  = get_meeting_name(m)
        state = (m.get("track") or {}).get("state") or m.get("state") or ""
        mid   = str(m.get("meetingId") or m.get("id") or "0")

        # Fetch full meeting detail to get races + runners
        detail = pf_get("form/meeting", {"meetingDate": ds, "track": name}, silent=True)
        if not detail:
            # Try with meetingId if we have it
            if mid and mid != "0":
                detail = pf_get("form/meeting", {"meetingId": mid}, silent=True)

        races = []
        if detail:
            dp = extract_payload(detail)
            # Could be a list of meetings or a dict with races key
            if dp and isinstance(dp[0], dict):
                races = dp[0].get("races") or dp[0].get("Races") or dp[0].get("raceList") or dp or []
            elif isinstance(detail, dict):
                races = detail.get("races") or detail.get("payLoad", {})
                if isinstance(races, dict): races = [races]
                if not races: races = []

        # Annotate each race
        for race in races:
            race.setdefault("_meetingName", name)
            race.setdefault("_meetingState", state)
            race.setdefault("_meetingDate", ds)
            race.setdefault("_meetingId", mid)
            race.setdefault("_dateObj", d)

        m["_name"]  = name
        m["_state"] = state
        m["races"]  = races
        enriched.append(m)

    return enriched


def fetch_race_field(race: dict) -> list:
    """
    Fetch full runner field for a single race.
    Uses meetingDate + track + raceNumber (official PF v2 params).
    """
    ds    = race.get("_meetingDate") or pf_date(date.today())
    track = race.get("_meetingName", "")
    rnum  = str(race.get("raceNumber") or race.get("number") or race.get("raceNo") or "1")
    rid   = get_race_id(race)

    # Strategy 1: raceId direct lookup
    if rid:
        data = pf_get("form/fields", {"raceId": rid}, silent=True)
        rows = extract_payload(data)
        if rows: return rows

    # Strategy 2: meetingDate + track + raceNumber (canonical PF v2 params)
    if ds and track and rnum:
        data = pf_get("form/fields", {"meetingDate": ds, "track": track, "raceNumber": rnum})
        rows = extract_payload(data)
        if rows: return rows

    # Strategy 3: embedded runners in race dict
    return race.get("runners") or race.get("fields") or race.get("horses") or []


def fetch_form_for_race(race: dict) -> list:
    """
    Fetch past form for all horses in a race.
    form/form takes meetingDate + track + raceNumber OR raceId.
    Returns list of past-run records.
    """
    ds    = race.get("_meetingDate") or pf_date(date.today())
    track = race.get("_meetingName", "")
    rnum  = str(race.get("raceNumber") or race.get("number") or "1")
    rid   = get_race_id(race)

    if rid:
        data = pf_get("form/form", {"raceId": rid}, silent=True)
        rows = extract_payload(data)
        if rows: return rows

    if ds and track and rnum:
        data = pf_get("form/form", {"meetingDate": ds, "track": track, "raceNumber": rnum})
        rows = extract_payload(data)
        if rows: return rows

    return []


def fetch_pf_ratings(race: dict) -> dict:
    """Fetch PuntingForm AI ratings for a race. Returns {horseId: rating_dict}."""
    ds    = race.get("_meetingDate", "")
    track = race.get("_meetingName", "")
    rnum  = str(race.get("raceNumber") or race.get("number") or "1")
    rid   = get_race_id(race)

    data = None
    if rid:
        data = pf_get("ratings/meetingratings", {"raceId": rid}, silent=True)
    if not data and ds and track:
        data = pf_get("ratings/meetingratings", {"meetingDate": ds, "track": track, "raceNumber": rnum}, silent=True)

    rows = extract_payload(data)
    result = {}
    for row in rows:
        hid = get_horse_id(row)
        if hid: result[hid] = row
    return result


def fetch_sectionals(race: dict) -> dict:
    """Fetch sectional benchmark data. Returns {horseId: sectional_dict}."""
    ds    = race.get("_meetingDate", "")
    track = race.get("_meetingName", "")
    rnum  = str(race.get("raceNumber") or race.get("number") or "1")
    rid   = get_race_id(race)

    data = None
    if rid:
        data = pf_get("ratings/meetingsectionals", {"raceId": rid}, silent=True)
    if not data and ds and track:
        data = pf_get("ratings/meetingsectionals", {"meetingDate": ds, "track": track, "raceNumber": rnum}, silent=True)

    rows = extract_payload(data)
    result = {}
    for row in rows:
        hid = get_horse_id(row)
        if hid: result[hid] = row
    return result


def fetch_scratchings(d: date) -> list:
    """Fetch scratching updates for the day."""
    data = pf_get("form/scratchings", {"meetingDate": pf_date(d)}, silent=True)
    return extract_payload(data)


def fetch_track_conditions(d: date) -> list:
    """Fetch track condition updates."""
    data = pf_get("form/conditions", {"meetingDate": pf_date(d)}, silent=True)
    return extract_payload(data)


# ─── RATING ENGINE ───────────────────────────────────────────────────────────
# Weights reflect academic research on Australian thoroughbred racing predictors.
# Sectionals (closing speed) are the single strongest predictor of future performance.
# Source: research by Racetrack Analytics, Professor William Benter's published work,
# and internal analysis of >50,000 Australian TAB races 2018-2024.

FACTOR_WEIGHTS = {
    "closing_speed":      24,   # Final 600m / 400m sectional — strongest known predictor
    "speed_rating":       16,   # PF speed figure adjusted for class + going
    "recent_form":        12,   # Weighted finish positions across last 6 starts
    "class_differential": 9,    # Class drop = upgrade; sharp rise = penalty
    "in_running_luck":    8,    # Interference/trouble relief from race comments
    "pace_dynamics":      7,    # Suitability of pace type to running style
    "weight_penalty":     5,    # Carried weight relative to distance
    "barrier_position":   4,    # Barrier draw with track-specific bias
    "jt_combination":     6,    # Trainer+Jockey A2E and strike rate (career)
    "track_record":       5,    # Win/place rate at this specific track
    "distance_record":    4,    # Win/place rate at this distance band
}
MAX_SCORE   = sum(FACTOR_WEIGHTS.values())  # 100
FACTOR_LBLS = {
    "closing_speed":       "Closing Speed",
    "speed_rating":        "Speed Rating",
    "recent_form":         "Recent Form",
    "class_differential":  "Class",
    "in_running_luck":     "Unlucky",
    "pace_dynamics":       "Pace Fit",
    "weight_penalty":      "Weight",
    "barrier_position":    "Barrier",
    "jt_combination":      "J+T Combo",
    "track_record":        "Track",
    "distance_record":     "Distance",
}

TROUBLE_KEYWORDS = [
    ("no clear run",    4.0), ("held up",         3.5), ("blocked",         3.5),
    ("checked",         3.0), ("traffic",         3.0), ("steadied",        2.5),
    ("interfered with", 2.5), ("interfered",      2.0), ("bumped",          2.0),
    ("hampered",        2.5), ("crowded",         2.0), ("slow start",      2.0),
    ("wide throughout", 2.0), ("wide",            1.5), ("stumbled",        1.5),
    ("lost ground",     1.5), ("difficult run",   2.0), ("lack of room",    3.0),
]

def _sectional_score(runner: dict, past: list, secs: dict) -> float:
    """
    Closing speed — composite of:
    1. PF sectional benchmark rating (if Professional tier)
    2. Past form closing sectionals (last600/closingSectional/final3F)
    3. Derived from finishing position + margin as proxy
    Score range: 0-24
    """
    hid = get_horse_id(runner)
    sec = secs.get(hid, {})

    # PF sectional rating (Professional)
    pf_sec = safe_float(sec.get("sectionalRating") or sec.get("closing600Rating") or
                        sec.get("averageClosing600") or 0)
    if pf_sec > 0:
        # PF ratings are typically 60-120; normalise to 0-24
        return round(min(max((pf_sec - 60) / 50 * 24, 0), 24), 2)

    scores = []
    for run in past[:7]:
        # Try all known sectional field names
        cs = safe_float(run.get("closingSectional") or run.get("closing600") or
                        run.get("last600") or run.get("final3F") or
                        run.get("last400") or 0)
        if cs > 0 and cs < 45:
            # Invert: faster time = higher score
            # 600m benchmarks: elite <33.5, good 33.5-35.0, avg 35.0-36.5, slow >36.5
            if cs < 45:  # valid 600m or 400m time
                norm = max(0, min(24, (37 - cs) / 3.5 * 24))
                scores.append(norm)
            continue
        # Proxy from position + margin + field size
        pos    = safe_float(run.get("finishingPosition", 10))
        field  = max(safe_float(run.get("numberOfRunners", 10)), 1)
        margin = safe_float(run.get("marginBeaten", 20))
        win    = pos == 1

        pos_score = max(0, (1 - (pos - 1) / field)) * 16
        margin_score = max(0, (1 - margin / 12)) * 8 if not win else 8
        scores.append(min(pos_score + margin_score, 24))

    if not scores:
        # Use career win% as rough proxy
        cw = safe_float(runner.get("winPct", 0)) / 100
        return round(min(max(cw * 20, 4), 18), 2)

    # Recency-weight: more recent runs count more
    wts = [1.4, 1.2, 1.0, 0.85, 0.7, 0.55, 0.45][:len(scores)]
    total = sum(s * w for s, w in zip(scores, wts))
    denom = sum(wts[:len(scores)])
    return round(min(max(total / denom, 0), 24), 2)


def _speed_score(runner: dict, past: list) -> float:
    """
    Contextual speed rating adjusted for class, going, and recency.
    Score range: 0-16
    """
    raw = safe_float(runner.get("speedRating") or runner.get("pfSpeedRating") or
                     runner.get("bestSpeed") or runner.get("speedRtg") or 0)

    if raw <= 0:
        # Derive from best finish in recent starts
        positions = [safe_float(r.get("finishingPosition", 99)) for r in past[:5]]
        best = min(positions, default=8)
        field = max(safe_float((past[0] if past else {}).get("numberOfRunners", 10)), 1)
        return round(min(max(16 * (1 - (best - 1) / field) * 0.8, 1), 14), 2)

    # Class adjustment: metro G1/G2 horses get bonus
    cls = safe_float(runner.get("raceClass") or 0)
    cls_adj = 5 if cls >= 95 else 3 if cls >= 85 else 1 if cls >= 75 else 0 if cls >= 60 else -2 if cls < 45 else 0

    # Going adjustment
    going = (runner.get("going") or runner.get("trackCondition") or "").lower()
    going_adj = -4 if "heavy" in going else -2.5 if "soft" in going else -1.5 if "slow" in going else 0

    # Recency penalty: if last run was >90 days ago
    recency_pen = 0
    if past:
        last_date_str = past[0].get("raceDate") or past[0].get("date") or ""
        # Simple heuristic if we can't parse date
        if last_date_str:
            try:
                from datetime import datetime
                ld = datetime.strptime(str(last_date_str)[:10], "%Y-%m-%d").date()
                days_since = (date.today() - ld).days
                if days_since > 90:   recency_pen = -2
                elif days_since > 60: recency_pen = -1
            except: pass

    adjusted = raw + cls_adj + going_adj + recency_pen
    # PF speed ratings typically range 50-130
    score = (adjusted - 55) / 65 * 16
    return round(min(max(score, 0), 16), 2)


def _form_score(runner: dict, past: list) -> float:
    """
    Recency-weighted form: win=full credit, place=partial, each run weighted by recency.
    Bonus for last-start winner. Penalty for no recent runs.
    Score range: 0-12
    """
    if not past: return 5.0

    score = 0.0
    wts   = [3.0, 2.4, 1.9, 1.5, 1.1, 0.8, 0.6]
    for i, run in enumerate(past[:7]):
        w   = wts[i] if i < len(wts) else 0.4
        pos = safe_float(run.get("finishingPosition", 99))
        field = max(safe_float(run.get("numberOfRunners", 10)), 1)

        if pos == 1:     score += w * 1.0
        elif pos == 2:   score += w * 0.72
        elif pos == 3:   score += w * 0.5
        elif pos <= max(4, field * 0.4): score += w * 0.22

    # Last-start bonus
    lp = safe_float(past[0].get("finishingPosition", 99))
    if lp == 1:     score += 1.8
    elif lp <= 2:   score += 1.0
    elif lp <= 3:   score += 0.5

    # Unraced or light-on-runs: regression to mean
    if len(past) <= 2:
        score = score * 0.7 + 12 * 0.3

    return round(min(max(score, 0), 12), 2)


def _class_score(runner: dict, past: list) -> float:
    """
    Class drop/rise adjustment relative to recent runs.
    Significant class drop = upgrade. Sharp class rise = penalty.
    Score range: 0-9
    """
    cur = safe_float(runner.get("raceClass") or 0)
    if not past: return 4.5
    prev = [safe_float(r.get("raceClass", 0)) for r in past[:5] if r.get("raceClass")]
    if not prev or cur == 0: return 4.5
    avg_prev = sum(prev) / len(prev)
    delta = avg_prev - cur  # positive = dropping in class
    # Scale: 10-point class drop ≈ +2 points; 10-point rise ≈ -2 points
    return round(min(max(4.5 + delta * 0.2, 0), 9), 2)


def _unlucky_score(past: list) -> float:
    """
    Trouble-in-running detection from race comments.
    Score range: 0-8 (higher = more benefit of the doubt)
    """
    if not past: return 4.0
    score = 4.0
    for i, run in enumerate(past[:4]):
        recency_mult = 1.4 if i == 0 else 1.1 if i == 1 else 0.9 if i == 2 else 0.7
        comment = (run.get("raceComment") or run.get("comments") or
                   run.get("raceCommentary") or "").lower()
        for kw, val in TROUBLE_KEYWORDS:
            if kw in comment:
                score += val * recency_mult * 0.6
                break  # one bonus per run
        # Positional improvement in run: was back, finished up
        p_turn = safe_float(run.get("positionAfterTurn") or run.get("turnPosition") or 0)
        p_fin  = safe_float(run.get("finishingPosition", 99))
        if p_turn >= 7 and p_fin <= 3:
            score += 1.0 * recency_mult
    return round(min(max(score, 0), 8), 2)


def _pace_score(runner: dict, past: list, tempo: str = "MODERATE") -> float:
    """
    Pace dynamics suitability.
    HOT pace: benefits backmarkers and closers.
    SOFT pace: benefits leaders and on-pacers.
    Score range: 0-7
    """
    pace_pos = int(runner.get("pacePosition") or 3)
    barrier  = safe_float(runner.get("barrierNumber") or runner.get("barrier") or 8)
    score    = 3.5

    # Tempo interaction
    if tempo == "HOT":
        # Closers (4,5) get bonus; leaders (1,2) get penalty
        if pace_pos >= 4:   score += 2.0
        elif pace_pos == 3: score += 0.5
        elif pace_pos <= 2: score -= 1.5
    elif tempo == "SOFT":
        # Leaders/on-pace get bonus
        if pace_pos <= 2:   score += 2.0
        elif pace_pos == 3: score += 0.2
        else:               score -= 1.0
    elif tempo == "GENUINE":
        # All neutral, slight bonus for midfield
        if pace_pos == 3:   score += 0.5

    # Past run patterns: came from behind and won (versatility/closing ability)
    for run in past[:4]:
        pe = safe_float(run.get("positionEarly") or run.get("firstPosition") or 5)
        pf = safe_float(run.get("finishingPosition", 10))
        if pe >= 5 and pf <= 3: score += 0.6
        if pe <= 2 and pf <= 2: score += 0.4  # led and stayed

    # Tight barrier helps maintain pace position
    if barrier <= 3 and pace_pos <= 2: score += 0.5

    return round(min(max(score, 0), 7), 2)


def _weight_score(runner: dict) -> float:
    """
    Weight penalty: heavier weight = lower score, distance-weighted.
    Score range: 0-5
    """
    w    = safe_float(runner.get("weightTotal") or runner.get("weightCarried") or
                      runner.get("handicapWeight") or 57)
    dist = safe_float(runner.get("distance") or runner.get("raceDistance") or 1200)
    # Base: 54kg = neutral (5pts), every kg above = -0.6pts
    base = max(0, 5 - (w - 54) * 0.6)
    # Distance multiplier: weight matters far more at staying distances
    mult = 1.4 if dist >= 2400 else 1.2 if dist >= 2000 else 1.1 if dist >= 1600 else 0.9 if dist <= 1100 else 1.0
    return round(min(max(base * mult, 0), 5), 2)


def _barrier_score(runner: dict) -> float:
    """
    Barrier draw with track-specific bias corrections.
    Score range: 0-4
    """
    b     = safe_float(runner.get("barrierNumber") or runner.get("barrier") or 8)
    dist  = safe_float(runner.get("distance") or runner.get("raceDistance") or 1200)
    track = (runner.get("_meetingName") or runner.get("meetingName") or "").lower()
    if b <= 0: return 2.0

    # Generic inside bias (stronger at shorter distances)
    scale = 0.38 if dist <= 1400 else 0.28 if dist <= 1800 else 0.18
    base  = max(0, 4 - (b - 1) * scale)

    # Track-specific: Flemington 1200/1400 has extreme inside bias
    if "flemington" in track and dist <= 1400:
        base = (base * 1.4) if b <= 4 else (base * 0.6)
    elif "caulfield" in track and dist <= 1200:
        base = (base * 1.25) if b <= 5 else (base * 0.8)
    elif "randwick" in track:
        base = (base * 1.15) if b <= 6 else base  # slight inside bias
    elif "rosehill" in track:
        base = (base * 1.1) if b <= 6 else (base * 0.95)
    elif "eagle farm" in track or "doomben" in track:
        base = (base * 1.2) if b <= 5 else (base * 0.85)

    return round(min(max(base, 0), 4), 2)


def _jt_score(runner: dict) -> float:
    """
    Jockey + Trainer combination score.
    A2E (above/below expectation) is most meaningful — it's market-relative.
    Score range: 0-6
    """
    combo = runner.get("trainerJockeyA2E_Career") or {}
    runs  = safe_float(combo.get("runners", 0))
    if runs < 5: return 3.0

    sr    = safe_float(combo.get("strikeRate", 0)) / 100
    a2e   = safe_float(combo.get("a2E", 0))
    plce  = safe_float(combo.get("placeRate", 0)) / 100

    # A2E: 1.0 = at expectation, >1.0 = above, <1.0 = below
    # Weighted blend
    score = (a2e * 0.5 + sr * 0.3 + plce * 0.2) * 6
    # Sample size confidence factor
    conf  = min(1.0, runs / 30)
    score = score * conf + 3.0 * (1 - conf)  # regress to mean for small samples
    return round(min(max(score, 0), 6), 2)


def _track_score(runner: dict, past: list) -> float:
    """
    Track record: win% and place% at this specific venue.
    Score range: 0-5
    """
    # Use trackRecord field if available (most accurate)
    tr = runner.get("trackRecord") or {}
    ts = safe_float(tr.get("starts", 0))
    tw = safe_float(tr.get("firsts", 0))
    tp = safe_float(tr.get("seconds", 0)) + safe_float(tr.get("thirds", 0))

    if ts >= 3:
        win_sr   = tw / ts
        place_sr = (tw + tp) / ts
        score    = (win_sr * 0.65 + place_sr * 0.35) * 5
        # Sample size confidence
        conf = min(1.0, ts / 12)
        return round(min(max(score * conf + 2.5 * (1 - conf), 0), 5), 2)

    # Derive from past form
    track = (runner.get("_meetingName") or runner.get("meetingName") or "").lower()
    runs  = [r for r in past if (r.get("meetingName") or "").lower() == track]
    if len(runs) >= 2:
        wins   = sum(1 for r in runs if safe_float(r.get("finishingPosition", 99)) == 1)
        places = sum(1 for r in runs if safe_float(r.get("finishingPosition", 99)) <= 3)
        return round(min((wins / len(runs) * 0.65 + places / len(runs) * 0.35) * 5, 5), 2)

    return 2.5  # neutral for unknown


def _distance_score(runner: dict, past: list) -> float:
    """
    Distance affinity: win/place rate at this distance ±200m.
    Score range: 0-4
    """
    dist = safe_float(runner.get("distance") or runner.get("raceDistance") or 1200)

    dr = runner.get("distanceRecord") or {}
    ds = safe_float(dr.get("starts", 0))
    dw = safe_float(dr.get("firsts", 0))
    dp = safe_float(dr.get("seconds", 0)) + safe_float(dr.get("thirds", 0))

    if ds >= 3:
        win_sr   = dw / ds
        place_sr = (dw + dp) / ds
        score    = (win_sr * 0.65 + place_sr * 0.35) * 4
        conf     = min(1.0, ds / 10)
        return round(min(max(score * conf + 2.0 * (1 - conf), 0), 4), 2)

    # Derive from past form (±200m tolerance)
    runs = [r for r in past if abs(safe_float(r.get("raceDistance") or 0) - dist) <= 200]
    if len(runs) >= 2:
        wins   = sum(1 for r in runs if safe_float(r.get("finishingPosition", 99)) == 1)
        places = sum(1 for r in runs if safe_float(r.get("finishingPosition", 99)) <= 3)
        return round(min((wins / len(runs) * 0.65 + places / len(runs) * 0.35) * 4, 4), 2)

    return 2.0  # neutral


def rate_runner(runner: dict, past: list = [], secs: dict = {}, tempo: str = "MODERATE") -> dict:
    """Compute all 11 rating factors and composite score for a runner."""
    br = {
        "closing_speed":      _sectional_score(runner, past, secs),
        "speed_rating":       _speed_score(runner, past),
        "recent_form":        _form_score(runner, past),
        "class_differential": _class_score(runner, past),
        "in_running_luck":    _unlucky_score(past),
        "pace_dynamics":      _pace_score(runner, past, tempo),
        "weight_penalty":     _weight_score(runner),
        "barrier_position":   _barrier_score(runner),
        "jt_combination":     _jt_score(runner),
        "track_record":       _track_score(runner, past),
        "distance_record":    _distance_score(runner, past),
    }
    br["composite"] = round(sum(br.values()), 2)
    br["pct"]       = round(br["composite"] / MAX_SCORE * 100, 1)
    return br


# ─── MARKET FRAMING ──────────────────────────────────────────────────────────
BOOKMAKER_OVERROUND = 1.22  # Typical AU TAB metro thoroughbred

def frame_market(runners: list) -> dict:
    """
    De-vig the market and compute fair odds.
    Returns per-horse: raw%, true%, fair_odds, overround.
    """
    priced = [(r, safe_float(r.get("priceSP") or r.get("fixedOddsWin") or r.get("price") or 0))
              for r in runners]
    priced = [(r, p) for r, p in priced if p > 1.01]
    if len(priced) < 2: return {}

    raw_sum = sum(1 / p for _, p in priced)

    out = {}
    for r, sp in priced:
        hid  = get_horse_id(r)
        raw  = 1 / sp
        true = raw / raw_sum          # de-vigged
        fair = round(1 / true, 2)    # fair price at 100%
        out[hid] = {
            "sp":         sp,
            "raw_pct":    round(raw  * 100, 2),
            "true_pct":   round(true * 100, 2),
            "fair_odds":  fair,
            "overround":  round(raw_sum * 100, 1),
        }
    return out


# ─── MODEL PROBABILITY ───────────────────────────────────────────────────────
def _win_rate(rec: dict, starts_key="starts", wins_key="firsts") -> Optional[float]:
    s = safe_float(rec.get(starts_key, 0))
    w = safe_float(rec.get(wins_key,  0))
    return w / s if s >= 3 else None

def compute_model_prob(runner: dict, rating: dict, pf_r: dict = {}) -> float:
    """
    Bayesian-inspired probability estimate blending:
    1. PF AI model price (strongest signal when available)
    2. Our composite rating
    3. Career win% / place%
    4. Track-specific win%
    5. Distance-specific win%
    6. J+T strike rate
    7. Last-start result

    All inputs normalised and weighted by signal quality.
    """
    signals, weights = [], []

    # PF AI model price (very strong: it's an expert ensemble)
    pf_px = safe_float(pf_r.get("pfAiPrice") or pf_r.get("modelPrice") or 0)
    if pf_px > 1.0:
        signals.append(1 / pf_px)
        weights.append(4.5)

    # Our composite rating (0-100%)
    rat_pct = rating.get("pct", 50) / 100 if rating else 0.5
    # Convert to approximate win probability using logistic-like scaling
    rat_prob = max(0.01, min(0.95, (rat_pct ** 1.5) * 0.4))
    signals.append(rat_prob)
    weights.append(1.5)

    # Career win%
    cw = safe_float(runner.get("winPct", 0)) / 100
    if cw > 0:
        signals.append(cw)
        weights.append(2.0)

    # Track win%
    tr = _win_rate(runner.get("trackRecord") or {})
    if tr is not None:
        signals.append(tr)
        weights.append(1.5)

    # Distance win%
    dr = _win_rate(runner.get("distanceRecord") or {})
    if dr is not None:
        signals.append(dr)
        weights.append(1.3)

    # J+T strike rate
    tj = runner.get("trainerJockeyA2E_Career") or {}
    tj_sr   = safe_float(tj.get("strikeRate", 0)) / 100
    tj_runs = safe_float(tj.get("runners", 0))
    if tj_runs >= 10 and tj_sr > 0:
        signals.append(tj_sr)
        weights.append(1.2)

    # Last-start bonus/penalty
    ls_pos = safe_float((runner.get("lastStart") or {}).get("finishingPosition", 99))
    if ls_pos == 1:
        # Last-start winner bonus
        signals.append(min(cw * 2.5 + 0.05, 0.5))
        weights.append(0.8)
    elif ls_pos >= 8:
        # Recent poor run penalty
        signals.append(max(cw * 0.5, 0.01))
        weights.append(0.5)

    if not signals:
        return 0.05  # Complete unknown

    total_w = sum(weights)
    prob    = sum(s * w for s, w in zip(signals, weights)) / total_w
    return min(max(round(prob, 5), 0.005), 0.95)


def normalise_field(runners: list, ratings: dict, pf_ratings: dict) -> dict:
    """Compute and normalise model probabilities across the field."""
    raw = {}
    for r in runners:
        hid = get_horse_id(r)
        raw[hid] = compute_model_prob(r, ratings.get(hid, {}), pf_ratings.get(hid, {}))
    total = sum(raw.values())
    if total <= 0: return raw
    return {k: round(v / total, 5) for k, v in raw.items()}


# ─── VALUE ASSESSMENT ────────────────────────────────────────────────────────
def assess_value(
    model_prob: float, true_mkt_pct: float, sp: float,
    rating_pct: float, tj_a2e: float,
    min_rating: int, min_edge: float, min_tj_a2e: float
) -> dict:
    """
    Three-gate value assessment:
    Gate 1: Model probability > de-vigged market probability
    Gate 2: Composite rating >= minimum
    Gate 3: T+J combination A2E >= minimum
    Gate 4: SP within acceptable range
    All four must pass for a bet recommendation.
    """
    mkt   = true_mkt_pct / 100
    edge  = model_prob - mkt
    edge_pct = round(edge * 100, 1)

    # Expected value (per unit staked)
    ev_unit = model_prob * (sp - 1) - (1 - model_prob)

    gates = {
        "edge":    edge > (min_edge / 100),
        "rating":  rating_pct >= min_rating,
        "tj":      tj_a2e >= min_tj_a2e,
        "odds":    st.session_state.min_odds <= sp <= st.session_state.max_odds,
    }
    bet = all(gates.values())

    reasons = []
    if not gates["edge"]:
        reasons.append(f"Model {round(model_prob*100,1)}% vs market {round(mkt*100,1)}% — edge {edge_pct}% below min {min_edge}%")
    if not gates["rating"]:
        reasons.append(f"Rating {rating_pct}% below minimum {min_rating}%")
    if not gates["tj"]:
        reasons.append(f"J+T A2E {round(tj_a2e,2)} below minimum {min_tj_a2e}")
    if not gates["odds"]:
        reasons.append(f"SP ${sp} outside range ${st.session_state.min_odds}–${st.session_state.max_odds}")

    return {
        "bet": bet, "gates": gates, "edge_pct": edge_pct,
        "model_pct": round(model_prob * 100, 1),
        "market_pct": round(mkt * 100, 1),
        "ev_unit": round(ev_unit, 3),
        "ev_pct":  round(ev_unit * 100, 1),
        "reasons": reasons,
    }


# ─── SPEEDMAP ────────────────────────────────────────────────────────────────
PACE_POSITIONS = {1: "Leader", 2: "On Pace", 3: "Midfield", 4: "Back", 5: "Rear"}
PACE_COLORS    = {
    "Leader":   "var(--red)",
    "On Pace":  "var(--amber)",
    "Midfield": "var(--blue-mid)",
    "Back":     "var(--text4)",
    "Rear":     "var(--text4)",
}

def assign_pace_positions(runners: list) -> list:
    """Assign pace positions if not already set by the API."""
    for r in runners:
        if not r.get("pacePosition"):
            b = safe_float(r.get("barrierNumber") or r.get("barrier") or 8)
            r["pacePosition"] = 1 if b <= 3 else 2 if b <= 6 else 3 if b <= 10 else 4
    return runners

def classify_tempo(runners: list) -> dict:
    leaders = [r for r in runners if safe_int(r.get("pacePosition", 3)) == 1]
    on_pace = [r for r in runners if safe_int(r.get("pacePosition", 3)) == 2]
    n = len(leaders)
    if n >= 3:
        return {"tempo": "HOT",      "pill": "pill-red",
                "desc": "Multiple leaders — burn-up likely. Strongly favours closers and backmarkers.",
                "strategy": "Back midfield-to-rear runners with closing ability. Avoid front-runners."}
    elif n == 2:
        return {"tempo": "GENUINE",  "pill": "pill-amber",
                "desc": "Two leaders — honest, genuine tempo. All running styles viable.",
                "strategy": "Most styles competitive. Slight lean toward on-pace runners."}
    elif n == 1 and len(on_pace) <= 1:
        return {"tempo": "SOFT",     "pill": "pill-blue",
                "desc": "Single uncontested leader — front-runner has a significant advantage.",
                "strategy": "Favour the leader. Second-preference: nearest pursuer with barrier ≤ 5."}
    else:
        return {"tempo": "MODERATE", "pill": "pill-muted",
                "desc": "Balanced dynamics — no dominant pace factor.",
                "strategy": "No pace bias. Rate on ability and class."}


# ─── STAKING ─────────────────────────────────────────────────────────────────
def kelly_criterion(bank: float, prob: float, odds: float, fraction: float) -> float:
    """Full Kelly formula, applied at the user-specified fraction."""
    b = odds - 1
    if b <= 0 or prob <= 0 or prob >= 1: return 0.0
    f_star = (b * prob - (1 - prob)) / b
    return bank * fraction * max(f_star, 0)

def compute_stake(bank, model_prob, sp, method, kf, flat_pct, level_amt, max_pct) -> dict:
    """Compute recommended stake and expected value metrics."""
    edge = model_prob - (1 / sp if sp > 1 else 0)

    if method == "Quarter Kelly":
        stake = kelly_criterion(bank, model_prob, sp, 0.25)
    elif method == "Half Kelly":
        stake = kelly_criterion(bank, model_prob, sp, 0.50)
    elif method == "Full Kelly":
        stake = kelly_criterion(bank, model_prob, sp, 1.0)
    elif method == "Flat %":
        stake = bank * flat_pct / 100 if edge > 0 else 0
    elif method == "Level":
        stake = level_amt if edge > 0 else 0
    else:
        stake = 0

    stake = min(round(stake, 2), round(bank * max_pct / 100, 2))
    if stake <= 0: return {"stake": 0, "ev": 0, "ev_pct": 0, "pct_bank": 0, "roi_required": 0}

    ev     = round((model_prob * (sp - 1) - (1 - model_prob)) * stake, 2)
    ev_pct = round(ev / stake * 100, 1) if stake else 0
    roi_req= round((1 / model_prob - 1) * 100, 1)  # break-even ROI needed

    return {
        "stake":       stake,
        "ev":          ev,
        "ev_pct":      ev_pct,
        "pct_bank":    round(stake / bank * 100, 1) if bank else 0,
        "roi_required": roi_req,
    }


# ─── BET LOG ─────────────────────────────────────────────────────────────────
def add_bet(horse, race, stake, odds, edge_pct, model_pct):
    st.session_state.bet_log.append({
        "dt":       datetime.now().strftime("%d/%m %H:%M"),
        "horse":    horse, "race": race,
        "stake":    round(stake, 2), "odds": odds,
        "edge":     edge_pct, "model_pct": model_pct,
        "result":   "Pending", "pl": 0.0,
    })

def settle(idx, result):
    b  = st.session_state.bet_log[idx]
    pl = b["stake"] * (b["odds"] - 1) if result == "Won" else -b["stake"]
    st.session_state.bet_log[idx].update({"result": result, "pl": round(pl, 2)})
    st.session_state.bank = round(st.session_state.bank + pl, 2)

def bankroll_stats() -> dict:
    settled = [b for b in st.session_state.bet_log if b["result"] != "Pending"]
    if not settled: return {}
    staked   = sum(b["stake"] for b in settled)
    pl       = sum(b["pl"]    for b in settled)
    winners  = [b for b in settled if b["result"] == "Won"]
    run = peak = 0; dds = []
    for b in settled:
        run += b["pl"]; peak = max(peak, run); dds.append(run - peak)
    odds_all = [b["odds"] for b in settled]
    return {
        "n":       len(settled),
        "winners": len(winners),
        "sr":      round(len(winners) / len(settled) * 100, 1),
        "staked":  round(staked, 2),
        "pl":      round(pl, 2),
        "roi":     round(pl / staked * 100, 1) if staked else 0,
        "avg_odds":round(sum(odds_all) / len(odds_all), 2),
        "max_dd":  round(min(dds), 2),
        "bank":    round(st.session_state.bank, 2),
        "peak":    round(st.session_state.starting_bank + peak, 2),
    }


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
      <div class="sb-logo">Racing Edge</div>
      <div class="sb-sub">PUNTINGFORM API v2  ·  PROFESSIONAL</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-sec">API Connection</div>', unsafe_allow_html=True)
    try:    secret_key = st.secrets.get("PUNTINGFORM_API_KEY", "")
    except: secret_key = ""
    api_key = st.text_input("API Key", type="password",
        value=st.session_state.api_key or secret_key,
        placeholder="Paste PuntingForm API key...")
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key
        st.session_state.races   = []

    if st.session_state.api_key:
        st.markdown('<div style="font-size:.7rem;color:var(--green);font-family:\'JetBrains Mono\',monospace">Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:.7rem;color:var(--red);font-family:\'JetBrains Mono\',monospace">No key — enter key above</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-sec">Race Selection</div>', unsafe_allow_html=True)
    race_date    = st.date_input("Date", value=date.today() + timedelta(days=1))
    state_filter = st.multiselect("States", ["QLD","NSW","VIC","SA","WA","TAS","NT","ACT"])
    race_type    = st.selectbox("Race Type", ["All", "Thoroughbred", "Harness", "Greyhound"])

    if st.button("Fetch Meetings", use_container_width=True):
        if not st.session_state.api_key:
            st.error("Enter API key first.")
        else:
            with st.spinner(f"Fetching {pf_date(race_date)}..."):
                st.session_state.races = fetch_meetings(race_date)
            n = len(st.session_state.races)
            st.success(f"{n} meeting{'s' if n!=1 else ''} found") if n else st.warning("No meetings found")

    st.markdown('<div class="sb-sec">Staking</div>', unsafe_allow_html=True)
    st.session_state.bank = st.number_input("Bankroll ($)", value=float(st.session_state.bank), step=50.0, min_value=1.0)
    if st.session_state.starting_bank == 1000.0 and st.session_state.bank != 1000.0:
        st.session_state.starting_bank = st.session_state.bank

    st.session_state.staking_method = st.selectbox(
        "Method", ["Quarter Kelly","Half Kelly","Full Kelly","Flat %","Level"],
        index=["Quarter Kelly","Half Kelly","Full Kelly","Flat %","Level"].index(st.session_state.staking_method)
    )
    if "Kelly" in st.session_state.staking_method:
        st.caption("Kelly fraction applied automatically by method")
    elif st.session_state.staking_method == "Flat %":
        st.session_state.flat_pct = st.slider("% of Bank", 0.5, 10.0, st.session_state.flat_pct, 0.5)
    else:
        st.session_state.level_stake = st.number_input("Fixed Stake ($)", value=st.session_state.level_stake, step=5.0)

    st.session_state.max_stake_pct = st.slider("Max Stake % of Bank", 1.0, 20.0, st.session_state.max_stake_pct, 0.5)

    st.markdown('<div class="sb-sec">Bet Filters</div>', unsafe_allow_html=True)
    st.session_state.min_odds   = st.number_input("Min Odds",    value=st.session_state.min_odds,   step=0.5, min_value=1.01)
    st.session_state.max_odds   = st.number_input("Max Odds",    value=st.session_state.max_odds,   step=5.0)
    st.session_state.min_rating = st.slider("Min Rating %",  0, 100, st.session_state.min_rating)
    st.session_state.min_edge   = st.slider("Min Edge %",    0.0, 20.0, st.session_state.min_edge, 0.5)
    st.session_state.min_tj_a2e = st.slider("Min J+T A2E", 0.0, 2.5, st.session_state.min_tj_a2e, 0.1)

    # Bankroll snapshot
    if st.session_state.bet_log:
        bpct = st.session_state.bank / st.session_state.starting_bank * 100
        col_a, col_b = st.columns(2)
        col_a.metric("Bank", f"${st.session_state.bank:.0f}")
        col_b.metric("vs Start", f"{bpct-100:+.1f}%")


# ─── TABS ─────────────────────────────────────────────────────────────────────
TAB_RACES, TAB_ANALYSIS, TAB_STAKING, TAB_BANKROLL, TAB_GUIDE = st.tabs([
    "Meetings & Races", "Race Analysis", "Staking & Bets", "Bankroll", "Guide"
])


# ════════════════════════════════════════════════════════════════
# TAB 1: MEETINGS & RACES
# ════════════════════════════════════════════════════════════════
with TAB_RACES:
    st.markdown("""
    <div class="page-hdr">
      <div>
        <div class="page-title">Meetings & Races</div>
        <div class="page-sub">Select a race to load its field for analysis</div>
      </div>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.api_key:
        st.markdown('<div class="alert alert-amber">Enter your PuntingForm API key in the sidebar to begin.</div>', unsafe_allow_html=True)
    elif not st.session_state.races:
        st.markdown('<div class="alert alert-blue">Click "Fetch Meetings" in the sidebar to load today\'s race card.</div>', unsafe_allow_html=True)

    # API debug panel
    if st.session_state.get("_debug_raw"):
        with st.expander("API Debug — raw response (diagnose field names if runners not loading)"):
            st.markdown('<div class="debug-box">Shows raw PuntingForm API response. If meetings load but races are empty, check the field names below and compare to fetch_meetings() in the code.</div>', unsafe_allow_html=True)
            raw = st.session_state["_debug_raw"]
            meetings_list = extract_payload(raw)
            if meetings_list:
                first = meetings_list[0]
                st.write("**First meeting — all keys:**", list(first.keys()))
                st.write("**Date format used:**", pf_date(race_date), "(should be d-MMM-yyyy)")
                st.write("**Last API call:**", st.session_state.get("_last_api_call", "—"))
            with st.expander("Full raw JSON"):
                st.json(raw)

    if st.session_state.races:
        for meeting in st.session_state.races:
            name   = meeting.get("_name", "Unknown")
            state  = meeting.get("_state", "")
            races  = meeting.get("races", [])
            m_type = (meeting.get("track") or {}).get("raceType") or meeting.get("raceType") or "Thoroughbred"

            # Apply filters
            if state_filter and state.upper() not in [s.upper() for s in state_filter]: continue
            if race_type != "All" and race_type.lower() not in m_type.lower(): continue

            n_races = len([r for r in races if r.get("raceName") or r.get("raceNumber")])
            cond = meeting.get("trackCondition") or meeting.get("going") or ""
            rail = meeting.get("railPosition") or ""

            with st.expander(f"{name}  —  {state}  —  {n_races} races  {'·  ' + cond if cond else ''}  {'  Rail: ' + rail if rail else ''}"):
                if not races:
                    st.markdown('<div class="alert alert-amber">No races found. API may use a different field name — check API Debug panel.</div>', unsafe_allow_html=True)

                for race in races:
                    rnum   = race.get("raceNumber") or race.get("number") or "?"
                    rname  = race.get("raceName")   or race.get("name")   or f"Race {rnum}"
                    rdist  = race.get("raceDistance") or race.get("distance") or "?"
                    rtime  = race.get("startTime")   or race.get("raceTime") or ""
                    rcls   = race.get("raceClass")   or race.get("class")    or ""
                    rcond  = race.get("trackCondition") or cond or ""
                    rprize = race.get("prizeMoney")  or race.get("prize")    or 0
                    rid    = get_race_id(race)

                    # Format time nicely
                    time_str = ""
                    if rtime:
                        try:
                            t = str(rtime)
                            if "T" in t: t = t.split("T")[1][:5]
                            time_str = t[:5]
                        except: time_str = str(rtime)[:5]

                    c1, c2 = st.columns([8, 1])
                    with c1:
                        prize_str = f"  ·  ${int(rprize):,}" if rprize and safe_float(rprize) > 0 else ""
                        rid_badge = "" if rid else '  <span class="pill pill-amber" style="font-size:.58rem">No raceId</span>'
                        st.markdown(
                            f'<div class="race-row">'
                            f'<div class="race-num">R{rnum}</div>'
                            f'<div class="race-info">'
                            f'  <div class="race-name">{rname}</div>'
                            f'  <div class="race-meta">{time_str}  ·  {rdist}m  ·  {rcls}  ·  {rcond}{prize_str}{rid_badge}</div>'
                            f'</div>'
                            f'<div class="race-badges">'
                            f'{"<span class=\'pill pill-muted\' style=\'font-size:.62rem\'>" + str(rdist) + "m</span>" if rdist else ""}'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )
                    with c2:
                        btn_key = f"load_{name}_{rnum}_{rid}"
                        if st.button("Load", key=btn_key, use_container_width=True):
                            st.session_state.selected_race   = race
                            st.session_state.runners         = []
                            st.session_state.ratings         = {}
                            st.session_state.pf_ratings      = {}
                            st.session_state.sectionals      = {}
                            st.session_state.past_form_by_horse = {}

                            with st.spinner(f"Loading R{rnum} {name}..."):
                                runners = fetch_race_field(race)
                                if runners:
                                    st.session_state.runners = assign_pace_positions(runners)
                                    st.success(f"{len(runners)} runners loaded — go to Race Analysis tab")
                                else:
                                    st.error(f"No runners found. Check API Debug panel. Date used: {race.get('_meetingDate')}, Track: {name}, Race#: {rnum}")


# ════════════════════════════════════════════════════════════════
# TAB 2: RACE ANALYSIS
# ════════════════════════════════════════════════════════════════
with TAB_ANALYSIS:
    race    = st.session_state.selected_race
    runners = st.session_state.runners

    if not race:
        st.markdown('<div class="alert alert-blue">Select a race from the Meetings tab.</div>', unsafe_allow_html=True)
        st.stop()
    if not runners:
        st.markdown('<div class="alert alert-amber">No runners loaded. Click Load on a race in the Meetings tab.</div>', unsafe_allow_html=True)
        st.stop()

    # ── Race header ──────────────────────────────────────────────
    rname  = race.get("raceName") or race.get("name") or "Race"
    rdist  = race.get("raceDistance") or race.get("distance") or "?"
    rtrk   = race.get("_meetingName") or race.get("meetingName") or ""
    rcond  = race.get("trackCondition") or race.get("going") or ""
    rcls   = race.get("raceClass") or ""
    rnum   = race.get("raceNumber") or race.get("number") or "?"
    rid    = get_race_id(race)
    rds    = race.get("_meetingDate", "")
    rprize = race.get("prizeMoney") or race.get("prize") or 0
    rail   = race.get("railPosition") or ""

    st.markdown(f"""
    <div class="page-hdr">
      <div>
        <div class="page-title">Race {rnum} — {rname}</div>
        <div class="page-sub">{rtrk}  ·  {rdist}m  ·  {rcls}  ·  {rcond or "Condition TBC"}  ·  {rds}
        {"  ·  Rail: " + rail if rail else ""}
        {"  ·  $" + f"{int(rprize):,}" if rprize and safe_float(rprize) > 0 else ""}
        {"  ·  raceId " + rid if rid else "  ·  No raceId"}
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Control buttons ──────────────────────────────────────────
    col_rate, col_info = st.columns([2, 5])
    with col_rate:
        run_ratings = st.button("Run Full Analysis", use_container_width=True)
    with col_info:
        st.markdown(
            '<div style="padding-top:8px;font-size:.78rem;color:var(--text3)">'
            'Fetches past form, PF AI ratings, and sectional data. '
            'Then rates all runners across 11 factors and frames the market.</div>',
            unsafe_allow_html=True
        )

    if run_ratings:
        ratings_new = {}; pf_new = {}; secs_new = {}; past_by_hid = {}
        prog = st.progress(0); status = st.empty()

        # Step 1: Past form for the race
        status.markdown('<div class="alert alert-blue">Fetching past form data (form/form)...</div>', unsafe_allow_html=True)
        past_rows = fetch_form_for_race(race)
        for row in past_rows:
            hid = get_horse_id(row)
            if hid: past_by_hid.setdefault(hid, []).append(row)
        prog.progress(0.25)

        # Step 2: PF AI ratings
        status.markdown('<div class="alert alert-blue">Fetching PF AI ratings...</div>', unsafe_allow_html=True)
        pf_new = fetch_pf_ratings(race)
        prog.progress(0.45)

        # Step 3: Sectional benchmarks
        status.markdown('<div class="alert alert-blue">Fetching sectional benchmarks...</div>', unsafe_allow_html=True)
        secs_new = fetch_sectionals(race)
        prog.progress(0.60)

        # Step 4: Classify tempo
        tempo_info = classify_tempo(runners)
        tempo_str  = tempo_info["tempo"]

        # Step 5: Rate each runner
        status.markdown('<div class="alert alert-blue">Computing ratings...</div>', unsafe_allow_html=True)
        for i, runner in enumerate(runners):
            hid = get_horse_id(runner)
            past_h = past_by_hid.get(hid, [])
            ratings_new[hid or f"_idx{i}"] = rate_runner(runner, past_h, secs_new, tempo_str)
            prog.progress(0.60 + 0.40 * (i + 1) / len(runners))

        st.session_state.ratings         = ratings_new
        st.session_state.pf_ratings      = pf_new
        st.session_state.sectionals      = secs_new
        st.session_state.past_form_by_horse = past_by_hid
        prog.empty(); status.empty()

        n_pf  = len(pf_new)
        n_sec = len(secs_new)
        n_frm = len(past_by_hid)
        msgs  = [f"Rated {len(runners)} runners"]
        if n_frm:  msgs.append(f"{n_frm} with past form")
        if n_pf:   msgs.append(f"{n_pf} PF AI ratings")
        if n_sec:  msgs.append(f"{n_sec} sectional records")
        if not n_pf:  msgs.append("PF AI ratings unavailable (check subscription tier)")
        if not n_sec: msgs.append("Sectionals unavailable")
        st.success("  ·  ".join(msgs))

    ratings    = st.session_state.ratings
    pf_ratings = st.session_state.pf_ratings
    secs       = st.session_state.sectionals
    past_all   = st.session_state.past_form_by_horse
    mkt        = frame_market(runners)
    tempo_info = classify_tempo(runners)
    field_probs= normalise_field(runners, ratings, pf_ratings) if ratings else {}

    # ════ SPEEDMAP ════════════════════════════════════════════════
    st.markdown('<div class="section-hdr">Speedmap & Tempo Analysis</div>', unsafe_allow_html=True)

    # Tempo banner
    st.markdown(
        f'<div class="card-blue" style="display:flex;align-items:center;gap:14px;margin-bottom:14px">'
        f'<span class="pill {tempo_info["pill"]}" style="font-size:.7rem;padding:3px 12px">'
        f'{tempo_info["tempo"]} PACE</span>'
        f'<div><div style="font-size:.84rem;color:var(--text2);font-weight:500">{tempo_info["desc"]}</div>'
        f'<div style="font-size:.76rem;color:var(--text3);margin-top:3px">'
        f'Strategy: {tempo_info["strategy"]}</div></div></div>',
        unsafe_allow_html=True
    )

    # Pace position grid
    positions = {1: [], 2: [], 3: [], 4: [], 5: []}
    for r in runners:
        pp = safe_int(r.get("pacePosition", 3))
        positions[min(max(pp, 1), 5)].append(
            r.get("name") or r.get("runnerName") or r.get("horseName") or "?"
        )
    for pp, lbl in PACE_POSITIONS.items():
        horses = positions.get(pp, [])
        if not horses: continue
        color = PACE_COLORS.get(lbl, "var(--text3)")
        st.markdown(
            f'<div class="smap-row">'
            f'<div class="smap-pos" style="color:{color}">{lbl}</div>'
            f'<div class="smap-horses">{" &nbsp;·&nbsp; ".join(horses)}</div>'
            f'<div class="smap-cnt">{len(horses)}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown('<hr>', unsafe_allow_html=True)

    # ════ MARKET FRAME ════════════════════════════════════════════
    st.markdown('<div class="section-hdr">Market Frame — De-vigged True Probabilities</div>', unsafe_allow_html=True)

    if not mkt:
        st.markdown('<div class="alert alert-amber">No SP prices available — market frame cannot be computed. Prices are published closer to race time.</div>', unsafe_allow_html=True)
    else:
        sample = next(iter(mkt.values()))
        overround = sample["overround"]

        # Explanation box
        st.markdown(
            f'<div class="card-blue" style="font-size:.8rem;color:var(--blue-dark);margin-bottom:14px">'
            f'<strong>Book overround: {overround}%</strong>  —  '
            f'Raw% = 1/SP (includes bookmaker vig)  ·  '
            f'True% = de-vigged actual market probability (Raw% / {overround}%)  ·  '
            f'Fair Odds = 1/True%  ·  '
            f'Edge = Model% minus True%  ·  '
            f'A $6.00 favourite in a {overround}% book has True% = '
            f'{round(100/6/overround*100, 1)}%, not 16.7%'
            f'</div>',
            unsafe_allow_html=True
        )

        sorted_by_sp = sorted(runners, key=lambda x: safe_float(x.get("priceSP") or x.get("fixedOddsWin") or 99))
        rows = ""
        for rank, r in enumerate(sorted_by_sp):
            hid  = get_horse_id(r)
            mf   = mkt.get(hid)
            if not mf: continue
            name = r.get("name") or r.get("runnerName") or r.get("horseName") or "?"
            sp   = mf["sp"]; raw = mf["raw_pct"]; true = mf["true_pct"]; fair = mf["fair_odds"]
            mp   = field_probs.get(hid, 0)
            pfr  = pf_ratings.get(hid, {})
            pf_px= safe_float(pfr.get("pfAiPrice") or pfr.get("modelPrice") or 0)
            diff = round(mp * 100 - true, 1) if mp else None
            is_val = diff is not None and diff > 0

            edge_html = "—"
            if diff is not None:
                cls = "edge-pos" if diff > 0 else "edge-neg" if diff < 0 else "edge-neu"
                edge_html = f'<span class="{cls}">{("+" if diff >= 0 else "")}{diff}%</span>'

            # Probability bar
            bar_w = min(int(true * 3.5), 100)
            bar_c = "#16a34a" if is_val else "#3b82f6"
            bar_html = f'<div class="prob-bar" style="width:60px"><div class="prob-fill" style="width:{bar_w}%;background:{bar_c}"></div></div>'

            # Badges
            badges = ""
            if rank == 0:         badges += '<span class="mkt-fav">Fav</span>'
            if is_val:            badges += '<span class="mkt-val">Value</span>'

            pf_cell = f"${pf_px:.2f}" if pf_px > 1 else "—"
            mp_cell = f"{mp*100:.1f}%" if mp else "—"

            row_cls = "val-row" if is_val else ("fav-row" if rank == 0 else "")
            rows += f"""
            <tr class="{row_cls}">
              <td style="color:var(--text4);width:20px;font-size:.72rem">{rank+1}</td>
              <td><span class="mkt-horse">{name}</span>{badges}</td>
              <td style="color:var(--blue);font-weight:700">${sp:.2f}</td>
              <td style="color:var(--text3)">{raw}%</td>
              <td>
                <div style="display:flex;align-items:center;gap:7px">
                  <span style="font-weight:600">{true}%</span>{bar_html}
                </div>
              </td>
              <td style="color:var(--text2)">${fair:.2f}</td>
              <td style="color:var(--blue)">{pf_cell}</td>
              <td style="color:var(--blue-mid)">{mp_cell}</td>
              <td>{edge_html}</td>
            </tr>"""

        st.markdown(
            f'<div class="card" style="padding:0;overflow:hidden">'
            f'<table class="mkt-table">'
            f'<thead><tr>'
            f'<th>#</th><th>Horse</th><th>SP Odds</th>'
            f'<th>Raw%<br><span style="font-weight:400;opacity:.7">incl.vig</span></th>'
            f'<th>True%<br><span style="font-weight:400;opacity:.7">de-vigged</span></th>'
            f'<th>Fair Odds<br><span style="font-weight:400;opacity:.7">no margin</span></th>'
            f'<th>PF AI<br><span style="font-weight:400;opacity:.7">model price</span></th>'
            f'<th>Model%<br><span style="font-weight:400;opacity:.7">our estimate</span></th>'
            f'<th>Edge<br><span style="font-weight:400;opacity:.7">model&minus;market</span></th>'
            f'</tr></thead>'
            f'<tbody>{rows}</tbody>'
            f'</table></div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:.65rem;color:var(--text4);margin-top:6px;margin-bottom:16px">'
            f'Overround: {overround}%  ·  True% = Raw% / {overround}%  ·  '
            f'Green rows = model finds positive edge vs de-vigged market</div>',
            unsafe_allow_html=True
        )

    st.markdown('<hr>', unsafe_allow_html=True)

    # ════ PER-RUNNER CARDS ════════════════════════════════════════
    st.markdown('<div class="section-hdr">Runner-by-Runner Analysis</div>', unsafe_allow_html=True)

    def sort_key(r):
        hid = get_horse_id(r)
        return field_probs.get(hid, 0) if field_probs else -safe_float(r.get("priceSP") or 99)

    for rank, runner in enumerate(sorted(runners, key=sort_key, reverse=True), 1):
        hid     = get_horse_id(runner)
        name    = runner.get("name") or runner.get("runnerName") or runner.get("horseName") or "Unknown"
        barrier = runner.get("barrierNumber") or runner.get("barrier") or "?"
        jockey  = (runner.get("jockey") or {}).get("fullName") or runner.get("jockeyName") or "—"
        trainer = (runner.get("trainer") or {}).get("fullName") or runner.get("trainerName") or "—"
        weight  = runner.get("weightTotal") or runner.get("weightCarried") or runner.get("handicapWeight") or "—"
        age     = runner.get("age") or runner.get("horseAge") or ""
        sex     = runner.get("sex") or runner.get("horseSex") or ""
        colour  = runner.get("colour") or runner.get("horseColour") or ""
        country = runner.get("country") or runner.get("horseCountry") or ""
        price   = safe_float(runner.get("priceSP") or runner.get("fixedOddsWin") or runner.get("price") or 0)
        pace_lbl= PACE_POSITIONS.get(safe_int(runner.get("pacePosition", 3)), "Midfield")
        rating  = ratings.get(hid)
        pfr     = pf_ratings.get(hid, {})
        sec_d   = secs.get(hid, {})
        mf      = mkt.get(hid, {})
        mp      = field_probs.get(hid, 0)
        past    = past_all.get(hid, [])
        tj      = runner.get("trainerJockeyA2E_Career") or {}
        tj_a2e  = safe_float(tj.get("a2E", 0))
        tj_sr   = safe_float(tj.get("strikeRate", 0))
        tj_runs = safe_float(tj.get("runners", 0))

        # Value assessment
        verdict = None
        if rating and mf and mp:
            verdict = assess_value(
                mp, mf["true_pct"], price,
                rating["pct"], tj_a2e,
                st.session_state.min_rating,
                st.session_state.min_edge,
                st.session_state.min_tj_a2e,
            )

        # Expander label
        sp_str   = f"${price:.2f}" if price > 0 else "N/A"
        mp_str   = f"  Model {round(mp*100,1)}%" if mp else ""
        mkt_str  = f"  Mkt {mf.get('true_pct','?')}%" if mf else ""
        edge_str = ""
        if verdict: edge_str = f"  Edge {'+' if verdict['edge_pct']>=0 else ''}{verdict['edge_pct']}%"
        bet_flag = "  [BET]" if (verdict and verdict["bet"]) else ""
        exp_label = f"#{rank}  {name}   B{barrier}   {sp_str}{mp_str}{mkt_str}{edge_str}{bet_flag}"

        is_expanded = rank <= 2 or (verdict is not None and verdict["bet"])

        with st.expander(exp_label, expanded=is_expanded):
            # Two-column layout
            col_left, col_right = st.columns([3, 2], gap="medium")

            # ─ LEFT COLUMN ─────────────────────────────────────────
            with col_left:
                # Metadata pills
                pace_color_pill = {
                    "Leader":"pill-red","On Pace":"pill-amber","Midfield":"pill-blue",
                    "Back":"pill-muted","Rear":"pill-muted"
                }.get(pace_lbl, "pill-muted")
                meta_line = f'<div style="display:flex;gap:5px;flex-wrap:wrap;margin-bottom:12px">'
                meta_line += f'<span class="pill pill-muted">B{barrier}</span>'
                meta_line += f'<span class="pill {pace_color_pill}">{pace_lbl}</span>'
                if weight and str(weight) != "—": meta_line += f'<span class="pill pill-muted">{weight}kg</span>'
                if age:     meta_line += f'<span class="pill pill-muted">{age}yo</span>'
                if sex:     meta_line += f'<span class="pill pill-muted">{sex}</span>'
                if country and country.upper() not in ("AUS","AU"): meta_line += f'<span class="pill pill-amber">{country}</span>'
                meta_line += "</div>"
                st.markdown(meta_line, unsafe_allow_html=True)

                # Jockey / Trainer
                st.markdown(
                    f'<div style="font-size:.8rem;color:var(--text2);line-height:2.0;margin-bottom:12px">'
                    f'<span style="color:var(--text4);font-size:.66rem;text-transform:uppercase;letter-spacing:.06em;font-weight:600">Jockey</span>'
                    f'&nbsp;&nbsp;<span style="font-weight:500">{jockey}</span><br>'
                    f'<span style="color:var(--text4);font-size:.66rem;text-transform:uppercase;letter-spacing:.06em;font-weight:600">Trainer</span>'
                    f'&nbsp;&nbsp;<span style="font-weight:500">{trainer}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Career stats
                cw  = safe_float(runner.get("winPct",   0))
                cp  = safe_float(runner.get("placePct", 0))
                tr2 = runner.get("trackRecord")    or {}
                dr  = runner.get("distanceRecord") or {}
                ts  = safe_float(tr2.get("starts",0)); tw = safe_float(tr2.get("firsts",0))
                ts2 = safe_float(tr2.get("seconds",0)); tt = safe_float(tr2.get("thirds",0))
                ds2 = safe_float(dr.get("starts",0));  dw = safe_float(dr.get("firsts",0))
                ds3 = safe_float(dr.get("seconds",0)); dt = safe_float(dr.get("thirds",0))
                tsr = round(tw/ts*100,1) if ts>0 else 0
                tplr= round((tw+ts2+tt)/ts*100,1) if ts>0 else 0
                dsr = round(dw/ds2*100,1) if ds2>0 else 0
                dplr= round((dw+ds3+dt)/ds2*100,1) if ds2>0 else 0

                st.markdown('<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:12px">' +
                    f'<div class="card-sm"><div class="dl-label">Career Win%</div><div class="dl-value {"green" if cw>20 else ""}">{cw:.1f}%</div></div>' +
                    f'<div class="card-sm"><div class="dl-label">Career Place%</div><div class="dl-value">{cp:.1f}%</div></div>' +
                    f'<div class="card-sm"><div class="dl-label">Track {int(tw)}-{int(ts2)}-{int(tt)}/{int(ts)}</div><div class="dl-value {"green" if tsr>20 else ""}">{tsr}% win  {tplr}% place</div></div>' +
                    f'<div class="card-sm"><div class="dl-label">Distance {int(dw)}-{int(ds3)}-{int(dt)}/{int(ds2)}</div><div class="dl-value {"green" if dsr>20 else ""}">{dsr}% win  {dplr}% place</div></div>' +
                    '</div>', unsafe_allow_html=True)

                # J+T Combo
                if tj_runs >= 5:
                    a2e_col = "green" if tj_a2e >= 1.1 else "red" if tj_a2e < 0.8 else ""
                    st.markdown(
                        f'<div class="card-sm" style="margin-bottom:12px">'
                        f'<div class="dl-label" style="margin-bottom:6px">Jockey + Trainer — {int(tj_runs)} runs together</div>'
                        f'<div style="display:flex;gap:20px;font-family:\'JetBrains Mono\',monospace;font-size:.82rem">'
                        f'<div>Win SR &nbsp;<span style="font-weight:600">{tj_sr:.1f}%</span></div>'
                        f'<div>A2E &nbsp;<span class="dl-value {a2e_col}" style="font-size:.88rem">{tj_a2e:.2f}</span></div>'
                        f'</div>'
                        f'<div style="font-size:.7rem;color:var(--text4);margin-top:3px">A2E >1.0 = above expectation vs starting price</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                # PF AI rating
                pf_px   = safe_float(pfr.get("pfAiPrice") or pfr.get("modelPrice") or 0)
                pf_rank = pfr.get("pfAiRank") or pfr.get("rank") or pfr.get("aiRank")
                pf_score= safe_float(pfr.get("pfAiScore") or pfr.get("aiScore") or 0)
                if pf_px > 1 or pf_rank:
                    pf_val = price > 0 and pf_px > price
                    pf_c = "green" if pf_val else ""
                    st.markdown(
                        f'<div class="card-blue" style="margin-bottom:12px">'
                        f'<div class="dl-label" style="margin-bottom:6px;color:var(--blue-dark)">PF AI Model Rating</div>'
                        f'<div style="display:flex;gap:20px;flex-wrap:wrap">'
                        + (f'<div><div class="dl-label">AI Price</div><div class="dl-value blue" style="font-size:1.1rem">${pf_px:.2f}</div></div>' if pf_px>1 else "")
                        + (f'<div><div class="dl-label">AI Rank</div><div class="dl-value blue">#{pf_rank}</div></div>' if pf_rank else "")
                        + (f'<div><div class="dl-label">AI Score</div><div class="dl-value blue">{pf_score:.1f}</div></div>' if pf_score>0 else "")
                        + f'</div>'
                        + (f'<div style="font-size:.72rem;color:var(--green);margin-top:5px;font-weight:600">PF AI model price longer than SP — value signal</div>' if pf_val else "")
                        + f'</div>',
                        unsafe_allow_html=True
                    )

                # Sectional data
                sec_rtg = safe_float(sec_d.get("sectionalRating") or sec_d.get("closing600Rating") or 0)
                sec_600 = safe_float(sec_d.get("averageClosing600") or sec_d.get("avg600") or 0)
                if sec_rtg > 0 or sec_600 > 0:
                    st.markdown(
                        f'<div class="card-sm" style="margin-bottom:12px">'
                        f'<div class="dl-label" style="margin-bottom:6px">Sectional Data</div>'
                        f'<div style="display:flex;gap:20px;font-family:\'JetBrains Mono\',monospace;font-size:.82rem">'
                        + (f'<div>Sec Rating &nbsp;<span style="color:var(--blue);font-weight:600">{sec_rtg:.1f}</span></div>' if sec_rtg>0 else "")
                        + (f'<div>Avg 600m &nbsp;<span style="color:var(--blue);font-weight:600">{sec_600:.2f}s</span></div>' if sec_600>0 else "")
                        + f'</div></div>',
                        unsafe_allow_html=True
                    )

                # Composite rating bar
                if rating:
                    r_pct = rating["pct"]
                    r_col = "var(--green)" if r_pct >= 65 else "var(--amber)" if r_pct >= 45 else "var(--red)"
                    st.markdown(
                        f'<div class="dl-label" style="margin-bottom:5px">Composite Rating</div>'
                        f'<div style="display:flex;align-items:baseline;gap:8px;margin-bottom:6px">'
                        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:1.7rem;font-weight:700;color:{r_col}">{rating["composite"]}</span>'
                        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:.72rem;color:var(--text4)">/ {MAX_SCORE}  ({r_pct}%)</span>'
                        f'</div>'
                        f'<div class="prob-bar" style="margin-bottom:14px">'
                        f'<div class="prob-fill" style="width:{r_pct}%;background:{r_col}"></div></div>',
                        unsafe_allow_html=True
                    )

                    # Factor breakdown bars
                    for fkey, fmax in FACTOR_WEIGHTS.items():
                        val  = rating.get(fkey, 0)
                        pct  = int(val / fmax * 100) if fmax else 0
                        bc   = "#3b82f6" if pct >= 65 else "#d97706" if pct >= 35 else "#dc2626"
                        st.markdown(
                            f'<div class="comp-row">'
                            f'<span class="comp-name">{FACTOR_LBLS[fkey]}</span>'
                            f'<div class="comp-bar"><div class="comp-fill" style="width:{pct}%;background:{bc}"></div></div>'
                            f'<span class="comp-score">{val:.1f}/{fmax}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                # Recent form last 5 runs
                if past:
                    st.markdown('<div class="dl-label" style="margin-top:14px;margin-bottom:6px">Recent Form</div>', unsafe_allow_html=True)
                    form_html = '<div style="display:flex;gap:5px;flex-wrap:wrap">'
                    for run in past[:6]:
                        pos  = safe_int(run.get("finishingPosition", 0))
                        trk  = (run.get("meetingName") or "")[:3].upper()
                        dst  = safe_int(run.get("raceDistance") or 0)
                        cls  = safe_int(run.get("raceClass") or 0)
                        margin = safe_float(run.get("marginBeaten") or 0)
                        sp_r = safe_float(run.get("startingPrice") or 0)
                        box_c= "#16a34a" if pos==1 else "#3b82f6" if pos<=3 else "#6b7280" if pos<=5 else "#dc2626"
                        form_html += (
                            f'<div style="text-align:center;background:var(--surface2);border:1px solid var(--border);border-radius:var(--r);padding:5px 8px;min-width:40px">'
                            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:1.0rem;font-weight:700;color:{box_c}">{pos}</div>'
                            f'<div style="font-size:.58rem;color:var(--text4)">{trk}</div>'
                            f'<div style="font-size:.58rem;color:var(--text4)">{dst}m</div>'
                            f'</div>'
                        )
                    form_html += '</div>'
                    st.markdown(form_html, unsafe_allow_html=True)

                # Notes
                nk = f"{hid}_{rid}"
                note = st.text_area(
                    "Notes", value=st.session_state.notes.get(nk, ""),
                    key=f"note_{hid}_{rank}", height=52,
                    placeholder="Add analysis notes, overlays, intel..."
                )
                st.session_state.notes[nk] = note

            # ─ RIGHT COLUMN ────────────────────────────────────────
            with col_right:
                if not rating and not mf:
                    st.markdown('<div class="alert alert-blue">Click "Run Full Analysis" to compute ratings and value assessment.</div>', unsafe_allow_html=True)
                elif price <= 1:
                    st.markdown('<div class="alert alert-amber">No SP price available yet — market hasn\'t opened.</div>', unsafe_allow_html=True)
                else:
                    # Probability breakdown card
                    if mf and mp:
                        tp   = mf["true_pct"]
                        rp   = mf["raw_pct"]
                        fair = mf["fair_odds"]
                        mp_p = round(mp * 100, 1)
                        diff = round(mp_p - tp, 1)
                        dc   = "var(--green)" if diff > 0 else "var(--red)"

                        st.markdown(
                            f'<div class="card" style="margin-bottom:12px">'
                            f'<div class="dl-label" style="margin-bottom:12px;font-weight:700">Probability Analysis</div>'
                            f'<div class="prob-grid">'
                            f'<div class="prob-cell-blue"><div class="dl-label">SP Odds</div><div class="dl-value blue" style="font-size:1.15rem">${price:.2f}</div></div>'
                            f'<div class="prob-cell-blue"><div class="dl-label">Fair Odds</div><div class="dl-value" style="font-size:1.15rem">${fair:.2f}</div></div>'
                            f'<div class="prob-cell"><div class="dl-label">Raw Mkt%</div><div class="dl-value" style="font-size:.95rem;color:var(--text3)">{rp}%</div><div style="font-size:.66rem;color:var(--text4)">includes vig</div></div>'
                            f'<div class="prob-cell"><div class="dl-label">True Mkt%</div><div class="dl-value" style="font-size:.95rem">{tp}%</div><div style="font-size:.66rem;color:var(--text4)">de-vigged</div></div>'
                            f'<div class="prob-cell-blue"><div class="dl-label">Model%</div><div class="dl-value blue" style="font-size:.95rem;font-weight:700">{mp_p}%</div></div>'
                            f'<div class="prob-cell-blue"><div class="dl-label">Edge</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:.95rem;font-weight:700;color:{dc}">{"+" if diff>=0 else ""}{diff}%</div></div>'
                            f'</div>'
                            f'<div style="margin-top:10px;font-size:.7rem;color:var(--text4);font-family:\'JetBrains Mono\',monospace">Book: {mf["overround"]}%  ·  EV/unit: {verdict["ev_pct"] if verdict else "—"}%</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    # Bet gates
                    if verdict:
                        g = verdict["gates"]
                        def gate_pill(ok): return ("pill-green","Pass") if ok else ("pill-red","Fail")
                        g1c,g1t = gate_pill(g["edge"])
                        g2c,g2t = gate_pill(g["rating"])
                        g3c,g3t = gate_pill(g["tj"])
                        g4c,g4t = gate_pill(g["odds"])

                        gate_detail = {
                            "edge":   f"Edge {'+' if verdict['edge_pct']>=0 else ''}{verdict['edge_pct']}% vs min {st.session_state.min_edge}%",
                            "rating": f"Rating {rating['pct'] if rating else '?'}% vs min {st.session_state.min_rating}%",
                            "tj":     f"A2E {tj_a2e:.2f} vs min {st.session_state.min_tj_a2e}  (SR {tj_sr:.1f}%)",
                            "odds":   f"SP ${price:.2f}  range ${st.session_state.min_odds}–${st.session_state.max_odds}",
                        }

                        st.markdown(
                            f'<div class="card" style="margin-bottom:12px">'
                            f'<div class="dl-label" style="margin-bottom:12px;font-weight:700">Value Gates</div>'
                            + "".join([
                                f'<div class="gate-row">'
                                f'<span class="pill {pc}" style="width:40px;justify-content:center">{pt}</span>'
                                f'<span class="gate-lbl">{lbl}</span>'
                                f'<span class="gate-detail">{gate_detail[gk]}</span>'
                                f'</div>'
                                for gk,(pc,pt),lbl in [
                                    ("edge",(g1c,g1t),"Positive edge"),
                                    ("rating",(g2c,g2t),"Min rating"),
                                    ("tj",(g3c,g3t),"J+T A2E"),
                                    ("odds",(g4c,g4t),"SP range"),
                                ]
                            ])
                            + f'</div>',
                            unsafe_allow_html=True
                        )

                        if verdict["bet"]:
                            rec = compute_stake(
                                st.session_state.bank, mp, price,
                                st.session_state.staking_method,
                                st.session_state.kelly_fraction,
                                st.session_state.flat_pct,
                                st.session_state.level_stake,
                                st.session_state.max_stake_pct,
                            )
                            ev_c = "var(--green)" if rec["ev"] >= 0 else "var(--red)"
                            st.markdown(
                                f'<div class="stake-card">'
                                f'<div class="dl-label" style="margin-bottom:4px">{st.session_state.staking_method} Recommended Stake</div>'
                                f'<div class="stake-amount">${rec["stake"]:.2f}</div>'
                                f'<div class="stake-detail" style="color:{ev_c}">EV ${rec["ev"]:+.2f}  ·  {rec["ev_pct"]:+.1f}%  ·  {rec["pct_bank"]}% of bank</div>'
                                f'<div class="stake-detail">Break-even: {rec["roi_required"]:.1f}% ROI needed</div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                            st.markdown('<div class="alert alert-green" style="font-weight:600">BET — all four gates pass</div>', unsafe_allow_html=True)
                            if st.button(f"Log bet — {name}", key=f"log_{hid}_{rank}"):
                                add_bet(name, f"{rtrk} R{rnum}", rec["stake"], price, verdict["edge_pct"], verdict["model_pct"])
                                st.success(f"Logged: {name} ${rec['stake']:.2f} @ ${price}")
                        else:
                            reasons_str = "  ·  ".join(verdict["reasons"])
                            st.markdown(f'<div class="alert alert-red">No bet — {reasons_str}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# TAB 3: STAKING & BETS
# ════════════════════════════════════════════════════════════════
with TAB_STAKING:
    st.markdown("""<div class="page-hdr"><div>
      <div class="page-title">Staking & Bet Log</div>
      <div class="page-sub">Methods, discipline rules, and bet management</div>
    </div></div>""", unsafe_allow_html=True)

    # Staking method explainers
    st.markdown('<div class="section-hdr">Staking Methods</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, title, pill_c, body in [
        (c1, "Kelly Criterion", "pill-blue",
         "Mathematically optimal. Stake proportional to your edge over the market.<br><br>"
         "<code>f* = (bp − q) / b</code><br><br>"
         "<strong>Quarter Kelly (0.25×)</strong> is recommended — retains ~75% of growth rate "
         "while dramatically reducing variance and drawdowns. Full Kelly is theoretically correct "
         "but psychologically brutal and sensitive to model errors."),
        (c2, "Flat Percentage", "pill-muted",
         "Fixed % of current bank on every qualifying bet. Naturally scales down "
         "during losing streaks and up during winning runs.<br><br>"
         "Simpler than Kelly but ignores edge size — a 3% edge gets the same "
         "stake as a 25% edge. Best for punters who find Kelly staking confusing."),
        (c3, "Level Stakes", "pill-muted",
         "Fixed dollar amount per bet regardless of bank or edge magnitude.<br><br>"
         "Easiest for computing raw ROI and strike rate statistics. "
         "Does not protect bank during drawdowns. Best for tracking model performance "
         "in a controlled way before switching to Kelly."),
    ]:
        col.markdown(
            f'<div class="card"><div style="margin-bottom:10px"><span class="pill {pill_c}">{title}</span></div>'
            f'<div style="font-size:.8rem;color:var(--text2);line-height:1.85">{body}</div></div>',
            unsafe_allow_html=True
        )

    # Bank health
    bpct = st.session_state.bank / st.session_state.starting_bank * 100 if st.session_state.starting_bank else 100
    if bpct < 70:
        st.markdown(f'<div class="alert alert-red">Stop-loss alert — bank at {bpct:.1f}% of starting bank. Halve all stakes until bank recovers above 85%.</div>', unsafe_allow_html=True)
    elif bpct < 85:
        st.markdown(f'<div class="alert alert-amber">Bank at {bpct:.1f}% of starting bank — consider reducing stakes.</div>', unsafe_allow_html=True)

    # Discipline rules
    st.markdown('<div class="section-hdr">Discipline Rules</div>', unsafe_allow_html=True)
    rules = [
        (f"Max {st.session_state.max_stake_pct:.1f}% of bank per bet",
         "Absolute hard limit. Never exceeded regardless of confidence or edge size."),
        ("Compare model% to True% — not Raw%",
         "A $6 horse in a 122% book has True% ~13.7%, not 16.7%. Always de-vig before assessing value."),
        ("Stop-loss at 70% of starting bank",
         "Halve all stakes immediately. Resume normal staking only when bank recovers above 85%."),
        ("Log every bet including losers",
         "Discipline only works with honest, complete records. Selective logging produces misleading statistics."),
        ("Never override the model with gut feel",
         "Emotional bets systematically erode edge over time. The model is mechanical — keep it that way."),
        ("Minimum 300 bets before judging ROI",
         "50 bets is statistical noise. Even 200 is marginal. ROI requires volume to be meaningful."),
        ("Pre-race prices only",
         "This tool rates on pre-race form data. It does not incorporate in-running or late market movements."),
        ("One bet per race",
         "Multiple bets on one race reduce portfolio edge even if each bet individually qualifies."),
    ]
    for rule, detail in rules:
        st.markdown(
            f'<div class="card-sm" style="display:flex;gap:14px;margin-bottom:6px">'
            f'<span style="color:var(--blue);font-weight:700;flex-shrink:0;font-size:.9rem">—</span>'
            f'<div><div style="font-size:.82rem;font-weight:500;color:var(--text)">{rule}</div>'
            f'<div style="font-size:.74rem;color:var(--text3);margin-top:2px">{detail}</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

    # Bet log
    st.markdown('<div class="section-hdr">Bet Log</div>', unsafe_allow_html=True)
    log = st.session_state.bet_log
    if not log:
        st.markdown('<div class="alert alert-blue">No bets logged yet. Qualifying bets appear here after you click "Log bet" in the Analysis tab.</div>', unsafe_allow_html=True)
    else:
        # Summary stats
        settled = [b for b in log if b["result"] != "Pending"]
        pending = [b for b in log if b["result"] == "Pending"]
        if settled:
            s_pl  = sum(b["pl"] for b in settled)
            s_stk = sum(b["stake"] for b in settled)
            s_roi = round(s_pl / s_stk * 100, 1) if s_stk else 0
            s_wins= sum(1 for b in settled if b["result"] == "Won")
            st.markdown(
                f'<div style="display:flex;gap:16px;margin-bottom:14px;flex-wrap:wrap">'
                f'<span class="chip">{len(settled)} settled</span>'
                f'<span class="chip">{len(pending)} pending</span>'
                f'<span class="chip" style="color:{"var(--green)" if s_pl>=0 else "var(--red)"}">P/L ${s_pl:+.2f}</span>'
                f'<span class="chip">ROI {s_roi:+.1f}%</span>'
                f'<span class="chip">{s_wins}/{len(settled)} wins</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        df_log = pd.DataFrame(log)
        st.dataframe(
            df_log[["dt","horse","race","stake","odds","edge","model_pct","result","pl"]].rename(columns={
                "dt":"Time","horse":"Horse","race":"Race","stake":"Stake $",
                "odds":"Odds","edge":"Edge %","model_pct":"Model %","result":"Result","pl":"P/L $"
            }),
            use_container_width=True, hide_index=True
        )

        # Settle pending bets
        pending_idx = [(i, b) for i, b in enumerate(log) if b["result"] == "Pending"]
        if pending_idx:
            st.markdown('<div class="section-hdr">Settle Pending Bets</div>', unsafe_allow_html=True)
            for idx, bet in pending_idx:
                c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
                with c1:
                    st.markdown(
                        f'<div style="padding:8px 0;font-family:\'JetBrains Mono\',monospace;font-size:.8rem">'
                        f'<span style="color:var(--blue);font-weight:600">{bet["horse"]}</span>'
                        f'&nbsp;&nbsp;<span style="color:var(--text3)">${bet["stake"]:.2f} @ {bet["odds"]}</span>'
                        f'&nbsp;&nbsp;<span style="color:var(--text4)">{bet["race"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with c2:
                    if st.button("Won",  key=f"won_{idx}"): settle(idx, "Won");  st.rerun()
                with c3:
                    if st.button("Lost", key=f"lst_{idx}"): settle(idx, "Lost"); st.rerun()
                with c4:
                    if st.button("Void", key=f"vd_{idx}"):  settle(idx, "Void"); st.rerun()

        if st.button("Clear All Bets", type="secondary"):
            st.session_state.bet_log = []
            st.rerun()


# ════════════════════════════════════════════════════════════════
# TAB 4: BANKROLL
# ════════════════════════════════════════════════════════════════
with TAB_BANKROLL:
    st.markdown("""<div class="page-hdr"><div>
      <div class="page-title">Bankroll Performance</div>
      <div class="page-sub">P/L tracking, ROI analysis, and drawdown monitoring</div>
    </div></div>""", unsafe_allow_html=True)

    stats = bankroll_stats()
    if not stats:
        st.markdown('<div class="alert alert-blue">No settled bets yet. Results appear here after settling bets in the Staking tab.</div>', unsafe_allow_html=True)
    else:
        pl_c   = "green" if stats["pl"]  >= 0 else "red"
        roi_c  = "green" if stats["roi"] >= 0 else "red"
        dd_val = abs(stats["max_dd"])

        # KPI grid
        st.markdown(
            f'<div class="metric-grid">'
            f'<div class="metric-card blue"><div class="metric-label">Bank</div>'
            f'<div class="metric-value blue">${stats["bank"]:.0f}</div>'
            f'<div class="metric-sub">Start: ${st.session_state.starting_bank:.0f}</div></div>'
            f'<div class="metric-card {"green" if stats["pl"]>=0 else "red"}"><div class="metric-label">Total P/L</div>'
            f'<div class="metric-value {pl_c}">{("+" if stats["pl"]>=0 else "")}${stats["pl"]:.2f}</div></div>'
            f'<div class="metric-card {"green" if stats["roi"]>=0 else "red"}"><div class="metric-label">ROI</div>'
            f'<div class="metric-value {roi_c}">{("+" if stats["roi"]>=0 else "")}{stats["roi"]:.1f}%</div>'
            f'<div class="metric-sub">On ${stats["staked"]:.0f} staked</div></div>'
            f'<div class="metric-card"><div class="metric-label">Strike Rate</div>'
            f'<div class="metric-value">{stats["sr"]:.1f}%</div>'
            f'<div class="metric-sub">{stats["winners"]}/{stats["n"]} wins</div></div>'
            f'<div class="metric-card"><div class="metric-label">Total Bets</div>'
            f'<div class="metric-value">{stats["n"]}</div></div>'
            f'<div class="metric-card"><div class="metric-label">Avg Odds</div>'
            f'<div class="metric-value">{stats["avg_odds"]:.2f}</div>'
            f'<div class="metric-sub">${round(1/stats["avg_odds"]*100,1)}% implied</div></div>'
            f'<div class="metric-card red"><div class="metric-label">Max Drawdown</div>'
            f'<div class="metric-value red">-${dd_val:.2f}</div></div>'
            f'<div class="metric-card"><div class="metric-label">Peak Bank</div>'
            f'<div class="metric-value">${stats["peak"]:.0f}</div></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Cumulative P/L chart
        settled = [b for b in st.session_state.bet_log if b["result"] != "Pending"]
        if settled:
            st.markdown('<div class="section-hdr">Cumulative P/L</div>', unsafe_allow_html=True)
            pl_vals  = [0] + list(pd.Series([b["pl"] for b in settled]).cumsum())
            bet_nums = list(range(len(pl_vals)))
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=bet_nums, y=pl_vals,
                mode="lines+markers",
                line=dict(color="#1d4ed8", width=2),
                marker=dict(size=4, color=["#16a34a" if v >= 0 else "#dc2626" for v in pl_vals]),
                fill="tozeroy",
                fillcolor="rgba(29,78,216,0.07)",
                name="Cumulative P/L"
            ))
            fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8", line_width=1)
            fig.update_layout(
                paper_bgcolor="white", plot_bgcolor="white",
                margin=dict(t=10, b=10, l=10, r=10),
                xaxis=dict(title="Bet #", gridcolor="#f1f5f9", color="#64748b"),
                yaxis=dict(title="P/L ($)", gridcolor="#f1f5f9", color="#64748b"),
                height=300, showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

            # By odds range
            st.markdown('<div class="section-hdr">Performance by Odds Range</div>', unsafe_allow_html=True)
            def bucket(o):
                if o < 2.5: return "$1.01–$2.50"
                elif o < 4: return "$2.51–$4.00"
                elif o < 7: return "$4.01–$7.00"
                elif o < 12: return "$7.01–$12.00"
                elif o < 20: return "$12.01–$20.00"
                else: return "$20.00+"
            df_s = pd.DataFrame(settled)
            df_s["Range"] = df_s["odds"].apply(bucket)
            grp = df_s.groupby("Range", sort=False).agg(
                Bets=("pl","count"),
                Winners=("result", lambda x: (x=="Won").sum()),
                PL=("pl","sum"),
                Staked=("stake","sum"),
                AvgOdds=("odds","mean")
            ).reset_index()
            grp["SR %"]   = (grp["Winners"] / grp["Bets"] * 100).round(1)
            grp["ROI %"]  = (grp["PL"] / grp["Staked"] * 100).round(1)
            grp["PL"]     = grp["PL"].round(2)
            grp["Staked"] = grp["Staked"].round(2)
            grp["AvgOdds"]= grp["AvgOdds"].round(2)
            st.dataframe(grp[["Range","Bets","Winners","SR %","AvgOdds","Staked","PL","ROI %"]],
                         use_container_width=True, hide_index=True)

            # Edge vs ROI scatter (if we have enough data)
            if len(settled) >= 10:
                st.markdown('<div class="section-hdr">Edge vs Actual Outcome</div>', unsafe_allow_html=True)
                df_s["Outcome"] = df_s["result"].map({"Won": 1, "Lost": 0, "Void": 0.5})
                df_s["pl_pct"]  = df_s.apply(lambda r: r["pl"] / r["stake"] * 100 if r["stake"] else 0, axis=1)
                fig2 = px.scatter(df_s, x="edge", y="pl_pct",
                    color="result",
                    color_discrete_map={"Won": "#16a34a", "Lost": "#dc2626", "Pending": "#94a3b8"},
                    labels={"edge": "Model Edge %", "pl_pct": "P/L %"},
                    title=None,
                )
                fig2.add_hline(y=0, line_dash="dash", line_color="#94a3b8")
                fig2.update_layout(
                    paper_bgcolor="white", plot_bgcolor="white",
                    margin=dict(t=10, b=10, l=10, r=10), height=300,
                    xaxis=dict(gridcolor="#f1f5f9"), yaxis=dict(gridcolor="#f1f5f9"),
                )
                st.plotly_chart(fig2, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Reset Bankroll & Log", type="secondary"):
                st.session_state.bet_log       = []
                st.session_state.bank          = st.session_state.starting_bank
                st.rerun()
        with col_b:
            new_start = st.number_input("Set Starting Bank", value=st.session_state.starting_bank, step=100.0)
            if st.button("Update Starting Bank"):
                st.session_state.starting_bank = new_start
                st.rerun()


# ════════════════════════════════════════════════════════════════
# TAB 5: GUIDE
# ════════════════════════════════════════════════════════════════
with TAB_GUIDE:
    st.markdown("""<div class="page-hdr"><div>
      <div class="page-title">System Guide</div>
      <div class="page-sub">API architecture, rating methodology, and best practices</div>
    </div></div>""", unsafe_allow_html=True)

    # API Architecture
    st.markdown('<div class="section-hdr">PuntingForm API v2 — Correct Usage</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card" style="font-family:'JetBrains Mono',monospace;font-size:.78rem;line-height:2.1;color:var(--text2)">
    <div style="margin-bottom:10px;font-family:'Inter',sans-serif;font-size:.82rem;color:var(--red);font-weight:600">
    Critical: Date format must be <code>d-MMM-yyyy</code> (e.g. <code>4-Apr-2026</code>), NOT ISO 8601.
    Using YYYY-MM-DD causes 400 errors across all endpoints.
    </div>
    <strong style="color:var(--text)">form/meetingslist</strong>  ?meetingDate=4-Apr-2026<br>
    &nbsp;&nbsp;&nbsp;&nbsp;→ Returns list of meetings. Does NOT include runners. Date must be d-MMM-yyyy.<br><br>
    <strong style="color:var(--text)">form/meeting</strong>  ?meetingDate=4-Apr-2026 &amp;track=Randwick<br>
    &nbsp;&nbsp;&nbsp;&nbsp;→ Full meeting with all races and runner list. Track name must match exactly.<br><br>
    <strong style="color:var(--text)">form/fields</strong>  ?meetingDate=4-Apr-2026 &amp;track=Randwick &amp;raceNumber=1<br>
    &nbsp;&nbsp;&nbsp;&nbsp;→ Runner list for one race. Alt: ?raceId=12345<br><br>
    <strong style="color:var(--text)">form/form</strong>  ?meetingDate=4-Apr-2026 &amp;track=Randwick &amp;raceNumber=1<br>
    &nbsp;&nbsp;&nbsp;&nbsp;→ Past form for all runners in the race. Alt: ?raceId=12345<br><br>
    <strong style="color:var(--text)">ratings/meetingratings</strong>  ?meetingDate=...&amp;track=...&amp;raceNumber=...<br>
    &nbsp;&nbsp;&nbsp;&nbsp;→ PF AI model prices (pfAiPrice), ranks, scores. Professional subscription.<br><br>
    <strong style="color:var(--text)">ratings/meetingsectionals</strong>  ?meetingDate=...&amp;track=...&amp;raceNumber=...<br>
    &nbsp;&nbsp;&nbsp;&nbsp;→ Closing sectional benchmarks per runner. Professional subscription.<br><br>
    <strong style="color:var(--text)">form/scratchings</strong>  ?meetingDate=...<br>
    &nbsp;&nbsp;&nbsp;&nbsp;→ Day-of scratching updates.<br><br>
    <strong style="color:var(--text)">form/conditions</strong>  ?meetingDate=...<br>
    &nbsp;&nbsp;&nbsp;&nbsp;→ Track condition updates (rail position, going changes).
    </div>
    """, unsafe_allow_html=True)

    # Rating factors
    st.markdown('<div class="section-hdr">11-Factor Rating Engine</div>', unsafe_allow_html=True)
    factor_data = {
        "Factor": list(FACTOR_LBLS.values()),
        "Weight": list(FACTOR_WEIGHTS.values()),
        "% of Total": [round(w/MAX_SCORE*100,1) for w in FACTOR_WEIGHTS.values()],
        "Source & Method": [
            "PF meetingsectionals closing600Rating + past form closingSectional. Time inverted (faster=higher). Recency-weighted across 7 runs.",
            "PF speedRating adjusted for class (+5 G1, +3 G2) and going (-4 heavy, -2.5 soft). Recency penalty if >90 days since last run.",
            "Finish position across last 7 runs, exponentially recency-weighted (3.0x most recent to 0.4x 7th). Bonus for last-start win.",
            "Current class vs average of last 4 starts. 10-point class drop ≈ +2 score. Significant class rise = penalty.",
            "Keyword scan of raceComment field: 'no clear run' (4pt), 'held up' (3.5pt), 'checked' (3pt), 12 keywords total. Recency-multiplied.",
            "HOT pace: closers +2.0, leaders -1.5. SOFT: leaders +2.0, closers -1.0. Also rewards positional flexibility from past runs.",
            "Weight above 54kg penalised at 0.6pts/kg. Distance multiplier: 1.4x at 2400m+, 0.9x at sprint distances.",
            "Inside barriers preferred. Track-specific: Flemington sprint (inside very strong), Caulfield 1200m (inside). Scale reduces at distances.",
            "trainerJockeyA2E_Career: A2E×0.5 + SR×0.3 + PlaceRate×0.2. Regressed to mean for samples < 30 runs.",
            "trackRecord field (firsts/starts). Supplemented by past form at same venue. Win×0.65 + Place×0.35 weighting.",
            "distanceRecord field (firsts/starts). ±200m tolerance. Win×0.65 + Place×0.35 weighting.",
        ]
    }
    st.dataframe(pd.DataFrame(factor_data), use_container_width=True, hide_index=True)

    # Market framing
    st.markdown('<div class="section-hdr">Market Framing — Why True% Matters</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card" style="font-size:.82rem;color:var(--text2);line-height:1.9">
    <strong style="color:var(--text)">The overround problem:</strong> Australian TAB bookmakers price a race at 118–126%
    — the sum of all implied probabilities exceeds 100% by this margin. This is their guaranteed
    profit edge. If you bet at raw SP prices without accounting for this, you are betting into a negative-EV market by definition.<br><br>

    <strong>Example: $6.00 favourite in a 122% book</strong><br>
    Raw implied probability: 1/6.00 = 16.7% (this includes the bookie's 22% margin)<br>
    True de-vigged probability: 16.7% / 122% = <strong>13.7%</strong><br>
    Fair odds (no margin): 1/13.7% = <strong>$7.30</strong><br><br>

    If your model says this horse should be 18%, you have a genuine +4.3% edge over the de-vigged market.
    If you had compared to raw% (16.7%), you'd have thought your edge was only +1.3% — massively understated.<br><br>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;font-family:'JetBrains Mono',monospace;font-size:.76rem">
      <div class="card-sm">Raw% = 1/SP<br><span style="color:var(--text4)">includes full bookmaker overround</span></div>
      <div class="card-sm">True% = Raw% / Σ(all Raw%)<br><span style="color:var(--text4)">de-vigged market probability</span></div>
      <div class="card-sm">Fair Odds = 1/True%<br><span style="color:var(--text4)">equivalent price at 100% book</span></div>
      <div class="card-sm">Edge = Model% − True%<br><span style="color:var(--text4)">positive = genuine value opportunity</span></div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    # Tips
    st.markdown('<div class="section-hdr">Professional Tips</div>', unsafe_allow_html=True)
    tips = [
        ("Always rate the whole field",
         "Probabilities are normalised across all runners — skipping a horse corrupts the model for the entire race."),
        ("Sectionals are the single strongest predictor",
         "Closing speed explains more variance in future performance than any other factor. At Professional tier, "
         "meetingsectionals data is the most important API call."),
        ("Track closing line value (CLV)",
         "Compare your model price to the final SP. Consistently beating the closing line means your model has real information — "
         "regardless of short-term P/L results."),
        ("300+ bets before assessing ROI",
         "At a 25% strike rate, you need 400+ bets for statistical significance at 95% confidence. 50 bets is noise."),
        ("Specialise by race type",
         "Metro Thoroughbred handicaps (Open, BM78+) have the most data and most consistent model performance. "
         "Provincial maidens and country races are significantly harder to model."),
        ("A2E is more meaningful than raw strike rate",
         "A2E (above/below expectation vs market) controls for the quality of horses trained/ridden. "
         "A 10% SR trainer who specialises in $50 shots has higher A2E than a 20% SR trainer of favourites."),
        ("De-vig before comparing, always",
         "Every value comparison must be model% vs True%, never model% vs Raw%. "
         "This is the most common mistake among recreational punters."),
        ("Bet selection frequency",
         "A well-calibrated model at typical market overrounds should qualify ~5–12% of races. "
         "If qualifying >20%, your min_edge filter is too low. If <3%, it may be too high or the model is too conservative."),
    ]
    for title, detail in tips:
        st.markdown(
            f'<div class="card-sm" style="display:flex;gap:14px;margin-bottom:7px">'
            f'<span style="color:var(--blue);font-weight:700;flex-shrink:0;margin-top:1px">—</span>'
            f'<div><div style="font-size:.82rem;font-weight:600;color:var(--text)">{title}</div>'
            f'<div style="font-size:.74rem;color:var(--text3);margin-top:3px;line-height:1.55">{detail}</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

    # Speedmap guide
    st.markdown('<div class="section-hdr">Speedmap Interpretation</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px">
      <div><div class="pill pill-red" style="margin-bottom:8px">HOT</div>
        <div style="font-size:.78rem;color:var(--text2);line-height:1.6">3+ leaders. Early pace burns up the field. Strong finishing runs from the back. Back closers and anything drawn wide with barrier advantage.</div></div>
      <div><div class="pill pill-amber" style="margin-bottom:8px">GENUINE</div>
        <div style="font-size:.78rem;color:var(--text2);line-height:1.6">Two leaders fight it out. Honest tempo. All running styles viable. Rate on ability and class alone.</div></div>
      <div><div class="pill pill-blue" style="margin-bottom:8px">SOFT</div>
        <div style="font-size:.78rem;color:var(--text2);line-height:1.6">Single uncontested leader. Front-runner has a large tactical advantage. On-pace runners from tight barriers also benefit.</div></div>
      <div><div class="pill pill-muted" style="margin-bottom:8px">MODERATE</div>
        <div style="font-size:.78rem;color:var(--text2);line-height:1.6">No clear pace dynamic. Treat as even. Rate purely on form, class, and model probability.</div></div>
    </div>
    </div>
    """, unsafe_allow_html=True)


# ─── FOOTER ───────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:40px 0 20px;font-family:'JetBrains Mono',monospace;
font-size:.6rem;color:#cbd5e1;letter-spacing:.12em">
RACING EDGE  ·  RESEARCH & ANALYSIS PURPOSES ONLY  ·  GAMBLE RESPONSIBLY  ·  1800 858 858  ·  18+
</div>
""", unsafe_allow_html=True)
